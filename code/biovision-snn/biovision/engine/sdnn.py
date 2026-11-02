"""Layered TTFS spiking network (Kheradpisheh et al. 2018 SDNN; CLAUDE.md Phase 0), built on ``engine/``.

Layers (from config): ``conv`` (non-leaky IF, weight sharing, feature-wise WTA, flat STDP with k-WTA learning
competition) and ``pool`` (max pooling = earliest spike wins). The last ``conv`` layer is read out for
classification as in the paper: its threshold is set to infinity and the global maximum of the final potential
of each map is the feature (one value per map).

Tensors: spike times ``[N, C, H, W]`` uint8 (``NO_SPIKE`` = silent); waves are built time-first
``[T, N, C, H, W]`` so ``engine.neurons.if_fire`` works unchanged.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import torch
import torch.nn.functional as F

from ..learning.convergence import convergence_index
from ..learning import hw
from ..learning.flat_stdp import flat_stdp_update_batch
from ..learning.sdsp import sdsp_update
from .inhibition import feature_wta, k_wta
from .neurons import if_fire
from .spikes import NO_SPIKE


@dataclass
class ConvLayer:
    maps: int
    kernel: int
    threshold: float
    k: int                  # learning winners per image (<= one per map)
    radius: int             # inter-map inhibition radius during learning
    padding: int = 0
    homeostasis: dict | None = None   # {eta, rho[, calcium]}: adaptive threshold (CLAUDE.md 5.2), or
                                      # {alpha, gamma[, brake]}: H-ASIZH threshold dynamics (Roshani et al., D21)
    neuron: str = "if"                # "if" (non-leaky, paper) or "lif" (leaky, D18)
    tau: float = 10.0                 # LIF membrane time constant in time steps: V(t) = exp(-1/tau) V(t-1) + I(t)
    schedule: dict | None = None      # per-map learning rate / budget (Kheradpisheh 2016): {a_start, a_max, every,
                                      # ratio, budget}; a+ doubles every `every` updates of a map, map stops at `budget`
    rule: str = "stdp"                # "stdp" (flat STDP, paper) or "sdsp" (calcium-gated SDSP, D20)
    sdsp: dict | None = None          # {kappa, lam, ca_up, ca_down, silent_ltd} (learning/sdsp.py)
    wta: bool = True                  # feature-wise WTA at inference (off: dense spike code for a readout layer)
    wta_groups: int = 1               # independent WTA groups of maps (V2 thin / pale stripes: 2)
    fire_rate: float = 0.05           # threshold "auto": ~this fraction of positions fire at calibration (CLAUDE.md 5.4)
    weight: torch.Tensor | None = field(default=None, repr=False)


@dataclass
class PoolLayer:
    kernel: int
    stride: int
    padding: int = 0


def build_layers(specs: list[dict]) -> list[ConvLayer | PoolLayer]:
    out = []
    for s in specs:
        s = dict(s)
        kind = s.pop("type")
        out.append(ConvLayer(**s) if kind == "conv" else PoolLayer(**s))
    return out


def wave(times: torch.Tensor, T: int, dtype=torch.float32) -> torch.Tensor:
    """``[N, C, H, W]`` spike times -> cumulative binary ``[T, N, C, H, W]``."""
    steps = torch.arange(T, device=times.device).view(T, 1, 1, 1, 1)
    return (times.unsqueeze(0).to(torch.int16) <= steps).to(dtype)


def fit_input(times: torch.Tensor, kernel: int, padding: int = 0) -> torch.Tensor:
    """Pad an input smaller than the kernel with silent positions (small scales of a multi-scale input)."""
    k = kernel - 2 * padding
    ph, pw = max(0, k - times.shape[-2]), max(0, k - times.shape[-1])
    return F.pad(times, (0, pw, 0, ph), value=NO_SPIKE) if ph or pw else times


def conv_potentials(times: torch.Tensor, layer: ConvLayer, T: int) -> torch.Tensor:
    """Membrane potentials ``[T, N, M, H', W']`` of a conv layer for input spike times ``[N, C, H, W]``.

    IF: ``V(t) = sum_{s<=t} W x(s)`` (convolution of the cumulative wave). LIF: ``V(t) = lam V(t-1) + W x(t)`` with
    ``lam = exp(-1/tau)`` and ``x(t)`` the spike onsets at step ``t``, so early inputs fade unless others follow soon.
    """
    w = wave(fit_input(times, layer.kernel, layer.padding), T, layer.weight.dtype)
    T_, N = w.shape[:2]
    if layer.neuron == "lif":
        onsets = torch.cat([w[:1], w[1:] - w[:-1]])
        cur = F.conv2d(onsets.flatten(0, 1), layer.weight, padding=layer.padding)
        cur = cur.view(T_, N, *cur.shape[1:])
        lam = math.exp(-1.0 / layer.tau)
        pot = torch.empty_like(cur)
        acc = torch.zeros_like(cur[0])
        for t in range(T_):
            acc = acc * lam + cur[t]
            pot[t] = acc
        return pot
    pot = F.conv2d(w.flatten(0, 1), layer.weight, padding=layer.padding)
    return pot.view(T_, N, *pot.shape[1:])


def readout_potential(times: torch.Tensor, layer: ConvLayer, T: int) -> torch.Tensor:
    """Readout with infinite threshold: final potential (IF, as in the paper) or the peak potential over the wave
    (LIF, whose final potential has leaked away)."""
    pot = conv_potentials(times, layer, T)
    return pot.amax(dim=0) if layer.neuron == "lif" else pot[-1]


def conv_forward(times: torch.Tensor, layer: ConvLayer, T: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Spike times after IF + feature-wise lateral inhibition, and the potentials at firing."""
    out, v = if_fire(conv_potentials(times, layer, T), layer.threshold)
    return (group_wta(out, v, layer.wta_groups) if layer.wta else out), v


