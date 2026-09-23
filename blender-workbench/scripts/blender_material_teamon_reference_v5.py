import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v5_orca_material.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_material_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-material-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def principled(material):
    if not material or not material.use_nodes:
        raise RuntimeError(f"Missing node material: {getattr(material, 'name', None)}")
    result = material.node_tree.nodes.get("Principled BSDF")
    if result is None:
        raise RuntimeError(f"Missing Principled BSDF: {material.name}")
    return result


acrylic = bpy.data.materials.get("TEAMON_Clear_Acrylic")
gradient = bpy.data.materials.get("TEAMON_RGB_Continuous_Gradient")
text_material = bpy.data.materials.get("TEAMON_Text_White")
robot_white = bpy.data.materials.get("TEAMON_Robot_White")
robot_secondary = bpy.data.materials.get("TEAMON_Robot_Secondary_White")
robot_joint = bpy.data.materials.get("TEAMON_Robot_Joint_Rose")
black = bpy.data.materials.get("TEAMON_Black_Monolith")
if None in (acrylic, gradient, text_material, robot_white, robot_secondary, robot_joint, black):
    raise RuntimeError("TEAMON v5 composition checkpoint lacks required materials")

# MATERIAL only: reveal the RGB plate without creating a second glass shell.
acrylic_bsdf = principled(acrylic)
acrylic_bsdf.inputs["Base Color"].default_value = (0.96, 0.985, 1.0, 1.0)
acrylic_bsdf.inputs["Roughness"].default_value = 0.075
acrylic_bsdf.inputs["IOR"].default_value = 1.45
acrylic_bsdf.inputs["Transmission Weight"].default_value = 0.32
acrylic_bsdf.inputs["Coat Weight"].default_value = 0.92
acrylic_bsdf.inputs["Coat Roughness"].default_value = 0.04
acrylic_bsdf.inputs["Alpha"].default_value = 0.30
acrylic.diffuse_color = (0.96, 0.985, 1.0, 0.30)
if hasattr(acrylic, "surface_render_method"):
    acrylic.surface_render_method = "DITHERED"

emission = next((node for node in gradient.node_tree.nodes if node.bl_idname == "ShaderNodeEmission"), None)
if emission is None:
    raise RuntimeError("TEAMON RGB gradient lacks its emission node")
emission.inputs["Strength"].default_value = 3.4

text_bsdf = principled(text_material)
text_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
text_bsdf.inputs["Roughness"].default_value = 0.15
if "Emission Color" in text_bsdf.inputs:
    text_bsdf.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    text_bsdf.inputs["Emission Strength"].default_value = 0.035

for material, color, roughness in (
    (robot_white, (0.96, 0.97, 0.99), 0.31),
    (robot_secondary, (0.84, 0.85, 0.89), 0.38),
    (robot_joint, (0.68, 0.45, 0.48), 0.40),
):
    bsdf = principled(material)
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness

black_bsdf = principled(black)
black_bsdf.inputs["Base Color"].default_value = (0.004, 0.003, 0.005, 1.0)
black_bsdf.inputs["Metallic"].default_value = 0.0
black_bsdf.inputs["Roughness"].default_value = 0.42

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v5 ORCA materials",
    "stage": "MATERIAL",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "acrylic": {"transmission": 0.32, "roughness": 0.075, "alpha": 0.30, "coat": 0.92},
    "rgb_emission_strength": 3.4,
    "status": "material_visual_gate"
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
