"""GPU path (DECISIONS D14): the same spike times on CUDA as on the CPU; CuPy kernels match PyTorch.
Skipped on machines without a GPU (the HPC)."""

import pytest
import torch

from biovision.engine import cuda_kernels
from biovision.engine.inhibition import feature_wta, k_wta
from biovision.engine.neurons import conv_potentials, if_fire
from biovision.engine.spikes import NO_SPIKE, from_binary, to_binary
from biovision.learning.flat_stdp import flat_stdp_update
from biovision.retina.dog import parvo_konio
from biovision.retina.latency import intensity_to_latency, rank_order

pytestmark = pytest.mark.skipif(not torch.cuda.is_available(), reason="no CUDA GPU")
T = 15
CUDA = torch.device("cuda")


def _image(seed=0, size=96):
    g = torch.Generator().manual_seed(seed)
    noise = torch.rand(3, size // 8, size // 8, generator=g, dtype=torch.float64)
    img = torch.nn.functional.interpolate(noise[None], size=(size, size), mode="bicubic", align_corners=False)[0]
    return img.clamp(0, 1)


def test_retina_and_coding_match_cpu():
    img = _image()
    for encode in (intensity_to_latency, rank_order):
        cpu = encode(parvo_konio(img), T, theta_in=0.02)
        gpu = encode(parvo_konio(img.to(CUDA)), T, theta_in=0.02)
        assert gpu.is_cuda and torch.equal(cpu, gpu.cpu())


def test_if_layer_wta_and_stdp_match_cpu():
    g = torch.Generator().manual_seed(1)
    x = torch.randint(0, T, (6, 48, 48), generator=g, dtype=torch.uint8)
    x[torch.rand(x.shape, generator=g) < 0.7] = NO_SPIKE
    w = torch.rand(12, 6, 5, 5, generator=g, dtype=torch.float64)
    out = {}
    for dev in ("cpu", "cuda"):
        xs, ws = x.to(dev), w.clone().to(dev)
        pot = conv_potentials(to_binary(xs, T, dtype=torch.float64), ws, padding=2)
        times, v = if_fire(pot, 8.0)
        times = feature_wta(times, v)
        winners = k_wta(times, k=5, radius=2, v_fire=v)
        flat_stdp_update(ws, xs, winners, times, a_plus=0.004, a_minus=0.003, padding=2)
        out[dev] = (times.cpu(), winners, ws.cpu())
    assert torch.equal(out["cpu"][0], out["cuda"][0])
    assert out["cpu"][1] == out["cuda"][1]
    assert torch.allclose(out["cpu"][2], out["cuda"][2], atol=1e-12)
    assert torch.equal(from_binary(to_binary(out["cpu"][0], T)), out["cpu"][0])


@pytest.mark.skipif(not cuda_kernels.available(), reason="CuPy not installed")
def test_cupy_first_crossing_matches_torch():
    g = torch.Generator().manual_seed(2)
    pot = torch.cumsum(torch.rand(T, 12, 64, 64, generator=g), dim=0).to(CUDA)  # monotone like IF potentials
    theta = torch.linspace(1.0, 9.0, 12)
    ref_t, ref_v = if_fire(pot, theta.to(CUDA))
    t, v = cuda_kernels.if_fire_cuda(pot, theta)
    assert torch.equal(t, ref_t) and torch.equal(v, ref_v)
    assert (t == NO_SPIKE).any() and (t != NO_SPIKE).any()
