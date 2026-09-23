"""Correct the dominant flattened/wide head silhouette in attempt23."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_head_silhouette_attempt24"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_hem_drape_attempt23.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_silhouette_attempt24.blend"
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
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


def preserve_copy(obj: bpy.types.Object) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A24"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "flattened_wide_head_silhouette"
    return copy.name


def scale_mesh_world(
    obj: bpy.types.Object,
    center: Vector,
    scale_x: float,
    scale_z: float,
) -> None:
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x = center.x + (world.x - center.x) * scale_x
        world.z = center.z + (world.z - center.z) * scale_z
        vertex.co = inverse @ world
    obj.data.update()


def scale_curve_world(
    obj: bpy.types.Object,
    center: Vector,
    scale_x: float,
    scale_z: float,
) -> None:
    inverse = obj.matrix_world.inverted()
    for spline in obj.data.splines:
        for point in spline.bezier_points:
            world = obj.matrix_world @ point.co
            world.x = center.x + (world.x - center.x) * scale_x
            world.z = center.z + (world.z - center.z) * scale_z
            point.co = inverse @ world
            for handle_name in ("handle_left", "handle_right"):
                handle = getattr(point, handle_name)
                handle_world = obj.matrix_world @ handle
                handle_world.x = center.x + (handle_world.x - center.x) * scale_x
                handle_world.z = center.z + (handle_world.z - center.z) * scale_z
                setattr(point, handle_name, inverse @ handle_world)
    # Curve datablocks update through the depsgraph in Blender 5.1.
    bpy.context.view_layer.update()


def scale_local_feature(
    obj: bpy.types.Object,
    scale_x: float,
    scale_z: float,
) -> None:
    obj_bounds = bounds(obj)
    center = Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )
    if obj.type == "MESH":
        scale_mesh_world(obj, center, scale_x, scale_z)
    elif obj.type == "CURVE":
        scale_curve_world(obj, center, scale_x, scale_z)


root = bpy.data.objects["CatV6_Root"]
feature_names = [
    "V6_Head",
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_MuzzleUnified",
    "V6_Nose",
    "V6_Eyebrow_L",
    "V6_Eyebrow_R",
    "V6_Ear_L",
    "V6_Ear_R",
    "V6_InnerEar_L",
    "V6_InnerEar_R",
    "V6_Mouth",
    "V6_Philtrum",
]
objects = [bpy.data.objects[name] for name in feature_names]
before = {obj.name: bounds(obj) for obj in objects}
preserved_sources = [preserve_copy(obj) for obj in objects]

# Reference front silhouette is roughly 1.20 width/height; attempt23 is 1.49.
face_center = Vector((0.0, 0.0, 2.82))
for obj in objects:
    if obj.type == "MESH":
        scale_mesh_world(obj, face_center, 0.84, 1.04)
    elif obj.type == "CURVE":
        scale_curve_world(obj, face_center, 0.84, 1.04)

# Keep the face readable after narrowing: reduce oversized toy-like facial disks
# and the broad white muzzle relative to the new head.
for name in [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
]:
    scale_local_feature(bpy.data.objects[name], 0.80, 0.76)
scale_local_feature(bpy.data.objects["V6_MuzzleUnified"], 0.70, 0.90)
scale_local_feature(bpy.data.objects["V6_Nose"], 0.92, 0.92)

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in objects}
head_dims = after["V6_Head"]["dimensions"]
metrics = {
    "head_width_height": round(head_dims[0] / head_dims[2], 5),
    "single_eye_width_over_head_width": round(
        after["V6_Eye_L"]["dimensions"][0] / head_dims[0], 5
    ),
    "single_eye_height_over_head_height": round(
        after["V6_Eye_L"]["dimensions"][2] / head_dims[2], 5
    ),
    "muzzle_width_over_head_width": round(
        after["V6_MuzzleUnified"]["dimensions"][0] / head_dims[0], 5
    ),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadSilhouette_A24"
scene["comforting_cat_v6_stage"] = "HEAD_SILHOUETTE"
scene["comforting_cat_v6_attempt"] = 24
scene["comforting_cat_v6_dominant_defect"] = "flattened_wide_head_silhouette"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)


def look_at(
    obj: bpy.types.Object,
    target: tuple[float, float, float],
) -> None:
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


camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 3.08), (0.0, 0.0, 1.88), 4.20)
render(camera, "03_front_3q", (4.0, -7.4, 3.35), (0.0, 0.02, 1.84), 4.30)
render(camera, "04_side", (8.4, -0.35, 3.08), (0.0, 0.08, 1.82), 4.30)
render(camera, "05_back", (0.0, 8.4, 3.08), (0.0, 0.12, 1.82), 4.30)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

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
    "stage": "HEAD_SILHOUETTE",
    "attempt": 24,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flattened_wide_head_silhouette",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": qa,
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(json.dumps(report, ensure_ascii=False))
