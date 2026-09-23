"""Build the original TeamON sitting plush teddy, render QA views and export a web GLB.

This script is intentionally self-contained and writes only below blender-workbench.
Run with Blender 5.1+ in an isolated factory-startup/background process.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "teamon_teddy_bear_v1"
WORKBENCH = Path(__file__).resolve().parents[1]
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
TEXTURE_DIR = WORKBENCH / "artifacts" / "textures"
for directory in (RENDER_DIR, EXPORT_DIR, BLEND_DIR, REPORT_DIR, TEXTURE_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def srgb_channel_to_linear(value: float) -> float:
    value /= 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def hex_rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = value.lstrip("#")
    return (
        srgb_channel_to_linear(int(value[0:2], 16)),
        srgb_channel_to_linear(int(value[2:4], 16)),
        srgb_channel_to_linear(int(value[4:6], 16)),
        alpha,
    )


def clear_factory_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    for current in list(obj.users_collection):
        if current != collection:
            current.objects.unlink(obj)


def make_material(
    name: str,
    color: str,
    *,
    roughness: float,
    sheen: float = 0.0,
    metallic: float = 0.0,
    alpha: float = 1.0,
    normal_image: bpy.types.Image | None = None,
    normal_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = hex_rgba(color, alpha)
    material.metallic = metallic
    material.roughness = roughness
    if alpha < 1.0:
        material.surface_render_method = "DITHERED"
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = hex_rgba(color, alpha)
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    if "IOR" in principled.inputs:
        principled.inputs["IOR"].default_value = 1.42
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.28
    if "Sheen Weight" in principled.inputs:
        principled.inputs["Sheen Weight"].default_value = sheen
    if "Sheen Roughness" in principled.inputs:
        principled.inputs["Sheen Roughness"].default_value = 0.88
    if "Alpha" in principled.inputs:
        principled.inputs["Alpha"].default_value = alpha
    if normal_image is not None and normal_strength > 0.0:
        image_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.name = "TeamON_FabricNormal"
        image_node.image = normal_image
        image_node.interpolation = "Linear"
        image_node.extension = "REPEAT"
        normal_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
        normal_node.name = "TeamON_FabricNormalMap"
        normal_node.inputs["Strength"].default_value = normal_strength
        material.node_tree.links.new(image_node.outputs["Color"], normal_node.inputs["Color"])
        material.node_tree.links.new(normal_node.outputs["Normal"], principled.inputs["Normal"])
    return material


def create_fabric_normal_texture(size: int = 384) -> bpy.types.Image:
    """Create a seamless woven normal map that the glTF exporter can embed."""
    image = bpy.data.images.new("TTB_FabricNormal", width=size, height=size, alpha=True, float_buffer=False)
    pixels = [0.0] * (size * size * 4)
    tau = math.tau
    for y in range(size):
        for x in range(size):
            # Two orthogonal thread families plus a finer diagonal fiber.
            dx = (
                0.28 * math.cos(tau * x / 9.0)
                + 0.08 * math.cos(tau * (x + y) / 5.0)
                + 0.035 * math.cos(tau * x / 3.0)
            )
            dy = (
                0.28 * math.cos(tau * y / 9.0)
                + 0.08 * math.cos(tau * (x + y) / 5.0)
                + 0.035 * math.cos(tau * y / 3.0)
            )
            normal = Vector((-dx, -dy, 1.0)).normalized()
            index = (y * size + x) * 4
            pixels[index] = normal.x * 0.5 + 0.5
            pixels[index + 1] = normal.y * 0.5 + 0.5
            pixels[index + 2] = normal.z * 0.5 + 0.5
            pixels[index + 3] = 1.0
    image.pixels.foreach_set(pixels)
    image.colorspace_settings.name = "Non-Color"
    image.filepath_raw = str(TEXTURE_DIR / f"{ASSET}_fabric_normal.png")
    image.file_format = "PNG"
    image.save()
    return image


def set_parent_keep_world(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    bpy.context.view_layer.update()
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world
    bpy.context.view_layer.update()


def shade_smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def add_soft_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    parent: bpy.types.Object | None = None,
    plush_noise: float = 0.0,
    pear: float = 0.0,
    segments: int = 36,
    rings: int = 24,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    if pear:
        for vertex in obj.data.vertices:
            normalized_z = max(-1.0, min(1.0, vertex.co.z))
            factor = 1.0 + pear * (-normalized_z * 0.7 + (1.0 - normalized_z * normalized_z) * 0.25)
            vertex.co.x *= factor
            vertex.co.y *= factor
    obj.scale = scale
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if plush_noise > 0:
        texture = bpy.data.textures.new(f"{name}_MicroPlush", type="CLOUDS")
        texture.noise_scale = 0.18
        texture.noise_depth = 1
        modifier = obj.modifiers.new("MicroPlush", "DISPLACE")
        modifier.texture = texture
        modifier.strength = plush_noise
        modifier.texture_coords = "LOCAL"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    if parent is not None:
        set_parent_keep_world(obj, parent)
    return obj


def add_capsule_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: tuple[float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    plush_noise: float = 0.0,
) -> bpy.types.Object:
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    length = direction.length
    midpoint = (start_v + end_v) * 0.5
    obj = add_soft_ellipsoid(
        name,
        tuple(midpoint),
        (radius[0], radius[1], length * 0.56),
        material,
        collection,
        parent=parent,
        plush_noise=plush_noise,
        segments=32,
        rings=22,
    )
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    obj.select_set(False)
    return obj


def add_curve_mesh(
    name: str,
    points: list[tuple[float, float, float]],
    bevel_depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    resolution: int = 3,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = resolution
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    set_parent_keep_world(obj, parent)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    shade_smooth(obj)
    obj.select_set(False)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    rotation: tuple[float, float, float],
    parent: bpy.types.Object,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=40,
        minor_segments=10,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    set_parent_keep_world(obj, parent)
    return obj


def add_empty(name: str, location: tuple[float, float, float], collection: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.location = location
    collection.objects.link(obj)
    return obj


def add_area_light(name: str, location: tuple[float, float, float], color: str, energy: float, size: float, collection: bpy.types.Collection) -> bpy.types.Object:
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = tuple(component ** (1 / 2.2) for component in hex_rgba(color)[:3])
    obj = bpy.data.objects.new(name, data)
    obj.location = location
    collection.objects.link(obj)
    return obj


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_camera(camera: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], lens: float = 68.0) -> None:
    camera.location = location
    camera.data.lens = lens
    look_at(camera, target)


def render_to(path: Path, camera: bpy.types.Object) -> None:
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners))),
        Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners))),
    )


def aabb_overlap(a: bpy.types.Object, b: bpy.types.Object) -> tuple[float, float, float]:
    a_min, a_max = world_bounds(a)
    b_min, b_max = world_bounds(b)
    return tuple(max(0.0, min(a_max[i], b_max[i]) - max(a_min[i], b_min[i])) for i in range(3))


clear_factory_scene()
scene = bpy.context.scene
scene.name = "TeamON_Teddy_Bear_V1"
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = True
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100
scene.render.pixel_aspect_x = 1.0
scene.render.pixel_aspect_y = 1.0
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world.color = hex_rgba("#F5FCF6")[:3]

export_collection = ensure_collection("TEAMON_TEDDY_EXPORT")
helper_collection = ensure_collection("TEAMON_TEDDY_RENDER_HELPERS")

fabric_normal = create_fabric_normal_texture()
porcelain = make_material("TTB_PorcelainPlush", "#F5FCF6", roughness=0.88, sheen=0.62, normal_image=fabric_normal, normal_strength=0.42)
porcelain_shadow = make_material("TTB_PorcelainShadow", "#DCEBE2", roughness=0.91, sheen=0.54, normal_image=fabric_normal, normal_strength=0.38)
mint = make_material("TTB_MintPlush", "#58D1BD", roughness=0.86, sheen=0.58, normal_image=fabric_normal, normal_strength=0.38)
mint_soft = make_material("TTB_MintSoft", "#BCEBE0", roughness=0.90, sheen=0.60, normal_image=fabric_normal, normal_strength=0.36)
deep_green = make_material("TTB_DeepGreenDetail", "#153D34", roughness=0.46, sheen=0.14)
chartreuse = make_material("TTB_ChartreuseAccent", "#E6F3B5", roughness=0.84, sheen=0.48, normal_image=fabric_normal, normal_strength=0.30)
coral = make_material("TTB_CoralStitch", "#FF9A78", roughness=0.76, sheen=0.30)
highlight = make_material("TTB_EyeHighlight", "#FFFFFF", roughness=0.18, sheen=0.0)
clay = make_material("TTB_QA_Clay", "#B9C8C0", roughness=0.92, sheen=0.15)
shadow_outer = make_material("TTB_ShadowOuter", "#153D34", roughness=1.0, alpha=0.035)
shadow_mid = make_material("TTB_ShadowMid", "#153D34", roughness=1.0, alpha=0.055)
shadow_inner = make_material("TTB_ShadowInner", "#153D34", roughness=1.0, alpha=0.075)

root = add_empty("Bear_Root", (0.0, 0.0, 0.0), export_collection)
body = add_soft_ellipsoid(
    "Bear_Body", (0.0, 0.02, 1.30), (0.79, 0.59, 0.98), porcelain, export_collection,
    parent=root, plush_noise=0.009, pear=0.22,
)
belly = add_soft_ellipsoid(
    "Bear_Belly", (0.0, -0.555, 1.28), (0.49, 0.105, 0.60), porcelain_shadow, export_collection,
    parent=root, plush_noise=0.005, segments=32, rings=22,
)

head_pivot = add_empty("Bear_Head", (0.0, 0.0, 2.06), export_collection)
set_parent_keep_world(head_pivot, root)
head_mesh = add_soft_ellipsoid(
    "Bear_Head_Mesh", (0.0, -0.01, 2.51), (0.88, 0.69, 0.82), porcelain, export_collection,
    parent=head_pivot, plush_noise=0.009, pear=-0.06,
)

for side, suffix in ((-1.0, "L"), (1.0, "R")):
    ear = add_soft_ellipsoid(
        f"Bear_Ear_{suffix}", (side * 0.66, -0.005, 2.99), (0.37, 0.20, 0.39), porcelain,
        export_collection, parent=head_pivot, plush_noise=0.007, segments=32, rings=22,
    )
    add_soft_ellipsoid(
        f"Bear_InnerEar_{suffix}", (side * 0.66, -0.190, 2.99), (0.235, 0.065, 0.250), mint_soft,
        export_collection, parent=head_pivot, plush_noise=0.003, segments=28, rings=20,
    )

muzzle = add_soft_ellipsoid(
    "Bear_Muzzle", (0.0, -0.665, 2.33), (0.545, 0.235, 0.365), chartreuse, export_collection,
    parent=head_pivot, plush_noise=0.006, segments=36, rings=24,
)
nose = add_soft_ellipsoid(
    "Bear_Nose", (0.0, -0.895, 2.405), (0.205, 0.115, 0.145), deep_green, export_collection,
    parent=head_pivot, segments=28, rings=20,
)

eye_bases: list[bpy.types.Object] = []
pupils: list[bpy.types.Object] = []
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    eye = add_soft_ellipsoid(
        f"Bear_Eye_{suffix}", (side * 0.315, -0.655, 2.590), (0.155, 0.075, 0.175), mint_soft,
        export_collection, parent=head_pivot, segments=32, rings=22,
    )
    pupil = add_soft_ellipsoid(
        f"Bear_Pupil_{suffix}", (side * 0.315, -0.727, 2.590), (0.082, 0.050, 0.097), deep_green,
        export_collection, parent=head_pivot, segments=28, rings=20,
    )
    add_soft_ellipsoid(
        f"Bear_EyeHighlight_{suffix}", (side * 0.288, -0.774, 2.633), (0.024, 0.018, 0.027), highlight,
        export_collection, parent=head_pivot, segments=20, rings=14,
    )
    eye_bases.append(eye)
    pupils.append(pupil)

mouth_stem = add_curve_mesh(
    "Bear_MouthStem", [(0.0, -0.907, 2.34), (0.0, -0.925, 2.245), (0.0, -0.920, 2.205)],
    0.018, deep_green, export_collection, parent=head_pivot,
)
mouth_l = add_curve_mesh(
    "Bear_Mouth_L", [(0.0, -0.920, 2.205), (-0.12, -0.915, 2.145), (-0.26, -0.860, 2.185)],
    0.016, deep_green, export_collection, parent=head_pivot,
)
mouth_r = add_curve_mesh(
    "Bear_Mouth_R", [(0.0, -0.920, 2.205), (0.12, -0.915, 2.145), (0.26, -0.860, 2.185)],
    0.016, deep_green, export_collection, parent=head_pivot,
)

left_arm = add_capsule_between(
    "Bear_Arm_L", (-0.63, -0.02, 1.78), (-0.43, -0.63, 0.92), (0.285, 0.245),
    porcelain, export_collection, parent=root, plush_noise=0.007,
)
right_arm = add_capsule_between(
    "Bear_Arm_R", (0.63, -0.02, 1.78), (0.43, -0.63, 0.92), (0.285, 0.245),
    porcelain, export_collection, parent=root, plush_noise=0.007,
)
add_soft_ellipsoid(
    "Bear_Paw_L", (-0.43, -0.64, 0.91), (0.31, 0.25, 0.34), porcelain, export_collection,
    parent=root, plush_noise=0.006, segments=32, rings=22,
)
add_soft_ellipsoid(
    "Bear_Paw_R", (0.43, -0.64, 0.91), (0.31, 0.25, 0.34), porcelain, export_collection,
    parent=root, plush_noise=0.006, segments=32, rings=22,
)

legs: list[bpy.types.Object] = []
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    leg = add_soft_ellipsoid(
        f"Bear_Leg_{suffix}", (side * 0.62, -0.06, 0.69), (0.61, 0.61, 0.56), porcelain,
        export_collection, parent=root, plush_noise=0.009, pear=0.04,
    )
    foot = add_soft_ellipsoid(
        f"Bear_Foot_{suffix}", (side * 0.64, -0.66, 0.47), (0.58, 0.40, 0.48), porcelain,
        export_collection, parent=root, plush_noise=0.008,
    )
    pad = add_soft_ellipsoid(
        f"Bear_PawPad_{suffix}", (side * 0.64, -1.015, 0.49), (0.395, 0.075, 0.315), mint,
        export_collection, parent=root, plush_noise=0.004, segments=32, rings=22,
    )
    legs.append(leg)
    stitch_x = side * 0.64
    for offset in (-0.11, 0.0, 0.11):
        add_curve_mesh(
            f"Bear_ToeStitch_{suffix}_{offset:+.2f}",
            [(stitch_x + offset - 0.018, -1.087, 0.61), (stitch_x + offset, -1.094, 0.665)],
            0.010, deep_green, export_collection, parent=root, resolution=2,
        )

badge = add_soft_ellipsoid(
    "Bear_Badge", (0.0, -0.622, 1.585), (0.235, 0.055, 0.235), chartreuse, export_collection,
    parent=root, segments=32, rings=20,
)
badge_ring = add_torus(
    "Bear_BadgeRing", (0.0, -0.680, 1.585), 0.155, 0.026, deep_green, export_collection,
    rotation=(math.radians(90), 0.0, 0.0), parent=root,
)
badge_mark = add_curve_mesh(
    "Bear_BadgeMark", [(-0.075, -0.710, 1.585), (-0.010, -0.717, 1.520), (0.105, -0.700, 1.665)],
    0.018, coral, export_collection, parent=root,
)

body_seam = add_curve_mesh(
    "Bear_BodySeam", [(0.0, -0.612, 1.11), (0.0, -0.640, 0.93), (0.0, -0.590, 0.75)],
    0.010, coral, export_collection, parent=root, resolution=2,
)

# Render-only contact shadow: three nested transparent ellipsoids, never exported.
for name, scale, material in (
    ("Shadow_Outer", (1.50, 0.82, 0.030), shadow_outer),
    ("Shadow_Mid", (1.22, 0.64, 0.025), shadow_mid),
    ("Shadow_Inner", (0.90, 0.46, 0.020), shadow_inner),
):
    add_soft_ellipsoid(name, (0.0, -0.08, 0.025), scale, material, helper_collection, segments=48, rings=16)

camera_data = bpy.data.cameras.new("TTB_RenderCamera")
camera = bpy.data.objects.new("TTB_RenderCamera", camera_data)
helper_collection.objects.link(camera)
camera.data.lens = 68.0
camera.data.sensor_width = 36.0

key = add_area_light("TTB_Key", (-4.6, -5.6, 7.0), "#FFF4E6", 970.0, 4.2, helper_collection)
fill = add_area_light("TTB_Fill", (4.6, -3.6, 4.5), "#B8F2E5", 720.0, 3.7, helper_collection)
rim = add_area_light("TTB_Rim", (3.0, 3.8, 6.6), "#E6F3B5", 1120.0, 3.4, helper_collection)
coral_lift = add_area_light("TTB_CoralLift", (-3.6, 1.0, 2.3), "#FF9A78", 250.0, 2.5, helper_collection)
for light in (key, fill, rim, coral_lift):
    look_at(light, (0.0, 0.0, 1.45))

export_objects = descendants(root)
original_materials: dict[str, list[bpy.types.Material]] = {}
for obj in export_objects:
    if obj.type == "MESH":
        original_materials[obj.name] = list(obj.data.materials)
        obj.data.materials.clear()
        obj.data.materials.append(clay)

set_camera(camera, (0.0, -8.5, 3.05), (0.0, -0.05, 1.53), 72.0)
render_to(RENDER_DIR / f"{ASSET}_01_geometry_front.png", camera)

for obj in export_objects:
    if obj.type == "MESH":
        obj.data.materials.clear()
        for material in original_materials[obj.name]:
            obj.data.materials.append(material)

set_camera(camera, (0.0, -8.5, 3.05), (0.0, -0.05, 1.53), 72.0)
render_to(RENDER_DIR / f"{ASSET}_02_material_front.png", camera)
set_camera(camera, (4.4, -8.0, 3.55), (0.0, -0.05, 1.50), 72.0)
render_to(RENDER_DIR / f"{ASSET}_03_front_3q.png", camera)
set_camera(camera, (8.9, -0.8, 3.35), (0.0, -0.05, 1.45), 72.0)
render_to(RENDER_DIR / f"{ASSET}_04_side.png", camera)
set_camera(camera, (4.1, -8.2, 3.48), (0.0, -0.06, 1.50), 72.0)
render_to(RENDER_DIR / f"{ASSET}_fallback.png", camera)

blend_path = BLEND_DIR / f"{ASSET}.blend"
fabric_normal.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_render = False
    obj.hide_viewport = False
    obj.select_set(True)
bpy.context.view_layer.objects.active = root

glb_path = EXPORT_DIR / f"{ASSET}.glb"
bpy.ops.export_scene.gltf(
    filepath=str(glb_path),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

triangle_count = 0
mesh_objects: list[dict[str, object]] = []
for obj in export_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangles = sum(max(0, len(polygon.vertices) - 2) for polygon in mesh.polygons)
    triangle_count += triangles
    bounds_min, bounds_max = world_bounds(obj)
    mesh_objects.append({
        "name": obj.name,
        "triangles": triangles,
        "bounds_min": [round(value, 4) for value in bounds_min],
        "bounds_max": [round(value, 4) for value in bounds_max],
    })
    evaluated.to_mesh_clear()

contact_pairs = [
    ("Bear_Head_Mesh", "Bear_Body"),
    ("Bear_Ear_L", "Bear_Head_Mesh"),
    ("Bear_Ear_R", "Bear_Head_Mesh"),
    ("Bear_Arm_L", "Bear_Body"),
    ("Bear_Arm_R", "Bear_Body"),
    ("Bear_Leg_L", "Bear_Body"),
    ("Bear_Leg_R", "Bear_Body"),
]
contacts: list[dict[str, object]] = []
contact_warnings: list[str] = []
for a_name, b_name in contact_pairs:
    overlap = aabb_overlap(bpy.data.objects[a_name], bpy.data.objects[b_name])
    passes = sum(1 for value in overlap if value > 0.0) == 3
    contacts.append({"a": a_name, "b": b_name, "aabb_overlap": [round(value, 4) for value in overlap], "passes": passes})
    if not passes:
        contact_warnings.append(f"Expected overlap missing: {a_name} / {b_name}")

errors: list[str] = []
warnings = list(contact_warnings)
if triangle_count > 60_000:
    warnings.append(f"Triangle count {triangle_count} exceeds preferred 60000 target")
if not glb_path.exists() or glb_path.stat().st_size == 0:
    errors.append("GLB export missing or empty")
if glb_path.exists() and glb_path.stat().st_size > 3_000_000:
    warnings.append(f"GLB size {glb_path.stat().st_size} exceeds preferred 3000000-byte target")

report = {
    "asset": ASSET,
    "blender_version": ".".join(map(str, bpy.app.version)),
    "mode": ["organic object", "icon/hero object", "GLB export"],
    "target_representation": "TRUE_360",
    "triangles": triangle_count,
    "mesh_objects": mesh_objects,
    "exportable_objects": len(export_objects),
    "materials": sorted({material.name for obj in export_objects if obj.type == "MESH" for material in obj.data.materials}),
    "required_nodes": ["Bear_Root", "Bear_Head", "Bear_Pupil_L", "Bear_Pupil_R"],
    "contacts": contacts,
    "outputs": {
        "blend": str(blend_path),
        "glb": str(glb_path),
        "glb_bytes": glb_path.stat().st_size if glb_path.exists() else 0,
        "fallback": str(RENDER_DIR / f"{ASSET}_fallback.png"),
    },
    "validation": {"errors": errors, "warnings": warnings},
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps({"asset": ASSET, "contacts": contacts, "errors": errors, "warnings": contact_warnings}, indent=2),
    encoding="utf-8",
)
print("TEAMON_TEDDY_REPORT=" + json.dumps(report))
