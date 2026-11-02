"""Global first-spike readout trained with R-STDP (Mozafari et al. 2018; CLAUDE.md Phase 1 readout (b)).

A conv IF layer with ``maps_per_class * n_classes`` maps; map ``i`` belongs to class ``i // maps_per_class``.
Decision = class of the map that fires first anywhere in the image (ties: larger potential, lower index);
no spike = no decision ("silence"). During training a random subset of maps is dropped (dropout, redrawn each
epoch), the single earliest neuron is the winner, and it is rewarded (STDP) when its class is correct and
punished (anti-STDP) otherwise. No external classifier is involved.

Calcium options (our extension, DECISIONS D20; ``None`` / ``0`` keeps the paper's rule):

* ``calcium={"lam": l}``: per-neuron adaptive rates. Each decision neuron keeps calcium-like traces of its own
  correct and wrong decisions, ``h_i <- l h_i + (1-l) [correct]`` and ``m_i <- l m_i + (1-l) [wrong]``, and its
  rates are Mozafari's adaptive rates computed from its own hit ratio ``h_i / (h_i + m_i)``: a neuron that has
  converged and still errs is punished hard, while the global epoch-level rates of the paper are not used.
* ``margin=d``: stop-learning (Brader et al. 2007): a correct decision whose first spike precedes the first spike of
  every other class by more than ``d`` steps is not rewarded any more.
* ``teacher=s``: on a wrong decision the earliest neuron of the correct class (or the one with the largest
  potential if none fired) also receives STDP with ``s`` times the reward rates, as the teacher current of SDSP.
* ``rule="sdsp"`` (R-SDSP, D23): the reward-modulated plasticity is SDSP instead of flat STDP. Reward applies the
  potential-gated SDSP jumps of ``learning/sdsp.py`` to the winner, punishment the same jumps with opposite sign.
  The calcium of a decision neuron is a trace of how often it wins (``sdsp.lam``); above ``ca_up`` it no longer
  potentiates, so one neuron per class cannot take over (stop-learning).
"""

from __future__ import annotations

import torch

from ..engine.inhibition import k_wta
from ..engine.neurons import if_fire
from ..engine.sdnn import conv_potentials, ConvLayer, fit_input
from ..engine.spikes import NO_SPIKE
from ..learning import hw
from ..learning.rstdp import RSTDPRates, rstdp_update


