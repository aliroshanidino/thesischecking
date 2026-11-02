"""Flat (simplified) STDP of Kheradpisheh et al. 2018 (CLAUDE.md Section 5).

For a post-synaptic winner firing at ``t_post`` and each pre-synaptic input ``j`` of its receptive field:

* pre fired before or with post (``t_pre <= t_post``): ``dw = +a_plus  * w * (1 - w)``  (LTP)
* otherwise (later, or never):                         ``dw = -a_minus * w * (1 - w)``  (LTD)

Only the spike order matters. The factor ``w (1 - w)`` keeps ``w`` in [0, 1] and drives it to 0 or 1.
"""

from __future__ import annotations

import torch

from ..engine.spikes import NO_SPIKE
from . import hw


def flat_stdp_delta(w: torch.Tensor, t_pre: torch.Tensor, t_post: int, a_plus: float, a_minus: float) -> torch.Tensor:
    """Weight change for one winner. ``w`` and ``t_pre`` (uint8 times) have the same shape."""
    if t_post == NO_SPIKE:
        raise ValueError("the post-synaptic neuron must have fired")
    ltp = (t_pre != NO_SPIKE) & (t_pre.to(torch.int16) <= int(t_post))
    stab = hw.stab(w)
    a_plus, a_minus = hw.rate(a_plus), hw.rate(a_minus)
    return torch.where(ltp, a_plus * stab, -a_minus * stab)


def flat_stdp_update(
    weight: torch.Tensor,
    pre_times: torch.Tensor,
    winners: list[tuple[int, int, int]],
    post_times: torch.Tensor,
    a_plus: float,
    a_minus: float,
    padding: int = 0,
) -> torch.Tensor:
    """Apply one STDP update per winner to a convolutional layer, in place; returns ``weight``.

    ``weight``: ``[C_out, C_in, k, k]``; ``pre_times``: input spike times ``[C_in, H, W]``;
    ``winners``: ``(map, y, x)`` from ``engine.inhibition.k_wta``; ``post_times``: ``[C_out, H', W']``.
    Positions outside the (padded) input count as inputs that never fired.
    """
    _, _, k, _ = weight.shape
    padded = torch.nn.functional.pad(pre_times, (padding,) * 4, value=NO_SPIKE)
    for c, y, x in winners:
        patch = padded[:, y: y + k, x: x + k]
        dw = flat_stdp_delta(weight[c], patch, int(post_times[c, y, x]), a_plus, a_minus)
        weight[c] = hw.quantize_((weight[c] + dw).clamp_(0.0, 1.0))
    return weight


def winner_patches(pre_times: torch.Tensor, winners: list[tuple[int, int, int]], k: int, padding: int = 0):
    """Receptive fields of several winners in one gather: ``(patches [n, C, k, k], maps, ys, xs)``."""
    padded = torch.nn.functional.pad(pre_times, (padding,) * 4, value=NO_SPIKE)
    idx = torch.tensor(winners, device=pre_times.device)
    cs, ys, xs = idx.unbind(1)
    ar = torch.arange(k, device=pre_times.device)
    patch = padded[:, (ys[:, None] + ar)[:, :, None], (xs[:, None] + ar)[:, None, :]]  # [C, n, k, k]
    return patch.permute(1, 0, 2, 3), cs, ys, xs


def per_winner(rate, n: int, like: torch.Tensor) -> torch.Tensor:
    return torch.as_tensor(rate, dtype=like.dtype, device=like.device).expand(n).reshape(n, 1, 1, 1)         if not isinstance(rate, float) else torch.as_tensor(rate, dtype=like.dtype, device=like.device)


def flat_stdp_update_batch(weight: torch.Tensor, pre_times: torch.Tensor, winners: list[tuple[int, int, int]],
                           post_times: torch.Tensor, a_plus, a_minus, padding: int = 0) -> torch.Tensor:
    """``flat_stdp_update`` for all winners at once (one winner per map, as k-WTA guarantees); ``a_plus`` and
    ``a_minus`` are floats or one value per winner. Same arithmetic, element by element, as the loop version."""
    if not winners:
        return weight
    patch, cs, ys, xs = winner_patches(pre_times, winners, weight.shape[-1], padding)
    t_post = post_times[cs, ys, xs].to(torch.int16).view(-1, 1, 1, 1)
    ltp = (patch != NO_SPIKE) & (patch.to(torch.int16) <= t_post)
    w = weight[cs]
    stab = hw.stab(w)
    n = len(winners)
    dw = torch.where(ltp, per_winner(hw.rate(a_plus), n, w) * stab, -per_winner(hw.rate(a_minus), n, w) * stab)
    weight[cs] = hw.quantize_((w + dw).clamp_(0.0, 1.0))
    return weight
