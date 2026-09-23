import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
ASSET_ROOT = PROJECT_ROOT / "blender-workbench" / "vendor" / "RUKA-v2" / "assets"
URDF_PATH = ASSET_ROOT / "robot.urdf"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v7_ruka_probe.blend"
RENDER_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v7-ruka-probe.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v7_ruka_probe.json"

for path in (BLEND_PATH, RENDER_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_vector(value, default=(0.0, 0.0, 0.0)):
    if value is None:
        return Vector(default)
    return Vector(tuple(float(part) for part in value.split()))


def urdf_transform(origin):
    if origin is None:
        return Matrix.Identity(4)
    xyz = parse_vector(origin.get("xyz"))
    rpy = parse_vector(origin.get("rpy"))
    rotation = Euler((rpy.x, rpy.y, rpy.z), "XYZ").to_matrix().to_4x4()
    return Matrix.Translation(xyz) @ rotation


def set_principled(material, color, roughness, coat=0.0, metallic=0.0):
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.14
    material.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])


def ensure_material(name, color, roughness, coat=0.0, metallic=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    set_principled(material, color, roughness, coat, metallic)
    return material


def remove_tree(obj):
    for child in list(obj.children):
        remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def move_to_collection(obj, collection):
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)


def mesh_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH" and not obj.hide_render:
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


output = bpy.data.collections.get("TEAMON_OUTPUT")
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
keycap = bpy.data.objects.get("TEAMON_Keycap")
camera = bpy.data.objects.get("TEAMON_Camera")
if None in (output, composition_root, keycap, camera):
    raise RuntimeError("TEAMON geometry checkpoint is incomplete")

for name in ("TEAMON_AbilityHandRoot", "TEAMON_RUKA_HandRoot"):
    old = bpy.data.objects.get(name)
    if old is not None:
        remove_tree(old)
for old in list(bpy.data.objects):
    if old.name.startswith("TEAMON_ORCA_") or old.name in {"TEAMON_AbilityHand_Cuff", "TEAMON_ORCA_CuffShell"}:
        bpy.data.objects.remove(old, do_unlink=True)

robot_white = ensure_material("TEAMON_RUKA_White", (0.92, 0.945, 0.985), 0.31, coat=0.20)
robot_joint = ensure_material("TEAMON_RUKA_Rose", (0.58, 0.34, 0.38), 0.40, coat=0.06)
robot_dark = ensure_material("TEAMON_RUKA_Dark", (0.055, 0.045, 0.06), 0.48, metallic=0.08)

pose = {
    "index_splay": 0.00,
    "index_mcp": 0.02,
    "index_pip": 0.03,
    "index_dip": 0.03,
    "mid_mcp": 0.66,
    "mid_pip": 0.82,
    "mid_dip": 0.55,
    "ring_splay": 0.00,
    "ring_mcp": 0.76,
    "ring_pip": 0.90,
    "ring_dip": 0.62,
    "pinky_splay": 0.02,
    "pinky_mcp": 0.84,
    "pinky_pip": 0.98,
    "pinky_dip": 0.68,
    "thumb_cmc": 0.34,
    "thumb_mcp": 0.24,
    "thumb_ip": 0.44,
    "wrist_yaw": 0.0,
    "base_pitch": 0.0,
    "base_yaw": 0.0,
}

root_xml = ET.parse(URDF_PATH).getroot()
link_xml = {element.get("name"): element for element in root_xml.findall("link")}
joint_by_child = {}
children_by_parent = {}
for joint in root_xml.findall("joint"):
    parent_name = joint.find("parent").get("link")
    child_name = joint.find("child").get("link")
    joint_by_child[child_name] = joint
    children_by_parent.setdefault(parent_name, []).append(child_name)

