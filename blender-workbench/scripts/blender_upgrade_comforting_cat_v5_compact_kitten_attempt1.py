"""Compress the lower character vertically into kitten-like proportions."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v5_compact_kitten_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_leg_paw_grounding_attempt1.blend"
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_compact_kitten_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def group_bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    points = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE"} or obj.hide_render:
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


root = bpy.data.objects["Cat_Root"]
head_group = bpy.data.objects["Cat_Head"]
all_export_before = descendants(root)
before = group_bounds(all_export_before)

ground_z = 0.02
vertical_factor = 0.78
affine = (
    Matrix.Translation((0.0, 0.0, ground_z))
    @ Matrix.Diagonal((1.0, 1.0, vertical_factor, 1.0))
    @ Matrix.Translation((0.0, 0.0, -ground_z))
)

scaled_top_level = []
for child in list(root.children):
    if child == head_group:
        continue
    child.matrix_world = affine @ child.matrix_world
    scaled_top_level.append(child.name)

# This retained scarf fold is still a visible standalone object outside the
# export root. Keep it aligned with the compressed wrap and drape.
standalone_scaled = []
for name in ("Cat_ScarfUpperFold",):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.parent is not None or obj.hide_render:
        continue
    obj.matrix_world = affine @ obj.matrix_world
    standalone_scaled.append(obj.name)

# Preserve the original head volume and facial layout as a rigid group. Lower
# it until the chin-scarf gap matches the pre-compression contact.
head_matrix = head_group.matrix_world.copy()
head_drop = 0.528
head_matrix.translation.z -= head_drop
head_group.matrix_world = head_matrix

bpy.context.view_layer.update()
all_export_after = descendants(root)
after = group_bounds(all_export_after)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_CompactKitten_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "COMPACT_KITTEN_PROPORTIONS"
scene["comforting_cat_v5_geometry_attempt"] = "compact_kitten_1"
scene["comforting_cat_v5_dominant_defect"] = "adult_overlong_torso_and_lower_body"
scene["comforting_cat_v5_vertical_factor"] = vertical_factor
scene["comforting_cat_v5_head_drop"] = head_drop
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head volume and facial layout",
        "horizontal body widths",
        "materials",
        "lighting",
        "camera directions",
    ]
)


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


export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 2.75), (0.0, -0.04, 1.62), 4.05)
render(camera, "03_front_3q", (4.0, -7.4, 3.05), (0.0, -0.02, 1.58), 4.15)
render(camera, "04_side", (8.4, -0.35, 2.75), (0.0, 0.0, 1.55), 4.15)
render(camera, "05_back", (0.0, 8.4, 2.75), (0.0, 0.04, 1.55), 4.15)
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
    "stage": "COMPACT_KITTEN_PROPORTIONS",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "adult_overlong_torso_and_lower_body",
    "vertical_factor": vertical_factor,
    "ground_z": ground_z,
    "head_drop": head_drop,
    "scaled_top_level": scaled_top_level,
    "standalone_scaled": standalone_scaled,
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
print("COMFORTING_CAT_V5_COMPACT_KITTEN_A1=" + json.dumps(report, ensure_ascii=False))
