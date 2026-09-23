import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
VENDOR_ROOT = PROJECT_ROOT / "blender-workbench" / "vendor" / "mujoco_menagerie" / "shadow_hand"
XML_PATH = VENDOR_ROOT / "right_hand.xml"
KEYFRAMES_PATH = VENDOR_ROOT / "keyframes.xml"
ASSET_ROOT = VENDOR_ROOT / "assets"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_shadow_geometry.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_shadow_geometry_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-geometry-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-geometry-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-geometry-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_vec(value, size=3, default=None):
    if value is None:
        return list(default if default is not None else ([0.0] * size))
    result = [float(item) for item in value.split()]
    if len(result) != size:
        raise ValueError(f"Expected {size} values, got {value!r}")
    return result


def quat_matrix(value):
    quat = Quaternion(parse_vec(value, 4, (1.0, 0.0, 0.0, 0.0)))
    quat.normalize()
    return quat.to_matrix().to_4x4()


def transform_matrix(pos=None, quat=None):
    return Matrix.Translation(Vector(parse_vec(pos, 3, (0.0, 0.0, 0.0)))) @ quat_matrix(quat)


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def remove_object(name):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def principled_material(name, color, roughness, metallic=0.0, coat=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.09
    return material


def rounded_box(name, dimensions, location, radius, material, collection, parent, segments=10):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.48)
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    apply_material(obj, material)
    move_to_collection(obj, collection)
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    obj["export"] = True
    return obj


def create_text(name, body, location, material, collection, parent):
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 1.0
    curve.extrude = 0.075
    curve.bevel_depth = 0.014
    curve.bevel_resolution = 4
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    curve.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    target_width = 3.78
    scale = target_width / max(obj.dimensions.x, 0.001)
    obj.scale = (scale, scale, scale)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    obj["export"] = True
    return obj


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


def triangle_count(objects):
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            obj.data.calc_loop_triangles()
            total += len(obj.data.loop_triangles)
    return total


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


output = ensure_collection("TEAMON_OUTPUT")
source = ensure_collection("TEAMON_SOURCE")
studio = ensure_collection("TEAMON_STUDIO")
source.hide_render = True

composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
button_root = bpy.data.objects.get("TEAMON_ButtonRoot")
press_group = bpy.data.objects.get("TEAMON_PressGroup")
if None in (composition_root, button_root, press_group):
    raise RuntimeError("TEAMON button checkpoint is missing its root hierarchy")

# GEOMETRY stage: replace the thin slab with the deep, softly radiused casing
# and raised acrylic key seen in the primary reference.
for object_name in (
    "TEAMON_Base",
    "TEAMON_Recess",
    "TEAMON_RGB_Underplate",
    "TEAMON_Keycap",
    "TEAMON_Text",
    "TEAMON_HandRoot",
):
    remove_object(object_name)

black = principled_material("TEAMON_Black_Monolith", (0.008, 0.006, 0.008), 0.25, coat=0.34)
recess_black = principled_material("TEAMON_Recess_Black", (0.004, 0.004, 0.005), 0.31, coat=0.12)
white_text = principled_material("TEAMON_Text_White", (0.96, 0.97, 0.99), 0.22, coat=0.10)
robot_white = principled_material("TEAMON_Robot_White", (0.78, 0.81, 0.86), 0.38, coat=0.22)
robot_joint = principled_material("TEAMON_Robot_Joint_Rose", (0.35, 0.22, 0.23), 0.36, metallic=0.12, coat=0.10)

acrylic = bpy.data.materials.get("TEAMON_Clear_Acrylic")
gradient = bpy.data.materials.get("TEAMON_RGB_Continuous_Gradient")
if acrylic is None or gradient is None:
    raise RuntimeError("TEAMON button checkpoint is missing acrylic materials")

base = rounded_box(
    "TEAMON_Base", (6.35, 4.55, 0.88), (0.0, 0.0, 0.44), 0.30, black, output, button_root, 12
)
recess = rounded_box(
    "TEAMON_Recess", (5.90, 4.10, 0.16), (0.0, 0.0, 0.81), 0.14, recess_black, output, button_root, 8
)
underplate = rounded_box(
    "TEAMON_RGB_Underplate", (5.68, 3.88, 0.09), (0.0, 0.0, 0.90), 0.14, gradient, output, press_group, 8
)
keycap = rounded_box(
    "TEAMON_Keycap", (5.74, 3.94, 0.58), (0.0, 0.0, 1.16), 0.22, acrylic, output, press_group, 14
)
text = create_text("TEAMON_Text", "TEAMON", (-0.16, -0.02, 1.48), white_text, output, press_group)

