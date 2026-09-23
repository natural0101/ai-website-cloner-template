from __future__ import annotations

import json
import os
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(
    os.environ.get(
        "TEAMON_PROJECT_ROOT",
        r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template",
    )
)
VARIANT = os.environ.get("TEAMON_ADA_VARIANT", "d")
SOURCE_BLEND = PROJECT_ROOT / "blender-workbench" / "vendor" / "openbionics-ada-v1.1" / "Ada Right v1.1.blend"
PREVIEW_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / f"teamon_reference_v12_ada_pose_{VARIANT}.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_v12_ada_pose_{VARIANT}_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_v12_ada_pose_{VARIANT}_structural_qa.json"
QA_MODULES = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


SOURCE_NAMES = ["Master - Palm", "0th Thumb", "1st finger", "2nd finger", "3rd finger", "4th finger"]
OUTPUT_NAMES = {
    "Master - Palm": "TEAMON_Ada_Palm",
    "0th Thumb": "TEAMON_Ada_Thumb",
    "1st finger": "TEAMON_Ada_Index",
    "2nd finger": "TEAMON_Ada_Middle",
    "3rd finger": "TEAMON_Ada_Ring",
    "4th finger": "TEAMON_Ada_Little",
}
FINGER_POSES = (
    {
        "TEAMON_Ada_Index": {"angles": (-3.0, -5.0, -4.0), "splay": -1.5},
        "TEAMON_Ada_Middle": {"angles": (15.0, 35.0, 25.0), "splay": -2.0},
        "TEAMON_Ada_Ring": {"angles": (20.0, 42.0, 30.0), "splay": 1.5},
        "TEAMON_Ada_Little": {"angles": (25.0, 48.0, 35.0), "splay": 5.0},
    }
    if VARIANT == "f"
    else {
        "TEAMON_Ada_Index": {"angles": (-3.0, -5.0, -4.0), "splay": -1.5},
        "TEAMON_Ada_Middle": {"angles": (28.0, 68.0, 52.0), "splay": -2.0},
        "TEAMON_Ada_Ring": {"angles": (34.0, 74.0, 58.0), "splay": 1.5},
        "TEAMON_Ada_Little": {"angles": (40.0, 80.0, 64.0), "splay": 5.0},
    }
    if VARIANT == "e"
    else {
        "TEAMON_Ada_Index": {"angles": (-4.0, -7.0, -5.0), "splay": -1.5},
        "TEAMON_Ada_Middle": {"angles": (-24.0, -66.0, -54.0), "splay": -2.0},
        "TEAMON_Ada_Ring": {"angles": (-30.0, -72.0, -60.0), "splay": 1.5},
        "TEAMON_Ada_Little": {"angles": (-38.0, -78.0, -66.0), "splay": 5.0},
    }
)


def clear_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name != bpy.context.scene.collection.name:
            bpy.data.collections.remove(collection)


def append_sources() -> list[bpy.types.Object]:
    with bpy.data.libraries.load(str(SOURCE_BLEND), link=False) as (available, requested):
        missing = sorted(set(SOURCE_NAMES) - set(available.objects))
        if missing:
            raise RuntimeError(f"Missing Ada objects: {missing}")
        requested.objects = SOURCE_NAMES
    objects = [obj for obj in requested.objects if obj is not None]
    source_collection = bpy.data.collections.new("SOURCE_Ada_v1_1")
    bpy.context.scene.collection.children.link(source_collection)
    for obj in objects:
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
        source_collection.objects.link(obj)
        obj.name = f"SOURCE_Ada_{obj.name}"
        obj.hide_render = True
        obj.hide_viewport = True
        obj["source_blend"] = str(SOURCE_BLEND)
        obj["source_revision"] = "2dbf3cc6c5df112066f12c11af1d001e319a766f"
        obj["source_license"] = "CC BY-SA 4.0"
    return objects