def group_wta(out: torch.Tensor, v: torch.Tensor, groups: int = 1) -> torch.Tensor:
    """Feature-wise WTA, separately inside ``groups`` equal blocks of maps (one winner per block and position)."""
    if groups <= 1:
        return feature_wta(out, v)
    return torch.cat([feature_wta(o, w) for o, w in zip(out.chunk(groups, dim=-3), v.chunk(groups, dim=-3))], dim=-3)


def pool_forward(times: torch.Tensor, layer: PoolLayer) -> torch.Tensor:
    """Max pooling in TTFS = the earliest spike in the window wins (``NO_SPIKE`` = 255 never wins)."""
    t = fit_input(times, layer.kernel, layer.padding).to(torch.float32)
    if layer.padding:
        t = F.pad(t, (layer.padding,) * 4, value=float(NO_SPIKE))
    return (-F.max_pool2d(-t, layer.kernel, layer.stride)).to(torch.uint8)


class SDNN:
    def __init__(self, in_channels: int, specs: list[dict], T: int, device: torch.device,
                 generator: torch.Generator, w_mean: float = 0.8, w_std: float = 0.05):
        self.T, self.device = T, device
        self.layers = build_layers(specs)
        c = in_channels
        for layer in self.layers:
            if isinstance(layer, ConvLayer):
                w = torch.randn(layer.maps, c, layer.kernel, layer.kernel, generator=generator) * w_std + w_mean
                layer.weight = hw.quantize_(w.clamp_(0, 1)).to(device)
                c = layer.maps
        self.conv_ids = [i for i, l in enumerate(self.layers) if isinstance(l, ConvLayer)]
        self.wins = {i: torch.zeros(self.layers[i].maps, dtype=torch.long) for i in self.conv_ids}  # updates per map
        self.calcium = {i: torch.zeros(self.layers[i].maps, device=device) for i in self.conv_ids}  # firing traces
        self.theta0 = {}  # resting thresholds of the H-ASIZH homeostasis (set at the first learning step)

    # ---- inference ------------------------------------------------------------------------------------
    @torch.no_grad()
    def forward(self, times: torch.Tensor, upto: int | None = None, record: list | None = None) -> torch.Tensor:
        """Spike times at the output of layer ``upto - 1`` (all layers if None). ``record`` collects every
        layer's output spike times (for sparsity / spike counts)."""
        x = times
        for i, layer in enumerate(self.layers[: len(self.layers) if upto is None else upto]):
            x = conv_forward(x, layer, self.T)[0] if isinstance(layer, ConvLayer) else pool_forward(x, layer)
            if record is not None:
                record.append(x)
        return x

    @torch.no_grad()
    def readout_maps(self, times: torch.Tensor, layers: list[int]) -> dict[int, torch.Tensor]:
        """Readout potentials ``{layer: [N, M, H, W]}`` (infinite threshold) of several conv layers, one pass."""
        maps, x, last = {}, times, max(layers)
        for i, layer in enumerate(self.layers[: last + 1]):
            if i in layers:
                maps[i] = readout_potential(x, layer, self.T)
            if i < last:
                x = conv_forward(x, layer, self.T)[0] if isinstance(layer, ConvLayer) else pool_forward(x, layer)
        return maps

    @staticmethod
    def pool_features(maps: dict[int, torch.Tensor], grid, layers: list[int]) -> torch.Tensor:
        """Global max of each map (``grid <= 1``, paper) or max over a ``grid x grid`` partition (fixed size);
        a list of grids is a spatial pyramid (the levels concatenated)."""
        if isinstance(grid, (list, tuple)):
            return torch.cat([SDNN.pool_features(maps, g, layers) for g in grid], dim=1)
        return torch.cat([maps[li].flatten(2).amax(dim=2) if grid <= 1
                          else F.adaptive_max_pool2d(maps[li], (grid, grid)).flatten(1) for li in layers], dim=1)

    @torch.no_grad()
    def features(self, times: torch.Tensor, grid: int = 1, layers: list[int] | None = None) -> torch.Tensor:
        """Paper readout: last conv layer with infinite threshold; global max of each map's final potential.
        ``grid > 1`` keeps coarse location: max over a ``grid x grid`` partition of each map (our variant).
        ``layers``: conv layer indices to read out and concatenate (default: the last conv layer)."""
        layers = layers or [self.conv_ids[-1]]
        return self.pool_features(self.readout_maps(times, layers), grid, layers)

    # ---- learning -------------------------------------------------------------------------------------
    @torch.no_grad()
    def stdp_step(self, layer_idx: int, x_in: torch.Tensor, a_plus: float, a_minus: float) -> int:
        """One image (``x_in``: ``[1, C, H, W]`` input spike times of this layer): IF + lateral inhibition,
        k-WTA learning competition, flat STDP (or SDSP) on the winners, homeostasis. Returns the number of winners."""
        layer = self.layers[layer_idx]
        x_in = fit_input(x_in, layer.kernel, layer.padding)
        pot = conv_potentials(x_in, layer, self.T)
        out, v = if_fire(pot, layer.threshold)
        out = group_wta(out, v, layer.wta_groups)
        winners = k_wta(out[0], layer.k, layer.radius, v[0])
        rates = [(a_plus, a_minus)] * len(winners)
        if winners and layer.schedule:  # frozen maps still compete (and inhibit) but no longer learn
            sch, wins, keep = layer.schedule, self.wins[layer_idx], []
            rates = []
            for c, y, x in winners:
                n = int(wins[c])
                if n >= sch["budget"]:
                    continue
                ap = min(sch["a_start"] * 2.0 ** (n // sch["every"]), sch["a_max"])
                keep.append((c, y, x))
                rates.append((ap, ap * sch["ratio"]))
                wins[c] += 1
            winners = keep
        fired = (out[0] != NO_SPIKE).flatten(1)
        # z_i: map i fired on this image (CLAUDE.md 5.2), or its firing rate over positions (``z: rate``, Phase 1:
        # in large maps every map fires somewhere on every image; the rate is a spike counter + a shift)
        z = fired.float().mean(1) if (layer.homeostasis or {}).get("z") == "rate" else fired.any(1).float()
        h = layer.homeostasis or {}
        ca = self.calcium[layer_idx]
        brake = h.get("brake", 0.0)
        if brake and winners:  # H-ASIZH brake moved into plasticity: LTD grows with the map's calcium
            rates = [(ap, am * (1.0 + brake * float(ca[c]))) for (c, _, _), (ap, am) in zip(winners, rates)]
        if winners and layer.rule == "sdsp":
            p = layer.sdsp or {}
            th = torch.as_tensor(layer.threshold, dtype=torch.float32, device=self.device).expand(layer.maps)
            sdsp_update(layer.weight, x_in[0], winners, out[0], pot[:, 0], th, ca, rates,
                        p.get("kappa", 0.0), p.get("ca_up", 1.0), p.get("ca_down", -1.0), p.get("silent_ltd", False),
                        padding=layer.padding)
        elif winners:
            flat_stdp_update_batch(layer.weight, x_in[0], winners, out[0], [r[0] for r in rates],
                                   [r[1] for r in rates], padding=layer.padding)
        self.homeostasis(layer_idx, z)
        return len(winners)

    @torch.no_grad()
    def homeostasis(self, layer_idx: int, z: torch.Tensor) -> None:
        """Adaptive thresholds and calcium trace of a conv layer after one image (``z[i] = 1``: map ``i`` fired)."""
        layer = self.layers[layer_idx]
        h = layer.homeostasis or {}
        ca = self.calcium[layer_idx]
        if layer.homeostasis:
            th = torch.as_tensor(layer.threshold, dtype=torch.float32, device=self.device)
            th = th.expand(layer.maps).clone() if th.dim() == 0 else th
            if "alpha" in h:
                # H-ASIZH (Roshani et al., Eq. 9), one step per image: theta <- theta + alpha (theta0 - theta) + gamma z.
                # theta stays in [theta0, theta0 + gamma / alpha]; (theta - theta0) alpha / gamma is the calcium, an
                # exponential trace of z with factor (1 - alpha) = an estimate of the map's firing probability.
                if layer_idx not in self.theta0:  # resting threshold theta0 = theta0_scale x configured threshold
                    self.theta0[layer_idx] = th * h.get("theta0_scale", 1.0)
                    th = self.theta0[layer_idx].clone()
                th0 = self.theta0[layer_idx]
                gamma = h["gamma"] if "gamma" in h else h["gamma_rel"] * h["alpha"] * float(th0.mean())
                th = th + h["alpha"] * (th0 - th) + gamma * z
                ca.copy_((th - th0) * h["alpha"] / gamma)
                layer.threshold = th
                return
            drive = ca if h.get("calcium") else z  # theta_i <- theta_i + eta (z_i - rho); with calcium: (C_i - rho)
            if "eta_rel" in h:  # Phase 1: step relative to the calibrated threshold, (z - rho) / rho (rho = 2^-k: shift)
                th0 = self.theta0.setdefault(layer_idx, th.clone())
                layer.threshold = (th + h["eta_rel"] * th0 * (drive - h["rho"]) / h["rho"]).clamp_(min=h.get("min", 1.0))
                return
            layer.threshold = (th + h["eta"] * (drive - h["rho"])).clamp_(min=h.get("min", 1.0))
        lam = (layer.sdsp or {}).get("lam", h.get("lam", 0.99))
        ca.mul_(lam).add_((1 - lam) * z)                      # calcium: slow trace of the map's firing

    @torch.no_grad()
    def calibrate(self, layer_idx: int, inputs: list[torch.Tensor], n: int = 200) -> float:
        """Threshold so that ~``fire_rate`` of the positions fire with the initial weights (CLAUDE.md 5.4): the
        (1 - rate) quantile over positions of the best map's final potential."""
        layer = self.layers[layer_idx]
        step = max(1, len(inputs) // n)
        peaks = []
        for x in inputs[::step][:n]:
            pot = conv_potentials(fit_input(x.to(self.device), layer.kernel, layer.padding), layer, self.T)[-1, 0]
            peaks.append(pot.amax(dim=0).flatten())
        peaks = torch.cat(peaks)
        th = float(torch.quantile(peaks[peaks > 0].float()[:4_000_000], 1 - layer.fire_rate)) if bool((peaks > 0).any()) else 1.0
        layer.threshold = max(th, 1.0)
        return layer.threshold

    def train_layer(self, layer_idx: int, inputs: list[torch.Tensor], a_plus: float, a_minus: float,
                    generator: torch.Generator, freeze_below: float, max_iter: int, log_every: int = 50,
                    log=print) -> list[tuple[int, float]]:
        """Present training images (spike times at this layer's input, ``[1, C, H, W]`` each) in random order
        until ``C_l < freeze_below`` or ``max_iter`` images. Returns the convergence curve ``[(iter, C_l)]``."""
        layer = self.layers[layer_idx]
        curve = [(0, convergence_index(layer.weight))]
        it = 0
        while it < max_iter:
            for j in torch.randperm(len(inputs), generator=generator).tolist():
                self.stdp_step(layer_idx, inputs[j].to(self.device), a_plus, a_minus)
                it += 1
                if it % log_every == 0:
                    c = convergence_index(layer.weight)
                    curve.append((it, c))
                    if it % (log_every * 10) == 0:
                        log(f"  layer {layer_idx}: iter {it}, C_l = {c:.4f}")
                    if c < freeze_below:
                        return curve
                if layer.schedule and it % log_every == 0 and bool((self.wins[layer_idx] >= layer.schedule["budget"]).all()):
                    curve.append((it, convergence_index(layer.weight)))
                    log(f"  layer {layer_idx}: every map reached its budget at iter {it}")
                    return curve
                if it >= max_iter:
                    break
        return curve
