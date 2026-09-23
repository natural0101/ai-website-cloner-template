"""Compact the visible A98 tail plume in place while preserving its concealed root."""

from __future__ import annotations

import bmesh
import hashlib
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v6_tail_silhouette_compaction_attempt102"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_compact_kitten_body_attempt98.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

EXPECTED_NON_TAIL_HASH = "0d0c622271a090ffa5fd63c1401bff65f7daf097999e91412667c879ce2a1e83"
EXPECTED_TAIL_SOURCE_HASH = "6ff380707b413577b2b913285995b2f956a16d383a4bdee79dcdd7c305c11633"
EXPECTED_TIP_SOURCE_HASH = "0e7db8a1b41536f25ff91335f06e82c5c063d085e3dfdd24f3fd1f73ec70c621"
EXPECTED_ROOT_LOCK_HASH = "29964bd28b2483bec51536aaa5db70257e5dc2f7cf180bd2a8dc6f6058c122fb"
EXPECTED_MUTABLE_SOURCE_HASH = "1f866745ba534d33aa83dd33f895065bff09618f496e66458f5956ccdf7a5ab7"
EXPECTED_TAIL_MATERIAL_TOPOLOGY_HASH = (
    "603223d4b6162255b1a6e13aeb244dc6b7c51bac19287166cbc3a1f9d67db2d8"
)
EXPECTED_TIP_MATERIAL_TOPOLOGY_HASH = (
    "1320bb4fecdd38bccc608a35274a8be0730c088a18db707d4080c7c848b62b09"
)

RING_SEGMENTS = 16
RING_COUNT = 31
ROOT_AND_SEAM_INDICES = list(range(144)) + [496]
MUTABLE_TAIL_INDICES = list(range(144, 496)) + [497]
START_CAP_INDEX = 496
END_CAP_INDEX = 497


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_silhouette_compaction_attempt102.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def topology(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(1 for edge in bm.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
        "loose_vertices": sum(1 for vertex in bm.verts if not vertex.link_edges),
    }
    bm.free()
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
                ",".join(material.name if material else "" for material in obj.data.materials).encode(
                    "utf-8"
                )
            )
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
            for polygon in obj.data.polygons:
                digest.update(
                    (
                        f"{polygon.material_index}:"
                        + ",".join(str(index) for index in polygon.vertices)
                        + ";"
                    ).encode("ascii")
                )
    return digest.hexdigest()


def indices_hash(obj: bpy.types.Object, indices: list[int]) -> str:
    digest = hashlib.sha256()
    for index in indices:
        point = obj.matrix_world @ obj.data.vertices[index].co
        digest.update(
            f"{index}:{point.x:.9f},{point.y:.9f},{point.z:.9f};".encode("ascii")
        )
    return digest.hexdigest()


def material_topology_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    digest.update(
        f"{len(obj.data.vertices)},{len(obj.data.edges)},{len(obj.data.polygons)};".encode("ascii")
    )
    for edge in obj.data.edges:
        digest.update(f"{edge.vertices[0]},{edge.vertices[1]};".encode("ascii"))
    for polygon in obj.data.polygons:
        digest.update(
            (
                f"{polygon.material_index}:"
                + ",".join(str(index) for index in polygon.vertices)
                + ";"
            ).encode("ascii")
        )
    for modifier in obj.modifiers:
        digest.update(f"{modifier.name}:{modifier.type};".encode("utf-8"))
    return digest.hexdigest()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge1 <= edge0:
        raise ValueError("smoothstep requires edge1 > edge0")
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def ring_points(obj: bpy.types.Object, ring: int) -> list[Vector]:
    first = ring * RING_SEGMENTS
    return [
        obj.matrix_world @ obj.data.vertices[index].co
        for index in range(first, first + RING_SEGMENTS)
    ]


def ring_center(obj: bpy.types.Object, ring: int) -> Vector:
    points = ring_points(obj, ring)
    return sum(points, Vector()) / len(points)


