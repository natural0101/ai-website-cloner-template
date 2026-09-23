"""Replace the hidden shield drape with a seated forward-sloping cloth overlap."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_scarf_front_layer_occlusion_attempt54"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_front_layer_occlusion_attempt54.blend"
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


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
non_drape_objects = [obj for obj in descendants(root) if obj.name != drape.name]
non_drape_hash_before = geometry_hash(non_drape_objects)
before = bounds(drape)
topology_before = {"vertices": len(drape.data.vertices), "faces": len(drape.data.polygons)}
preserved_source = preserve_copy(
    drape,
    "Comforting_Cat_V6",
    "A54",
    "front_drape_hidden_behind_tunic_and_shield_shaped",
)

outline = [
    (-0.400, 2.320),
    (-0.100, 2.360),
    (0.380, 2.280),
    (0.330, 2.120),
    (0.200, 1.980),
    (-0.050, 1.940),
    (-0.300, 2.020),
    (-0.420, 2.160),
]
front_vertices = [(x, -0.490, z) for x, z in outline]
back_vertices = []
for x, z in outline:
    if z >= 2.260:
        y = -0.280
    elif z <= 2.020:
        y = -0.400
    else:
        t = (z - 2.020) / 0.240
        y = -0.400 + 0.120 * t
    back_vertices.append((x, y, z))
vertices = front_vertices + back_vertices
count = len(outline)
faces: list[tuple[int, ...]] = [
    tuple(reversed(range(count))),
    tuple(range(count, count * 2)),
]
for index in range(count):
    next_index = (index + 1) % count
    faces.append((index, count + index, count + next_index, next_index))

materials = list(drape.data.materials)
mesh = bpy.data.meshes.new("V6_Scarf_FrontDrape_ForwardFoldMesh_A54")
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
bevel = drape.modifiers.new("V6_Scarf_FrontDrape_SoftFoldEdge_A54", "BEVEL")
bevel.width = 0.014
bevel.segments = 3
bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = bounds(drape)
topology_after = {"vertices": len(drape.data.vertices), "faces": len(drape.data.polygons)}
non_drape_hash_after = geometry_hash(non_drape_objects)
if non_drape_hash_before != non_drape_hash_after:
    raise RuntimeError("Drape pass changed non-drape geometry or transforms")

upper_bounds = bounds(upper)
lower_bounds = bounds(lower)
tunic_bounds = bounds(bpy.data.objects["V6_FrontTunic"])
metrics = {
    "drape_dimensions": after["dimensions"],
    "drape_upper_y_overlap": round(overlap_1d(after, upper_bounds, 1), 5),
    "drape_upper_z_overlap": round(overlap_1d(after, upper_bounds, 2), 5),
    "drape_lower_y_overlap": round(overlap_1d(after, lower_bounds, 1), 5),
    "drape_lower_z_overlap": round(overlap_1d(after, lower_bounds, 2), 5),
    "drape_front_margin_over_tunic": round(tunic_bounds["min"][1] - after["min"][1], 5),
    "non_drape_hash_before": non_drape_hash_before,
    "non_drape_hash_after": non_drape_hash_after,
}
if metrics["drape_front_margin_over_tunic"] < 0.03:
    raise RuntimeError("Drape is not visibly in front of the tunic")
if metrics["drape_upper_y_overlap"] < 0.02 or metrics["drape_upper_z_overlap"] < 0.10:
    raise RuntimeError("Drape top is not seated through the upper scarf")
if metrics["drape_lower_y_overlap"] < 0.04 or metrics["drape_lower_z_overlap"] < 0.15:
    raise RuntimeError("Drape is not seated through the lower scarf")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfFrontLayerOcclusion_A54"
scene["comforting_cat_v6_stage"] = "SCARF_FRONT_LAYER_OCCLUSION"
scene["comforting_cat_v6_attempt"] = 54
scene["comforting_cat_v6_dominant_defect"] = "drape_hidden_behind_tunic_and_shield_shaped"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_FRONT_LAYER_OCCLUSION",
    "attempt": 54,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "drape_hidden_behind_tunic_and_shield_shaped",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
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
