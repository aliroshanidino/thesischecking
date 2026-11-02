"""Figures for the reports: learned features (back-projection, Kheradpisheh et al. 2018), convergence curves,
confusion matrices. Matplotlib with the Agg backend (no display needed)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

from ..engine.sdnn import ConvLayer, PoolLayer  # noqa: E402


@torch.no_grad()
def reconstruct_features(layers, input_kernels: list[torch.Tensor], upto: int) -> torch.Tensor:
    """Preferred feature of every map of conv layer ``upto`` as an image: each layer's feature is the
    weighted sum of the previous layer's features placed on its (strided) receptive field."""
    feats = torch.stack([k.float() for k in input_kernels]).cpu()       # [C0, s, s]
    stride = 1
    for i, layer in enumerate(layers[: upto + 1]):
        if isinstance(layer, PoolLayer):
            stride *= layer.stride
            continue
        w = layer.weight.detach().float().cpu()                         # [M, C, k, k]
        feats = F.conv_transpose2d(w, feats.unsqueeze(1), stride=stride)[:, 0]
    return feats


def feature_grid(feats: torch.Tensor, path: Path, title: str, cols: int = 10) -> None:
    n = feats.shape[0]
    cols = min(cols, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(1.3 * cols, 1.3 * rows + 0.4), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for i in range(n):
        f = feats[i].numpy()
        m = np.abs(f).max() or 1.0
        axes.flat[i].imshow(f / m, cmap="gray", vmin=-1, vmax=1)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def convergence_plot(curves: dict[str, list[tuple[int, float]]], path: Path, freeze_below: float) -> None:
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for name, c in curves.items():
        ax.plot([p[0] for p in c], [p[1] for p in c], label=name)
    ax.axhline(freeze_below, color="gray", ls=":", lw=1)
    ax.set_xlabel("iteration (images) per layer")
    ax.set_ylabel("convergence index $C_l$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def confusion_plot(cm: list[list[int]], classes: list[str], path: Path, title: str) -> None:
    cm = np.asarray(cm, dtype=float)
    norm = cm / cm.sum(axis=1, keepdims=True).clip(min=1)
    fig, ax = plt.subplots(figsize=(1 + 0.45 * len(classes), 0.8 + 0.45 * len(classes)))
    ax.imshow(norm, cmap="magma", vmin=0, vmax=1)
    ax.set_xticks(range(len(classes)), classes, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(classes)), classes, fontsize=7)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=6, color="w" if norm[i, j] < 0.6 else "k")
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
