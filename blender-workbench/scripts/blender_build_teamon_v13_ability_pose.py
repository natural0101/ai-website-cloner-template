from __future__ import annotations

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
VENDOR_ROOT = PROJECT_ROOT / "blender-workbench" / "vendor" / "ability-hand-api"
URDF_PATH = VENDOR_ROOT / "URDF" / "ability_hand_right_large.urdf"
PREVIEW_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v13_ability_pose_d.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v13_ability_pose_d_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v13_ability_pose_d_structural_qa.json"
QA_MODULES = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


VARIANT = "d"
POSE = {
    "index_q1": 0.02,
    "index_q2": 0.05,
    "middle_q1": 0.82,
    "middle_q2": 0.72,
    "ring_q1": 0.98,
    "ring_q2": 0.86,
    "pinky_q1": 1.12,
    "pinky_q2": 1.00,
    "thumb_q1": -0.08,
    "thumb_q2": 0.28,
}


def clear_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name != bpy.context.scene.collection.name:
            bpy.data.collections.remove(collection)


def parse_vector(value: str | None, default: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Vector:
    if value is None:
        return Vector(default)
    values = tuple(float(part) for part in value.split())
    if len(values) != 3:
        raise ValueError(f"Expected three values, got {value!r}")
    return Vector(values)


def origin_matrix(element: ET.Element | None) -> Matrix:
    if element is None:
        return Matrix.Identity(4)
    location = parse_vector(element.get("xyz"))
    rotation = parse_vector(element.get("rpy"))
    return Matrix.Translation(location) @ Euler(rotation, "XYZ").to_matrix().to_4x4()


def joint_matrix(joint: ET.Element) -> Matrix:
    matrix = origin_matrix(joint.find("origin"))
    if joint.get("type") == "fixed":
        return matrix
    axis = parse_vector(joint.find("axis").get("xyz") if joint.find("axis") is not None else None, (1.0, 0.0, 0.0))
    if axis.length == 0.0:
        axis = Vector((1.0, 0.0, 0.0))
    axis.normalize()
    angle = POSE.get(joint.get("name"), 0.0)
    return matrix @ Quaternion(axis, angle).to_matrix().to_4x4()


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def load_template(path: Path, source_collection: bpy.types.Collection, cache: dict[Path, bpy.types.Object]) -> bpy.types.Object:
    cached = cache.get(path)
    if cached is not None:
        return cached
    if not path.exists():
        raise FileNotFoundError(path)
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if len(imported) != 1:
        raise RuntimeError(f"STL import for {path.name} produced {len(imported)} meshes")
    template = imported[0]
    template.name = f"SOURCE_Ability_{path.stem}"
    move_to_collection(template, source_collection)
    template.hide_render = True
    template.hide_viewport = True
    template["abt_export"] = False
    template["source_file"] = str(path)
    for polygon in template.data.polygons:
        polygon.use_smooth = True
    cache[path] = template
    return template


def make_material(name: str, color: tuple[float, float, float], roughness: float, coat: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Coat Weight"].default_value = coat
    return material


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def add_area(name: str, location: Vector, target: Vector, energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (target - location).to_track_quat("-Z", "Y").to_euler()
    light["abt_export"] = False


def configure_preview(objects: list[bpy.types.Object]) -> bpy.types.Object:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.12, 0.004, 0.003, 1.0)
    background.inputs["Strength"].default_value = 0.45
    low, high = bounds(objects)
    center = (low + high) * 0.5
    span = max(high - low)
    add_area("TEAMON_Ability_Key", center + Vector((span * 1.4, -span * 1.5, span * 1.6)), center, 850.0, span)
    add_area("TEAMON_Ability_Fill", center + Vector((-span * 1.2, -span * 0.5, span)), center, 450.0, span * 1.2)
    add_area("TEAMON_Ability_Rim", center + Vector((0.0, span * 1.5, span)), center, 700.0, span)
    camera_data = bpy.data.cameras.new("TEAMON_Ability_PreviewCamera")
    camera = bpy.data.objects.new("TEAMON_Ability_PreviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera["abt_export"] = False
    scene.camera = camera
    return camera


def render_view(camera: bpy.types.Object, objects: list[bpy.types.Object], name: str, direction: Vector, up_axis: str) -> str:
    low, high = bounds(objects)
    center = (low + high) * 0.5
    extent = high - low
    span = max(extent)
    camera.location = center + direction.normalized() * span * 3.5
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", up_axis).to_euler()
    if name == "front":
        camera.data.ortho_scale = max(extent.x / (900 / 720), extent.z) * 1.18
    elif name == "side":
        camera.data.ortho_scale = max(extent.y / (900 / 720), extent.z) * 1.18
    else:
        camera.data.ortho_scale = span * 1.22
    path = PREVIEW_DIR / f"teamon-v13-ability-pose-{VARIANT}-{name}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def evaluated_triangles(obj: bpy.types.Object) -> int:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return len(mesh.loop_triangles)
    finally:
        evaluated.to_mesh_clear()


clear_scene()
root = ET.parse(URDF_PATH).getroot()
links = {link.get("name"): link for link in root.findall("link")}
joints = root.findall("joint")
child_links = {joint.find("child").get("link") for joint in joints}
root_links = sorted(set(links) - child_links)
if root_links != ["base"]:
    raise RuntimeError(f"Unexpected URDF roots: {root_links}")

source_collection = bpy.data.collections.new("SOURCE_Ability")
output_collection = bpy.data.collections.new("TEAMON_Ability_Pose_OUTPUT")
bpy.context.scene.collection.children.link(source_collection)
bpy.context.scene.collection.children.link(output_collection)
hand_root = bpy.data.objects.new("TEAMON_Ability_HandRoot", None)
output_collection.objects.link(hand_root)
hand_root.scale = (10.0, 10.0, 10.0)
hand_root["abt_export"] = True
hand_root["pose_variant"] = VARIANT
hand_root["source_revision"] = "34c9a9324d3739d976e6de441e56ccefafd0000b"
hand_root["source_license"] = "MIT"

white = make_material("TEAMON_Ability_DebugWhite", (0.94, 0.965, 1.0), 0.3, 0.12)
template_cache: dict[Path, bpy.types.Object] = {}
link_objects: dict[str, bpy.types.Object] = {}
visual_objects: list[bpy.types.Object] = []
children_by_parent: dict[str, list[ET.Element]] = {}
for joint in joints:
    children_by_parent.setdefault(joint.find("parent").get("link"), []).append(joint)


def create_link(link_name: str, parent_object: bpy.types.Object, local_matrix: Matrix) -> None:
    link_object = bpy.data.objects.new(f"TEAMON_Ability_Link_{link_name}", None)
    output_collection.objects.link(link_object)
    link_object.parent = parent_object
    link_object.matrix_local = local_matrix
    link_object["urdf_link"] = link_name
    link_object["abt_export"] = True
    link_objects[link_name] = link_object
    link_element = links[link_name]
    for visual_index, visual in enumerate(link_element.findall("visual")):
        mesh_element = visual.find("geometry/mesh")
        if mesh_element is None:
            continue
        mesh_path = (URDF_PATH.parent / mesh_element.get("filename")).resolve()
        template = load_template(mesh_path, source_collection, template_cache)
        visual_name = visual.get("name") or f"visual_{visual_index:02d}"
        obj = bpy.data.objects.new(f"TEAMON_Ability_{link_name}_{visual_name}", template.data)
        output_collection.objects.link(obj)
        obj.parent = link_object
        obj.matrix_local = origin_matrix(visual.find("origin"))
        obj.data.materials.clear()
        obj.data.materials.append(white)
        obj["urdf_link"] = link_name
        obj["source_mesh"] = str(mesh_path)
        obj["abt_export"] = True
        visual_objects.append(obj)
    for child_joint in children_by_parent.get(link_name, []):
        create_link(child_joint.find("child").get("link"), link_object, joint_matrix(child_joint))


create_link("base", hand_root, Matrix.Identity(4))
bpy.context.view_layer.update()

camera = configure_preview(visual_objects)
previews = [
    render_view(camera, visual_objects, "front", Vector((0.0, -1.0, 0.0)), "Z"),
    render_view(camera, visual_objects, "front-3q", Vector((0.8, -1.0, 0.55)), "Z"),
    render_view(camera, visual_objects, "side", Vector((1.0, 0.0, 0.0)), "Z"),
]

qa = scene_qa.audit_scene(object_names=[obj.name for obj in visual_objects], contact_tolerance=0.04, floating_tolerance=0.12)
QA_PATH.parent.mkdir(parents=True, exist_ok=True)
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
report = {
    "stage": "GEOMETRY",
    "target_mode": "HYBRID_HERO",
    "variant": VARIANT,
    "source_urdf": str(URDF_PATH),
    "source_revision": "34c9a9324d3739d976e6de441e56ccefafd0000b",
    "source_license": "MIT",
    "pose": POSE,
    "checkpoint": str(BLEND_PATH),
    "previews": previews,
    "link_count": len(link_objects),
    "visual_mesh_count": len(visual_objects),
    "triangle_count": sum(evaluated_triangles(obj) for obj in visual_objects),
    "bounds": {"min": list(bounds(visual_objects)[0]), "max": list(bounds(visual_objects)[1])},
    "qa_report": str(QA_PATH),
    "acceptance_gate": {
        "one_extended_index": "requires visual review",
        "three_curled_fingers": "requires visual review",
        "thumb_below_palm": "requires visual review",
        "no_parallel_comb": "requires visual review"
    }
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
