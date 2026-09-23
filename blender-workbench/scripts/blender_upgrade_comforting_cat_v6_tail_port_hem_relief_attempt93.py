"""Restore A90 hem height only around the tail port while preserving the A91 compact front hem."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_tail_port_hem_relief_attempt93"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_lower_garment_rehang_attempt91.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_port_hem_relief_attempt93.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
descendants = utils["descendants"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def geometry_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted((item for item in objects if item.type == "MESH"), key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def smoothstep(value: float) -> float:
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
source_robe = bpy.data.objects["V6_Robe_SOURCE_A91"]
tail = bpy.data.objects["V6_TailBase"]
foot_l = bpy.data.objects["V6_Foot_L"]
foot_r = bpy.data.objects["V6_Foot_R"]
locked_objects = [obj for obj in descendants(root) if obj.name != robe.name]
locked_hash_before = geometry_hash(locked_objects)
before = {
    "robe": bounds(robe),
    "tail": bounds(tail),
    "foot_l": bounds(foot_l),
    "foot_r": bounds(foot_r),
}
topology_before = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
preserved_source = preserve_copy(
    robe,
    "Comforting_Cat_V6",
    "A93",
    "a91_tail_port_wedge_grew_after_global_hem_drop",
)
if len(source_robe.data.vertices) != len(robe.data.vertices):
    raise RuntimeError("A93 source robe topology mismatch")

inverse = robe.matrix_world.inverted()
changed_vertices = 0
max_restore = 0.0
weighted_records: list[dict[str, float | int]] = []
for vertex in robe.data.vertices:
    current = robe.matrix_world @ vertex.co
    if current.z > 0.74:
        continue
    source = source_robe.matrix_world @ source_robe.data.vertices[vertex.index].co
    if source.z <= current.z:
        continue
    lateral_weight = smoothstep((current.x - 0.22) / 0.30)
    back_weight = smoothstep((current.y - 0.02) / 0.34)
    weight = lateral_weight * back_weight
    if weight <= 1e-6:
        continue
    restore = (source.z - current.z) * weight
    current.z += restore
    vertex.co = inverse @ current
    changed_vertices += 1
    max_restore = max(max_restore, restore)
    weighted_records.append(
        {
            "index": vertex.index,
            "weight": round(weight, 5),
            "restore_z": round(restore, 5),
        }
    )
robe.data.update()
bpy.context.view_layer.update()

after = {
    "robe": bounds(robe),
    "tail": bounds(tail),
    "foot_l": bounds(foot_l),
    "foot_r": bounds(foot_r),
}
topology_after = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A93 changed A91 tail, tunic, face, ears, legs, feet or materials")
if topology_before != topology_after:
    raise RuntimeError("A93 changed robe topology")

foot_top = max(after["foot_l"]["max"][2], after["foot_r"]["max"][2])
exposed_shin_gap = after["robe"]["min"][2] - foot_top
metrics = {
    "before": before,
    "after": after,
    "changed_vertices": changed_vertices,
    "max_tail_port_restore_z": round(max_restore, 5),
    "exposed_shin_gap": round(exposed_shin_gap, 5),
    "weighted_records": weighted_records,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A93_PRE_GATE_METRICS=" + repr(metrics))
if not 12 <= changed_vertices <= 40:
    raise RuntimeError("A93 tail-port sector scope outside target")
if not 0.090 <= max_restore <= 0.125:
    raise RuntimeError("A93 tail-port height restore outside target")
if not 0.19 <= exposed_shin_gap <= 0.22:
    raise RuntimeError("A93 lost the accepted compact front leg proportion")
if before["tail"] != after["tail"]:
    raise RuntimeError("A93 changed tail bounds")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailPortHemRelief_A93"
scene["comforting_cat_v6_stage"] = "TAIL_PORT_HEM_RELIEF"
scene["comforting_cat_v6_attempt"] = 93
scene["comforting_cat_v6_dominant_defect"] = "a91_back_tail_root_wedge_notch"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_PORT_HEM_RELIEF",
    "attempt": 93,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a91_back_tail_root_wedge_notch",
    "preserved_source": preserved_source,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Robe lower back-right tail-port vertices Z only"],
        "preserved": [
            "A91 front/left/side compact hem",
            "A91 tunic",
            "A90/A89 face and head",
            "ears/scarf/satchel/arms",
            "tail/legs/feet",
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
