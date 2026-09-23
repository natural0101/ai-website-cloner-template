"""Compact the A97 mid-torso and arm span without reopening the locked tail port."""

from __future__ import annotations

import bmesh
import hashlib
import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_compact_kitten_body_attempt98"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_soft_backswept_ear_cup_attempt97.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (CHECKPOINT_DIR / "comforting_cat_v6_before_compact_kitten_body_attempt98.blend").resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


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
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
            for polygon in obj.data.polygons:
                digest.update(
                    (f"{polygon.material_index}:" + ",".join(str(i) for i in polygon.vertices) + ";").encode("ascii")
                )
    return digest.hexdigest()


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


def yz_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        digest.update(f"{point.y:.9f},{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def indices_hash(obj: bpy.types.Object, indices: list[int]) -> str:
    digest = hashlib.sha256()
    for index in indices:
        point = obj.matrix_world @ obj.data.vertices[index].co
        digest.update(f"{index}:{point.x:.9f},{point.y:.9f},{point.z:.9f};".encode("ascii"))
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


def reshape_ring(
    obj: bpy.types.Object,
    indices: range,
    target_min_x: float,
    target_max_x: float,
) -> dict[str, float]:
    inverse = obj.matrix_world.inverted()
    points = [obj.matrix_world @ obj.data.vertices[index].co for index in indices]
    current_min = min(point.x for point in points)
    current_max = max(point.x for point in points)
    if current_max - current_min <= 1e-8:
        raise RuntimeError(f"Degenerate X ring on {obj.name}")
    for index, point in zip(indices, points):
        u = (point.x - current_min) / (current_max - current_min)
        point.x = target_min_x + u * (target_max_x - target_min_x)
        obj.data.vertices[index].co = inverse @ point
    return {
        "before_min": round(float(current_min), 6),
        "before_max": round(float(current_max), 6),
        "target_min": target_min_x,
        "target_max": target_max_x,
    }


def reshape_full_x(obj: bpy.types.Object, target_min_x: float, target_max_x: float) -> dict[str, float]:
    inverse = obj.matrix_world.inverted()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    current_min = min(point.x for point in points)
    current_max = max(point.x for point in points)
    for vertex, point in zip(obj.data.vertices, points):
        u = (point.x - current_min) / (current_max - current_min)
        point.x = target_min_x + u * (target_max_x - target_min_x)
        vertex.co = inverse @ point
    return {
        "before_min": round(float(current_min), 6),
        "before_max": round(float(current_max), 6),
        "target_min": target_min_x,
        "target_max": target_max_x,
    }


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(0.0, min(a["max"][axis], b["max"][axis]) - max(a["min"][axis], b["min"][axis]))


def x_band(obj: bpy.types.Object, center_z: float, tolerance: float) -> dict[str, float]:
    points = [
        obj.matrix_world @ vertex.co
        for vertex in obj.data.vertices
        if abs((obj.matrix_world @ vertex.co).z - center_z) <= tolerance
    ]
    if not points:
        raise RuntimeError(f"No band vertices for {obj.name} at Z={center_z}")
    return {"min": min(point.x for point in points), "max": max(point.x for point in points)}


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
left_arm = bpy.data.objects["V6_ArmUnified_L"]
right_arm = bpy.data.objects["V6_ArmUnified_R"]
head = bpy.data.objects["V6_Head"]
tail = bpy.data.objects["V6_TailBase"]
tunic = bpy.data.objects["V6_FrontTunic"]
satchel = bpy.data.objects["V6_Satchel"]
left_leg = bpy.data.objects["V6_Leg_L"]
right_leg = bpy.data.objects["V6_Leg_R"]

targets = [robe, left_arm, right_arm]
target_names = {obj.name for obj in targets}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in target_names]
locked_hash_before = object_state_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in targets + [head, tail, tunic, satchel]}
topology_before = {obj.name: topology(obj) for obj in targets}
material_topology_before = {obj.name: material_topology_hash(obj) for obj in targets}
yz_before = {obj.name: yz_hash(obj) for obj in targets}
locked_tail_port_before = indices_hash(robe, list(range(128)))

expected_baseline = {
    "robe_yz": "4fe8fb895d8adfd0512063e927410fce16e00f232c13be5676a238ebf0e418f7",
    "left_arm_yz": "1411c6f7cbac1dd85de73ed44374bbcb2924dbf57fc9d1eabec329e1c0912e8a",
    "right_arm_yz": "d81808d88e47546257536e51a273af7817f27f4b85b2ff497c83d54e955e98e0",
}

preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A98", "authoritative_a97_compact_body_source")
    for obj in targets
]

deformation = {
    "robe_z0_98": reshape_ring(robe, range(128, 192), -0.630, 0.610),
    "robe_z1_23": reshape_ring(robe, range(192, 256), -0.590, 0.570),
    "robe_z1_63": reshape_ring(robe, range(256, 320), -0.600, 0.580),
    "robe_z2_01": reshape_ring(robe, range(320, 384), -0.620, 0.600),
    "left_arm": reshape_full_x(left_arm, -0.750, -0.450),
    "right_arm": reshape_full_x(right_arm, 0.450, 0.750),
}
robe.data.update()
left_arm.data.update()
right_arm.data.update()
bpy.context.view_layer.update()

