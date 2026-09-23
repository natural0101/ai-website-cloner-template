"""Build a genuine volumetric orange companion cat from the turnaround sheet.

This branch is TRUE_360 geometry.  The reference image is never loaded into
Blender: there are no image planes, projected textures, camera cards or relief
meshes.  Every visible feature is modeled as editable geometry or a procedural
material, and the same object is rendered from front, three-quarter and side.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v3_true3d"
WORKBENCH = Path(__file__).resolve().parents[1]
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
REFERENCE_DIR = WORKBENCH / "references"
for directory in (RENDER_DIR, EXPORT_DIR, BLEND_DIR, REPORT_DIR):
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
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
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


def set_parent_keep_world(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    bpy.context.view_layer.update()
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def shade_smooth(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def make_material(
    name: str,
    color: str,
    *,
    roughness: float = 0.8,
    sheen: float = 0.0,
    metallic: float = 0.0,
    fur_bump: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = hex_rgba(color)
    material.roughness = roughness
    material.metallic = metallic
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = hex_rgba(color)
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    if "IOR" in principled.inputs:
        principled.inputs["IOR"].default_value = 1.40
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.30
    if "Sheen Weight" in principled.inputs:
        principled.inputs["Sheen Weight"].default_value = sheen
    if fur_bump > 0.0:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 22.0
        noise.inputs["Detail"].default_value = 5.0
        noise.inputs["Roughness"].default_value = 0.72
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = fur_bump
        bump.inputs["Distance"].default_value = 0.035
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def add_ellipsoid(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object | None = None,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    noise: float = 0.0,
    pear: float = 0.0,
    segments: int = 40,
    rings: int = 28,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    if pear:
        for vertex in obj.data.vertices:
            z = max(-1.0, min(1.0, vertex.co.z))
            factor = 1.0 + pear * (-0.72 * z + 0.22 * (1.0 - z * z))
            vertex.co.x *= factor
            vertex.co.y *= factor
    obj.scale = scale
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if noise > 0.0:
        texture = bpy.data.textures.new(f"{name}_FurNoise", type="CLOUDS")
        texture.noise_scale = 0.14
        texture.noise_depth = 2
        modifier = obj.modifiers.new("FurSurface", "DISPLACE")
        modifier.texture = texture
        modifier.strength = noise
        modifier.texture_coords = "LOCAL"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    if parent is not None:
        set_parent_keep_world(obj, parent)
    return obj


def add_sculpted_cat_head(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    """Create a cheek-led feline skull instead of a uniformly scaled sphere."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=40, location=location)
    obj = bpy.context.object
    obj.name = name
    for vertex in obj.data.vertices:
        x, y, z = vertex.co
        cheek = math.exp(-((z + 0.20) / 0.34) ** 2)
        chin = max(0.0, -z - 0.34)
        crown = max(0.0, z - 0.48)
        vertex.co.x *= 1.0 + 0.17 * cheek - 0.20 * chin - 0.08 * crown
        vertex.co.y *= 0.96 + 0.05 * cheek
        if y < -0.15:
            vertex.co.y -= 0.025 * cheek
        vertex.co.z -= 0.035 * cheek
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    set_parent_keep_world(obj, parent)
    return obj


