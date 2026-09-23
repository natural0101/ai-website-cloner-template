"""Restrain A48 material noise without changing accepted geometry or cameras."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_material_variation_restraint_attempt49"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_soft_painterly_materials_attempt48.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_material_variation_restraint_attempt49.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
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


def set_socket(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def update_variation(
    material_name: str,
    low: tuple[float, float, float, float],
    high: tuple[float, float, float, float],
    color_scale: float,
    bump_strength: float,
) -> dict:
    material = bpy.data.materials[material_name]
    if not material.use_nodes:
        raise RuntimeError(f"Material {material_name} has no nodes")
    nodes = material.node_tree.nodes
    noise = nodes.get("A48_ColorVariation")
    ramp = nodes.get("A48_ColorRamp")
    bump = nodes.get("A48_MicroBump")
    if noise is None or ramp is None or bump is None:
        raise RuntimeError(f"A48 variation nodes missing from {material_name}")
    set_socket(noise, "Scale", color_scale)
    set_socket(noise, "Detail", 1.55)
    set_socket(noise, "Roughness", 0.52)
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = low
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = high
    set_socket(bump, "Strength", bump_strength)
    return {
        "material": material_name,
        "color_low": list(low),
        "color_high": list(high),
        "color_scale": color_scale,
        "bump_strength": bump_strength,
    }


root = bpy.data.objects["CatV6_Root"]
export_objects = descendants(root)
mesh_objects = [obj for obj in export_objects if obj.type == "MESH"]
geometry_hash_before = geometry_hash(export_objects)
bounds_before = {obj.name: bounds(obj) for obj in mesh_objects}

material_names = [
    "CAT_GoldenOrangeFur",
    "V6_CreamFur",
    "V6_WarmFelinePaw_A34",
    "CAT_WeatheredBlueCloth",
    "V6_TunicWarmLinen_A27",
    "V6_DarkWeatheredLeather",
]
preserved_materials = []
for name in material_names:
    source = bpy.data.materials[name].copy()
    source.name = f"{name}_SOURCE_A49"
    source["comforting_cat_preserved_material"] = True
    source["comforting_cat_rejection_reason"] = "a48_variation_too_cloudy"
    preserved_materials.append(source.name)

changes = [
    update_variation(
        "CAT_GoldenOrangeFur",
        (0.325, 0.155, 0.052, 1.0),
        (0.355, 0.175, 0.063, 1.0),
        7.0,
        0.055,
    ),
    update_variation(
        "V6_CreamFur",
        (0.540, 0.410, 0.245, 1.0),
        (0.580, 0.450, 0.275, 1.0),
        7.5,
        0.045,
    ),
    update_variation(
        "V6_WarmFelinePaw_A34",
        (0.480, 0.315, 0.165, 1.0),
        (0.515, 0.350, 0.190, 1.0),
        8.0,
        0.040,
    ),
    update_variation(
        "CAT_WeatheredBlueCloth",
        (0.047, 0.095, 0.117, 1.0),
        (0.054, 0.108, 0.132, 1.0),
        7.0,
        0.065,
    ),
    update_variation(
        "V6_TunicWarmLinen_A27",
        (0.118, 0.158, 0.168, 1.0),
        (0.135, 0.175, 0.183, 1.0),
        8.0,
        0.050,
    ),
    update_variation(
        "V6_DarkWeatheredLeather",
        (0.088, 0.031, 0.011, 1.0),
        (0.102, 0.038, 0.014, 1.0),
        8.0,
        0.035,
    ),
]

bpy.context.view_layer.update()
geometry_hash_after = geometry_hash(export_objects)
bounds_after = {obj.name: bounds(obj) for obj in mesh_objects}
geometry_unchanged = geometry_hash_before == geometry_hash_after and bounds_before == bounds_after
if not geometry_unchanged:
    raise RuntimeError("Material stage changed geometry or object transforms")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_MaterialVariationRestraint_A49"
scene["comforting_cat_v6_stage"] = "MATERIAL_VARIATION_RESTRAINT"
scene["comforting_cat_v6_attempt"] = 49
scene["comforting_cat_v6_dominant_defect"] = "a48_cloudy_material_variation"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "MATERIAL_VARIATION_RESTRAINT",
    "attempt": 49,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a48_cloudy_material_variation",
    "preserved_materials": preserved_materials,
    "changes": changes,
    "geometry_lock": {
        "hash_before": geometry_hash_before,
        "hash_after": geometry_hash_after,
        "bounds_unchanged": bounds_before == bounds_after,
        "passed": geometry_unchanged,
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
