"""Rebuild the tail as one low plume whose descending root stays hidden by the robe."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v6_tail_occluded_root_low_plume_attempt58"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_face_envelope_rebalance_attempt57.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_occluded_root_low_plume_attempt58.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


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


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
robe = bpy.data.objects["V6_Robe"]
tail_names = [tail.name, tip.name]
non_tail_objects = [obj for obj in descendants(root) if obj.name not in tail_names]
non_tail_hash_before = geometry_hash(non_tail_objects)
before = {"tail": bounds(tail), "tip": bounds(tip), "robe": bounds(robe)}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A58", "high_visible_root_and_ringed_sausage_tail"),
    preserve_copy(tip, "Comforting_Cat_V6", "A58", "small_axis_aligned_tip_knob"),
]

path = [
    ((0.430, 0.240, 0.790), 0.88),
    ((0.500, 0.290, 0.490), 0.75),
    ((0.600, 0.360, 0.310), 1.05),
    ((0.760, 0.680, 0.280), 1.22),
    ((1.050, 0.960, 0.290), 0.90),
]
curve = bpy.data.curves.new("V6_TailBase_OccludedRootLowPlumeCurve_A58", "CURVE")
curve.dimensions = "3D"
curve.resolution_u = 12
curve.bevel_depth = 0.180
curve.bevel_resolution = 8
curve.use_fill_caps = True
spline = curve.splines.new("BEZIER")
spline.bezier_points.add(len(path) - 1)
for point, (coordinate, radius) in zip(spline.bezier_points, path, strict=True):
    point.co = coordinate
    point.radius = radius
    point.handle_left_type = "AUTO"
    point.handle_right_type = "AUTO"

collection = bpy.data.collections["Comforting_Cat_V6"]
temporary = bpy.data.objects.new("V6_TailBase_TemporaryCurve_A58", curve)
collection.objects.link(temporary)
bpy.ops.object.select_all(action="DESELECT")
temporary.select_set(True)
bpy.context.view_layer.objects.active = temporary
bpy.ops.object.convert(target="MESH")
new_mesh = temporary.data.copy()
bpy.data.objects.remove(temporary, do_unlink=True)

materials = list(tail.data.materials)
old_mesh = tail.data
tail.data = new_mesh
tail.data.name = "V6_TailBase_OccludedRootLowPlumeMesh_A58"
for material in materials:
    tail.data.materials.append(material)
for polygon in tail.data.polygons:
    polygon.use_smooth = True
tail.data.update()
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)

# Tangent-align and flatten the cream tip into the plume instead of keeping a
# separate round knob.
tip_before = bounds(tip)
tip_center = object_center(tip)
old_dimensions = Vector(tip_before["dimensions"])
target_center = Vector((1.100, 1.000, 0.230))
target_dimensions = Vector((0.220, 0.150, 0.150))
tangent = Vector((1.050 - 0.760, 0.960 - 0.680, 0.0))
angle = math.atan2(tangent.y, tangent.x)
rotation = Matrix.Rotation(angle, 4, "Z")
inverse = tip.matrix_world.inverted()
for vertex in tip.data.vertices:
    world = tip.matrix_world @ vertex.co
    offset = world - tip_center
    normalized = Vector(
        (
            offset.x / old_dimensions.x,
            offset.y / old_dimensions.y,
            offset.z / old_dimensions.z,
        )
    )
    shaped = Vector(
        (
            normalized.x * target_dimensions.x,
            normalized.y * target_dimensions.y,
            normalized.z * target_dimensions.z,
        )
    )
    vertex.co = inverse @ (target_center + rotation @ shaped)
tip.data.update()

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "tip": bounds(tip), "robe": bounds(robe)}
non_tail_hash_after = geometry_hash(non_tail_objects)
if non_tail_hash_before != non_tail_hash_after:
    raise RuntimeError("Tail pass changed locked body or costume geometry")

combined_min_x = min(after["tail"]["min"][0], after["tip"]["min"][0])
combined_max_x = max(after["tail"]["max"][0], after["tip"]["max"][0])
metrics = {
    "combined_x_span": round(combined_max_x - combined_min_x, 5),
    "tail_min_z": after["tail"]["min"][2],
    "tip_min_z": after["tip"]["min"][2],
    "tail_robe_overlap_x": round(overlap_1d(after["tail"], after["robe"], 0), 5),
    "tail_robe_overlap_y": round(overlap_1d(after["tail"], after["robe"], 1), 5),
    "tail_robe_overlap_z": round(overlap_1d(after["tail"], after["robe"], 2), 5),
    "tip_tail_overlap_x": round(overlap_1d(after["tail"], after["tip"], 0), 5),
    "path": [{"coordinate": list(coordinate), "radius": radius} for coordinate, radius in path],
    "non_tail_hash_before": non_tail_hash_before,
    "non_tail_hash_after": non_tail_hash_after,
}
if not 0.88 <= metrics["combined_x_span"] <= 0.96:
    raise RuntimeError(f"Tail X span outside target: {metrics['combined_x_span']}")
if not 0.04 <= metrics["tail_min_z"] <= 0.08:
    raise RuntimeError(f"Tail ground clearance outside target: {metrics['tail_min_z']}")
if metrics["tip_tail_overlap_x"] < 0.12:
    raise RuntimeError(f"Cream tip overlap too small: {metrics['tip_tail_overlap_x']}")
print("A58_PRE_GATE_METRICS=" + repr(metrics))
if (
    metrics["tail_robe_overlap_x"] < 0.30
    or metrics["tail_robe_overlap_y"] < 0.25
    or metrics["tail_robe_overlap_z"] < 0.15
):
    raise RuntimeError("Tail root is not sufficiently concealed by the robe")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailOccludedRootLowPlume_A58"
scene["comforting_cat_v6_stage"] = "TAIL_OCCLUDED_ROOT_LOW_PLUME"
scene["comforting_cat_v6_attempt"] = 58
scene["comforting_cat_v6_dominant_defect"] = "high_visible_root_and_ringed_sausage_tail"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_OCCLUDED_ROOT_LOW_PLUME",
    "attempt": 58,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "high_visible_root_and_ringed_sausage_tail",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": tail_names, "non_tail_geometry_unchanged": True},
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
