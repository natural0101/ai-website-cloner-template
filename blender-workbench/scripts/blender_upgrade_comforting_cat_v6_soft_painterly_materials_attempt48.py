"""Replace saturated plastic lookdev with soft muted fur and cloth materials."""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_soft_painterly_materials_attempt48"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_side_sweep_remediation_attempt47.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_soft_painterly_materials_attempt48.blend"
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


def principled(material: bpy.types.Material) -> bpy.types.ShaderNodeBsdfPrincipled:
    material.use_nodes = True
    node = next(
        (item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED"),
        None,
    )
    if node is None:
        raise RuntimeError(f"No Principled BSDF in {material.name}")
    return node


def set_socket(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def clear_a48_nodes(material: bpy.types.Material) -> None:
    for node in list(material.node_tree.nodes):
        if node.name.startswith("A48_"):
            material.node_tree.nodes.remove(node)


def configure_material(
    material_name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
    sheen: float,
    color_low: tuple[float, float, float, float] | None = None,
    color_high: tuple[float, float, float, float] | None = None,
    color_scale: float = 3.0,
    bump_scale: float | None = None,
    bump_strength: float = 0.08,
    bump_distance: float = 0.01,
    coat: float = 0.0,
    coat_roughness: float = 0.22,
) -> dict:
    material = bpy.data.materials[material_name]
    shader = principled(material)
    clear_a48_nodes(material)
    set_socket(shader, "Base Color", base_color)
    set_socket(shader, "Roughness", roughness)
    set_socket(shader, "Sheen Weight", sheen)
    set_socket(shader, "Coat Weight", coat)
    set_socket(shader, "Coat Roughness", coat_roughness)
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    if color_low is not None and color_high is not None:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.name = "A48_ColorVariation"
        noise.label = "A48 soft color variation"
        noise.noise_dimensions = "3D"
        set_socket(noise, "Scale", color_scale)
        set_socket(noise, "Detail", 2.0)
        set_socket(noise, "Roughness", 0.65)
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.name = "A48_ColorRamp"
        ramp.label = "A48 narrow painterly palette"
        ramp.color_ramp.interpolation = "EASE"
        ramp.color_ramp.elements[0].position = 0.28
        ramp.color_ramp.elements[0].color = color_low
        ramp.color_ramp.elements[1].position = 0.72
        ramp.color_ramp.elements[1].color = color_high
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])

    if bump_scale is not None:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.name = "A48_MicroBumpNoise"
        noise.label = "A48 soft micro relief"
        noise.noise_dimensions = "3D"
        set_socket(noise, "Scale", bump_scale)
        set_socket(noise, "Detail", 3.0)
        set_socket(noise, "Roughness", 0.72)
        bump = nodes.new("ShaderNodeBump")
        bump.name = "A48_MicroBump"
        bump.label = "A48 restrained surface breakup"
        set_socket(bump, "Strength", bump_strength)
        set_socket(bump, "Distance", bump_distance)
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    return {
        "material": material_name,
        "base_color": list(base_color),
        "roughness": roughness,
        "sheen": sheen,
        "coat": coat,
        "color_variation": color_low is not None,
        "micro_bump": bump_scale is not None,
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
    "V6_EyeIrisWarm_A14",
    "CAT_EyeDarkGlass",
    "CAT_InnerEarPink",
    "V6_LeatherBrown",
    "V6_DarkWeatheredLeather",
]
preserved_materials = []
for name in material_names:
    source = bpy.data.materials[name].copy()
    source.name = f"{name}_SOURCE_A48"
    source["comforting_cat_preserved_material"] = True
    source["comforting_cat_rejection_reason"] = "saturated_plastic_material_baseline"
    preserved_materials.append(source.name)

# Create a dedicated eye highlight before modifying the shared cream-fur shader.
highlight_material = bpy.data.materials["V6_CreamFur"].copy()
highlight_material.name = "V6_EyeHighlightSoft_A48"
highlight_shader = principled(highlight_material)
clear_a48_nodes(highlight_material)
set_socket(highlight_shader, "Base Color", (0.90, 0.82, 0.67, 1.0))
set_socket(highlight_shader, "Roughness", 0.28)
set_socket(highlight_shader, "Sheen Weight", 0.0)
set_socket(highlight_shader, "Coat Weight", 0.12)
set_socket(highlight_shader, "Coat Roughness", 0.18)
for object_name in ("V6_EyeHighlight_L", "V6_EyeHighlight_R"):
    obj = bpy.data.objects[object_name]
    obj.data.materials.clear()
    obj.data.materials.append(highlight_material)

