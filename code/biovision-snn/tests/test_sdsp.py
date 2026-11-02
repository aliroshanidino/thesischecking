import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.learning.flat_stdp import flat_stdp_delta
from biovision.learning.sdsp import sdsp_delta


def _case():
    w = torch.full((5,), 0.5)
    t_pre = torch.tensor([0, 2, 4, 6, NO_SPIKE], dtype=torch.uint8)
    v_before = torch.tensor([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])  # potential just before each step
    return w, t_pre, v_before


def test_sdsp_reduces_to_flat_stdp():
    w, t_pre, v_before = _case()
    flat = flat_stdp_delta(w, t_pre, 4, 0.1, 0.05)
    sdsp = sdsp_delta(w, t_pre, 4, v_before, v_gate=0.0, a_plus=0.1, a_minus=0.05, silent_ltd=True)
    assert torch.allclose(flat, sdsp)


def test_sdsp_silent_inputs_do_not_change():
    w, t_pre, v_before = _case()
    d = sdsp_delta(w, t_pre, 4, v_before, v_gate=0.0, a_plus=0.1, a_minus=0.05)
    assert d[4] == 0 and d[0] > 0 and d[3] < 0  # silent: none; causal: LTP; after the post spike: LTD


def test_sdsp_potential_gate_depresses_early_low_potential_inputs():
    w, t_pre, v_before = _case()
    d = sdsp_delta(w, t_pre, 4, v_before, v_gate=1.5, a_plus=0.1, a_minus=0.05)
    # pre at t=0 sees V=0 and pre at t=2 sees V=2: only the second is above the gate
    assert d[0] < 0 and d[1] > 0 and d[2] > 0


def test_sdsp_calcium_windows_stop_learning():
    w, t_pre, v_before = _case()
    d = sdsp_delta(w, t_pre, 4, v_before, 0.0, 0.1, 0.05, ltp_open=False, ltd_open=True)
    assert (d <= 0).all() and d[3] < 0
    d = sdsp_delta(w, t_pre, 4, v_before, 0.0, 0.1, 0.05, ltp_open=False, ltd_open=False)
    assert (d == 0).all()


def test_hasizh_threshold_is_bounded_and_tracks_firing_rate():
    from biovision.engine.sdnn import SDNN
    net = SDNN(1, [{"type": "conv", "maps": 2, "kernel": 3, "threshold": 2.0, "k": 1, "radius": 0,
                    "homeostasis": {"alpha": 0.05, "gamma": 0.5}}], T=4, device=torch.device("cpu"),
               generator=torch.Generator().manual_seed(0))
    x = torch.zeros(1, 1, 3, 3, dtype=torch.uint8)  # every input spikes at t = 0: the maps fire on every image
    for _ in range(400):
        net.stdp_step(0, x, 0.0, 0.0)
    th = net.layers[0].threshold
    # a map firing on every image settles at theta0 + gamma / alpha (Eq. 18 with r* = 1), calcium -> 1
    fired = th > 2.0 + 1e-6
    assert bool(fired.any()) and bool((th <= 2.0 + 0.5 / 0.05 + 1e-4).all())
    assert torch.allclose(net.calcium[0][fired], (th[fired] - 2.0) * 0.05 / 0.5)


def test_rsdsp_with_open_windows_equals_rstdp():
    from biovision.learning.rstdp import RSTDPRates
    from biovision.ventral.rstdp_global import RSTDPReadout
    g = torch.Generator().manual_seed(3)
    xs = []
    for _ in range(12):
        t = torch.randint(0, 6, (1, 3, 5, 5), generator=g).to(torch.uint8)
        t[torch.rand(t.shape, generator=g) < 0.4] = NO_SPIKE
        xs.append(t)
    ys = [i % 2 for i in range(12)]
    out = []
    for rule in ("stdp", "sdsp"):
        r = RSTDPReadout(3, 2, 2, 5, 4.0, RSTDPRates(), 0.0, 8, torch.device("cpu"), torch.Generator().manual_seed(0),
                         rule=rule, sdsp={"kappa": 0.0, "silent_ltd": True})
        for _ in range(3):
            r.train_epoch(xs, ys)
        out.append(r.layer.weight.clone())
    assert torch.allclose(out[0], out[1], atol=1e-6)


def test_rstdp_on_inputs_smaller_than_the_kernel():
    from biovision.learning.rstdp import RSTDPRates
    from biovision.ventral.rstdp_global import RSTDPReadout
    g = torch.Generator().manual_seed(5)
    xs = [torch.randint(0, 6, (1, 2, 4, 9), generator=g).to(torch.uint8) for _ in range(6)]  # height 4 < kernel 6
    r = RSTDPReadout(2, 2, 1, 6, 3.0, RSTDPRates(), 0.0, 8, torch.device("cpu"), torch.Generator().manual_seed(0))
    out = r.train_epoch(xs, [0, 1, 0, 1, 0, 1])
    assert out["hit"] + out["miss"] + out["silent"] == 1.0
