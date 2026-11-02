"""Device selection and run metadata (DECISIONS D14: laptop RTX 3050 GPU, HPC CPU).

Config key ``device``: ``auto`` (CUDA if available, else CPU), ``cpu``, or ``cuda[:N]``.
Numbers inside one results table must come from a single device; ``describe`` goes into every run dir.
"""

from __future__ import annotations

import platform

import torch


def resolve_device(name: str = "auto") -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(name)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("config asks for CUDA but no GPU is available")
    return device


def set_deterministic(enabled: bool = True) -> None:
    """Deterministic convolutions so that STDP runs are repeatable on the GPU."""
    torch.backends.cudnn.deterministic = enabled
    torch.backends.cudnn.benchmark = not enabled
    torch.use_deterministic_algorithms(enabled, warn_only=True)


def describe(device: torch.device) -> dict[str, str]:
    info = {"device": str(device), "torch": torch.__version__, "host": platform.node(),
            "threads": str(torch.get_num_threads())}
    if device.type == "cuda":
        info |= {"gpu": torch.cuda.get_device_name(device), "cuda": str(torch.version.cuda)}
    return info
