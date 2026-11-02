"""Caltech-101 face/motorbike (Kheradpisheh et al. 2018): grey images rescaled to 160 px height (aspect kept);
200 random training images per class, the rest for testing. Images are returned on the 0..255 scale."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image

CLASSES = ("Faces", "Motorbikes")


def letterbox(img: "Image.Image", size: int) -> "Image.Image":
    """Fit into ``size x size`` keeping the aspect ratio; the border is the mean colour (CLAUDE.md 4.2)."""
    w, h = img.size
    f = size / max(w, h)
    img = img.resize((max(1, round(w * f)), max(1, round(h * f))), Image.BILINEAR)
    a = np.asarray(img, dtype=np.float32)
    mean = tuple(int(v) for v in a.reshape(-1, a.shape[-1] if a.ndim == 3 else 1).mean(0))
    canvas = Image.new(img.mode, (size, size), mean if img.mode == "RGB" else mean[0])
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    return canvas


def load_gray(path: Path, height: int, scale: float = 0.0, colour: bool = False, square: int = 0) -> torch.Tensor:
    img = Image.open(path).convert("RGB" if colour else "L")
    if square:
        a = torch.from_numpy(np.asarray(letterbox(img, square), dtype=np.float32))
        return a.permute(2, 0, 1).contiguous() if colour else a
    if scale > 0:  # Mozafari et al. 2018: images scaled by a factor (0.5)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.BILINEAR)
    elif height > 0:  # height <= 0: keep the original size
        w = round(img.width * height / img.height)
        img = img.resize((w, height), Image.BILINEAR)
    return torch.from_numpy(np.asarray(img, dtype=np.float32))


def load(root: Path, seed: int, train_per_class: int = 200, height: int = 160, per_class: int = 0,
         scale: float = 0.0, classes: tuple | list = CLASSES, colour: bool = False, square: int = 0):
    """Returns ``(train_imgs, train_labels, test_imgs, test_labels)``; images are ``[H, W]`` float tensors.
    ``per_class > 0``: only that many random images per class are used (Mozafari et al. 2018: 435)."""
    rng = np.random.default_rng(seed)
    split = {"train": ([], []), "test": ([], [])}
    for label, cls in enumerate(classes):
        files = sorted((Path(root) / cls).glob("*.jpg"))
        order = rng.permutation(len(files))
        if per_class:
            order = order[:per_class]
        for rank, i in enumerate(order):
            part = "train" if rank < train_per_class else "test"
            split[part][0].append(load_gray(files[i], height, scale, colour, square))
            split[part][1].append(label)
    return (*split["train"], *split["test"])
