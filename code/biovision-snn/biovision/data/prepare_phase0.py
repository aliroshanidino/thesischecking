"""Unpack the Phase 0 datasets from the verified archives in ``paths.raw`` into ``paths.proc`` (idempotent).

* Caltech-101: only ``Faces`` and ``Motorbikes`` (Kheradpisheh et al. 2018, Caltech face/motorbike).
* ETH-80: ``eth80-cropped256`` images (segmentation maps skipped).
* MNIST is read directly from the ``.gz`` files (``data/mnist.py``).

    python -m biovision.data.prepare_phase0 [--config configs/base.yaml]
"""

from __future__ import annotations

import argparse
import io
import tarfile
import zipfile
from pathlib import Path

from ..config import load_config
from ..paths import Paths

CALTECH_CLASSES = ("Faces", "Motorbikes", "airplanes", "Leopards")  # Phase 0: first two; Phase 1: colour 4-class


def prepare_caltech(raw: Path, proc: Path) -> Path:
    out = proc / "caltech101"
    if all((out / c).is_dir() and any((out / c).iterdir()) for c in CALTECH_CLASSES):
        return out
    with zipfile.ZipFile(raw / "caltech101" / "caltech-101.zip") as z:
        inner = io.BytesIO(z.read("caltech-101/101_ObjectCategories.tar.gz"))
    with tarfile.open(fileobj=inner, mode="r:gz") as t:
        for m in t.getmembers():
            parts = Path(m.name).parts  # 101_ObjectCategories/<class>/image_0001.jpg
            if m.isfile() and len(parts) == 3 and parts[1] in CALTECH_CLASSES:
                dst = out / parts[1] / parts[2]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(t.extractfile(m).read())
    return out


def prepare_eth80(raw: Path, proc: Path, variant: str = "cropped256") -> Path:
    """``variant``: ``cropped256`` (SDNN runs) or ``cropped-close128`` (Mozafari 2018)."""
    out = proc / "eth80" / variant
    if out.is_dir() and sum(1 for _ in out.rglob("*.png")) == 3280:
        return out
    with tarfile.open(raw / "eth80" / f"eth80-{variant}.tgz", "r:gz") as t:
        for m in t.getmembers():
            parts = Path(m.name).parts  # eth80-cropped256/<obj>/<obj>-<tilt>-<pan>.png
            if m.isfile() and len(parts) == 3 and parts[2].endswith(".png"):
                dst = out / parts[1] / parts[2]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(t.extractfile(m).read())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/base.yaml")
    paths = Paths.from_config(load_config(ap.parse_args().config))
    paths.proc.mkdir(parents=True, exist_ok=True)
    c = prepare_caltech(paths.raw, paths.proc)
    print("caltech:", {k: len(list((c / k).glob("*.jpg"))) for k in CALTECH_CLASSES})
    for variant in ("cropped256", "cropped-close128"):
        e = prepare_eth80(paths.raw, paths.proc, variant)
        print(f"eth80 {variant}:", sum(1 for _ in e.rglob("*.png")), "images in", len(list(e.iterdir())), "object folders")


if __name__ == "__main__":
    main()
