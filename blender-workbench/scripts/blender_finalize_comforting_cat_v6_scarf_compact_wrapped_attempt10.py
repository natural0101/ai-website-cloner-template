"""Finalize GLB and QA for the already-open scarf attempt10 scene."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_compact_wrapped_attempt10"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_PATH = (WORKBENCH / "artifacts" / "blend" / f"{ASSET}.blend").resolve()
GLB_PATH = (WORKBENCH / "artifacts" / "exports" / f"{ASSET}.glb").resolve()
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != BLEND_PATH:
    raise RuntimeError(f"Expected already-open {BLEND_PATH}; got {bpy.data.filepath}")


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


root = bpy.data.objects["CatV6_Root"]
export_objects = descendants(root)
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

qa = runpy.run_path(str(SCENE_QA_PATH))["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "SCARF_COMPACT_WRAPPED",
    "attempt": 10,
    "source_blend": str(
        WORKBENCH
        / "artifacts"
        / "blend"
        / "comforting_cat_v6_unified_arms_attempt8.blend"
    ),
    "checkpoint": str(
        WORKBENCH
        / "artifacts"
        / "blend"
        / "checkpoints"
        / "comforting_cat_v6_before_scarf_compact_wrapped_attempt10.blend"
    ),
    "dominant_defect": "rigid_scarf_shields",
    "preserved_sources": [
        "V6_Scarf_FrontDrape_SOURCE_A10",
        "V6_Scarf_FrontFold_Upper_SOURCE_A10",
        "V6_Scarf_BackDrape_SOURCE_A10",
    ],
    "after": {
        "front_drape": bounds(bpy.data.objects["V6_Scarf_FrontDrape"]),
        "front_upper_fold": bounds(
            bpy.data.objects["V6_Scarf_FrontFold_Upper"]
        ),
        "back_drape": bounds(bpy.data.objects["V6_Scarf_BackDrape"]),
        "upper_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Upper"]),
        "lower_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Lower"]),
    },
    "outputs": {
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "front": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_02_material_front.png"
        ),
        "three_quarter": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_03_front_3q.png"
        ),
        "side": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_04_side.png"
        ),
        "back": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_05_back.png"
        ),
    },
    "visual_gate": {
        "status": "accepted_intermediate",
        "improved": [
            "rear shield removed",
            "front drape compacted",
            "front edges wrap farther around chest",
        ],
        "remaining": [
            "front drape still shows an edge-on plate in side view",
            "front fold remains too geometric",
        ],
    },
    "validation": {
        "errors": sorted(set(qa["errors"])),
        "warnings": sorted(set(qa["warnings"])),
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
bpy.context.scene["comforting_cat_v6_stage"] = "EXPORT_QA"
bpy.context.scene["comforting_cat_v6_visual_gate"] = "accepted_intermediate"
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print("COMFORTING_CAT_V6_SCARF_COMPACT_WRAPPED_A10_FINAL=" + json.dumps(report, ensure_ascii=False))
