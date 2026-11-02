"""CLAUDE.md Section 6.1: latency coding is monotonic; brightness x0.25...x4 leaves spike order unchanged."""

import pytest
import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.retina.dog import parvo_konio
from biovision.retina.latency import intensity_to_latency, rank_order

T = 15


def test_latency_is_monotonic():
    r = torch.linspace(0, 1, 1000).view(1, 1, -1)
    t = intensity_to_latency(r, T, theta_in=0.05).view(-1)
    active = t != NO_SPIKE
    assert bool((r.view(-1)[~active] < 0.05).all()) and bool((r.view(-1)[active] >= 0.05).all())
    ta = t[active].to(torch.int16)
    assert bool((ta[1:] <= ta[:-1]).all())  # stronger response -> earlier (or equal) spike
    assert int(ta[-1]) == 0  # the maximum fires at step 0
    assert int(ta.max()) <= T - 1


def test_latency_range_per_channel():
    r = torch.rand(4, 20, 20) * torch.tensor([1.0, 10.0, 0.1, 3.0]).view(4, 1, 1)
    t = intensity_to_latency(r, T, theta_in=0.0)
    for c in range(4):
        assert int(t[c].min()) == 0  # r_max is taken per channel


def _natural_like_image(seed=0, size=64):
    g = torch.Generator().manual_seed(seed)
    noise = torch.rand(3, size // 8, size // 8, generator=g, dtype=torch.float64)
    img = torch.nn.functional.interpolate(noise[None], size=(size, size), mode="bicubic", align_corners=False)[0]
    return 0.05 + 0.2 * img.clamp(0, 1)  # in [0.05, 0.25] so x4 stays <= 1 (no clipping)


def _order_preserved(t1, t2):
    """No pair (i, j) with t1_i < t1_j but t2_i > t2_j (spike sets must also match)."""
    if not torch.equal(t1 == NO_SPIKE, t2 == NO_SPIKE):
        return False
    a, b = t1[t1 != NO_SPIKE].long(), t2[t2 != NO_SPIKE].long()
    hi = torch.full((T,), -1, dtype=torch.long).scatter_reduce(0, a, b, "amax")
    lo = torch.full((T,), 10**6, dtype=torch.long).scatter_reduce(0, a, b, "amin")
    prev_max = torch.cummax(hi, 0).values
    return bool((prev_max[:-1] <= lo[1:]).all())


@pytest.mark.parametrize("factor", [0.25, 0.5, 2.0, 4.0])
@pytest.mark.parametrize("coding", ["latency", "rank"])
def test_brightness_leaves_spike_order_unchanged(factor, coding):
    encode = intensity_to_latency if coding == "latency" else rank_order
    img = _natural_like_image()
    # float64 and a negligible eps isolate the property itself from rounding noise
    base = encode(parvo_konio(img, eps=1e-12), T, theta_in=0.02)
    scaled = encode(parvo_konio(img * factor, eps=1e-12), T, theta_in=0.02)
    assert (base != NO_SPIKE).float().mean() > 0.05  # the test image does produce spikes
    assert _order_preserved(base, scaled)
    assert torch.equal(base, scaled)


def test_rank_order_quantises_to_T_groups():
    r = torch.arange(1, 151, dtype=torch.float64).view(1, 10, 15)
    t = rank_order(r, T, theta_in=0.0)
    counts = torch.bincount(t.view(-1).long(), minlength=T)
    assert torch.all(counts == 10)  # 150 active neurons / 15 steps
    assert int(t[0, 9, 14]) == 0  # strongest fires first
