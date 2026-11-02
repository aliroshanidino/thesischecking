"""Attention-gated R-STDP (AGREL in TTFS, DECISIONS D24): only hidden units that caused the decision learn."""

import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.learning.rstdp import RSTDPRates
from biovision.ventral.rstdp_attention import AttentionRSTDP


def _net():
    return AttentionRSTDP(2, 2, {"maps": 3, "kernel": 3, "threshold": 2.0, "pool": [2, 2]},
                          {"maps_per_class": 1, "kernel": 2, "threshold": 1.0}, RSTDPRates(), 0.0, 6,
                          torch.device("cpu"), torch.Generator().manual_seed(0), {"gate": 0.5, "top": 4, "scale": 1.0})


def test_only_attended_hidden_maps_learn():
    net = _net()
    net.dec.layer.weight.zero_()
    net.dec.layer.weight[0, 0] = 0.9          # decision neuron 0 listens strongly to hidden map 0 only
    net.dec.layer.weight[0, 1] = 0.2          # map 1: weak synapse -> gated out
    x_in = torch.zeros(1, 2, 6, 6, dtype=torch.uint8)
    h = torch.full((1, 3, 4, 4), NO_SPIKE, dtype=torch.uint8)
    h[0, 0, 1, 1] = 1                          # hidden map 0 spiked early inside the decision's receptive field
    h[0, 1, 2, 2] = 1                          # map 1 also spiked, but its synapse is weak
    h[0, 2, 0, 0] = 5                          # map 2 spiked after the decision
    pooled = torch.full((1, 3, 2, 2), NO_SPIKE, dtype=torch.uint8)
    pooled[0, 0, 0, 0], pooled[0, 1, 1, 1], pooled[0, 2, 0, 0] = 1, 1, 5
    times = torch.full((2, 1, 1), NO_SPIKE, dtype=torch.uint8)
    times[0, 0, 0] = 3
    before = net.h.weight.clone()
    net._attend(x_in, pooled, h, (0, 0, 0), times, True, RSTDPRates())
    changed = (net.h.weight != before).flatten(1).any(1)
    assert changed.tolist() == [True, False, False] and net.updates == 1
