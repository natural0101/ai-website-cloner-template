"""Darken the over-bright linen inset to a muted medium gray-blue."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_chest_linen_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_chest_linen_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_chest_linen_attempt2.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


material = bpy.data.materials["CAT_GrayLinenInset"]
principled = material.node_tree.nodes["Principled BSDF"]
before_color = [round(float(value), 6) for value in principled.inputs["Base Color"].default_value]
after_color = (0.16, 0.19, 0.19, 1.0)
principled.inputs["Base Color"].default_value = after_color

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_ChestLinen_A2"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "CHEST_LINEN_MATERIAL"
scene["comforting_cat_v5_geometry_attempt"] = "chest_linen_2"
scene["comforting_cat_v5_dominant_defect"] = "over_bright_white_chest_inset"
scene["comforting_cat_v5_rejected_attempt"] = "chest_linen_attempt1"


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 2.76), (0.0, -0.04, 1.62), 4.05)
render(camera, "03_front_3q", (4.0, -7.4, 3.06), (0.0, -0.02, 1.58), 4.15)
render(camera, "04_side", (8.4, -0.35, 2.76), (0.0, 0.0, 1.56), 4.15)
render(camera, "05_back", (0.0, 8.4, 2.76), (0.0, 0.04, 1.56), 4.15)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

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
    "stage": "CHEST_LINEN_MATERIAL",
    "attempt": 2,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "over_bright_white_chest_inset",
    "rejected_attempt": "comforting_cat_v5_chest_linen_attempt1",
    "before_color": before_color,
    "after_color": list(after_color),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
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
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_CHEST_LINEN_A2=" + json.dumps(report, ensure_ascii=False))