# Read the official point pose. Joint order is the MJCF depth-first order.
xml_root = ET.parse(XML_PATH).getroot()
key_root = ET.parse(KEYFRAMES_PATH).getroot()
point_key = next(item for item in key_root.findall(".//key") if item.get("name") == "point")
qpos = [float(item) for item in point_key.get("qpos").split()]
joints = list(xml_root.findall(".//worldbody//joint"))
if len(qpos) != len(joints):
    raise RuntimeError(f"Point pose has {len(qpos)} qpos values for {len(joints)} joints")
qpos_by_joint = {joint.get("name"): qpos[index] for index, joint in enumerate(joints)}

class_axes = {
    "wrist_y": Vector((0.0, 1.0, 0.0)),
    "wrist_x": Vector((1.0, 0.0, 0.0)),
    "thbase": Vector((0.0, 0.0, -1.0)),
    "thproximal": Vector((1.0, 0.0, 0.0)),
    "thhub": Vector((1.0, 0.0, 0.0)),
    "thmiddle": Vector((0.0, -1.0, 0.0)),
    "thdistal": Vector((1.0, 0.0, 0.0)),
    "metacarpal": Vector((0.573576, 0.0, 0.819152)),
    "knuckle": Vector((0.0, -1.0, 0.0)),
    "proximal": Vector((1.0, 0.0, 0.0)),
    "middle_distal": Vector((1.0, 0.0, 0.0)),
}

hand_root = bpy.data.objects.new("TEAMON_HandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["asset_source"] = "Google DeepMind MuJoCo Menagerie / Shadow Hand E3M5"
hand_root["asset_license"] = "Apache-2.0"
hand_root["asset_revision"] = "71f066ad0be9cd271f7ed58c030243ef157af9f4"
hand_root["pose_source"] = "keyframes.xml:point"

template_by_mesh = {}
body_by_name = {}
visible_objects = []


def load_template(mesh_name):
    template = template_by_mesh.get(mesh_name)
    if template is not None:
        return template
    asset_path = ASSET_ROOT / f"{mesh_name}.obj"
    if not asset_path.exists():
        raise FileNotFoundError(asset_path)
    bpy.ops.object.select_all(action="DESELECT")
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(asset_path), forward_axis="Y", up_axis="Z")
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if not imported:
        raise RuntimeError(f"OBJ import created no mesh for {asset_path}")
    if len(imported) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in imported:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = imported[0]
        bpy.ops.object.join()
        imported = [bpy.context.object]
    template = imported[0]
    template.name = f"TEAMON_SOURCE_Shadow_{mesh_name}"
    move_to_collection(template, source)
    template.hide_render = True
    template.hide_set(True)
    template["export"] = False
    for polygon in template.data.polygons:
        polygon.use_smooth = True
    apply_material(template, robot_joint if mesh_name in {"f_knuckle", "wrist"} else robot_white)
    template_by_mesh[mesh_name] = template
    return template


def body_local_matrix(body_element):
    matrix = transform_matrix(body_element.get("pos"), body_element.get("quat"))
    for joint in body_element.findall("joint"):
        axis = Vector(parse_vec(joint.get("axis"), 3, class_axes.get(joint.get("class"), Vector((1.0, 0.0, 0.0)))))
        axis.normalize()
        pivot = Vector(parse_vec(joint.get("pos"), 3, (0.0, 0.0, 0.0)))
        angle = qpos_by_joint.get(joint.get("name"), 0.0)
        matrix @= Matrix.Translation(pivot) @ Quaternion(axis, angle).to_matrix().to_4x4() @ Matrix.Translation(-pivot)
    return matrix