def ring_spans(obj: bpy.types.Object, ring: int) -> dict[str, float]:
    points = ring_points(obj, ring)
    return {
        "x": max(point.x for point in points) - min(point.x for point in points),
        "y": max(point.y for point in points) - min(point.y for point in points),
        "z": max(point.z for point in points) - min(point.z for point in points),
    }


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
robe = bpy.data.objects["V6_Robe"]
right_leg = bpy.data.objects["V6_Leg_R"]
right_foot = bpy.data.objects["V6_Foot_R"]
head = bpy.data.objects["V6_Head"]

if len(tail.data.vertices) != RING_COUNT * RING_SEGMENTS + 2:
    raise RuntimeError("A98 TailBase no longer has the A59 31x16 rings plus two caps")
if START_CAP_INDEX != len(tail.data.vertices) - 2 or END_CAP_INDEX != len(tail.data.vertices) - 1:
    raise RuntimeError("Unexpected A98 TailBase cap indices")

target_names = {tail.name, tip.name}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in target_names]
non_tail_hash_before = object_state_hash(locked_objects)
tail_source_hash = indices_hash(tail, list(range(len(tail.data.vertices))))
tip_source_hash = indices_hash(tip, list(range(len(tip.data.vertices))))
root_lock_hash_before = indices_hash(tail, ROOT_AND_SEAM_INDICES)
mutable_source_hash = indices_hash(tail, MUTABLE_TAIL_INDICES)
topology_before = {tail.name: topology(tail), tip.name: topology(tip)}
material_topology_before = {
    tail.name: material_topology_hash(tail),
    tip.name: material_topology_hash(tip),
}

if non_tail_hash_before != EXPECTED_NON_TAIL_HASH:
    raise RuntimeError("A102 source is not the authoritative A98 non-tail scene")
if tail_source_hash != EXPECTED_TAIL_SOURCE_HASH:
    raise RuntimeError("A102 source TailBase vertices do not match authoritative A98")
if tip_source_hash != EXPECTED_TIP_SOURCE_HASH:
    raise RuntimeError("A102 source TailTip vertices do not match authoritative A98")
if root_lock_hash_before != EXPECTED_ROOT_LOCK_HASH:
    raise RuntimeError("A102 source root/seam lock does not match authoritative A98")
if mutable_source_hash != EXPECTED_MUTABLE_SOURCE_HASH:
    raise RuntimeError("A102 source mutable tail band does not match authoritative A98")
if material_topology_before[tail.name] != EXPECTED_TAIL_MATERIAL_TOPOLOGY_HASH:
    raise RuntimeError("A102 source TailBase material/topology hash mismatch")
if material_topology_before[tip.name] != EXPECTED_TIP_MATERIAL_TOPOLOGY_HASH:
    raise RuntimeError("A102 source TailTip material/topology hash mismatch")
if topology_before[tail.name] != {
    "vertices": 498,
    "edges": 1008,
    "faces": 512,
    "boundary_edges": 0,
    "non_manifold_edges": 0,
    "loose_vertices": 0,
}:
    raise RuntimeError(f"Unexpected A98 TailBase topology: {topology_before[tail.name]}")
if topology_before[tip.name] != {
    "vertices": 1490,
    "edges": 3024,
    "faces": 1536,
    "boundary_edges": 0,
    "non_manifold_edges": 0,
    "loose_vertices": 0,
}:
    raise RuntimeError(f"Unexpected A98 TailTip topology: {topology_before[tip.name]}")

before = {
    tail.name: bounds(tail),
    tip.name: bounds(tip),
    robe.name: bounds(robe),
    right_leg.name: bounds(right_leg),
    right_foot.name: bounds(right_foot),
    head.name: bounds(head),
}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A102", "authoritative_a98_tail_source"),
    preserve_copy(tip, "Comforting_Cat_V6", "A102", "authoritative_a98_cream_tip_source"),
]

