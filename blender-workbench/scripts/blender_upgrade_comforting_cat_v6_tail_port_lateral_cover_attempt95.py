"""Cover the orange tail-root wedge by widening only the existing lower robe boundary toward it."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_tail_port_lateral_cover_attempt95"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_port_partial_relief_attempt94.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_port_lateral_cover_attempt95.blend"
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
    "A95",
    "a94_tail_root_still_cut_a_sharp_orange_wedge",
)

inverse = robe.matrix_world.inverted()
changed_vertices = 0
max_shift = 0.0
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if world.z >= 0.69:
        continue
    lateral_weight = smoothstep((world.x - 0.22) / 0.28)
    back_weight = smoothstep((world.y - 0.14) / 0.26)
    lower_weight = 1.0 - smoothstep((world.z - 0.50) / 0.19)
    weight = lateral_weight * back_weight * lower_weight
    if weight <= 1e-6:
        continue
    shift = 0.078 * weight
    world.x += shift
    vertex.co = inverse @ world
    changed_vertices += 1
    max_shift = max(max_shift, shift)
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
    raise RuntimeError("A95 changed geometry outside V6_Robe")
if topology_before != topology_after:
    raise RuntimeError("A95 changed robe topology")

foot_top = max(bounds(foot_l)["max"][2], bounds(foot_r)["max"][2])
exposed_shin_gap = after["robe"]["min"][2] - foot_top
metrics = {
    "before": before,
    "after": after,
    "changed_vertices": changed_vertices,
    "max_tail_port_shift_x": round(max_shift, 5),
    "robe_width_delta": round(after["robe"]["dimensions"][0] - before["robe"]["dimensions"][0], 5),
    "exposed_shin_gap": round(exposed_shin_gap, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A95_PRE_GATE_METRICS=" + repr(metrics))
if not 8 <= changed_vertices <= 28:
    raise RuntimeError("A95 lateral-cover scope outside target")
if not 0.060 <= max_shift <= 0.080:
    raise RuntimeError("A95 tail-port cover shift outside target")
if metrics["robe_width_delta"] > 0.030:
    raise RuntimeError("A95 widened the global robe silhouette")
if not 0.19 <= exposed_shin_gap <= 0.22:
    raise RuntimeError("A95 lost compact front leg proportion")
if before["tail"] != after["tail"]:
    raise RuntimeError("A95 changed tail bounds")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailPortLateralCover_A95"
scene["comforting_cat_v6_stage"] = "TAIL_PORT_LATERAL_COVER"
scene["comforting_cat_v6_attempt"] = 95
scene["comforting_cat_v6_dominant_defect"] = "a94_orange_tail_root_wedge"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_PORT_LATERAL_COVER",
    "attempt": 95,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a94_orange_tail_root_wedge",
    "preserved_source": preserved_source,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Robe lower back-right tail-port vertices X only"],
        "preserved": [
            "A94/A91 compact front hem and tunic",
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
