"""Lateral inhibition (CLAUDE.md Section 1.3.4 and 4.5).

* ``feature_wta``: at each position only the earliest map may fire (inference and learning).
* ``k_wta``: during learning, pick up to ``k`` winners per image; each winner inhibits its whole
  feature map and every map within ``radius`` (square neighbourhood) around it, so different maps
  learn different features (Kheradpisheh et al. 2018; SpykeTorch ``get_k_winners``).

Ties in spike time are broken by the larger potential at the firing step, then by the lower index.
"""

from __future__ import annotations

import numpy as np
import torch

from .spikes import NO_SPIKE


def _priority(times: torch.Tensor, v_fire: torch.Tensor | None) -> torch.Tensor:
    """Larger value = wins first: earlier spike, then larger potential. Silent neurons get -inf."""
    t = times.to(torch.float64)
    score = -t * 1e6
    if v_fire is not None:
        v = v_fire.to(torch.float64)
        # squash the potential into (0, 1) so it can only break ties between equal spike times
        score = score + torch.sigmoid(v / (v.abs().max() + 1e-12))
    return torch.where(times == NO_SPIKE, torch.full_like(score, float("-inf")), score)


def feature_wta(times: torch.Tensor, v_fire: torch.Tensor | None = None) -> torch.Tensor:
    """Keep at most one firing map per position (the earliest; ties -> larger potential, lower index).

    ``times``: ``[C, H, W]`` or batched ``[..., C, H, W]`` uint8 spike times. Returns a new tensor where
    losers are ``NO_SPIKE``.
    """
    score = _priority(times, v_fire)
    winner = score.argmax(dim=-3, keepdim=True)  # first index on exact ties
    keep = torch.zeros_like(times, dtype=torch.bool).scatter_(-3, winner, True) & (times != NO_SPIKE)
    return torch.where(keep, times, torch.full_like(times, NO_SPIKE))


def k_wta(times: torch.Tensor, k: int, radius: int, v_fire: torch.Tensor | None = None) -> list[tuple[int, int, int]]:
    """Select up to ``k`` learning winners ``(map, y, x)`` in order of priority.

    After each pick, the winner's map is excluded everywhere and all maps are excluded at positions
    with ``max(|dy|, |dx|) <= radius`` around it. Implemented as one sort of the fired neurons by priority (ties:
    lower flat index, as ``argmax``) and a greedy scan on the CPU, which gives exactly the winners of repeated
    ``argmax`` picks (``_k_wta_reference``) without one GPU synchronisation per winner.
    """
    score = _priority(times, v_fire).flatten()
    C, H, W = times.shape
    fired = torch.nonzero(torch.isfinite(score)).flatten()
    if fired.numel() == 0 or k <= 0:
        return []
    order = torch.argsort(-score[fired], stable=True)
    cand = fired[order].cpu().numpy()
    used = np.zeros(C, dtype=bool)
    blocked = np.zeros((H, W), dtype=bool)
    winners: list[tuple[int, int, int]] = []
    for idx in cand:
        c, rem = divmod(int(idx), H * W)
        y, x = divmod(rem, W)
        if used[c] or blocked[y, x]:
            continue
        winners.append((c, y, x))
        if len(winners) == k:
            break
        used[c] = True
        blocked[max(0, y - radius): y + radius + 1, max(0, x - radius): x + radius + 1] = True
    return winners


def _k_wta_reference(times: torch.Tensor, k: int, radius: int, v_fire: torch.Tensor | None = None):
    """Straightforward repeated-argmax version of ``k_wta`` (kept for the equivalence test)."""
    score = _priority(times, v_fire).clone()
    C, H, W = times.shape
    winners: list[tuple[int, int, int]] = []
    for _ in range(k):
        best = int(score.argmax())
        if score.view(-1)[best] == float("-inf"):
            break
        c, rem = divmod(best, H * W)
        y, x = divmod(rem, W)
        winners.append((c, y, x))
        score[c] = float("-inf")
        score[:, max(0, y - radius): y + radius + 1, max(0, x - radius): x + radius + 1] = float("-inf")
    return winners
