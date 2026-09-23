from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REFERENCE = REPO / "blender-workbench" / "references" / "hands-sphere-primary.png"
OUT = REPO / "blender-workbench" / "artifacts" / "reference_masks" / "v3"
OUT.mkdir(parents=True, exist_ok=True)
UPSCALE = 4


def clean(mask: np.ndarray, close_radius: int = 3, open_radius: int = 1) -> np.ndarray:
    if close_radius > 0:
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (close_radius * 2 + 1, close_radius * 2 + 1)
        )
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    if open_radius > 0:
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (open_radius * 2 + 1, open_radius * 2 + 1)
        )
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


if not REFERENCE.is_file():
    raise SystemExit(f"Reference not found: {REFERENCE}")
image = cv2.imdecode(np.fromfile(str(REFERENCE), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
if image is None:
    raise SystemExit(f"Cannot read {REFERENCE}")

if image.shape[2] == 4:
    bgr = image[:, :, :3]
    alpha = image[:, :, 3]
else:
    bgr = image
    alpha = np.full(image.shape[:2], 255, dtype=np.uint8)

hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
b, g, r = cv2.split(bgr)
sat = hsv[:, :, 1]

green = clean(
    np.where((g > 100) & (r < 180) & (b < 160) & (sat > 35) & (alpha > 10), 255, 0).astype(np.uint8),
    4,
    1,
)
orange = clean(
    np.where((r > 155) & (g > 45) & (g < 215) & (b < 120) & (sat > 45) & (alpha > 10), 255, 0).astype(np.uint8),
    3,
    1,
)
pink = clean(
    np.where((r > 185) & (b > 115) & (g < 235) & (sat > 20) & (alpha > 10), 255, 0).astype(np.uint8),
    4,
    1,
)
object_mask = clean(np.maximum.reduce([green, orange, pink]), 2, 1)

masks = {
    "object": object_mask,
    "green": green,
    "orange": orange,
    "pink": pink,
}


def write_png(path: Path, image_data: np.ndarray) -> None:
    ok, encoded = cv2.imencode(".png", image_data)
    if not ok:
        raise SystemExit(f"Could not encode {path}")
    encoded.tofile(str(path))


def smooth_upscale(mask: np.ndarray) -> np.ndarray:
    enlarged = cv2.resize(mask, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(enlarged, (5, 5), 0)
    return np.where(blurred >= 127, 255, 0).astype(np.uint8)


summary: dict[str, dict[str, int | str]] = {}
for name, mask in masks.items():
    path = OUT / f"hands_sphere_{name}_mask.png"
    write_png(path, mask)
    x4_path = OUT / f"hands_sphere_{name}_mask_x4.png"
    x4 = smooth_upscale(mask)
    write_png(x4_path, x4)
    summary[name] = {
        "path": str(path),
        "path_x4": str(x4_path),
        "foreground_pixels": int(np.count_nonzero(mask)),
        "foreground_pixels_x4": int(np.count_nonzero(x4)),
    }

preview = np.full_like(bgr, 255)
preview[object_mask > 0] = (232, 232, 232)
preview[green > 0] = (80, 210, 80)
preview[orange > 0] = (0, 130, 255)
preview[pink > 0] = (210, 150, 255)
preview_path = OUT / "hands_sphere_v3_masks_preview.png"
write_png(preview_path, preview)

summary_path = OUT / "hands_sphere_v3_masks_summary.json"
summary_path.write_text(
    json.dumps(
        {
            "reference": str(REFERENCE),
            "width": int(image.shape[1]),
            "height": int(image.shape[0]),
            "masks": summary,
            "preview": str(preview_path),
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)
print(summary_path)
