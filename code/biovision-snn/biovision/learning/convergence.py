"""Convergence index of a layer (CLAUDE.md Section 5.1).

``C_l = (1 / n_w) * sum_w w (1 - w)``. When ``C_l < 0.01`` almost every weight is near 0 or 1:
stop learning and freeze the layer.
"""

from __future__ import annotations

import torch

FREEZE_BELOW = 0.01


def convergence_index(weight: torch.Tensor) -> float:
    return float((weight * (1 - weight)).mean())


def is_converged(weight: torch.Tensor, threshold: float = FREEZE_BELOW) -> bool:
    return convergence_index(weight) < threshold
