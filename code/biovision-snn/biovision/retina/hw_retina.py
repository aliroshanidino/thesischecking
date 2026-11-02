"""Hardware-aware three-channel retina in the log domain (Phase 1; docs/phase1_design_fa.md; DECISIONS D26).

Every operation maps to adders, shifters, comparators and counters on an FPGA:

* **binomial filters** ``B_n = ([1, 1] / 2)^{*n}`` (separable; variance n / 4) instead of Gaussians: centre
  ``n = 4`` (sigma 1), surround ``n = 36`` (sigma 3), konio ``n = 16`` (sigma 2), normalisation pool ``n = 36``;
* **cones** ``L ~ R, M ~ G, S ~ B, Y = (L + M) / 2`` (a shift);
* **Mitchell logarithm** ``log2(2^k (1 + f)) ~ k + f`` (read the bits; error in [0, 0.0861] octave);
* **divisive normalisation as a subtraction** ``l = log2 D+ - log2(eps + B * Y)``: invariant to a brightness factor
  (exactly for powers of two, within 0.0861 octave otherwise);
* **latency code** ``t = floor((l_max - l) / delta)`` with ``delta`` a power of two (a shift), or the rank code of
  Phase 0 (equal packets: a histogram + prefix sums in hardware);
* **pyramid** with factor-2 steps: each level is the 2x2 sum of the previous one shifted right by 2;
* **magno** events from microsaccades (address shifts) when ``|l_Y(t) - l_Y(ref)| >= C`` (subtract, compare).
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from ..engine.spikes import NO_SPIKE, SPIKE_DTYPE
from .latency import rank_order

CHANNELS = {"grey": 2, "p": 4, "pk": 6, "pkm": 8, "m": 2}  # "m": magno only (event camera with microsaccades)


def binomial_1d(n: int, dtype=torch.float32) -> torch.Tensor:
    """``[C(n, 0), ..., C(n, n)] / 2^n``."""
    return torch.tensor([math.comb(n, k) for k in range(n + 1)], dtype=torch.float64).div(2.0 ** n).to(dtype)


def binomial_blur(img: torch.Tensor, n: int) -> torch.Tensor:
    """Separable binomial filter (replicate border) of ``[H, W]`` or ``[C, H, W]``."""
    if n <= 0:
        return img
    squeeze = img.dim() == 2
    x = (img.unsqueeze(0) if squeeze else img).unsqueeze(1)          # [C, 1, H, W]
    k = binomial_1d(n, img.dtype).to(img.device)
    r = n // 2
    x = F.pad(x, (r, n - r, 0, 0), mode="replicate")
    x = F.conv2d(x, k.view(1, 1, 1, -1))
    x = F.pad(x, (0, 0, r, n - r), mode="replicate")
    x = F.conv2d(x, k.view(1, 1, -1, 1))
    x = x.squeeze(1)
    return x.squeeze(0) if squeeze else x


def mitchell_log2(x: torch.Tensor) -> torch.Tensor:
    """``k + f`` for ``x = 2^k (1 + f)``; ``-inf`` for ``x <= 0``."""
    m, e = torch.frexp(x.clamp(min=torch.finfo(x.dtype).tiny))     # x = m 2^e, m in [0.5, 1)
    approx = (e - 1).to(x.dtype) + (2 * m - 1)
    return torch.where(x > 0, approx, torch.full_like(x, float("-inf")))


def log2_of(x: torch.Tensor, mode: str) -> torch.Tensor:
    if mode == "exact":
        return torch.where(x > 0, torch.log2(x.clamp(min=torch.finfo(x.dtype).tiny)), torch.full_like(x, float("-inf")))
    return mitchell_log2(x)


def ventral_log_responses(rgb: torch.Tensor, channels: str = "pk", n_c: int = 4, n_s: int = 36, n_k: int = 16,
                          n_n: int = 36, eps: float = 1 / 256, log: str = "mitchell", lcn: int | None = None,
                          kappa: float = 2 ** -5, dual: bool = False) -> torch.Tensor:
    """Normalised log responses ``l`` (``[C, H, W]``, ``-inf`` = no response) of one scale; ``rgb`` in 0..1.

    Order: ``grey``: Y ON, Y OFF; ``p``: (L+M-) ON, OFF, (M+L-) ON, OFF; ``pk``: p + K (S-Y) ON, OFF.

    ``lcn = n``: local contrast normalisation (contrast gain control, D28): each response is divided by
    ``kappa (eps + B_36 * Y) + B_n * |D|`` (Naka-Rushton denominator: luminance x a power of two + the local contrast
    energy of the same channel), i.e. ``l = log2 D+ - log2(...)``. A brightness factor cancels exactly (log2 exact)
    and, to first order, so does gamma: ``I^g ~ I0^g (1 + g e)`` multiplies every contrast in the pool by ``g``.
    ``dual``: both codes, the luminance-normalised channels (surface colour, single-opponent cells) followed by the
    contrast-normalised ones (colour edges, double-opponent cells, D29): twice the channels.
    """
    if rgb.dim() == 2:
        rgb = rgb.unsqueeze(0).expand(3, -1, -1)
    L, M, S = rgb[0], rgb[1], rgb[2]
    Y = (L + M) / 2
    if channels == "grey":
        ds = [binomial_blur(Y, n_c) - binomial_blur(Y, n_s)]
    else:
        ds = [binomial_blur(L, n_c) - binomial_blur(M, n_s), binomial_blur(M, n_c) - binomial_blur(L, n_s)]
        if channels in ("pk", "pkm"):
            ds.append(binomial_blur(S - Y, n_k))
    lum = eps + binomial_blur(Y, n_n)
    log_den = log2_of(lum, log)
    out, out_lcn = [], []
    for D in ds:
        on, off = log2_of(D.clamp(min=0), log), log2_of((-D).clamp(min=0), log)
        if lcn:
            den = log2_of(kappa * lum + binomial_blur(D.abs(), lcn), log)
            out_lcn += [on - den, off - den]
        if not lcn or dual:
            out += [on - log_den, off - log_den]
    return torch.stack(out + out_lcn)


def log_latency(ell: torch.Tensor, T: int, delta: float = 0.5, per_channel: bool = False,
                floor_rel: float | None = None) -> torch.Tensor:
    """``t = floor((l_max - l) / delta)``; no spike beyond ``T - 1`` steps or for ``-inf``. ``l_max`` is the largest
    response of the channel (``per_channel``) or of all channels (they compete, as the Phase 0 rank code)."""
    finite = torch.isfinite(ell)
    if per_channel:
        lmax = torch.where(finite, ell, torch.full_like(ell, float("-inf"))).amax(dim=(1, 2), keepdim=True)
    else:
        lmax = torch.where(finite, ell, torch.full_like(ell, float("-inf"))).amax()
    t = torch.floor((lmax - ell) / delta)
    ok = finite & (t < T)
    if floor_rel is not None:
        ok &= ell >= lmax - floor_rel
    return torch.where(ok, t.clamp(min=0), torch.full_like(t, NO_SPIKE)).to(SPIKE_DTYPE)


def rank_code(ell: torch.Tensor, T: int, per_channel: bool = False) -> torch.Tensor:
    """Phase 0 rank code on the (monotone) log responses: equal spike packets over the active cells."""
    finite = torch.isfinite(ell)
    lo = ell[finite].min() if bool(finite.any()) else torch.tensor(0.0, device=ell.device)
    r = torch.where(finite, ell - lo + 1.0, torch.zeros_like(ell))
    return rank_order(r, T, theta_in=1e-9, per_channel=per_channel)


def magno_times(rgb: torch.Tensor, T: int, shifts=((1, 0, 0), (0, -1, 3), (-1, 0, 6), (0, 1, 9)),
                contrast: float = 0.25, n_m: int = 4, log: str = "mitchell") -> torch.Tensor:
    """M channel (ON, OFF) from microsaccades: the image moves by ``(dx, dy)`` at step ``t``; a pixel spikes at the
    first step where its log intensity changed by at least ``contrast`` (octaves) since the last event."""
    if rgb.dim() == 2:
        rgb = rgb.unsqueeze(0).expand(3, -1, -1)
    Y = binomial_blur((rgb[0] + rgb[1]) / 2, n_m)
    ref = log2_of(Y + 1 / 256, log)
    out = torch.full((2, *Y.shape), NO_SPIKE, dtype=SPIKE_DTYPE, device=Y.device)
    pos = (0, 0)
    for dx, dy, t in shifts:
        if t >= T:
            break
        pos = (pos[0] + dx, pos[1] + dy)
        cur = torch.roll(ref, shifts=(pos[1], pos[0]), dims=(0, 1))
        d = cur - ref
        for ch, hit in ((0, d >= contrast), (1, d <= -contrast)):
            new = hit & (out[ch] == NO_SPIKE)
            out[ch][new] = t
        ref = torch.where((d >= contrast) | (d <= -contrast), cur, ref)
    return out


def pyramid_pow2(img: torch.Tensor, levels: int) -> list[torch.Tensor]:
    """Factor-2 pyramid of ``[C, H, W]``: level ``l + 1`` = 2x2 sum of level ``l`` shifted right by 2."""
    out = [img]
    for _ in range(levels - 1):
        x = out[-1]
        if min(x.shape[-2:]) < 4:
            break
        out.append(F.avg_pool2d(x.unsqueeze(0), 2).squeeze(0))
    return out


def adaptive_l_min(ell: torch.Tensor, rate: float, delta: float) -> torch.Tensor:
    """Contrast adaptation: per image and channel, the threshold that lets ~``rate`` of the cells spike, on the
    ``delta / 4`` grid below the channel's l_max, rounded up (at most ``rate`` of the cells). Hardware: a histogram
    of the quantised responses + a prefix sum, i.e. counters only. ``[C, 1, 1]``; the active set is invariant to a
    brightness factor and nearly so to a monotone change (gamma) that keeps the order of the responses."""
    C = ell.shape[0]
    flat = ell.flatten(1)
    lmax = torch.where(torch.isfinite(flat), flat, torch.full_like(flat, float("-inf"))).amax(1, keepdim=True)
    k = max(1, int(rate * flat.shape[1]))
    vals = torch.where(torch.isfinite(flat), flat, torch.full_like(flat, -1e9))
    kth = vals.topk(k, dim=1).values[:, -1:]                                   # the k-th strongest response
    g = delta / 4                                                              # histogram bins of delta / 4
    q = lmax - torch.floor((lmax - kth) / g) * g                               # up to the bin edge: <= rate
    return torch.where(torch.isfinite(lmax), q, torch.full_like(q, float("inf"))).view(C, 1, 1)


def encode_bio3(rgb01: torch.Tensor, T: int, channels: str = "pk", coding: str = "log", delta: float = 0.25,
                log: str = "mitchell", per_channel: bool = False, magno: dict | None = None,
                filters: dict | None = None, l_min: float | None = -0.5, rate: float = 0.07,
                l_floor: torch.Tensor | None = None) -> torch.Tensor:
    """Spike times ``[1, C, H, W]`` of one scale: ventral channels (+ magno ON/OFF for ``pkm``). ``l_min``: contrast
    threshold of the ganglion cells (octaves of normalised contrast; one comparator): weaker responses stay silent;
    ``"adaptive"``: per image and channel (contrast adaptation, ``rate`` of the cells, ``adaptive_l_min``), never
    below ``l_floor`` (``[C, 1, 1]``: the adaptation range is finite, so a channel without signal stays silent
    instead of spiking on noise)."""
    if channels == "m":  # magno only: ON / OFF change events from the microsaccades, like a DVS on a pan-tilt
        return magno_times(rgb01, T, log=log, **(magno or {})).unsqueeze(0)
    f = filters or {}
    ell = ventral_log_responses(rgb01, "pk" if channels == "pkm" else channels, log=log, **f)
    if isinstance(l_min, str) and l_min == "adaptive":
        l_min = adaptive_l_min(ell, rate, delta)
        if l_floor is not None:
            l_min = torch.maximum(l_min, l_floor.to(l_min.device, l_min.dtype))
    if l_min is not None:  # a float, or one threshold per channel ([C, 1, 1], calibrated offline: one comparator each)
        lm = l_min.to(ell.device, ell.dtype) if torch.is_tensor(l_min) else l_min
        ell = torch.where(ell >= lm, ell, torch.full_like(ell, float("-inf")))
    t = log_latency(ell, T, delta, per_channel) if coding == "log" else rank_code(ell, T, per_channel)
    if channels == "pkm":
        t = torch.cat([t, magno_times(rgb01, T, log=log, **(magno or {}))])
    return t.unsqueeze(0)


def calibrate_l_min(images: list[torch.Tensor], channels: str, rate: float = 0.07, log: str = "mitchell",
                    filters: dict | None = None) -> torch.Tensor:
    """Per-channel contrast thresholds ``[C, 1, 1]`` so that ~``rate`` of each channel's cells spike on these
    (training) images: the (1 - rate) quantile of the channel's log responses (offline; stored as constants)."""
    vals = None
    for img in images:
        x = img / 255.0 if img.max() > 1.5 else img
        ell = ventral_log_responses(x, "pk" if channels == "pkm" else channels, log=log, **(filters or {}))
        flat = ell.flatten(1)
        vals = flat if vals is None else torch.cat([vals, flat], dim=1)
    q = []
    for c in range(vals.shape[0]):
        v = vals[c]
        v = torch.where(torch.isfinite(v), v, torch.full_like(v, -1e9))
        q.append(torch.quantile(v.float()[:4_000_000], 1 - rate))
    return torch.stack(q).view(-1, 1, 1)
