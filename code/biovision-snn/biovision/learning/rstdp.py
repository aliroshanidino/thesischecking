"""Reward-modulated STDP (Mozafari et al. 2018; CLAUDE.md Section 5).

Reward (correct decision): ordinary flat STDP with rates ``(a_plus, a_minus)``.
Punishment (wrong decision): anti-STDP — causal inputs (pre at or before post) are depressed and late/silent
inputs potentiated — with rates ``(p_minus, p_plus)``: ``dw = -p_minus * w(1-w)`` if pre <= post,
``+p_plus * w(1-w)`` otherwise.

Adaptive rates (Mozafari et al. 2018, Eq. 8 as implemented in SpykeTorch): after each epoch, reward rates are
scaled by ``0.8 * miss_rate + 0.2`` and punishment rates by ``0.8 * hit_rate + 0.2`` (never below 20 %).
"""

from __future__ import annotations

from dataclasses import dataclass

import torch

from . import hw
from .flat_stdp import flat_stdp_update


@dataclass
class RSTDPRates:
    a_plus: float = 0.005     # reward, causal (LTP)
    a_minus: float = 0.0025   # reward, non-causal (LTD)
    p_minus: float = 0.005    # punishment, causal (depression)
    p_plus: float = 0.0005    # punishment, non-causal (potentiation)
    adaptive_min: float = 0.2
    adaptive_int: float = 0.8

    def scaled(self, hit_rate: float, miss_rate: float) -> "RSTDPRates":
        r = hw.rate(miss_rate * self.adaptive_int + self.adaptive_min)  # power of two in hardware mode
        p = hw.rate(hit_rate * self.adaptive_int + self.adaptive_min)
        return RSTDPRates(self.a_plus * r, self.a_minus * r, self.p_minus * p, self.p_plus * p,
                          self.adaptive_min, self.adaptive_int)

    def initial(self, n_classes: int) -> "RSTDPRates":
        """Rates before the first epoch: chance-level hit rate ``1 / n_classes``."""
        return self.scaled(1.0 / n_classes, 1.0 - 1.0 / n_classes)


def rstdp_update(weight: torch.Tensor, pre_times: torch.Tensor, winner: tuple[int, int, int],
                 post_times: torch.Tensor, rewarded: bool, rates: RSTDPRates, padding: int = 0) -> torch.Tensor:
    """Apply R-STDP for one winner ``(map, y, x)``; in place on ``weight`` ``[M, C, k, k]``."""
    if rewarded:
        return flat_stdp_update(weight, pre_times, [winner], post_times, rates.a_plus, rates.a_minus, padding)
    # anti-STDP: flat_stdp_update computes +a_plus*stab (causal) and -a_minus*stab (non-causal)
    return flat_stdp_update(weight, pre_times, [winner], post_times, -rates.p_minus, -rates.p_plus, padding)
