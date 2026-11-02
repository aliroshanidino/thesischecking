"""Data locations (DECISIONS D15): raw downloads are read-only; everything we produce goes under ``work``.

``Paths.from_config(cfg)`` reads ``cfg["paths"]``; relative entries are taken from the repo root, and the
environment variables ``BIOVISION_RAW`` / ``BIOVISION_WORK`` override them (used on the HPC).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve(value: str, env: str) -> Path:
    p = Path(os.environ.get(env, value))
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


@dataclass(frozen=True)
class Paths:
    raw: Path
    work: Path

    @property
    def proc(self) -> Path:
        return self.work / "proc"

    @property
    def cache(self) -> Path:
        return self.work / "cache"

    @property
    def runs(self) -> Path:
        return self.work / "runs"

    @classmethod
    def from_config(cls, cfg: dict) -> "Paths":
        p = cfg.get("paths", {})
        return cls(raw=_resolve(p.get("raw", "../download/datasets"), "BIOVISION_RAW"),
                   work=_resolve(p.get("work", "../work"), "BIOVISION_WORK"))