changes = [
    configure_material(
        "CAT_GoldenOrangeFur",
        (0.34, 0.16, 0.055, 1.0),
        0.86,
        0.34,
        (0.30, 0.135, 0.045, 1.0),
        (0.38, 0.19, 0.070, 1.0),
        2.8,
        34.0,
        0.09,
        0.012,
    ),
    configure_material(
        "V6_CreamFur",
        (0.55, 0.41, 0.24, 1.0),
        0.88,
        0.28,
        (0.50, 0.37, 0.21, 1.0),
        (0.60, 0.46, 0.28, 1.0),
        3.5,
        30.0,
        0.075,
        0.010,
    ),
    configure_material(
        "V6_WarmFelinePaw_A34",
        (0.49, 0.32, 0.17, 1.0),
        0.86,
        0.24,
        (0.45, 0.28, 0.14, 1.0),
        (0.54, 0.37, 0.20, 1.0),
        4.0,
        32.0,
        0.07,
        0.010,
    ),
    configure_material(
        "CAT_WeatheredBlueCloth",
        (0.050, 0.100, 0.125, 1.0),
        0.91,
        0.24,
        (0.040, 0.080, 0.100, 1.0),
        (0.060, 0.120, 0.145, 1.0),
        3.2,
        55.0,
        0.12,
        0.008,
    ),
    configure_material(
        "V6_TunicWarmLinen_A27",
        (0.125, 0.165, 0.175, 1.0),
        0.92,
        0.18,
        (0.105, 0.145, 0.155, 1.0),
        (0.145, 0.190, 0.198, 1.0),
        4.0,
        48.0,
        0.10,
        0.007,
    ),
    configure_material(
        "V6_EyeIrisWarm_A14",
        (0.030, 0.022, 0.017, 1.0),
        0.50,
        0.0,
        coat=0.10,
        coat_roughness=0.20,
    ),
    configure_material(
        "CAT_EyeDarkGlass",
        (0.006, 0.007, 0.008, 1.0),
        0.31,
        0.0,
        coat=0.18,
        coat_roughness=0.16,
    ),
    configure_material(
        "CAT_InnerEarPink",
        (0.42, 0.14, 0.11, 1.0),
        0.88,
        0.20,
        bump_scale=28.0,
        bump_strength=0.05,
        bump_distance=0.006,
    ),
    configure_material(
        "V6_LeatherBrown",
        (0.070, 0.026, 0.010, 1.0),
        0.78,
        0.0,
    ),
    configure_material(
        "V6_DarkWeatheredLeather",
        (0.095, 0.034, 0.012, 1.0),
        0.80,
        0.08,
        (0.075, 0.025, 0.008, 1.0),
        (0.115, 0.045, 0.018, 1.0),
        5.0,
        18.0,
        0.07,
        0.010,
    ),
]

bpy.context.view_layer.update()
geometry_hash_after = geometry_hash(export_objects)
bounds_after = {obj.name: bounds(obj) for obj in mesh_objects}
geometry_unchanged = geometry_hash_before == geometry_hash_after and bounds_before == bounds_after
if not geometry_unchanged:
    raise RuntimeError("Material stage changed geometry or object transforms")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_SoftPainterlyMaterials_A48"
scene["comforting_cat_v6_stage"] = "SOFT_PAINTERLY_MATERIALS"
scene["comforting_cat_v6_attempt"] = 48
scene["comforting_cat_v6_dominant_defect"] = "saturated_plastic_fur_and_flat_dark_cloth"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SOFT_PAINTERLY_MATERIALS",
    "attempt": 48,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "saturated_plastic_fur_and_flat_dark_cloth",
    "preserved_materials": preserved_materials,
    "dedicated_highlight_material": highlight_material.name,
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