def output_copy(source: bpy.types.Object, target_name: str, collection: bpy.types.Collection) -> bpy.types.Object:
    hidden_viewport = source.hide_viewport
    source.hide_viewport = False
    modifier_state = []
    for modifier in source.modifiers:
        modifier_state.append((modifier, modifier.show_viewport, modifier.show_render, getattr(modifier, "levels", None), getattr(modifier, "render_levels", None)))
        if modifier.type == "SUBSURF":
            modifier.show_viewport = True
            modifier.show_render = True
            modifier.levels = 2
            modifier.render_levels = 2
        else:
            modifier.show_viewport = False
            modifier.show_render = False
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = source.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.transform(source.matrix_world)
    for modifier, show_viewport, show_render, levels, render_levels in modifier_state:
        modifier.show_viewport = show_viewport
        modifier.show_render = show_render
        if levels is not None:
            modifier.levels = levels
        if render_levels is not None:
            modifier.render_levels = render_levels
    source.hide_viewport = hidden_viewport
    obj = bpy.data.objects.new(target_name, mesh)
    collection.objects.link(obj)
    obj["semantic_part"] = target_name.removeprefix("TEAMON_Ada_").lower()
    obj["source_object"] = source.name
    obj["abt_export"] = True
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def average_near_axis(mesh: bpy.types.Mesh, original_axis: list[float], threshold: float, band: float, axis: int) -> Vector:
    points = [vertex.co.copy() for vertex, coordinate in zip(mesh.vertices, original_axis) if abs(coordinate - threshold) <= band]
    if not points:
        closest = sorted(zip(mesh.vertices, original_axis), key=lambda item: abs(item[1] - threshold))[:12]
        points = [vertex.co.copy() for vertex, _ in closest]
    center = sum(points, Vector()) / len(points)
    center[axis] = threshold
    return center


def bend_finger(obj: bpy.types.Object, angles: tuple[float, float, float], splay: float) -> list[Vector]:
    mesh = obj.data
    original_y = [vertex.co.y for vertex in mesh.vertices]
    minimum = min(original_y)
    maximum = max(original_y)
    length = maximum - minimum
    band = length * 0.045
    thresholds = [minimum + length * fraction for fraction in (0.19, 0.51, 0.76)]
    for threshold, angle in zip(thresholds, angles):
        pivot = average_near_axis(mesh, original_y, threshold, band, 1)
        for vertex, coordinate in zip(mesh.vertices, original_y):
            weight = smoothstep((coordinate - (threshold - band)) / (band * 2.0))
            if weight <= 0.0:
                continue
            rotation = Quaternion((1.0, 0.0, 0.0), radians(angle) * weight)
            vertex.co = pivot + rotation @ (vertex.co - pivot)
    base = minimum + length * 0.08
    pivot = average_near_axis(mesh, original_y, base, band, 1)
    for vertex, coordinate in zip(mesh.vertices, original_y):
        weight = smoothstep((coordinate - minimum) / (length * 0.22))
        rotation = Quaternion((0.0, 0.0, 1.0), radians(splay) * weight)
        vertex.co = pivot + rotation @ (vertex.co - pivot)
    mesh.update()
    return [
        sum(
            (vertex.co.copy() for vertex, coordinate in zip(mesh.vertices, original_y) if abs(coordinate - threshold) <= band),
            Vector(),
        )
        / max(1, sum(1 for coordinate in original_y if abs(coordinate - threshold) <= band))
        for threshold in thresholds
    ]


def create_joint(name: str, center: Vector, radius: float, collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius, location=(0.0, 0.0, 0.0))
    joint = bpy.context.object
    joint.name = name
    for linked_collection in list(joint.users_collection):
        linked_collection.objects.unlink(joint)
    collection.objects.link(joint)
    joint.data.transform(Matrix.Translation(center))
    for polygon in joint.data.polygons:
        polygon.use_smooth = True
    joint["semantic_part"] = "finger_joint"
    joint["abt_export"] = True
    return joint


def pose_thumb(obj: bpy.types.Object) -> None:
    mesh = obj.data
    original_x = [vertex.co.x for vertex in mesh.vertices]
    minimum = min(original_x)
    maximum = max(original_x)
    length = maximum - minimum
    band = length * 0.06
    pivot = average_near_axis(mesh, original_x, minimum + length * 0.08, band, 0)
    for vertex, coordinate in zip(mesh.vertices, original_x):
        weight = smoothstep((coordinate - minimum) / (length * 0.30))
        point = vertex.co - pivot
        point = Quaternion((0.0, 0.0, 1.0), radians(-22.0) * weight) @ point
        point = Quaternion((0.0, 1.0, 0.0), radians(18.0) * weight) @ point
        vertex.co = pivot + point
    mesh.update()


