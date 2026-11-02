"""Spike-time tensors (CLAUDE.md Section 6, conventions).

A wave is stored as one ``torch.uint8`` tensor of spike times ``[C, H, W]``: the time step at which
each neuron fires, or ``NO_SPIKE`` (255) when it stays silent. Time-to-first-spike coding means a
neuron fires at most once per wave, so this representation is exact.

SpykeTorch works on cumulative binary "spike waves" ``[T, C, H, W]`` where ``b[t] = 1`` once the
neuron has fired at or before step ``t``. ``to_binary`` / ``from_binary`` convert between the two;
this is the only conversion code path in the project.
"""

from __future__ import annotations

import torch

NO_SPIKE: int = 255
SPIKE_DTYPE = torch.uint8


def silent(shape: tuple[int, ...], device: torch.device | str | None = None) -> torch.Tensor:
    """A spike-time tensor in which no neuron fires."""
    return torch.full(shape, NO_SPIKE, dtype=SPIKE_DTYPE, device=device)


def check_times(times: torch.Tensor, T: int) -> None:
    """Raise if ``times`` is not a valid spike-time tensor for a wave of ``T`` steps."""
    if times.dtype != SPIKE_DTYPE:
        raise TypeError(f"spike times must be torch.uint8, got {times.dtype}")
    if not 1 <= T < NO_SPIKE:
        raise ValueError(f"T must be in [1, {NO_SPIKE - 1}], got {T}")
    bad = (times >= T) & (times != NO_SPIKE)
    if bool(bad.any()):
        raise ValueError(f"{int(bad.sum())} spike times are >= T={T} but not NO_SPIKE")


def to_binary(times: torch.Tensor, T: int, dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """Spike times ``[...]`` -> cumulative binary spike wave ``[T, ...]`` (SpykeTorch format).

    ``b[t, i] = 1`` iff ``times[i] <= t``. Silent neurons (``NO_SPIKE``) are 0 at every step.
    """
    check_times(times, T)
    steps = torch.arange(T, device=times.device).view(T, *([1] * times.dim()))
    return (times.unsqueeze(0).to(torch.int16) <= steps).to(dtype)


def from_binary(wave: torch.Tensor) -> torch.Tensor:
    """Binary spike wave ``[T, ...]`` -> spike times ``[...]`` (time of the first 1, else NO_SPIKE).

    Works for cumulative waves and for waves holding only the spike onsets.
    """
    if wave.shape[0] >= NO_SPIKE:
        raise ValueError(f"T must be < {NO_SPIKE}, got {wave.shape[0]}")
    fired = wave > 0
    first = fired.to(torch.uint8).argmax(dim=0).to(SPIKE_DTYPE)  # index of the first maximum = first spike
    return torch.where(fired.any(dim=0), first, torch.full_like(first, NO_SPIKE))


def onsets(wave: torch.Tensor) -> torch.Tensor:
    """Per-step spike events of a cumulative wave: ``e[t] = b[t] - b[t-1]`` (with ``b[-1] = 0``)."""
    prev = torch.cat([torch.zeros_like(wave[:1]), wave[:-1]], dim=0)
    return wave - prev


def spike_count(times: torch.Tensor) -> int:
    """Number of neurons that fired in this wave."""
    return int((times != NO_SPIKE).sum())


def sparsity(times: torch.Tensor) -> float:
    """Fraction of neurons that fired in this wave (CLAUDE.md Section 5.3, target 1-10 %)."""
    return spike_count(times) / times.numel()
