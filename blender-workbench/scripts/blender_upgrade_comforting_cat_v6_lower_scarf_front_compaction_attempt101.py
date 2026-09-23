"""Compact only the front half of A98's lower scarf wrap in world X.

This pass must be launched with the authoritative A98 blend already open.
It preserves every world Y/Z coordinate, the rear half of the lower wrap, and
all scene state outside ``V6_ScarfWrap_Lower``.
"""

from __future__ import annotations

import bmesh
import hashlib
import json
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_lower_scarf_front_compaction_attempt101"
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

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_lower_scarf_front_compaction_attempt101.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge1 <= edge0:
        raise ValueError("smoothstep requires edge1 > edge0")
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


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
    """Project-standard state lock used by A98, expanded to edge topology."""
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
        if obj.type != "MESH":
            continue
        digest.update(
            ",".join(material.name if material else "" for material in obj.data.materials).encode(
                "utf-8"
            )
        )
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
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


def yz_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        digest.update(f"{vertex.index}:{point.y:.9f},{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def selected_xyz_hash(obj: bpy.types.Object, indices: list[int]) -> str:
    digest = hashlib.sha256()
    for index in indices:
        point = obj.matrix_world @ obj.data.vertices[index].co
        digest.update(
            f"{index}:{point.x:.9f},{point.y:.9f},{point.z:.9f};".encode("ascii")
        )
    return digest.hexdigest()


def band_bounds(obj: bpy.types.Object, y_upper: float) -> dict[str, list[float] | int]:
    points = [
        obj.matrix_world @ vertex.co
        for vertex in obj.data.vertices
        if (obj.matrix_world @ vertex.co).y < y_upper
    ]
    if not points:
        raise RuntimeError(f"No {obj.name} vertices with world Y < {y_upper}")
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {"count": len(points), "min": minimum, "max": maximum}


def interval_overlap(first: tuple[float, float], second: tuple[float, float]) -> float:
    return max(0.0, min(first[1], second[1]) - max(first[0], second[0]))


def assert_close_bounds(
    actual: dict[str, list[float]], expected_min: tuple[float, float, float], expected_max: tuple[float, float, float]
) -> None:
    tolerance = 5.0e-4
    for axis in range(3):
        if abs(actual["min"][axis] - expected_min[axis]) > tolerance:
            raise RuntimeError(f"Unexpected source min bound on axis {axis}: {actual['min'][axis]}")
        if abs(actual["max"][axis] - expected_max[axis]) > tolerance:
            raise RuntimeError(f"Unexpected source max bound on axis {axis}: {actual['max'][axis]}")


root = bpy.data.objects["CatV6_Root"]
lower = bpy.data.objects.get("V6_ScarfWrap_Lower")
if lower is None or lower.type != "MESH":
    raise RuntimeError("Expected mesh object V6_ScarfWrap_Lower")
if lower.data.name != "V6_ScarfWrap_Lower_Mesh":
    raise RuntimeError(f"Unexpected lower-scarf mesh datablock: {lower.data.name}")

upper = bpy.data.objects["V6_ScarfWrap_Upper"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
satchel = bpy.data.objects["V6_Satchel"]

expected_topology = {
    "vertices": 1280,
    "edges": 2560,
    "faces": 1280,
    "boundary_edges": 0,
    "non_manifold_edges": 0,
    "loose_vertices": 0,
}
topology_before = topology(lower)
if topology_before != expected_topology:
    raise RuntimeError(f"Unexpected A98 lower-scarf topology: {topology_before}")

before = {
    obj.name: bounds(obj)
    for obj in (lower, upper, drape, robe, tunic, satchel)
}
assert_close_bounds(
    before[lower.name],
    (-0.529998, -0.339498, 1.749148),
    (0.529998, 0.304998, 2.145978),
)

front_before = band_bounds(lower, -0.12)
frontmost_before = band_bounds(lower, -0.25)
front_span_before = front_before["max"][0] - front_before["min"][0]
frontmost_span_before = frontmost_before["max"][0] - frontmost_before["min"][0]
if abs(front_span_before - 1.059996) > 1.0e-4:
    raise RuntimeError(f"Unexpected A98 front span: {front_span_before}")
if abs(frontmost_span_before - 0.957070) > 1.0e-4:
    raise RuntimeError(f"Unexpected A98 frontmost span: {frontmost_span_before}")

target_names = {lower.name}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in target_names]
locked_hash_before = object_state_hash(locked_objects)
material_topology_before = material_topology_hash(lower)
yz_before = yz_hash(lower)
rear_indices = [
    vertex.index
    for vertex in lower.data.vertices
    if (lower.matrix_world @ vertex.co).y >= 0.10
]
if len(rear_indices) != 257:
    raise RuntimeError(f"Unexpected A98 rear vertex count: {len(rear_indices)}")
rear_hash_before = selected_xyz_hash(lower, rear_indices)

preserved_sources = [
    preserve_copy(lower, "Comforting_Cat_V6", "A101", "a98_wide_horizontal_lower_scarf_hose")
]

inverse = lower.matrix_world.inverted()
deformation_metrics = {
    "front_edge0_y": -0.12,
    "rear_edge1_y": 0.10,
    "maximum_front_weight": 1.0,
    "minimum_front_scale_x": 0.755,
}
for vertex in lower.data.vertices:
    world = lower.matrix_world @ vertex.co
    front = 1.0 - smoothstep(-0.12, 0.10, float(world.y))
    scale_x = 1.0 - 0.245 * front
    world.x *= scale_x
    vertex.co = inverse @ world
lower.data.update()
bpy.context.view_layer.update()

after = {
    obj.name: bounds(obj)
    for obj in (lower, upper, drape, robe, tunic, satchel)
}
front_after = band_bounds(lower, -0.12)
frontmost_after = band_bounds(lower, -0.25)
front_span_after = front_after["max"][0] - front_after["min"][0]
frontmost_span_after = frontmost_after["max"][0] - frontmost_after["min"][0]

topology_after = topology(lower)
material_topology_after = material_topology_hash(lower)
yz_after = yz_hash(lower)
rear_hash_after = selected_xyz_hash(lower, rear_indices)
locked_hash_after = object_state_hash(locked_objects)

if topology_after != topology_before or topology_after != expected_topology:
    raise RuntimeError(f"A101 changed lower-scarf topology: {topology_after}")
if material_topology_after != material_topology_before:
    raise RuntimeError("A101 changed material assignments, edges, faces or modifiers")
if yz_after != yz_before:
    raise RuntimeError("A101 changed world Y/Z on an X-only pass")
if rear_hash_after != rear_hash_before:
    raise RuntimeError("A101 changed the locked rear scarf vertices (world Y >= 0.10)")
if locked_hash_after != locked_hash_before:
    raise RuntimeError("A101 changed scene state outside V6_ScarfWrap_Lower")
if not 0.70 <= frontmost_span_after <= 0.78:
    raise RuntimeError(f"A101 frontmost span outside target: {frontmost_span_after}")
if not 0.80 <= front_span_after <= 0.86:
    raise RuntimeError(f"A101 front span outside target: {front_span_after}")

drape_bounds = after[drape.name]
lower_bounds = after[lower.name]
front_drape_x_overlap = interval_overlap(
    (front_after["min"][0], front_after["max"][0]),
    (drape_bounds["min"][0], drape_bounds["max"][0]),
)
front_drape_z_overlap = interval_overlap(
    (lower_bounds["min"][2], lower_bounds["max"][2]),
    (drape_bounds["min"][2], drape_bounds["max"][2]),
)
front_drape_y_gap = max(0.0, lower_bounds["min"][1] - drape_bounds["max"][1])
robe_overlap = [
    interval_overlap(
        (lower_bounds["min"][axis], lower_bounds["max"][axis]),
        (after[robe.name]["min"][axis], after[robe.name]["max"][axis]),
    )
    for axis in range(3)
]

if front_drape_x_overlap < 0.68:
    raise RuntimeError(f"A101 lost lower-wrap/front-drape X overlap: {front_drape_x_overlap}")
if front_drape_z_overlap < 0.13:
    raise RuntimeError(f"A101 lost lower-wrap/front-drape Z overlap: {front_drape_z_overlap}")
if not 0.020 <= front_drape_y_gap <= 0.030:
    raise RuntimeError(f"A101 changed the seated drape/lower-wrap Y gap: {front_drape_y_gap}")
if robe_overlap[0] < 0.85 or robe_overlap[1] < 0.60 or robe_overlap[2] < 0.38:
    raise RuntimeError(f"A101 lost lower-wrap/robe envelope contact: {robe_overlap}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "deformation": deformation_metrics,
    "front_span_before": round(front_span_before, 6),
    "front_span_after": round(front_span_after, 6),
    "frontmost_span_before": round(frontmost_span_before, 6),
    "frontmost_span_after": round(frontmost_span_after, 6),
    "expected_front_span": 0.800297,
    "expected_frontmost_span": 0.722588,
    "front_drape_x_overlap": round(front_drape_x_overlap, 6),
    "front_drape_z_overlap": round(front_drape_z_overlap, 6),
    "front_drape_y_gap": round(front_drape_y_gap, 6),
    "robe_overlap": [round(value, 6) for value in robe_overlap],
    "topology_before": topology_before,
    "topology_after": topology_after,
    "material_topology_hash_before": material_topology_before,
    "material_topology_hash_after": material_topology_after,
    "yz_hash_before": yz_before,
    "yz_hash_after": yz_after,
    "rear_vertex_count": len(rear_indices),
    "rear_hash_before": rear_hash_before,
    "rear_hash_after": rear_hash_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A101_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_LowerScarfFrontCompaction_A101"
scene["comforting_cat_v6_stage"] = "LOWER_SCARF_FRONT_COMPACTION"
scene["comforting_cat_v6_attempt"] = 101
scene["comforting_cat_v6_dominant_defect"] = "wide_horizontal_lower_scarf_hose"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "LOWER_SCARF_FRONT_COMPACTION",
    "attempt": 101,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "wide_horizontal_lower_scarf_hose",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": [lower.name],
        "preserved": [
            "A98 head, face, brows and ears",
            "upper scarf, front fold, front drape and back drape",
            "robe, tunic, satchel and strap",
            "arms, legs, feet and tail",
            "all world Y/Z coordinates on V6_ScarfWrap_Lower",
            "rear V6_ScarfWrap_Lower vertices with world Y >= 0.10",
            "camera, lights and materials",
        ],
    },
    "visual_gates": [
        "front lower scarf reads as a short soft fold, not a shoulder-width hose",
        "front drape remains seated over the lower wrap without a visible gap",
        "three-quarter view has no pinch, self-intersection or floating end",
        "side and back silhouettes do not regress from A98",
        "face, arms, tunic, satchel, hem and tail remain visually unchanged",
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
