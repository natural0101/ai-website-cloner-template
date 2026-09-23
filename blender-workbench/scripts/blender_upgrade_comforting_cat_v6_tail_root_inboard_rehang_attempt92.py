"""Hide the A91 tail-root notch by moving only the robe-covered root band inboard in X."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_tail_root_inboard_rehang_attempt92"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_root_inboard_rehang_attempt92.blend"
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


def selected_hash(obj: bpy.types.Object, predicate) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if predicate(world):
            digest.update(
                f"{vertex.index}:{world.x:.9f},{world.y:.9f},{world.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def smoothstep(value: float) -> float:
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
locked_objects = [obj for obj in descendants(root) if obj.name != tail.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tail)
topology_before = (
    len(tail.data.vertices),
    len(tail.data.edges),
    len(tail.data.polygons),
)
preserved_source = preserve_copy(
    tail,
    "Comforting_Cat_V6",
    "A92",
    "a91_sharp_tail_root_notch_through_lowered_robe_hem",
)
low_hash_before = selected_hash(tail, lambda point: point.z <= 0.35)
distal_hash_before = selected_hash(tail, lambda point: point.x >= 0.76)

inverse = tail.matrix_world.inverted()
changed_indices: list[int] = []
max_shift = 0.0
root_x_before: list[float] = []
root_x_after: list[float] = []
root_band_indices: set[int] = set()
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    if 0.42 <= world.z <= 0.66 and world.x <= 0.68:
        root_x_before.append(float(world.x))
        root_band_indices.add(vertex.index)
    z_rise = smoothstep((world.z - 0.36) / 0.14)
    z_fall = 1.0 - smoothstep((world.z - 0.62) / 0.12)
    x_gate = 1.0 - smoothstep((world.x - 0.68) / 0.08)
    weight = z_rise * z_fall * x_gate
    if weight > 1e-6:
        shift = 0.120 * weight
        world.x -= shift
        vertex.co = inverse @ world
        changed_indices.append(vertex.index)
        max_shift = max(max_shift, shift)
tail.data.update()
bpy.context.view_layer.update()

after = bounds(tail)
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    if vertex.index in root_band_indices:
        root_x_after.append(float(world.x))
topology_after = (
    len(tail.data.vertices),
    len(tail.data.edges),
    len(tail.data.polygons),
)
locked_hash_after = geometry_hash(locked_objects)
low_hash_after = selected_hash(tail, lambda point: point.z <= 0.35)
distal_hash_after = selected_hash(tail, lambda point: point.x >= 0.76)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A92 changed A91 garment, face, ears, legs or feet")
if topology_before != topology_after:
    raise RuntimeError("A92 changed tail topology")
if low_hash_before != low_hash_after:
    raise RuntimeError("A92 changed the accepted low plume")
if distal_hash_before != distal_hash_after:
    raise RuntimeError("A92 changed the distal tail silhouette")

metrics = {
    "before": before,
    "after": after,
    "changed_vertices": len(changed_indices),
    "max_inboard_shift_x": round(max_shift, 5),
    "root_band_max_x_before": round(max(root_x_before), 5),
    "changed_root_band_max_x_after": round(max(root_x_after), 5),
    "tail_min_z_delta": round(after["min"][2] - before["min"][2], 6),
    "tail_max_x_delta": round(after["max"][0] - before["max"][0], 6),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "low_hash_before": low_hash_before,
    "low_hash_after": low_hash_after,
    "distal_hash_before": distal_hash_before,
    "distal_hash_after": distal_hash_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A92_PRE_GATE_METRICS=" + repr(metrics))
if not 0.110 <= max_shift <= 0.121:
    raise RuntimeError("A92 root shift outside target")
if metrics["changed_root_band_max_x_after"] > 0.60:
    raise RuntimeError("A92 tail root remains outside the robe-side concealment zone")
if abs(metrics["tail_min_z_delta"]) > 0.000001:
    raise RuntimeError("A92 changed ground contact")
if abs(metrics["tail_max_x_delta"]) > 0.000001:
    raise RuntimeError("A92 changed distal X span")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailRootInboardRehang_A92"
scene["comforting_cat_v6_stage"] = "TAIL_ROOT_INBOARD_REHANG"
scene["comforting_cat_v6_attempt"] = 92
scene["comforting_cat_v6_dominant_defect"] = "a91_back_orange_tail_root_notch"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_ROOT_INBOARD_REHANG",
    "attempt": 92,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a91_back_orange_tail_root_notch",
    "preserved_source": preserved_source,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_TailBase covered root-band X only"],
        "preserved": [
            "A91 lower garment rehang",
            "A90/A89 face and head",
            "ears/scarf/satchel/arms",
            "legs/feet",
            "tail z<=0.35 low plume",
            "tail x>=0.76 distal plume",
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
