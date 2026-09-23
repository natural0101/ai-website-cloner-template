"""Replace A103's detached cream tip with a continuous distal material zone."""

from __future__ import annotations

import bmesh
import hashlib
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_integrated_cream_tail_tip_attempt104"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_side_sweep_attempt103.blend").resolve()
SOURCE_REPORT = (REPORT_DIR / "comforting_cat_v6_tail_side_sweep_attempt103_scene_report.json").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

EXPECTED_BLEND_SHA256 = "a35e29a0017220c96ff19670a5cb9e5bf2afe2123fb1710035b57d68ae088e70"
EXPECTED_REPORT_SHA256 = "47b79323fbec9334c3f488497d604d517897c6de0c29ca7995eb76a991d0d0b2"
RING_SEGMENTS = 16
LOCKED_GEOMETRY_INDICES = list(range(448)) + [496]
MUTABLE_GEOMETRY_INDICES = list(range(448, 496)) + [497]
CREAM_FACE_INDICES = set(range(448, 480)) | set(range(481, 512, 2))

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
if hashlib.sha256(SOURCE_BLEND.read_bytes()).hexdigest() != EXPECTED_BLEND_SHA256:
    raise RuntimeError("A104 source blend SHA256 mismatch")
if hashlib.sha256(SOURCE_REPORT.read_bytes()).hexdigest() != EXPECTED_REPORT_SHA256:
    raise RuntimeError("A104 source report SHA256 mismatch")

checkpoint = (CHECKPOINT_DIR / "comforting_cat_v6_before_integrated_cream_tail_tip_attempt104.blend").resolve()
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


def z_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        digest.update(f"{vertex.index}:{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def mesh_connectivity_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for edge in obj.data.edges:
        digest.update(f"{edge.vertices[0]},{edge.vertices[1]};".encode("ascii"))
    for polygon in obj.data.polygons:
        digest.update((",".join(str(i) for i in polygon.vertices) + ";").encode("ascii"))
    for modifier in obj.modifiers:
        digest.update(f"{modifier.name}:{modifier.type};".encode("utf-8"))
    return digest.hexdigest()


def polygon_material_hash(obj: bpy.types.Object, indices: list[int]) -> str:
    digest = hashlib.sha256()
    for index in indices:
        digest.update(f"{index}:{obj.data.polygons[index].material_index};".encode("ascii"))
    return digest.hexdigest()


def ring_center(obj: bpy.types.Object, ring: int) -> Vector:
    first = ring * RING_SEGMENTS
    points = [
        obj.matrix_world @ obj.data.vertices[index].co
        for index in range(first, first + RING_SEGMENTS)
    ]
    return sum(points, Vector()) / RING_SEGMENTS


def ring_spans(obj: bpy.types.Object, ring: int) -> tuple[float, float, float]:
    first = ring * RING_SEGMENTS
    points = [
        obj.matrix_world @ obj.data.vertices[index].co
        for index in range(first, first + RING_SEGMENTS)
    ]
    return tuple(max(point[axis] for point in points) - min(point[axis] for point in points) for axis in range(3))


def overlap_1d(first: dict, second: dict, axis: int) -> float:
    return max(0.0, min(first["max"][axis], second["max"][axis]) - max(first["min"][axis], second["min"][axis]))


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
robe = bpy.data.objects["V6_Robe"]
right_leg = bpy.data.objects["V6_Leg_R"]
right_foot = bpy.data.objects["V6_Foot_R"]

if any(
    abs(float(tail.matrix_world[row][column]) - (1.0 if row == column else 0.0)) > 1.0e-9
    for row in range(4)
    for column in range(4)
):
    raise RuntimeError("A104 requires identity TailBase world transform")

expected_tail_topology = {
    "vertices": 498, "edges": 1008, "faces": 512,
    "boundary_edges": 0, "non_manifold_edges": 0, "loose_vertices": 0,
}
topology_before = topology(tail)
if topology_before != expected_tail_topology:
    raise RuntimeError(f"Unexpected A103 TailBase topology: {topology_before}")
if len(CREAM_FACE_INDICES) != 48:
    raise RuntimeError("A104 cream face selection must contain exactly 48 faces")
for index in range(448, 480):
    if len(tail.data.polygons[index].vertices) != 4:
        raise RuntimeError(f"A104 expected distal quad at face {index}")
for index in range(481, 512, 2):
    if 497 not in tail.data.polygons[index].vertices:
        raise RuntimeError(f"A104 expected end-cap face containing vertex 497 at {index}")

target_names = {tail.name, tip.name}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in target_names]
locked_hash_before = object_state_hash(locked_objects)
locked_geometry_hash_before = indices_hash(tail, LOCKED_GEOMETRY_INDICES)
z_hash_before = z_hash(tail)
connectivity_hash_before = mesh_connectivity_hash(tail)
unchanged_face_indices = sorted(set(range(len(tail.data.polygons))) - CREAM_FACE_INDICES)
unchanged_material_hash_before = polygon_material_hash(tail, unchanged_face_indices)
ring_spans_before = {ring: ring_spans(tail, ring) for ring in range(28, 31)}
before = {obj.name: bounds(obj) for obj in (tail, tip, robe, right_leg, right_foot)}

preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A104", "a103_swept_tail_source"),
    preserve_copy(tip, "Comforting_Cat_V6", "A104", "a103_detached_cream_tip_source"),
]

center30_before = ring_center(tail, 30)
target_center30 = Vector((1.080, 0.790, float(center30_before.z)))
delta = target_center30 - center30_before
weights = {28: 7.0 / 27.0, 29: 20.0 / 27.0, 30: 1.0}
for ring, weight in weights.items():
    first = ring * RING_SEGMENTS
    for index in range(first, first + RING_SEGMENTS):
        tail.data.vertices[index].co.x += delta.x * weight
        tail.data.vertices[index].co.y += delta.y * weight
tail.data.vertices[497].co.x += delta.x
tail.data.vertices[497].co.y += delta.y

if not tip.data.materials:
    raise RuntimeError("A104 TailTip has no cream material")
cream_material = tip.data.materials[0]
if "Cream" not in cream_material.name:
    raise RuntimeError(f"Unexpected A104 cream material: {cream_material.name}")
cream_index = next(
    (index for index, material in enumerate(tail.data.materials) if material == cream_material),
    -1,
)
if cream_index < 0:
    tail.data.materials.append(cream_material)
    cream_index = len(tail.data.materials) - 1
for face_index in CREAM_FACE_INDICES:
    tail.data.polygons[face_index].material_index = cream_index

tip.hide_render = True
tip.hide_viewport = True
tip.hide_set(True)
tip.parent = None
tail.data.update()
bpy.context.view_layer.update()

after = {obj.name: bounds(obj) for obj in (tail, tip, robe, right_leg, right_foot)}
locked_hash_after = object_state_hash(locked_objects)
locked_geometry_hash_after = indices_hash(tail, LOCKED_GEOMETRY_INDICES)
z_hash_after = z_hash(tail)
connectivity_hash_after = mesh_connectivity_hash(tail)
unchanged_material_hash_after = polygon_material_hash(tail, unchanged_face_indices)
topology_after = topology(tail)
ring_spans_after = {ring: ring_spans(tail, ring) for ring in range(28, 31)}

centers = {ring: ring_center(tail, ring) for ring in range(27, 31)}
segments = [centers[ring + 1] - centers[ring] for ring in range(27, 30)]
segment_lengths = [segment.length for segment in segments]
terminal_angle = math.degrees(math.atan2(segments[-1].y, segments[-1].x))
turn_angle = math.degrees(segments[-2].angle(segments[-1]))
tail_bounds = after[tail.name]
robe_bounds = after[robe.name]
leg_bounds = after[right_leg.name]
foot_bounds = after[right_foot.name]
tail_x_span = tail_bounds["dimensions"][0]
side_reach = tail_bounds["max"][1] - robe_bounds["max"][1]
right_protrusion = tail_bounds["max"][0] - robe_bounds["max"][0]
robe_tail_overlap = [overlap_1d(robe_bounds, tail_bounds, axis) for axis in range(3)]
tail_leg_overlap = [overlap_1d(tail_bounds, leg_bounds, axis) for axis in range(3)]
tail_foot_overlap = [overlap_1d(tail_bounds, foot_bounds, axis) for axis in range(3)]
cream_faces_after = [
    polygon.index for polygon in tail.data.polygons if polygon.material_index == cream_index
]

if locked_hash_after != locked_hash_before:
    raise RuntimeError("A104 changed scene state outside TailBase and TailTip")
if locked_geometry_hash_after != locked_geometry_hash_before:
    raise RuntimeError("A104 changed locked TailBase rings 0-27 or cap 496")
if z_hash_after != z_hash_before:
    raise RuntimeError("A104 changed TailBase Z coordinates")
if connectivity_hash_after != connectivity_hash_before or topology_after != topology_before:
    raise RuntimeError("A104 changed TailBase connectivity or topology")
if unchanged_material_hash_after != unchanged_material_hash_before:
    raise RuntimeError("A104 changed material indices outside the distal cream patch")
if set(cream_faces_after) != CREAM_FACE_INDICES:
    raise RuntimeError(f"A104 cream assignment is not exactly the 48-face distal patch: {cream_faces_after}")
