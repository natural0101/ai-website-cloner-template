import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
VENDOR_ROOT = PROJECT_ROOT / "blender-workbench" / "vendor" / "orcahand_description"
ASSET_XML = VENDOR_ROOT / "v2" / "models" / "mjcf" / "orcahand_right.mjcf"
BODY_XML = VENDOR_ROOT / "v2" / "models" / "mjcf" / "orcahand_right_body.xml"
SOURCE_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_rigged.blend"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v5_orca_geometry.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_geometry_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-geometry-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-geometry-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-geometry-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_vec(value, size=3, default=None):
    if value is None:
        return list(default if default is not None else ([0.0] * size))
    values = [float(item) for item in value.split()]
    if len(values) != size:
        raise ValueError(f"Expected {size} values, got {value!r}")
    return values


def quat_matrix(value):
    quat = Quaternion(parse_vec(value, 4, (1.0, 0.0, 0.0, 0.0)))
    quat.normalize()
    return quat.to_matrix().to_4x4()


def transform_matrix(pos=None, quat=None):
    return Matrix.Translation(Vector(parse_vec(pos, 3, (0.0, 0.0, 0.0)))) @ quat_matrix(quat)


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def remove_tree(obj):
    for child in list(obj.children):
        remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def remove_named(name):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        remove_tree(obj)


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def set_principled(material, color, roughness, metallic=0.0, coat=0.0):
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.12
    material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return bsdf


def material(name, color, roughness, metallic=0.0, coat=0.0):
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    set_principled(result, color, roughness, metallic, coat)
    return result


def rounded_box(name, dimensions, location, radius, material_value, collection, parent, segments=12):
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
    apply_material(obj, material_value)
    move_to_collection(obj, collection)
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    obj["export"] = True
    return obj


def create_text(name, body, location, material_value, collection, parent, target_width):
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 1.0
    curve.extrude = 0.032
    curve.bevel_depth = 0.007
    curve.bevel_resolution = 4
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    curve.materials.append(material_value)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    uniform_scale = target_width / max(obj.dimensions.x, 0.001)
    obj.scale = (uniform_scale, uniform_scale, uniform_scale)
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


def world_points(obj):
    if obj.type != "MESH":
        return []
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH":
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


if not SOURCE_BLEND.exists():
    raise FileNotFoundError(SOURCE_BLEND)

output = ensure_collection("TEAMON_OUTPUT")
source = ensure_collection("TEAMON_SOURCE")
source.hide_render = True
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
button_root = bpy.data.objects.get("TEAMON_ButtonRoot")
press_group = bpy.data.objects.get("TEAMON_PressGroup")
if None in (composition_root, button_root, press_group):
    raise RuntimeError("TEAMON v4 checkpoint lacks the expected root hierarchy")

# GEOMETRY: preserve the rejected v4 checkpoint on disk while replacing its
# hand and rebuilding the visible key layers in this v5 branch.
remove_named("TEAMON_HandRoot")
remove_named("TEAMON_HandPressGroup")
for obj in list(bpy.data.objects):
    if obj.name.startswith("TEAMON_SOURCE_Shadow_"):
        bpy.data.objects.remove(obj, do_unlink=True)
for name in ("TEAMON_Base", "TEAMON_Recess", "TEAMON_RGB_Underplate", "TEAMON_Keycap", "TEAMON_Text"):
    remove_named(name)

for obj in (press_group,):
    obj.animation_data_clear()

black = material("TEAMON_Black_Monolith", (0.006, 0.005, 0.007), 0.40, coat=0.12)
recess_black = material("TEAMON_Recess_Black", (0.003, 0.003, 0.004), 0.45, coat=0.04)
text_white = material("TEAMON_Text_White", (0.98, 0.99, 1.0), 0.22, coat=0.06)
robot_white = material("TEAMON_Robot_White", (0.92, 0.94, 0.98), 0.34, coat=0.18)
robot_secondary = material("TEAMON_Robot_Secondary_White", (0.76, 0.78, 0.83), 0.42, coat=0.08)
robot_joint = material("TEAMON_Robot_Joint_Rose", (0.58, 0.38, 0.41), 0.43, coat=0.05)

