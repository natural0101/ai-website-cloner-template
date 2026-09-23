"""Remediate A102's exact-side tail stump without changing its front X/Z silhouette."""

from __future__ import annotations

import bmesh
import hashlib
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v6_tail_side_sweep_attempt103"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_silhouette_compaction_attempt102.blend").resolve()
SOURCE_REPORT = (
    REPORT_DIR / "comforting_cat_v6_tail_silhouette_compaction_attempt102_scene_report.json"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

EXPECTED_BLEND_SHA256 = "660cb5c3ad658b83bdaf2f66fd08dc0ed13cfb61630b18c873c22e7fd57cbd9c"
EXPECTED_REPORT_SHA256 = "3de791be86181ffd10a97ea54dd18d66a7e33f7d0baf096c0a09e03b8b1eb691"
EXPECTED_NON_TAIL_HASH = "0d0c622271a090ffa5fd63c1401bff65f7daf097999e91412667c879ce2a1e83"
EXPECTED_TAIL_MATERIAL_TOPOLOGY_HASH = "603223d4b6162255b1a6e13aeb244dc6b7c51bac19287166cbc3a1f9d67db2d8"
EXPECTED_TIP_MATERIAL_TOPOLOGY_HASH = "1320bb4fecdd38bccc608a35274a8be0730c088a18db707d4080c7c848b62b09"

RING_SEGMENTS = 16
LOCKED_INDICES = list(range(304)) + [496]

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
if hashlib.sha256(SOURCE_BLEND.read_bytes()).hexdigest() != EXPECTED_BLEND_SHA256:
    raise RuntimeError("A103 source blend SHA256 mismatch")
if hashlib.sha256(SOURCE_REPORT.read_bytes()).hexdigest() != EXPECTED_REPORT_SHA256:
    raise RuntimeError("A103 source structural report SHA256 mismatch")

checkpoint = (CHECKPOINT_DIR / "comforting_cat_v6_before_tail_side_sweep_attempt103.blend").resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def topology(obj: bpy.types.Object) -> dict[str, int]:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    result = {
        "vertices": len(mesh.verts),
        "edges": len(mesh.edges),
        "faces": len(mesh.faces),
        "boundary_edges": sum(1 for edge in mesh.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in mesh.edges if not edge.is_manifold),
        "loose_vertices": sum(1 for vertex in mesh.verts if not vertex.link_edges),
    }
    mesh.free()
    return result


def object_state_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        digest.update(obj.type.encode("ascii"))
        digest.update((obj.parent.name if obj.parent else "").encode("utf-8"))
        digest.update(f"{int(obj.hide_render)},{int(obj.hide_viewport)}".encode("ascii"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for modifier in obj.modifiers:
            digest.update(f"{modifier.name}:{modifier.type};".encode("utf-8"))
        if obj.type == "MESH":
            digest.update(
                ",".join(material.name if material else "" for material in obj.data.materials).encode("utf-8")
            )
            for vertex in obj.data.vertices:
                digest.update(f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii"))
            for polygon in obj.data.polygons:
                digest.update(
                    (f"{polygon.material_index}:" + ",".join(str(i) for i in polygon.vertices) + ";").encode("ascii")
                )
    return digest.hexdigest()


def indices_hash(obj: bpy.types.Object, indices: list[int]) -> str:
    digest = hashlib.sha256()
    for index in indices:
        point = obj.matrix_world @ obj.data.vertices[index].co
        digest.update(f"{index}:{point.x:.9f},{point.y:.9f},{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def xz_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        digest.update(f"{vertex.index}:{point.x:.9f},{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def material_topology_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    digest.update(f"{len(obj.data.vertices)},{len(obj.data.edges)},{len(obj.data.polygons)};".encode("ascii"))
    for edge in obj.data.edges:
        digest.update(f"{edge.vertices[0]},{edge.vertices[1]};".encode("ascii"))
    for polygon in obj.data.polygons:
        digest.update(
            (f"{polygon.material_index}:" + ",".join(str(i) for i in polygon.vertices) + ";").encode("ascii")
        )
    for modifier in obj.modifiers:
        digest.update(f"{modifier.name}:{modifier.type};".encode("utf-8"))
    return digest.hexdigest()


def ring_center(obj: bpy.types.Object, ring: int) -> Vector:
    first = ring * RING_SEGMENTS
    points = [
        obj.matrix_world @ obj.data.vertices[index].co
        for index in range(first, first + RING_SEGMENTS)
    ]
    return sum(points, Vector()) / RING_SEGMENTS


def smoothstep01(value: float) -> float:
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


def overlap_1d(first: dict, second: dict, axis: int) -> float:
    return max(0.0, min(first["max"][axis], second["max"][axis]) - max(first["min"][axis], second["min"][axis]))


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
robe = bpy.data.objects["V6_Robe"]
right_leg = bpy.data.objects["V6_Leg_R"]
right_foot = bpy.data.objects["V6_Foot_R"]

expected_tail_topology = {
    "vertices": 498, "edges": 1008, "faces": 512,
    "boundary_edges": 0, "non_manifold_edges": 0, "loose_vertices": 0,
}
expected_tip_topology = {
    "vertices": 1490, "edges": 3024, "faces": 1536,
    "boundary_edges": 0, "non_manifold_edges": 0, "loose_vertices": 0,
}
topology_before = {tail.name: topology(tail), tip.name: topology(tip)}
if topology_before[tail.name] != expected_tail_topology or topology_before[tip.name] != expected_tip_topology:
    raise RuntimeError(f"Unexpected A102 tail topology: {topology_before}")

target_names = {tail.name, tip.name}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in target_names]
non_tail_hash_before = object_state_hash(locked_objects)

material_topology_before = {
    tail.name: material_topology_hash(tail),
    tip.name: material_topology_hash(tip),
}
if material_topology_before[tail.name] != EXPECTED_TAIL_MATERIAL_TOPOLOGY_HASH:
    raise RuntimeError("A103 source TailBase material/topology mismatch")
if material_topology_before[tip.name] != EXPECTED_TIP_MATERIAL_TOPOLOGY_HASH:
    raise RuntimeError("A103 source TailTip material/topology mismatch")

before = {obj.name: bounds(obj) for obj in (tail, tip, robe, right_leg, right_foot)}
lock_hash_before = indices_hash(tail, LOCKED_INDICES)
tail_xz_hash_before = xz_hash(tail)
ring19_before = {
    index: tail.matrix_world @ tail.data.vertices[index].co
    for index in range(304, 320)
}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A103", "a102_front_accepted_tail_source"),
    preserve_copy(tip, "Comforting_Cat_V6", "A103", "a102_round_tip_source"),
]

source_centers = [ring_center(tail, ring) for ring in range(31)]
target_centers = [center.copy() for center in source_centers]
if any(
    abs(float(tail.matrix_world[row][column]) - (1.0 if row == column else 0.0)) > 1.0e-9
    for row in range(4)
    for column in range(4)
):
    raise RuntimeError("A103 requires identity TailBase world transform for exact local-Y editing")
deformation = []
for ring in range(19, 31):
    u = (ring - 18) / 12.0
    delta_y = 0.10 * smoothstep01(u) + 0.06 * u * u
    target_centers[ring].y += delta_y
    first = ring * RING_SEGMENTS
    for index in range(first, first + RING_SEGMENTS):
        tail.data.vertices[index].co.y += delta_y
    deformation.append({"ring": ring, "u": round(u, 8), "delta_y": round(delta_y, 8)})

tail.data.vertices[497].co.y += 0.160
tail.data.update()
bpy.context.view_layer.update()

terminal_xy = Vector((
    target_centers[30].x - target_centers[29].x,
    target_centers[30].y - target_centers[29].y,
    0.0,
))
if terminal_xy.length <= 1.0e-8:
    raise RuntimeError("Degenerate A103 terminal tangent")
terminal_xy.normalize()
tip_target_center = target_centers[30] + terminal_xy * 0.040
tip_target_dimensions = Vector((0.200, 0.095, 0.115))
tip_angle = math.atan2(terminal_xy.y, terminal_xy.x)
tip_rotation = Matrix.Rotation(tip_angle, 4, "Z")

tip_before = before[tip.name]
tip_center_before = Vector(tuple((tip_before["min"][axis] + tip_before["max"][axis]) * 0.5 for axis in range(3)))
tip_dimensions_before = Vector(tip_before["dimensions"])
inverse_tip = tip.matrix_world.inverted()
for vertex in tip.data.vertices:
    world = tip.matrix_world @ vertex.co
    offset = world - tip_center_before
    normalized = Vector(tuple(offset[axis] / tip_dimensions_before[axis] for axis in range(3)))
    shaped = Vector(tuple(normalized[axis] * tip_target_dimensions[axis] for axis in range(3)))
    oriented = tip_rotation @ shaped
    oriented.x *= 1.25
    oriented.y *= 0.925
    vertex.co = inverse_tip @ (tip_target_center + oriented)
tip.data.update()
bpy.context.view_layer.update()

after = {obj.name: bounds(obj) for obj in (tail, tip, robe, right_leg, right_foot)}
non_tail_hash_after = object_state_hash(locked_objects)
lock_hash_after = indices_hash(tail, LOCKED_INDICES)
tail_xz_hash_after = xz_hash(tail)
topology_after = {tail.name: topology(tail), tip.name: topology(tip)}
material_topology_after = {tail.name: material_topology_hash(tail), tip.name: material_topology_hash(tip)}
ring19_after = {index: tail.matrix_world @ tail.data.vertices[index].co for index in range(304, 320)}
ring19_max_displacement = max((ring19_after[index] - ring19_before[index]).length for index in ring19_before)
centers_after = [ring_center(tail, ring) for ring in range(18, 31)]
terminal_angle = math.degrees(tip_angle)

tail_bounds = after[tail.name]
tip_bounds = after[tip.name]
robe_bounds = after[robe.name]
leg_bounds = after[right_leg.name]
foot_bounds = after[right_foot.name]
combined_min_x = min(tail_bounds["min"][0], tip_bounds["min"][0])
combined_max_x = max(tail_bounds["max"][0], tip_bounds["max"][0])
combined_max_y = max(tail_bounds["max"][1], tip_bounds["max"][1])
combined_x_span = combined_max_x - combined_min_x
side_reach = combined_max_y - robe_bounds["max"][1]
tail_tip_overlap = [overlap_1d(tail_bounds, tip_bounds, axis) for axis in range(3)]
robe_tail_overlap = [overlap_1d(robe_bounds, tail_bounds, axis) for axis in range(3)]
tail_leg_overlap = [overlap_1d(tail_bounds, leg_bounds, axis) for axis in range(3)]
tail_foot_overlap = [overlap_1d(tail_bounds, foot_bounds, axis) for axis in range(3)]
tip_side_aspect = tip_bounds["dimensions"][1] / tip_bounds["dimensions"][2]

print("A103_GATE_DIAG=" + json.dumps({
    "tail_bounds": tail_bounds,
    "tip_bounds": tip_bounds,
    "tip_target_center": [float(value) for value in tip_target_center],
    "terminal_angle": terminal_angle,
    "combined_x_span": combined_x_span,
    "side_reach": side_reach,
    "tail_tip_overlap": tail_tip_overlap,
}, ensure_ascii=False))

if non_tail_hash_after != non_tail_hash_before:
    raise RuntimeError("A103 changed non-tail A102 state")
if lock_hash_after != lock_hash_before:
    raise RuntimeError("A103 changed locked rings 0-18 or cap 496")
if tail_xz_hash_after != tail_xz_hash_before:
    raise RuntimeError("A103 changed accepted A102 TailBase X/Z silhouette")
if topology_after != topology_before or material_topology_after != material_topology_before:
    raise RuntimeError("A103 changed topology, materials, faces, edges or modifiers")
if ring19_max_displacement > 0.003:
    raise RuntimeError(f"A103 ring19 seam displacement too large: {ring19_max_displacement}")
if not 48.0 <= terminal_angle <= 60.0:
    raise RuntimeError(f"A103 terminal tangent outside target: {terminal_angle}")
if any(centers_after[index + 1].y <= centers_after[index].y for index in range(len(centers_after) - 1)):
    raise RuntimeError("A103 distal centerline Y is not monotonic")
if not 0.77 <= tail_bounds["dimensions"][1] <= 0.80:
    raise RuntimeError(f"A103 TailBase Y span outside target: {tail_bounds['dimensions'][1]}")
if not 0.37 <= side_reach <= 0.40:
    raise RuntimeError(f"A103 side reach outside target: {side_reach}")
if not 0.76 <= combined_x_span <= 0.80:
    raise RuntimeError(f"A103 combined X span outside target: {combined_x_span}")
if not 0.135 <= tip_bounds["dimensions"][0] <= 0.150:
    raise RuntimeError(f"A103 tip projected X span outside target: {tip_bounds['dimensions'][0]}")
if not 0.16 <= tip_bounds["dimensions"][1] <= 0.18:
    raise RuntimeError(f"A103 tip projected Y span outside target: {tip_bounds['dimensions'][1]}")
if tip_side_aspect < 1.35:
    raise RuntimeError(f"A103 tip side aspect remains bead-like: {tip_side_aspect}")
if tail_tip_overlap[0] < 0.05 or tail_tip_overlap[1] < 0.10 or tail_tip_overlap[2] < 0.10:
    raise RuntimeError(f"A103 tip integration overlap too low: {tail_tip_overlap}")
if any(tail_leg_overlap[axis] > (0.02544, 0.11988, 0.49)[axis] + 1e-5 for axis in range(3)):
    raise RuntimeError(f"A103 increased tail/right-leg overlap: {tail_leg_overlap}")
if any(tail_foot_overlap[axis] > (0.12815, 0.08975, 0.14476)[axis] + 1e-5 for axis in range(3)):
    raise RuntimeError(f"A103 increased tail/right-foot overlap: {tail_foot_overlap}")
for actual, expected in zip(robe_tail_overlap, (0.31844, 0.45, 0.26557)):
    if abs(actual - expected) > 1e-5:
        raise RuntimeError(f"A103 changed robe/tail concealment: {robe_tail_overlap}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "deformation": deformation,
    "terminal_angle_degrees": round(terminal_angle, 6),
    "tip_target_center": [round(float(value), 8) for value in tip_target_center],
    "tip_target_dimensions_local": [0.200, 0.095, 0.115],
    "tip_world_projection_scale": [1.25, 0.925, 1.0],
    "ring19_max_displacement": round(ring19_max_displacement, 8),
    "combined_x_span": round(combined_x_span, 6),
    "combined_max_y": round(combined_max_y, 6),
    "side_reach": round(side_reach, 6),
    "tip_side_aspect": round(tip_side_aspect, 6),
    "tail_tip_overlap": [round(value, 6) for value in tail_tip_overlap],
    "robe_tail_overlap": [round(value, 6) for value in robe_tail_overlap],
    "tail_right_leg_overlap": [round(value, 6) for value in tail_leg_overlap],
    "tail_right_foot_overlap": [round(value, 6) for value in tail_foot_overlap],
    "source_blend_sha256": EXPECTED_BLEND_SHA256,
    "source_report_sha256": EXPECTED_REPORT_SHA256,
    "non_tail_hash_before": non_tail_hash_before,
    "non_tail_hash_after": non_tail_hash_after,
    "locked_hash_before": lock_hash_before,
    "locked_hash_after": lock_hash_after,
    "tail_xz_hash_before": tail_xz_hash_before,
    "tail_xz_hash_after": tail_xz_hash_after,
    "topology_before": topology_before,
    "topology_after": topology_after,
}
print("A103_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailSideSweep_A103"
scene["comforting_cat_v6_stage"] = "TAIL_SIDE_SWEEP"
scene["comforting_cat_v6_attempt"] = 103
scene["comforting_cat_v6_dominant_defect"] = "exact_side_tail_stump_and_tip_bead"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "TAIL_SIDE_SWEEP",
    "attempt": 103,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "exact_side_tail_stump_and_tip_bead",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": [tail.name, tip.name],
        "preserved": [
            "A102 TailBase X/Z silhouette",
            "TailBase rings 0-18 and start cap 496",
            "robe tail port and entire non-tail A98 scene",
            "camera, lights, materials and topology",
        ],
    },
    "visual_abort_gates": [
        "exact side must read as a swept taper, not a third leg or horizontal rod",
        "cream tip must continue the tangent without a bead or cap silhouette",
        "front and three-quarter A102 tail mass must remain unchanged",
        "back must not gain a new orange wedge or seam kink",
    ],
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
