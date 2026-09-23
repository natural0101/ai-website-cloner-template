"""Seat the A81 tunic perimeter just behind locally sampled scarf/robe surfaces."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tunic_surface_seat_attempt83"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tunic_edge_occlusion_attempt81.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tunic_surface_seat_attempt83.blend"
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
    raise RuntimeError(f"A83 expected A81 126-vertex tunic; got {len(tunic.data.vertices)}")

locked_objects = [obj for obj in descendants(root) if obj.name != tunic.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tunic)
topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
preserved_sources = [
    preserve_copy(tunic, "Comforting_Cat_V6", "A83", "shallow_edge_occlusion")
]

top_targets = [-0.248, -0.282, -0.314, -0.324, -0.324, -0.313, -0.294]
edge_targets = [-0.334, -0.329, -0.324, -0.319, -0.314, -0.306, -0.298]
inverse = tunic.matrix_world.inverted()
front_world = [
    tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)
]
for row in range(rows):
    for column in range(columns):
        index = row * columns + column
        point = front_world[index]
        if row == 0:
            point.y = top_targets[column]
        elif row == 1:
            point.y = point.y + 0.62 * (top_targets[column] - point.y)
        elif column in (0, columns - 1):
            point.y = edge_targets[row - 2]
        elif column in (1, columns - 2):
            point.y = point.y + 0.55 * (edge_targets[row - 2] - point.y)
        front_world[index] = point

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
    raise RuntimeError("A83 changed locked A81/A79 geometry outside V6_FrontTunic")
if topology_before != topology_after:
    raise RuntimeError("A83 changed closed-cloth topology")

front_after = [tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)]
top_y = [front_after[column].y for column in range(columns)]
outer_y = [
    front_after[row * columns].y for row in range(2, rows)
] + [
    front_after[row * columns + columns - 1].y for row in range(2, rows)
]
center_points = [
    front_after[row * columns + column]
    for row in range(2, rows)
    for column in (2, 3, 4)
]
center_visible_x = max(point.x for point in center_points) - min(point.x for point in center_points)
if any(abs(actual - target) > 1e-5 for actual, target in zip(top_y, top_targets)):
    raise RuntimeError("A83 top row missed the ray-cast scarf targets")
if center_visible_x < 0.20:
    raise RuntimeError("A83 central untouched cloth span collapsed")

metrics = {
    "before": before,
    "after": after,
    "raycast_top_targets_y": top_targets,
    "raycast_outer_edge_targets_y": edge_targets,
    "actual_top_y": top_y,
    "actual_outer_y": outer_y,
    "neighbor_column_blend": 0.55,
    "untouched_center_grid_x_span": round(center_visible_x, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A83_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TunicSurfaceSeat_A83"
scene["comforting_cat_v6_stage"] = "TUNIC_SURFACE_SEAT"
scene["comforting_cat_v6_attempt"] = 83
scene["comforting_cat_v6_dominant_defect"] = "tunic_edges_not_seated_to_local_garment_surfaces"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TUNIC_SURFACE_SEAT",
    "attempt": 83,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "tunic_edges_not_seated_to_local_garment_surfaces",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_FrontTunic top/outer/neighbor Y only"],
        "preserved": [
            "A81/A80 tunic topology, X/Z outline, central three columns, material",
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