def add_surface_fur(
    name: str,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    strand_count: int,
    length_range: tuple[float, float],
    seed: int,
    face_clearance: bool = False,
    bevel_depth: float = 0.004,
) -> bpy.types.Object:
    """Add real tapered strand geometry distributed on an ellipsoid."""
    rng = random.Random(seed)
    curve_data = bpy.data.curves.new(name=f"{name}_Curves", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 1
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 1
    curve_data.resolution_v = 0
    curve_data.use_fill_caps = True
    accepted = 0
    attempts = 0
    center_v = Vector(center)
    while accepted < strand_count and attempts < strand_count * 12:
        attempts += 1
        z = rng.uniform(-0.95, 0.98)
        phi = rng.uniform(0.0, math.tau)
        radial = math.sqrt(max(0.0, 1.0 - z * z))
        unit = Vector((radial * math.cos(phi), radial * math.sin(phi), z))
        if face_clearance and unit.y < -0.24 and abs(unit.x) < 0.66 and -0.60 < unit.z < 0.46:
            continue
        base = center_v + Vector((unit.x * radii[0], unit.y * radii[1], unit.z * radii[2]))
        normal = Vector(
            (
                unit.x / max(radii[0], 0.001),
                unit.y / max(radii[1], 0.001),
                unit.z / max(radii[2], 0.001),
            )
        ).normalized()
        tangent = normal.cross(Vector((0.0, 0.0, 1.0)))
        if tangent.length < 0.01:
            tangent = Vector((1.0, 0.0, 0.0))
        tangent.normalize()
        strand_length = rng.uniform(*length_range)
        bend = tangent * rng.uniform(-0.014, 0.014)
        mid = base + normal * (strand_length * 0.56) + bend
        tip = base + normal * strand_length + bend * 0.55 + Vector((0.0, 0.0, -0.008))
        spline = curve_data.splines.new("POLY")
        spline.points.add(2)
        for point, coordinate, radius in zip(
            spline.points,
            (base, mid, tip),
            (1.0, 0.62, 0.04),
            strict=True,
        ):
            point.co = (*coordinate, 1.0)
            point.radius = radius
        accepted += 1
    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    set_parent_keep_world(obj, parent)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    shade_smooth(obj)
    obj.select_set(False)
    return obj


def add_capsule(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radii: tuple[float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    noise: float = 0.0,
) -> bpy.types.Object:
    start_v = Vector(start)
    end_v = Vector(end)
    direction = end_v - start_v
    length = direction.length
    obj = add_ellipsoid(
        name,
        tuple((start_v + end_v) * 0.5),
        (radii[0], radii[1], length * 0.57),
        material,
        collection,
        parent=parent,
        noise=noise,
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


def add_curve(
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


def add_fur_outline(
    name: str,
    center: tuple[float, float, float],
    radii_xz: tuple[float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    count: int = 72,
    strand_length: float = 0.075,
    bevel_depth: float = 0.006,
) -> bpy.types.Object:
    """Create one lightweight curve object containing a soft fur silhouette."""
    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 1
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 2
    cx, cy, cz = center
    rx, rz = radii_xz
    for index in range(count):
        angle_jitter = 0.32 * math.sin(index * 17.173) / count
        angle = math.tau * (index / count + angle_jitter)
        # Leave small gaps where the two large ears already define the crown.
        top_factor = math.sin(angle)
        if top_factor > 0.72 and abs(math.cos(angle)) > 0.28:
            continue
        nx = math.cos(angle)
        nz = math.sin(angle)
        jitter = 0.58 + 0.66 * (0.5 + 0.5 * math.sin(index * 12.9898))
        base = (cx + rx * nx, cy, cz + rz * nz)
        tangent_x = -nz
        tangent_z = nx
        sideways = strand_length * 0.18 * math.sin(index * 9.71)
        mid = (
            base[0] + nx * strand_length * jitter * 0.55 + tangent_x * sideways,
            cy - 0.004,
            base[2] + nz * strand_length * jitter * 0.55 + tangent_z * sideways - 0.004,
        )
        tip = (
            base[0] + nx * strand_length * jitter + tangent_x * sideways * 0.45,
            cy - 0.007,
            base[2] + nz * strand_length * jitter + tangent_z * sideways * 0.45 - 0.008,
        )
        spline = curve_data.splines.new("POLY")
        spline.points.add(2)
        for point, coordinate, radius in zip(
            spline.points,
            (base, mid, tip),
            (1.0, 0.58, 0.03),
            strict=True,
        ):
            point.co = (*coordinate, 1.0)
            point.radius = radius
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


def add_beveled_cube(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.12,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    modifier = obj.modifiers.new("SoftEdges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 4
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    set_parent_keep_world(obj, parent)
    return obj


def add_extruded_polygon(
    name: str,
    points_xz: list[tuple[float, float]],
    y_front: float,
    thickness: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    bevel: float = 0.035,
) -> bpy.types.Object:
    """Create a shallow editable garment panel from a front-view outline."""
    y_back = y_front + thickness
    vertices = [(x, y_front, z) for x, z in points_xz] + [(x, y_back, z) for x, z in points_xz]
    count = len(points_xz)
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(range(count)))
    faces.append(tuple(range(count, count * 2))[::-1])
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    bevel_modifier = obj.modifiers.new("SoftClothEdge", "BEVEL")
    bevel_modifier.width = bevel
    bevel_modifier.segments = 3
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel_modifier.name)
    shade_smooth(obj)
    set_parent_keep_world(obj, parent)
    obj.select_set(False)
    return obj


def add_soft_scarf_panel(
    name: str,
    *,
    top_z: float,
    bottom_z: float,
    width_top: float,
    width_bottom: float,
    y_front: float,
    thickness: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    """Build a softly curved scarf fold with actual front, back and side volume."""
    columns = 16
    rows = 6
    front_vertices: list[tuple[float, float, float]] = []
    for row in range(rows):
        t = row / (rows - 1)
        width = width_top * (1.0 - t) + width_bottom * t
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            edge_lift = 0.11 * abs(u) * t
            fold = 0.028 * math.sin((u + 0.15) * math.pi * 2.0) * math.sin(math.pi * t)
            z = top_z * (1.0 - t) + bottom_z * t + edge_lift + fold
            bulge = 0.072 * (1.0 - u * u) * math.sin(math.pi * t)
            front_vertices.append((u * width, y_front - bulge, z))
    count = len(front_vertices)
    vertices = front_vertices + [(x, y + thickness, z) for x, y, z in front_vertices]
    faces: list[tuple[int, ...]] = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            a = row * columns + column
            b = a + 1
            c = a + columns + 1
            d = a + columns
            faces.append((a, d, c, b))
            faces.append((count + a, count + b, count + c, count + d))
    perimeter: list[int] = []
    perimeter.extend(range(columns))
    perimeter.extend(row * columns + columns - 1 for row in range(1, rows))
    perimeter.extend(range((rows - 1) * columns + columns - 2, (rows - 1) * columns - 1, -1))
    perimeter.extend(row * columns for row in range(rows - 2, 0, -1))
    for index, a in enumerate(perimeter):
        b = perimeter[(index + 1) % len(perimeter)]
        faces.append((a, b, count + b, count + a))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    subdivision = obj.modifiers.new("SoftClothSubdivision", "SUBSURF")
    subdivision.levels = 1
    subdivision.render_levels = 1
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=subdivision.name)
    shade_smooth(obj)
    set_parent_keep_world(obj, parent)
    obj.select_set(False)
    return obj


def add_triangular_prism(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=3,
        radius1=1.0,
        radius2=0.0,
        depth=2.0,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bevel = obj.modifiers.new("SoftTip", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.data.materials.append(material)
    shade_smooth(obj)
    move_to_collection(obj, collection)
    set_parent_keep_world(obj, parent)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    parent: bpy.types.Object,
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=48,
        minor_segments=12,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
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


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    color: str,
    energy: float,
    size: float,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
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


def set_camera(
    camera: bpy.types.Object,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
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
scene.name = "Comforting_Cat_V2"
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.film_transparent = False
scene.render.pixel_aspect_x = 1.0
scene.render.pixel_aspect_y = 1.0
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world.color = hex_rgba("#938B7E")[:3]
scene.world.use_nodes = True
world_background = scene.world.node_tree.nodes.get("Background")
world_background.inputs["Color"].default_value = hex_rgba("#938B7E")
world_background.inputs["Strength"].default_value = 0.72

export_collection = ensure_collection("COMFORTING_CAT_EXPORT")
helper_collection = ensure_collection("COMFORTING_CAT_RENDER_HELPERS")

fur_orange = make_material("CAT_GoldenOrangeFur", "#A75A20", roughness=0.94, sheen=0.58, fur_bump=0.22)
fur_light = make_material("CAT_CreamFur", "#D3AD76", roughness=0.95, sheen=0.60, fur_bump=0.20)
fur_dark = make_material("CAT_DarkOrangeFur", "#79411D", roughness=0.93, sheen=0.48, fur_bump=0.17)
inner_ear = make_material("CAT_InnerEarPink", "#D98F7E", roughness=0.86, sheen=0.25)
blue = make_material("CAT_WeatheredBlueCloth", "#203844", roughness=0.97, sheen=0.68, fur_bump=0.12)
blue_light = make_material("CAT_BlueClothHighlight", "#34515D", roughness=0.96, sheen=0.62, fur_bump=0.10)
linen = make_material("CAT_WarmLinenTunic", "#777E7B", roughness=0.96, sheen=0.44, fur_bump=0.07)
brown = make_material("CAT_SatchelLeather", "#432A18", roughness=0.72, sheen=0.12)
brown_light = make_material("CAT_SatchelEdge", "#76502D", roughness=0.76, sheen=0.10)
eye_white = make_material("CAT_EyeDarkGlass", "#23160F", roughness=0.20)
iris = make_material("CAT_IrisWarmBrown", "#2D1D13", roughness=0.22)
pupil = make_material("CAT_Pupil", "#090706", roughness=0.16)
highlight = make_material("CAT_EyeHighlight", "#FFF9E8", roughness=0.12)
line = make_material("CAT_LineDark", "#3B2618", roughness=0.72)
whisker = make_material("CAT_WhiskerWarm", "#D9BC8D", roughness=0.84)
clay = make_material("CAT_QAClay", "#B8A68B", roughness=0.96)
ground_mat = make_material("CAT_Backdrop", "#71695D", roughness=1.0)

root = add_empty("Cat_Root", (0.0, 0.0, 0.0), export_collection)

# GEOMETRY: large masses first. Front points toward negative Y.
body = add_ellipsoid(
    "Cat_Body",
    (0.0, 0.03, 1.46),
    (0.70, 0.47, 1.00),
    fur_orange,
    export_collection,
    parent=root,
    noise=0.010,
    pear=0.22,
)

# Tail stays behind the robe and exits to camera-right as one continuous form.
tail_a = add_curve(
    "Cat_Tail_Base",
    [
        (0.43, 0.18, 0.66),
        (0.67, 0.20, 0.37),
        (0.96, 0.16, 0.25),
        (1.18, 0.10, 0.29),
    ],
    0.19,
    fur_orange,
    export_collection,
    parent=root,
    resolution=4,
)
tail_tip = add_ellipsoid(
    "Cat_Tail_CreamTip",
    (1.23, 0.09, 0.30),
    (0.18, 0.155, 0.16),
    fur_light,
    export_collection,
    parent=root,
    noise=0.008,
    rotation=(0.0, 0.18, 0.0),
)

# Blue robe and its lighter front inset.
bpy.ops.mesh.primitive_cone_add(
    vertices=48,
    radius1=1.0,
    radius2=0.76,
    depth=2.0,
    location=(0.0, 0.0, 1.45),
)
robe = bpy.context.object
robe.name = "Cat_BlueRobe"
robe.scale = (0.77, 0.50, 0.88)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
robe.data.materials.append(blue)
shade_smooth(robe)
move_to_collection(robe, export_collection)
set_parent_keep_world(robe, root)
add_extruded_polygon(
    "Cat_RobeFrontInset",
    [(-0.35, 1.98), (0.35, 1.98), (0.33, 0.82), (0.12, 0.72), (-0.12, 0.72), (-0.33, 0.82)],
    -0.57,
    0.09,
    linen,
    export_collection,
    parent=root,
    bevel=0.055,
)

head_pivot = add_empty("Cat_Head", (0.0, 0.0, 2.42), export_collection)
set_parent_keep_world(head_pivot, root)
head = add_sculpted_cat_head(
    "Cat_Head_Mesh",
    (0.0, -0.03, 3.08),
    (0.78, 0.64, 0.64),
    fur_orange,
    export_collection,
    parent=head_pivot,
)
add_surface_fur(
    "Cat_Head_FurStrands",
    (0.0, -0.03, 3.08),
    (0.79, 0.65, 0.65),
    fur_orange,
    export_collection,
    parent=head_pivot,
    strand_count=1300,
    length_range=(0.015, 0.034),
    seed=731,
    face_clearance=True,
    bevel_depth=0.0016,
)

for side, suffix in ((-1.0, "L"), (1.0, "R")):
    add_triangular_prism(
        f"Cat_Ear_{suffix}",
        (side * 0.57, -0.01, 3.65),
        (0.34, 0.22, 0.50),
        fur_orange,
        export_collection,
        parent=head_pivot,
        rotation=(0.0, side * -0.11, 0.0),
    )
    add_triangular_prism(
        f"Cat_InnerEar_{suffix}",
        (side * 0.57, -0.130, 3.64),
        (0.22, 0.025, 0.33),
        inner_ear,
        export_collection,
        parent=head_pivot,
        rotation=(0.0, side * -0.11, 0.0),
    )

# Two compact cream muzzle puffs.
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    add_ellipsoid(
        f"Cat_Muzzle_{suffix}",
        (side * 0.140, -0.686, 2.86),
        (0.195, 0.120, 0.155),
        fur_light,
        export_collection,
        parent=head_pivot,
        noise=0.006,
    )

# Large low-set eyes and worried brows from the concept turnaround.
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    add_ellipsoid(
        f"Cat_Eye_{suffix}",
        (side * 0.270, -0.660, 3.17),
        (0.112, 0.035, 0.145),
        eye_white,
        export_collection,
        parent=head_pivot,
    )
    add_ellipsoid(
        f"Cat_Iris_{suffix}",
        (side * 0.270, -0.692, 3.16),
        (0.084, 0.020, 0.108),
        iris,
        export_collection,
        parent=head_pivot,
    )
    add_ellipsoid(
        f"Cat_Pupil_{suffix}",
        (side * 0.270, -0.714, 3.16),
        (0.044, 0.012, 0.080),
        pupil,
        export_collection,
        parent=head_pivot,
    )
    add_ellipsoid(
        f"Cat_EyeHighlight_{suffix}",
        (side * 0.250, -0.730, 3.215),
        (0.020, 0.007, 0.024),
        highlight,
        export_collection,
        parent=head_pivot,
        segments=20,
        rings=14,
    )
    eyebrow_points = (
        [
            (side * 0.43, -0.674, 3.43),
            (side * 0.31, -0.704, 3.50),
            (side * 0.17, -0.685, 3.45),
        ]
        if side < 0
        else [
            (side * 0.17, -0.685, 3.45),
            (side * 0.31, -0.704, 3.50),
            (side * 0.43, -0.674, 3.43),
        ]
    )
    add_curve(
        f"Cat_Eyebrow_{suffix}",
        eyebrow_points,
        0.014,
        fur_dark,
        export_collection,
        parent=head_pivot,
        resolution=2,
    )

# Three subtle forehead markings are modeled curves, not painted pixels.
for index, points in enumerate(
    (
        [(-0.14, -0.39, 3.62), (-0.11, -0.47, 3.54)],
        [(0.0, -0.37, 3.65), (0.0, -0.49, 3.54)],
        [(0.14, -0.39, 3.62), (0.11, -0.47, 3.54)],
    )
):
    add_curve(
        f"Cat_ForeheadStripe_{index}",
        points,
        0.008,
        fur_dark,
        export_collection,
        parent=head_pivot,
        resolution=2,
    )

nose = add_ellipsoid(
    "Cat_Nose",
    (0.0, -0.842, 2.93),
    (0.082, 0.045, 0.060),
    inner_ear,
    export_collection,
    parent=head_pivot,
    rotation=(0.0, 0.0, math.pi / 4.0),
    segments=28,
    rings=18,
)
add_curve(
    "Cat_MouthStem",
    [(0.0, -0.866, 2.89), (0.0, -0.875, 2.84)],
    0.010,
    line,
    export_collection,
    parent=head_pivot,
    resolution=2,
)
add_curve(
    "Cat_Mouth_L",
    [(0.0, -0.875, 2.84), (-0.055, -0.870, 2.80), (-0.12, -0.850, 2.82)],
    0.010,
    line,
    export_collection,
    parent=head_pivot,
    resolution=2,
)
add_curve(
    "Cat_Mouth_R",
    [(0.0, -0.875, 2.84), (0.055, -0.870, 2.80), (0.12, -0.850, 2.82)],
    0.010,
    line,
    export_collection,
    parent=head_pivot,
    resolution=2,
)

# Fine whiskers are separate curves so they remain editable.
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    for index, z_offset in enumerate((-0.10, 0.0, 0.10)):
        add_curve(
            f"Cat_Whisker_{suffix}_{index}",
            [
                (side * 0.27, -0.785, 2.86 + z_offset * 0.75),
                (side * 0.53, -0.820, 2.87 + z_offset),
                (side * 0.78, -0.770, 2.91 + z_offset * 1.25),
            ],
            0.003,
            whisker,
            export_collection,
            parent=head_pivot,
            resolution=2,
        )

# Scarf/cowl sits at the head-body junction and overlaps both.
add_torus(
    "Cat_ScarfWrap",
    (0.0, -0.01, 2.38),
    0.55,
    0.12,
    blue,
    export_collection,
    parent=root,
    scale=(1.0, 0.80, 0.78),
)
add_soft_scarf_panel(
    "Cat_ScarfUpperFold",
    top_z=2.44,
    bottom_z=2.16,
    width_top=0.59,
    width_bottom=0.50,
    y_front=-0.63,
    thickness=0.12,
    material=blue,
    collection=export_collection,
    parent=root,
)
add_soft_scarf_panel(
    "Cat_ScarfLowerDrape",
    top_z=2.31,
    bottom_z=2.00,
    width_top=0.55,
    width_bottom=0.44,
    y_front=-0.67,
    thickness=0.10,
    material=blue_light,
    collection=export_collection,
    parent=root,
)
# Slender short arms and compact paws from the turnaround target.
add_ellipsoid(
    "Cat_LowerBellyBridge",
    (0.0, -0.05, 0.53),
    (0.34, 0.30, 0.24),
    fur_orange,
    export_collection,
    parent=root,
    noise=0.006,
    segments=32,
    rings=22,
)
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    add_capsule(
        f"Cat_Sleeve_{suffix}",
        (side * 0.54, -0.03, 1.90),
        (side * 0.58, -0.30, 1.48),
        (0.155, 0.135),
        blue,
        export_collection,
        parent=root,
    )
    add_capsule(
        f"Cat_Arm_{suffix}",
        (side * 0.58, -0.29, 1.53),
        (side * 0.58, -0.50, 0.87),
        (0.130, 0.112),
        fur_orange,
        export_collection,
        parent=root,
        noise=0.007,
    )
    add_ellipsoid(
        f"Cat_Paw_{suffix}",
        (side * 0.58, -0.54, 0.78),
        (0.14, 0.120, 0.18),
        fur_orange,
        export_collection,
        parent=root,
        noise=0.006,
    )
    add_capsule(
        f"Cat_Leg_{suffix}",
        (side * 0.23, -0.22, 0.70),
        (side * 0.23, -0.43, 0.30),
        (0.17, 0.15),
        fur_orange,
        export_collection,
        parent=root,
        noise=0.006,
    )
    add_ellipsoid(
        f"Cat_Foot_{suffix}",
        (side * 0.23, -0.49, 0.22),
        (0.20, 0.19, 0.15),
        fur_light,
        export_collection,
        parent=root,
        noise=0.007,
    )
    for toe_index, x_offset in enumerate((-0.050, 0.0, 0.050)):
        add_curve(
            f"Cat_ToeLine_{suffix}_{toe_index}",
            [
                (side * 0.23 + x_offset, -0.712, 0.20),
                (side * 0.23 + x_offset, -0.718, 0.27),
            ],
            0.006,
            fur_dark,
            export_collection,
            parent=root,
            resolution=2,
        )

# Cross-body satchel and recognizable heart clasp.
add_curve(
    "Cat_SatchelStrap",
    [(-0.48, -0.715, 2.18), (-0.18, -0.755, 1.78), (0.15, -0.77, 1.40), (0.34, -0.75, 1.18)],
    0.026,
    brown,
    export_collection,
    parent=root,
    resolution=3,
)
bag = add_beveled_cube(
    "Cat_SatchelBag",
    (0.34, -0.73, 1.18),
    (0.22, 0.09, 0.26),
    brown,
    export_collection,
    parent=root,
    rotation=(math.radians(-4.0), 0.0, math.radians(-4.0)),
    bevel=0.075,
)
add_ellipsoid(
    "Cat_SatchelFlap",
    (0.34, -0.838, 1.29),
    (0.21, 0.038, 0.14),
    brown_light,
    export_collection,
    parent=root,
    segments=32,
    rings=20,
)
add_curve(
    "Cat_SatchelHeart",
    [
        (0.34, -0.886, 1.29),
        (0.30, -0.885, 1.32),
        (0.26, -0.883, 1.29),
        (0.28, -0.884, 1.24),
        (0.34, -0.886, 1.19),
        (0.40, -0.884, 1.24),
        (0.42, -0.883, 1.29),
        (0.38, -0.885, 1.32),
        (0.34, -0.886, 1.29),
    ],
    0.012,
    fur_light,
    export_collection,
    parent=root,
    resolution=2,
)
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    add_curve(
        f"Cat_SatchelTasselCord_{suffix}",
        [(0.34 + side * 0.10, -0.845, 0.96), (0.34 + side * 0.10, -0.855, 0.88)],
        0.009,
        fur_light,
        export_collection,
        parent=root,
        resolution=2,
    )
    add_ellipsoid(
        f"Cat_SatchelTassel_{suffix}",
        (0.34 + side * 0.10, -0.865, 0.84),
        (0.034, 0.024, 0.060),
        fur_light,
        export_collection,
        parent=root,
        segments=20,
        rings=14,
    )

# Render-only backdrop and ground.
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.60, 0.02))
ground = bpy.context.object
ground.name = "Cat_RenderGround"
ground.data.materials.append(ground_mat)
move_to_collection(ground, helper_collection)

camera_data = bpy.data.cameras.new("CAT_RenderCamera")
camera = bpy.data.objects.new("CAT_RenderCamera", camera_data)
helper_collection.objects.link(camera)

key = add_area_light("CAT_Key", (-4.5, -5.5, 7.2), "#FFE3B8", 1050.0, 4.6, helper_collection)
fill = add_area_light("CAT_Fill", (4.3, -4.2, 4.7), "#B8CDD2", 600.0, 4.0, helper_collection)
rim = add_area_light("CAT_Rim", (3.0, 3.4, 6.4), "#F6C982", 1150.0, 3.6, helper_collection)
for light in (key, fill, rim):
    look_at(light, (0.0, 0.0, 2.0))

export_objects = descendants(root)
original_materials: dict[str, list[bpy.types.Material]] = {}
for obj in export_objects:
    if obj.type == "MESH":
        original_materials[obj.name] = list(obj.data.materials)
        obj.data.materials.clear()
        obj.data.materials.append(clay)

set_camera(camera, (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_to(RENDER_DIR / f"{ASSET}_01_geometry_front.png", camera)
scene.render.film_transparent = True
ground.hide_render = True
render_to(RENDER_DIR / f"{ASSET}_00_silhouette_front.png", camera)
scene.render.film_transparent = False
ground.hide_render = False

for obj in export_objects:
    if obj.type == "MESH":
        obj.data.materials.clear()
        for material in original_materials[obj.name]:
            obj.data.materials.append(material)

set_camera(camera, (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_to(RENDER_DIR / f"{ASSET}_02_material_front.png", camera)
set_camera(camera, (4.0, -7.4, 3.45), (0.0, -0.02, 2.00), 4.85)
render_to(RENDER_DIR / f"{ASSET}_03_front_3q.png", camera)
set_camera(camera, (8.4, -0.35, 3.15), (0.0, 0.00, 1.95), 4.85)
render_to(RENDER_DIR / f"{ASSET}_04_side.png", camera)
set_camera(camera, (0.0, 8.4, 3.15), (0.0, 0.04, 1.95), 4.85)
render_to(RENDER_DIR / f"{ASSET}_05_back.png", camera)
set_camera(camera, (3.5, -7.7, 3.35), (0.0, -0.03, 2.02), 4.80)
render_to(RENDER_DIR / f"{ASSET}_fallback.png", camera)

blend_path = BLEND_DIR / f"{ASSET}.blend"
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
    mesh_objects.append(
        {
            "name": obj.name,
            "triangles": triangles,
            "bounds_min": [round(value, 4) for value in bounds_min],
            "bounds_max": [round(value, 4) for value in bounds_max],
        }
    )
    evaluated.to_mesh_clear()

contact_pairs = [
    ("Cat_Head_Mesh", "Cat_Body"),
    ("Cat_Ear_L", "Cat_Head_Mesh"),
    ("Cat_Ear_R", "Cat_Head_Mesh"),
    ("Cat_BlueRobe", "Cat_Body"),
    ("Cat_ScarfWrap", "Cat_Head_Mesh"),
    ("Cat_ScarfWrap", "Cat_BlueRobe"),
    ("Cat_Arm_L", "Cat_Sleeve_L"),
    ("Cat_Arm_R", "Cat_Sleeve_R"),
    ("Cat_Leg_L", "Cat_Body"),
    ("Cat_Leg_R", "Cat_Body"),
    ("Cat_Foot_L", "Cat_Leg_L"),
    ("Cat_Foot_R", "Cat_Leg_R"),
    ("Cat_Tail_Base", "Cat_Body"),
    ("Cat_SatchelBag", "Cat_SatchelStrap"),
]
contacts: list[dict[str, object]] = []
contact_warnings: list[str] = []
for a_name, b_name in contact_pairs:
    overlap = aabb_overlap(bpy.data.objects[a_name], bpy.data.objects[b_name])
    passes = sum(1 for value in overlap if value > 0.0) == 3
    contacts.append(
        {
            "a": a_name,
            "b": b_name,
            "aabb_overlap": [round(value, 4) for value in overlap],
            "passes": passes,
        }
    )
    if not passes:
        contact_warnings.append(f"Expected overlap missing: {a_name} / {b_name}")

errors: list[str] = []
warnings = list(contact_warnings)
forbidden_tokens = ("reference", "relief", "billboard", "imageplane", "projection")
forbidden_scene_objects = [
    obj.name
    for obj in bpy.data.objects
    if any(token in obj.name.lower() for token in forbidden_tokens)
]
external_images = [
    {"name": image.name, "filepath": image.filepath}
    for image in bpy.data.images
    if image.source == "FILE"
]
image_texture_nodes = [
    f"{material.name}/{node.name}"
    for material in bpy.data.materials
    if material.use_nodes
    for node in material.node_tree.nodes
    if node.bl_idname == "ShaderNodeTexImage"
]
if forbidden_scene_objects:
    errors.append(f"Forbidden reference-like scene objects: {forbidden_scene_objects}")
if external_images:
    errors.append(f"External images loaded in scene: {external_images}")
if image_texture_nodes:
    errors.append(f"Image texture nodes found: {image_texture_nodes}")
if triangle_count > 100_000:
    warnings.append(f"Triangle count {triangle_count} exceeds 100000 hero target")
if not glb_path.exists() or glb_path.stat().st_size == 0:
    errors.append("GLB export missing or empty")
if glb_path.exists() and glb_path.stat().st_size > 5_000_000:
    warnings.append(f"GLB size {glb_path.stat().st_size} exceeds 5000000-byte target")

scene_graph = {
    "asset": ASSET,
    "target_mode": "TRUE_360",
    "reference": str(REFERENCE_DIR / "comforting_cat_concept_primary.png"),
    "camera_range": "full turnaround: front, three-quarter, side and back",
    "parts": [
        "sculpted cheek-led head, ears and real tapered fur strands",
        "eyes, brows, muzzle and whiskers",
        "body, arms, paws, feet and tail",
        "blue robe, front inset and scarf",
        "satchel, strap, clasp and tassels",
    ],
    "expected_contacts": contact_pairs,
    "acceptance_criteria": [
        "one continuous volumetric design reads consistently from all four reviewed views",
        "no reference plane, relief, billboard, projection or image texture exists in the scene",
        "recognizable feline silhouette rather than bear silhouette",
        "head occupies roughly 43 percent of total height",
        "large low-set dark worried eyes and compact cream muzzle",
        "blue layered scarf/robe and brown cross-body satchel read at thumbnail size",
        "front, three-quarter, side and back renders have no floating primary parts",
        "editable blend and web GLB export exist",
    ],
    "hidden_form_assumption": "depth is modeled from the concept sheet turnaround; no photographed pixels are part of the asset",
}
(REPORT_DIR / f"{ASSET}_scene_graph.json").write_text(json.dumps(scene_graph, indent=2), encoding="utf-8")

report = {
    "asset": ASSET,
    "blender_version": ".".join(map(str, bpy.app.version)),
    "mode": ["shape reconstruction", "organic object", "icon/hero object", "GLB export"],
    "target_representation": "TRUE_360",
    "reference_integrity_audit": {
        "forbidden_scene_objects": forbidden_scene_objects,
        "external_images": external_images,
        "image_texture_nodes": image_texture_nodes,
        "passed": not forbidden_scene_objects and not external_images and not image_texture_nodes,
    },
    "triangles": triangle_count,
    "mesh_objects": mesh_objects,
    "exportable_objects": len(export_objects),
    "materials": sorted(
        {
            material.name
            for obj in export_objects
            if obj.type == "MESH"
            for material in obj.data.materials
        }
    ),
    "required_nodes": ["Cat_Root", "Cat_Head", "Cat_Pupil_L", "Cat_Pupil_R", "Cat_SatchelBag"],
    "contacts": contacts,
    "outputs": {
        "blend": str(blend_path),
        "glb": str(glb_path),
        "glb_bytes": glb_path.stat().st_size if glb_path.exists() else 0,
        "fallback": str(RENDER_DIR / f"{ASSET}_fallback.png"),
        "silhouette_front": str(RENDER_DIR / f"{ASSET}_00_silhouette_front.png"),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {"errors": errors, "warnings": warnings},
    "assumptions": [
        "front turnaround is the primary match target",
        "side and back volumes are reconstructed from the same turnaround sheet",
        "procedural fur bump is render-only; GLB keeps base material colors",
        "real head fur strands are exported geometry",
    ],
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(
        {"asset": ASSET, "contacts": contacts, "errors": errors, "warnings": contact_warnings},
        indent=2,
    ),
    encoding="utf-8",
)
print("COMFORTING_CAT_REPORT=" + json.dumps(report))