acrylic = bpy.data.materials.get("TEAMON_Clear_Acrylic") or bpy.data.materials.new("TEAMON_Clear_Acrylic")
acrylic_bsdf = set_principled(acrylic, (0.91, 0.96, 1.0), 0.12, coat=0.72)
acrylic_bsdf.inputs["IOR"].default_value = 1.45
acrylic_bsdf.inputs["Transmission Weight"].default_value = 0.18
acrylic_bsdf.inputs["Alpha"].default_value = 0.42
acrylic.diffuse_color = (0.91, 0.96, 1.0, 0.42)
if hasattr(acrylic, "surface_render_method"):
    acrylic.surface_render_method = "DITHERED"

gradient = bpy.data.materials.get("TEAMON_RGB_Continuous_Gradient")
if gradient is None:
    raise RuntimeError("TEAMON v4 checkpoint lacks the RGB underplate material")

base = rounded_box("TEAMON_Base", (6.10, 4.35, 0.86), (0.0, 0.0, 0.43), 0.32, black, output, button_root, 14)
recess = rounded_box("TEAMON_Recess", (5.65, 3.90, 0.12), (0.0, 0.0, 0.78), 0.14, recess_black, output, button_root, 10)
underplate = rounded_box("TEAMON_RGB_Underplate", (5.00, 3.28, 0.08), (0.0, 0.0, 0.86), 0.16, gradient, output, button_root, 10)
keycap = rounded_box("TEAMON_Keycap", (5.18, 3.46, 0.28), (0.0, 0.0, 1.04), 0.20, acrylic, output, press_group, 16)
text = create_text("TEAMON_Text", "TEAMON", (-0.38, -0.02, 1.205), text_white, output, press_group, 2.90)
underplate["interaction"] = "fixed_rgb_light_source"

asset_root = ET.parse(ASSET_XML).getroot()
asset_map = {}
for mesh_element in asset_root.findall(".//asset/mesh"):
    relative = mesh_element.get("file")
    if relative:
        asset_map[mesh_element.get("name")] = VENDOR_ROOT / "v2" / relative

pose = {
    "right_wrist": 0.06,
    "right_p-abd": 0.00,
    "right_p-mcp": 1.02,
    "right_p-pip": 1.20,
    "right_r-abd": 0.00,
    "right_r-mcp": 0.96,
    "right_r-pip": 1.16,
    "right_m-abd": 0.00,
    "right_m-mcp": 0.88,
    "right_m-pip": 1.10,
    "right_i-abd": 0.00,
    "right_i-mcp": 0.00,
    "right_i-pip": 0.03,
    "right_t-cmc": 0.12,
    "right_t-abd": 0.48,
    "right_t-mcp": 0.58,
    "right_t-pip": 0.62,
}

