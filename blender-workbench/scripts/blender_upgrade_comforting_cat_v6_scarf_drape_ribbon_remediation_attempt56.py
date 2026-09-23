"""Remediate A53's leaf flap as a compact diagonal scarf ribbon."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_scarf_drape_ribbon_remediation_attempt56"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_scarf_vertical_layer_stack_attempt53.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_drape_ribbon_remediation_attempt56.blend"
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


root = bpy.data.objects["CatV6_Root"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
non_drape_objects = [obj for obj in descendants(root) if obj.name != drape.name]
non_drape_hash_before = geometry_hash(non_drape_objects)
before = bounds(drape)
preserved_source = preserve_copy(
    drape,
    "Comforting_Cat_V6",
    "A56",
    "centered_convex_leaf_drape",
)

# Seven-point trapezoid: broad diagonal upper edge, narrower rounded lower edge,
# no single central apex and only a shallow center sag.
outline = [
    (-0.430, 2.310),
    (-0.220, 2.330),
    (-0.050, 2.325),
    (0.310, 2.250),
    (0.200, 2.090),
    (-0.080, 2.070),
    (-0.340, 2.100),
]
front = [(x, -0.405, z) for x, z in outline]
back = []
for x, z in outline:
    if z >= 2.245:
        y = -0.295
    elif z <= 2.105:
        y = -0.320
    else:
        t = (z - 2.105) / 0.140
        y = -0.320 + 0.025 * t
    back.append((x, y, z))

vertices = front + back
count = len(outline)
faces: list[tuple[int, ...]] = [
    tuple(reversed(range(count))),
    tuple(range(count, count * 2)),
]
for index in range(count):
    next_index = (index + 1) % count
    faces.append((index, count + index, count + next_index, next_index))

materials = list(drape.data.materials)
mesh = bpy.data.meshes.new("V6_Scarf_FrontDrape_RibbonMesh_A56")
mesh.from_pydata(vertices, [], faces)
mesh.update(calc_edges=True)
old_mesh = drape.data
drape.data = mesh
for material in materials:
    drape.data.materials.append(material)
for polygon in drape.data.polygons:
    polygon.use_smooth = True
drape.data.update()
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)

for modifier in list(drape.modifiers):
    if modifier.type in {"SOLIDIFY", "BEVEL"}:
        drape.modifiers.remove(modifier)
bevel = drape.modifiers.new("V6_Scarf_FrontDrape_RibbonEdge_A56", "BEVEL")
bevel.width = 0.004
bevel.segments = 2
bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = bounds(drape)
non_drape_hash_after = geometry_hash(non_drape_objects)
if non_drape_hash_before != non_drape_hash_after:
    raise RuntimeError("Ribbon pass changed non-drape geometry or transforms")

all_meshes = [obj for obj in descendants(root) if obj.type == "MESH"]
subject_min_z = min(bounds(obj)["min"][2] for obj in all_meshes)
subject_max_z = max(bounds(obj)["max"][2] for obj in all_meshes)
subject_height = subject_max_z - subject_min_z
scarf_objects = [
    bpy.data.objects["V6_ScarfWrap_Upper"],
    bpy.data.objects["V6_ScarfWrap_Lower"],
    drape,
]
scarf_bounds = [bounds(obj) for obj in scarf_objects]
scarf_min_z = min(item["min"][2] for item in scarf_bounds)
scarf_max_z = max(item["max"][2] for item in scarf_bounds)
scarf_width = max(item["max"][0] for item in scarf_bounds) - min(
    item["min"][0] for item in scarf_bounds
)
robe_bounds = bounds(bpy.data.objects["V6_Robe"])
metrics = {
    "drape_dimensions": after["dimensions"],
    "drape_centroid_x": round((after["min"][0] + after["max"][0]) * 0.5, 5),
    "upper_edge_drop": 0.060,
    "lower_over_upper_width": round((0.200 - (-0.340)) / (0.310 - (-0.430)), 5),
    "scarf_union_height_over_subject": round((scarf_max_z - scarf_min_z) / subject_height, 5),
    "scarf_union_width_over_subject": round(scarf_width / subject_height, 5),
    "ear_top_to_scarf_bottom_over_subject": round((subject_max_z - scarf_min_z) / subject_height, 5),
    "scarf_bottom_to_robe_hem_over_subject": round((scarf_min_z - robe_bounds["min"][2]) / subject_height, 5),
    "non_drape_hash_before": non_drape_hash_before,
    "non_drape_hash_after": non_drape_hash_after,
}
if not 0.70 <= metrics["drape_dimensions"][0] <= 0.77:
    raise RuntimeError(f"Ribbon width outside target: {metrics['drape_dimensions'][0]}")
if not 0.085 <= metrics["drape_dimensions"][1] <= 0.120:
    raise RuntimeError(f"Ribbon depth outside target: {metrics['drape_dimensions'][1]}")
if not 0.25 <= metrics["drape_dimensions"][2] <= 0.29:
    raise RuntimeError(f"Ribbon height outside target: {metrics['drape_dimensions'][2]}")
if abs(metrics["scarf_union_height_over_subject"] - 0.1919) > 0.01:
    raise RuntimeError("A53 scarf/subject height ratio regressed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfDrapeRibbonRemediation_A56"
scene["comforting_cat_v6_stage"] = "SCARF_DRAPE_RIBBON_REMEDIATION"
scene["comforting_cat_v6_attempt"] = 56
scene["comforting_cat_v6_dominant_defect"] = "centered_convex_leaf_drape"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_DRAPE_RIBBON_REMEDIATION",
    "attempt": 56,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "centered_convex_leaf_drape",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": [drape.name], "non_drape_geometry_unchanged": True},
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
