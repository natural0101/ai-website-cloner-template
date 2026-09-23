"""Extend only the front scarf layers to fix the long box-like torso partition."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_vertical_layer_stack_attempt53"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_crown_ear_root_continuity_attempt52.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_vertical_layer_stack_attempt53.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def gaussian(value: float, center: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - center) / sigma) ** 2)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def geometry_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted((item for item in objects if item.type == "MESH"), key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for value in obj.matrix_world:
            for component in value:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def object_center(obj: bpy.types.Object) -> Vector:
    obj_bounds = bounds(obj)
    return Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )


def fit_mesh_world(obj: bpy.types.Object, center: Vector, dimensions: Vector) -> None:
    old_center = object_center(obj)
    old_dimensions = Vector(bounds(obj)["dimensions"])
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        offset = world - old_center
        offset.x *= dimensions.x / old_dimensions.x
        offset.y *= dimensions.y / old_dimensions.y
        offset.z *= dimensions.z / old_dimensions.z
        vertex.co = inverse @ (center + offset)
    obj.data.update()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
scarf_objects = [upper, lower, drape]
scarf_names = [obj.name for obj in scarf_objects]
non_scarf_objects = [obj for obj in descendants(root) if obj.name not in scarf_names]
non_scarf_hash_before = geometry_hash(non_scarf_objects)
before = {obj.name: bounds(obj) for obj in scarf_objects}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A53", "short_symmetric_scarf_stack")
    for obj in scarf_objects
]

# Upper collar: preserve width and height, but reduce torus depth and add a
# subtle front diagonal to prevent a mechanically level donut edge.
upper_center = object_center(upper)
fit_mesh_world(upper, upper_center, Vector((1.320, 0.580, 0.304)))
inverse = upper.matrix_world.inverted()
for vertex in upper.data.vertices:
    world = upper.matrix_world @ vertex.co
    front = 1.0 - smoothstep(-0.02, 0.20, world.y)
    lower_edge = 1.0 - smoothstep(2.24, 2.34, world.z)
    world.z += 0.032 * (world.x / 0.66) * front * lower_edge
    if world.y > 0.04:
        world.y = 0.04 + (world.y - 0.04) * 0.88
    vertex.co = inverse @ world
upper.data.update()

# Lower wrap: lower and pull forward only the camera-facing half. Rear collar
# height remains intact, so side/back views still read as a wrapped scarf.
inverse = lower.matrix_world.inverted()
for vertex in lower.data.vertices:
    world = lower.matrix_world @ vertex.co
    front = 1.0 - smoothstep(-0.02, 0.24, world.y)
    world.y -= 0.195 * front
    diagonal = 0.042 * (world.x / 0.53)
    valleys = 0.020 * gaussian(world.x, -0.20, 0.13) + 0.026 * gaussian(
        world.x, 0.18, 0.16
    )
    world.z -= front * (0.220 - diagonal + valleys)
    vertex.co = inverse @ world
lower.data.update()

# Keep the front drape as the compact upper overlap. Lengthening comes from
# the lower wrap, while this patch gets a rounded asymmetric bottom.
fit_mesh_world(drape, Vector((-0.030, -0.340, 2.155)), Vector((0.760, 0.120, 0.350)))
inverse = drape.matrix_world.inverted()
for vertex in drape.data.vertices:
    world = drape.matrix_world @ vertex.co
    if world.z < 2.080:
        center_weight = 1.0 - smoothstep(0.0, 0.19, abs(world.x + 0.015))
        world.z += 0.055 * center_weight
    u = clamp((world.x + 0.410) / 0.760, 0.0, 1.0)
    world.z += 0.020 * (u - 0.45) + 0.010 * math.sin(u * math.pi)
    world.y += 0.005 * math.sin(u * math.pi)
    vertex.co = inverse @ world
drape.data.update()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in scarf_objects}
non_scarf_hash_after = geometry_hash(non_scarf_objects)
if non_scarf_hash_before != non_scarf_hash_after:
    raise RuntimeError("Scarf pass changed non-scarf geometry or transforms")

all_meshes = [obj for obj in descendants(root) if obj.type == "MESH"]
subject_min_z = min(bounds(obj)["min"][2] for obj in all_meshes)
subject_max_z = max(bounds(obj)["max"][2] for obj in all_meshes)
subject_height = subject_max_z - subject_min_z
scarf_min_z = min(item["min"][2] for item in after.values())
scarf_max_z = max(item["max"][2] for item in after.values())
scarf_width = max(item["max"][0] for item in after.values()) - min(
    item["min"][0] for item in after.values()
)
robe_bounds = bounds(bpy.data.objects["V6_Robe"])
metrics = {
    "subject_min_z": subject_min_z,
    "subject_max_z": subject_max_z,
    "subject_height": subject_height,
    "scarf_union_min_z": scarf_min_z,
    "scarf_union_max_z": scarf_max_z,
    "scarf_union_height_over_subject": round((scarf_max_z - scarf_min_z) / subject_height, 5),
    "scarf_union_width_over_subject": round(scarf_width / subject_height, 5),
    "ear_top_to_scarf_bottom_over_subject": round((subject_max_z - scarf_min_z) / subject_height, 5),
    "scarf_bottom_to_robe_hem_over_subject": round((scarf_min_z - robe_bounds["min"][2]) / subject_height, 5),
    "lower_drape_y_overlap": round(overlap_1d(after[lower.name], after[drape.name], 1), 5),
    "lower_drape_z_overlap": round(overlap_1d(after[lower.name], after[drape.name], 2), 5),
    "upper_drape_y_overlap": round(overlap_1d(after[upper.name], after[drape.name], 1), 5),
    "upper_drape_z_overlap": round(overlap_1d(after[upper.name], after[drape.name], 2), 5),
    "lower_robe_z_overlap": round(overlap_1d(after[lower.name], robe_bounds, 2), 5),
    "non_scarf_hash_before": non_scarf_hash_before,
    "non_scarf_hash_after": non_scarf_hash_after,
}

if not 0.18 <= metrics["scarf_union_height_over_subject"] <= 0.205:
    raise RuntimeError(f"Scarf height ratio outside target: {metrics['scarf_union_height_over_subject']}")
if metrics["lower_drape_y_overlap"] < 0.02 or metrics["lower_drape_z_overlap"] < 0.10:
    raise RuntimeError("Lower wrap and drape are not sufficiently seated")
if metrics["upper_drape_y_overlap"] < 0.02 or metrics["upper_drape_z_overlap"] < 0.10:
    raise RuntimeError("Upper wrap and drape are not sufficiently seated")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfVerticalLayerStack_A53"
scene["comforting_cat_v6_stage"] = "SCARF_VERTICAL_LAYER_STACK"
scene["comforting_cat_v6_attempt"] = 53
scene["comforting_cat_v6_dominant_defect"] = "short_symmetric_scarf_exposes_long_box_torso"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_VERTICAL_LAYER_STACK",
    "attempt": 53,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "short_symmetric_scarf_exposes_long_box_torso",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": scarf_names, "non_scarf_geometry_unchanged": True},
}
finalize_pass(
    asset=ASSET,
    root=root,
    scene=scene,
    final_blend=FINAL_BLEND,
    glb_path=GLB_PATH,
    render_dir=RENDER_DIR,
    report_dir=REPORT_DIR,
    scene_qa_path=SCENE_QA_PATH,
    report=report,
)
