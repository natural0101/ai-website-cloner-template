"""Audit PNG/JPEG exposure and clipping outside Blender.

Uses OpenCV when available, otherwise Pillow. Example:
    python image_quality_audit.py render.png --out render.audit.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def _load_rgb(path: Path) -> np.ndarray:
    try:
        import cv2  # type: ignore

        bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if bgr is None:
            raise ValueError(f"Cannot read image: {path}")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    except ImportError:
        from PIL import Image  # type: ignore

        return np.asarray(Image.open(path).convert("RGB"))


def audit_image(path: str | Path) -> dict[str, Any]:
    image_path = Path(path).expanduser().resolve()
    rgb8 = _load_rgb(image_path)
    rgb = rgb8.astype(np.float32) / 255.0
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    any_exact_clip = np.any(rgb8 == 255, axis=2)
    full_exact_clip = np.all(rgb8 == 255, axis=2)
    any_near_clip = np.any(rgb8 >= 252, axis=2)
    full_near_clip = np.all(rgb8 >= 252, axis=2)

    metrics = {
        "path": str(image_path),
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "mean_luma": float(luma.mean()),
        "median_luma": float(np.median(luma)),
        "p01_luma": float(np.percentile(luma, 1)),
        "p05_luma": float(np.percentile(luma, 5)),
        "p95_luma": float(np.percentile(luma, 95)),
        "p99_luma": float(np.percentile(luma, 99)),
        "near_black_pct": float((luma < 0.02).mean() * 100.0),
        "near_white_pct": float((luma > 0.98).mean() * 100.0),
        "any_channel_exactly_clipped_pct": float(any_exact_clip.mean() * 100.0),
        "all_channels_exactly_clipped_pct": float(full_exact_clip.mean() * 100.0),
        "any_channel_near_clipped_pct": float(any_near_clip.mean() * 100.0),
        "all_channels_near_clipped_pct": float(full_near_clip.mean() * 100.0),
    }

    warnings: list[str] = []
    if metrics["all_channels_exactly_clipped_pct"] > 1.0:
        warnings.append("Exact full-white clipping exceeds 1%; inspect emitters and exposure.")
    if metrics["any_channel_exactly_clipped_pct"] > 5.0:
        warnings.append("Exact channel clipping exceeds 5%; saturated highlights may lose hue/detail.")
    if metrics["all_channels_near_clipped_pct"] > 2.0:
        warnings.append("Near-white plateau is large; preserve highlight texture before adding bloom.")
    if metrics["near_black_pct"] > 30.0:
        warnings.append("More than 30% is near-black; verify intentional background vs crushed detail.")
    if metrics["p95_luma"] >= 0.999:
        warnings.append("95th percentile is clipped; highlights occupy too much of the frame.")
    metrics["warnings"] = warnings
    metrics["status"] = "PASS" if not warnings else "REVIEW_REQUIRED"
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--out")
    args = parser.parse_args()
    report = audit_image(args.image)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        out = Path(args.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
