"""Rebuild the accumulated banded head and wedge ears as a soft kitten silhouette."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_head_ear_silhouette_rebuild_attempt50"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_material_variation_restraint_attempt49.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_ear_silhouette_rebuild_attempt50.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def gaussian(value: float, center: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - center) / sigma) ** 2)


def rebuild_head(obj: bpy.types.Object) -> None:
    old_mesh = obj.data
    materials = list(old_mesh.materials)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=48, location=(0.0, 0.0, 0.0))
    temporary = bpy.context.object
    new_mesh = temporary.data.copy()
    bpy.data.objects.remove(temporary, do_unlink=True)

    for vertex in new_mesh.vertices:
        unit = vertex.co.normalized()
        zn = max(-1.0, min(1.0, unit.z))
        radial = math.sqrt(max(0.0, 1.0 - zn * zn))
        cheek = gaussian(zn, -0.18, 0.34)
        crown_softening = gaussian(zn, 0.62, 0.28)
        x_radius = 0.625 + 0.045 * cheek - 0.018 * crown_softening
        y_radius = 0.445 + 0.014 * cheek
        front_bias = 1.055 if unit.y < 0.0 else 1.0
        vertex.co.x = unit.x * radial * x_radius
        vertex.co.y = unit.y * radial * y_radius * front_bias
        vertex.co.z = unit.z * 0.540

    obj.data = new_mesh
    obj.data.name = "V6_Head_SoftKittenMesh_A50"
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def rebuild_prism(
    obj: bpy.types.Object,
    outline: list[tuple[float, float]],
    y_front: float,
    y_back: float,
) -> None:
    materials = list(obj.data.materials)
    count = len(outline)
    vertices = [(x, y_front, z) for x, z in outline] + [
        (x, y_back, z) for x, z in outline
    ]
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, count + index, count + next_index, next_index))
    mesh = bpy.data.meshes.new(f"{obj.name}_RoundedKittenMesh_A50")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    old_mesh = obj.data
    obj.data = mesh
    obj.data.materials.clear()
    for material in materials:
        obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
affected = [head, *ears]
before = {obj.name: bounds(obj) for obj in affected}
topology_before = {
    obj.name: {"vertices": len(obj.data.vertices), "faces": len(obj.data.polygons)}
    for obj in affected
}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A50", "banded_head_and_wedge_ear_baseline")
    for obj in affected
]

rebuild_head(head)

for side, sign in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer_outline = [
        (sign * 0.275, 3.195),
        (sign * 0.305, 3.285),
        (sign * 0.455, 3.490),
        (sign * 0.605, 3.285),
        (sign * 0.625, 3.190),
    ]
    inner_outline = [
        (sign * 0.335, 3.225),
        (sign * 0.355, 3.295),
        (sign * 0.455, 3.445),
        (sign * 0.555, 3.295),
        (sign * 0.575, 3.225),
    ]
    rebuild_prism(outer, outer_outline, -0.155, 0.135)
    rebuild_prism(inner, inner_outline, -0.178, -0.158)
    for obj, width in ((outer, 0.030), (inner, 0.014)):
        bevel = next((modifier for modifier in obj.modifiers if modifier.type == "BEVEL"), None)
        if bevel is None:
            bevel = obj.modifiers.new(f"{obj.name}_SoftFelineEdge_A50", "BEVEL")
        bevel.width = width
        bevel.segments = 4
        bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in affected}
topology_after = {
    obj.name: {"vertices": len(obj.data.vertices), "faces": len(obj.data.polygons)}
    for obj in affected
}

head_dims = after["V6_Head"]["dimensions"]
ear_height = after["V6_Ear_L"]["dimensions"][2]
metrics = {
    "head_width_height": round(head_dims[0] / head_dims[2], 5),
    "head_depth_height": round(head_dims[1] / head_dims[2], 5),
    "ear_height_over_head_height": round(ear_height / head_dims[2], 5),
    "head_width_before": before["V6_Head"]["dimensions"][0],
    "head_width_after": head_dims[0],
    "ear_height_before": before["V6_Ear_L"]["dimensions"][2],
    "ear_height_after": ear_height,
}

if not 1.19 <= metrics["head_width_height"] <= 1.27:
    raise RuntimeError(f"Head width/height outside target: {metrics['head_width_height']}")
if not 0.34 <= metrics["ear_height_over_head_height"] <= 0.39:
    raise RuntimeError(
        f"Ear/head height ratio outside target: {metrics['ear_height_over_head_height']}"
    )
if topology_after["V6_Head"] != topology_before["V6_Head"]:
    raise RuntimeError("Head rebuild unexpectedly changed resolution")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadEarSilhouetteRebuild_A50"
scene["comforting_cat_v6_stage"] = "HEAD_EAR_SILHOUETTE_REBUILD"
scene["comforting_cat_v6_attempt"] = 50
scene["comforting_cat_v6_dominant_defect"] = "banded_wide_head_and_tall_wedge_ears"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_EAR_SILHOUETTE_REBUILD",
    "attempt": 50,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "banded_wide_head_and_tall_wedge_ears",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head", *ear_names],
        "preserved": [
            "face_features",
            "costume",
            "arms",
            "legs",
            "tail",
            "satchel",
            "materials",
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
