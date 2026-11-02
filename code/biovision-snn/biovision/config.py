"""YAML configuration (CLAUDE.md Section 6: every module is configurable, no magic numbers in code).

``load_config("configs/phase0_caltech.yaml")`` reads the file; a top-level ``base: <path>`` key names a
parent config whose values are deep-merged underneath. ``config_hash`` identifies a resolved config in
``results/registry.csv``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    parent = cfg.pop("base", None)
    if parent is not None:
        cfg = _merge(load_config(path.parent / parent), cfg)
    return cfg


def config_hash(cfg: dict[str, Any]) -> str:
    return hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:10]
