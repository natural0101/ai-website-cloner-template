#!/usr/bin/env python3
"""Validate a stylized hand-target JSON file.

Runs outside Blender. Uses jsonschema when available and adds semantic checks
that JSON Schema cannot express clearly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REQUIRED_LANDMARKS = {
    "wrist_inner",
    "wrist_outer",
    "palm_center",
    "palm_heel",
    "thumb_base",
    "thumb_tip",
    "web_thumb_index",
    "index_tip",
    "middle_tip",
    "ring_tip",
    "little_tip",
    "valley_index_middle",
    "valley_middle_ring",
    "valley_ring_little",
    "occlusion_enter",
    "occlusion_exit",
}

REQUIRED_CENTERLINES = {
    "palm",
    "thumb",
    "index",
    "middle",
    "ring",
    "little",
    "wrist",
}

REQUIRED_LAYERS = {
    "background",
    "hand_hidden_inferred",
    "object_front",
    "hand_visible",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def unique_ids(entries: list[dict[str, Any]], label: str, errors: list[str]) -> set[str]:
    ids = [str(entry.get("id", "")) for entry in entries]
    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate {label} ids: {duplicates}")
    return set(ids)


def semantic_validate(data: dict[str, Any], spec_path: Path, check_files: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    hand = data.get("hand", {})
    landmarks = hand.get("landmarks", [])
    landmark_ids = unique_ids(landmarks, "landmark", errors)
    missing_landmarks = sorted(REQUIRED_LANDMARKS - landmark_ids)
    if missing_landmarks:
        errors.append(f"missing landmarks: {missing_landmarks}")

    centerlines = hand.get("centerlines", [])
    centerline_ids = unique_ids(centerlines, "centerline", errors)
    missing_centerlines = sorted(REQUIRED_CENTERLINES - centerline_ids)
    if missing_centerlines:
        errors.append(f"missing centerlines: {missing_centerlines}")

    for line in centerlines:
        points = line.get("points", [])
        if len(points) < 2:
            errors.append(f"centerline {line.get('id')} has fewer than 2 points")
        radii = [point.get("radius", 0) for point in points]
        if any(not isinstance(radius, (int, float)) or radius <= 0 for radius in radii):
            errors.append(f"centerline {line.get('id')} has invalid radius")
        if line.get("id") in {"thumb", "index", "middle", "ring", "little"}:
            if radii and radii[-1] >= radii[0]:
                warnings.append(f"centerline {line.get('id')} does not taper toward tip")

    layers = data.get("layers", [])
    layer_ids = unique_ids(layers, "layer", errors)
    missing_layers = sorted(REQUIRED_LAYERS - layer_ids)
    if missing_layers:
        errors.append(f"missing layers: {missing_layers}")
    z_values = [entry.get("z_order") for entry in layers]
    if len(z_values) != len(set(z_values)):
        warnings.append("two or more layers share z_order")

    contours = hand.get("contours", {})
    if len(contours.get("visible", [])) < 8:
        errors.append("visible contour has fewer than 8 points")
    if len(contours.get("hidden", [])) < 2:
        errors.append("hidden contour is missing or too short")
    if not contours.get("negative_spaces"):
        warnings.append("negative_spaces list is empty")

    camera = data.get("camera", {})
    if camera.get("projection") != "ORTHO":
        errors.append("camera projection must be ORTHO for this patch")
    if camera.get("locked") is not True:
        errors.append("camera must be locked")

    gates = data.get("gates", {})
    if gates.get("mask_iou_min", 0) < 0.75:
        warnings.append("mask_iou_min is unusually low")
    if gates.get("boundary_f1_min", 0) < 0.85:
        warnings.append("boundary_f1_min is unusually low")

    if check_files:
        image = data.get("reference", {}).get("image")
        if image:
            image_path = (spec_path.parent / image).resolve()
            if not image_path.is_file():
                errors.append(f"reference image not found: {image_path}")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "landmarks": len(landmarks),
            "centerlines": len(centerlines),
            "layers": len(layers),
            "negative_spaces": len(contours.get("negative_spaces", [])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--schema", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    data = load_json(spec_path)
    report = semantic_validate(data, spec_path, args.check_files)

    schema_path = args.schema
    if schema_path is None:
        schema_path = Path(__file__).resolve().parents[1] / "02_spec" / "hand_target.schema.json"
    try:
        from jsonschema import Draft202012Validator

        schema = load_json(schema_path.resolve())
        schema_errors = sorted(
            Draft202012Validator(schema).iter_errors(data),
            key=lambda error: list(error.absolute_path),
        )
        for error in schema_errors:
            location = ".".join(str(part) for part in error.absolute_path) or "$"
            report["errors"].append(f"schema {location}: {error.message}")
        report["schema_validation"] = "pass" if not schema_errors else "fail"
    except ModuleNotFoundError:
        report["schema_validation"] = "skipped: jsonschema not installed"
        report["warnings"].append("install jsonschema for full schema validation")

    report["status"] = "pass" if not report["errors"] else "fail"
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
