"""CLAUDE.md Section 6.1: spike-time <-> binary conversion is lossless."""

import pytest
import torch

from biovision.engine.spikes import NO_SPIKE, from_binary, onsets, silent, sparsity, to_binary


@pytest.mark.parametrize("T", [1, 15, 30])
def test_roundtrip_is_lossless(T):
    g = torch.Generator().manual_seed(0)
    times = torch.randint(0, T, (12, 31, 17), generator=g, dtype=torch.uint8)
    times[torch.rand(times.shape, generator=g) < 0.4] = NO_SPIKE
    wave = to_binary(times, T)
    assert wave.shape == (T, 12, 31, 17)
    assert torch.equal(from_binary(wave), times)


def test_binary_is_cumulative_and_has_one_onset():
    T = 15
    times = torch.tensor([[[0, 7, 14, NO_SPIKE]]], dtype=torch.uint8)
    wave = to_binary(times, T)
    assert torch.all(wave[1:] >= wave[:-1])  # once fired, stays 1 (SpykeTorch format)
    ev = onsets(wave)
    assert torch.all(ev.sum(0) == torch.tensor([[[1, 1, 1, 0]]], dtype=ev.dtype))
    assert torch.equal(from_binary(ev), times)  # onset-only waves decode too


def test_silent_and_validation():
    s = silent((3, 4, 4))
    assert s.dtype == torch.uint8 and sparsity(s) == 0.0
    assert to_binary(s, 15).sum() == 0
    with pytest.raises(ValueError):
        to_binary(torch.tensor([20], dtype=torch.uint8), 15)  # time >= T but not NO_SPIKE
    with pytest.raises(TypeError):
        to_binary(torch.tensor([2]), 15)  # wrong dtype
