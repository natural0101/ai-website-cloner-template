"""Occlude the A80 tunic edges so the curved cloth stops reading as an apron."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tunic_edge_occlusion_attempt81"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_front_tunic_curved_cloth_attempt80.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tunic_edge_occlusion_attempt81.blend"
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


def smoothstep(value: float) -> float:
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


root = bpy.data.objects["CatV6_Root"]
tunic = bpy.data.objects["V6_FrontTunic"]
columns = 7
rows = 9
front_count = columns * rows
if len(tunic.data.vertices) != front_count * 2:
    raise RuntimeError(f"A81 expected A80 126-vertex tunic; got {len(tunic.data.vertices)}")

locked_objects = [obj for obj in descendants(root) if obj.name != tunic.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tunic)
topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
)
preserved_sources = [
    preserve_copy(tunic, "Comforting_Cat_V6", "A81", "visible_apron_outline")
]

widths = [0.600, 0.620, 0.660, 0.680, 0.690, 0.660, 0.600, 0.560, 0.530]
inverse = tunic.matrix_world.inverted()
front_world: list[Vector] = [
    tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)
]

for row in range(rows):
    row_fraction = row / (rows - 1)
    lower_shift = -0.042 * smoothstep((row_fraction - 0.45) / 0.55)
    for column in range(columns):
        index = row * columns + column
        point = front_world[index]
        u = -1.0 + 2.0 * column / (columns - 1)
        if row <= 1 or row == rows - 1 or column in (0, 1, columns - 2, columns - 1):
            point.x = lower_shift + 0.5 * widths[row] * u

        if row == 0:
            point.y = -0.362 + 0.006 * abs(u)
            point.z += 0.026 * (1.0 - abs(u))
        elif row == 1:
            point.y = -0.374 - 0.010 * (1.0 - abs(u))
        elif column in (0, columns - 1):
            point.y = -0.388 - 0.004 * (1.0 - row_fraction)
        elif column in (1, columns - 2):
            point.y = 0.55 * point.y + 0.45 * (-0.395)

        if row == rows - 1:
            point.z = 0.758 + 0.018 * abs(u + 0.18) ** 1.5
            point.z += 0.118 * smoothstep((u + 0.12) / 1.12)
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
    raise RuntimeError("A81 changed locked A80/A79 geometry outside V6_FrontTunic")
if topology_before != topology_after:
    raise RuntimeError("A81 changed the accepted A80 closed-cloth topology")

front_after = [tunic.matrix_world @ tunic.data.vertices[index].co for index in range(front_count)]
top_y = [front_after[column].y for column in range(columns)]
left_edge_y = [front_after[row * columns].y for row in range(2, rows)]
right_edge_y = [front_after[row * columns + columns - 1].y for row in range(2, rows)]
hem_z = [front_after[(rows - 1) * columns + column].z for column in range(columns)]
if not all(-0.378 <= value <= -0.352 for value in top_y):
    raise RuntimeError(f"A81 top row not seated behind scarf: {top_y}")
if not all(-0.397 <= value <= -0.382 for value in left_edge_y + right_edge_y):
    raise RuntimeError("A81 side edges are not embedded into robe")
if hem_z[-1] - hem_z[0] < 0.09:
    raise RuntimeError("A81 visible hem remains too symmetric")
if not 0.52 <= after["dimensions"][0] <= 0.70:
    raise RuntimeError(f"A81 tunic outline width outside target: {after['dimensions'][0]}")

metrics = {
    "before": before,
    "after": after,
    "width_profile": widths,
    "top_row_y": top_y,
    "left_edge_y": left_edge_y,
    "right_edge_y": right_edge_y,
    "hem_z": hem_z,
    "hem_right_minus_left": round(hem_z[-1] - hem_z[0], 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A81_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TunicEdgeOcclusion_A81"
scene["comforting_cat_v6_stage"] = "TUNIC_EDGE_OCCLUSION"
scene["comforting_cat_v6_attempt"] = 81
scene["comforting_cat_v6_dominant_defect"] = "visible_rectangular_apron_outline"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TUNIC_EDGE_OCCLUSION",
    "attempt": 81,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "visible_rectangular_apron_outline",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_FrontTunic outer columns, top two rows and hem"],
        "preserved": [
            "A80 tunic interior grid/topology/thickness/material",
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
