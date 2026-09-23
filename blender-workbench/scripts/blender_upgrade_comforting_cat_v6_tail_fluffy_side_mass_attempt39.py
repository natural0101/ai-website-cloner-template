"""Rebuild the compact tube tail into the broad low side mass of the reference."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tail_fluffy_side_mass_attempt39"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_scarf_cloth_fold_attempt38.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_fluffy_side_mass_attempt39.blend"
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


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
before = {"tail": bounds(tail), "tip": bounds(tip)}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A39", "thin_hidden_tail_tube"),
    preserve_copy(tip, "Comforting_Cat_V6", "A39", "separate_white_tip_ball"),
]

current_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.55, 0.54, 0.45)),
    Vector((0.69, 0.73, 0.25)),
    Vector((0.84, 0.86, 0.25)),
]
target_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.64, 0.43, 0.52)),
    Vector((0.90, 0.56, 0.34)),
    Vector((1.12, 0.66, 0.35)),
]

inverse = tail.matrix_world.inverted()
locked_vertices = 0
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    u = closest_u(world, current_path)
    if u <= 0.09:
        locked_vertices += 1
        continue
    current_center = interpolate(current_path, u)
    target_center = interpolate(target_path, u)
    weight = smoothstep(0.09, 0.28, u)
    center = current_center.lerp(target_center, weight)
    # Broadest in the middle with two very soft thickness pulses. Scaling is
    # stronger in camera X/Z and restrained in depth to avoid a pipe in side view.
    bulge = math.sin(math.pi * u) ** 0.85
    soft_lobes = 1.0 + 0.06 * math.sin(3.0 * math.pi * u) * bulge
    scale_xz = (1.0 + 0.48 * bulge) * soft_lobes
    scale_y = 1.0 + 0.14 * bulge
    radial = world - current_center
    radial.x *= scale_xz
    radial.y *= scale_y
    radial.z *= scale_xz
    vertex.co = inverse @ (center + weight * radial + (1.0 - weight) * (world - current_center))
tail.data.update()

tip_before = bounds(tip)
tip_center = Vector(
    (
        (tip_before["min"][0] + tip_before["max"][0]) * 0.5,
        (tip_before["min"][1] + tip_before["max"][1]) * 0.5,
        (tip_before["min"][2] + tip_before["max"][2]) * 0.5,
    )
)
tip_inverse = tip.matrix_world.inverted()
new_tip_center = Vector((1.15, 0.665, 0.355))
target_dimensions = Vector((0.27, 0.19, 0.22))
source_dimensions = Vector(tip_before["dimensions"])
for vertex in tip.data.vertices:
    world = tip.matrix_world @ vertex.co
    offset = world - tip_center
    offset.x *= target_dimensions.x / source_dimensions.x
    offset.y *= target_dimensions.y / source_dimensions.y
    offset.z *= target_dimensions.z / source_dimensions.z
    # Pull the cream volume slightly inward so more than half overlaps the base.
    offset.x -= 0.025 * (1.0 - abs(offset.x) / (target_dimensions.x * 0.5))
    vertex.co = tip_inverse @ (new_tip_center + offset)
tip.data.update()

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "tip": bounds(tip)}
combined_min_x = min(after["tail"]["min"][0], after["tip"]["min"][0])
combined_max_x = max(after["tail"]["max"][0], after["tip"]["max"][0])
metrics = {
    "locked_root_vertices": locked_vertices,
    "combined_tail_x_span": round(combined_max_x - combined_min_x, 5),
    "tail_base_x_span_ratio": round(
        after["tail"]["dimensions"][0] / before["tail"]["dimensions"][0], 5
    ),
    "tail_base_max_thickness_z": after["tail"]["dimensions"][2],
    "tip_width_over_base_z_thickness": round(
        after["tip"]["dimensions"][0] / after["tail"]["dimensions"][2], 5
    ),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailFluffySideMass_A39"
scene["comforting_cat_v6_stage"] = "TAIL_FLUFFY_SIDE_MASS"
scene["comforting_cat_v6_attempt"] = 39
scene["comforting_cat_v6_dominant_defect"] = "thin_hidden_tail_and_narrow_lower_silhouette"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_FLUFFY_SIDE_MASS",
    "attempt": 39,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "thin_hidden_tail_and_narrow_lower_silhouette",
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
