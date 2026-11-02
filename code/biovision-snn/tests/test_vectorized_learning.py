"""The vectorised k-WTA, flat STDP and SDSP give exactly the results of the straightforward loop versions."""

import pytest
import torch

from biovision.engine.inhibition import _k_wta_reference, k_wta
from biovision.engine.spikes import NO_SPIKE
from biovision.learning.flat_stdp import flat_stdp_update, flat_stdp_update_batch
from biovision.learning.sdsp import sdsp_delta, sdsp_update


def _layer(seed, maps=12, c_in=3, k=4, h=9, T=8):
    g = torch.Generator().manual_seed(seed)
    times = torch.randint(0, T, (maps, h, h), generator=g).to(torch.uint8)
    times[torch.rand(times.shape, generator=g) < 0.7] = NO_SPIKE
    v = torch.rand(times.shape, generator=g) * 10
    pre = torch.randint(0, T, (c_in, h + k - 1, h + k - 1), generator=g).to(torch.uint8)
    pre[torch.rand(pre.shape, generator=g) < 0.5] = NO_SPIKE
    w = torch.rand(maps, c_in, k, k, generator=g)
    return times, v, pre, w


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("radius", [0, 1, 3])
def test_k_wta_matches_reference(seed, radius):
    times, v, _, _ = _layer(seed)
    times[0, 0, 0] = times[1, 0, 1] = 0  # exact ties in time
    assert k_wta(times, 7, radius, v) == _k_wta_reference(times, 7, radius, v)
    assert k_wta(times, 7, radius, None) == _k_wta_reference(times, 7, radius, None)


@pytest.mark.parametrize("seed", range(4))
def test_flat_stdp_batch_matches_loop(seed):
    times, v, pre, w = _layer(seed)
    winners = k_wta(times, 6, 1, v)
    rates = [(0.01 * (i + 1), 0.004 * (i + 1)) for i in range(len(winners))]
    a = w.clone()
    for wi, (ap, am) in zip(winners, rates):
        flat_stdp_update(a, pre, [wi], times, ap, am)
    b = flat_stdp_update_batch(w.clone(), pre, winners, times, [r[0] for r in rates], [r[1] for r in rates])
    assert torch.equal(a, b)


@pytest.mark.parametrize("seed", range(4))
def test_sdsp_batch_matches_delta(seed):
    times, v, pre, w = _layer(seed)
    T = 8
    winners = k_wta(times, 6, 1, v)
    pot = torch.rand(T, *times.shape, generator=torch.Generator().manual_seed(seed)).cumsum(0) * 3
    th = torch.full((times.shape[0],), 6.0)
    ca = torch.linspace(0, 1, times.shape[0])
    rates = [(0.02, 0.01)] * len(winners)
    ref = w.clone()
    for (c, y, x) in winners:
        trace = pot[:, c, y, x]
        vb = torch.cat([trace.new_zeros(1), trace[:-1]])
        dw = sdsp_delta(ref[c], pre[:, y:y + 4, x:x + 4], int(times[c, y, x]), vb, 0.3 * 6.0, 0.02, 0.01,
                        ltp_open=float(ca[c]) < 0.7, ltd_open=float(ca[c]) > 0.1, silent_ltd=True)
        ref[c] = (ref[c] + dw).clamp_(0, 1)
    out = sdsp_update(w.clone(), pre, winners, times, pot, th, ca, rates, 0.3, 0.7, 0.1, silent_ltd=True)
    assert torch.allclose(ref, out, atol=1e-7)
