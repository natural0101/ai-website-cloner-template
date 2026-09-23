"""Push only the A81 tunic perimeter behind the robe to remove the apron outline."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tunic_deep_occlusion_attempt82"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_tunic_deep_occlusion_attempt82.blend"
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
robe = bpy.data.objects["V6_Robe"]
columns = 7
rows = 9
front_count = columns * rows
if len(tunic.data.vertices) != front_count * 2:
    raise RuntimeError(f"A82 expected A81 126-vertex tunic; got {len(tunic.data.vertices)}")

locked_objects = [obj for obj in descendants(root) if obj.name != tunic.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tunic)
robe_bounds = bounds(robe)
topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
preserved_sources = [
    preserve_copy(tunic, "Comforting_Cat_V6", "A82", "insufficient_edge_occlusion")
]

inverse = tunic.matrix_world.inverted()
front_world = [
    tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)
]
for row in range(rows):
    for column in range(columns):
        index = row * columns + column
        point = front_world[index]
        if row == 0:
            point.y = -0.200
        elif row == 1:
            point.y = [-0.200, -0.270, -0.330, -0.345, -0.330, -0.270, -0.200][column]
        elif column in (0, columns - 1):
            point.y = -0.200
        elif column in (1, columns - 2):
            point.y = -0.300
        if row == rows - 1:
            point.y = [-0.200, -0.280, -0.365, point.y, -0.350, -0.270, -0.200][column]
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
    raise RuntimeError("A82 changed locked A81/A79 geometry outside V6_FrontTunic")
if topology_before != topology_after:
    raise RuntimeError("A82 changed closed-cloth topology")

front_after = [tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)]
top_y = [front_after[column].y for column in range(columns)]
outer_y = []
for row in range(rows):
    outer_y.extend(
        [front_after[row * columns].y, front_after[row * columns + columns - 1].y]
    )
robe_front_bound = robe_bounds["min"][1]
if not all(value >= robe_front_bound + 0.15 for value in top_y):
    raise RuntimeError("A82 top row is not deeply behind the robe/scarf envelope")
if not all(value >= robe_front_bound + 0.15 for value in outer_y):
    raise RuntimeError("A82 outer edge is not deeply behind the robe envelope")

metrics = {
    "before": before,
    "after": after,
    "robe_front_bound_y": robe_front_bound,
    "top_row_y": top_y,
    "outer_edge_y": outer_y,
    "occlusion_margin_over_robe_front": round(min(outer_y) - robe_front_bound, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A82_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TunicDeepOcclusion_A82"
scene["comforting_cat_v6_stage"] = "TUNIC_DEEP_OCCLUSION"
scene["comforting_cat_v6_attempt"] = 82
scene["comforting_cat_v6_dominant_defect"] = "visible_tunic_perimeter_despite_shallow_occlusion"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TUNIC_DEEP_OCCLUSION",
    "attempt": 82,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "visible_tunic_perimeter_despite_shallow_occlusion",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_FrontTunic perimeter Y only"],
        "preserved": [
            "A81/A80 tunic topology, X/Z outline, interior bulge, material",
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
