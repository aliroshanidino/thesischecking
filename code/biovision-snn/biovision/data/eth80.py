"""ETH-80: 8 categories x 10 object instances x 41 views. Grey images from ``eth80-cropped256`` (or
``cropped-close128``), resized to ``size x size``, 0..255 scale.

Protocols (the test objects are never seen during learning):

* ``random`` (Kheradpisheh et al. 2016 and 2018): ``train_instances`` (5) random instances of each category for
  training, the others for testing; a different split per seed.
* ``loo`` (Mozafari et al. 2018): leave-one-object-out cross-validation; fold ``f`` (0..9) tests the ``f``-th
  instance of every category and trains on the other nine.

``val_instances > 0`` (hyper-parameter search, D17): that many of the training instances of each class are held out
and returned in place of the test set, so no test object is ever loaded during the search. ``groups`` (the object
instance of every training image) allow grouped cross-validation inside the training set."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image

CLASSES = ("apple", "car", "cow", "cup", "dog", "horse", "pear", "tomato")


def load_gray(path: Path, size: int, colour: bool = False) -> torch.Tensor:
    """``[size, size]`` grey or ``[3, size, size]`` RGB (Phase 1), 0..255."""
    img = Image.open(path).convert("RGB" if colour else "L").resize((size, size), Image.BILINEAR)
    a = torch.from_numpy(np.asarray(img, dtype=np.float32))
    return a.permute(2, 0, 1).contiguous() if colour else a


def load(root: Path, seed: int, train_instances: int = 5, size: int = 160, val_instances: int = 0,
         protocol: str = "random", fold: int = 0, with_groups: bool = False, colour: bool = False):
    """Returns ``(train_x, train_y, test_x, test_y)`` (+ ``train_groups`` with ``with_groups``)."""
    rng = np.random.default_rng(seed)
    split = {"train": ([], [], []), "test": ([], [], [])}
    for label, cls in enumerate(CLASSES):
        instances = sorted(p for p in Path(root).iterdir() if p.is_dir() and p.name.rstrip("0123456789") == cls)
        if protocol == "loo":
            chosen = [i for i in range(len(instances)) if i != fold % len(instances)]
            chosen = rng.permutation(chosen).tolist()  # random validation instances (seed) inside the 9
        else:
            chosen = rng.choice(len(instances), train_instances, replace=False).tolist()
        held = set(chosen[:val_instances])
        for i, inst in enumerate(instances):
            if val_instances:
                if i not in chosen:
                    continue  # the real test objects are not loaded at all during the search
                part = "test" if i in held else "train"
            else:
                part = "train" if i in chosen else "test"
            for f in sorted(inst.glob("*.png")):
                split[part][0].append(load_gray(f, size, colour))
                split[part][1].append(label)
                split[part][2].append(label * 100 + i)
    out = (split["train"][0], split["train"][1], split["test"][0], split["test"][1])
    return (*out, split["train"][2]) if with_groups else out
