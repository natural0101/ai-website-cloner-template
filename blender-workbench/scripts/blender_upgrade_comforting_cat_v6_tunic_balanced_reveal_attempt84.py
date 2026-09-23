"""Reveal the A82 tunic neighbor columns against exact local robe-surface targets."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tunic_balanced_reveal_attempt84"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tunic_deep_occlusion_attempt82.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tunic_balanced_reveal_attempt84.blend"
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
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


root = bpy.data.objects["CatV6_Root"]
tunic = bpy.data.objects["V6_FrontTunic"]
columns = 7
rows = 9
front_count = columns * rows
if len(tunic.data.vertices) != front_count * 2:
    raise RuntimeError(f"A84 expected A82 126-vertex tunic; got {len(tunic.data.vertices)}")

locked_objects = [obj for obj in descendants(root) if obj.name != tunic.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tunic)
topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
preserved_sources = [
    preserve_copy(tunic, "Comforting_Cat_V6", "A84", "over_occluded_inner_cloth")
]

neighbor_targets = {
    1: (-0.3238, -0.3224),
    2: (-0.3476, -0.3462),
    3: (-0.3557, -0.3543),
    4: (-0.3643, -0.3633),
    5: (-0.3676, -0.3706),
    6: (-0.3634, -0.3705),
    7: (-0.3537, -0.3659),
    8: (-0.3443, -0.3626),
}
upper_center_targets = {2: -0.3447, 3: -0.3517, 4: -0.3444}
inverse = tunic.matrix_world.inverted()
front_world = [
    tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)
]

for row, (left_y, right_y) in neighbor_targets.items():
    front_world[row * columns + 1].y = left_y
    front_world[row * columns + 5].y = right_y
for column, target_y in upper_center_targets.items():
    front_world[columns + column].y = target_y

thickness = 0.022
for index, point in enumerate(front_world):
    tunic.data.vertices[index].co = inverse @ point
    tunic.data.vertices[front_count + index].co = inverse @ Vector(
        (point.x, point.y + thickness, point.z)
    )
tunic.data.update()

bpy.context.view_layer.update()
after = bounds(tunic)
topology_after = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A84 changed locked A82/A79 geometry outside V6_FrontTunic")
if topology_before != topology_after:
    raise RuntimeError("A84 changed closed-cloth topology")

front_after = [tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)]
actual_neighbors = {
    row: (
        front_after[row * columns + 1].y,
        front_after[row * columns + 5].y,
    )
    for row in neighbor_targets
}
actual_upper_center = {
    column: front_after[columns + column].y for column in upper_center_targets
}
outer_y = [
    front_after[row * columns].y for row in range(rows)
] + [
    front_after[row * columns + 6].y for row in range(rows)
]
for row, targets in neighbor_targets.items():
    if any(abs(actual - target) > 1e-5 for actual, target in zip(actual_neighbors[row], targets)):
        raise RuntimeError(f"A84 row {row} missed exact ray-cast target")
if not all(abs(value + 0.2) <= 1e-5 for value in outer_y):
    raise RuntimeError("A84 exposed an A82 outer boundary column")

expected_visible_spans = {
    "row2": 0.440,
    "row3": 0.453,
    "row4": 0.460,
    "row5": 0.440,
    "row6": 0.400,
}
metrics = {
    "before": before,
    "after": after,
    "neighbor_targets_y": neighbor_targets,
    "actual_neighbor_y": actual_neighbors,
    "upper_center_targets_y": upper_center_targets,
    "actual_upper_center_y": actual_upper_center,
    "outer_columns_y": outer_y,
    "expected_visible_spans": expected_visible_spans,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A84_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TunicBalancedReveal_A84"
scene["comforting_cat_v6_stage"] = "TUNIC_BALANCED_REVEAL"
scene["comforting_cat_v6_attempt"] = 84
scene["comforting_cat_v6_dominant_defect"] = "inner_cloth_mass_lost_after_deep_occlusion"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TUNIC_BALANCED_REVEAL",
    "attempt": 84,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "inner_cloth_mass_lost_after_deep_occlusion",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_FrontTunic cols1/5 Y and row1 center transition only"],
        "preserved": [
            "A82 outer hidden columns, X/Z outline, topology, material",
            "A79 head/face/muzzle",
            "robe/scarf/satchel/arms",
            "legs",
            "tail",
            "camera",
            "lights",
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
