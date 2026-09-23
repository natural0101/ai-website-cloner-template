"""Remediate rejected A99 lids by collapsing their deep head wedges into thin shells."""

from __future__ import annotations

import bmesh
import hashlib
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_upper_lid_thin_shell_attempt100"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_upper_lid_worry_integration_attempt99.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_upper_lid_thin_shell_attempt100.blend"
).resolve()
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
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
            for polygon in obj.data.polygons:
                digest.update((",".join(str(i) for i in polygon.vertices) + ";").encode("ascii"))
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


def x_lower_z_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for station in range(13):
        for offset in range(4):
            index = station * 4 + offset
            point = obj.matrix_world @ obj.data.vertices[index].co
            lower_z = obj.matrix_world @ obj.data.vertices[station * 4].co
            digest.update(f"{index}:{point.x:.9f},{lower_z.z:.9f};".encode("ascii"))
    return digest.hexdigest()


root = bpy.data.objects["CatV6_Root"]
lids = [bpy.data.objects["V6_UpperLid_L"], bpy.data.objects["V6_UpperLid_R"]]
lid_names = {obj.name for obj in lids}
locked_objects = [obj for obj in bpy.data.objects if obj.name not in lid_names]
locked_hash_before = object_state_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in lids}
topology_before = {obj.name: topology(obj) for obj in lids}
x_lower_before = {obj.name: x_lower_z_hash(obj) for obj in lids}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A100", "rejected_a99_deep_lid_wedge")
    for obj in lids
]

profiles: dict[str, list[dict[str, float]]] = {}
for lid in lids:
    inverse = lid.matrix_world.inverted()
    stations: list[dict[str, float]] = []
    for station in range(13):
        t = station / 12.0
        base = station * 4
        lower_front = lid.matrix_world @ lid.data.vertices[base].co
        upper_front = lid.matrix_world @ lid.data.vertices[base + 1].co
        lower_back = lid.matrix_world @ lid.data.vertices[base + 2].co
        upper_back = lid.matrix_world @ lid.data.vertices[base + 3].co
        height = 0.003 + math.sin(math.pi * t) * 0.021
        upper_z = lower_front.z + height
        lower_front.y = -0.5090
        upper_front.y = -0.5070
        lower_back.y = -0.5060
        upper_back.y = -0.5040
        upper_front.z = upper_z
        upper_back.z = upper_z
        lid.data.vertices[base].co = inverse @ lower_front
        lid.data.vertices[base + 1].co = inverse @ upper_front
        lid.data.vertices[base + 2].co = inverse @ lower_back
        lid.data.vertices[base + 3].co = inverse @ upper_back
        stations.append(
            {
                "t": round(t, 6),
                "x": round(float(lower_front.x), 6),
                "lower_z": round(float(lower_front.z), 6),
                "upper_z": round(float(upper_z), 6),
                "cap_height": round(float(height), 6),
            }
        )
    lid.data.update()
    profiles[lid.name] = stations

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in lids}
topology_after = {obj.name: topology(obj) for obj in lids}
x_lower_after = {obj.name: x_lower_z_hash(obj) for obj in lids}
locked_hash_after = object_state_hash(locked_objects)

if locked_hash_before != locked_hash_after:
    raise RuntimeError("A100 changed A98 state outside the two A99 lid objects")
if topology_before != topology_after:
    raise RuntimeError("A100 changed A99 lid topology")
if x_lower_before != x_lower_after:
    raise RuntimeError("A100 changed the accepted A99 X span or lower worry edge")
for obj in lids:
    topo = topology_after[obj.name]
    if topo != {
        "vertices": 52,
        "edges": 100,
        "faces": 50,
        "boundary_edges": 0,
        "non_manifold_edges": 0,
        "loose_vertices": 0,
    }:
        raise RuntimeError(f"A100 invalid topology on {obj.name}: {topo}")
    dims = after[obj.name]["dimensions"]
    if not 0.0045 <= dims[1] <= 0.0055:
        raise RuntimeError(f"A100 {obj.name} remains too deep: {dims[1]}")
    if not 0.047 <= dims[2] <= 0.050:
        raise RuntimeError(f"A100 {obj.name} cap height outside target: {dims[2]}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "profiles": profiles,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "x_lower_hash_before": x_lower_before,
    "x_lower_hash_after": x_lower_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
    "remediation": "A99 shell Y depth collapsed from about 0.179 BU to 0.005 BU; center height 0.030 to 0.024 BU",
}
print("A100_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_UpperLidThinShell_A100"
scene["comforting_cat_v6_stage"] = "UPPER_LID_THIN_SHELL_REMEDIATION"
scene["comforting_cat_v6_attempt"] = 100
scene["comforting_cat_v6_dominant_defect"] = "a99_lid_shelves_and_side_spikes"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "UPPER_LID_THIN_SHELL_REMEDIATION",
    "attempt": 100,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a99_lid_shelves_and_side_spikes",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_UpperLid_L/R Y depth and upper-edge height only"],
        "preserved": [
            "A99 lower worry edge and X span",
            "all pre-A99 A98 objects exactly",
            "eyes, pupils and highlights",
            "brows, muzzle and ears",
            "A98 compact body, costume, limbs and tail",
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
