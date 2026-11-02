"""MNIST from the original IDX ``.gz`` files (md5-checked in ``download/``). Images on the 0..255 scale."""

from __future__ import annotations

import gzip
from pathlib import Path

import numpy as np
import torch


def _read(path: Path, offset: int, shape: tuple[int, ...]) -> np.ndarray:
    with gzip.open(path, "rb") as f:
        return np.frombuffer(f.read(), dtype=np.uint8, offset=offset).reshape(shape)


def load(root: Path, seed: int = 0, train_limit: int | None = None):
    """Returns ``(train_imgs [N,28,28] float, train_labels, test_imgs, test_labels)``. ``train_limit`` takes a
    seeded random subset of the training set (smoke runs only)."""
    root = Path(root)
    xtr = _read(root / "train-images-idx3-ubyte.gz", 16, (-1, 28, 28))
    ytr = _read(root / "train-labels-idx1-ubyte.gz", 8, (-1,))
    xte = _read(root / "t10k-images-idx3-ubyte.gz", 16, (-1, 28, 28))
    yte = _read(root / "t10k-labels-idx1-ubyte.gz", 8, (-1,))
    if train_limit:
        idx = np.random.default_rng(seed).permutation(len(xtr))[:train_limit]
        xtr, ytr = xtr[idx], ytr[idx]
    f = lambda a: torch.from_numpy(a.astype(np.float32))  # noqa: E731
    return f(xtr), ytr.tolist(), f(xte), yte.tolist()
