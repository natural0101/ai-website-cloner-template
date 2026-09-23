from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


REPO = Path(__file__).resolve().parents[2]
WORKBENCH = REPO / "blender-workbench"
REFERENCE = WORKBENCH / "references" / "low_poly_character_fighting_pose_primary.png"
OUT_DIR = WORKBENCH / "artifacts" / "reference_masks" / "low_poly_character_fighting_pose"
OUT_JSON = OUT_DIR / "silhouette_contour.json"
OUT_PREVIEW = OUT_DIR / "silhouette_preview.png"


def largest_component(mask: np.ndarray) -> np.ndarray:
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    if component_count <= 1:
        raise RuntimeError("No foreground component found")
    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = int(np.argmax(areas) + 1)
    return (labels == largest_label).astype(np.uint8) * 255


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = np.fromfile(str(REFERENCE), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(REFERENCE)

    h, w = image.shape[:2]
    corner_samples = np.concatenate(
        [
            image[:32, :32].reshape(-1, 3),
            image[:32, -32:].reshape(-1, 3),
            image[-32:, :32].reshape(-1, 3),
            image[-32:, -32:].reshape(-1, 3),
        ],
        axis=0,
    )
    background = np.median(corner_samples, axis=0)
    diff = np.linalg.norm(image.astype(np.float32) - background.astype(np.float32), axis=2)
    bright = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) > 86
    mask = ((diff > 18) | bright).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    mask = largest_component(mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise RuntimeError("No contour found")
    contour = max(contours, key=cv2.contourArea)
    epsilon = 0.0025 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)

    x, y, bw, bh = cv2.boundingRect(contour)
    model_height = 2.58
    model_bottom = 0.04
    scale = model_height / float(bh)
    center_x = x + bw * 0.5
    bottom_y = y + bh
    contour_model = [
        {
            "x": round((float(px) - center_x) * scale, 5),
            "z": round((bottom_y - float(py)) * scale + model_bottom, 5),
            "px": int(px),
            "py": int(py),
        }
        for px, py in approx
    ]

    preview = image.copy()
    cv2.drawContours(preview, [approx.reshape(-1, 1, 2)], -1, (0, 220, 255), 2)
    cv2.rectangle(preview, (x, y), (x + bw, y + bh), (255, 120, 0), 1)
    ok, encoded_preview = cv2.imencode(".png", preview)
    if not ok:
        raise RuntimeError("Failed to encode silhouette preview")
    encoded_preview.tofile(str(OUT_PREVIEW))

    payload = {
        "schema_version": "1.0",
        "reference": str(REFERENCE),
        "image_size": {"width": w, "height": h},
        "background_bgr": [round(float(v), 3) for v in background.tolist()],
        "bbox_px": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
        "model_mapping": {"height": model_height, "bottom_z": model_bottom, "scale": scale, "center_x_px": center_x, "bottom_y_px": bottom_y},
        "contour_point_count": int(len(contour_model)),
        "contour": contour_model,
        "preview": str(OUT_PREVIEW),
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"json": str(OUT_JSON), "preview": str(OUT_PREVIEW), "points": len(contour_model)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
