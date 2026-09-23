"""Initialize a non-destructive v4 working copy of the comforting cat.

The currently open Blender scene is checkpointed first. The approved v3
TRUE_360 source is then opened read-only and immediately saved under a new v4
working filename, so the v3 .blend is never overwritten.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v3_true3d.blend").resolve()
WORKING_BLEND = (BLEND_DIR / "comforting_cat_v4_face_geometry_working.blend").resolve()


def assert_under(path: Path, root: Path) -> None:
    path.relative_to(root)


for directory in (CHECKPOINT_DIR, REPORT_DIR):
    assert_under(directory, WORKBENCH)
    directory.mkdir(parents=True, exist_ok=True)

assert_under(SOURCE_BLEND, WORKBENCH)
assert_under(WORKING_BLEND, WORKBENCH)
if not SOURCE_BLEND.exists():
    raise FileNotFoundError(SOURCE_BLEND)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
live_checkpoint = (CHECKPOINT_DIR / f"live_scene_before_comforting_cat_v4_{timestamp}.blend").resolve()
assert_under(live_checkpoint, WORKBENCH)

checks = [
    "ops.object.modifier_apply",
    "ops.export_scene.gltf",
    "ops.wm.open_mainfile",
    "ops.wm.save_as_mainfile",
    "data.materials.new",
    "types.GeometryNodeTree",
]


def has_capability(path: str) -> bool:
    current = bpy
    for part in path.split("."):
        if not hasattr(current, part):
            return False
        current = getattr(current, part)
    return True


capability_probe = {
    "blender_version": ".".join(map(str, bpy.app.version)),
    "python_version": sys.version.split()[0],
    "background": bool(bpy.app.background),
    "capabilities": {name: has_capability(name) for name in checks},
}

if not all(capability_probe["capabilities"].values()):
    raise RuntimeError(f"Required Blender capabilities missing: {capability_probe}")

bpy.ops.wm.save_as_mainfile(filepath=str(live_checkpoint))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
bpy.context.scene["comforting_cat_source_asset"] = "comforting_cat_v3_true3d"
bpy.context.scene["comforting_cat_target_mode"] = "TRUE_360"
bpy.context.scene["comforting_cat_v4_stage"] = "INITIALIZATION"
bpy.context.scene["comforting_cat_v4_dominant_defect"] = "head_and_face_proportions"
bpy.ops.wm.save_as_mainfile(filepath=str(WORKING_BLEND))

report = {
    "asset": "comforting_cat_v4_face_geometry",
    "stage": "INITIALIZATION",
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "live_scene_checkpoint": str(live_checkpoint),
    "working_blend": str(WORKING_BLEND),
    "capability_probe": capability_probe,
    "object_count": len(bpy.data.objects),
    "mesh_count": len(bpy.data.meshes),
    "material_count": len(bpy.data.materials),
    "source_preserved": SOURCE_BLEND != WORKING_BLEND,
}
(REPORT_DIR / "comforting_cat_v4_initialization_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("COMFORTING_CAT_V4_INITIALIZATION=" + json.dumps(report, ensure_ascii=False))
