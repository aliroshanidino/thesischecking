"""Spike-driven synaptic plasticity (SDSP; Brader, Senn & Fusi 2007) rewritten for TTFS waves (DECISIONS D20).

Brader et al.: at each PRE-synaptic spike the synapse jumps up if the post-synaptic depolarisation is high
(``V > theta_V``) and the post-synaptic calcium is inside the potentiation window, and jumps down if ``V`` is low and
the calcium is inside the depression window. Silent pre-synaptic inputs never change. The calcium is a slow trace of
post-synaptic spikes, so a neuron that is already very active stops potentiating and a silent one stops depressing
("stop-learning").

TTFS version (one spike per neuron per wave; the potential is reset after the spike):

* calcium of map ``i``, updated once per image: ``C_i <- lam * C_i + (1 - lam) * z_i`` (``z_i = 1`` if map ``i``
  fired), i.e. a running estimate of the map's firing probability;
* for a learning winner (map ``c`` at ``(y, x)``, spike at ``t_post``) and each input ``j`` with a spike at ``t_j``:

  - LTP ``dw = +a_plus  * w(1-w)`` if ``t_j <= t_post`` and ``V(t_j - 1) >= kappa * theta_c`` and ``C_c < ca_up``
  - LTD ``dw = -a_minus * w(1-w)`` otherwise (pre after the post spike, or arriving at a low potential), if
    ``C_c > ca_down``
  - silent input: ``dw = 0`` (``silent_ltd=True`` depresses it as flat STDP does)

  ``V(t)`` is the winner's potential at step ``t`` (``V(-1) = 0``) and ``theta_c`` its (possibly homeostatic)
  threshold, so the adaptive threshold enters the learning rule itself. After ``t_post`` the potential is reset,
  so later pre spikes depress, as after a spike of Brader's integrate-and-fire neuron. With ``kappa = 0``,
  ``silent_ltd=True`` and open calcium windows the rule is exactly flat STDP.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

from ..engine.spikes import NO_SPIKE
from . import hw
from .flat_stdp import winner_patches


def sdsp_delta(w: torch.Tensor, t_pre: torch.Tensor, t_post: int, v_before: torch.Tensor, v_gate: float,
               a_plus: float, a_minus: float, ltp_open: bool = True, ltd_open: bool = True,
               silent_ltd: bool = False) -> torch.Tensor:
    """Weight change of one winner. ``w`` and ``t_pre`` (uint8 times) share a shape; ``v_before[t]`` is the
    post-synaptic potential just before step ``t`` (length ``T``)."""
    if t_post == NO_SPIKE:
        raise ValueError("the post-synaptic neuron must have fired")
    fired = t_pre != NO_SPIKE
    idx = t_pre.long().clamp_(max=v_before.numel() - 1)
    v_at = v_before[idx]
    ltp = fired & (t_pre.to(torch.int16) <= int(t_post)) & (v_at >= v_gate)
    ltd = (fired | silent_ltd) & ~ltp
    stab = hw.stab(w)
    a_plus, a_minus = hw.rate(a_plus), hw.rate(a_minus)
    dw = torch.zeros_like(w)
    if ltp_open:
        dw = dw + a_plus * stab * ltp
    if ltd_open:
        dw = dw - a_minus * stab * ltd
    return dw


def sdsp_update(weight: torch.Tensor, pre_times: torch.Tensor, winners: list[tuple[int, int, int]],
                post_times: torch.Tensor, potentials: torch.Tensor, thresholds: torch.Tensor,
                calcium: torch.Tensor, rates: list[tuple[float, float]], kappa: float, ca_up: float,
                ca_down: float, silent_ltd: bool = False, padding: int = 0) -> torch.Tensor:
    """Apply SDSP to a conv layer in place, all winners at once (one per map); returns ``weight``.

    ``weight`` ``[M, C, k, k]``; ``pre_times`` ``[C, H, W]``; ``post_times`` ``[M, H', W']``; ``potentials``
    ``[T, M, H', W']`` (no reset); ``thresholds`` ``[M]``; ``calcium`` ``[M]``; ``rates`` one ``(a_plus, a_minus)``
    per winner. Element by element this is ``sdsp_delta`` for each winner.
    """
    if not winners:
        return weight
    patch, cs, ys, xs = winner_patches(pre_times, winners, weight.shape[-1], padding)
    n, T = len(winners), potentials.shape[0]
    trace = potentials[:, cs, ys, xs]                                     # [T, n]
    v_before = torch.cat([trace.new_zeros(1, n), trace[:-1]]).t()         # [n, T]: V just before each step
    v_at = torch.gather(v_before, 1, patch.long().clamp_(max=T - 1).reshape(n, -1)).view(patch.shape)
    t_post = post_times[cs, ys, xs].to(torch.int16).view(-1, 1, 1, 1)
    gate = (kappa * thresholds[cs].to(v_at.dtype)).view(-1, 1, 1, 1)
    fired = patch != NO_SPIKE
    ltp = fired & (patch.to(torch.int16) <= t_post) & (v_at >= gate)
    ltd = (fired | silent_ltd) & ~ltp
    ca = calcium[cs].view(-1, 1, 1, 1)
    ltp = ltp & (ca < ca_up)
    ltd = ltd & (ca > ca_down)
    w = weight[cs]
    stab = hw.stab(w)
    ap = torch.tensor(hw.rate([r[0] for r in rates]), dtype=w.dtype, device=w.device).view(-1, 1, 1, 1)
    am = torch.tensor(hw.rate([r[1] for r in rates]), dtype=w.dtype, device=w.device).view(-1, 1, 1, 1)
    dw = ap * stab * ltp - am * stab * ltd
    weight[cs] = hw.quantize_((w + dw).clamp_(0.0, 1.0))
    return weight
