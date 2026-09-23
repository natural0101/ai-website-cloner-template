"""Pull only the hidden upper tail root inward so it no longer cuts through the robe back."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tail_root_robe_conceal_attempt63"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_robe_hem_two_ring_blend_attempt62.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_root_robe_conceal_attempt63.blend"
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


def selected_world_hash(obj: bpy.types.Object, maximum_z: float) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if world.z <= maximum_z:
            digest.update(
                f"{vertex.index}:{world.x:.9f},{world.y:.9f},{world.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
robe = bpy.data.objects["V6_Robe"]
non_tail_objects = [obj for obj in descendants(root) if obj.name != tail.name]
non_tail_hash_before = geometry_hash(non_tail_objects)
low_visible_hash_before = selected_world_hash(tail, 0.55)
before = {"tail": bounds(tail), "robe": bounds(robe)}
preserved_source = preserve_copy(
    tail,
    "Comforting_Cat_V6",
    "A63",
    "upper_tail_root_visible_through_robe_back",
)

root_vertices_before = [
    tail.matrix_world @ vertex.co
    for vertex in tail.data.vertices
    if (tail.matrix_world @ vertex.co).z >= 0.65
]
if not root_vertices_before:
    raise RuntimeError("No upper tail-root vertices found")
root_max_y_before = max(vertex.y for vertex in root_vertices_before)
inverse = tail.matrix_world.inverted()
changed_vertices = 0
max_shift = 0.0
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    if world.z <= 0.55:
        continue
    weight = smoothstep(0.55, 0.72, world.z)
    shift = 0.140 * weight
    world.y -= shift
    vertex.co = inverse @ world
    changed_vertices += 1
    max_shift = max(max_shift, shift)
tail.data.update()

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "robe": bounds(robe)}
non_tail_hash_after = geometry_hash(non_tail_objects)
low_visible_hash_after = selected_world_hash(tail, 0.55)
if non_tail_hash_before != non_tail_hash_after:
    raise RuntimeError("Tail-root pass changed locked body or costume geometry")
if low_visible_hash_before != low_visible_hash_after:
    raise RuntimeError("Tail-root pass changed the accepted low plume")

root_vertices_after = [
    tail.matrix_world @ vertex.co
    for vertex in tail.data.vertices
    if (tail.matrix_world @ vertex.co).z >= 0.65
]
root_max_y_after = max(vertex.y for vertex in root_vertices_after)
metrics = {
    "changed_vertices": changed_vertices,
    "max_root_shift_y": round(max_shift, 5),
    "root_max_y_before": round(root_max_y_before, 5),
    "root_max_y_after": round(root_max_y_after, 5),
    "root_max_y_reduction": round(root_max_y_before - root_max_y_after, 5),
    "tail_min_z_before": before["tail"]["min"][2],
    "tail_min_z_after": after["tail"]["min"][2],
    "tail_x_span_before": before["tail"]["dimensions"][0],
    "tail_x_span_after": after["tail"]["dimensions"][0],
    "low_visible_hash_before": low_visible_hash_before,
    "low_visible_hash_after": low_visible_hash_after,
    "non_tail_hash_before": non_tail_hash_before,
    "non_tail_hash_after": non_tail_hash_after,
}
print("A63_PRE_GATE_METRICS=" + repr(metrics))
if not 0.12 <= metrics["max_root_shift_y"] <= 0.15:
    raise RuntimeError("Tail root inward shift outside target")
if metrics["root_max_y_reduction"] < 0.09:
    raise RuntimeError("Tail root remains too exposed at the robe back")
if abs(metrics["tail_min_z_after"] - metrics["tail_min_z_before"]) > 0.002:
    raise RuntimeError("Tail ground contact changed")
if abs(metrics["tail_x_span_after"] - metrics["tail_x_span_before"]) > 0.002:
    raise RuntimeError("Accepted tail silhouette width changed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailRootRobeConceal_A63"
scene["comforting_cat_v6_stage"] = "TAIL_ROOT_ROBE_CONCEAL"
scene["comforting_cat_v6_attempt"] = 63
scene["comforting_cat_v6_dominant_defect"] = "orange_tail_notch_through_robe_back"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_ROOT_ROBE_CONCEAL",
    "attempt": 63,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "orange_tail_notch_through_robe_back",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": [tail.name], "non_tail_geometry_unchanged": True},
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