after = {obj.name: bounds(obj) for obj in targets + [head, tail, tunic, satchel]}
topology_after = {obj.name: topology(obj) for obj in targets}
material_topology_after = {obj.name: material_topology_hash(obj) for obj in targets}
yz_after = {obj.name: yz_hash(obj) for obj in targets}
locked_tail_port_after = indices_hash(robe, list(range(128)))
locked_hash_after = object_state_hash(locked_objects)

if locked_hash_before != locked_hash_after:
    raise RuntimeError("A98 changed A97 scene state outside robe and two arm meshes")
if topology_before != topology_after:
    raise RuntimeError("A98 changed target topology")
if material_topology_before != material_topology_after:
    raise RuntimeError("A98 changed target material indices, faces, edges or modifiers")
if yz_before != yz_after:
    raise RuntimeError("A98 changed Y or Z on an X-only target")
if locked_tail_port_before != locked_tail_port_after:
    raise RuntimeError("A98 changed the locked hem/tail-port rings 0-127")
for name, topo in topology_after.items():
    if topo["boundary_edges"] or topo["non_manifold_edges"] or topo["loose_vertices"]:
        raise RuntimeError(f"A98 invalid topology on {name}: {topo}")

robe_after = after[robe.name]
head_width = after[head.name]["dimensions"][0]
arm_span = after[right_arm.name]["max"][0] - after[left_arm.name]["min"][0]
mid_widths = {
    "z0_98": x_band(robe, 0.980, 0.002),
    "z1_23": x_band(robe, 1.230, 0.002),
    "z1_63": x_band(robe, 1.630, 0.002),
    "z2_01": x_band(robe, 2.010, 0.002),
}
mid_width_values = {
    key: round(value["max"] - value["min"], 6) for key, value in mid_widths.items()
}
contacts = {
    "robe_tail": [round(overlap_1d(robe_after, after[tail.name], axis), 6) for axis in range(3)],
    "robe_left_leg": [round(overlap_1d(robe_after, bounds(left_leg), axis), 6) for axis in range(3)],
    "robe_right_leg": [round(overlap_1d(robe_after, bounds(right_leg), axis), 6) for axis in range(3)],
}
ratios = {
    "global_robe_over_head": round(robe_after["dimensions"][0] / head_width, 6),
    "arm_span_over_head": round(arm_span / head_width, 6),
    "tunic_over_narrowest_mid": round(
        after[tunic.name]["dimensions"][0] / min(mid_width_values.values()), 6
    ),
    "satchel_over_narrowest_mid": round(
        after[satchel.name]["dimensions"][0] / min(mid_width_values.values()), 6
    ),
}

if not 1.15 <= mid_width_values["z1_23"] <= 1.17:
    raise RuntimeError("A98 lower-mid robe width outside target")
if not 1.17 <= mid_width_values["z1_63"] <= 1.19:
    raise RuntimeError("A98 waist robe width outside target")
if not 1.21 <= mid_width_values["z2_01"] <= 1.23:
    raise RuntimeError("A98 upper robe width outside target")
if not 1.49 <= arm_span <= 1.51:
    raise RuntimeError("A98 arm span outside compact-body target")
if ratios["arm_span_over_head"] > 1.13:
    raise RuntimeError("A98 arms remain too broad relative to head")
if contacts["robe_tail"][0] < 0.23 or contacts["robe_tail"][1] < 0.44 or contacts["robe_tail"][2] < 0.26:
    raise RuntimeError(f"A98 lost robe/tail overlap: {contacts['robe_tail']}")
if ratios["tunic_over_narrowest_mid"] > 0.60:
    raise RuntimeError("A98 tunic became too wide for compact torso")
if ratios["satchel_over_narrowest_mid"] > 0.48:
    raise RuntimeError("A98 satchel became too wide for compact torso")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "deformation": deformation,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "mid_widths": mid_widths,
    "mid_width_values": mid_width_values,
    "contacts": contacts,
    "ratios": ratios,
    "arm_span": round(arm_span, 6),
    "yz_hash_before": yz_before,
    "yz_hash_after": yz_after,
    "external_local_yz_hash_reference": expected_baseline,
    "locked_tail_port_hash_before": locked_tail_port_before,
    "locked_tail_port_hash_after": locked_tail_port_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A98_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_CompactKittenBody_A98"
scene["comforting_cat_v6_stage"] = "COMPACT_KITTEN_BODY"
scene["comforting_cat_v6_attempt"] = 98
scene["comforting_cat_v6_dominant_defect"] = "barrel_robe_and_humanoid_arm_span"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "COMPACT_KITTEN_BODY",
    "attempt": 98,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "barrel_robe_and_humanoid_arm_span",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": [robe.name, left_arm.name, right_arm.name],
        "preserved": [
            "A97 head/face/brows/ears",
            "scarf and front tunic",
            "satchel, strap and tassels",
            "legs, feet and tail",
            "robe hem and tail-port rings 0-127",
            "all Y/Z coordinates",
            "camera, lights and materials",
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
