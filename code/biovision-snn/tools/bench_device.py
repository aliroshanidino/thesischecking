"""Throughput of the current pipeline per device: retina (P/K) -> latency code -> S1 (12 maps, 5x5x6, IF,
feature WTA) on the 3-level pyramid of a 256^2 RGB image, plus one k-WTA + flat-STDP learning step.
Usage: python tools/bench_device.py [--n 30] [--devices cpu,cuda] [--threads 12]
"""

from __future__ import annotations

import argparse
import time

import torch
import torch.nn.functional as F

from biovision.engine.inhibition import feature_wta, k_wta
from biovision.engine.neurons import conv_potentials, if_fire
from biovision.engine.spikes import to_binary
from biovision.learning.flat_stdp import flat_stdp_update
from biovision.retina.dog import parvo_konio
from biovision.retina.latency import intensity_to_latency

T, SIZES = 15, (256, 181, 128)


def one_image(img, w, learn):
    for s in SIZES:
        x = F.interpolate(img[None], size=(s, s), mode="bilinear", align_corners=False)[0]
        times = intensity_to_latency(parvo_konio(x), T, theta_in=0.02)
        pot = conv_potentials(to_binary(times, T), w, padding=2)
        out, v = if_fire(pot, 10.0)
        out = feature_wta(out, v)
        if learn and s == SIZES[0]:
            winners = k_wta(out, k=5, radius=2, v_fire=v)
            flat_stdp_update(w, times, winners, out, 0.004, 0.003, padding=2)
    return out


def bench(device: str, n: int, learn: bool) -> float:
    dev = torch.device(device)
    g = torch.Generator().manual_seed(0)
    imgs = [torch.rand(3, 256, 256, generator=g).to(dev) for _ in range(4)]
    w = torch.rand(12, 6, 5, 5, generator=g).to(dev)
    for i in range(3):  # warm-up (CUDA context, cuDNN autotune)
        one_image(imgs[i % 4], w, learn)
    if dev.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    for i in range(n):
        one_image(imgs[i % 4], w, learn)
    if dev.type == "cuda":
        torch.cuda.synchronize()
    return n / (time.perf_counter() - t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--devices", default="cpu,cuda")
    ap.add_argument("--threads", type=int, default=12)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    for d in a.devices.split(","):
        if d == "cuda" and not torch.cuda.is_available():
            print("cuda: not available")
            continue
        name = torch.cuda.get_device_name(0) if d == "cuda" else f"CPU, {torch.get_num_threads()} threads"
        inf = bench(d, a.n, learn=False)
        lrn = bench(d, max(5, a.n // 2), learn=True)
        print(f"{d:5s} ({name}): inference {inf:6.1f} img/s | with STDP step {lrn:6.1f} img/s")


if __name__ == "__main__":
    main()
