"""CLAUDE.md Section 6.1: k-WTA / feature WTA: at most one winner per position; winners respect the
inhibition radius."""

import pytest
import torch

from biovision.engine.inhibition import feature_wta, k_wta
from biovision.engine.spikes import NO_SPIKE


def _random_times(seed, C=12, H=20, W=20, T=15, p_silent=0.5):
    g = torch.Generator().manual_seed(seed)
    t = torch.randint(0, T, (C, H, W), generator=g, dtype=torch.uint8)
    t[torch.rand(t.shape, generator=g) < p_silent] = NO_SPIKE
    v = torch.rand(t.shape, generator=g)
    return t, v


@pytest.mark.parametrize("seed", range(5))
def test_feature_wta_one_winner_per_position(seed):
    t, v = _random_times(seed)
    out = feature_wta(t, v)
    fired = out != NO_SPIKE
    assert int(fired.sum(0).max()) <= 1
    # wherever any map fired, exactly one survives and it is (one of) the earliest
    any_fired = (t != NO_SPIKE).any(0)
    assert torch.equal(fired.any(0), any_fired)
    earliest = t.min(0).values
    assert torch.equal(out.min(0).values[any_fired], earliest[any_fired])


def test_feature_wta_tie_broken_by_potential():
    t = torch.full((3, 1, 1), 4, dtype=torch.uint8)
    v = torch.tensor([0.2, 0.9, 0.5]).view(3, 1, 1)
    out = feature_wta(t, v)
    assert out[:, 0, 0].tolist() == [NO_SPIKE, 4, NO_SPIKE]


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("radius", [0, 1, 3])
def test_k_wta_respects_radius_and_maps(seed, radius):
    t, v = _random_times(seed)
    winners = k_wta(t, k=8, radius=radius, v_fire=v)
    assert 1 <= len(winners) <= 8
    maps = [c for c, _, _ in winners]
    assert len(set(maps)) == len(maps)  # one winner per feature map
    for c, y, x in winners:
        assert t[c, y, x] != NO_SPIKE
    for i in range(len(winners)):
        for j in range(i + 1, len(winners)):
            (_, y1, x1), (_, y2, x2) = winners[i], winners[j]
            assert max(abs(y1 - y2), abs(x1 - x2)) > radius  # also implies one winner per position
    c0, y0, x0 = winners[0]
    assert t[c0, y0, x0] == t.min()  # the first winner is the earliest spike


def test_k_wta_on_silent_layer():
    t = torch.full((4, 5, 5), NO_SPIKE, dtype=torch.uint8)
    assert k_wta(t, k=3, radius=1) == []
