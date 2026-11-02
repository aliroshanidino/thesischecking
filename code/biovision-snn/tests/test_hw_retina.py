"""Hardware-aware log-domain retina (Phase 1, docs/phase1_design_fa.md): the error bounds of the design note."""

import math

import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.retina.hw_retina import (binomial_1d, binomial_blur, encode_bio3, log_latency, magno_times,
                                       mitchell_log2, pyramid_pow2, ventral_log_responses)


def test_binomial_is_shift_add_and_has_variance_n_over_4():
    for n in (4, 16, 36):
        k = binomial_1d(n, torch.float64)
        assert torch.allclose(k.sum(), torch.tensor(1.0, dtype=torch.float64))
        assert all(float(c * 2 ** n).is_integer() for c in k)          # integer numerators: shifts and adds
        x = torch.arange(n + 1, dtype=torch.float64)
        mean = (k * x).sum()
        assert abs(float((k * (x - mean) ** 2).sum()) - n / 4) < 1e-9


def test_mitchell_log_error_bound():
    x = torch.logspace(-6, 6, 20001, base=2, dtype=torch.float64)
    err = torch.log2(x) - mitchell_log2(x)
    assert float(err.min()) >= -1e-12 and float(err.max()) <= 0.0862
    assert abs(float(err.max()) - (math.log2(1 / math.log(2)) - (1 / math.log(2) - 1))) < 1e-3


def test_brightness_invariance_exact_for_powers_of_two_and_bounded_otherwise():
    g = torch.Generator().manual_seed(0)
    img = torch.rand(3, 48, 48, generator=g, dtype=torch.float64) * 0.4 + 0.05
    base = ventral_log_responses(img, "pk", eps=1e-9)
    for s, bound in ((2.0, 1e-6), (0.5, 1e-6), (1.37, 2 * 0.0862)):  # 1e-6: eps does not scale
        other = ventral_log_responses(img * s, "pk", eps=1e-9)
        both = torch.isfinite(base) & torch.isfinite(other)
        assert bool((torch.isfinite(base) == torch.isfinite(other)).all())
        assert float((base[both] - other[both]).abs().max()) <= bound


def test_latency_moves_at_most_one_step_under_brightness():
    g = torch.Generator().manual_seed(1)
    img = torch.rand(3, 40, 40, generator=g, dtype=torch.float64) * 0.4 + 0.05
    a = log_latency(ventral_log_responses(img, "pk", eps=1e-9), 15, 0.5)
    b = log_latency(ventral_log_responses(img * 1.37, "pk", eps=1e-9), 15, 0.5)
    both = (a != NO_SPIKE) & (b != NO_SPIKE)
    assert int((a[both].int() - b[both].int()).abs().max()) <= 1


def test_pyramid_halves_and_magno_and_encoding_shapes():
    img = torch.rand(3, 64, 64, generator=torch.Generator().manual_seed(2))
    lv = pyramid_pow2(img, 3)
    assert [tuple(x.shape[-2:]) for x in lv] == [(64, 64), (32, 32), (16, 16)]
    assert torch.allclose(lv[1][:, 0, 0], img[:, :2, :2].mean(dim=(1, 2)))
    m = magno_times(img, 15)
    assert m.shape == (2, 64, 64) and set(torch.unique(m).tolist()) <= {0, 3, 6, 9, NO_SPIKE}
    t = encode_bio3(img, 15, "pkm")
    assert t.shape == (1, 8, 64, 64) and t.dtype == torch.uint8
    assert binomial_blur(torch.ones(10, 10), 36).allclose(torch.ones(10, 10))


def test_latency_shift_bound_is_ceil_of_four_mitchell_errors_over_delta():
    """|d(l_max - l)| <= 4 x 0.0861 = 0.344 octave under any brightness factor, so a spike moves by at most
    ceil(0.344 / delta) steps: 1 for delta = 1/2, 2 for delta = 1/4 (the Phase 1 setting)."""
    g = torch.Generator().manual_seed(2)
    img = torch.rand(3, 40, 40, generator=g, dtype=torch.float64) * 0.4 + 0.05
    for s in (1.37, 0.71, 1.9):
        a = log_latency(ventral_log_responses(img, "pk", eps=1e-9), 15, 0.25)
        b = log_latency(ventral_log_responses(img * s, "pk", eps=1e-9), 15, 0.25)
        both = (a != NO_SPIKE) & (b != NO_SPIKE)
        assert int((a[both].int() - b[both].int()).abs().max()) <= 2


def test_adaptive_contrast_threshold_keeps_the_rate_and_survives_gamma():
    from biovision.retina.hw_retina import encode_bio3
    g = torch.Generator().manual_seed(3)
    img = torch.rand(3, 64, 64, generator=g, dtype=torch.float64) * 0.6 + 0.2
    img = binomial_blur(img, 4)
    a = encode_bio3(img, 15, "pk", l_min="adaptive", rate=0.07, per_channel=True)[0]
    frac = (a != NO_SPIKE).flatten(1).float().mean(1)
    assert bool((frac <= 0.07).all()) and bool((frac >= 0.01).all())       # at most the rate (one bin less at worst)
    b = encode_bio3(img ** 0.5, 15, "pk", l_min="adaptive", rate=0.07, per_channel=True)[0]
    same = ((a != NO_SPIKE) & (b != NO_SPIKE)).sum() / (a != NO_SPIKE).sum()
    assert float(same) > 0.6                                                   # mostly the same active cells


def test_local_contrast_normalisation_cancels_brightness_and_most_of_gamma():
    """l = log2 D+ - log2(kappa L + B * |D|): a brightness factor cancels exactly; gamma multiplies every contrast in
    the pool by ~g, which the contrast-energy term divides out (first order)."""
    g = torch.Generator().manual_seed(4)
    img = binomial_blur(torch.rand(3, 64, 64, generator=g, dtype=torch.float64) * 0.6 + 0.2, 2)
    f = dict(lcn=36, kappa=2 ** -7, eps=1e-12, log="exact")
    base = ventral_log_responses(img, "pk", **f)
    bright = ventral_log_responses(img * 0.37, "pk", **f)
    both = torch.isfinite(base) & torch.isfinite(bright)
    assert float((base[both] - bright[both]).abs().max()) < 1e-6
    plain = ventral_log_responses(img ** 0.5, "pk", eps=1e-12, log="exact")
    plain0 = ventral_log_responses(img, "pk", eps=1e-12, log="exact")
    lcn = ventral_log_responses(img ** 0.5, "pk", **f)
    fin = torch.isfinite(plain) & torch.isfinite(plain0) & torch.isfinite(lcn) & torch.isfinite(base)
    shift_plain = float((plain[fin] - plain0[fin]).median())
    shift_lcn = float((lcn[fin] - base[fin]).median())
    assert shift_plain < -0.8 and abs(shift_lcn) < 0.3        # gamma 0.5 halves contrasts: -1 octave without LCN
