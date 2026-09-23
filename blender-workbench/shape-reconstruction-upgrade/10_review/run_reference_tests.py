"""Normal-Python tests for contour reconstruction and Blender mask comparison."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
EXTERNAL = UPGRADE / "05_external_tools"
if str(EXTERNAL) not in sys.path:
    sys.path.insert(0, str(EXTERNAL))

import reference_preprocess as rp

RUNTIME = UPGRADE / "demo" / "blender_runtime"
DEMO = UPGRADE / "demo"
results = []


def compare_case(name, reference, candidate, expected_holes):
    ref, _ = rp.load_mask(reference)
    cand, _ = rp.load_mask(candidate)
    report, overlay, difference = rp.compare_masks(
        ref, cand, alignment="none", tolerance_px=3.0,
        world_height=4.0, gate_iou=0.85, gate_boundary_f1=0.90
    )
    rp.save_json(RUNTIME / f"{name}_compare_report.json", report)
    rp.save_image(RUNTIME / f"{name}_compare_overlay.png", overlay)
    rp.save_image(RUNTIME / f"{name}_compare_difference.png", difference)
    passed = (
        report["quality_gate"]["pass"]
        and report["metrics"]["reference_holes"] == expected_holes
        and report["metrics"]["candidate_holes"] == expected_holes
    )
    results.append({"name": name, "status": "pass" if passed else "fail", "report": report})


compare_case(
    "contour",
    DEMO / "masks" / "combined.png",
    RUNTIME / "contour_blender_mask.png",
    0,
)
compare_case(
    "hole",
    DEMO / "masks" / "hole_test.png",
    RUNTIME / "hole_blender_mask.png",
    1,
)

for name, min_iou, holes in [
    ("combined", 0.98, 0),
    ("hole_test", 0.98, 1),
    ("ball", 0.98, 0),
    ("left_hand", 0.98, 0),
    ("right_hand", 0.98, 0),
]:
    payload = json.loads((DEMO / f"{name}.contours.json").read_text(encoding="utf-8"))
    extraction = payload["extraction"]
    passed = (
        extraction["reconstruction_iou"] >= min_iou
        and extraction["hole_count"] == holes
    )
    results.append({
        "name": f"contour_json_{name}",
        "status": "pass" if passed else "fail",
        "reconstruction_iou": extraction["reconstruction_iou"],
        "hole_count": extraction["hole_count"],
    })

report = {
    "schema": "ai-blender-reference-tests/v1",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "python": sys.version.split()[0],
    "status": "pass" if all(item["status"] == "pass" for item in results) else "fail",
    "tests": results,
}
(RUNTIME / "reference_runtime_tests.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False, indent=2))
if report["status"] != "pass":
    raise SystemExit(1)
