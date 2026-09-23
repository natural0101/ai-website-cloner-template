"""Taper A50 ear depth toward each tip so side views stop reading as slabs."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_ear_depth_taper_attempt51"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_head_ear_silhouette_rebuild_attempt50.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_ear_depth_taper_attempt51.blend"
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


def rebuild_tapered_prism(
    obj: bpy.types.Object,
    front: list[tuple[float, float, float]],
    back: list[tuple[float, float, float]],
) -> None:
    materials = list(obj.data.materials)
    count = len(front)
    vertices = front + back
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, count + index, count + next_index, next_index))
    mesh = bpy.data.meshes.new(f"{obj.name}_DepthTaperMesh_A51")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    old_mesh = obj.data
    obj.data = mesh
    for material in materials:
        obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


root = bpy.data.objects["CatV6_Root"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
non_ear_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
non_ear_hash_before = geometry_hash(non_ear_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {
    obj.name: {"vertices": len(obj.data.vertices), "faces": len(obj.data.polygons)}
    for obj in ears
}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A51", "constant_depth_ear_slab")
    for obj in ears
]

for side, sign in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    outline = [
        (sign * 0.275, 3.195, -0.135, 0.105),
        (sign * 0.305, 3.285, -0.105, 0.075),
        (sign * 0.455, 3.490, -0.045, 0.035),
        (sign * 0.605, 3.285, -0.105, 0.075),
        (sign * 0.625, 3.190, -0.135, 0.105),
    ]
    outer_front = [(x, y_front, z) for x, z, y_front, _ in outline]
    outer_back = [(x, y_back, z) for x, z, _, y_back in outline]
    rebuild_tapered_prism(outer, outer_front, outer_back)

    inner_outline = [
        (sign * 0.335, 3.225, -0.149),
        (sign * 0.355, 3.295, -0.119),
        (sign * 0.455, 3.445, -0.059),
        (sign * 0.555, 3.295, -0.119),
        (sign * 0.575, 3.225, -0.149),
    ]
    inner_front = [(x, y, z) for x, z, y in inner_outline]
    inner_back = [(x, y + 0.006, z) for x, z, y in inner_outline]
    rebuild_tapered_prism(inner, inner_front, inner_back)

    for obj, width in ((outer, 0.024), (inner, 0.010)):
        bevel = next((modifier for modifier in obj.modifiers if modifier.type == "BEVEL"), None)
        if bevel is None:
            bevel = obj.modifiers.new(f"{obj.name}_SoftFelineEdge_A51", "BEVEL")
        bevel.width = width
        bevel.segments = 4
        bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {
    obj.name: {"vertices": len(obj.data.vertices), "faces": len(obj.data.polygons)}
    for obj in ears
}
non_ear_hash_after = geometry_hash(non_ear_objects)
if non_ear_hash_before != non_ear_hash_after:
    raise RuntimeError("Ear pass changed non-ear geometry or transforms")

left_outer = bpy.data.objects["V6_Ear_L"]
tip_y = [vertex.co.y for vertex in left_outer.data.vertices if vertex.co.z > 3.44]
base_y = [vertex.co.y for vertex in left_outer.data.vertices if vertex.co.z < 3.23]
tip_depth = max(tip_y) - min(tip_y)
base_depth = max(base_y) - min(base_y)
metrics = {
    "outer_ear_depth_before": before["V6_Ear_L"]["dimensions"][1],
    "outer_ear_depth_after": after["V6_Ear_L"]["dimensions"][1],
    "mesh_tip_depth": round(tip_depth, 5),
    "mesh_base_depth": round(base_depth, 5),
    "tip_over_base_depth": round(tip_depth / base_depth, 5),
    "non_ear_hash_before": non_ear_hash_before,
    "non_ear_hash_after": non_ear_hash_after,
}
if metrics["tip_over_base_depth"] > 0.38:
    raise RuntimeError(f"Ear tip did not taper enough: {metrics['tip_over_base_depth']}")
if topology_before != topology_after:
    raise RuntimeError("Ear taper unexpectedly changed topology resolution")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EarDepthTaper_A51"
scene["comforting_cat_v6_stage"] = "EAR_DEPTH_TAPER"
scene["comforting_cat_v6_attempt"] = 51
scene["comforting_cat_v6_dominant_defect"] = "ear_side_profile_reads_as_rectangular_slab"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "EAR_DEPTH_TAPER",
    "attempt": 51,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "ear_side_profile_reads_as_rectangular_slab",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {"changed": ear_names, "non_ear_geometry_unchanged": True},
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
