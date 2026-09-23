"""Reblock the garment stack from rigid primitives into layered asymmetric cloth."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_garment_cloth_reblock_attempt44"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_face_relief_integration_attempt43.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_garment_cloth_reblock_attempt44.blend"
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


def interpolate_knots(value: float, knots: list[tuple[float, float]]) -> float:
    if value <= knots[0][0]:
        return knots[0][1]
    if value >= knots[-1][0]:
        return knots[-1][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= value <= x1:
            t = smoothstep(x0, x1, value)
            return y0 * (1.0 - t) + y1 * t
    return knots[-1][1]


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


def close_open_boundaries(obj: bpy.types.Object) -> tuple[int, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary = [edge for edge in bm.edges if edge.is_boundary]
    before_count = len(boundary)
    if boundary:
        bmesh.ops.holes_fill(bm, edges=boundary, sides=0)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    check = bmesh.new()
    check.from_mesh(obj.data)
    after_count = sum(edge.is_boundary for edge in check.edges)
    check.free()
    return before_count, after_count


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
left_arm = bpy.data.objects["V6_ArmUnified_L"]
right_arm = bpy.data.objects["V6_ArmUnified_R"]
affected = [robe, tunic, upper, lower, drape, left_arm, right_arm]
before = {obj.name: bounds(obj) for obj in affected}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A44", "rigid_geometric_garment")
    for obj in affected
]

# Robe: narrow shoulder/upper torso, retain lower cloth mass, and add a very
# small left/right inequality plus a soft uneven hem.
robe_profile = [
    (0.66, 0.665),
    (0.74, 0.685),
    (1.05, 0.705),
    (1.30, 0.705),
    (1.70, 0.675),
    (2.08, 0.625),
    (2.25, 0.575),
]
world_vertices = [robe.matrix_world @ vertex.co for vertex in robe.data.vertices]
ring_half_widths: dict[float, float] = {}
for world in world_vertices:
    key = round(float(world.z), 4)
    ring_half_widths[key] = max(ring_half_widths.get(key, 0.0), abs(float(world.x)))
inverse = robe.matrix_world.inverted()
for vertex, world in zip(robe.data.vertices, world_vertices, strict=True):
    key = round(float(world.z), 4)
    current_half = max(ring_half_widths[key], 1e-6)
    target_half = interpolate_knots(world.z, robe_profile)
    normalized_x = world.x / current_half
    side_bias = 0.014 if world.x < 0.0 else -0.006
    world.x = normalized_x * (target_half + side_bias)
    hem_weight = 1.0 - smoothstep(0.67, 0.90, world.z)
    world.z += hem_weight * (
        0.020 * math.sin(normalized_x * math.pi)
        + 0.012 * normalized_x
    )
    vertex.co = inverse @ world
robe.data.update()

# Tunic: a wider, thinner front panel that hugs the robe. Keep the existing
# editable mesh/modifier stack and introduce a center dip plus unequal sides.
fit_mesh_world(tunic, Vector((0.0, -0.380, 1.400)), Vector((0.950, 0.100, 1.160)))
solidify = next((modifier for modifier in tunic.modifiers if modifier.type == "SOLIDIFY"), None)
if solidify is not None:
    solidify.thickness = 0.030
inverse = tunic.matrix_world.inverted()
tunic_bounds = bounds(tunic)
for vertex in tunic.data.vertices:
    world = tunic.matrix_world @ vertex.co
    normalized_x = clamp(world.x / 0.475, -1.0, 1.0)
    lower_weight = 1.0 - smoothstep(0.84, 1.18, world.z)
    world.x += 0.014 * (1.0 - world.z / 2.0)
    world.z -= lower_weight * (
        0.035 * (1.0 - abs(normalized_x))
        + 0.018 * normalized_x
    )
    world.y += 0.010 * (1.0 - normalized_x * normalized_x)
    vertex.co = inverse @ world
tunic.data.update()

# Upper scarf: reduce depth and replace the torus read with a front-heavy,
# diagonally folded wrap. Rear vertices stay a shallow band.
fit_mesh_world(upper, object_center(upper), Vector((1.320, 0.620, 0.255)))
upper_center_z = object_center(upper).z
inverse = upper.matrix_world.inverted()
for vertex in upper.data.vertices:
    world = upper.matrix_world @ vertex.co
    front = clamp((0.10 - world.y) / 0.43, 0.0, 1.0)
    side = clamp(world.x / 0.66, -1.0, 1.0)
    scale_z = 0.82 + 0.46 * front
    world.z = upper_center_z + (world.z - upper_center_z) * scale_z
    world.z += front * (
        -0.040 * side
        - 0.018 * math.cos(side * 2.0 * math.pi)
    )
    world.y += front * 0.018 * math.sin(side * math.pi)
    vertex.co = inverse @ world
upper.data.update()

# Secondary wrap: compact support visible only in an asymmetric front band.
fit_mesh_world(lower, Vector((0.0, 0.075, 2.165)), Vector((1.060, 0.460, 0.200)))
inverse = lower.matrix_world.inverted()
for vertex in lower.data.vertices:
    world = lower.matrix_world @ vertex.co
    front = clamp((0.02 - world.y) / 0.25, 0.0, 1.0)
    side = clamp(world.x / 0.53, -1.0, 1.0)
    world.z += front * (0.018 * math.sin((side + 0.20) * math.pi))
    world.y += front * (0.015 + 0.012 * side)
    vertex.co = inverse @ world
lower.data.update()

# Front scarf overlap: widen and move backward so it physically overlaps both
# the upper wrap and robe instead of floating as a separate shield.
fit_mesh_world(drape, Vector((-0.045, -0.400, 2.135)), Vector((0.960, 0.120, 0.370)))
inverse = drape.matrix_world.inverted()
for vertex in drape.data.vertices:
    world = drape.matrix_world @ vertex.co
    side = clamp((world.x + 0.525) / 0.960, 0.0, 1.0)
    world.z += 0.030 * (side - 0.5) + 0.016 * math.sin(side * math.pi)
    world.y += 0.008 * math.sin(side * math.pi)
    vertex.co = inverse @ world
drape.data.update()

# Arms: preserve continuous sleeve/fur meshes, break perfect mirroring, narrow
# the forearms and close their old open boundary loops.
arm_boundary_metrics: dict[str, dict[str, int]] = {}
for arm, sign, bottom_z in (
    (left_arm, -1.0, 0.945),
    (right_arm, 1.0, 1.035),
):
    old = bounds(arm)
    old_min_z = old["min"][2]
    old_max_z = old["max"][2]
    inverse = arm.matrix_world.inverted()
    for vertex in arm.data.vertices:
        world = arm.matrix_world @ vertex.co
        u = clamp((world.z - old_min_z) / (old_max_z - old_min_z), 0.0, 1.0)
        old_center_x = (old["min"][0] + old["max"][0]) * 0.5
        old_half = (old["max"][0] - old["min"][0]) * 0.5
        if u >= 0.72:
            target_half = 0.160
        elif u >= 0.22:
            target_half = 0.112
        else:
            target_half = 0.132
        center_abs = (
            0.655
            + 0.050 * math.sin(u * math.pi)
            + (0.010 if sign < 0.0 else -0.008) * (1.0 - u)
        )
        normalized_x = (world.x - old_center_x) / max(old_half, 1e-6)
        world.x = sign * center_abs + normalized_x * target_half
        world.z = bottom_z + u * (2.020 - bottom_z)
        vertex.co = inverse @ world
    arm.data.update()
    boundary_before, boundary_after = close_open_boundaries(arm)
    arm_boundary_metrics[arm.name] = {
        "boundary_edges_before": boundary_before,
        "boundary_edges_after": boundary_after,
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in affected}
metrics = {
    "robe_width_over_height": round(
        after[robe.name]["dimensions"][0] / after[robe.name]["dimensions"][2], 5
    ),
    "tunic_width_over_robe": round(
        after[tunic.name]["dimensions"][0] / after[robe.name]["dimensions"][0], 5
    ),
    "tunic_depth": after[tunic.name]["dimensions"][1],
    "upper_scarf_depth": after[upper.name]["dimensions"][1],
    "upper_scarf_height": after[upper.name]["dimensions"][2],
    "drape_upper_y_overlap": round(
        overlap_1d(after[drape.name], after[upper.name], 1), 5
    ),
    "drape_upper_z_overlap": round(
        overlap_1d(after[drape.name], after[upper.name], 2), 5
    ),
    "drape_robe_y_overlap": round(
        overlap_1d(after[drape.name], after[robe.name], 1), 5
    ),
    "drape_robe_z_overlap": round(
        overlap_1d(after[drape.name], after[robe.name], 2), 5
    ),
    "arm_bottom_delta_z": round(
        abs(after[left_arm.name]["min"][2] - after[right_arm.name]["min"][2]), 5
    ),
    "arm_boundaries": arm_boundary_metrics,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_GarmentClothReblock_A44"
scene["comforting_cat_v6_stage"] = "GARMENT_CLOTH_SILHOUETTE_REBLOCK"
scene["comforting_cat_v6_attempt"] = 44
scene["comforting_cat_v6_dominant_defect"] = "torus_scarf_board_tunic_capsule_robe_mirrored_arms"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "GARMENT_CLOTH_SILHOUETTE_REBLOCK",
    "attempt": 44,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "torus_scarf_board_tunic_capsule_robe_mirrored_arms",
    "preserved_sources": preserved_sources,
    "do_not_change": [
        "face/head/ears",
        "tail",
        "satchel",
        "feet",
        "camera/light/materials",
    ],
    "robe_profile": robe_profile,
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
