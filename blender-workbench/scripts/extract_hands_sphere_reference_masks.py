from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


REFERENCE_PATH = Path(r"C:\Users\se-20\AppData\Local\Temp\codex-clipboard-22475c29-ff69-43c5-b7e8-5578bbedfa52.png")
OUT_DIR = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output\reference_masks")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_mask(mask: np.ndarray, close_size=5, open_size=3) -> np.ndarray:
    close_kernel = np.ones((close_size, close_size), np.uint8)
    open_kernel = np.ones((open_size, open_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel)
    return mask


def contours_for(mask: np.ndarray, epsilon_ratio: float, min_area: int):
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    if hierarchy is None:
        return polygons
    hierarchy = hierarchy[0]
    for index, contour in enumerate(contours):
        parent = hierarchy[index][3]
        if parent != -1:
            continue
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        epsilon = epsilon_ratio * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
        if len(approx) < 3:
            continue
        holes = []
        child = hierarchy[index][2]
        while child != -1:
            child_contour = contours[child]
            child_area = cv2.contourArea(child_contour)
            if child_area >= 24:
                child_epsilon = epsilon_ratio * cv2.arcLength(child_contour, True)
                child_approx = cv2.approxPolyDP(child_contour, child_epsilon, True).reshape(-1, 2)
                if len(child_approx) >= 3:
                    holes.append([[int(x), int(y)] for x, y in child_approx.tolist()])
            child = hierarchy[child][0]
        polygons.append(
            {
                "area": float(area),
                "points": [[int(x), int(y)] for x, y in approx.tolist()],
                "holes": holes,
                "bbox": [int(v) for v in cv2.boundingRect(contour)],
            }
        )
    polygons.sort(key=lambda item: item["area"], reverse=True)
    return polygons


image = cv2.imread(str(REFERENCE_PATH), cv2.IMREAD_UNCHANGED)
if image is None:
    raise SystemExit(f"Cannot read {REFERENCE_PATH}")

if image.shape[2] == 4:
    bgr = image[:, :, :3]
    alpha = image[:, :, 3]
else:
    bgr = image
    alpha = np.full(image.shape[:2], 255, dtype=np.uint8)

hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
b, g, r = cv2.split(bgr)

# These ranges are intentionally based on the supplied reference, not generic color names.
green_mask = ((g > 105) & (r < 175) & (b < 140) & (alpha > 10)).astype(np.uint8) * 255
orange_mask = ((r > 165) & (g > 55) & (g < 205) & (b < 95) & (alpha > 10)).astype(np.uint8) * 255
pink_mask = ((r > 185) & (b > 125) & (g < 225) & (alpha > 10)).astype(np.uint8) * 255

# Remove pale background/card pixels from pink.
sat = hsv[:, :, 1]
pink_mask = np.where((pink_mask > 0) & (sat > 22), 255, 0).astype(np.uint8)

masks = {
    "green": clean_mask(green_mask, 7, 3),
    "orange": clean_mask(orange_mask, 5, 2),
    "pink": clean_mask(pink_mask, 7, 3),
}

layers = {
    "green": {
        "color": [0.48, 0.82, 0.27, 1.0],
        "y": -0.18,
        "thickness": 0.14,
        "bevel": 0.028,
        "polygons": contours_for(masks["green"], 0.0015, 220),
    },
    "orange": {
        "color": [0.96, 0.40, 0.03, 1.0],
        "y": -0.42,
        "thickness": 0.16,
        "bevel": 0.032,
        "polygons": contours_for(masks["orange"], 0.0013, 130),
    },
    "pink": {
        "color": [1.0, 0.70, 0.80, 1.0],
        "y": -0.50,
        "thickness": 0.13,
        "bevel": 0.025,
        "polygons": contours_for(masks["pink"], 0.0015, 180),
    },
}

preview = np.full_like(bgr, 255)
colors = {"green": (80, 210, 80), "orange": (0, 130, 255), "pink": (210, 150, 255)}
for name, mask in masks.items():
    preview[mask > 0] = colors[name]

json_path = OUT_DIR / "hands_sphere_reference_masks.json"
preview_path = OUT_DIR / "hands_sphere_reference_masks_preview.png"
json_path.write_text(
    json.dumps(
        {
            "source": str(REFERENCE_PATH),
            "width": int(image.shape[1]),
            "height": int(image.shape[0]),
            "px_per_unit": 100.0,
            "layers": layers,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
cv2.imwrite(str(preview_path), preview)

print(json.dumps({"json": str(json_path), "preview": str(preview_path), "counts": {k: len(v["polygons"]) for k, v in layers.items()}}, indent=2))