hand_root = bpy.data.objects.new("TEAMON_RUKA_HandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["asset_source"] = "https://github.com/ruka-hand-v2/RUKA-v2"
hand_root["asset_revision"] = "f19818821c90f985be30ce3ea7b35e5c5db6b7ce"
hand_root["asset_license"] = "MIT"

template_by_path = {}
link_objects = {}
visual_objects = []


def template_for(path):
    template = template_by_path.get(path)
    if template is not None:
        return template
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if len(imported) != 1:
        raise RuntimeError(f"Unexpected STL import count for {path}: {len(imported)}")
    template = imported[0]
    template.name = f"TEAMON_SOURCE_RUKA_{path.stem}"
    source_collection = bpy.data.collections.get("TEAMON_SOURCE")
    move_to_collection(template, source_collection)
    template.hide_render = True
    template.hide_set(True)
    template["export"] = False
    for polygon in template.data.polygons:
        polygon.use_smooth = True
    template_by_path[path] = template
    return template


def choose_material(mesh_name):
    lower = mesh_name.lower()
    if any(token in lower for token in ("inner", "low_ball", "bearing", "part_1")):
        return robot_dark
    if any(token in lower for token in ("outer", "cap", "connector")):
        return robot_joint
    return robot_white


def joint_matrix(joint):
    matrix = urdf_transform(joint.find("origin"))
    if joint.get("type") == "revolute":
        axis = parse_vector(joint.find("axis").get("xyz"), (0.0, 0.0, 1.0)).normalized()
        angle = pose.get(joint.get("name"), 0.0)
        matrix @= Quaternion(axis, angle).to_matrix().to_4x4()
    return matrix


def build_link(link_name, parent_object):
    link_object = bpy.data.objects.new(f"TEAMON_RUKA_LINK_{link_name}", None)
    output.objects.link(link_object)
    link_object.parent = parent_object
    joint = joint_by_child.get(link_name)
    link_object.matrix_local = joint_matrix(joint) if joint is not None else Matrix.Identity(4)
    link_object["ruka_link"] = link_name
    link_objects[link_name] = link_object

    hero_hidden_links = {"base_new", "outer", "inner"}
    for index, visual in enumerate(link_xml[link_name].findall("visual")):
        if link_name in hero_hidden_links:
            continue
        mesh = visual.find("geometry/mesh")
        if mesh is None:
            continue
        filename = mesh.get("filename").replace("package://assets/", "")
        mesh_path = ASSET_ROOT / filename
        template = template_for(mesh_path)
        obj = bpy.data.objects.new(f"TEAMON_RUKA_{link_name}_{mesh_path.stem}_{index:02d}", template.data)
        output.objects.link(obj)
        obj.parent = link_object
        obj.matrix_local = urdf_transform(visual.find("origin"))
        obj.data.materials.clear()
        obj.data.materials.append(choose_material(mesh_path.stem))
        obj["ruka_link"] = link_name
        obj["ruka_mesh"] = mesh_path.stem
        obj["export"] = True
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        visual_objects.append(obj)

    for child_name in children_by_parent.get(link_name, []):
        build_link(child_name, link_object)

    return link_object


build_link("base_new", hand_root)
bpy.context.view_layer.update()

wrist_point = link_objects["backhand"].matrix_world.translation.copy()
index_tip = link_objects["index_actual_tip"].matrix_world.translation.copy()
index_base = link_objects["knuclke_index_ext"].matrix_world.translation.copy()
pinky_base = link_objects["knuckle_ring_ext_2"].matrix_world.translation.copy()
source_long = (index_tip - wrist_point).normalized()
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
rotation = Quaternion(target_long, math.radians(34.0)).to_matrix() @ target_basis @ source_basis.transposed()
hand_scale = 3.05 / (index_tip - wrist_point).length
hand_root.matrix_world = rotation.to_4x4() @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
bpy.context.view_layer.update()

key_points = [keycap.matrix_world @ Vector(corner) for corner in keycap.bound_box]
key_top = max(point.z for point in key_points)
tip_world = link_objects["index_actual_tip"].matrix_world.translation.copy()
contact_target = Vector((1.90, -0.54, key_top + 0.055))
hand_root.location += contact_target - tip_world
bpy.context.view_layer.update()

visible = [obj for obj in visual_objects if not obj.hide_render]
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(RENDER_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON v7 RUKA-v2 probe",
    "stage": "ASSET_POSE_PROBE",
    "blend": str(BLEND_PATH),
    "render": str(RENDER_PATH),
    "source": "https://github.com/ruka-hand-v2/RUKA-v2",
    "revision": "f19818821c90f985be30ce3ea7b35e5c5db6b7ce",
    "license": "MIT",
    "visual_meshes": len(visible),
    "triangles": triangle_count(visible),
    "hand_scale": hand_scale,
    "hand_bounds": mesh_bounds(visible),
    "contact_target": list(contact_target),
    "pose": pose,
    "status": "visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
