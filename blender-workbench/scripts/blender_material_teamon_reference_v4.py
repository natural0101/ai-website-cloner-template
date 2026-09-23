import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_material.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_material_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-material-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def set_principled(material, color, roughness, metallic=0.0, coat=0.0, coat_roughness=0.10):
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = coat_roughness
    material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return bsdf


black = bpy.data.materials.get("TEAMON_Black_Monolith")
recess = bpy.data.materials.get("TEAMON_Recess_Black")
acrylic = bpy.data.materials.get("TEAMON_Clear_Acrylic")
gradient = bpy.data.materials.get("TEAMON_RGB_Continuous_Gradient")
robot_white = bpy.data.materials.get("TEAMON_Robot_White")
robot_joint = bpy.data.materials.get("TEAMON_Robot_Joint_Rose")
text_material = bpy.data.materials.get("TEAMON_Text_White")
if None in (black, recess, acrylic, gradient, robot_white, robot_joint, text_material):
    raise RuntimeError("TEAMON v4 material checkpoint is incomplete")

set_principled(black, (0.008, 0.006, 0.008), 0.33, coat=0.22, coat_roughness=0.16)
set_principled(recess, (0.003, 0.003, 0.004), 0.38, coat=0.08, coat_roughness=0.22)
set_principled(robot_white, (0.82, 0.84, 0.88), 0.36, coat=0.20, coat_roughness=0.13)
set_principled(robot_joint, (0.36, 0.23, 0.24), 0.42, metallic=0.06, coat=0.08)
set_principled(text_material, (0.98, 0.99, 1.0), 0.24, coat=0.06)

# Clear optical shell. All RGB belongs to the separate underplate so the key
# keeps transparent depth and white edge reflections instead of reading as a
# flat emissive card.
acrylic_bsdf = set_principled(acrylic, (0.85, 0.93, 1.0), 0.095, coat=0.65, coat_roughness=0.055)
acrylic_bsdf.inputs["IOR"].default_value = 1.45
acrylic_bsdf.inputs["Transmission Weight"].default_value = 0.10
acrylic_bsdf.inputs["Alpha"].default_value = 0.28
acrylic.diffuse_color = (0.85, 0.93, 1.0, 0.28)
if hasattr(acrylic, "surface_render_method"):
    acrylic.surface_render_method = "BLENDED"

# Two-dimensional luminous field: warm red/orange at the left and front,
# yellow through the centre, green/cyan at the right and rear.
gradient.use_nodes = True
nodes = gradient.node_tree.nodes
links = gradient.node_tree.links
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
emission = nodes.new("ShaderNodeEmission")
texcoord = nodes.new("ShaderNodeTexCoord")
separate = nodes.new("ShaderNodeSeparateXYZ")
ramp_x = nodes.new("ShaderNodeValToRGB")
ramp_y = nodes.new("ShaderNodeValToRGB")
mix = nodes.new("ShaderNodeMixRGB")
mix.blend_type = "MIX"
mix.inputs[0].default_value = 0.32

for ramp in (ramp_x, ramp_y):
    ramp.color_ramp.interpolation = "B_SPLINE"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])

x_stops = (
    (0.00, (1.0, 0.015, 0.004, 1.0)),
    (0.32, (1.0, 0.19, 0.010, 1.0)),
    (0.52, (1.0, 0.78, 0.035, 1.0)),
    (0.77, (0.10, 1.0, 0.20, 1.0)),
    (1.00, (0.00, 0.72, 0.48, 1.0)),
)
y_stops = (
    (0.00, (1.0, 0.035, 0.008, 1.0)),
    (0.48, (1.0, 0.58, 0.025, 1.0)),
    (1.00, (0.20, 1.0, 0.24, 1.0)),
)
for position, color in x_stops:
    element = ramp_x.color_ramp.elements[0] if position == 0.0 else ramp_x.color_ramp.elements.new(position)
    element.position = position
    element.color = color
for position, color in y_stops:
    element = ramp_y.color_ramp.elements[0] if position == 0.0 else ramp_y.color_ramp.elements.new(position)
    element.position = position
    element.color = color

emission.inputs["Strength"].default_value = 1.80
links.new(texcoord.outputs["Generated"], separate.inputs["Vector"])
links.new(separate.outputs["X"], ramp_x.inputs["Fac"])
links.new(separate.outputs["Y"], ramp_y.inputs["Fac"])
links.new(ramp_x.outputs["Color"], mix.inputs[1])
links.new(ramp_y.outputs["Color"], mix.inputs[2])
links.new(mix.outputs["Color"], emission.inputs["Color"])
links.new(emission.outputs["Emission"], output.inputs["Surface"])

scene = bpy.context.scene
scene.render.resolution_x = 1024
scene.render.resolution_y = 576
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v4 materials",
    "stage": "MATERIAL",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "acrylic": {
        "transmission": 0.10,
        "roughness": 0.095,
        "ior": 1.45,
        "alpha": 0.28,
    },
    "rgb_underplate": "2D generated-coordinate blend, emission 1.80",
    "exported_glb": False,
    "status": "material_visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
