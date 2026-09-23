"""Correct the over-tall ear pass to a moderate kitten-ear scale."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_ear_scale_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_ear_scale_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_ear_scale_attempt2.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


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
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


names = ["Cat_Ear_L", "Cat_InnerEar_L", "Cat_Ear_R", "Cat_InnerEar_R"]
before = {name: bounds(bpy.data.objects[name]) for name in names}
height_correction = 1.22 / 1.48
width_correction = 1.15 / 1.28

for suffix in ("L", "R"):
    outer = bpy.data.objects[f"Cat_Ear_{suffix}"]
    inner = bpy.data.objects[f"Cat_InnerEar_{suffix}"]
    outer_points = [outer.matrix_world @ vertex.co for vertex in outer.data.vertices]
    root_z = min(point.z for point in outer_points)
    center_x = sum(point.x for point in outer_points) / len(outer_points)
    for obj in (outer, inner):
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            point.x = center_x + (point.x - center_x) * width_correction
            point.z = root_z + (point.z - root_z) * height_correction
            vertex.co = inverse @ point
        obj.data.update()

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in names}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_EarScale_A2"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "EAR_SILHOUETTE"
scene["comforting_cat_v5_geometry_attempt"] = "ear_scale_2"
scene["comforting_cat_v5_dominant_defect"] = "over_tall_fox_like_ears"
scene["comforting_cat_v5_rejected_attempt"] = "ear_scale_attempt1"


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
errors = list(qa["errors"])
warnings = list(qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "EAR_SILHOUETTE",
    "attempt": 2,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "over_tall_fox_like_ears",
    "rejected_attempt": "comforting_cat_v5_ear_scale_attempt1",
    "target_width_vs_original": 1.15,
    "target_height_vs_original": 1.22,
    "before": before,
    "after": after,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
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
print("COMFORTING_CAT_V5_EAR_SCALE_A2=" + json.dumps(report, ensure_ascii=False))
