from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT_VERSION = os.environ.get("TEAMON_OUTPUT_VERSION", "v19")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / f"teamon_reference_{OUTPUT_VERSION}_material.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / f"teamon-{OUTPUT_VERSION}-material-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_{OUTPUT_VERSION}_material_report.json"


def principled(material_name: str):
    material = bpy.data.materials[material_name]
    return next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")


acrylic = bpy.data.materials["TEAMON_Clear_Acrylic"]
acrylic.surface_render_method = "DITHERED"
acrylic_bsdf = principled("TEAMON_Clear_Acrylic")
acrylic_bsdf.inputs["Base Color"].default_value = (0.72, 0.90, 1.0, 1.0)
acrylic_bsdf.inputs["Roughness"].default_value = 0.035
acrylic_bsdf.inputs["IOR"].default_value = 1.47
acrylic_bsdf.inputs["Alpha"].default_value = 0.12
acrylic_bsdf.inputs["Transmission Weight"].default_value = 0.12
acrylic_bsdf.inputs["Coat Weight"].default_value = 1.0
acrylic_bsdf.inputs["Coat Roughness"].default_value = 0.025

gradient = bpy.data.materials["TEAMON_RGB_Continuous_Gradient"]
emission = next(node for node in gradient.node_tree.nodes if node.type == "EMISSION")
emission.inputs["Strength"].default_value = 2.2
mix = gradient.node_tree.nodes.get("Mix (Legacy)")
if mix is not None:
    mix.inputs[0].default_value = 0.24

# Put the same RGB field directly on the acrylic surface. This keeps the
# saturated color readable while a glossy Principled layer supplies the
# thick-keycap highlights that the reference depends on.
surface = bpy.data.materials.get("TEAMON_RGB_GlassSurface")
if surface is not None:
    bpy.data.materials.remove(surface)
surface = gradient.copy()
surface.name = "TEAMON_RGB_GlassSurface"
surface.surface_render_method = "DITHERED"
surface_nodes = surface.node_tree.nodes
surface_links = surface.node_tree.links
surface_output = next(node for node in surface_nodes if node.type == "OUTPUT_MATERIAL")
surface_emission = next(node for node in surface_nodes if node.type == "EMISSION")
surface_mix = surface_nodes.get("Mix (Legacy)")
surface_links.remove(next(link for link in surface_links if link.to_node == surface_output))
surface_nodes.remove(surface_emission)
surface_bsdf = surface_nodes.new("ShaderNodeBsdfPrincipled")
surface_bsdf.name = "RGB Acrylic BSDF"
surface_bsdf.inputs["Roughness"].default_value = 0.085
surface_bsdf.inputs["IOR"].default_value = 1.47
surface_bsdf.inputs["Alpha"].default_value = 0.82
surface_bsdf.inputs["Transmission Weight"].default_value = 0.08
surface_bsdf.inputs["Coat Weight"].default_value = 1.0
surface_bsdf.inputs["Coat Roughness"].default_value = 0.025
surface_bsdf.inputs["Emission Strength"].default_value = 0.55
surface_links.new(surface_mix.outputs["Color"], surface_bsdf.inputs["Base Color"])
surface_links.new(surface_mix.outputs["Color"], surface_bsdf.inputs["Emission Color"])
surface_links.new(surface_bsdf.outputs["BSDF"], surface_output.inputs["Surface"])
keycap = bpy.data.objects["TEAMON_Keycap"]
keycap.data.materials.clear()
keycap.data.materials.append(surface)

white = principled("TEAMON_Ability_DebugWhite")
white.inputs["Base Color"].default_value = (0.97, 0.985, 1.0, 1.0)
white.inputs["Roughness"].default_value = 0.22
white.inputs["Coat Weight"].default_value = 0.22
white.inputs["Coat Roughness"].default_value = 0.035

text = principled("TEAMON_Text_White")
text.inputs["Roughness"].default_value = 0.20
text.inputs["Emission Strength"].default_value = 0.0

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.filepath = str(PREVIEW_PATH)
bpy.ops.render.render(write_still=True)

report = {
    "stage": "MATERIAL",
    "target_mode": "HYBRID_HERO",
    "input_checkpoint": bpy.data.filepath,
    "checkpoint": str(BLEND_PATH),
    "preview": str(PREVIEW_PATH),
    "acrylic": {
        "alpha": 0.82,
        "transmission": 0.08,
        "roughness": 0.085,
        "coat": 1.0,
    },
    "rgb_emission_strength": 2.2,
    "status": "material_visual_gate",
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