if ring_spans_after != ring_spans_before:
    raise RuntimeError("A104 changed distal ring cross-sections instead of translating them")
if tip.parent is not None or not tip.hide_render or not tip.hide_viewport:
    raise RuntimeError("A104 detached TailTip remains active or exportable")
if not 0.748 <= tail_x_span <= 0.765:
    raise RuntimeError(f"A104 TailBase X span outside target: {tail_x_span}")
if not 0.385 <= side_reach <= 0.400:
    raise RuntimeError(f"A104 side reach outside target: {side_reach}")
if not 0.43 <= right_protrusion <= 0.46:
    raise RuntimeError(f"A104 right protrusion outside target: {right_protrusion}")
if not 46.0 <= terminal_angle <= 52.0:
    raise RuntimeError(f"A104 terminal tangent outside target: {terminal_angle}")
if not 0.06 <= segment_lengths[-2] <= 0.075 or not 0.06 <= segment_lengths[-1] <= 0.075:
    raise RuntimeError(f"A104 terminal segment lengths outside target: {segment_lengths}")
segment_ratio = segment_lengths[-2] / segment_lengths[-1]
if not 0.85 <= segment_ratio <= 1.15:
    raise RuntimeError(f"A104 terminal segment ratio outside target: {segment_ratio}")
if turn_angle >= 8.0:
    raise RuntimeError(f"A104 terminal turn angle creates a kink: {turn_angle}")
if any(tail_leg_overlap[axis] > (0.02544, 0.11988, 0.49)[axis] + 1e-5 for axis in range(3)):
    raise RuntimeError(f"A104 increased tail/right-leg overlap: {tail_leg_overlap}")
if any(tail_foot_overlap[axis] > (0.12815, 0.08975, 0.14476)[axis] + 1e-5 for axis in range(3)):
    raise RuntimeError(f"A104 increased tail/right-foot overlap: {tail_foot_overlap}")
for actual, expected in zip(robe_tail_overlap, (0.31844, 0.45, 0.26557)):
    if abs(actual - expected) > 1e-5:
        raise RuntimeError(f"A104 changed robe/tail concealment: {robe_tail_overlap}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "source_blend_sha256": EXPECTED_BLEND_SHA256,
    "source_report_sha256": EXPECTED_REPORT_SHA256,
    "center30_before": [round(float(value), 8) for value in center30_before],
    "center30_after": [round(float(value), 8) for value in centers[30]],
    "delta": [round(float(value), 8) for value in delta],
    "ring_weights": weights,
    "cream_material": cream_material.name,
    "cream_material_index": cream_index,
    "cream_face_count": len(cream_faces_after),
    "cream_faces": cream_faces_after,
    "tail_x_span": round(tail_x_span, 6),
    "side_reach": round(side_reach, 6),
    "right_protrusion": round(right_protrusion, 6),
    "terminal_angle_degrees": round(terminal_angle, 6),
    "terminal_segment_lengths": [round(value, 6) for value in segment_lengths[-2:]],
    "terminal_segment_ratio": round(segment_ratio, 6),
    "terminal_turn_angle_degrees": round(turn_angle, 6),
    "robe_tail_overlap": [round(value, 6) for value in robe_tail_overlap],
    "tail_right_leg_overlap": [round(value, 6) for value in tail_leg_overlap],
    "tail_right_foot_overlap": [round(value, 6) for value in tail_foot_overlap],
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
    "locked_geometry_hash_before": locked_geometry_hash_before,
    "locked_geometry_hash_after": locked_geometry_hash_after,
    "z_hash_before": z_hash_before,
    "z_hash_after": z_hash_after,
    "topology_before": topology_before,
    "topology_after": topology_after,
}
print("A104_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_IntegratedCreamTailTip_A104"
scene["comforting_cat_v6_stage"] = "INTEGRATED_CREAM_TAIL_TIP"
scene["comforting_cat_v6_attempt"] = 104
scene["comforting_cat_v6_dominant_defect"] = "detached_cream_tip_bead"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "INTEGRATED_CREAM_TAIL_TIP",
    "attempt": 104,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "detached_cream_tip_bead",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": [tail.name, tip.name],
        "preserved": [
            "TailBase rings 0-27 and start cap 496",
            "all TailBase Z coordinates and ring cross-sections",
            "A103 tail sweep through ring 27",
            "robe tail port and entire non-tail scene",
            "camera, lights and non-tail materials",
        ],
    },
    "visual_abort_gates": [
        "cream must read as one connected painted distal zone, never a bead or collar",
        "front tail reach may not lose more than 0.015 BU from A103",
        "side must keep the swept taper without stump or rod",
        "back must not gain a new wedge, kink or intersection",
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
