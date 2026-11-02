"""Image perturbations for the Phase 1 invariance tests (CLAUDE.md Phase 1): brightness, gamma, rescale, translation.

Images are ``[H, W]`` or ``[3, H, W]`` on the 0..255 scale; every perturbation keeps the image size.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


def brightness(img: torch.Tensor, s: float) -> torch.Tensor:
    return (img * s).clamp(0, 255)


def gamma(img: torch.Tensor, g: float) -> torch.Tensor:
    return 255.0 * (img.clamp(0, 255) / 255.0) ** g


def rescale(img: torch.Tensor, f: float) -> torch.Tensor:
    """Zoom by ``f`` about the centre; borders replicated when the content shrinks."""
    x = img.unsqueeze(0) if img.dim() == 2 else img
    C, H, W = x.shape
    h, w = max(2, round(H * f)), max(2, round(W * f))
    y = F.interpolate(x.unsqueeze(0), size=(h, w), mode="bilinear", align_corners=False)[0]
    if f >= 1:
        t, l = (h - H) // 2, (w - W) // 2
        y = y[:, t:t + H, l:l + W]
    else:
        pt, pl = (H - h) // 2, (W - w) // 2
        y = F.pad(y.unsqueeze(0), (pl, W - w - pl, pt, H - h - pt), mode="replicate")[0]
    return y[0] if img.dim() == 2 else y


def translate(img: torch.Tensor, d: int) -> torch.Tensor:
    """Horizontal shift by ``d`` pixels (border replicated)."""
    x = img.unsqueeze(0) if img.dim() == 2 else img
    W = x.shape[-1]
    p = abs(d)
    y = F.pad(x.unsqueeze(0), (p, p, 0, 0), mode="replicate")[0]
    y = y[..., p - d: p - d + W]
    return y[0] if img.dim() == 2 else y


def perturbations(cfg: dict) -> list[tuple[str, callable]]:
    out = []
    for s in cfg.get("brightness", []):
        out.append((f"brightness x{s}", lambda im, s=s: brightness(im, s)))
    for g in cfg.get("gamma", []):
        out.append((f"gamma {g}", lambda im, g=g: gamma(im, g)))
    for f in cfg.get("scale", []):
        out.append((f"scale {f}", lambda im, f=f: rescale(im, f)))
    for d in cfg.get("shift", []):
        out.append((f"shift {d}px", lambda im, d=d: translate(im, d)))
    return out