def create_body(body_element, parent_object):
    body_name = body_element.get("name")
    body_object = bpy.data.objects.new(f"TEAMON_SH_{body_name}", None)
    output.objects.link(body_object)
    body_object.parent = parent_object
    body_object.matrix_local = body_local_matrix(body_element)
    body_object["mjcf_body"] = body_name
    body_by_name[body_name] = body_object

    visual_index = 0
    for geom in body_element.findall("geom"):
        mesh_name = geom.get("mesh")
        if mesh_name is None or geom.get("class") != "plastic_visual":
            continue
        template = load_template(mesh_name)
        visual = bpy.data.objects.new(
            f"TEAMON_SH_{body_name}_{mesh_name}_{visual_index:02d}", template.data
        )
        output.objects.link(visual)
        visual.parent = body_object
        visual.matrix_local = transform_matrix(geom.get("pos"), geom.get("quat")) @ Matrix.Diagonal((0.001, 0.001, 0.001, 1.0))
        visual["export"] = True
        visual["mjcf_mesh"] = mesh_name
        visual["mjcf_body"] = body_name
        visible_objects.append(visual)
        visual_index += 1

    for child_body in body_element.findall("body"):
        create_body(child_body, body_object)


worldbody = xml_root.find("worldbody")
for body in worldbody.findall("body"):
    create_body(body, hand_root)

bpy.context.view_layer.update()

# Initial HYBRID_HERO placement: align the hand plane over the button and use
# the real index distal mesh as the contact anchor.
wrist_point = body_by_name["rh_wrist"].matrix_world.translation.copy()
palm_point = body_by_name["rh_palm"].matrix_world.translation.copy()
index_tip_point = body_by_name["rh_ffdistal"].matrix_world @ Vector((0.0, 0.0, 0.030))
ff_point = body_by_name["rh_ffknuckle"].matrix_world.translation.copy()
lf_point = body_by_name["rh_lfknuckle"].matrix_world.translation.copy()

source_long = (index_tip_point - wrist_point).normalized()
source_width = (ff_point - lf_point).normalized()
source_normal = source_long.cross(source_width).normalized()
source_width = source_normal.cross(source_long).normalized()

target_long = Vector((-1.0, -0.10, -0.23)).normalized()
target_width = Vector((0.10, 1.0, 0.02))
target_width = (target_width - target_long * target_width.dot(target_long)).normalized()
target_normal = target_long.cross(target_width).normalized()
target_width = target_normal.cross(target_long).normalized()

source_basis = Matrix((source_long, source_width, source_normal)).transposed()
target_basis = Matrix((target_long, target_width, target_normal)).transposed()
rotation = target_basis @ source_basis.transposed()
hand_scale = 13.2
hand_root.matrix_world = rotation.to_4x4() @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
bpy.context.view_layer.update()

index_object = next(obj for obj in visible_objects if obj.get("mjcf_body") == "rh_ffdistal")
index_bounds = world_bounds([index_object])
index_center = Vector(
    (
        (index_bounds["min"][0] + index_bounds["max"][0]) * 0.5,
        (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5,
        index_bounds["min"][2],
    )
)
contact_target = Vector((1.12, -0.58, world_bounds([keycap])["max"][2] + 0.006))
hand_root.location += contact_target - index_center
bpy.context.view_layer.update()

# Preserve the current camera but frame the new, larger hand/button composition.
camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON checkpoint is missing the hero camera")
camera.location = (11.8, -13.9, 9.15)
camera.data.lens = 66
look_at(camera, (0.72, 0.10, 1.02))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"

hand_bounds = world_bounds(visible_objects)
button_bounds = world_bounds([base, keycap, text])
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens
camera.location = (9.8, 1.0, 5.1)
camera.data.lens = 62
look_at(camera, (0.8, 0.0, 1.0))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)
camera.location = (0.0, -0.4, 14.8)
camera.data.lens = 66
look_at(camera, (0.4, 0.0, 0.8))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v4 Shadow Hand geometry",
    "stage": "GEOMETRY",
    "mode": "HYBRID_HERO",
    "source_blend": bpy.data.filepath,
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "hand_source": "https://github.com/google-deepmind/mujoco_menagerie/tree/main/shadow_hand",
    "hand_revision": "71f066ad0be9cd271f7ed58c030243ef157af9f4",
    "hand_license": "Apache-2.0",
    "pose": "point",
    "hand_scale": hand_scale,
    "hand_visual_mesh_instances": len(visible_objects),
    "hand_triangles": triangle_count(visible_objects),
    "hand_bounds": hand_bounds,
    "button_bounds": button_bounds,
    "contact_target": list(contact_target),
    "index_tip_bounds": world_bounds([index_object]),
    "exported_glb": False,
    "status": "geometry_visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
