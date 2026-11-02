"""CLAUDE.md Section 6.1: DoG kernel sums to ~0; uniform image -> no spikes."""

import pytest
import torch

from biovision.retina.dog import dog_kernel, gaussian_kernel, parvo_konio
from biovision.retina.latency import intensity_to_latency
from biovision.engine.spikes import NO_SPIKE


@pytest.mark.parametrize("sigma_c,sigma_s", [(1.0, 3.0), (2.0, 6.0), (0.7, 2.1), (2.0, 2.0)])
def test_dog_kernel_sums_to_zero(sigma_c, sigma_s):
    k = dog_kernel(sigma_c, sigma_s, dtype=torch.float64)
    assert abs(float(k.sum())) < 1e-12
    assert k.shape[0] == k.shape[1] and k.shape[0] % 2 == 1


def test_gaussian_is_normalised_and_symmetric():
    g = gaussian_kernel(1.5, dtype=torch.float64)
    assert abs(float(g.sum()) - 1) < 1e-12
    assert torch.allclose(g, g.T) and torch.allclose(g, g.flip(0))


@pytest.mark.parametrize("grey", [0.02, 0.3, 0.5, 1.0])
def test_uniform_image_gives_no_spikes(grey):
    # achromatic: a uniform *coloured* field does drive the L/M and S-Y opponent cells (by design)
    img = torch.full((3, 64, 48), grey, dtype=torch.float32)
    r = parvo_konio(img)
    assert r.shape == (6, 64, 48)
    assert float(r.abs().max()) < 1e-5  # zero response everywhere, borders included
    t = intensity_to_latency(r, T=15, theta_in=0.02)
    assert bool((t == NO_SPIKE).all())


def test_opponent_maps_have_the_right_sign():
    # a red disc on a green background must drive L+/M- ON at the disc centre, not M+/L- ON
    img = torch.zeros(3, 41, 41)
    img[1] = 0.5
    yy, xx = torch.meshgrid(torch.arange(41), torch.arange(41), indexing="ij")
    disc = (yy - 20) ** 2 + (xx - 20) ** 2 <= 9
    img[0][disc], img[1][disc] = 0.5, 0.0
    r = parvo_konio(img)
    assert r[0, 20, 20] > 0 and r[2, 20, 20] == 0
