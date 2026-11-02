"""CLAUDE.md Section 6.1: STDP sign correct on a synthetic pre/post pair; w stays in [0, 1]."""

import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.learning.convergence import convergence_index, is_converged
from biovision.learning.flat_stdp import flat_stdp_delta, flat_stdp_update

A_PLUS, A_MINUS = 0.004, 0.003


def test_sign_on_pre_post_pairs():
    w = torch.full((4,), 0.5)
    t_pre = torch.tensor([2, 5, 7, NO_SPIKE], dtype=torch.uint8)  # before, with, after, never
    dw = flat_stdp_delta(w, t_pre, t_post=5, a_plus=A_PLUS, a_minus=A_MINUS)
    assert dw[0] > 0 and dw[1] > 0  # pre before or with post -> LTP
    assert dw[2] < 0 and dw[3] < 0  # pre after post or silent -> LTD
    assert torch.allclose(dw, torch.tensor([A_PLUS, A_PLUS, -A_MINUS, -A_MINUS]) * 0.25)


def test_weights_stay_in_unit_interval_and_converge():
    g = torch.Generator().manual_seed(0)
    weight = torch.rand(6, 2, 5, 5, generator=g) * 0.2 + 0.4  # SpykeTorch-style init around 0.5
    c_start = convergence_index(weight)
    pattern = torch.randint(0, 15, (2, 9, 9), generator=g, dtype=torch.uint8)
    pattern[torch.rand(pattern.shape, generator=g) < 0.5] = NO_SPIKE
    for step in range(3000):
        post = torch.full((6, 5, 5), 7, dtype=torch.uint8)
        winners = [(step % 6, 2, 2)]
        flat_stdp_update(weight, pattern, winners, post, a_plus=0.05, a_minus=0.04)
        assert float(weight.min()) >= 0.0 and float(weight.max()) <= 1.0
    assert convergence_index(weight) < c_start
    assert is_converged(weight)  # repeated identical input drives every weight to 0 or 1


def test_padding_counts_as_silent_input():
    weight = torch.full((1, 1, 3, 3), 0.5)
    pre = torch.zeros(1, 1, 1, dtype=torch.uint8)  # single input that fires at t = 0
    post = torch.zeros(1, 1, 1, dtype=torch.uint8)
    flat_stdp_update(weight, pre, [(0, 0, 0)], post, A_PLUS, A_MINUS, padding=1)
    assert weight[0, 0, 1, 1] > 0.5  # the real input potentiates
    border = weight[0, 0].clone()
    border[1, 1] = 0.0
    assert bool((border[border > 0] < 0.5).all())  # the 8 padded inputs are depressed
