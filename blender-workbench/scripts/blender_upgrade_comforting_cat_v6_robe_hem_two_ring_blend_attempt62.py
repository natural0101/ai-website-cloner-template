"""Blend the robe's two lowest rings into a soft hem without side paper points."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_robe_hem_two_ring_blend_attempt62"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_scarf_drape_cloth_relief_attempt60.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_robe_hem_two_ring_blend_attempt62.blend"
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


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
non_robe_objects = [obj for obj in descendants(root) if obj.name != robe.name]
non_robe_hash_before = geometry_hash(non_robe_objects)
before = bounds(robe)
preserved_source = preserve_copy(
    robe,
    "Comforting_Cat_V6",
    "A62",
    "a61_single_ring_kept_side_points_and_back_v",
)

if len(robe.data.vertices) != 450:
    raise RuntimeError(f"Unexpected robe topology: {len(robe.data.vertices)} vertices")

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

inverse = robe.matrix_world.inverted()
center_y = (before["min"][1] + before["max"][1]) * 0.5
half_y = before["dimensions"][1] * 0.5
locked_before: dict[int, Vector] = {}
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if world.z > 0.88:
        locked_before[vertex.index] = world.copy()


def angle_for_world(world: Vector) -> float:
    return math.atan2((world.y - center_y) / half_y, world.x / 0.70)


bottom_world_after: list[Vector] = []
for index in bottom_ring:
    vertex = robe.data.vertices[index]
    world = robe.matrix_world @ vertex.co
    theta = angle_for_world(world)
    half_width = 0.650 if math.cos(theta) < 0.0 else 0.640
    world.x = half_width * math.cos(theta)
    world.z = (
        0.680
        + 0.008 * math.cos(theta + 0.45)
        + 0.009 * math.sin(2.0 * theta - 0.25)
    )
    vertex.co = inverse @ world
    bottom_world_after.append(world)

second_world_after: list[Vector] = []
for index in second_ring:
    vertex = robe.data.vertices[index]
    world = robe.matrix_world @ vertex.co
    theta = angle_for_world(world)
    half_width = 0.665 if math.cos(theta) < 0.0 else 0.655
    world.x = half_width * math.cos(theta)
    world.z = (
        0.752
        + 0.004 * math.cos(theta + 0.45)
        + 0.003 * math.sin(2.0 * theta - 0.25)
    )
    vertex.co = inverse @ world
    second_world_after.append(world)

bottom_center = robe.data.vertices[bottom_center_index]
bottom_center_world = robe.matrix_world @ bottom_center.co
bottom_center_world.z = sum(point.z for point in bottom_world_after) / len(bottom_world_after)
bottom_center.co = inverse @ bottom_center_world
robe.data.update()

bevel = next((modifier for modifier in robe.modifiers if modifier.name == "V6_RobeSoftHem"), None)
if bevel is None:
    raise RuntimeError("Expected V6_RobeSoftHem modifier")
bevel.width = 0.030
bevel.segments = 4

bpy.context.view_layer.update()
after = bounds(robe)
non_robe_hash_after = geometry_hash(non_robe_objects)
if non_robe_hash_before != non_robe_hash_after:
    raise RuntimeError("Two-ring robe hem pass changed locked geometry or transforms")

locked_max_delta = 0.0
for index, before_world in locked_before.items():
    after_world = robe.matrix_world @ robe.data.vertices[index].co
    locked_max_delta = max(locked_max_delta, (after_world - before_world).length)

bottom_after = [robe.matrix_world @ robe.data.vertices[index].co for index in bottom_ring]
second_after = [robe.matrix_world @ robe.data.vertices[index].co for index in second_ring]
hem_min_z = min(point.z for point in bottom_after)
hem_max_z = max(point.z for point in bottom_after)
left_point = min(bottom_after, key=lambda point: point.x)
right_point = max(bottom_after, key=lambda point: point.x)
bottom_width = max(point.x for point in bottom_after) - min(point.x for point in bottom_after)
second_width = max(point.x for point in second_after) - min(point.x for point in second_after)

front_template: list[Vector] = []
for index in range(33):
    theta = -math.pi + math.pi * index / 32
    half_width = 0.650 if math.cos(theta) < 0.0 else 0.640
    x = half_width * math.cos(theta)
    z = 0.680 + 0.008 * math.cos(theta + 0.45) + 0.009 * math.sin(2.0 * theta - 0.25)
    front_template.append(Vector((x, 0.0, z)))
front_segment_lengths = [
    (front_template[index + 1] - front_template[index]).length
    for index in range(len(front_template) - 1)
]
front_angles: list[float] = []
for index in range(1, len(front_template) - 1):
    incoming = front_template[index - 1] - front_template[index]
    outgoing = front_template[index + 1] - front_template[index]
    front_angles.append(math.degrees(incoming.angle(outgoing)))

metrics = {
    "robe_dimensions": after["dimensions"],
    "robe_width_over_height": round(after["dimensions"][0] / after["dimensions"][2], 5),
    "hem_vertical_amplitude": round(hem_max_z - hem_min_z, 5),
    "left_right_endpoint_delta_z": round(abs(left_point.z - right_point.z), 5),
    "bottom_ring_width": round(bottom_width, 5),
    "second_ring_width": round(second_width, 5),
    "second_minus_bottom_width": round(second_width - bottom_width, 5),
    "max_front_hem_segment": round(max(front_segment_lengths), 5),
    "min_front_hem_angle": round(min(front_angles), 5),
    "side_depth_delta": round(after["dimensions"][1] - before["dimensions"][1], 5),
    "locked_above_088_max_delta": round(locked_max_delta, 8),
    "bevel_width": bevel.width,
    "bevel_segments": bevel.segments,
    "non_robe_hash_before": non_robe_hash_before,
    "non_robe_hash_after": non_robe_hash_after,
}
print("A62_PRE_GATE_METRICS=" + repr(metrics))
if not 1.40 <= metrics["robe_dimensions"][0] <= 1.43:
    raise RuntimeError("Robe width envelope changed")
if not 1.57 <= metrics["robe_dimensions"][2] <= 1.60:
    raise RuntimeError("Robe height envelope changed")
if not 0.88 <= metrics["robe_width_over_height"] <= 0.91:
    raise RuntimeError("Robe width/height ratio changed")
if not 0.025 <= metrics["hem_vertical_amplitude"] <= 0.038:
    raise RuntimeError("Hem wave remains too rigid or too dramatic")
if not 0.008 <= metrics["left_right_endpoint_delta_z"] <= 0.020:
    raise RuntimeError("Hem asymmetry outside target")
if not 0.010 <= metrics["second_minus_bottom_width"] <= 0.040:
    raise RuntimeError("Two-ring side transition still forms a paper wing")
if metrics["max_front_hem_segment"] > 0.08:
    raise RuntimeError("Hem contains a long straight segment")
if metrics["min_front_hem_angle"] < 150.0:
    raise RuntimeError("Hem contains an origami-like sharp corner")
if abs(metrics["side_depth_delta"]) > 0.015:
    raise RuntimeError("Side depth envelope changed")
if metrics["locked_above_088_max_delta"] > 0.000001:
    raise RuntimeError("Robe vertices above the hem band moved")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_RobeHemTwoRingBlend_A62"
scene["comforting_cat_v6_stage"] = "ROBE_HEM_TWO_RING_BLEND"
scene["comforting_cat_v6_attempt"] = 62
scene["comforting_cat_v6_dominant_defect"] = "a61_side_points_and_back_v"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "ROBE_HEM_TWO_RING_BLEND",
    "attempt": 62,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a61_side_points_and_back_v",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": [robe.name], "non_robe_geometry_unchanged": True},
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
