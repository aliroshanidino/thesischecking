"""Non-leaky integrate-and-fire (IF) neurons with time-to-first-spike output (CLAUDE.md Section 4).

Potential of neuron i: ``V_i(t) = sum_{s<=t} sum_j w_ij * x_j(s)``. The neuron fires once, at the
first step where ``V_i(t) >= theta_i``, and is silent for the rest of the wave.

With cumulative binary input waves ``b(t) = sum_{s<=t} x(s)`` (see ``engine.spikes``), a convolution of
``b(t)`` gives ``V(t)`` directly, which is how SpykeTorch simulates these layers.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

from .spikes import NO_SPIKE, SPIKE_DTYPE


def conv_potentials(wave: torch.Tensor, weight: torch.Tensor, padding: int = 0, stride: int = 1) -> torch.Tensor:
    """Membrane potentials ``[T, C_out, H', W']`` of a convolutional IF layer.

    ``wave``: cumulative binary input ``[T, C_in, H, W]``; ``weight``: ``[C_out, C_in, k, k]``,
    shared over positions (weight sharing, Section 1.3.3). Time steps are processed as a batch.
    """
    return F.conv2d(wave.to(weight.dtype), weight, padding=padding, stride=stride)


def if_fire(potentials: torch.Tensor, threshold: float | torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """First threshold crossing of each neuron.

    ``potentials``: ``[T, C, H, W]``; ``threshold``: scalar or per-map tensor broadcastable to ``[C, 1, 1]``.
    Returns ``(times, v_fire)``: spike times ``[C, H, W]`` (``NO_SPIKE`` if never crossed) and the
    potential at the firing step (0 for silent neurons), used to break ties in the WTA.
    """
    T = potentials.shape[0]
    if T >= NO_SPIKE:
        raise ValueError(f"T must be < {NO_SPIKE}")
    theta = torch.as_tensor(threshold, dtype=potentials.dtype, device=potentials.device)
    if theta.dim() == 1:
        theta = theta.view(-1, 1, 1)
    crossed = potentials >= theta
    fired = crossed.any(dim=0)
    first = crossed.to(torch.uint8).argmax(dim=0)
    t = first.to(SPIKE_DTYPE)
    times = torch.where(fired, t, torch.full_like(t, NO_SPIKE))
    v_fire = torch.gather(potentials, 0, first.unsqueeze(0).long()).squeeze(0)
    v_fire = torch.where(fired, v_fire, torch.zeros_like(v_fire))
    return times, v_fire
