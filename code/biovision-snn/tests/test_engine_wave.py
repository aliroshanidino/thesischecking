"""CLAUDE.md Section 6.1: wave engine: no neuron fires more than once per wave.
Also: wave 1 is feed-forward, feedback from wave n reaches wave n + 1 (Section 4.1)."""

import torch

from biovision.engine.inhibition import feature_wta
from biovision.engine.neurons import conv_potentials, if_fire
from biovision.engine.spikes import NO_SPIKE, onsets, to_binary
from biovision.engine.wave import Feedback, WaveEngine

T = 15


class IFConv:
    """Minimal S-layer: convolution + IF + feature WTA, weights shared over positions."""

    def __init__(self, name, c_in, c_out, k, threshold, seed):
        g = torch.Generator().manual_seed(seed)
        self.name = name
        self.weight = torch.rand(c_out, c_in, k, k, generator=g)
        self.threshold = threshold
        self.k = k
        self.seen_feedback = []

    def forward(self, times, feedback):
        self.seen_feedback.append(feedback)
        pot = conv_potentials(to_binary(times, T), self.weight, padding=self.k // 2)
        out, v = if_fire(pot, self.threshold)
        return feature_wta(out, v)


def test_if_neuron_fires_at_most_once_and_at_first_crossing():
    pot = torch.tensor([0.0, 0.5, 1.25, 0.75, 2.0]).view(5, 1, 1, 1)  # crosses 1.0 at t=2 (and again at 4)
    times, v = if_fire(pot, 1.0)
    assert int(times) == 2 and float(v) == 1.25
    silent, _ = if_fire(pot, 5.0)
    assert int(silent) == NO_SPIKE


def test_no_neuron_fires_twice_per_wave():
    g = torch.Generator().manual_seed(1)
    x = torch.randint(0, T, (6, 32, 32), generator=g, dtype=torch.uint8)
    x[torch.rand(x.shape, generator=g) < 0.7] = NO_SPIKE
    s1 = IFConv("S1", 6, 12, 5, threshold=8.0, seed=2)
    s2 = IFConv("S2", 12, 16, 5, threshold=6.0, seed=3)
    history = WaveEngine([s1, s2]).run(x, n_waves=3)
    assert len(history) == 3
    for wave in history:
        for name in ("S1", "S2"):
            times = wave[name]
            assert times.dtype == torch.uint8
            ev = onsets(to_binary(times, T))
            assert float(ev.min()) >= 0 and float(ev.sum(0).max()) <= 1
            assert int((times != NO_SPIKE).sum(0).max()) <= 1  # feature WTA
    assert (history[0]["S1"] != NO_SPIKE).any()  # the layers are not silent


def test_feedback_reaches_the_next_wave_only():
    s1 = IFConv("S1", 1, 2, 3, threshold=1.0, seed=0)
    calls = []

    def feedback_fn(outputs, previous):
        calls.append(len(calls))
        return Feedback(a=torch.full((4, 4), float(len(calls))))

    x = torch.zeros(1, 4, 4, dtype=torch.uint8)
    WaveEngine([s1], feedback_fn=feedback_fn).run(x, n_waves=3)
    seen = s1.seen_feedback
    assert seen[0].a is None and seen[0].g is None and seen[0].phi is None  # wave 1: a(x) = 0
    assert float(seen[1].a[0, 0]) == 1.0 and float(seen[2].a[0, 0]) == 2.0


def test_lif_leaks_and_matches_if_for_long_tau():
    from biovision.engine.sdnn import ConvLayer, conv_potentials

    times = torch.tensor([0, 5], dtype=torch.uint8).view(1, 2, 1, 1)       # two inputs, at t=0 and t=5
    w = torch.ones(1, 2, 1, 1)
    if_layer = ConvLayer(maps=1, kernel=1, threshold=1.5, k=1, radius=0, weight=w)
    lif = ConvLayer(maps=1, kernel=1, threshold=1.5, k=1, radius=0, neuron="lif", tau=2.0, weight=w)
    p_if = conv_potentials(times, if_layer, 8)[:, 0, 0, 0, 0]
    p_lif = conv_potentials(times, lif, 8)[:, 0, 0, 0, 0]
    assert p_if[4] == 1 and p_if[5] == 2
    assert p_lif[4] < 0.2 and p_lif[5] < 1.5     # the first input has leaked away: no coincidence, no spike
    slow = ConvLayer(maps=1, kernel=1, threshold=1.5, k=1, radius=0, neuron="lif", tau=1e9, weight=w)
    assert torch.allclose(conv_potentials(times, slow, 8)[:, 0, 0, 0, 0], p_if, atol=1e-5)


def test_schedule_doubles_rate_and_freezes_map_at_budget():
    from biovision.engine.sdnn import SDNN
    torch.manual_seed(0)
    spec = [{"type": "conv", "maps": 1, "kernel": 3, "threshold": 1.0, "k": 1, "radius": 0,
             "schedule": {"a_start": 0.01, "a_max": 0.04, "every": 2, "ratio": 0.75, "budget": 5}}]
    net = SDNN(1, spec, T=4, device=torch.device("cpu"), generator=torch.Generator().manual_seed(0))
    x = torch.zeros(1, 1, 3, 3, dtype=torch.uint8)  # every input fires at t=0 -> pure LTP
    w0 = net.layers[0].weight.clone()
    deltas = []
    for _ in range(7):
        before = net.layers[0].weight.clone()
        net.stdp_step(0, x, 0.004, 0.003)
        stab = before * (1 - before)
        deltas.append(float(((net.layers[0].weight - before) / stab).mean()))
    assert [round(d, 4) for d in deltas[:5]] == [0.01, 0.01, 0.02, 0.02, 0.04]
    assert deltas[5] == 0 and deltas[6] == 0 and int(net.wins[0][0]) == 5
    assert (net.layers[0].weight > w0).all()
