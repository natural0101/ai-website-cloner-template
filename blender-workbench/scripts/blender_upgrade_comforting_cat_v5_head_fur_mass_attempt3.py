"""Correct the over-sharp cheek wings from head-fur attempt 2."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_head_fur_mass_attempt3"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_head_fur_mass_attempt2.blend"
).resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_head_fur_mass_attempt3.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


def gaussian(value: float, center: float, width: float) -> float:
    return math.exp(-((value - center) / width) ** 2)


head = bpy.data.objects["Cat_Head_Mesh"]
before = bounds(head)
points = [head.matrix_world @ vertex.co for vertex in head.data.vertices]
z_min = min(point.z for point in points)
z_max = max(point.z for point in points)
height = z_max - z_min
half_width = max(abs(point.x) for point in points)
inverse = head.matrix_world.inverted()

for vertex in head.data.vertices:
    point = head.matrix_world @ vertex.co
    t = max(0.0, min(1.0, (point.z - z_min) / height))
    side_ratio = min(1.0, abs(point.x) / half_width)
    previous_lobe = (
        0.052 * gaussian(t, 0.285, 0.038)
        + 0.072 * gaussian(t, 0.365, 0.040)
        + 0.050 * gaussian(t, 0.455, 0.045)
        - 0.028 * gaussian(t, 0.325, 0.021)
        - 0.025 * gaussian(t, 0.410, 0.023)
    )
    point.x -= math.copysign(previous_lobe * 0.48 * side_ratio**4, point.x)
    vertex.co = inverse @ point
head.data.update()
bpy.context.view_layer.update()
after = bounds(head)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_HeadFurMass_A3"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "HEAD_FUR_MASS"
scene["comforting_cat_v5_geometry_attempt"] = "head_fur_mass_3"
scene["comforting_cat_v5_dominant_defect"] = "over_sharp_horizontal_cheek_wings"
scene["comforting_cat_v5_rejected_attempt"] = "head_fur_mass_attempt2"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head depth and crown",
        "ears and face",
        "integrated lids and brows",
        "costume and pear robe",
        "limbs",
        "satchel and tail",
        "materials",
        "lighting and cameras",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
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
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
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

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "HEAD_FUR_MASS",
    "attempt": 3,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "over_sharp_horizontal_cheek_wings",
    "rejected_attempt": "comforting_cat_v5_head_fur_mass_attempt2",
    "amplitude_reduction_fraction": 0.48,
    "before": before,
    "after": after,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
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
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_HEAD_FUR_MASS_A3=" + json.dumps(report, ensure_ascii=False))