class RSTDPReadout:
    def __init__(self, in_channels: int, n_classes: int, maps_per_class: int, kernel: int, threshold: float,
                 rates: RSTDPRates, dropout: float, T: int, device: torch.device, generator: torch.Generator,
                 w_mean: float = 0.8, w_std: float = 0.05, calcium: dict | None = None, margin: int | None = None,
                 teacher: float = 0.0, rule: str = "stdp", sdsp: dict | None = None):
        self.n_classes, self.mpc, self.T, self.device = n_classes, maps_per_class, T, device
        m = n_classes * maps_per_class
        w = hw.quantize_((torch.randn(m, in_channels, kernel, kernel, generator=generator) * w_std + w_mean).clamp_(0, 1))
        self.layer = ConvLayer(maps=m, kernel=kernel, threshold=threshold, k=1, radius=0, weight=w.to(device))
        self.base_rates, self.rates = rates, rates.initial(n_classes)
        self.dropout, self.gen = dropout, generator
        self.drop_mask = torch.zeros(m, dtype=torch.bool, device=device)
        self.calcium, self.margin, self.teacher = calcium, margin, teacher
        self.rule, self.sdsp = rule, sdsp or {}
        self.ca = torch.zeros(m, device=device)               # R-SDSP calcium: how often each neuron wins
        self.h = torch.full((m,), 1.0 / n_classes)          # per-neuron traces of correct / wrong decisions
        self.m = torch.full((m,), 1.0 - 1.0 / n_classes)

    def _fire(self, x: torch.Tensor, training: bool):
        pot = conv_potentials(x, self.layer, self.T)                     # [T, 1, M, H, W]
        if training and self.dropout > 0:
            pot = pot.masked_fill(self.drop_mask.view(1, 1, -1, 1, 1), 0.0)
        times, v = if_fire(pot, self.layer.threshold)
        self.last_final = pot[-1, 0]                                      # final potentials (teacher)
        self.last_pot = pot[:, 0]                                         # [T, M, H, W] (R-SDSP)
        return times[0], v[0]                                             # [M, H, W]

    @torch.no_grad()
    def decide(self, x: torch.Tensor, training: bool = False):
        """Returns ``(class or -1, winner (map, y, x) or None, output spike times)``."""
        times, v = self._fire(x, training)
        winners = k_wta(times, 1, 0, v)
        if not winners:
            return -1, None, times
        return winners[0][0] // self.mpc, winners[0], times

    @torch.no_grad()
    def train_epoch(self, inputs: list[torch.Tensor], labels: list[int], prepare=None, after=None) -> dict:
        """One pass over the training set in random order. ``prepare(j)`` builds the decision-layer input of image
        ``j`` (default ``inputs[j]``); ``after(j, winner, times, ok, rates)`` runs after each rewarded/punished
        decision (attention-gated learning of a hidden layer, ``rstdp_attention.py``)."""
        m = self.layer.maps
        self.drop_mask = torch.rand(m, generator=self.gen).to(self.device) < self.dropout
        hit = miss = silent = 0
        for j in torch.randperm(len(inputs), generator=self.gen).tolist():
            # pad an input smaller than the kernel (as the convolution does), so the plasticity sees full patches
            x = fit_input((prepare(j) if prepare else inputs[j]).to(self.device), self.layer.kernel, self.layer.padding)
            d, winner, times = self.decide(x, training=True)
            if d < 0:
                silent += 1
                continue
            ok = d == labels[j]
            hit += ok
            miss += not ok
            c = winner[0]
            rates = self.rates
            if self.calcium:
                tot = float(self.h[c] + self.m[c])
                rates = self.base_rates.scaled(float(self.h[c]) / tot, float(self.m[c]) / tot)
            learn = True
            if ok and self.margin is not None:
                t_win = int(times[winner])
                others = torch.ones(self.layer.maps, dtype=torch.bool, device=times.device)
                others[d * self.mpc:(d + 1) * self.mpc] = False
                t_other = int(times[others].min()) if bool(others.any()) else NO_SPIKE
                learn = t_other - t_win <= self.margin
            if learn and self.rule == "sdsp":
                self._sdsp(x, winner, times, ok, rates)
            elif learn:
                rstdp_update(self.layer.weight, x[0], winner, times, ok, rates, self.layer.padding)
            if self.rule == "sdsp":
                lam = self.sdsp.get("lam", 0.99)
                self.ca.mul_(lam)
                self.ca[c] += 1 - lam
            if not ok and self.teacher > 0:
                self._teach(x, labels[j], times, rates)
            if self.calcium:
                lam = self.calcium.get("lam", 0.9)
                self.h[c] = lam * self.h[c] + (1 - lam) * float(ok)
                self.m[c] = lam * self.m[c] + (1 - lam) * float(not ok)
            if after is not None:
                after(j, x, winner, times, ok, rates)
        n = len(inputs)
        self.rates = self.base_rates.scaled(hit / n, miss / n)
        return {"hit": hit / n, "miss": miss / n, "silent": silent / n}

    def _sdsp(self, x: torch.Tensor, winner, times: torch.Tensor, ok: bool, rates: RSTDPRates) -> None:
        """R-SDSP: SDSP jumps on the winner, sign set by the reward (punishment = the anti rule)."""
        from ..learning.sdsp import sdsp_update
        p = self.sdsp
        ap, am = (rates.a_plus, rates.a_minus) if ok else (-rates.p_minus, -rates.p_plus)
        th = torch.as_tensor(self.layer.threshold, dtype=torch.float32, device=self.device).expand(self.layer.maps)
        sdsp_update(self.layer.weight, x[0], [winner], times, self.last_pot, th, self.ca, [(ap, am)],
                    p.get("kappa", 0.0), p.get("ca_up", 1.0) if ok else 2.0, p.get("ca_down", -1.0) if ok else -1.0,
                    p.get("silent_ltd", True), padding=self.layer.padding)

    def _teach(self, x: torch.Tensor, label: int, times: torch.Tensor, rates: RSTDPRates) -> None:
        """Teacher signal: STDP on the earliest (or most depolarised) neuron of the correct class."""
        lo, hi = label * self.mpc, (label + 1) * self.mpc
        sub = times[lo:hi]
        if bool((sub != NO_SPIKE).any()):
            c, y, xx = k_wta(sub, 1, 0, None)[0]
            post = times
        else:
            fin = self.last_final[lo:hi].masked_fill(self.drop_mask[lo:hi].view(-1, 1, 1), float("-inf"))
            if not bool((fin > 0).any()):
                return
            c, rem = divmod(int(fin.argmax()), fin.shape[1] * fin.shape[2])
            y, xx = divmod(rem, fin.shape[2])
            post = times.clone()
            post[lo + c, y, xx] = self.T - 1                     # as if it fired at the end of the wave
        s = self.teacher
        teach = RSTDPRates(rates.a_plus * s, rates.a_minus * s, 0.0, 0.0, rates.adaptive_min, rates.adaptive_int)
        rstdp_update(self.layer.weight, x[0], (lo + c, y, xx), post, True, teach, self.layer.padding)

    @torch.no_grad()
    def evaluate(self, inputs: list[torch.Tensor], labels: list[int]) -> dict:
        hit = miss = silent = 0
        pred = []
        for x, y in zip(inputs, labels):
            d, _, _ = self.decide(x.to(self.device), training=False)
            pred.append(d)
            if d < 0:
                silent += 1
            elif d == y:
                hit += 1
            else:
                miss += 1
        n = len(inputs)
        return {"acc": hit / n, "miss": miss / n, "silent": silent / n, "pred": pred}

    @torch.no_grad()
    def spike_count(self, x: torch.Tensor) -> int:
        return int((self._fire(x.to(self.device), False)[0] != NO_SPIKE).sum())