def make_debug_material() -> bpy.types.Material:
    material = bpy.data.materials.new("TEAMON_Debug_White")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.94, 0.965, 1.0, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.3
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
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.12, 0.004, 0.003, 1.0)
    background.inputs["Strength"].default_value = 0.5
    minimum, maximum = bounds(objects)
    center = (minimum + maximum) * 0.5
    extent = maximum - minimum
    radius = max(extent) * 1.8
    add_area("TEAMON_Preview_Key", center + Vector((radius, -radius, radius * 1.4)), center, 900.0, radius)
    add_area("TEAMON_Preview_Fill", center + Vector((-radius, -radius * 0.2, radius)), center, 550.0, radius * 1.2)
    add_area("TEAMON_Preview_Rim", center + Vector((0.0, radius, radius * 1.2)), center, 800.0, radius)
    camera_data = bpy.data.cameras.new("TEAMON_Preview_Camera")
    camera = bpy.data.objects.new("TEAMON_Preview_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera["abt_export"] = False
    scene.camera = camera
    return camera


def render_view(camera: bpy.types.Object, objects: list[bpy.types.Object], name: str, direction: Vector, up_axis: str) -> str:
    minimum, maximum = bounds(objects)
    center = (minimum + maximum) * 0.5
    extent = maximum - minimum
    distance = max(extent) * 4.0
    camera.location = center + direction.normalized() * distance
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", up_axis).to_euler()
    if name == "hero":
        camera.data.ortho_scale = max(extent.x / (960 / 720), extent.y) * 1.15
    elif name == "side":
        camera.data.ortho_scale = max(extent.z / (960 / 720), extent.y) * 1.18
    else:
        camera.data.ortho_scale = max(extent.x / (960 / 720), extent.y) * 1.15
    path = PREVIEW_DIR / f"teamon-v12-ada-pose-{VARIANT}-{name}.png"
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
sources = append_sources()
output_collection = bpy.data.collections.new("TEAMON_Ada_Pose_OUTPUT")
bpy.context.scene.collection.children.link(output_collection)
source_by_original = {obj.name.removeprefix("SOURCE_Ada_"): obj for obj in sources}
outputs = {
    target_name: output_copy(source_by_original[source_name], target_name, output_collection)
    for source_name, target_name in OUTPUT_NAMES.items()
}

joint_positions = {}
for name, pose in FINGER_POSES.items():
    joint_positions[name] = bend_finger(outputs[name], pose["angles"], pose["splay"])
pose_thumb(outputs["TEAMON_Ada_Thumb"])

joint_objects = []
for finger_name, pivots in joint_positions.items():
    selected_pivots = pivots[:1] if finger_name == "TEAMON_Ada_Index" else pivots
    radius = 5.4 if finger_name != "TEAMON_Ada_Little" else 4.9
    for index, pivot in enumerate(selected_pivots, start=1):
        joint_objects.append(create_joint(f"{finger_name}_Joint{index:02d}", pivot, radius, output_collection))

hand_root = bpy.data.objects.new("TEAMON_Ada_HandRoot", None)
output_collection.objects.link(hand_root)
hand_root["abt_export"] = True
hand_root["pose_variant"] = VARIANT
hand_transform = Matrix.Diagonal((-0.018, 0.018, 0.018, 1.0)) @ Matrix.Rotation(radians(-90.0), 4, "Z")
geometry_objects = list(outputs.values()) + joint_objects
for obj in geometry_objects:
    obj.data.transform(hand_transform)
    obj.parent = hand_root
bpy.context.view_layer.update()

material = make_debug_material()
for obj in geometry_objects:
    obj.data.materials.clear()
    obj.data.materials.append(material)

render_objects = geometry_objects
camera = configure_preview(render_objects)
previews = [
    render_view(camera, render_objects, "hero", Vector((0.2, -0.55, 1.0)), "Y"),
    render_view(camera, render_objects, "front", Vector((0.0, 0.0, 1.0)), "Y"),
    render_view(camera, render_objects, "side", Vector((0.0, -1.0, 0.0)), "Z"),
]

qa = scene_qa.audit_scene(object_names=[obj.name for obj in render_objects], contact_tolerance=0.025, floating_tolerance=0.08)
QA_PATH.parent.mkdir(parents=True, exist_ok=True)
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

report = {
    "stage": "GEOMETRY",
    "target_mode": "HYBRID_HERO",
    "variant": VARIANT,
    "source_blend": str(SOURCE_BLEND),
    "source_revision": "2dbf3cc6c5df112066f12c11af1d001e319a766f",
    "source_license": "CC BY-SA 4.0",
    "checkpoint": str(BLEND_PATH),
    "previews": previews,
    "objects": [
        {
            "name": obj.name,
            "dimensions_world": list(obj.dimensions),
            "triangles_evaluated": evaluated_triangles(obj),
            "parent": obj.parent.name if obj.parent else None,
        }
        for obj in render_objects
    ],
    "triangle_count": sum(evaluated_triangles(obj) for obj in render_objects),
    "qa_report": str(QA_PATH),
    "acceptance_gate": {
        "one_extended_index": "requires visual review",
        "three_curled_fingers": "requires visual review",
        "thumb_below_palm": "requires visual review",
        "no_parallel_comb": "requires visual review",
    },
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
