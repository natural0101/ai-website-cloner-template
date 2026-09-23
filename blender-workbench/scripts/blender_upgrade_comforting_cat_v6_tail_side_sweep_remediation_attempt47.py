"""Remediate A46 by sweeping the low plume backward in side-camera depth."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tail_side_sweep_remediation_attempt47"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_grounded_plume_attempt46.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_side_sweep_remediation_attempt47.blend"
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


def closest_u(point: Vector, knots: list[Vector]) -> float:
    best_distance = float("inf")
    best_u = 0.0
    segments = len(knots) - 1
    for index in range(segments):
        start = knots[index]
        delta = knots[index + 1] - start
        local = 0.0
        if delta.length_squared > 1e-12:
            local = clamp((point - start).dot(delta) / delta.length_squared, 0.0, 1.0)
        distance = (point - (start + local * delta)).length_squared
        if distance < best_distance:
            best_distance = distance
            best_u = (index + local) / segments
    return best_u


def interpolate(knots: list[Vector], u: float) -> Vector:
    segments = len(knots) - 1
    position = clamp(u, 0.0, 1.0) * segments
    index = min(segments - 1, int(position))
    return knots[index].lerp(knots[index + 1], position - index)


def object_center(obj: bpy.types.Object) -> Vector:
    obj_bounds = bounds(obj)
    return Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
before = {"tail": bounds(tail), "tip": bounds(tip)}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A47", "a46_visible_vertical_side_drop"),
    preserve_copy(tip, "Comforting_Cat_V6", "A47", "a46_tip_side_placement"),
]

current_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.58, 0.35, 0.33)),
    Vector((0.82, 0.46, 0.25)),
    Vector((1.12, 0.55, 0.25)),
]
target_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.58, 0.55, 0.36)),
    Vector((0.82, 0.86, 0.29)),
    Vector((1.12, 1.02, 0.29)),
]

inverse = tail.matrix_world.inverted()
locked_vertices = 0
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    u = closest_u(world, current_path)
    if u <= 0.11:
        locked_vertices += 1
        continue
    current_center = interpolate(current_path, u)
    target_center = interpolate(target_path, u)
    weight = smoothstep(0.11, 0.30, u)
    radial = world - current_center
    vertex.co = inverse @ (current_center.lerp(target_center, weight) + radial)
tail.data.update()

tip_center = object_center(tip)
target_tip_center = Vector((1.155, 1.025, 0.290))
delta = target_tip_center - tip_center
tip_inverse = tip.matrix_world.inverted()
for vertex in tip.data.vertices:
    vertex.co = tip_inverse @ (tip.matrix_world @ vertex.co + delta)
tip.data.update()

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "tip": bounds(tip)}
combined_min_x = min(after["tail"]["min"][0], after["tip"]["min"][0])
combined_max_x = max(after["tail"]["max"][0], after["tip"]["max"][0])
metrics = {
    "locked_root_vertices": locked_vertices,
    "combined_x_span": round(combined_max_x - combined_min_x, 5),
    "tail_y_span": after["tail"]["dimensions"][1],
    "tail_min_z": after["tail"]["min"][2],
    "tip_min_z": after["tip"]["min"][2],
    "distal_target_z": 0.29,
    "distal_target_y": 1.02,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailSideSweepRemediation_A47"
scene["comforting_cat_v6_stage"] = "TAIL_SIDE_SWEEP_REMEDIATION"
scene["comforting_cat_v6_attempt"] = 47
scene["comforting_cat_v6_dominant_defect"] = "a46_tail_still_reads_as_side_third_leg"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_SIDE_SWEEP_REMEDIATION",
    "attempt": 47,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a46_tail_still_reads_as_side_third_leg",
    "preserved_sources": preserved_sources,
    "current_path": [list(point) for point in current_path],
    "target_path": [list(point) for point in target_path],
    "before": before,
    "after": after,
    "metrics": metrics,
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
