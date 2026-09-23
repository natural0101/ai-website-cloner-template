#!/usr/bin/env python3
"""Draw a human-reviewable target board from hand_target.json.

Runs outside Blender and requires Pillow only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def point_xy(point: dict, width: int, height: int) -> tuple[int, int]:
    return round(float(point["x"]) * width), round(float(point["y"]) * height)


def polyline_xy(points: Iterable[dict], width: int, height: int) -> list[tuple[int, int]]:
    return [point_xy(point, width, height) for point in points]


def draw_dashed(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    fill: tuple[int, int, int, int],
    width: int,
    dash: int = 12,
    gap: int = 8,
) -> None:
    import math

    for start, end in zip(points, points[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        ux, uy = dx / length, dy / length
        cursor = 0.0
        while cursor < length:
            segment_end = min(cursor + dash, length)
            a = (round(start[0] + ux * cursor), round(start[1] + uy * cursor))
            b = (round(start[0] + ux * segment_end), round(start[1] + uy * segment_end))
            draw.line([a, b], fill=fill, width=width)
            cursor += dash + gap


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    image_path = (spec_path.parent / data["reference"]["image"]).resolve()
    reference = Image.open(image_path).convert("RGBA")
    if args.scale != 1.0:
        new_size = (round(reference.width * args.scale), round(reference.height * args.scale))
        reference = reference.resize(new_size, Image.Resampling.LANCZOS)

    ref_width, ref_height = reference.size
    panel_width = max(300, round(ref_width * 0.36))
    canvas = Image.new("RGBA", (ref_width + panel_width, ref_height), (247, 247, 247, 255))

    veil = Image.new("RGBA", reference.size, (255, 255, 255, 0))
    ImageDraw.Draw(veil, "RGBA").rectangle((0, 0, ref_width, ref_height), fill=(255, 255, 255, 55))
    reference = Image.alpha_composite(reference, veil)
    canvas.alpha_composite(reference, (0, 0))

    draw = ImageDraw.Draw(canvas, "RGBA")
    font = ImageFont.load_default()
    line_width = max(2, round(min(ref_width, ref_height) / 250))

    contours = data["hand"]["contours"]
    visible = polyline_xy(contours["visible"], ref_width, ref_height)
    if len(visible) >= 2:
        draw.line(visible, fill=(255, 80, 30, 245), width=line_width * 2, joint="curve")

    hidden = polyline_xy(contours["hidden"], ref_width, ref_height)
    if len(hidden) >= 2:
        draw_dashed(draw, hidden, fill=(0, 190, 220, 245), width=line_width * 2)

    for negative in contours.get("negative_spaces", []):
        points = polyline_xy(negative, ref_width, ref_height)
        if len(points) >= 2:
            draw.line(points, fill=(190, 60, 220, 230), width=line_width * 2, joint="curve")

    for line in data["hand"]["centerlines"]:
        points = polyline_xy(line["points"], ref_width, ref_height)
        if len(points) >= 2:
            draw.line(points, fill=(30, 90, 255, 220), width=line_width, joint="curve")
        for point in line["points"]:
            x, y = point_xy(point, ref_width, ref_height)
            radius = max(2, round(float(point["radius"]) * ref_width))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(30, 90, 255, 85), width=line_width)

    landmark_colors = {
        "visible": (255, 20, 20, 255),
        "occluded": (0, 180, 220, 255),
        "inferred": (255, 160, 0, 255),
    }
    landmarks = data["hand"]["landmarks"]
    for index, landmark in enumerate(landmarks, start=1):
        x, y = point_xy(landmark, ref_width, ref_height)
        fill = landmark_colors[landmark["visibility"]]
        radius = max(5, line_width * 2)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=(255, 255, 255, 255), width=1)
        number = str(index)
        draw.text((x + radius + 2, y - radius - 1), number, font=font, fill=(0, 0, 0, 255), stroke_width=1, stroke_fill=(255, 255, 255, 230))

    panel_x = ref_width
    draw.rectangle((panel_x, 0, ref_width + panel_width, ref_height), fill=(250, 250, 250, 255))
    draw.line((panel_x, 0, panel_x, ref_height), fill=(170, 170, 170, 255), width=1)

    title = f"{data['hand']['id']} | {data['mode']}"
    draw.text((panel_x + 14, 14), title, font=font, fill=(0, 0, 0, 255))
    draw.text((panel_x + 14, 32), "camera: ORTHO / locked", font=font, fill=(0, 0, 0, 255))
    draw.text((panel_x + 14, 54), "orange: visible contour", font=font, fill=(255, 80, 30, 255))
    draw.text((panel_x + 14, 70), "cyan: hidden inferred contour", font=font, fill=(0, 150, 180, 255))
    draw.text((panel_x + 14, 86), "blue: centerlines + radii", font=font, fill=(30, 90, 255, 255))
    draw.text((panel_x + 14, 102), "purple: negative spaces", font=font, fill=(160, 40, 190, 255))

    y = 132
    row_height = 22
    for index, landmark in enumerate(landmarks, start=1):
        color = landmark_colors[landmark["visibility"]]
        draw.ellipse((panel_x + 14, y + 3, panel_x + 24, y + 13), fill=color)
        label = f"{index:02d}  {landmark['id']}  [{landmark['visibility']}]"
        draw.text((panel_x + 32, y), label, font=font, fill=(10, 10, 10, 255))
        y += row_height
        if y > ref_height - 28:
            draw.text((panel_x + 14, ref_height - 22), "legend truncated: inspect JSON", font=font, fill=(130, 0, 0, 255))
            break

    result = canvas.convert("RGB")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, quality=95)
    print(json.dumps({"status": "pass", "output": str(args.output), "size": list(result.size)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
