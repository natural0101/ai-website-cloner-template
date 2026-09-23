import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REFERENCE_PATH = PROJECT_ROOT / "blender-workbench" / "references" / "teamon_button_reference.png"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_click_button_v1.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_click_button_v1_scene_report.json"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_click_button_v1.glb"
RENDER_PATH = PROJECT_ROOT / "public" / "images" / "teamon-click-button-v1.png"


for path in (BLEND_PATH, REPORT_PATH, GLB_PATH, RENDER_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def collection(name):
    item = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(item)
    return item


def move_to_collection(obj, target):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def material_principled(name, base_color, metallic=0.0, roughness=0.4, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def material_acrylic(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (0.72, 0.96, 1.0, 0.32)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.82, 0.97, 1.0, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.07
    bsdf.inputs["IOR"].default_value = 1.46
    bsdf.inputs["Alpha"].default_value = 0.32
    bsdf.inputs["Transmission Weight"].default_value = 0.34
    bsdf.inputs["Coat Weight"].default_value = 0.35
    bsdf.inputs["Coat Roughness"].default_value = 0.08
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    return mat


def apply_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def rounded_box(name, dimensions, location, radius, mat, target_collection, segments=8):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name="Rounded_Edges", type="BEVEL")
    bevel.width = radius
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    if hasattr(bevel, "harden_normals"):
        bevel.harden_normals = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    apply_material(obj, mat)
    move_to_collection(obj, target_collection)
    return obj


def add_text(name, text, location, target_collection, mat):
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 1.25
    curve.extrude = 0.105
    curve.bevel_depth = 0.018
    curve.bevel_resolution = 4
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path))
    obj = bpy.data.objects.new(name, curve)
    target_collection.objects.link(obj)
    obj.location = location
    apply_material(obj, mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    if obj.dimensions.x > 4.14:
        scale = 4.14 / obj.dimensions.x
        obj.scale.x *= scale
        obj.scale.y *= scale
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area(name, location, energy, color, size, target_collection):
    data = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    target_collection.objects.link(obj)
    obj.location = location
    look_at(obj, (0.0, 0.0, 0.9))
    return obj


def add_point(name, location, energy, color, target_collection):
    data = bpy.data.lights.new(name=f"{name}_Data", type="POINT")
    data.energy = energy
    data.color = color
    data.shadow_soft_size = 1.0
    obj = bpy.data.objects.new(name, data)
    target_collection.objects.link(obj)
    obj.location = location
    return obj


clear_scene()
scene = bpy.context.scene
scene.name = "TEAMON_Click_Button_Scene"
asset = collection("TEAMON_ASSET")
studio = collection("TEAMON_STUDIO")
references = collection("TEAMON_REFERENCES")
references.hide_render = True

black = material_principled("TEAMON_Black_Base", (0.008, 0.009, 0.012), metallic=0.12, roughness=0.23)
rim_black = material_principled("TEAMON_Inner_Rim", (0.016, 0.018, 0.022), metallic=0.28, roughness=0.16)
white = material_principled("TEAMON_White_Lettering", (0.94, 0.97, 1.0), metallic=0.0, roughness=0.19)
red_glow = material_principled("TEAMON_Glow_Red", (0.85, 0.012, 0.004), roughness=0.24, emission=(1.0, 0.008, 0.001), emission_strength=8.0)
yellow_glow = material_principled("TEAMON_Glow_Yellow", (0.9, 0.36, 0.002), roughness=0.22, emission=(1.0, 0.32, 0.002), emission_strength=7.5)
green_glow = material_principled("TEAMON_Glow_Green", (0.002, 0.72, 0.12), roughness=0.22, emission=(0.002, 1.0, 0.10), emission_strength=7.5)
acrylic = material_acrylic("TEAMON_Clear_Acrylic")

root = bpy.data.objects.new("TEAMON_Root", None)
asset.objects.link(root)
press_group = bpy.data.objects.new("TEAMON_PressGroup", None)
asset.objects.link(press_group)
press_group.parent = root

base = rounded_box("TEAMON_Base", (5.9, 4.35, 0.82), (0.0, 0.0, 0.31), 0.34, black, asset)
base.parent = root
rim = rounded_box("TEAMON_Rim", (5.28, 3.76, 0.38), (0.0, 0.0, 0.82), 0.26, rim_black, asset)
rim.parent = root

panel_width = 1.58
for name, x, mat in (
    ("TEAMON_Glow_R", -1.58, red_glow),
    ("TEAMON_Glow_Y", 0.0, yellow_glow),
    ("TEAMON_Glow_G", 1.58, green_glow),
):
    panel = rounded_box(name, (panel_width, 3.23, 0.18), (x, 0.0, 1.02), 0.14, mat, asset, segments=6)
    panel.parent = root

keycap = rounded_box("TEAMON_Keycap", (4.92, 3.46, 0.52), (0.0, 0.0, 1.33), 0.24, acrylic, asset, segments=10)
keycap.parent = press_group
text_obj = add_text("TEAMON_Text", "TEAMON", (0.0, -0.02, 1.755), asset, white)
text_obj.parent = press_group

# A very thin bright edge under the clear cap sells the acrylic perimeter.
edge_mat = material_principled("TEAMON_Acrylic_Edge", (0.68, 0.91, 1.0), roughness=0.08, emission=(0.35, 0.72, 1.0), emission_strength=1.6)
edge = rounded_box("TEAMON_Keycap_Edge", (5.0, 3.54, 0.08), (0.0, 0.0, 1.12), 0.22, edge_mat, asset, segments=8)
edge.parent = press_group

if REFERENCE_PATH.exists():
    image = bpy.data.images.load(str(REFERENCE_PATH), check_existing=True)
    reference = bpy.data.objects.new("TEAMON_Reference_Image", None)
    reference.empty_display_type = "IMAGE"
    reference.data = image
    reference.empty_display_size = 5.5
    reference.location = (0.0, 4.8, 2.5)
    reference.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
    references.objects.link(reference)

studio_red = material_principled("TEAMON_Studio_Red", (0.48, 0.003, 0.002), roughness=0.31)
floor = rounded_box("TEAMON_Studio_Floor", (16.0, 13.0, 0.20), (0.0, 0.0, -0.21), 0.18, studio_red, studio, segments=4)

world = bpy.data.worlds.new("TEAMON_Red_World")
scene.world = world
world.use_nodes = True
world_bg = world.node_tree.nodes.get("Background")
world_bg.inputs["Color"].default_value = (0.12, 0.0015, 0.001, 1.0)
world_bg.inputs["Strength"].default_value = 0.22

add_area("TEAMON_Key_Light", (-4.5, -3.0, 7.8), 1250.0, (1.0, 0.92, 0.86), 5.0, studio)
add_area("TEAMON_Fill_Light", (4.8, -0.8, 5.4), 900.0, (0.70, 0.88, 1.0), 4.0, studio)
add_area("TEAMON_Rim_Light", (0.0, 5.0, 5.0), 1050.0, (1.0, 0.18, 0.08), 3.8, studio)
add_point("TEAMON_Red_Bounce", (-2.0, -0.3, 1.3), 105.0, (1.0, 0.02, 0.004), studio)
add_point("TEAMON_Green_Bounce", (2.0, 0.1, 1.35), 90.0, (0.01, 1.0, 0.16), studio)

camera_data = bpy.data.cameras.new("TEAMON_Camera_Data")
camera = bpy.data.objects.new("TEAMON_Camera", camera_data)
studio.objects.link(camera)
camera.location = (6.7, -7.8, 5.8)
camera.data.lens = 53
look_at(camera, (0.0, 0.0, 0.78))
scene.camera = camera

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1024
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.filepath = str(RENDER_PATH)
scene.render.resolution_percentage = 100
scene.render.image_settings.color_depth = "8"
scene.render.image_settings.compression = 18
scene.render.fps = 60
scene.render.film_transparent = False
scene.view_settings.look = "AgX - Medium High Contrast"

# Render first, while the studio is visible.
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

# Export only the named interactive asset hierarchy.
bpy.ops.object.select_all(action="DESELECT")
for obj in asset.objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)

