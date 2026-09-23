from __future__ import annotations

from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HAND_NAMES = ["0th Thumb", "1st finger", "2nd finger", "3rd finger", "4th finger", "5th Palm"]
HAND_OBJECTS = [bpy.data.objects[name] for name in HAND_NAMES]


def make_material() -> bpy.types.Material:
    material = bpy.data.materials.new("Ada_Source_White")
    material.diffuse_color = (0.92, 0.94, 0.97, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.92, 0.94, 0.97, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.28
    return material


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def add_area(name: str, location: tuple[float, float, float], energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    target = Vector((0.0, 20.0, 10.0))
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()


def render_view(name: str, direction: Vector, up_axis: str = "Y") -> None:
    bounds_min, bounds_max = world_bounds(HAND_OBJECTS)
    center = (bounds_min + bounds_max) * 0.5
    extent = bounds_max - bounds_min
    distance = max(extent) * 3.0
    camera.location = center + direction.normalized() * distance
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", up_axis).to_euler()
    camera.data.type = "ORTHO"
    if name == "front":
        camera.data.ortho_scale = max(extent.x / (900 / 720), extent.y) * 1.16
    elif name == "side":
        camera.data.ortho_scale = max(extent.z / (900 / 720), extent.y) * 1.18
    else:
        camera.data.ortho_scale = max(extent.x / (900 / 720), extent.y) * 1.22
    bpy.context.scene.render.filepath = str(OUTPUT_DIR / f"ada-v1-source-{name}.png")
    bpy.ops.render.render(write_still=True)


white = make_material()
for obj in bpy.data.objects:
    obj.hide_render = obj not in HAND_OBJECTS
for obj in HAND_OBJECTS:
    obj.hide_render = False
    if obj.type == "MESH":
        obj.data.materials.clear()
        obj.data.materials.append(white)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.world.use_nodes = True
world_background = scene.world.node_tree.nodes.get("Background")
world_background.inputs["Color"].default_value = (0.08, 0.003, 0.003, 1.0)
world_background.inputs["Strength"].default_value = 0.55
scene.view_settings.look = "Medium High Contrast"

camera_data = bpy.data.cameras.new("Ada_Source_Camera")
camera = bpy.data.objects.new("Ada_Source_Camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera

add_area("Ada_Key", (130.0, -120.0, 210.0), 70000.0, 140.0)
add_area("Ada_Fill", (-150.0, 20.0, 120.0), 40000.0, 160.0)
add_area("Ada_Rim", (20.0, 150.0, 170.0), 60000.0, 120.0)

render_view("front", Vector((0.0, 0.0, 1.0)), "Y")
render_view("front-3q", Vector((0.8, -0.65, 1.0)), "Y")
render_view("side", Vector((1.0, 0.0, 0.0)), "Z")
