"""TRUE_360 face pass: fuse the two-ball muzzle into one editable soft volume."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_muzzle_union_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_eye_integration_attempt2.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_muzzle_union_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
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


head_root = bpy.data.objects["Cat_Head"]
source_left = bpy.data.objects["Cat_Muzzle_L"]
source_right = bpy.data.objects["Cat_Muzzle_R"]
fur_light = source_left.data.materials[0]
before = {
    "left": world_bounds(source_left),
    "right": world_bounds(source_right),
}

# Preserve source geometry outside the export hierarchy.
source_objects = [source_left, source_right]
source_world_matrices = {obj.name: obj.matrix_world.copy() for obj in source_objects}
for obj in source_objects:
    original_name = obj.name
    obj.parent = None
    obj.matrix_world = source_world_matrices[original_name]
    obj.hide_viewport = True
    obj.hide_render = True
    obj.name = f"{obj.name}_SOURCE_V5_A1"

# Work only on duplicates and an overlapping center bridge.
work_parts = []
for source, name in zip(source_objects, ("Cat_MuzzleUnion_L", "Cat_MuzzleUnion_R")):
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    duplicate.name = name
    duplicate.hide_viewport = False
    duplicate.hide_render = False
    bpy.context.scene.collection.objects.link(duplicate)
    work_parts.append(duplicate)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=40,
    ring_count=24,
    location=(0.0, -0.590, 2.735),
    scale=(0.175, 0.092, 0.135),
)
bridge = bpy.context.object
bridge.name = "Cat_MuzzleUnion_Bridge"
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bridge.data.materials.append(fur_light)
work_parts.append(bridge)

bpy.ops.object.select_all(action="DESELECT")
for obj in work_parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = work_parts[0]
bpy.ops.object.join()
unified = bpy.context.object
unified.name = "Cat_MuzzleUnified"

remesh = unified.modifiers.new(name="MuzzleVoxelUnion", type="REMESH")
remesh.mode = "VOXEL"
remesh.voxel_size = 0.018
remesh.use_smooth_shade = True
bpy.context.view_layer.objects.active = unified
bpy.ops.object.modifier_apply(modifier=remesh.name)

smooth = unified.modifiers.new(name="MuzzleSurfaceSmooth", type="SMOOTH")
smooth.factor = 0.42
smooth.iterations = 3
bpy.ops.object.modifier_apply(modifier=smooth.name)
for polygon in unified.data.polygons:
    polygon.use_smooth = True

world_matrix = unified.matrix_world.copy()
unified.parent = head_root
unified.matrix_world = world_matrix
bpy.context.view_layer.update()
after = world_bounds(unified)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_MuzzleUnion_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_MUZZLE_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "muzzle_union_1"
scene["comforting_cat_v5_dominant_defect"] = "two_separate_muzzle_ellipsoids"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head group scale",
        "eye layout and integration",
        "nose and mouth",
        "head and ear meshes",
        "robe and rear coverage",
        "scarf integration",
        "arms and legs",
        "satchel and strap",
        "tail",
        "lighting",
        "review cameras",
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
    scene["comforting_cat_v5_stage"] = "FACE_MUZZLE_REVIEW"
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
    obj.hide_render = False
    obj.hide_viewport = False
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
    "stage": "FACE_MUZZLE_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "two_separate_muzzle_ellipsoids",
    "source_parts": [obj.name for obj in source_objects],
    "unified_part": unified.name,
    "voxel_size": 0.018,
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
print("COMFORTING_CAT_V5_MUZZLE_UNION=" + json.dumps(report, ensure_ascii=False))