mesh_objects = [obj for obj in asset.objects if obj.type == "MESH"]
triangle_count = sum(len(obj.data.loop_triangles) for obj in mesh_objects)
for obj in mesh_objects:
    obj.data.calc_loop_triangles()
triangle_count = sum(len(obj.data.loop_triangles) for obj in mesh_objects)

report = {
    "asset": "TEAMON clickable 3D button",
    "blender_version": bpy.app.version_string,
    "reference": str(REFERENCE_PATH),
    "outputs": {
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "preview": str(RENDER_PATH),
    },
    "collections": [item.name for item in scene.collection.children],
    "asset_objects": [
        {
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "dimensions": [round(value, 4) for value in obj.dimensions],
        }
        for obj in sorted(asset.objects, key=lambda item: item.name)
    ],
    "materials": sorted({slot.material.name for obj in mesh_objects for slot in obj.material_slots if slot.material}),
    "mesh_count": len(mesh_objects),
    "triangle_count": triangle_count,
    "contact_checks": {
        "base_top_z": 0.72,
        "rim_bottom_z": 0.63,
        "glow_top_z": 1.11,
        "keycap_bottom_z": 1.07,
        "keycap_to_glow_overlap": 0.04,
        "text_bottom_z": round(min((text_obj.matrix_world @ Vector(vertex.co)).z for vertex in text_obj.data.vertices), 4),
        "keycap_top_z": 1.59,
    },
    "validation": {
        "required_nodes": ["TEAMON_Root", "TEAMON_PressGroup", "TEAMON_Base", "TEAMON_Keycap", "TEAMON_Text"],
        "missing_required_nodes": [
            name for name in ("TEAMON_Root", "TEAMON_PressGroup", "TEAMON_Base", "TEAMON_Keycap", "TEAMON_Text")
            if bpy.data.objects.get(name) is None
        ],
        "web_triangle_budget_max": 100000,
        "within_triangle_budget": triangle_count <= 100000,
    },
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("TEAMON_BUILD_REPORT=" + json.dumps(report, ensure_ascii=False))