# Rings 0-8 and start cap 496 remain byte-for-byte fixed. Ring 9 starts with
# a near-zero smooth deformation, preventing a visible kink at the locked seam.
source_centers = [ring_center(tail, ring) for ring in range(RING_COUNT)]
target_centers = [center.copy() for center in source_centers]
ring9_before = {
    index: tail.matrix_world @ tail.data.vertices[index].co
    for index in range(9 * RING_SEGMENTS, 10 * RING_SEGMENTS)
}
anchor = source_centers[8]
inverse_tail = tail.matrix_world.inverted()
deformation: list[dict[str, object]] = []

for ring in range(9, RING_COUNT):
    u = (ring - 8) / (RING_COUNT - 1 - 8)
    envelope = smoothstep(0.0, 1.0, u)
    radial_envelope = smoothstep(0.0, 0.65, u)
    source_center = source_centers[ring]
    target_center = Vector(
        (
            anchor.x + (source_center.x - anchor.x) * (1.0 - 0.12 * envelope),
            anchor.y + (source_center.y - anchor.y) * (1.0 - 0.10 * envelope),
            source_center.z + 0.035 * envelope,
        )
    )
    scale_xz = 1.0 - 0.28 * radial_envelope
    scale_y = 1.0 - 0.24 * radial_envelope
    target_centers[ring] = target_center

    first = ring * RING_SEGMENTS
    for index in range(first, first + RING_SEGMENTS):
        world = tail.matrix_world @ tail.data.vertices[index].co
        offset = world - source_center
        reshaped = target_center + Vector(
            (offset.x * scale_xz, offset.y * scale_y, offset.z * scale_xz)
        )
        tail.data.vertices[index].co = inverse_tail @ reshaped

    deformation.append(
        {
            "ring": ring,
            "u": round(u, 8),
            "envelope": round(envelope, 8),
            "radial_envelope": round(radial_envelope, 8),
            "scale_xz": round(scale_xz, 8),
            "scale_y": round(scale_y, 8),
            "source_center": [round(float(value), 8) for value in source_center],
            "target_center": [round(float(value), 8) for value in target_center],
        }
    )

tail.data.vertices[END_CAP_INDEX].co = inverse_tail @ target_centers[-1]
tail.data.update()
bpy.context.view_layer.update()

# Reuse the existing dense cream-tip mesh. Normalize its A98 bounding box,
# resize it, and align its long axis to the new terminal tangent.
tip_before = before[tip.name]
tip_center_before = Vector(
    tuple((tip_before["min"][axis] + tip_before["max"][axis]) * 0.5 for axis in range(3))
)
tip_dimensions_before = Vector(tip_before["dimensions"])
terminal_tangent = target_centers[30] - target_centers[29]
tip_angle = math.atan2(terminal_tangent.y, terminal_tangent.x)
tip_rotation = Matrix.Rotation(tip_angle, 4, "Z")
tip_target_center = target_centers[30] + Vector((0.035, 0.008, 0.0))
tip_target_dimensions = Vector((0.155, 0.105, 0.115))
inverse_tip = tip.matrix_world.inverted()

for vertex in tip.data.vertices:
    world = tip.matrix_world @ vertex.co
    offset = world - tip_center_before
    normalized = Vector(
        tuple(offset[axis] / tip_dimensions_before[axis] for axis in range(3))
    )
    shaped = Vector(
        tuple(normalized[axis] * tip_target_dimensions[axis] for axis in range(3))
    )
    vertex.co = inverse_tip @ (tip_target_center + tip_rotation @ shaped)

tip.data.update()
bpy.context.view_layer.update()

after = {
    tail.name: bounds(tail),
    tip.name: bounds(tip),
    robe.name: bounds(robe),
    right_leg.name: bounds(right_leg),
    right_foot.name: bounds(right_foot),
    head.name: bounds(head),
}
non_tail_hash_after = object_state_hash(locked_objects)
root_lock_hash_after = indices_hash(tail, ROOT_AND_SEAM_INDICES)
topology_after = {tail.name: topology(tail), tip.name: topology(tip)}
material_topology_after = {
    tail.name: material_topology_hash(tail),
    tip.name: material_topology_hash(tip),
}
ring9_after = {
    index: tail.matrix_world @ tail.data.vertices[index].co
    for index in range(9 * RING_SEGMENTS, 10 * RING_SEGMENTS)
}
ring9_max_displacement = max(
    (ring9_after[index] - ring9_before[index]).length for index in ring9_before
)

