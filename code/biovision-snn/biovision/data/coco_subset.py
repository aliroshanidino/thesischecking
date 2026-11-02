"""COCO 2017 subset selection (CLAUDE.md Section 3.7): classes person, car, bird; at most ``per_class``
train images per class (seeded random sample); all val2017 images that contain any of the classes.

Reads the official ``annotations_trainval2017.zip`` directly and writes, into ``out_dir``:
* ``coco_urls.txt``: ``split image_id file_name coco_url`` per selected image;
* ``instances_subset_{train,val}2017.json``: the selected images with only the chosen classes' annotations
  (segmentations kept: masks give the readout cell labels, Section 4.7; boxes are never a training target).

Standard library only, so it runs on the laptop or on the HPC:
    python -m biovision.data.coco_subset <annotations_trainval2017.zip> <out_dir> [--per-class 3000] [--seed 0]
"""

from __future__ import annotations

import argparse
import json
import random
import zipfile
from collections import defaultdict
from pathlib import Path

CLASSES = ("person", "car", "bird")


def _load(zf: zipfile.ZipFile, split: str) -> dict:
    with zf.open(f"annotations/instances_{split}.json") as f:
        return json.load(f)


def select(data: dict, classes: tuple[str, ...], per_class: int | None, seed: int) -> tuple[list[int], dict]:
    """Image ids to keep and the filtered annotation dict (non-crowd instances of ``classes`` only)."""
    cat_ids = {c["id"]: c["name"] for c in data["categories"] if c["name"] in classes}
    by_class: dict[int, set[int]] = defaultdict(set)
    for a in data["annotations"]:
        if a["category_id"] in cat_ids and not a.get("iscrowd", 0):
            by_class[a["category_id"]].add(a["image_id"])
    rng = random.Random(seed)
    keep: set[int] = set()
    for cid in sorted(cat_ids):
        ids = sorted(by_class[cid])
        if per_class is not None and len(ids) > per_class:
            ids = rng.sample(ids, per_class)
        keep.update(ids)
    images = [im for im in data["images"] if im["id"] in keep]
    anns = [a for a in data["annotations"] if a["image_id"] in keep and a["category_id"] in cat_ids]
    subset = {
        "info": data.get("info", {}),
        "licenses": data.get("licenses", []),
        "categories": [c for c in data["categories"] if c["id"] in cat_ids],
        "images": images,
        "annotations": anns,
    }
    return sorted(keep), subset


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("annotations_zip")
    ap.add_argument("out_dir")
    ap.add_argument("--per-class", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    lines = []
    with zipfile.ZipFile(args.annotations_zip) as zf:
        for split, per_class in (("train2017", args.per_class), ("val2017", None)):
            data = _load(zf, split)
            ids, subset = select(data, CLASSES, per_class, args.seed)
            (out / f"instances_subset_{split}.json").write_text(json.dumps(subset), encoding="utf-8")
            for im in subset["images"]:
                lines.append(f"{split} {im['id']} {im['file_name']} {im['coco_url']}")
            counts = defaultdict(set)
            for a in subset["annotations"]:
                counts[a["category_id"]].add(a["image_id"])
            names = {c["id"]: c["name"] for c in subset["categories"]}
            print(f"{split}: {len(ids)} images; per class: " + ", ".join(f"{names[c]} {len(v)}" for c, v in sorted(counts.items())))
    (out / "coco_urls.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} urls to {out / 'coco_urls.txt'}")


if __name__ == "__main__":
    main()
