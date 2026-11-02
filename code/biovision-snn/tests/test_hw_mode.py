"""Shift-and-add (hardware) learning arithmetic, DECISIONS D22."""

import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.learning import hw
from biovision.learning.flat_stdp import flat_stdp_update_batch
from biovision.learning.rstdp import RSTDPRates


def teardown_function():
    hw.configure(None)


def test_pwl_soft_bound_has_the_zeros_and_peak_of_w_one_minus_w():
    hw.configure({"enabled": True})
    w = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0])
    assert torch.equal(hw.stab(w), torch.tensor([0.0, 0.125, 0.25, 0.125, 0.0]))
    hw.configure(None)
    assert torch.equal(hw.stab(w), w * (1 - w))


def test_rates_become_powers_of_two():
    hw.configure({"enabled": True})
    assert hw.rate(0.004) == 2 ** -8 and hw.rate(0.003) == 2 ** -8 and hw.rate(0.75) == 1.0
    assert hw.rate([0.01, 0.0005]) == [2 ** -7, 2 ** -11]
    r = RSTDPRates().scaled(0.9, 0.1)  # 0.8 x 0.1 + 0.2 = 0.28 -> 0.25 ; 0.8 x 0.9 + 0.2 = 0.92 -> 1
    assert r.a_plus == 0.005 * 0.25 and r.p_minus == 0.005 * 1.0


def test_stdp_update_stays_on_the_fixed_point_grid():
    hw.configure({"enabled": True, "bits": 12})
    w = hw.quantize_(torch.rand(3, 2, 3, 3, generator=torch.Generator().manual_seed(0)))
    pre = torch.randint(0, 5, (2, 5, 5), generator=torch.Generator().manual_seed(1)).to(torch.uint8)
    pre[0, 0, 0] = NO_SPIKE
    post = torch.full((3, 3, 3), NO_SPIKE, dtype=torch.uint8)
    post[0, 1, 1] = post[2, 0, 2] = 2
    flat_stdp_update_batch(w, pre, [(0, 1, 1), (2, 0, 2)], post, 0.004, 0.003)
    assert torch.equal(w * 4096, torch.floor(w * 4096))


def test_slope_matched_soft_bound_converges_as_fast_as_w_one_minus_w():
    """Near w = 1 the potentiation is 1 - w <- (1 - w)(1 - a s), s = w (float), 1 (slope) or 1/2 (half): after n
    updates the half bound is where the float rule was after n / 2 (docs: Phase 1 report, convergence lemma)."""
    a, n = 2 ** -6, 600

    def run(cfg):
        hw.configure(cfg)
        w = torch.tensor([0.8], dtype=torch.float64)
        for _ in range(n):
            w = w + a * hw.stab(w)
        return float(1 - w)

    flt, half, slope = run(None), run({"enabled": True}), run({"enabled": True, "stab": "slope"})
    assert slope < 1.3 * flt and half > 3 * flt
    hw.configure({"enabled": True, "stab": "slope"})
    w = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0])
    assert torch.equal(hw.stab(w), torch.tensor([0.0, 0.25, 0.5, 0.25, 0.0]))
