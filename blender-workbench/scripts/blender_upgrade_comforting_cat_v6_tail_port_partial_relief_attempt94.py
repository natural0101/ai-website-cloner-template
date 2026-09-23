"""Keep only a restrained fraction of A93 tail-port hem relief to avoid a back hem slope."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_tail_port_partial_relief_attempt94"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_port_hem_relief_attempt93.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_port_partial_relief_attempt94.blend"
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


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
a91_robe = bpy.data.objects["V6_Robe_SOURCE_A93"]
tail = bpy.data.objects["V6_TailBase"]
foot_l = bpy.data.objects["V6_Foot_L"]
foot_r = bpy.data.objects["V6_Foot_R"]
locked_objects = [obj for obj in descendants(root) if obj.name != robe.name]
locked_hash_before = geometry_hash(locked_objects)
before = {"robe": bounds(robe), "tail": bounds(tail)}
topology_before = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
preserved_source = preserve_copy(
    robe,
    "Comforting_Cat_V6",
    "A94",
    "a93_tail_port_relief_created_excessive_back_hem_slope",
)
if len(a91_robe.data.vertices) != len(robe.data.vertices):
    raise RuntimeError("A94 A91 source topology mismatch")

inverse = robe.matrix_world.inverted()
keep_fraction = 0.38
changed_vertices = 0
max_relief_after = 0.0
for vertex in robe.data.vertices:
    current = robe.matrix_world @ vertex.co
    a91 = a91_robe.matrix_world @ a91_robe.data.vertices[vertex.index].co
    relief = current.z - a91.z
    if relief <= 1e-7:
        continue
    current.z = a91.z + relief * keep_fraction
    vertex.co = inverse @ current
    changed_vertices += 1
    max_relief_after = max(max_relief_after, relief * keep_fraction)
robe.data.update()
bpy.context.view_layer.update()

after = {"robe": bounds(robe), "tail": bounds(tail)}
topology_after = (
    len(robe.data.vertices),
    len(robe.data.edges),
    len(robe.data.polygons),
)
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A94 changed geometry outside V6_Robe")
if topology_before != topology_after:
    raise RuntimeError("A94 changed robe topology")

foot_top = max(bounds(foot_l)["max"][2], bounds(foot_r)["max"][2])
exposed_shin_gap = after["robe"]["min"][2] - foot_top
metrics = {
    "before": before,
    "after": after,
    "keep_fraction_of_a93_relief": keep_fraction,
    "changed_vertices": changed_vertices,
    "max_tail_port_relief_z": round(max_relief_after, 5),
    "exposed_shin_gap": round(exposed_shin_gap, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A94_PRE_GATE_METRICS=" + repr(metrics))
if not 0.035 <= max_relief_after <= 0.045:
    raise RuntimeError("A94 retained tail-port relief outside target")
if not 0.19 <= exposed_shin_gap <= 0.22:
    raise RuntimeError("A94 lost compact front leg proportion")
if before["tail"] != after["tail"]:
    raise RuntimeError("A94 changed tail bounds")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailPortPartialRelief_A94"
scene["comforting_cat_v6_stage"] = "TAIL_PORT_PARTIAL_RELIEF"
scene["comforting_cat_v6_attempt"] = 94
scene["comforting_cat_v6_dominant_defect"] = "a93_excessive_tail_port_hem_slope"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_PORT_PARTIAL_RELIEF",
    "attempt": 94,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a93_excessive_tail_port_hem_slope",
    "preserved_source": preserved_source,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["A93 tail-port robe relief reduced to 38%"],
        "preserved": [
            "A91 compact front/side hem and tunic",
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
