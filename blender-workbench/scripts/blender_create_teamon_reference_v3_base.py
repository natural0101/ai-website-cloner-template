import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REFERENCE_PATH = PROJECT_ROOT / "blender-workbench" / "references" / "teamon_button_reference.png"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_button_blockout.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_button_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-button-hero.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-button-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.worlds,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def create_collection(name):
    result = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(result)
    return result


def move_to_collection(obj, target):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def principled_material(name, color, roughness, metallic=0.0, coat=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.08
    return material


def acrylic_material(name):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (0.88, 0.96, 1.0, 0.80)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "B_SPLINE"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    stops = (
        (0.00, (1.0, 0.025, 0.008, 1.0)),
        (0.24, (1.0, 0.12, 0.018, 1.0)),
        (0.48, (1.0, 0.62, 0.035, 1.0)),
        (0.70, (0.20, 1.0, 0.13, 1.0)),
        (1.00, (0.00, 0.86, 0.43, 1.0)),
    )
    for index, (position, color) in enumerate(stops):
        element = ramp.color_ramp.elements[0] if index == 0 else ramp.color_ramp.elements.new(position)
        element.position = position
        element.color = color
    links.new(texcoord.outputs["Generated"], separate.inputs["Vector"])
    links.new(separate.outputs["X"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.85
    bsdf.inputs["Roughness"].default_value = 0.105
    bsdf.inputs["IOR"].default_value = 1.46
    bsdf.inputs["Alpha"].default_value = 0.80
    bsdf.inputs["Transmission Weight"].default_value = 0.28
    bsdf.inputs["Coat Weight"].default_value = 0.32
    bsdf.inputs["Coat Roughness"].default_value = 0.075
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    return material


def rgb_gradient_material(name):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")

    ramp.color_ramp.interpolation = "B_SPLINE"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    stops = (
        (0.00, (1.0, 0.006, 0.002, 1.0)),
        (0.24, (1.0, 0.08, 0.006, 1.0)),
        (0.48, (1.0, 0.55, 0.015, 1.0)),
        (0.70, (0.12, 1.0, 0.10, 1.0)),
        (1.00, (0.00, 0.88, 0.48, 1.0)),
    )
    for index, (position, color) in enumerate(stops):
        element = ramp.color_ramp.elements[0] if index == 0 else ramp.color_ramp.elements.new(position)
        element.position = position
        element.color = color

    emission.inputs["Strength"].default_value = 1.75
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], separate.inputs["Vector"])
    links.new(separate.outputs["X"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def rounded_box(name, dimensions, location, radius, material, target_collection, segments=10):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.48)
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    if hasattr(bevel, "harden_normals"):
        bevel.harden_normals = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    apply_material(obj, material)
    move_to_collection(obj, target_collection)
    return obj


def add_text(name, body, location, material, target_collection):
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 1.0
    curve.extrude = 0.075
    curve.bevel_depth = 0.012
    curve.bevel_resolution = 3
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path))
    obj = bpy.data.objects.new(name, curve)
    target_collection.objects.link(obj)
    obj.location = location
    apply_material(obj, material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    target_width = 3.44
    scale = target_width / max(obj.dimensions.x, 0.001)
    obj.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_area(name, location, energy, color, size, target_collection, target=(0.0, 0.0, 0.8)):
    data = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    target_collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


clear_scene()
scene = bpy.context.scene
scene.name = "TEAMON_Reference_V3"
source = create_collection("TEAMON_SOURCE")
output = create_collection("TEAMON_OUTPUT")
studio = create_collection("TEAMON_STUDIO")
source.hide_render = True

composition_root = bpy.data.objects.new("TEAMON_CompositionRoot", None)
output.objects.link(composition_root)
button_root = bpy.data.objects.new("TEAMON_ButtonRoot", None)
output.objects.link(button_root)
button_root.parent = composition_root
press_group = bpy.data.objects.new("TEAMON_PressGroup", None)
output.objects.link(press_group)
press_group.parent = button_root
press_group["interaction"] = "press"
press_group["press_axis"] = "LOCAL_Z"
press_group["press_travel"] = 0.14

black = principled_material("TEAMON_Black_Monolith", (0.010, 0.007, 0.008), 0.24, metallic=0.0, coat=0.30)
recess_black = principled_material("TEAMON_Recess_Black", (0.006, 0.005, 0.006), 0.30, metallic=0.0, coat=0.10)
white = principled_material("TEAMON_Text_White", (0.94, 0.96, 0.98), 0.26, coat=0.08)
acrylic = acrylic_material("TEAMON_Clear_Acrylic")
gradient = rgb_gradient_material("TEAMON_RGB_Continuous_Gradient")

base = rounded_box("TEAMON_Base", (6.00, 4.30, 0.70), (0.0, 0.0, 0.35), 0.14, black, output, segments=8)
parent_keep_world(base, button_root)
recess = rounded_box("TEAMON_Recess", (5.62, 3.90, 0.045), (0.0, 0.0, 0.6225), 0.018, recess_black, output, segments=4)
parent_keep_world(recess, button_root)
underplate = rounded_box("TEAMON_RGB_Underplate", (5.30, 3.56, 0.015), (0.0, 0.0, 0.650), 0.006, gradient, output, segments=3)
parent_keep_world(underplate, press_group)
keycap = rounded_box("TEAMON_Keycap", (5.46, 3.72, 0.42), (0.0, 0.0, 0.89), 0.040, acrylic, output, segments=6)
parent_keep_world(keycap, press_group)
text = add_text("TEAMON_Text", "TEAMON", (-0.28, -0.08, 1.112), white, output)
parent_keep_world(text, press_group)

if REFERENCE_PATH.exists():
    image = bpy.data.images.load(str(REFERENCE_PATH), check_existing=True)
    reference = bpy.data.objects.new("TEAMON_Reference_Image", None)
    reference.empty_display_type = "IMAGE"
    reference.data = image
    reference.empty_display_size = 6.0
    reference.location = (0.0, 5.2, 3.0)
    reference.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
    source.objects.link(reference)

red = principled_material("TEAMON_Studio_Red", (0.55, 0.004, 0.002), 0.34)
floor = rounded_box("TEAMON_Studio_Floor", (18.0, 14.0, 0.18), (0.0, 0.0, -0.22), 0.08, red, studio, segments=3)

world = bpy.data.worlds.new("TEAMON_Red_World")
world.use_nodes = True
scene.world = world
world_bg = world.node_tree.nodes.get("Background")
world_bg.inputs["Color"].default_value = (0.18, 0.0012, 0.0006, 1.0)
world_bg.inputs["Strength"].default_value = 0.32

add_area("TEAMON_Key_Light", (-4.0, -4.2, 8.2), 1450.0, (1.0, 0.93, 0.88), 5.4, studio)
add_area("TEAMON_Fill_Light", (5.4, -1.5, 6.2), 980.0, (0.76, 0.88, 1.0), 4.2, studio)
add_area("TEAMON_Rim_Light", (0.0, 6.0, 5.8), 1150.0, (1.0, 0.13, 0.05), 4.0, studio)

camera_data = bpy.data.cameras.new("TEAMON_Camera_Data")
camera = bpy.data.objects.new("TEAMON_Camera", camera_data)
studio.objects.link(camera)
camera.location = (11.25, -12.60, 9.55)
camera.data.lens = 68
look_at(camera, (0.92, 0.24, 0.72))
scene.camera = camera

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 16
scene.render.film_transparent = False
scene.render.fps = 60
scene.view_settings.look = "AgX - Medium High Contrast"

bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens
camera.location = (0.0, -0.15, 10.9)
camera.data.lens = 66
look_at(camera, (0.0, 0.0, 0.75))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens

report = {
    "asset": "TEAMON reference v3 button blockout",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(TOP_PATH)],
    "exported_glb": False,
    "objects": [obj.name for obj in output.objects],
    "button_dimensions": {
        "base": list(base.dimensions),
        "recess": list(recess.dimensions),
        "keycap": list(keycap.dimensions),
    },
    "gate": "Button silhouette and materials must be visually approved before hand construction",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
