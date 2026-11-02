"""Attention-gated reward-modulated learning of a hidden layer (AGREL, Roelfsema & van Ooyen 2005; BrainProp,
Pozzi et al. 2020) rewritten for TTFS spiking layers and shift-and-add hardware (DECISIONS D24).

Network on fixed input spikes ``x`` (e.g. Gabor C1):

    x -> hidden conv H (IF, feature-wise WTA) -> max pooling P -> decision layer D (first spike, class-assigned
    maps, R-STDP: ``rstdp_global.RSTDPReadout``)

1. **Pre-training:** H learns unsupervised with flat STDP and k-WTA (as every STDP layer of the project).
2. **Attention-gated R-STDP:** after D's winner ``o`` (map ``c`` at ``(y, x)``, spike at ``t_o``) has been rewarded
   or punished, the same reward signal reaches only the hidden units that *caused* this decision -- the attention
   feedback of AGREL travels back from the selected output unit over its own synapses:

   * a pooled hidden unit ``(m, i, j)`` in o's receptive field is *attended* if it spiked no later than ``o``
     (``t_{m,i,j} <= t_o``) and its synapse to ``o`` is strong (``W_D[c, m, i, j] >= gate``);
   * up to ``top`` attended units with distinct maps (strongest synapses first) are traced back through the
     pooling window to the hidden neuron that produced the pooled spike;
   * each of these hidden neurons receives R-STDP with the decision's reward sign (STDP after a correct decision,
     anti-STDP after a wrong one) at ``scale`` times the decision layer's rates.

   So hidden features that support correct decisions are reinforced and those behind wrong decisions are pushed
   away, while hidden units that did not take part in the decision do not change (credit assignment without a
   backpropagated error). Hardware: the gate is one comparison of a stored weight with a constant, the update is
   the R-STDP of the decision layer.

3. **Reward prediction error** (as AGREL, ``rpe: true``): the hidden update is scaled by ``delta = r - r_bar``
   (``r`` = 1 correct / 0 wrong, ``r_bar`` its running mean, factor ``1 - rpe_lam`` = a shift): early in training,
   when wrong decisions are expected, they barely punish the hidden layer, which otherwise is silenced by a flood of
   anti-STDP (first run: 87 % silent decisions after 40 epochs). ``punish: false`` updates the hidden layer after
   correct decisions only. The hidden thresholds keep their homeostasis during this phase.
"""

from __future__ import annotations

import torch

from ..engine.sdnn import SDNN, conv_forward, fit_input, pool_forward
from ..engine.spikes import NO_SPIKE
from ..learning.flat_stdp import flat_stdp_update_batch
from ..learning.rstdp import RSTDPRates
from .rstdp_global import RSTDPReadout


