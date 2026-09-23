#!/usr/bin/env python3
"""Create an overlay/edge comparison between a reference and a render.

This is intentionally lightweight: it uses Pillow only, so it can run in most
Codex/Blender environments without OpenCV.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps


def fit_contain(image: Image.Image, size: tuple[int, int], background=(255, 255, 255, 255)) -> Image.Image:
    image = image.convert("RGBA")
    fitted = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, background)
    x = (size[0] - fitted.width) // 2
    y = (size[1] - fitted.height) // 2
    canvas.alpha_composite(fitted, (x, y))
    return canvas


def edge_mask(image: Image.Image, threshold: int = 28) -> Image.Image:
    gray = ImageOps.grayscale(image.convert("RGB"))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    return edges.point(lambda value: 255 if value >= threshold else 0, mode="1").convert("L")


def count_nonzero(mask: Image.Image) -> int:
    hist = mask.histogram()
    return sum(count for value, count in enumerate(hist) if value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--render", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--size", default="1024x768")
    parser.add_argument("--threshold", type=int, default=28)
    args = parser.parse_args()

    width, height = (int(part) for part in args.size.lower().split("x", 1))
    ref = fit_contain(Image.open(args.reference), (width, height))
    ren = fit_contain(Image.open(args.render), (width, height))

    ref_edges = edge_mask(ref, args.threshold)
    ren_edges = edge_mask(ren, args.threshold)
    intersection = ImageChops.logical_and(ref_edges.convert("1"), ren_edges.convert("1")).convert("L")
    union = ImageChops.logical_or(ref_edges.convert("1"), ren_edges.convert("1")).convert("L")

    i_count = count_nonzero(intersection)
    u_count = count_nonzero(union)
    edge_iou = i_count / u_count if u_count else 0.0

    overlay = Image.blend(ref.convert("RGBA"), ren.convert("RGBA"), 0.5)
    red_edges = Image.new("RGBA", (width, height), (255, 50, 30, 0))
    red_edges.putalpha(ref_edges.point(lambda value: 190 if value else 0))
    blue_edges = Image.new("RGBA", (width, height), (50, 130, 255, 0))
    blue_edges.putalpha(ren_edges.point(lambda value: 190 if value else 0))
    overlay.alpha_composite(red_edges)
    overlay.alpha_composite(blue_edges)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(args.out)

    report = {
        "reference": str(args.reference),
        "render": str(args.render),
        "overlay": str(args.out),
        "size": [width, height],
        "threshold": args.threshold,
        "edge_iou": round(edge_iou, 4),
        "reference_edge_pixels": count_nonzero(ref_edges),
        "render_edge_pixels": count_nonzero(ren_edges),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