tail_bounds = after[tail.name]
tip_bounds = after[tip.name]
robe_bounds = after[robe.name]
right_leg_bounds = after[right_leg.name]
right_foot_bounds = after[right_foot.name]
head_width = after[head.name]["dimensions"][0]
combined_min_x = min(tail_bounds["min"][0], tip_bounds["min"][0])
combined_max_x = max(tail_bounds["max"][0], tip_bounds["max"][0])
combined_x_span = combined_max_x - combined_min_x
robe_tail_overlap = [overlap_1d(robe_bounds, tail_bounds, axis) for axis in range(3)]
tail_tip_overlap = [overlap_1d(tail_bounds, tip_bounds, axis) for axis in range(3)]
tail_leg_overlap = [overlap_1d(tail_bounds, right_leg_bounds, axis) for axis in range(3)]
tail_foot_overlap = [overlap_1d(tail_bounds, right_foot_bounds, axis) for axis in range(3)]
bulge_spans = ring_spans(tail, 18)
terminal_spans = ring_spans(tail, 30)
distal_to_bulge_y = terminal_spans["y"] / bulge_spans["y"]
distal_to_bulge_z = terminal_spans["z"] / bulge_spans["z"]
tail_protrusion = combined_max_x - robe_bounds["max"][0]

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "deformation": deformation,
    "tip_target_center": [round(float(value), 8) for value in tip_target_center],
    "tip_target_dimensions_before_rotation": [
        round(float(value), 8) for value in tip_target_dimensions
    ],
    "tip_tangent_angle_degrees": round(math.degrees(tip_angle), 6),
    "combined_x_span": round(combined_x_span, 6),
    "combined_span_over_head": round(combined_x_span / head_width, 6),
    "tail_protrusion_from_robe": round(tail_protrusion, 6),
    "tail_protrusion_over_head": round(tail_protrusion / head_width, 6),
    "robe_tail_overlap": [round(value, 6) for value in robe_tail_overlap],
    "tail_tip_overlap": [round(value, 6) for value in tail_tip_overlap],
    "tail_right_leg_overlap": [round(value, 6) for value in tail_leg_overlap],
    "tail_right_foot_overlap": [round(value, 6) for value in tail_foot_overlap],
    "ring9_max_displacement": round(ring9_max_displacement, 8),
    "ring18_spans": {axis: round(value, 6) for axis, value in bulge_spans.items()},
    "ring30_spans": {axis: round(value, 6) for axis, value in terminal_spans.items()},
    "distal_to_bulge_y": round(distal_to_bulge_y, 6),
    "distal_to_bulge_z": round(distal_to_bulge_z, 6),
    "source_hashes": {
        "non_tail": non_tail_hash_before,
        "tail_vertices": tail_source_hash,
        "tip_vertices": tip_source_hash,
        "root_and_seam": root_lock_hash_before,
        "mutable_tail_band": mutable_source_hash,
        "tail_material_topology": material_topology_before[tail.name],
        "tip_material_topology": material_topology_before[tip.name],
    },
    "after_hashes": {
        "non_tail": non_tail_hash_after,
        "root_and_seam": root_lock_hash_after,
        "tail_material_topology": material_topology_after[tail.name],
        "tip_material_topology": material_topology_after[tip.name],
    },
    "topology_before": topology_before,
    "topology_after": topology_after,
}
print("A102_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

if non_tail_hash_after != non_tail_hash_before:
    raise RuntimeError("A102 changed the authoritative A98 non-tail scene")
if root_lock_hash_after != root_lock_hash_before:
    raise RuntimeError("A102 changed locked TailBase rings 0-8 or start cap 496")
if topology_after != topology_before:
    raise RuntimeError("A102 changed TailBase or TailTip topology")
if material_topology_after != material_topology_before:
    raise RuntimeError("A102 changed materials, edges, faces or modifiers")
for name, topo in topology_after.items():
    if topo["boundary_edges"] or topo["non_manifold_edges"] or topo["loose_vertices"]:
        raise RuntimeError(f"A102 produced invalid topology on {name}: {topo}")
if ring9_max_displacement > 0.003:
    raise RuntimeError(f"A102 ring 9 seam displacement is too large: {ring9_max_displacement}")
if not 0.77 <= combined_x_span <= 0.80:
    raise RuntimeError(f"A102 combined tail X span outside target: {combined_x_span}")
if not 0.10 <= tail_bounds["min"][2] <= 0.14:
    raise RuntimeError(f"A102 tail ground clearance outside target: {tail_bounds['min'][2]}")
if not 0.67 <= tail_bounds["dimensions"][0] <= 0.70:
    raise RuntimeError("A102 TailBase X dimension outside target")
if not 0.62 <= tail_bounds["dimensions"][1] <= 0.66:
    raise RuntimeError("A102 TailBase Y dimension outside target")
if not 0.72 <= tail_bounds["dimensions"][2] <= 0.75:
    raise RuntimeError("A102 TailBase Z dimension outside target")
if not 0.14 <= tip_bounds["dimensions"][0] <= 0.16:
    raise RuntimeError("A102 TailTip X dimension outside target")
if not 0.10 <= tip_bounds["dimensions"][1] <= 0.12:
    raise RuntimeError("A102 TailTip Y dimension outside target")
if not 0.11 <= tip_bounds["dimensions"][2] <= 0.12:
    raise RuntimeError("A102 TailTip Z dimension outside target")
if robe_tail_overlap[0] < 0.31 or robe_tail_overlap[1] < 0.44 or robe_tail_overlap[2] < 0.26:
    raise RuntimeError(f"A102 lost robe/tail concealment: {robe_tail_overlap}")
if tail_tip_overlap[0] < 0.05 or tail_tip_overlap[1] < 0.09 or tail_tip_overlap[2] < 0.10:
    raise RuntimeError(f"A102 cream tip is insufficiently integrated: {tail_tip_overlap}")
if tail_foot_overlap[2] > 0.16:
    raise RuntimeError(f"A102 tail remains too crowded against the right foot: {tail_foot_overlap}")
if any(
    tail_leg_overlap[axis] > (0.026, 0.121, 0.491)[axis]
    for axis in range(3)
):
    raise RuntimeError(f"A102 increased the locked tail/right-leg overlap: {tail_leg_overlap}")
if not 0.44 <= tail_protrusion <= 0.49:
    raise RuntimeError(f"A102 tail protrusion outside target: {tail_protrusion}")
if distal_to_bulge_y > 0.45 or distal_to_bulge_z > 0.45:
    raise RuntimeError("A102 distal plume does not taper strongly enough")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailSilhouetteCompaction_A102"
scene["comforting_cat_v6_stage"] = "TAIL_SILHOUETTE_COMPACTION"
scene["comforting_cat_v6_attempt"] = 102
scene["comforting_cat_v6_dominant_defect"] = "oversized_ground_hugging_sausage_tail"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "TAIL_SILHOUETTE_COMPACTION",
    "attempt": 102,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "oversized_ground_hugging_sausage_tail",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": [tail.name, tip.name],
        "preserved": [
            "authoritative A98 scene outside V6_TailBase and V6_TailTip",
            "V6_Robe and its accepted tail port",
            "TailBase rings 0-8, indices 0-143",
            "TailBase start cap index 496",
            "A97 ears and accepted head/face",
            "A98 compact body, arms, legs and feet",
            "scarf, tunic, satchel, strap and tassels",
            "camera, lights and materials",
        ],
    },
    "visual_abort_gates": [
        "front/3q tail must retain a large furry counterweight silhouette",
        "back/rear-3q must not reveal a new orange wedge above the robe hem",
        "side must not read as a vertical stump or float above Z 0.14",
        "cream tip must read as an integrated taper rather than a separate bead",
        "no visible kink may appear between locked ring 8 and mutable ring 9",
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
