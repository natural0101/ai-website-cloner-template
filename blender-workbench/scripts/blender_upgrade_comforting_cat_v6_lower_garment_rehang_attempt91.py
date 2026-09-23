"""Lower only the robe hem and tunic bottom rows to restore compact kitten leg proportions."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_lower_garment_rehang_attempt91"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_brow_surface_ribbon_attempt90.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_lower_garment_rehang_attempt91.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
descendants = utils["descendants"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def object_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        digest.update(obj.type.encode("ascii"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                for point in spline.bezier_points:
                    digest.update(
                        f"{point.co.x:.9f},{point.co.y:.9f},{point.co.z:.9f},{point.radius:.9f};".encode("ascii")
                    )
    return digest.hexdigest()


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
foot_l = bpy.data.objects["V6_Foot_L"]
foot_r = bpy.data.objects["V6_Foot_R"]
leg_l = bpy.data.objects["V6_Leg_L"]
leg_r = bpy.data.objects["V6_Leg_R"]
tail = bpy.data.objects["V6_TailBase"]
changed_names = {robe.name, tunic.name}
locked_objects = [obj for obj in descendants(root) if obj.name not in changed_names]
locked_hash_before = object_hash(locked_objects)
before = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "foot_l": bounds(foot_l),
    "foot_r": bounds(foot_r),
    "leg_l": bounds(leg_l),
    "leg_r": bounds(leg_r),
    "tail": bounds(tail),
}
robe_topology_before = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
tunic_topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
preserved_sources = [
    preserve_copy(robe, "Comforting_Cat_V6", "A91", "excessive_exposed_shin_gap"),
    preserve_copy(tunic, "Comforting_Cat_V6", "A91", "tunic_bottom_would_float_above_rehung_robe"),
]

if len(robe.data.vertices) != 450:
    raise RuntimeError(f"Unexpected robe topology: {len(robe.data.vertices)} vertices")
if len(tunic.data.vertices) != 126:
    raise RuntimeError(f"Unexpected tunic topology: {len(tunic.data.vertices)} vertices")

adjacency: dict[int, set[int]] = {vertex.index: set() for vertex in robe.data.vertices}
for edge in robe.data.edges:
    first, second = edge.vertices
    adjacency[first].add(second)
    adjacency[second].add(first)
max_degree = max(len(neighbors) for neighbors in adjacency.values())
center_candidates = [index for index, neighbors in adjacency.items() if len(neighbors) == max_degree]
bottom_center_index = min(
    center_candidates,
    key=lambda index: (robe.matrix_world @ robe.data.vertices[index].co).z,
)
bottom_ring = set(adjacency[bottom_center_index])
if len(bottom_ring) != 64:
    raise RuntimeError(f"Unexpected bottom ring size: {len(bottom_ring)}")
second_ring: set[int] = set()
for index in bottom_ring:
    second_ring.update(adjacency[index] - bottom_ring - {bottom_center_index})
if len(second_ring) != 64:
    raise RuntimeError(f"Unexpected second ring size: {len(second_ring)}")

robe_locked_before: dict[int, Vector] = {}
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if world.z >= 0.82:
        robe_locked_before[vertex.index] = world.copy()

robe_inverse = robe.matrix_world.inverted()
center_y = (before["robe"]["min"][1] + before["robe"]["max"][1]) * 0.5
half_y = before["robe"]["dimensions"][1] * 0.5


def angle_for_world(world: Vector) -> float:
    return math.atan2((world.y - center_y) / half_y, world.x / 0.70)


bottom_drops: list[float] = []
for index in bottom_ring:
    vertex = robe.data.vertices[index]
    world = robe.matrix_world @ vertex.co
    theta = angle_for_world(world)
    frontness = max(0.0, -math.sin(theta))
    leftness = max(0.0, -math.cos(theta))
    rightness = max(0.0, math.cos(theta))
    drop = 0.112 + 0.008 * frontness + 0.004 * leftness - 0.012 * rightness * frontness
    world.z -= drop
    vertex.co = robe_inverse @ world
    bottom_drops.append(drop)

second_drops: list[float] = []
for index in second_ring:
    vertex = robe.data.vertices[index]
    world = robe.matrix_world @ vertex.co
    theta = angle_for_world(world)
    frontness = max(0.0, -math.sin(theta))
    leftness = max(0.0, -math.cos(theta))
    rightness = max(0.0, math.cos(theta))
    drop = 0.074 + 0.006 * frontness + 0.003 * leftness - 0.008 * rightness * frontness
    world.z -= drop
    vertex.co = robe_inverse @ world
    second_drops.append(drop)

bottom_center = robe.data.vertices[bottom_center_index]
bottom_center_world = robe.matrix_world @ bottom_center.co
bottom_center_world.z -= sum(bottom_drops) / len(bottom_drops)
bottom_center.co = robe_inverse @ bottom_center_world
robe.data.update()

tunic_locked_before: dict[int, Vector] = {}
tunic_inverse = tunic.matrix_world.inverted()
columns = 7
rows = 9
front_count = columns * rows
for vertex in tunic.data.vertices:
    local_index = vertex.index % front_count
    row = local_index // columns
    world = tunic.matrix_world @ vertex.co
    if row <= rows - 3:
        tunic_locked_before[vertex.index] = world.copy()
    elif row == rows - 2:
        world.z -= 0.035
        vertex.co = tunic_inverse @ world
    else:
        u = -1.0 + 2.0 * (local_index % columns) / (columns - 1)
        hem_drop = 0.075 + 0.005 * (1.0 - abs(u))
        world.z -= hem_drop
        vertex.co = tunic_inverse @ world
tunic.data.update()
bpy.context.view_layer.update()

after = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "foot_l": bounds(foot_l),
    "foot_r": bounds(foot_r),
    "leg_l": bounds(leg_l),
    "leg_r": bounds(leg_r),
    "tail": bounds(tail),
}
locked_hash_after = object_hash(locked_objects)
robe_topology_after = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
tunic_topology_after = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A91 changed face, ears, upper costume, legs, feet, tail, camera or materials")
if robe_topology_before != robe_topology_after or tunic_topology_before != tunic_topology_after:
    raise RuntimeError("A91 changed garment topology")

robe_locked_delta = max(
    (
        (robe.matrix_world @ robe.data.vertices[index].co) - before_world
    ).length
    for index, before_world in robe_locked_before.items()
)
tunic_locked_delta = max(
    (
        (tunic.matrix_world @ tunic.data.vertices[index].co) - before_world
    ).length
    for index, before_world in tunic_locked_before.items()
)
foot_top = max(after["foot_l"]["max"][2], after["foot_r"]["max"][2])
exposed_shin_gap = after["robe"]["min"][2] - foot_top
tunic_robe_gap = after["tunic"]["min"][2] - after["robe"]["min"][2]
bottom_after = [robe.matrix_world @ robe.data.vertices[index].co for index in bottom_ring]
hem_amplitude = max(point.z for point in bottom_after) - min(point.z for point in bottom_after)

metrics = {
    "before": before,
    "after": after,
    "exposed_shin_gap": round(exposed_shin_gap, 5),
    "tunic_to_robe_min_gap": round(tunic_robe_gap, 5),
    "bottom_drop_range": [round(min(bottom_drops), 5), round(max(bottom_drops), 5)],
    "second_drop_range": [round(min(second_drops), 5), round(max(second_drops), 5)],
    "hem_vertical_amplitude": round(hem_amplitude, 5),
    "robe_locked_above_082_max_delta": round(robe_locked_delta, 8),
    "tunic_locked_rows_0_6_max_delta": round(tunic_locked_delta, 8),
    "robe_topology_before": robe_topology_before,
    "robe_topology_after": robe_topology_after,
    "tunic_topology_before": tunic_topology_before,
    "tunic_topology_after": tunic_topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A91_PRE_GATE_METRICS=" + repr(metrics))
if not 0.46 <= after["robe"]["min"][2] <= 0.49:
    raise RuntimeError("A91 robe hem outside compact-proportion target")
if not 0.19 <= exposed_shin_gap <= 0.22:
    raise RuntimeError("A91 visible shin gap outside target")
if not 0.17 <= tunic_robe_gap <= 0.22:
    raise RuntimeError("A91 tunic layering gap outside target")
if not 0.025 <= hem_amplitude <= 0.060:
    raise RuntimeError("A91 hem became planar or excessively wavy")
if robe_locked_delta > 0.000001 or tunic_locked_delta > 0.000001:
    raise RuntimeError("A91 moved locked upper garment vertices")
for key in ("foot_l", "foot_r", "leg_l", "leg_r", "tail"):
    if before[key] != after[key]:
        raise RuntimeError(f"A91 changed locked {key} bounds")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_LowerGarmentRehang_A91"
scene["comforting_cat_v6_stage"] = "LOWER_GARMENT_REHANG"
scene["comforting_cat_v6_attempt"] = 91
scene["comforting_cat_v6_dominant_defect"] = "excessive_exposed_shin_gap_stilted_proportion"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "LOWER_GARMENT_REHANG",
    "attempt": 91,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "excessive_exposed_shin_gap_stilted_proportion",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Robe bottom two rings", "V6_FrontTunic bottom two rows Z only"],
        "preserved": [
            "A90 face/brows/head",
            "ears",
            "robe vertices z>=0.82",
            "tunic rows 0-6",
            "scarf/satchel/arms",
            "legs/feet/tail",
            "camera/lights/materials",
        ],
    },
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