class AttentionRSTDP:
    def __init__(self, in_channels: int, n_classes: int, hidden: dict, decision: dict, rates: RSTDPRates,
                 dropout: float, T: int, device: torch.device, generator: torch.Generator, attention: dict,
                 w_mean: float = 0.8, w_std: float = 0.05, **decision_kw):
        self.T, self.device, self.gen = T, device, generator
        spec = {"type": "conv", "maps": hidden["maps"], "kernel": hidden["kernel"], "threshold": hidden["threshold"],
                "k": hidden.get("k", hidden["maps"]), "radius": hidden.get("radius", 1)}
        if hidden.get("homeostasis"):
            spec["homeostasis"] = hidden["homeostasis"]
        pk, ps = hidden.get("pool", [2, 2])
        self.net = SDNN(in_channels, [spec, {"type": "pool", "kernel": pk, "stride": ps}], T, device, generator,
                        w_mean=w_mean, w_std=w_std)
        self.h, self.pool = self.net.layers
        self.dec = RSTDPReadout(hidden["maps"], n_classes, decision["maps_per_class"], decision["kernel"],
                                decision["threshold"], rates, dropout, T, device, generator, w_mean=w_mean,
                                w_std=w_std, **decision_kw)
        self.att = {"gate": 0.5, "top": 16, "scale": 0.5, "rpe": False, "rpe_lam": 0.99, "punish": True,
                    **(attention or {})}
        self.base_rates = rates
        self.r_bar = 1.0 / n_classes
        self.hidden_cfg = hidden
        self.updates = 0  # attention-gated hidden updates (diagnostics)

    # ---- forward ------------------------------------------------------------------------------------------
    @torch.no_grad()
    def hidden_spikes(self, x: torch.Tensor) -> torch.Tensor:
        return conv_forward(x.to(self.device), self.h, self.T)[0]                # [1, Mh, Hh, Wh]

    @torch.no_grad()
    def features(self, x: torch.Tensor) -> torch.Tensor:
        return pool_forward(self.hidden_spikes(x), self.pool)                     # [1, Mh, Hp, Wp]

    # ---- learning ----------------------------------------------------------------------------------------------
    def pretrain(self, inputs: list[torch.Tensor], a_plus: float, a_minus: float, max_iter: int, log=print):
        """Unsupervised STDP of the hidden layer (k-WTA, homeostasis if configured)."""
        return self.net.train_layer(0, inputs, a_plus, a_minus, self.gen, 0.01, max_iter, log=log)

    @torch.no_grad()
    def _attend(self, x_in: torch.Tensor, pooled: torch.Tensor, h_times: torch.Tensor, winner, times, ok: bool,
                rates: RSTDPRates) -> None:
        if self.att["rpe"]:  # reward prediction error delta = r - r_bar; r_bar is updated after this decision
            delta = (1.0 - self.r_bar) if ok else self.r_bar
            lam = self.att["rpe_lam"]
            self.r_bar = lam * self.r_bar + (1 - lam) * float(ok)
            b = self.base_rates
            rates = RSTDPRates(b.a_plus * delta, b.a_minus * delta, b.p_minus * delta, b.p_plus * delta)
        if self.att["top"] <= 0 or self.att["scale"] == 0:  # control run: the hidden layer keeps its STDP features
            return
        if not ok and not self.att["punish"]:
            return
        c, y, xx = winner
        k = self.dec.layer.kernel
        t_o = int(times[c, y, xx])
        patch = pooled[0, :, y:y + k, xx:xx + k]                                  # [Mh, k, k] pooled spike times
        w = self.dec.layer.weight[c]                                              # [Mh, k, k]
        attended = (patch != NO_SPIKE) & (patch.to(torch.int16) <= t_o) & (w >= self.att["gate"])
        if not bool(attended.any()):
            return
        score = torch.where(attended, w, torch.full_like(w, -1.0)).flatten(1)     # strongest synapse per map
        best_w, best_pos = score.max(dim=1)
        maps = torch.nonzero(best_w >= 0).flatten()
        order = maps[torch.argsort(best_w[maps], descending=True)][: self.att["top"]].tolist()
        pk, ps = self.pool.kernel, self.pool.stride
        s = self.att["scale"]
        mt = torch.tensor(order, device=pooled.device)
        i, j = best_pos[mt] // k, best_pos[mt] % k
        t = patch[mt, i, j]                                                       # pooled spike time per map
        # trace each pooled spike back to the hidden neuron that produced it (first match in its pooling window)
        win = h_times[0][mt.view(-1, 1, 1),
                         ((y + i) * ps).view(-1, 1, 1) + torch.arange(pk, device=mt.device).view(1, -1, 1),
                         ((xx + j) * ps).view(-1, 1, 1) + torch.arange(pk, device=mt.device).view(1, 1, -1)]
        match = (win == t.view(-1, 1, 1)).flatten(1).float().argmax(1)
        hy, hx = (y + i) * ps + match // pk, (xx + j) * ps + match % pk
        winners = list(zip(order, hy.tolist(), hx.tolist()))
        ap, am = (rates.a_plus * s, rates.a_minus * s) if ok else (-rates.p_minus * s, -rates.p_plus * s)
        flat_stdp_update_batch(self.h.weight, x_in[0], winners, h_times[0], ap, am, padding=self.h.padding)
        self.updates += len(winners)

    def train_epoch(self, inputs: list[torch.Tensor], labels: list[int]) -> dict:
        cache = {}

        def prepare(j):
            x = inputs[j].to(self.device)
            h = self.hidden_spikes(x)
            if self.h.homeostasis:  # keep the hidden maps alive while attention-gated learning changes them
                self.net.homeostasis(0, (h[0] != NO_SPIKE).flatten(1).any(1).float())
            cache["x"], cache["h"] = x, h  # pooled map padded to the decision kernel (as the decision layer sees it)
            cache["p"] = fit_input(pool_forward(h, self.pool), self.dec.layer.kernel, self.dec.layer.padding)
            return cache["p"]

        def after(j, x, winner, times, ok, rates):
            self._attend(cache["x"], cache["p"], cache["h"], winner, times, ok, rates)

        return self.dec.train_epoch(inputs, labels, prepare=prepare, after=after)

    def evaluate(self, inputs: list[torch.Tensor], labels: list[int]) -> dict:
        return self.dec.evaluate([self.features(x) for x in inputs], labels)

    @property
    def rates(self):
        return self.dec.rates