hand_root = bpy.data.objects.new("TEAMON_AbilityHandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["asset_source"] = "https://github.com/orcahand/orcahand_description"
hand_root["asset_license"] = "MIT"
hand_root["asset_revision"] = "b9b349a21ee0238c62b6cf92ae7597027867adf8"
hand_root["pose"] = "index extended; middle/ring/pinky curled"

template_by_mesh = {}
body_by_name = {}
visual_objects = []
visual_by_mesh = {}


def load_template(mesh_name):
    template = template_by_mesh.get(mesh_name)
    if template is not None:
        return template
    path = asset_map.get(mesh_name)
    if path is None or not path.exists():
        raise FileNotFoundError(path or mesh_name)
    bpy.ops.object.select_all(action="DESELECT")
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if len(imported) != 1:
        raise RuntimeError(f"STL import for {mesh_name} produced {len(imported)} meshes")
    template = imported[0]
    template.name = f"TEAMON_SOURCE_ORCA_{mesh_name}"
    move_to_collection(template, source)
    template.hide_render = True
    template.hide_set(True)
    template["export"] = False
    for polygon in template.data.polygons:
        polygon.use_smooth = True
    template.data.calc_loop_triangles()
    original_triangles = len(template.data.loop_triangles)
    if original_triangles > 1000:
        decimate = template.modifiers.new(name="TEAMON_WebDecimate", type="DECIMATE")
        decimate.ratio = 0.72 if "Skin" in mesh_name else 0.16
        decimate.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = template
        bpy.ops.object.modifier_apply(modifier=decimate.name)
        template.data.calc_loop_triangles()
    template["source_triangles"] = original_triangles
    template["web_triangles"] = len(template.data.loop_triangles)
    template_by_mesh[mesh_name] = template
    return template


def body_local_matrix(body_element):
    matrix = transform_matrix(body_element.get("pos"), body_element.get("quat"))
    for joint in body_element.findall("joint"):
        axis = Vector(parse_vec(joint.get("axis"), 3, (1.0, 0.0, 0.0)))
        axis.normalize()
        pivot = Vector(parse_vec(joint.get("pos"), 3, (0.0, 0.0, 0.0)))
        angle = pose.get(joint.get("name"), float(joint.get("ref", "0")))
        matrix @= Matrix.Translation(pivot) @ Quaternion(axis, angle).to_matrix().to_4x4() @ Matrix.Translation(-pivot)
    return matrix


def choose_robot_material(mesh_name, declared):
    if declared == "white":
        return robot_white
    if "IP_IP" in mesh_name:
        return robot_joint
    if "ForeArm" in mesh_name or "TopTower" in mesh_name or "Carpals" in mesh_name:
        return robot_white
    return robot_secondary


def create_body(body_element, parent):
    body_name = body_element.get("name")
    body_object = bpy.data.objects.new(f"TEAMON_ORCA_{body_name}", None)
    output.objects.link(body_object)
    body_object.parent = parent
    body_object.matrix_local = body_local_matrix(body_element)
    body_object["orca_body"] = body_name
    body_by_name[body_name] = body_object

    for index, geom in enumerate(body_element.findall("geom")):
        mesh_name = geom.get("mesh")
        if not mesh_name:
            continue
        template = load_template(mesh_name)
        visual = bpy.data.objects.new(f"TEAMON_ORCA_{body_name}_{mesh_name}_{index:02d}", template.data)
        output.objects.link(visual)
        visual.parent = body_object
        visual.matrix_local = transform_matrix(geom.get("pos"), geom.get("quat")) @ Matrix.Diagonal((0.001, 0.001, 0.001, 1.0))
        apply_material(visual, choose_robot_material(mesh_name, geom.get("material")))
        visual["export"] = True
        visual["orca_mesh"] = mesh_name
        visual["orca_body"] = body_name
        visual_objects.append(visual)
        visual_by_mesh.setdefault(mesh_name, []).append(visual)

    for child in body_element.findall("body"):
        create_body(child, body_object)


body_root = ET.parse(BODY_XML).getroot()
for body_element in body_root.findall("body"):
    create_body(body_element, hand_root)
bpy.context.view_layer.update()

wrist = body_by_name["right_R-Carpals_8d1f1041"].matrix_world.translation.copy()
index_base = body_by_name["right_I-AP-R_d95d02d1"].matrix_world.translation.copy()
pinky_base = body_by_name["right_P-AP_f5e42b61"].matrix_world.translation.copy()
index_skin = visual_by_mesh["right_I-FingerTipAssembly_I-DP-Skin"][0]
index_points = world_points(index_skin)
index_tip = max(index_points, key=lambda point: (point - wrist).length)
source_long = (index_tip - wrist).normalized()
source_width = (index_base - pinky_base).normalized()
source_normal = source_long.cross(source_width).normalized()
source_width = source_normal.cross(source_long).normalized()

target_long = Vector((-1.0, -0.10, -0.55)).normalized()
target_width = Vector((-0.08, -0.05, -1.0))
target_width = (target_width - target_long * target_width.dot(target_long)).normalized()
target_normal = target_long.cross(target_width).normalized()
target_width = target_normal.cross(target_long).normalized()
source_basis = Matrix((source_long, source_width, source_normal)).transposed()
target_basis = Matrix((target_long, target_width, target_normal)).transposed()
rotation = Quaternion(target_long, math.radians(5.0)).to_matrix() @ target_basis @ source_basis.transposed()
source_length = (index_tip - wrist).length
hand_scale = 2.95 / source_length
hand_root.matrix_world = rotation.to_4x4() @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
bpy.context.view_layer.update()

index_bounds = world_bounds([index_skin])
index_contact = Vector(((index_bounds["min"][0] + index_bounds["max"][0]) * 0.5, (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5, index_bounds["min"][2]))
key_bounds = world_bounds([keycap])
contact_target = Vector((1.95, -0.56, key_bounds["max"][2] + 0.004))
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

# ORCA's mechanical forearm is deliberately open. The supplied reference uses
# a broad, uninterrupted white cuff, so hide only the open tower meshes and add
# one editable rounded shell that overlaps the retained wrist/palm assembly.
for visual in visual_objects:
    if visual.get("orca_mesh") in {
        "right_ForeArmStructure-Model",
        "right_ForeArmStructure-Model_Logo",
        "right_TopTower-Model",
    }:
        visual.hide_render = True
        visual["export"] = False

wrist_world = body_by_name["right_R-Carpals_8d1f1041"].matrix_world.translation.copy()
arm_axis = -target_long
cuff_rings = [
    (-0.18, 0.68, 0.56),
    (0.08, 0.74, 0.61),
    (0.55, 0.82, 0.68),
    (1.35, 0.92, 0.76),
    (2.35, 1.02, 0.84),
]
cuff_segments = 32
cuff_power = 2.0 / 2.6
cuff_vertices = []
for distance, half_width, half_height in cuff_rings:
    center = wrist_world + arm_axis * distance
    for segment in range(cuff_segments):
        angle = math.tau * segment / cuff_segments
        cosine = math.cos(angle)
        sine = math.sin(angle)
        width_value = math.copysign(abs(cosine) ** cuff_power, cosine) * half_width
        height_value = math.copysign(abs(sine) ** cuff_power, sine) * half_height
        cuff_vertices.append(center + target_width * width_value + target_normal * height_value)
cuff_faces = []
for ring_index in range(len(cuff_rings) - 1):
    current_start = ring_index * cuff_segments
    next_start = (ring_index + 1) * cuff_segments
    for segment in range(cuff_segments):
        next_segment = (segment + 1) % cuff_segments
        cuff_faces.append(
            (
                current_start + segment,
                current_start + next_segment,
                next_start + next_segment,
                next_start + segment,
            )
        )
cuff_faces.append(tuple(range((len(cuff_rings) - 1) * cuff_segments, len(cuff_rings) * cuff_segments)))
cuff_mesh = bpy.data.meshes.new("TEAMON_ORCA_CuffShell_Mesh")
cuff_mesh.from_pydata(cuff_vertices, [], cuff_faces)
cuff_mesh.validate(clean_customdata=True)
cuff_mesh.update()
cuff = bpy.data.objects.new("TEAMON_ORCA_CuffShell", cuff_mesh)
output.objects.link(cuff)
cuff.data.materials.append(robot_white)
for polygon in cuff.data.polygons:
    polygon.use_smooth = True
cuff.parent = hand_root
cuff.matrix_world = Matrix.Identity(4)
cuff["source"] = "tapered reference-matching cuff shell over ORCA wrist"
cuff["export"] = True
visual_objects.append(cuff)
bpy.context.view_layer.update()

camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON v4 checkpoint lacks the hero camera")
camera.location = (12.8, -14.0, 9.7)
camera.data.lens = 70
look_at(camera, (0.45, 0.05, 1.12))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"

scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens

camera.location = (10.5, 1.5, 5.8)
camera.data.lens = 62
look_at(camera, (0.7, 0.0, 1.1))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)

camera.location = (0.2, -0.5, 15.5)
camera.data.lens = 68
look_at(camera, (0.5, 0.0, 0.9))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
report = {
    "asset": "TEAMON reference v5 ORCA geometry",
    "stage": "GEOMETRY",
    "mode": "HYBRID_HERO",
    "source_blend": str(SOURCE_BLEND),
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "hand_source": "https://github.com/orcahand/orcahand_description",
    "hand_revision": "b9b349a21ee0238c62b6cf92ae7597027867adf8",
    "hand_license": "MIT",
    "hand_visual_meshes": len(visual_objects),
    "hand_triangles": triangle_count(visual_objects),
    "hand_scale": hand_scale,
    "hand_bounds": world_bounds(visual_objects),
    "button_bounds": world_bounds([base, keycap, text]),
    "contact_target": list(contact_target),
    "index_tip_bounds": world_bounds([index_skin]),
    "pose": pose,
    "exported_glb": False,
    "status": "geometry_visual_gate"
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
