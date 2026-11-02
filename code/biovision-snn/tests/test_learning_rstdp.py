"""R-STDP (Mozafari et al. 2018): reward = STDP, punishment = anti-STDP; adaptive rates; readout decisions."""

import torch

from biovision.engine.spikes import NO_SPIKE
from biovision.learning.rstdp import RSTDPRates, rstdp_update
from biovision.ventral.rstdp_global import RSTDPReadout


def test_reward_is_stdp_and_punishment_is_anti_stdp():
    rates = RSTDPRates(a_plus=0.1, a_minus=0.05, p_minus=0.1, p_plus=0.02)
    pre = torch.tensor([[[0, 9], [0, 9]]], dtype=torch.uint8)    # [C=1, 2, 2]: column 0 causal, column 1 late
    post = torch.tensor([[[5]]], dtype=torch.uint8)              # [M=1, 1, 1]
    for rewarded, sign_causal, sign_late in ((True, 1, -1), (False, -1, 1)):
        w = torch.full((1, 1, 2, 2), 0.5)
        rstdp_update(w, pre, (0, 0, 0), post, rewarded, rates)
        assert (w[0, 0, 0, 0] - 0.5) * sign_causal > 0 and (w[0, 0, 0, 1] - 0.5) * sign_late > 0


def test_adaptive_rates_never_below_20_percent():
    r = RSTDPRates(a_plus=1.0, a_minus=1.0, p_minus=1.0, p_plus=1.0)
    s = r.scaled(hit_rate=1.0, miss_rate=0.0)
    assert abs(s.a_plus - 0.2) < 1e-9 and abs(s.p_minus - 1.0) < 1e-9
    s = r.scaled(hit_rate=0.0, miss_rate=1.0)
    assert abs(s.a_plus - 1.0) < 1e-9 and abs(s.p_minus - 0.2) < 1e-9


def test_readout_learns_two_patterns():
    torch.manual_seed(0)
    g = torch.Generator().manual_seed(0)
    a = torch.full((1, 2, 6, 6), NO_SPIKE, dtype=torch.uint8); a[0, 0] = 0   # class 0: channel 0 fires early
    b = torch.full((1, 2, 6, 6), NO_SPIKE, dtype=torch.uint8); b[0, 1] = 0   # class 1: channel 1 fires early
    ro = RSTDPReadout(2, 2, 2, 3, threshold=5.0, rates=RSTDPRates(0.05, 0.03, 0.05, 0.01), dropout=0.0,
                      T=4, device=torch.device("cpu"), generator=g)
    for _ in range(60):
        ro.train_epoch([a, b], [0, 1])
    assert ro.evaluate([a, b], [0, 1])["acc"] == 1.0
