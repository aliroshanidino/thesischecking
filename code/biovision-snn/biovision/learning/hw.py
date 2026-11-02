"""Shift-and-add learning arithmetic: the hardware mode of every learning rule (DECISIONS D22).

The BioVision chip must learn and decide with shifts, additions and comparisons only (no multiplier). In software
the same arithmetic is emulated:

* soft bound: ``w (1 - w)`` (a product) becomes ``min(w, 1 - w) / 2`` -- one comparison, one subtraction and a
  one-bit shift; same zeros (w = 0, 1), same peak (0.25 at w = 0.5), piecewise linear in between;
* every learning rate and adaptive factor is rounded to a power of two, so ``a * x`` is a shift of ``x``;
* weights are fixed-point numbers with ``bits`` fractional bits and are truncated after each update (a shift right
  of the accumulator);
* neuron potentials are sums of weights (additions) and thresholds are compared, as before.

``configure`` is called once per run from the config (``hardware: {enabled, bits}``); all rules read ``HW``.
"""

from __future__ import annotations

import math

import torch

HW = {"enabled": False, "bits": 16, "rate_terms": 1, "stab": "half"}


def configure(cfg: dict | None) -> None:
    cfg = cfg or {}
    HW["enabled"] = bool(cfg.get("enabled", False))
    HW["bits"] = int(cfg.get("bits", 16))
    HW["rate_terms"] = int(cfg.get("rate_terms", 1))
    HW["stab"] = str(cfg.get("stab", "half"))


def stab(w: torch.Tensor) -> torch.Tensor:
    """Soft-bound factor of flat STDP: ``w (1 - w)``, or in hardware mode ``min(w, 1 - w) / 2`` (``stab: half``: same
    peak) or ``min(w, 1 - w)`` (``stab: slope``: same slope at the bounds w = 0, 1, so the same convergence rate
    ``1 - w ~ exp(-a n)`` near the attractors; ``half`` converges twice as slowly there)."""
    if HW["enabled"]:
        m = torch.minimum(w, 1 - w)
        return m if HW["stab"] == "slope" else m * 0.5
    return w * (1 - w)


def pow2(a: float) -> float:
    """Nearest power of two (in log scale); 0 stays 0, the sign is kept."""
    if a == 0:
        return 0.0
    return math.copysign(2.0 ** round(math.log2(abs(a))), a)


def csd(a: float, terms: int) -> float:
    """``a`` as a sum of ``terms`` signed powers of two (greedy canonical-signed-digit approximation): a product
    with it is ``terms`` shifts and ``terms - 1`` additions. ``terms = 1`` is ``pow2``."""
    out, rest = 0.0, a
    for _ in range(terms):
        if rest == 0:
            break
        q = pow2(rest)
        out += q
        rest = a - out
    return out


def rate(a):
    """A learning rate (float or list of floats) as the hardware uses it (``rate_terms`` powers of two)."""
    if not HW["enabled"]:
        return a
    t = HW["rate_terms"]
    return [csd(x, t) for x in a] if isinstance(a, (list, tuple)) else csd(a, t)


def quantize_(w: torch.Tensor) -> torch.Tensor:
    """In place: truncate to ``bits`` fractional bits in hardware mode (no-op otherwise)."""
    if HW["enabled"]:
        q = float(2 ** HW["bits"])
        w.mul_(q).floor_().div_(q)
    return w
