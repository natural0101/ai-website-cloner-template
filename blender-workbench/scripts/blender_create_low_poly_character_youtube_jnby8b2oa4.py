from __future__ import annotations

import json
import math
import random
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
WORKBENCH = REPO / "blender-workbench"
RESEARCH_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
PUBLIC_MODELS = REPO / "public" / "models"
REFERENCE = WORKBENCH / "references" / "low_poly_character_fighting_pose_primary.png"
MASK_JSON = ARTIFACTS / "reference_masks" / "low_poly_character_fighting_pose" / "silhouette_contour.json"

for directory in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    directory.mkdir(parents=True, exist_ok=True)

if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import scene_qa


ASSET = "low_poly_character_youtube_jnby8b2oa4_v35_chamfered_projection"
SCENE_NAME = "LowPolyCharacterYouTubeJnbY8B2oa4V35ChamferedProjection"
COLLECTION_NAME = "ABT_LOW_POLY_CHARACTER_YOUTUBE"
WIDTH = 900
HEIGHT = 1050
TRIANGLE_BUDGET = 60_000
RANDOM_SEED = 20250623

random.seed(RANDOM_SEED)


def ensure_allowed_path(path: Path) -> Path:
    resolved = path.resolve()
    root = REPO.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError(f"Refusing to write outside repo: {resolved}")
    return resolved


def write_json(path: Path, data: dict) -> None:
    target = ensure_allowed_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def remove_default_objects() -> None:
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_collection(scene: bpy.types.Scene) -> bpy.types.Collection:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    return collection


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> bpy.types.Object:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def set_exportable(obj: bpy.types.Object, exportable: bool = True) -> None:
    obj["abt_export"] = bool(exportable)


def make_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_geometry_transform(obj: bpy.types.Object) -> None:
    make_active(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def material_principled(name: str, color: Sequence[float], *, roughness: float = 0.58) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def material_reference_emission(name: str, image_path: Path, *, strength: float = 1.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new(type="ShaderNodeOutputMaterial")
    emission = nodes.new(type="ShaderNodeEmission")
    tex = nodes.new(type="ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(image_path))
    tex.image.colorspace_settings.name = "sRGB"
    emission.inputs["Strength"].default_value = strength
    mat.node_tree.links.new(tex.outputs["Color"], emission.inputs["Color"])
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    mat.diffuse_color = (0.72, 0.74, 0.74, 1.0)
    return mat


def add_materials(obj: bpy.types.Object, mats: Sequence[bpy.types.Material]) -> None:
    obj.data.materials.clear()
    for mat in mats:
        obj.data.materials.append(mat)


def assign_low_poly_facets(obj: bpy.types.Object, mats: Sequence[bpy.types.Material], *, shadow_bias: float = 0.0) -> None:
    add_materials(obj, mats)
    for polygon in obj.data.polygons:
        z = polygon.normal.z
        jitter = random.random()
        if shadow_bias and jitter < shadow_bias:
            polygon.material_index = min(len(mats) - 1, 2)
        elif z > 0.52:
            polygon.material_index = 0
        elif z < -0.22:
            polygon.material_index = min(len(mats) - 1, 2)
        else:
            polygon.material_index = 1 if jitter > 0.28 else 0


def flat_mesh(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = False


def shrink_mesh_world_xz(obj: bpy.types.Object, *, anchor_x: float, anchor_z: float, scale_x: float, scale_z: float) -> None:
    if obj.type != "MESH":
        return
    world = obj.matrix_world.copy()
    inv_world = world.inverted()
    for vertex in obj.data.vertices:
        point = world @ vertex.co
        point.x = anchor_x + (point.x - anchor_x) * scale_x
        point.z = anchor_z + (point.z - anchor_z) * scale_z
        vertex.co = inv_world @ point
    obj.data.update()


def create_ico_ellipsoid(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    rotation: Sequence[float],
    mats: Sequence[bpy.types.Material],
    *,
    subdivisions: int = 2,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.scale = scale
    link_to_collection(obj, collection)
    apply_geometry_transform(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def create_faceted_box(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    dimensions: Sequence[float],
    rotation: Sequence[float],
    mats: Sequence[bpy.types.Material],
    *,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.dimensions = dimensions
    link_to_collection(obj, collection)
    apply_geometry_transform(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def ring_basis(start: Vector, end: Vector) -> tuple[Vector, Vector, Vector, float]:
    direction = end - start
    length = direction.length
    if length <= 1e-6:
        raise ValueError("Zero-length limb")
    axis = direction.normalized()
    helper = Vector((0.0, 0.0, 1.0))
    if abs(axis.dot(helper)) > 0.92:
        helper = Vector((0.0, 1.0, 0.0))
    x_axis = axis.cross(helper).normalized()
    y_axis = x_axis.cross(axis).normalized()
    return axis, x_axis, y_axis, length


def create_frustum_between(
    collection: bpy.types.Collection,
    name: str,
    start: Sequence[float] | Vector,
    end: Sequence[float] | Vector,
    radius_start: float,
    radius_end: float,
    mats: Sequence[bpy.types.Material],
    *,
    vertices_count: int = 6,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    s = Vector(start)
    e = Vector(end)
    _, x_axis, y_axis, _ = ring_basis(s, e)
    vertices: list[tuple[float, float, float]] = []
    for center, radius in ((s, radius_start), (e, radius_end)):
        for i in range(vertices_count):
            angle = 2.0 * math.pi * i / vertices_count
            point = center + math.cos(angle) * radius * x_axis + math.sin(angle) * radius * y_axis
            vertices.append((point.x, point.y, point.z))

    faces: list[tuple[int, ...]] = []
    for i in range(vertices_count):
        faces.append((i, (i + 1) % vertices_count, vertices_count + (i + 1) % vertices_count, vertices_count + i))
    faces.append(tuple(reversed(range(vertices_count))))
    faces.append(tuple(vertices_count + i for i in range(vertices_count)))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def create_elliptic_frustum_between(
    collection: bpy.types.Collection,
    name: str,
    start: Sequence[float] | Vector,
    end: Sequence[float] | Vector,
    start_radii: tuple[float, float],
    end_radii: tuple[float, float],
    mats: Sequence[bpy.types.Material],
    *,
    vertices_count: int = 8,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    s = Vector(start)
    e = Vector(end)
    _, x_axis, y_axis, _ = ring_basis(s, e)
    vertices: list[tuple[float, float, float]] = []
    for center, radii in ((s, start_radii), (e, end_radii)):
        for i in range(vertices_count):
            angle = 2.0 * math.pi * i / vertices_count
            point = center + math.cos(angle) * radii[0] * x_axis + math.sin(angle) * radii[1] * y_axis
            vertices.append((point.x, point.y, point.z))

    faces: list[tuple[int, ...]] = []
    for i in range(vertices_count):
        faces.append((i, (i + 1) % vertices_count, vertices_count + (i + 1) % vertices_count, vertices_count + i))
    faces.append(tuple(reversed(range(vertices_count))))
    faces.append(tuple(vertices_count + i for i in range(vertices_count)))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def create_stacked_poly_volume(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    levels: Sequence[tuple[float, float, float]],
    rotation: Sequence[float],
    mats: Sequence[bpy.types.Material],
    *,
    vertices_count: int = 8,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for z, radius_x, radius_y in levels:
        for i in range(vertices_count):
            angle = 2.0 * math.pi * i / vertices_count
            vertices.append((radius_x * math.cos(angle), radius_y * math.sin(angle), z))

    faces: list[tuple[int, ...]] = []
    ring_count = len(levels)
    for ring_index in range(ring_count - 1):
        row = ring_index * vertices_count
        next_row = (ring_index + 1) * vertices_count
        for i in range(vertices_count):
            faces.append((row + i, row + (i + 1) % vertices_count, next_row + (i + 1) % vertices_count, next_row + i))
    faces.append(tuple(reversed(range(vertices_count))))
    last = (ring_count - 1) * vertices_count
    faces.append(tuple(last + i for i in range(vertices_count)))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    collection.objects.link(obj)
    apply_geometry_transform(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def create_front_prism(
    collection: bpy.types.Collection,
    name: str,
    points_xz: Sequence[tuple[float, float]],
    *,
    y_center: float,
    depth: float,
    mats: Sequence[bpy.types.Material],
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    if len(points_xz) < 3:
        raise ValueError("A front prism needs at least three silhouette points")

    front_y = y_center - depth * 0.5
    back_y = y_center + depth * 0.5

    vertices: list[tuple[float, float, float]] = [(x, front_y, z) for x, z in points_xz]
    back_start = len(vertices)
    vertices.extend((x, back_y, z) for x, z in points_xz)

    faces: list[tuple[int, ...]] = []
    count = len(points_xz)
    triangles = tessellate_polygon([[Vector((x, 0.0, z)) for x, z in points_xz]])
    for triangle in triangles:
        faces.append(tuple(reversed(triangle)))
        faces.append(tuple(back_start + index for index in triangle))
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, back_start + next_index, back_start + index))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=shadow_bias)
    set_exportable(obj, exportable)
    return obj


def model_point_to_reference_uv(x: float, z: float, payload: dict) -> tuple[float, float]:
    mapping = payload["model_mapping"]
    width = float(payload["image_size"]["width"])
    height = float(payload["image_size"]["height"])
    scale = float(mapping["scale"])
    center_x_px = float(mapping["center_x_px"])
    bottom_y_px = float(mapping["bottom_y_px"])
    bottom_z = float(mapping["bottom_z"])
    px = center_x_px + x / scale
    py = bottom_y_px - (z - bottom_z) / scale
    return (px / width, 1.0 - py / height)


def create_textured_reference_cutout(
    collection: bpy.types.Collection,
    name: str,
    payload: dict,
    *,
    y_center: float,
    depth: float,
    front_mat: bpy.types.Material,
    side_mat: bpy.types.Material,
    exportable: bool = True,
) -> bpy.types.Object:
    contour = [(float(point["x"]), float(point["z"])) for point in payload["contour"]]
    if len(contour) < 8:
        raise ValueError("Silhouette contour is too small for projection cutout")

    front_y = y_center - depth * 0.5
    back_y = y_center + depth * 0.5
    vertices: list[tuple[float, float, float]] = [(x, front_y, z) for x, z in contour]
    back_start = len(vertices)
    vertices.extend((x, back_y, z) for x, z in contour)

    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    triangles = tessellate_polygon([[Vector((x, 0.0, z)) for x, z in contour]])
    for triangle in triangles:
        faces.append(tuple(reversed(triangle)))
        material_indices.append(0)
    for triangle in triangles:
        faces.append(tuple(back_start + index for index in triangle))
        material_indices.append(1)
    count = len(contour)
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, back_start + next_index, back_start + index))
        material_indices.append(1)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    add_materials(obj, [front_mat, side_mat])
    for polygon, material_index in zip(obj.data.polygons, material_indices):
        polygon.material_index = material_index
        polygon.use_smooth = False

    uv_layer = obj.data.uv_layers.new(name="ReferenceProjectionUV")
    for polygon in obj.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = obj.data.loops[loop_index].vertex_index
            co = obj.data.vertices[vertex_index].co
            uv_layer.data[loop_index].uv = model_point_to_reference_uv(co.x, co.z, payload)

    set_exportable(obj, exportable)
    return obj


def create_textured_reference_chamfered_cutout(
    collection: bpy.types.Collection,
    name: str,
    payload: dict,
    *,
    rings: Sequence[tuple[float, float, float]],
    front_mat: bpy.types.Material,
    side_mat: bpy.types.Material,
    anchor_x: float = 0.0,
    anchor_z: float = 1.34,
    exportable: bool = True,
) -> bpy.types.Object:
    contour = [(float(point["x"]), float(point["z"])) for point in payload["contour"]]
    if len(contour) < 8:
        raise ValueError("Silhouette contour is too small for chamfered projection cutout")
    if len(rings) < 2:
        raise ValueError("Chamfered cutout needs at least front and back rings")

    vertices: list[tuple[float, float, float]] = []
    for y, scale_x, scale_z in rings:
        for x, z in contour:
            sx = anchor_x + (x - anchor_x) * scale_x
            sz = anchor_z + (z - anchor_z) * scale_z
            vertices.append((sx, y, sz))

    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    count = len(contour)
    triangles = tessellate_polygon([[Vector((x, 0.0, z)) for x, z in contour]])
    for triangle in triangles:
        faces.append(tuple(reversed(triangle)))
        material_indices.append(0)

    back_start = (len(rings) - 1) * count
    for triangle in triangles:
        faces.append(tuple(back_start + index for index in triangle))
        material_indices.append(1)

    for ring_index in range(len(rings) - 1):
        row = ring_index * count
        next_row = (ring_index + 1) * count
        for index in range(count):
            next_index = (index + 1) % count
            faces.append((row + index, row + next_index, next_row + next_index, next_row + index))
            material_indices.append(1)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    add_materials(obj, [front_mat, side_mat])
    for polygon, material_index in zip(obj.data.polygons, material_indices):
        polygon.material_index = material_index
        polygon.use_smooth = False

    uv_layer = obj.data.uv_layers.new(name="ReferenceProjectionUV")
    for polygon in obj.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = obj.data.loops[loop_index].vertex_index
            co = obj.data.vertices[vertex_index].co
            uv_layer.data[loop_index].uv = model_point_to_reference_uv(co.x, co.z, payload)

    set_exportable(obj, exportable)
    return obj


def create_textured_reference_front_plane(
    collection: bpy.types.Collection,
    name: str,
    payload: dict,
    *,
    y: float,
    front_mat: bpy.types.Material,
    exportable: bool = True,
) -> bpy.types.Object:
    contour = [(float(point["x"]), float(point["z"])) for point in payload["contour"]]
    if len(contour) < 8:
        raise ValueError("Silhouette contour is too small for projection plane")

    vertices = [(x, y, z) for x, z in contour]
    faces: list[tuple[int, ...]] = []
    triangles = tessellate_polygon([[Vector((x, 0.0, z)) for x, z in contour]])
    for triangle in triangles:
        faces.append(tuple(reversed(triangle)))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    add_materials(obj, [front_mat])
    for polygon in obj.data.polygons:
        polygon.material_index = 0
        polygon.use_smooth = False

    uv_layer = obj.data.uv_layers.new(name="ReferenceProjectionUV")
    for polygon in obj.data.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = obj.data.loops[loop_index].vertex_index
            co = obj.data.vertices[vertex_index].co
            uv_layer.data[loop_index].uv = model_point_to_reference_uv(co.x, co.z, payload)

    set_exportable(obj, exportable)
    return obj


def rotate_points_xz(points: Sequence[tuple[float, float]], center: Sequence[float], rotation_z: float) -> list[tuple[float, float]]:
    cx, _, cz = center
    cos_z = math.cos(rotation_z)
    sin_z = math.sin(rotation_z)
    return [(cx + x * cos_z - z * sin_z, cz + x * sin_z + z * cos_z) for x, z in points]


def create_front_prism_local(
    collection: bpy.types.Collection,
    name: str,
    local_points_xz: Sequence[tuple[float, float]],
    center: Sequence[float],
    rotation_z: float,
    depth: float,
    mats: Sequence[bpy.types.Material],
    *,
    exportable: bool = True,
    shadow_bias: float = 0.0,
) -> bpy.types.Object:
    return create_front_prism(
        collection,
        name,
        rotate_points_xz(local_points_xz, center, rotation_z),
        y_center=float(center[1]),
        depth=depth,
        mats=mats,
        exportable=exportable,
        shadow_bias=shadow_bias,
    )


def create_low_poly_mitten_hand(
    collection: bpy.types.Collection,
    name: str,
    center: Sequence[float],
    *,
    width: float,
    height: float,
    depth: float,
    rotation_z: float,
    thumb_side: int,
    mats: Sequence[bpy.types.Material],
) -> list[bpy.types.Object]:
    half_w = width * 0.5
    half_h = height * 0.5
    palm_points = [
        (-0.36 * width, -0.43 * height),
        (0.18 * width, -0.48 * height),
        (0.43 * width, -0.25 * height),
        (0.38 * width, 0.26 * height),
        (0.12 * width, 0.50 * height),
        (-0.20 * width, 0.46 * height),
        (-0.45 * width, 0.18 * height),
        (-0.46 * width, -0.20 * height),
    ]
    objects = [
        create_front_prism_local(
            collection,
            f"{name}_palm_mitten_low_poly",
            palm_points,
            center,
            rotation_z,
            depth,
            mats,
            shadow_bias=0.07,
        )
    ]

    thumb_points = [
        (thumb_side * 0.24 * width, -0.20 * height),
        (thumb_side * 0.58 * width, -0.10 * height),
        (thumb_side * 0.63 * width, 0.07 * height),
        (thumb_side * 0.31 * width, 0.04 * height),
    ]
    objects.append(create_front_prism_local(
        collection,
        f"{name}_thumb_wedge_overlap",
        thumb_points,
        center,
        rotation_z,
        depth * 0.72,
        mats,
        shadow_bias=0.10,
    ))

    # Low-poly finger planes: unequal, embedded into the palm, and subtle enough to keep the lesson style.
    finger_specs = [(-0.18, 0.03, 0.46), (0.00, 0.02, 0.50), (0.17, 0.025, 0.42)]
    for index, (x_offset, taper, z_top) in enumerate(finger_specs, start=1):
        ridge = [
            ((x_offset - 0.035) * width, -0.12 * height),
            ((x_offset + 0.030) * width, -0.10 * height),
            ((x_offset + taper) * width, z_top * height),
            ((x_offset - 0.050) * width, (z_top - 0.06) * height),
        ]
        objects.append(create_front_prism_local(
            collection,
            f"{name}_finger_facet_{index}",
            ridge,
            (center[0], center[1] - depth * 0.47, center[2]),
            rotation_z,
            depth * 0.18,
            [mats[0], mats[1], mats[min(2, len(mats) - 1)]],
            shadow_bias=0.12,
        ))
    return objects


def create_low_poly_open_hand(
    collection: bpy.types.Collection,
    name: str,
    center: Sequence[float],
    *,
    width: float,
    height: float,
    depth: float,
    rotation_z: float,
    thumb_side: int,
    mats: Sequence[bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    palm = [
        (-0.42 * width, -0.34 * height),
        (0.30 * width, -0.36 * height),
        (0.47 * width, -0.13 * height),
        (0.33 * width, 0.13 * height),
        (-0.18 * width, 0.17 * height),
        (-0.48 * width, -0.04 * height),
    ]
    objects.append(create_front_prism_local(
        collection,
        f"{name}_palm_wedge",
        palm,
        center,
        rotation_z,
        depth,
        mats,
        shadow_bias=0.08,
    ))

    thumb = [
        (thumb_side * 0.25 * width, -0.26 * height),
        (thumb_side * 0.73 * width, -0.16 * height),
        (thumb_side * 0.68 * width, 0.05 * height),
        (thumb_side * 0.31 * width, 0.02 * height),
    ]
    objects.append(create_front_prism_local(
        collection,
        f"{name}_thumb_block_overlap",
        thumb,
        (center[0], center[1] - depth * 0.12, center[2]),
        rotation_z,
        depth * 0.72,
        mats,
        shadow_bias=0.11,
    ))

    finger_specs = [
        (-0.28, 0.070, 0.080, 0.445, -0.014),
        (-0.095, 0.072, 0.105, 0.545, -0.006),
        (0.095, 0.070, 0.100, 0.505, 0.006),
        (0.270, 0.062, 0.070, 0.390, 0.014),
    ]
    for index, (x_mid, half_w, z_base, z_tip, splay) in enumerate(finger_specs, start=1):
        finger = [
            ((x_mid - half_w) * width, (z_base - 0.055) * height),
            ((x_mid + half_w) * width, (z_base - 0.040) * height),
            ((x_mid + half_w * 0.58 + splay) * width, z_tip * height),
            ((x_mid - half_w * 0.66 + splay * 0.35) * width, (z_tip - 0.022) * height),
        ]
        objects.append(create_front_prism_local(
            collection,
            f"{name}_finger_{index}_overlap",
            finger,
            (center[0], center[1] - depth * 0.42, center[2]),
            rotation_z,
            depth * 0.30,
            mats,
            shadow_bias=0.12 + index * 0.012,
        ))
    return objects


def create_low_poly_block_hand(
    collection: bpy.types.Collection,
    name: str,
    center: Sequence[float],
    *,
    width: float,
    height: float,
    depth: float,
    rotation_z: float,
    thumb_side: int,
    mats: Sequence[bpy.types.Material],
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    outline = [
        (-0.42 * width, -0.40 * height),
        (0.26 * width, -0.42 * height),
        (0.42 * width, -0.22 * height),
        (0.38 * width, 0.08 * height),
        (0.32 * width, 0.39 * height),
        (0.21 * width, 0.49 * height),
        (0.11 * width, 0.17 * height),
        (0.03 * width, 0.52 * height),
        (-0.09 * width, 0.50 * height),
        (-0.12 * width, 0.15 * height),
        (-0.22 * width, 0.45 * height),
        (-0.34 * width, 0.38 * height),
        (-0.31 * width, 0.08 * height),
        (-0.50 * width, -0.08 * height),
    ]
    objects.append(create_front_prism_local(
        collection,
        f"{name}_single_piece_fingered_mitten",
        outline,
        center,
        rotation_z,
        depth,
        mats,
        shadow_bias=0.08,
    ))

    thumb = [
        (thumb_side * 0.26 * width, -0.23 * height),
        (thumb_side * 0.70 * width, -0.15 * height),
        (thumb_side * 0.65 * width, 0.08 * height),
        (thumb_side * 0.30 * width, 0.04 * height),
    ]
    objects.append(create_front_prism_local(
        collection,
        f"{name}_thumb_wedge",
        thumb,
        (center[0], center[1] - depth * 0.10, center[2]),
        rotation_z,
        depth * 0.70,
        mats,
        shadow_bias=0.10,
    ))

    crease_specs = [(-0.145, 0.31), (0.005, 0.36), (0.150, 0.30)]
    for index, (x_offset, z_tip) in enumerate(crease_specs, start=1):
        crease = [
            ((x_offset - 0.018) * width, 0.02 * height),
            ((x_offset + 0.018) * width, 0.04 * height),
            ((x_offset + 0.010) * width, z_tip * height),
            ((x_offset - 0.020) * width, (z_tip - 0.04) * height),
        ]
        objects.append(create_front_prism_local(
            collection,
            f"{name}_finger_crease_{index}",
            crease,
            (center[0], center[1] - depth * 0.45, center[2]),
            rotation_z,
            depth * 0.16,
            [mats[1], mats[2], mats[1]],
            shadow_bias=0.16,
        ))
    return objects


def create_low_poly_foot(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    rotation_z: float,
    mats: Sequence[bpy.types.Material],
) -> bpy.types.Object:
    sx, sy, sz = scale
    vertices = [
        (-0.55 * sx, -0.34 * sy, -0.45 * sz),
        (0.35 * sx, -0.38 * sy, -0.45 * sz),
        (0.70 * sx, -0.18 * sy, -0.45 * sz),
        (0.72 * sx, 0.25 * sy, -0.45 * sz),
        (-0.52 * sx, 0.34 * sy, -0.45 * sz),
        (-0.44 * sx, -0.24 * sy, 0.28 * sz),
        (0.30 * sx, -0.27 * sy, 0.40 * sz),
        (0.68 * sx, -0.11 * sy, 0.24 * sz),
        (0.60 * sx, 0.22 * sy, 0.24 * sz),
        (-0.44 * sx, 0.25 * sy, 0.32 * sz),
    ]
    faces = [
        (0, 1, 2, 3, 4),
        (5, 9, 8, 7, 6),
        (0, 5, 6, 1),
        (1, 6, 7, 2),
        (2, 7, 8, 3),
        (3, 8, 9, 4),
        (4, 9, 5, 0),
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = (math.radians(-3), 0.0, rotation_z)
    collection.objects.link(obj)
    apply_geometry_transform(obj)
    flat_mesh(obj)
    assign_low_poly_facets(obj, mats, shadow_bias=0.10)
    set_exportable(obj, True)
    return obj


def create_limb(
    collection: bpy.types.Collection,
    base_name: str,
    start: Vector,
    joint: Vector,
    end: Vector,
    upper_radii: tuple[float, float],
    lower_radii: tuple[float, float],
    joint_scale: Sequence[float],
    mats: Sequence[bpy.types.Material],
) -> list[bpy.types.Object]:
    upper = create_elliptic_frustum_between(
        collection,
        f"{base_name}_upper_faceted_taper",
        start,
        joint,
        (upper_radii[0], upper_radii[0] * 0.72),
        (upper_radii[1], upper_radii[1] * 0.72),
        mats,
        vertices_count=8,
        shadow_bias=0.12,
    )
    joint_obj = create_ico_ellipsoid(
        collection,
        f"{base_name}_joint_low_poly",
        joint,
        joint_scale,
        (0.0, 0.0, 0.0),
        mats,
        subdivisions=1,
        shadow_bias=0.10,
    )
    lower = create_elliptic_frustum_between(
        collection,
        f"{base_name}_lower_faceted_taper",
        joint,
        end,
        (lower_radii[0], lower_radii[0] * 0.70),
        (lower_radii[1], lower_radii[1] * 0.70),
        mats,
        vertices_count=8,
        shadow_bias=0.14,
    )
    return [upper, joint_obj, lower]


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - Vector(obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> tuple[bpy.types.Scene, bpy.types.Collection, dict[str, bpy.types.Material]]:
    remove_default_objects()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = engine
            break
        except Exception:
            continue
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (("taa_render_samples", 96), ("use_gtao", True), ("gtao_distance", 3.0), ("gtao_factor", 1.2)):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - High Contrast", "None"):
        try:
            scene.view_settings.look = look
            break
        except TypeError:
            continue
    scene.view_settings.exposure = -0.1
    scene.view_settings.gamma = 1.0

    collection = make_collection(scene)
    mats = {
        "grey_light": material_principled("LPC_Mat_polygon_light_warm_grey", (0.82, 0.85, 0.84, 1.0), roughness=0.62),
        "grey_mid": material_principled("LPC_Mat_polygon_mid_grey", (0.56, 0.61, 0.61, 1.0), roughness=0.66),
        "grey_dark": material_principled("LPC_Mat_polygon_shadow_grey", (0.25, 0.31, 0.32, 1.0), roughness=0.72),
        "joint_dark": material_principled("LPC_Mat_dark_joint_occlusion", (0.16, 0.21, 0.22, 1.0), roughness=0.76),
        "floor": material_principled("LPC_Mat_preview_neutral_gray_floor_not_exported", (0.25, 0.25, 0.24, 1.0), roughness=0.78),
    }
    return scene, collection, mats


def create_character(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # Body masses: controlled faceted volumes instead of noisy separated blobs.
    objects.append(create_stacked_poly_volume(
        collection,
        "LPC_Pelvis_blocky_low_poly",
        (0.0, 0.0, 0.82),
        [(-0.18, 0.34, 0.20), (-0.01, 0.50, 0.29), (0.18, 0.40, 0.23)],
        (math.radians(-7), 0.0, math.radians(1)),
        skin,
        vertices_count=9,
        shadow_bias=0.12,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPC_Abdomen_faceted",
        (0.02, -0.055, 1.13),
        [(-0.20, 0.30, 0.20), (-0.01, 0.40, 0.25), (0.21, 0.34, 0.22)],
        (math.radians(-13), 0.0, math.radians(-2)),
        skin,
        vertices_count=9,
        shadow_bias=0.12,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPC_Chest_angular_torso",
        (0.03, -0.085, 1.53),
        [(-0.31, 0.40, 0.24), (-0.09, 0.60, 0.32), (0.19, 0.56, 0.30), (0.35, 0.36, 0.20)],
        (math.radians(-15), 0.0, math.radians(-3)),
        skin,
        vertices_count=10,
        shadow_bias=0.10,
    ))
    objects.append(create_elliptic_frustum_between(collection, "LPC_Neck_short_faceted", (0.04, -0.11, 1.88), (0.07, -0.14, 2.05), (0.12, 0.10), (0.14, 0.12), skin, vertices_count=8, shadow_bias=0.12))
    objects.append(create_ico_ellipsoid(collection, "LPC_Head_featureless_faceted", (0.09, -0.17, 2.32), (0.30, 0.255, 0.34), (math.radians(-10), 0.0, math.radians(-6)), skin, subdivisions=2, shadow_bias=0.08))

    # Dark occlusion bands reproduce the hard graphic separations in the lesson thumbnail.
    objects.append(create_faceted_box(collection, "LPC_Waist_dark_polygon_gap", (0.02, -0.20, 1.06), (0.62, 0.045, 0.060), (math.radians(-13), 0.0, math.radians(-2)), shadow, shadow_bias=0.8))
    objects.append(create_ico_ellipsoid(collection, "LPC_Left_armpit_dark_wedge", (-0.47, -0.12, 1.56), (0.065, 0.050, 0.105), (0.0, 0.0, 0.0), shadow, subdivisions=1, shadow_bias=0.9))
    objects.append(create_ico_ellipsoid(collection, "LPC_Right_armpit_dark_wedge", (0.50, -0.12, 1.54), (0.065, 0.050, 0.105), (0.0, 0.0, 0.0), shadow, subdivisions=1, shadow_bias=0.9))

    # Shoulders and arms: bent, angular, with hands placed near the thighs.
    left_shoulder = Vector((-0.50, -0.05, 1.68))
    left_elbow = Vector((-0.83, -0.02, 1.22))
    left_wrist = Vector((-0.38, -0.13, 0.98))
    right_shoulder = Vector((0.52, -0.05, 1.64))
    right_elbow = Vector((1.05, -0.02, 1.23))
    right_wrist = Vector((0.72, -0.14, 0.96))

    objects.append(create_ico_ellipsoid(collection, "LPC_Left_shoulder_cap", left_shoulder, (0.18, 0.13, 0.16), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.12))
    objects.append(create_ico_ellipsoid(collection, "LPC_Right_shoulder_cap", right_shoulder, (0.18, 0.13, 0.16), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.12))
    objects.extend(create_limb(collection, "LPC_Left_arm", left_shoulder, left_elbow, left_wrist, (0.115, 0.090), (0.090, 0.065), (0.105, 0.095, 0.105), skin))
    objects.extend(create_limb(collection, "LPC_Right_arm", right_shoulder, right_elbow, right_wrist, (0.115, 0.090), (0.090, 0.065), (0.105, 0.095, 0.105), skin))
    objects.append(create_ico_ellipsoid(collection, "LPC_Left_hand_simple_mitten", (-0.40, -0.145, 0.97), (0.155, 0.074, 0.060), (0.0, math.radians(8), math.radians(-18)), skin, subdivisions=2, shadow_bias=0.10))
    objects.append(create_ico_ellipsoid(collection, "LPC_Right_hand_simple_mitten", (0.78, -0.145, 0.95), (0.155, 0.074, 0.060), (0.0, math.radians(-8), math.radians(18)), skin, subdivisions=2, shadow_bias=0.10))

    # Legs: wide crouch pose with low-poly knee/ankle joints and outward feet.
    left_hip = Vector((-0.25, 0.03, 0.80))
    left_knee = Vector((-0.68, 0.06, 0.58))
    left_ankle = Vector((-0.94, -0.03, 0.17))
    right_hip = Vector((0.27, 0.03, 0.80))
    right_knee = Vector((0.78, 0.06, 0.57))
    right_ankle = Vector((1.08, -0.03, 0.17))

    objects.append(create_ico_ellipsoid(collection, "LPC_Left_hip_socket_overlap", left_hip, (0.20, 0.14, 0.13), (0.0, 0.0, math.radians(-10)), skin, subdivisions=2, shadow_bias=0.12))
    objects.append(create_ico_ellipsoid(collection, "LPC_Right_hip_socket_overlap", right_hip, (0.20, 0.14, 0.13), (0.0, 0.0, math.radians(10)), skin, subdivisions=2, shadow_bias=0.12))
    objects.extend(create_limb(collection, "LPC_Left_leg", left_hip, left_knee, left_ankle, (0.190, 0.145), (0.135, 0.080), (0.145, 0.115, 0.120), skin))
    objects.extend(create_limb(collection, "LPC_Right_leg", right_hip, right_knee, right_ankle, (0.190, 0.145), (0.135, 0.080), (0.145, 0.115, 0.120), skin))
    objects.append(create_ico_ellipsoid(collection, "LPC_Left_ankle_cap", left_ankle, (0.085, 0.075, 0.085), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.12))
    objects.append(create_ico_ellipsoid(collection, "LPC_Right_ankle_cap", right_ankle, (0.085, 0.075, 0.085), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.12))
    objects.append(create_low_poly_foot(collection, "LPC_Left_low_poly_foot", (-1.14, -0.15, 0.065), (0.45, 0.26, 0.18), math.radians(-13), skin))
    objects.append(create_low_poly_foot(collection, "LPC_Right_low_poly_foot", (1.32, -0.15, 0.065), (0.45, 0.26, 0.18), math.radians(13), skin))

    for obj in objects:
        obj["source_reference"] = "YouTube J-nbY8B2oa4 thumbnail: low-poly crouching Blender character"
        obj["target_mode"] = "HYBRID_HERO"
    return objects


def create_fighting_pose_character(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # Upright guard/fighting pose from the new primary reference.
    # The pose is built from overlapping masses, not a squat thumbnail blockout.
    objects.append(create_front_prism(
        collection,
        "LPCV10_Chest_reference_silhouette",
        [(-0.30, 1.88), (-0.12, 2.00), (0.23, 1.86), (0.21, 1.62), (0.10, 1.45), (-0.17, 1.49), (-0.25, 1.64)],
        y_center=-0.04,
        depth=0.32,
        mats=skin,
        shadow_bias=0.08,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV10_Abdomen_reference_silhouette",
        [(-0.17, 1.47), (0.12, 1.43), (0.12, 1.15), (0.04, 0.98), (-0.09, 0.99), (-0.18, 1.18)],
        y_center=-0.035,
        depth=0.28,
        mats=skin,
        shadow_bias=0.10,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV10_Pelvis_reference_silhouette",
        [(-0.11, 1.00), (0.13, 0.99), (0.17, 0.89), (0.04, 0.81), (-0.10, 0.86), (-0.15, 0.96)],
        y_center=-0.035,
        depth=0.27,
        mats=skin,
        shadow_bias=0.10,
    ))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV9_Neck_short_overlap",
        (-0.06, -0.10, 1.96),
        (-0.07, -0.12, 2.14),
        (0.095, 0.075),
        (0.125, 0.090),
        skin,
        vertices_count=7,
        shadow_bias=0.10,
    ))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV9_Head_oval_low_poly",
        (-0.07, -0.13, 2.33),
        (0.205, 0.178, 0.292),
        (math.radians(-4), 0.0, math.radians(-4)),
        skin,
        subdivisions=2,
        shadow_bias=0.06,
    ))

    # Subtle shadow planes, not black holes.
    objects.append(create_faceted_box(collection, "LPCV9_Under_chest_soft_shadow", (-0.02, -0.215, 1.55), (0.42, 0.032, 0.050), (math.radians(-3), 0.0, math.radians(-3)), shadow, shadow_bias=0.55))
    objects.append(create_faceted_box(collection, "LPCV9_Groin_soft_shadow", (0.04, -0.18, 1.00), (0.25, 0.032, 0.060), (math.radians(8), 0.0, math.radians(-3)), shadow, shadow_bias=0.55))

    # Guard arm near the face, crossing the torso.
    near_shoulder = Vector((-0.29, -0.04, 1.82))
    near_elbow = Vector((-0.25, -0.22, 1.58))
    near_wrist = Vector((-0.02, -0.32, 1.97))
    objects.append(create_ico_ellipsoid(collection, "LPCV9_Near_shoulder_mass", near_shoulder, (0.125, 0.095, 0.125), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV9_Near_guard_arm", near_shoulder, near_elbow, near_wrist, (0.092, 0.074), (0.066, 0.046), (0.078, 0.064, 0.078), skin))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV9_Near_vertical_hand_at_face",
        (0.035, -0.35, 2.06),
        (0.052, 0.030, 0.142),
        (math.radians(8), math.radians(-8), math.radians(6)),
        skin,
        subdivisions=2,
        shadow_bias=0.08,
    ))

    # Forward hand/palm held out in front of the torso.
    far_shoulder = Vector((0.26, -0.03, 1.72))
    far_elbow = Vector((0.42, -0.17, 1.45))
    far_wrist = Vector((0.62, -0.30, 1.54))
    objects.append(create_ico_ellipsoid(collection, "LPCV9_Far_shoulder_mass", far_shoulder, (0.120, 0.092, 0.120), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV9_Far_forward_arm", far_shoulder, far_elbow, far_wrist, (0.088, 0.070), (0.062, 0.044), (0.074, 0.060, 0.074), skin))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV9_Far_vertical_open_palm",
        (0.69, -0.35, 1.65),
        (0.052, 0.030, 0.140),
        (math.radians(2), math.radians(-12), math.radians(-8)),
        skin,
        subdivisions=2,
        shadow_bias=0.08,
    ))

    # Walking/fighting stance legs. One leg supports vertically, the other crosses back.
    lead_hip = Vector((-0.09, -0.01, 0.98))
    lead_knee = Vector((-0.26, -0.04, 0.58))
    lead_ankle = Vector((-0.47, -0.08, 0.14))
    rear_hip = Vector((0.11, -0.01, 0.98))
    rear_knee = Vector((0.34, -0.04, 0.66))
    rear_ankle = Vector((0.33, -0.08, 0.23))

    objects.append(create_ico_ellipsoid(collection, "LPCV9_Lead_hip_overlap", lead_hip, (0.120, 0.092, 0.100), (0.0, 0.0, math.radians(-6)), skin, subdivisions=2, shadow_bias=0.08))
    objects.append(create_ico_ellipsoid(collection, "LPCV9_Rear_hip_overlap", rear_hip, (0.120, 0.092, 0.100), (0.0, 0.0, math.radians(6)), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV9_Lead_leg", lead_hip, lead_knee, lead_ankle, (0.118, 0.090), (0.083, 0.056), (0.082, 0.068, 0.082), skin))
    objects.extend(create_limb(collection, "LPCV9_Rear_leg", rear_hip, rear_knee, rear_ankle, (0.116, 0.088), (0.082, 0.055), (0.082, 0.068, 0.082), skin))
    objects.append(create_ico_ellipsoid(collection, "LPCV9_Lead_ankle_overlap_cap", lead_ankle, (0.068, 0.058, 0.062), (0.0, 0.0, math.radians(-4)), skin, subdivisions=1, shadow_bias=0.08))
    objects.append(create_ico_ellipsoid(collection, "LPCV9_Rear_ankle_overlap_cap", rear_ankle, (0.068, 0.058, 0.062), (0.0, 0.0, math.radians(5)), skin, subdivisions=1, shadow_bias=0.08))
    objects.append(create_front_prism(
        collection,
        "LPCV9_Lead_wedge_foot",
        [(-0.62, 0.12), (-0.39, 0.14), (-0.32, 0.08), (-0.38, 0.04), (-0.58, 0.03), (-0.66, 0.07)],
        y_center=-0.11,
        depth=0.17,
        mats=skin,
        shadow_bias=0.10,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV9_Rear_wedge_foot",
        [(0.30, 0.21), (0.46, 0.18), (0.57, 0.12), (0.50, 0.08), (0.36, 0.11), (0.29, 0.16)],
        y_center=-0.11,
        depth=0.17,
        mats=skin,
        shadow_bias=0.10,
    ))

    for obj in objects:
        obj["source_reference"] = "Primary user screenshot: low-poly upright fighting/guard pose"
        obj["target_mode"] = "HYBRID_HERO"
    return objects


def create_reference_relief_character(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))
    contour = [(float(point["x"]), float(point["z"])) for point in payload["contour"]]
    if len(contour) < 8:
        raise ValueError("Silhouette contour is too small for the reference relief")

    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    accent = [mats["grey_mid"], mats["grey_dark"], mats["joint_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    objects.append(create_front_prism(
        collection,
        "LPCV12_Reference_silhouette_extruded_low_poly",
        contour,
        y_center=-0.02,
        depth=0.24,
        mats=skin,
        shadow_bias=0.09,
    ))

    # Surface accents preserve the Blender-lesson mannequin read while the outer contour stays reference-locked.
    objects.append(create_front_prism(
        collection,
        "LPCV12_Near_guard_arm_surface_facet",
        [(-0.34, 1.66), (-0.03, 1.93), (0.025, 1.86), (-0.26, 1.54)],
        y_center=-0.155,
        depth=0.020,
        mats=accent,
        shadow_bias=0.18,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV12_Far_forearm_surface_facet",
        [(0.28, 1.44), (0.58, 1.52), (0.60, 1.44), (0.33, 1.35)],
        y_center=-0.155,
        depth=0.020,
        mats=accent,
        shadow_bias=0.16,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV12_Chest_shadow_triangle",
        [(-0.03, 1.82), (0.18, 1.60), (0.02, 1.55)],
        y_center=-0.158,
        depth=0.018,
        mats=shadow,
        shadow_bias=0.24,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV12_Groin_shadow_triangle",
        [(0.00, 1.10), (0.14, 0.91), (-0.05, 0.92)],
        y_center=-0.158,
        depth=0.018,
        mats=shadow,
        shadow_bias=0.26,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV12_Left_leg_light_facet",
        [(-0.42, 0.92), (-0.24, 0.80), (-0.49, 0.34), (-0.62, 0.40)],
        y_center=-0.158,
        depth=0.016,
        mats=[mats["grey_light"], mats["grey_mid"], mats["grey_light"]],
        shadow_bias=0.04,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV12_Right_leg_light_facet",
        [(0.21, 0.95), (0.35, 0.80), (0.23, 0.45), (0.13, 0.50)],
        y_center=-0.158,
        depth=0.016,
        mats=[mats["grey_light"], mats["grey_mid"], mats["grey_light"]],
        shadow_bias=0.04,
    ))

    for obj in objects:
        obj["source_reference"] = "Primary user screenshot contour: low-poly upright fighting/guard pose"
        obj["target_mode"] = "FRONT_2_5D_HYBRID_HERO"
        obj["mask_json"] = str(MASK_JSON)
    return objects


def create_refined_semantic_character_v14(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # Semantic HYBRID_HERO branch: editable volumes, not a flat contour card.
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV14_Chest_tapered_reference_mass",
        (0.02, -0.04, 1.72),
        [(-0.26, 0.19, 0.12), (-0.03, 0.31, 0.18), (0.18, 0.27, 0.15), (0.29, 0.14, 0.10)],
        (math.radians(-2), 0.0, math.radians(-5)),
        skin,
        vertices_count=8,
        shadow_bias=0.08,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV14_Abdomen_narrow_taper",
        (0.01, -0.035, 1.30),
        [(-0.25, 0.15, 0.10), (0.00, 0.20, 0.125), (0.23, 0.14, 0.09)],
        (math.radians(1), 0.0, math.radians(-4)),
        skin,
        vertices_count=8,
        shadow_bias=0.10,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV14_Pelvis_small_overlap",
        (0.04, -0.03, 0.99),
        [(-0.15, 0.15, 0.10), (0.00, 0.22, 0.13), (0.15, 0.16, 0.10)],
        (math.radians(3), 0.0, math.radians(-3)),
        skin,
        vertices_count=8,
        shadow_bias=0.10,
    ))

    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV14_Neck_overlap",
        (-0.03, -0.10, 1.95),
        (-0.04, -0.12, 2.14),
        (0.080, 0.065),
        (0.105, 0.080),
        skin,
        vertices_count=7,
        shadow_bias=0.10,
    ))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV14_Head_faceted_oval",
        (-0.035, -0.13, 2.34),
        (0.180, 0.162, 0.285),
        (math.radians(-4), 0.0, math.radians(-4)),
        skin,
        subdivisions=2,
        shadow_bias=0.06,
    ))

    objects.append(create_front_prism_local(
        collection,
        "LPCV15_Under_chest_triangular_occlusion",
        [(-0.13, 0.02), (0.15, 0.01), (0.03, -0.055)],
        (0.00, -0.215, 1.49),
        math.radians(-4),
        0.020,
        shadow,
        shadow_bias=0.55,
    ))
    objects.append(create_front_prism_local(
        collection,
        "LPCV15_Groin_small_shadow",
        [(-0.07, 0.035), (0.08, 0.015), (0.00, -0.055)],
        (0.03, -0.18, 0.96),
        math.radians(-3),
        0.020,
        shadow,
        shadow_bias=0.55,
    ))

    near_shoulder = Vector((-0.27, -0.045, 1.78))
    near_elbow = Vector((-0.24, -0.23, 1.57))
    near_wrist = Vector((-0.035, -0.32, 1.96))
    objects.append(create_ico_ellipsoid(collection, "LPCV14_Near_shoulder_blend", near_shoulder, (0.120, 0.090, 0.120), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV14_Near_guard_arm", near_shoulder, near_elbow, near_wrist, (0.088, 0.070), (0.062, 0.044), (0.074, 0.060, 0.074), skin))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV14_Near_guard_hand",
        (0.020, -0.345, 2.035),
        width=0.112,
        height=0.260,
        depth=0.064,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    far_shoulder = Vector((0.24, -0.04, 1.70))
    far_elbow = Vector((0.36, -0.17, 1.45))
    far_wrist = Vector((0.54, -0.30, 1.53))
    objects.append(create_ico_ellipsoid(collection, "LPCV14_Far_shoulder_blend", far_shoulder, (0.115, 0.088, 0.115), (0.0, 0.0, 0.0), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV14_Far_forward_arm", far_shoulder, far_elbow, far_wrist, (0.084, 0.066), (0.058, 0.042), (0.070, 0.058, 0.070), skin))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV14_Far_open_hand",
        (0.600, -0.35, 1.625),
        width=0.122,
        height=0.275,
        depth=0.064,
        rotation_z=math.radians(-9),
        thumb_side=-1,
        mats=skin,
    ))

    lead_hip = Vector((-0.045, -0.02, 0.95))
    lead_knee = Vector((-0.190, -0.045, 0.57))
    lead_ankle = Vector((-0.340, -0.075, 0.13))
    rear_hip = Vector((0.125, -0.02, 0.96))
    rear_knee = Vector((0.330, -0.045, 0.66))
    rear_ankle = Vector((0.320, -0.075, 0.22))

    objects.append(create_ico_ellipsoid(collection, "LPCV14_Lead_hip_socket", lead_hip, (0.110, 0.086, 0.095), (0.0, 0.0, math.radians(-6)), skin, subdivisions=2, shadow_bias=0.08))
    objects.append(create_ico_ellipsoid(collection, "LPCV14_Rear_hip_socket", rear_hip, (0.110, 0.086, 0.095), (0.0, 0.0, math.radians(6)), skin, subdivisions=2, shadow_bias=0.08))
    objects.extend(create_limb(collection, "LPCV14_Lead_leg", lead_hip, lead_knee, lead_ankle, (0.112, 0.086), (0.078, 0.052), (0.078, 0.064, 0.078), skin))
    objects.extend(create_limb(collection, "LPCV14_Rear_leg", rear_hip, rear_knee, rear_ankle, (0.110, 0.084), (0.076, 0.052), (0.078, 0.064, 0.078), skin))
    objects.append(create_ico_ellipsoid(collection, "LPCV14_Lead_ankle_blend", lead_ankle, (0.064, 0.055, 0.060), (0.0, 0.0, math.radians(-4)), skin, subdivisions=1, shadow_bias=0.08))
    objects.append(create_ico_ellipsoid(collection, "LPCV14_Rear_ankle_blend", rear_ankle, (0.064, 0.055, 0.060), (0.0, 0.0, math.radians(5)), skin, subdivisions=1, shadow_bias=0.08))
    objects.append(create_front_prism(
        collection,
        "LPCV14_Lead_wedge_foot",
        [(-0.50, 0.12), (-0.27, 0.14), (-0.20, 0.08), (-0.26, 0.04), (-0.46, 0.03), (-0.54, 0.07)],
        y_center=-0.11,
        depth=0.17,
        mats=skin,
        shadow_bias=0.10,
    ))
    objects.append(create_front_prism(
        collection,
        "LPCV14_Rear_wedge_foot",
        [(0.30, 0.21), (0.46, 0.18), (0.57, 0.12), (0.50, 0.08), (0.36, 0.11), (0.29, 0.16)],
        y_center=-0.11,
        depth=0.17,
        mats=skin,
        shadow_bias=0.10,
    ))

    for obj in objects:
        obj["source_reference"] = "Primary user screenshot: low-poly upright fighting/guard pose"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v15 refines hand construction: smaller palm, wrist overlap, separate thumb, unequal embedded finger facets, softer torso occlusion"
    return objects


def create_contour_semantic_character_v17(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # Head and torso are contour-guided semantic prisms: closer front silhouette without collapsing into one flat card.
    objects.append(create_front_prism(collection, "LPCV19_Head_custom_faceted_prism", [
        (-0.035, 2.620), (-0.160, 2.575), (-0.190, 2.460), (-0.168, 2.273),
        (-0.060, 2.205), (0.050, 2.295), (0.093, 2.420), (0.068, 2.534),
    ], y_center=-0.12, depth=0.300, mats=skin, shadow_bias=0.06))
    objects.append(create_front_prism(collection, "LPCV19_Head_front_light_facet", [
        (-0.115, 2.530), (-0.025, 2.590), (0.030, 2.500), (-0.020, 2.360), (-0.125, 2.420),
    ], y_center=-0.282, depth=0.018, mats=[mats["grey_light"], mats["grey_mid"], mats["grey_light"]], shadow_bias=0.03))
    objects.append(create_front_prism(collection, "LPCV19_Head_lower_shadow_facet", [
        (-0.145, 2.315), (-0.055, 2.210), (0.055, 2.295), (-0.030, 2.330),
    ], y_center=-0.284, depth=0.018, mats=shadow, shadow_bias=0.22))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV18_Neck_overlap_from_contour",
        (-0.055, -0.11, 2.160),
        (-0.048, -0.12, 2.265),
        (0.055, 0.050),
        (0.073, 0.058),
        skin,
        vertices_count=7,
        shadow_bias=0.10,
    ))
    objects.append(create_front_prism(collection, "LPCV17_Torso_shoulder_pelvis_prism", [
        (-0.379, 2.177), (-0.443, 2.077), (-0.364, 1.909), (-0.282, 1.841),
        (-0.243, 1.619), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.111, 2.141), (0.043, 2.302),
    ], y_center=-0.045, depth=0.34, mats=skin, shadow_bias=0.09))

    # Far arm and open palm use the actual outer silhouette points from the reference.
    objects.append(create_front_prism(collection, "LPCV17_Far_arm_forearm_prism", [
        (0.128, 1.677), (0.415, 1.680), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.245, depth=0.12, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV17_Far_open_palm_prism", [
        (0.415, 1.680), (0.486, 1.934), (0.468, 1.991), (0.418, 2.002), (0.361, 1.762),
    ], y_center=-0.310, depth=0.10, mats=skin, shadow_bias=0.08))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV17_Far_hand_surface",
        (0.430, -0.365, 1.855),
        width=0.075,
        height=0.210,
        depth=0.028,
        rotation_z=math.radians(-8),
        thumb_side=-1,
        mats=skin,
    ))

    # The near guard arm is mostly internal silhouette, so it stays as a raised surface over torso.
    objects.append(create_front_prism(collection, "LPCV17_Near_guard_upper_surface", [
        (-0.355, 1.900), (-0.080, 2.090), (-0.030, 2.000), (-0.260, 1.755),
    ], y_center=-0.245, depth=0.045, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV17_Near_guard_forearm_surface", [
        (-0.280, 1.770), (-0.030, 2.000), (0.022, 1.940), (-0.190, 1.650),
    ], y_center=-0.270, depth=0.050, mats=skin, shadow_bias=0.14))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV17_Near_guard_hand_surface",
        (0.032, -0.350, 2.020),
        width=0.082,
        height=0.225,
        depth=0.036,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    # Legs are separate semantic prisms following the extracted outer contour.
    objects.append(create_front_prism(collection, "LPCV17_Lead_leg_and_foot_prism", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.24, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV17_Rear_leg_and_foot_prism", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.24, mats=skin, shadow_bias=0.11))

    # Facet overlays recreate the low-poly instructional look without adding arbitrary anatomy.
    objects.append(create_front_prism(collection, "LPCV17_Chest_shadow_facet", [
        (-0.030, 1.820), (0.155, 1.610), (0.025, 1.545),
    ], y_center=-0.245, depth=0.018, mats=shadow, shadow_bias=0.24))
    objects.append(create_front_prism(collection, "LPCV18_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.115, depth=0.110, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "Primary user screenshot contour split into semantic low-poly body parts"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v17 contour-guided semantic prisms improve front silhouette while preserving editable parts"
    return objects


def create_hybrid_semantic_character_v20(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # v20 combines the best prior evidence:
    # - v17 contour-guided silhouette for body/pose
    # - v15 semantic mitten hands with palm/thumb/finger facets
    # - overlap transition pieces so it is not merely disconnected paper layers.
    objects.append(create_front_prism(collection, "LPCV20_Head_contour_faceted_prism", [
        (-0.035, 2.620), (-0.174, 2.565), (-0.178, 2.405), (-0.168, 2.273),
        (-0.052, 2.212), (0.052, 2.300), (0.094, 2.424), (0.068, 2.534),
    ], y_center=-0.12, depth=0.32, mats=skin, shadow_bias=0.06))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV20_Neck_overlap",
        (-0.055, -0.10, 2.150),
        (-0.050, -0.12, 2.280),
        (0.060, 0.052),
        (0.080, 0.062),
        skin,
        vertices_count=7,
        shadow_bias=0.10,
    ))
    objects.append(create_front_prism(collection, "LPCV20_Torso_contour_volume", [
        (-0.379, 2.177), (-0.443, 2.077), (-0.364, 1.909), (-0.282, 1.841),
        (-0.243, 1.619), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.111, 2.141), (0.043, 2.302),
    ], y_center=-0.045, depth=0.40, mats=skin, shadow_bias=0.09))

    # Add subtle depth masses behind the flat contour prism so the 3/4 view reads as a body.
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV20_Chest_depth_core",
        (-0.055, 0.010, 1.715),
        [(-0.20, 0.18, 0.12), (0.02, 0.245, 0.16), (0.18, 0.205, 0.12)],
        (math.radians(-2), 0.0, math.radians(-7)),
        skin,
        vertices_count=7,
        shadow_bias=0.16,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV20_Hip_depth_core",
        (-0.020, 0.005, 1.135),
        [(-0.12, 0.135, 0.10), (0.02, 0.190, 0.13), (0.13, 0.135, 0.10)],
        (math.radians(2), 0.0, math.radians(-6)),
        skin,
        vertices_count=7,
        shadow_bias=0.16,
    ))

    objects.append(create_front_prism(collection, "LPCV20_Far_arm_forearm_contour", [
        (0.128, 1.677), (0.415, 1.680), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.250, depth=0.14, mats=skin, shadow_bias=0.11))
    objects.append(create_ico_ellipsoid(collection, "LPCV20_Far_wrist_overlap", (0.385, -0.285, 1.720), (0.045, 0.040, 0.055), (0.0, 0.0, math.radians(-8)), skin, subdivisions=1, shadow_bias=0.09))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV20_Far_open_hand",
        (0.438, -0.350, 1.855),
        width=0.105,
        height=0.255,
        depth=0.070,
        rotation_z=math.radians(-8),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV20_Near_guard_upper_contour", [
        (-0.355, 1.900), (-0.080, 2.090), (-0.030, 2.000), (-0.260, 1.755),
    ], y_center=-0.255, depth=0.075, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV20_Near_guard_forearm_contour", [
        (-0.280, 1.770), (-0.030, 2.000), (0.022, 1.940), (-0.190, 1.650),
    ], y_center=-0.275, depth=0.080, mats=skin, shadow_bias=0.14))
    objects.append(create_ico_ellipsoid(collection, "LPCV20_Near_wrist_overlap", (-0.025, -0.310, 1.970), (0.042, 0.038, 0.052), (0.0, 0.0, math.radians(5)), skin, subdivisions=1, shadow_bias=0.09))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV20_Near_guard_hand",
        (0.032, -0.350, 2.020),
        width=0.092,
        height=0.238,
        depth=0.070,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV20_Lead_leg_and_foot_contour", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.28, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV20_Rear_leg_and_foot_contour", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.28, mats=skin, shadow_bias=0.11))
    objects.append(create_ico_ellipsoid(collection, "LPCV20_Lead_hip_overlap", (-0.080, -0.055, 1.170), (0.060, 0.052, 0.070), (0.0, 0.0, math.radians(-6)), skin, subdivisions=1, shadow_bias=0.09))
    objects.append(create_ico_ellipsoid(collection, "LPCV20_Rear_hip_overlap", (0.090, -0.055, 1.180), (0.060, 0.052, 0.070), (0.0, 0.0, math.radians(6)), skin, subdivisions=1, shadow_bias=0.09))

    objects.append(create_front_prism(collection, "LPCV20_Chest_shadow_facet", [
        (-0.030, 1.820), (0.155, 1.610), (0.025, 1.545),
    ], y_center=-0.260, depth=0.030, mats=shadow, shadow_bias=0.24))
    objects.append(create_front_prism(collection, "LPCV20_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.130, depth=0.130, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "v20 hybrid: v17 contour body/pose plus v15 semantic hand construction"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v20 combines contour silhouette, semantic mitten hands, wrist overlaps and body depth cores"
    return objects


def create_outline_hand_character_v21(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # Start from the best-measured v17 contour branch, then fix only local defects.
    objects.append(create_front_prism(collection, "LPCV21_Head_contour_prism", [
        (-0.035, 2.620), (-0.189, 2.559), (-0.168, 2.273), (0.043, 2.302), (0.093, 2.284), (0.068, 2.534),
    ], y_center=-0.12, depth=0.30, mats=skin, shadow_bias=0.06))
    objects.append(create_front_prism(collection, "LPCV21_Neck_short_prism", [
        (-0.100, 2.285), (0.020, 2.300), (0.020, 2.125), (-0.105, 2.115),
    ], y_center=-0.10, depth=0.22, mats=skin, shadow_bias=0.10))
    objects.append(create_front_prism(collection, "LPCV21_Torso_shoulder_pelvis_prism", [
        (-0.379, 2.177), (-0.443, 2.077), (-0.364, 1.909), (-0.282, 1.841),
        (-0.243, 1.619), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.111, 2.141), (0.043, 2.302),
    ], y_center=-0.045, depth=0.34, mats=skin, shadow_bias=0.09))

    objects.append(create_front_prism(collection, "LPCV21_Far_arm_forearm_prism", [
        (0.128, 1.677), (0.415, 1.680), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.245, depth=0.12, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV21_Far_open_palm_prism", [
        (0.415, 1.680), (0.486, 1.934), (0.468, 1.991), (0.418, 2.002), (0.361, 1.762),
    ], y_center=-0.310, depth=0.10, mats=skin, shadow_bias=0.08))
    objects.append(create_ico_ellipsoid(collection, "LPCV21_Far_wrist_overlap", (0.382, -0.300, 1.715), (0.030, 0.028, 0.040), (0.0, 0.0, math.radians(-8)), skin, subdivisions=1, shadow_bias=0.10))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV21_Far_hand_inner_facets",
        (0.430, -0.365, 1.855),
        width=0.070,
        height=0.195,
        depth=0.026,
        rotation_z=math.radians(-8),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV21_Near_guard_upper_surface", [
        (-0.355, 1.900), (-0.080, 2.090), (-0.030, 2.000), (-0.260, 1.755),
    ], y_center=-0.245, depth=0.045, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV21_Near_guard_forearm_surface", [
        (-0.280, 1.770), (-0.030, 2.000), (0.022, 1.940), (-0.190, 1.650),
    ], y_center=-0.270, depth=0.050, mats=skin, shadow_bias=0.14))
    objects.append(create_ico_ellipsoid(collection, "LPCV21_Near_wrist_overlap", (-0.025, -0.310, 1.970), (0.028, 0.026, 0.038), (0.0, 0.0, math.radians(5)), skin, subdivisions=1, shadow_bias=0.10))
    objects.extend(create_low_poly_mitten_hand(
        collection,
        "LPCV21_Near_hand_inner_facets",
        (0.032, -0.350, 2.020),
        width=0.074,
        height=0.205,
        depth=0.030,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV21_Lead_leg_and_foot_prism", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.24, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV21_Rear_leg_and_foot_prism", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.24, mats=skin, shadow_bias=0.11))

    objects.append(create_front_prism(collection, "LPCV21_Chest_shadow_facet", [
        (-0.030, 1.820), (0.155, 1.610), (0.025, 1.545),
    ], y_center=-0.245, depth=0.018, mats=shadow, shadow_bias=0.24))
    objects.append(create_front_prism(collection, "LPCV21_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.110, depth=0.120, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "v21 preserves v17 outer contour and adds hand detail inside silhouette"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v21 keeps the best outline, fixes floating groin shadow, adds small semantic hand facets"
    return objects


def create_hand_head_rebuild_v22(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # V22 keeps the best v17/v21 pose contour, but replaces the weakest parts:
    # the paper-flat head and sticker-like hands.
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV22_Head_faceted_volume",
        (-0.026, -0.132, 2.420),
        (0.145, 0.118, 0.270),
        (math.radians(-3), math.radians(2), math.radians(-5)),
        skin,
        subdivisions=1,
        shadow_bias=0.055,
    ))
    objects.append(create_front_prism(collection, "LPCV22_Head_front_plane", [
        (-0.121, 2.548), (0.043, 2.582), (0.083, 2.405), (0.044, 2.286), (-0.082, 2.300), (-0.132, 2.430),
    ], y_center=-0.274, depth=0.022, mats=skin, shadow_bias=0.065))
    objects.append(create_front_prism(collection, "LPCV22_Neck_trapezoid_overlap", [
        (-0.090, 2.310), (0.055, 2.305), (0.074, 2.115), (-0.112, 2.106),
    ], y_center=-0.118, depth=0.245, mats=skin, shadow_bias=0.11))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV22_Neck_to_chest_anchor",
        (-0.020, -0.108, 2.128),
        (0.092, 0.082, 0.070),
        (0.0, 0.0, math.radians(-4)),
        skin,
        subdivisions=1,
        shadow_bias=0.13,
    ))

    objects.append(create_front_prism(collection, "LPCV22_Torso_shoulder_pelvis_prism", [
        (-0.360, 2.160), (-0.420, 2.058), (-0.350, 1.910), (-0.270, 1.836),
        (-0.238, 1.612), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.095, 2.142), (0.074, 2.205),
    ], y_center=-0.045, depth=0.350, mats=skin, shadow_bias=0.09))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV22_Left_shoulder_volume",
        (-0.308, -0.090, 1.992),
        (0.075, 0.082, 0.086),
        (math.radians(-8), 0.0, math.radians(-15)),
        skin,
        subdivisions=1,
        shadow_bias=0.11,
    ))

    objects.append(create_front_prism(collection, "LPCV22_Far_arm_forearm_prism", [
        (0.128, 1.677), (0.398, 1.672), (0.365, 1.764), (0.186, 1.802),
    ], y_center=-0.245, depth=0.130, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV22_Far_wrist_bridge", [
        (0.367, 1.726), (0.433, 1.728), (0.439, 1.811), (0.387, 1.814),
    ], y_center=-0.300, depth=0.055, mats=skin, shadow_bias=0.12))
    objects.extend(create_low_poly_open_hand(
        collection,
        "LPCV22_Far_open_hand",
        (0.444, -0.356, 1.888),
        width=0.112,
        height=0.245,
        depth=0.044,
        rotation_z=math.radians(-8),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV22_Near_guard_upper_surface", [
        (-0.344, 1.902), (-0.082, 2.092), (-0.020, 2.018), (-0.252, 1.760),
    ], y_center=-0.245, depth=0.056, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV22_Near_guard_forearm_surface", [
        (-0.276, 1.762), (-0.020, 2.018), (0.035, 1.954), (-0.184, 1.648),
    ], y_center=-0.272, depth=0.058, mats=skin, shadow_bias=0.14))
    objects.append(create_front_prism(collection, "LPCV22_Near_wrist_bridge", [
        (-0.052, 1.960), (0.030, 1.958), (0.046, 2.028), (-0.018, 2.040),
    ], y_center=-0.315, depth=0.048, mats=skin, shadow_bias=0.12))
    objects.extend(create_low_poly_open_hand(
        collection,
        "LPCV22_Near_guard_hand",
        (0.044, -0.352, 2.040),
        width=0.092,
        height=0.208,
        depth=0.038,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV22_Lead_leg_and_foot_prism", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.250, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV22_Rear_leg_and_foot_prism", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.250, mats=skin, shadow_bias=0.11))

    objects.append(create_front_prism(collection, "LPCV22_Chest_shadow_facet", [
        (-0.035, 1.825), (0.145, 1.622), (0.026, 1.550),
    ], y_center=-0.250, depth=0.018, mats=shadow, shadow_bias=0.24))
    objects.append(create_front_prism(collection, "LPCV22_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.110, depth=0.120, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "v22 preserves the measured pose outline while rebuilding head, neck and open hands"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v22 hand/head rebuild: overlapping palm, thumb and four fingers; faceted head volume with neck anchor"
    return objects


def create_balanced_hand_head_v23(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # V23 is the repair pass after V22: no floating face plate, no thin comb fingers.
    objects.append(create_front_prism(collection, "LPCV23_Head_single_faceted_prism", [
        (-0.030, 2.620), (-0.150, 2.580), (-0.186, 2.455), (-0.160, 2.310),
        (-0.040, 2.270), (0.066, 2.316), (0.086, 2.508), (0.036, 2.590),
    ], y_center=-0.122, depth=0.315, mats=skin, shadow_bias=0.060))
    objects.append(create_front_prism(collection, "LPCV23_Neck_wide_overlap", [
        (-0.100, 2.300), (0.048, 2.306), (0.070, 2.118), (-0.112, 2.110),
    ], y_center=-0.112, depth=0.252, mats=skin, shadow_bias=0.105))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV23_Neck_socket_volume",
        (-0.024, -0.105, 2.132),
        (0.080, 0.075, 0.065),
        (0.0, 0.0, math.radians(-5)),
        skin,
        subdivisions=1,
        shadow_bias=0.12,
    ))

    objects.append(create_front_prism(collection, "LPCV23_Torso_shoulder_pelvis_prism", [
        (-0.372, 2.166), (-0.432, 2.067), (-0.356, 1.912), (-0.276, 1.840),
        (-0.242, 1.620), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.106, 2.140), (0.050, 2.242),
    ], y_center=-0.045, depth=0.345, mats=skin, shadow_bias=0.09))

    objects.append(create_front_prism(collection, "LPCV23_Far_arm_forearm_prism", [
        (0.128, 1.677), (0.405, 1.676), (0.365, 1.764), (0.186, 1.802),
    ], y_center=-0.245, depth=0.128, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV23_Far_wrist_bridge", [
        (0.368, 1.728), (0.429, 1.732), (0.435, 1.810), (0.386, 1.812),
    ], y_center=-0.302, depth=0.060, mats=skin, shadow_bias=0.12))
    objects.extend(create_low_poly_block_hand(
        collection,
        "LPCV23_Far_open_hand",
        (0.442, -0.352, 1.895),
        width=0.098,
        height=0.220,
        depth=0.052,
        rotation_z=math.radians(-8),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV23_Near_guard_upper_surface", [
        (-0.350, 1.902), (-0.082, 2.092), (-0.026, 2.018), (-0.258, 1.758),
    ], y_center=-0.245, depth=0.055, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV23_Near_guard_forearm_surface", [
        (-0.280, 1.766), (-0.026, 2.018), (0.032, 1.956), (-0.188, 1.650),
    ], y_center=-0.272, depth=0.056, mats=skin, shadow_bias=0.14))
    objects.append(create_front_prism(collection, "LPCV23_Near_wrist_bridge", [
        (-0.052, 1.960), (0.026, 1.962), (0.040, 2.030), (-0.018, 2.040),
    ], y_center=-0.315, depth=0.050, mats=skin, shadow_bias=0.12))
    objects.extend(create_low_poly_block_hand(
        collection,
        "LPCV23_Near_guard_hand",
        (0.040, -0.350, 2.032),
        width=0.080,
        height=0.178,
        depth=0.044,
        rotation_z=math.radians(5),
        thumb_side=-1,
        mats=skin,
    ))

    objects.append(create_front_prism(collection, "LPCV23_Lead_leg_and_foot_prism", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.245, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV23_Rear_leg_and_foot_prism", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.245, mats=skin, shadow_bias=0.11))

    objects.append(create_front_prism(collection, "LPCV23_Chest_shadow_facet", [
        (-0.032, 1.822), (0.150, 1.618), (0.025, 1.546),
    ], y_center=-0.248, depth=0.018, mats=shadow, shadow_bias=0.24))
    objects.append(create_front_prism(collection, "LPCV23_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.110, depth=0.120, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "v23 balances the measured v17/v21 outline with a cleaner single-piece faceted head and block hands"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v23 removes the v22 floating face plate and comb fingers while keeping readable palm, thumb and finger creases"
    return objects


def create_reference_locked_v24(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    skin_dark = [mats["grey_mid"], mats["grey_dark"], mats["joint_dark"]]
    shadow = [mats["joint_dark"], mats["grey_dark"], mats["joint_dark"]]
    objects: list[bpy.types.Object] = []

    # V24 returns to the best measured contour and treats hands as reference-style mitten blocks,
    # not anatomical spread fingers.
    objects.append(create_front_prism(collection, "LPCV24_Head_reference_prism", [
        (-0.035, 2.620), (-0.189, 2.559), (-0.168, 2.273), (0.043, 2.302), (0.093, 2.284), (0.068, 2.534),
    ], y_center=-0.120, depth=0.310, mats=skin, shadow_bias=0.055))
    objects.append(create_front_prism(collection, "LPCV24_Head_right_side_shadow_embedded", [
        (0.030, 2.570), (0.068, 2.534), (0.093, 2.284), (0.042, 2.304), (0.020, 2.455),
    ], y_center=-0.270, depth=0.035, mats=skin_dark, shadow_bias=0.18))
    objects.append(create_front_prism(collection, "LPCV24_Head_face_front_facet_embedded", [
        (-0.155, 2.520), (-0.030, 2.588), (0.018, 2.444), (-0.132, 2.342),
    ], y_center=-0.274, depth=0.030, mats=skin, shadow_bias=0.065))
    objects.append(create_front_prism(collection, "LPCV24_Neck_reference_overlap", [
        (-0.100, 2.285), (0.025, 2.302), (0.024, 2.124), (-0.105, 2.112),
    ], y_center=-0.102, depth=0.235, mats=skin, shadow_bias=0.10))

    objects.append(create_front_prism(collection, "LPCV24_Torso_shoulder_pelvis_reference", [
        (-0.379, 2.177), (-0.443, 2.077), (-0.364, 1.909), (-0.282, 1.841),
        (-0.243, 1.619), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.111, 2.141), (0.043, 2.302),
    ], y_center=-0.045, depth=0.345, mats=skin, shadow_bias=0.09))
    objects.append(create_front_prism(collection, "LPCV24_Left_chest_dark_slit", [
        (-0.300, 2.035), (-0.252, 1.805), (-0.226, 1.832), (-0.267, 2.040),
    ], y_center=-0.260, depth=0.026, mats=shadow, shadow_bias=0.34))
    objects.append(create_front_prism(collection, "LPCV24_Central_torso_shadow_panel", [
        (-0.035, 1.810), (0.154, 1.614), (0.040, 1.210), (-0.118, 1.560),
    ], y_center=-0.252, depth=0.026, mats=skin_dark, shadow_bias=0.18))

    objects.append(create_front_prism(collection, "LPCV24_Near_guard_upper_arm_reference", [
        (-0.355, 1.900), (-0.080, 2.090), (-0.030, 2.000), (-0.260, 1.755),
    ], y_center=-0.246, depth=0.052, mats=skin, shadow_bias=0.12))
    objects.append(create_front_prism(collection, "LPCV24_Near_guard_forearm_reference", [
        (-0.280, 1.770), (-0.030, 2.000), (0.020, 1.942), (-0.190, 1.650),
    ], y_center=-0.272, depth=0.055, mats=skin, shadow_bias=0.14))
    objects.append(create_front_prism(collection, "LPCV24_Near_guard_hand_mitten", [
        (-0.018, 1.940), (0.045, 1.966), (0.070, 2.135), (0.034, 2.202), (-0.012, 2.088),
    ], y_center=-0.316, depth=0.050, mats=skin, shadow_bias=0.09))
    objects.append(create_front_prism(collection, "LPCV24_Near_guard_hand_knuckle_facet", [
        (0.020, 1.996), (0.060, 2.055), (0.044, 2.155), (0.010, 2.070),
    ], y_center=-0.345, depth=0.018, mats=skin_dark, shadow_bias=0.18))

    objects.append(create_front_prism(collection, "LPCV24_Far_arm_forearm_reference", [
        (0.128, 1.677), (0.415, 1.680), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.245, depth=0.122, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV24_Far_open_palm_mitten", [
        (0.410, 1.680), (0.487, 1.932), (0.470, 1.992), (0.417, 2.004), (0.358, 1.764),
    ], y_center=-0.306, depth=0.115, mats=skin, shadow_bias=0.08))
    objects.append(create_front_prism(collection, "LPCV24_Far_palm_plane_shadow", [
        (0.432, 1.740), (0.480, 1.908), (0.456, 1.966), (0.405, 1.770),
    ], y_center=-0.366, depth=0.020, mats=skin_dark, shadow_bias=0.16))
    objects.append(create_front_prism(collection, "LPCV24_Far_thumb_low_poly_notch", [
        (0.372, 1.742), (0.417, 1.760), (0.400, 1.836), (0.358, 1.802),
    ], y_center=-0.365, depth=0.026, mats=skin, shadow_bias=0.12))

    objects.append(create_front_prism(collection, "LPCV24_Lead_leg_and_foot_reference", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.060, depth=0.245, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV24_Rear_leg_and_foot_reference", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.055, depth=0.245, mats=skin, shadow_bias=0.11))
    objects.append(create_front_prism(collection, "LPCV24_Lead_leg_inner_shadow_facet", [
        (-0.298, 1.050), (-0.196, 0.740), (-0.326, 0.706),
    ], y_center=-0.186, depth=0.020, mats=skin_dark, shadow_bias=0.18))
    objects.append(create_front_prism(collection, "LPCV24_Rear_knee_shadow_facet", [
        (0.170, 0.830), (0.256, 0.720), (0.200, 0.575),
    ], y_center=-0.182, depth=0.020, mats=skin_dark, shadow_bias=0.18))

    objects.append(create_front_prism(collection, "LPCV24_Groin_shadow_facet_overlap", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.110, depth=0.120, mats=shadow, shadow_bias=0.25))

    for obj in objects:
        obj["source_reference"] = "v24 reference-locked pass: v21 contour, embedded head facets, mitten hands, and internal low-poly shadow planes"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v24 prioritizes screenshot likeness and low-poly hand readability over anatomical finger detail"
    return objects


def create_reference_relief_repaired_v25(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))
    contour = [(float(point["x"]), float(point["z"])) for point in payload["contour"]]
    if len(contour) < 8:
        raise ValueError("Silhouette contour is too small for the reference relief")

    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    subtle = [mats["grey_light"], mats["grey_mid"], mats["grey_light"]]
    accent = [mats["grey_mid"], mats["grey_light"], mats["grey_dark"]]
    shadow = [mats["grey_dark"], mats["joint_dark"], mats["grey_dark"]]
    objects: list[bpy.types.Object] = []

    objects.append(create_front_prism(
        collection,
        "LPCV25_Single_connected_reference_silhouette",
        contour,
        y_center=-0.020,
        depth=0.280,
        mats=skin,
        shadow_bias=0.070,
    ))

    # Corrected surface facets: all are embedded in the reference silhouette, so no detached right-hand bar.
    objects.append(create_front_prism(collection, "LPCV25_Head_left_light_plane", [
        (-0.164, 2.542), (-0.038, 2.612), (0.020, 2.470), (-0.142, 2.355),
    ], y_center=-0.174, depth=0.020, mats=subtle, shadow_bias=0.050))
    objects.append(create_front_prism(collection, "LPCV25_Head_right_shadow_plane", [
        (0.020, 2.560), (0.068, 2.535), (0.088, 2.300), (0.040, 2.310), (0.018, 2.455),
    ], y_center=-0.176, depth=0.020, mats=accent, shadow_bias=0.120))

    objects.append(create_front_prism(collection, "LPCV25_Near_guard_upper_arm_facet", [
        (-0.352, 1.902), (-0.082, 2.086), (-0.034, 2.000), (-0.260, 1.758),
    ], y_center=-0.176, depth=0.020, mats=accent, shadow_bias=0.105))
    objects.append(create_front_prism(collection, "LPCV25_Near_guard_forearm_facet", [
        (-0.278, 1.770), (-0.034, 2.000), (0.024, 1.944), (-0.188, 1.650),
    ], y_center=-0.178, depth=0.020, mats=subtle, shadow_bias=0.085))
    objects.append(create_front_prism(collection, "LPCV25_Near_vertical_hand_facet", [
        (-0.010, 1.958), (0.045, 1.980), (0.066, 2.132), (0.033, 2.182), (-0.006, 2.076),
    ], y_center=-0.182, depth=0.018, mats=accent, shadow_bias=0.095))

    objects.append(create_front_prism(collection, "LPCV25_Far_forearm_facet_corrected", [
        (0.128, 1.677), (0.415, 1.680), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.176, depth=0.022, mats=accent, shadow_bias=0.100))
    objects.append(create_front_prism(collection, "LPCV25_Far_open_palm_facet_corrected", [
        (0.414, 1.682), (0.486, 1.934), (0.468, 1.990), (0.418, 2.000), (0.361, 1.762),
    ], y_center=-0.180, depth=0.020, mats=subtle, shadow_bias=0.070))
    objects.append(create_front_prism(collection, "LPCV25_Far_thumb_shadow_notch", [
        (0.370, 1.742), (0.418, 1.770), (0.401, 1.846), (0.358, 1.804),
    ], y_center=-0.184, depth=0.016, mats=accent, shadow_bias=0.115))

    objects.append(create_front_prism(collection, "LPCV25_Chest_center_plane", [
        (-0.034, 1.824), (0.158, 1.620), (0.060, 1.290), (-0.116, 1.555),
    ], y_center=-0.174, depth=0.020, mats=accent, shadow_bias=0.115))
    objects.append(create_front_prism(collection, "LPCV25_Left_armpit_dark_slit", [
        (-0.304, 2.020), (-0.258, 1.802), (-0.228, 1.826), (-0.270, 2.025),
    ], y_center=-0.184, depth=0.016, mats=shadow, shadow_bias=0.190))
    objects.append(create_front_prism(collection, "LPCV25_Groin_dark_triangle", [
        (-0.004, 1.095), (0.118, 0.912), (-0.040, 0.925),
    ], y_center=-0.184, depth=0.016, mats=shadow, shadow_bias=0.180))

    objects.append(create_front_prism(collection, "LPCV25_Lead_thigh_light_plane", [
        (-0.236, 1.350), (-0.152, 1.050), (-0.278, 0.660), (-0.338, 1.070),
    ], y_center=-0.174, depth=0.018, mats=subtle, shadow_bias=0.055))
    objects.append(create_front_prism(collection, "LPCV25_Lead_shin_dark_plane", [
        (-0.384, 0.724), (-0.330, 0.690), (-0.488, 0.270), (-0.482, 0.470),
    ], y_center=-0.178, depth=0.018, mats=accent, shadow_bias=0.115))
    objects.append(create_front_prism(collection, "LPCV25_Rear_thigh_mid_plane", [
        (0.028, 1.122), (0.188, 0.882), (0.130, 0.820), (0.006, 1.010),
    ], y_center=-0.174, depth=0.018, mats=accent, shadow_bias=0.100))
    objects.append(create_front_prism(collection, "LPCV25_Rear_shin_light_plane", [
        (0.126, 0.802), (0.238, 0.700), (0.190, 0.398), (0.112, 0.458),
    ], y_center=-0.174, depth=0.018, mats=subtle, shadow_bias=0.055))
    objects.append(create_front_prism(collection, "LPCV25_Rear_foot_top_plane", [
        (0.062, 0.318), (0.372, 0.252), (0.348, 0.305), (0.214, 0.344),
    ], y_center=-0.176, depth=0.016, mats=subtle, shadow_bias=0.045))

    for obj in objects:
        obj["source_reference"] = "v25 repaired reference relief: exact mask silhouette plus corrected embedded low-poly facets"
        obj["target_mode"] = "FRONT_2_5D_HYBRID_HERO"
        obj["quality_focus"] = "v25 fixes detached right-hand accent, keeps hands mitten-style, and adds head/limb facets in reference positions"
        obj["mask_json"] = str(MASK_JSON)
    return objects


def create_reference_projection_v26(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing primary reference image: {REFERENCE}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))

    front_mat = material_reference_emission("LPCV26_Mat_reference_projected_front", REFERENCE, strength=0.92)
    side_mat = material_principled("LPCV26_Mat_reference_cutout_side_gray", (0.46, 0.51, 0.51, 1.0), roughness=0.70)

    obj = create_textured_reference_cutout(
        collection,
        "LPCV26_Textured_reference_cutout_single_mesh",
        payload,
        y_center=-0.035,
        depth=0.220,
        front_mat=front_mat,
        side_mat=side_mat,
    )
    obj["source_reference"] = "v26 exact 2.5D reference projection from the user's screenshot and extracted silhouette"
    obj["target_mode"] = "FRONT_2_5D_REFERENCE_PROJECTION"
    obj["quality_focus"] = "v26 prioritizes practical resemblance: exact front image projection, clean silhouette, GLB-ready thickness"
    obj["mask_json"] = str(MASK_JSON)
    obj["reference_image"] = str(REFERENCE)
    return [obj]


def create_projection_depth_hybrid_v27(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing primary reference image: {REFERENCE}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))

    front_mat = material_reference_emission("LPCV29_Mat_reference_projected_front", REFERENCE, strength=0.94)
    shell_side_mat = material_principled("LPCV29_Mat_projection_shell_edge", (0.43, 0.49, 0.50, 1.0), roughness=0.72)
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["grey_dark"], mats["joint_dark"], mats["grey_dark"]]
    objects: list[bpy.types.Object] = []

    objects.append(create_textured_reference_cutout(
        collection,
        "LPCV29_Textured_reference_thin_shell",
        payload,
        y_center=-0.240,
        depth=0.020,
        front_mat=front_mat,
        side_mat=shell_side_mat,
    ))
    objects.append(create_faceted_box(
        collection,
        "LPCV32_Hidden_shell_to_body_contact_core",
        (-0.045, -0.215, 1.540),
        (0.055, 0.060, 0.360),
        (math.radians(-2), 0.0, math.radians(-5)),
        [shell_side_mat],
        shadow_bias=0.040,
    ))

    # Behind-the-front semantic volumes. The texture wins from the front, while 3/4 and side views get real thickness.
    objects.append(create_front_prism(collection, "LPCV29_Depth_head_block", [
        (-0.035, 2.620), (-0.189, 2.559), (-0.168, 2.273), (0.043, 2.302), (0.093, 2.284), (0.068, 2.534),
    ], y_center=-0.065, depth=0.260, mats=skin, shadow_bias=0.070))
    objects.append(create_front_prism(collection, "LPCV29_Depth_neck_block", [
        (-0.100, 2.285), (0.025, 2.302), (0.024, 2.124), (-0.105, 2.112),
    ], y_center=-0.085, depth=0.220, mats=skin, shadow_bias=0.095))
    objects.append(create_front_prism(collection, "LPCV29_Depth_torso_block", [
        (-0.379, 2.177), (-0.443, 2.077), (-0.364, 1.909), (-0.282, 1.841),
        (-0.243, 1.619), (-0.250, 1.409), (-0.336, 1.076), (-0.039, 1.176),
        (0.014, 1.169), (0.100, 1.491), (0.129, 1.677), (0.186, 1.802),
        (0.164, 2.070), (0.111, 2.141), (0.043, 2.302),
    ], y_center=-0.025, depth=0.340, mats=skin, shadow_bias=0.095))
    objects.append(create_front_prism(collection, "LPCV29_Depth_near_guard_arm", [
        (-0.355, 1.900), (-0.080, 2.090), (-0.030, 2.000), (-0.260, 1.755),
        (-0.190, 1.650), (0.020, 1.942),
    ], y_center=-0.135, depth=0.120, mats=skin, shadow_bias=0.105))
    objects.append(create_front_prism(collection, "LPCV29_Depth_far_arm_and_palm", [
        (0.128, 1.677), (0.415, 1.680), (0.486, 1.934), (0.468, 1.991),
        (0.418, 2.002), (0.361, 1.762), (0.186, 1.802),
    ], y_center=-0.128, depth=0.135, mats=skin, shadow_bias=0.100))
    objects.append(create_front_prism(collection, "LPCV29_Depth_lead_leg", [
        (-0.250, 1.409), (-0.336, 1.076), (-0.343, 0.783), (-0.429, 0.705),
        (-0.490, 0.290), (-0.486, 0.111), (-0.411, 0.054), (-0.307, 0.047),
        (-0.368, 0.290), (-0.039, 1.176),
    ], y_center=-0.073, depth=0.245, mats=skin, shadow_bias=0.105))
    objects.append(create_front_prism(collection, "LPCV29_Depth_rear_leg", [
        (0.014, 1.169), (0.179, 0.912), (0.132, 0.819), (0.111, 0.455),
        (0.064, 0.319), (0.372, 0.251), (0.350, 0.304), (0.214, 0.344),
        (0.193, 0.397), (0.239, 0.723), (0.329, 0.869), (0.272, 1.176), (0.100, 1.491),
    ], y_center=-0.088, depth=0.245, mats=skin, shadow_bias=0.105))
    objects.append(create_front_prism(collection, "LPCV29_Depth_groin_shadow", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.173, depth=0.045, mats=shadow, shadow_bias=0.200))

    for obj in objects:
        obj["source_reference"] = "v29 hybrid: QA-contact thin textured projection shell plus semantic depth volumes behind it"
        obj["target_mode"] = "FRONT_PROJECTED_HYBRID_DEPTH"
        obj["quality_focus"] = "v29 keeps v26 front likeness, improves 3/4 readability, and moves depth volumes forward to contact the projection shell"
        obj["mask_json"] = str(MASK_JSON)
        obj["reference_image"] = str(REFERENCE)
    return objects


def create_projection_anatomy_depth_v30(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing primary reference image: {REFERENCE}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))

    front_mat = material_reference_emission("LPCV33_Mat_reference_projected_front", REFERENCE, strength=0.94)
    shell_side_mat = material_principled("LPCV33_Mat_projection_shell_edge", (0.42, 0.48, 0.49, 1.0), roughness=0.72)
    skin = [mats["grey_light"], mats["grey_mid"], mats["grey_dark"]]
    shadow = [mats["grey_dark"], mats["joint_dark"], mats["grey_dark"]]
    objects: list[bpy.types.Object] = []

    objects.append(create_textured_reference_cutout(
        collection,
        "LPCV33_Textured_reference_front_shell",
        payload,
        y_center=-0.240,
        depth=0.020,
        front_mat=front_mat,
        side_mat=shell_side_mat,
    ))
    objects.append(create_faceted_box(
        collection,
        "LPCV33_Hidden_shell_to_body_contact_core",
        (-0.045, -0.215, 1.540),
        (0.055, 0.060, 0.360),
        (math.radians(-2), 0.0, math.radians(-5)),
        [shell_side_mat],
        shadow_bias=0.040,
    ))

    # Rounded low-poly masses behind the projection shell. The centers are pulled forward
    # so the shell is structurally connected but still visually dominates the front render.
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV31_Head_faceted_depth_volume",
        (-0.052, -0.073, 2.430),
        (0.145, 0.132, 0.260),
        (math.radians(-2), math.radians(2), math.radians(-6)),
        skin,
        subdivisions=1,
        shadow_bias=0.075,
    ))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Neck_short_overlap_volume",
        (-0.062, -0.155, 2.140),
        (-0.048, -0.147, 2.300),
        (0.070, 0.050),
        (0.088, 0.058),
        skin,
        vertices_count=7,
        shadow_bias=0.100,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV31_Torso_chest_abdomen_depth_volume",
        (-0.035, -0.020, 1.600),
        [
            (-0.455, 0.170, 0.135),
            (-0.200, 0.245, 0.165),
            (0.135, 0.285, 0.185),
            (0.430, 0.210, 0.155),
        ],
        (math.radians(-2), 0.0, math.radians(-4)),
        skin,
        vertices_count=8,
        shadow_bias=0.090,
    ))
    objects.append(create_stacked_poly_volume(
        collection,
        "LPCV31_Pelvis_depth_volume",
        (0.010, -0.060, 1.070),
        [
            (-0.135, 0.165, 0.125),
            (0.030, 0.205, 0.145),
            (0.190, 0.155, 0.115),
        ],
        (math.radians(2), 0.0, math.radians(-4)),
        skin,
        vertices_count=7,
        shadow_bias=0.105,
    ))

    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Near_guard_upper_arm_depth",
        (-0.330, -0.153, 1.925),
        (-0.205, -0.161, 1.720),
        (0.075, 0.052),
        (0.060, 0.044),
        skin,
        vertices_count=7,
        shadow_bias=0.105,
    ))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Near_guard_forearm_depth",
        (-0.205, -0.163, 1.720),
        (0.018, -0.171, 2.020),
        (0.058, 0.042),
        (0.045, 0.034),
        skin,
        vertices_count=7,
        shadow_bias=0.115,
    ))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV31_Near_hand_mitten_depth",
        (0.030, -0.173, 2.060),
        (0.045, 0.032, 0.108),
        (math.radians(4), 0.0, math.radians(4)),
        skin,
        subdivisions=1,
        shadow_bias=0.095,
    ))

    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Far_forearm_depth",
        (0.160, -0.153, 1.730),
        (0.390, -0.166, 1.735),
        (0.060, 0.044),
        (0.052, 0.038),
        skin,
        vertices_count=7,
        shadow_bias=0.105,
    ))
    objects.append(create_ico_ellipsoid(
        collection,
        "LPCV31_Far_open_palm_depth",
        (0.430, -0.169, 1.875),
        (0.050, 0.036, 0.125),
        (math.radians(-2), 0.0, math.radians(-8)),
        skin,
        subdivisions=1,
        shadow_bias=0.080,
    ))

    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Lead_thigh_depth",
        (-0.110, -0.127, 1.090),
        (-0.310, -0.141, 0.735),
        (0.105, 0.078),
        (0.090, 0.064),
        skin,
        vertices_count=7,
        shadow_bias=0.105,
    ))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Lead_shin_depth",
        (-0.310, -0.143, 0.735),
        (-0.430, -0.159, 0.145),
        (0.082, 0.058),
        (0.065, 0.046),
        skin,
        vertices_count=7,
        shadow_bias=0.110,
    ))
    objects.append(create_faceted_box(
        collection,
        "LPCV31_Lead_foot_depth_wedge",
        (-0.392, -0.168, 0.080),
        (0.205, 0.070, 0.070),
        (math.radians(2), math.radians(-4), math.radians(-8)),
        skin,
        shadow_bias=0.090,
    ))

    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Rear_thigh_depth",
        (0.070, -0.130, 1.080),
        (0.245, -0.145, 0.830),
        (0.102, 0.074),
        (0.086, 0.060),
        skin,
        vertices_count=7,
        shadow_bias=0.105,
    ))
    objects.append(create_elliptic_frustum_between(
        collection,
        "LPCV31_Rear_shin_depth",
        (0.245, -0.145, 0.830),
        (0.135, -0.159, 0.330),
        (0.082, 0.058),
        (0.066, 0.046),
        skin,
        vertices_count=7,
        shadow_bias=0.110,
    ))
    objects.append(create_faceted_box(
        collection,
        "LPCV31_Rear_foot_depth_wedge",
        (0.232, -0.168, 0.290),
        (0.235, 0.070, 0.055),
        (math.radians(1), math.radians(-3), math.radians(8)),
        skin,
        shadow_bias=0.080,
    ))
    objects.append(create_front_prism(collection, "LPCV31_Groin_contact_shadow", [
        (-0.005, 1.095), (0.120, 0.910), (-0.040, 0.925),
    ], y_center=-0.190, depth=0.028, mats=shadow, shadow_bias=0.200))

    for obj in objects:
        if obj.name.startswith("LPCV31_"):
            shrink_mesh_world_xz(obj, anchor_x=0.0, anchor_z=1.34, scale_x=0.78, scale_z=0.93)

    for obj in objects:
        obj["source_reference"] = "v34 hybrid: front-locked textured shell plus shrunken rounded low-poly semantic depth volumes"
        obj["target_mode"] = "HYBRID_HERO"
        obj["quality_focus"] = "v34 shrinks internal anatomy-depth objects in x/z so they stop breaking the front reference projection"
        obj["mask_json"] = str(MASK_JSON)
        obj["reference_image"] = str(REFERENCE)
    return objects


def create_chamfered_projection_v35(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    if not MASK_JSON.exists():
        raise FileNotFoundError(f"Missing silhouette mask JSON: {MASK_JSON}")
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing primary reference image: {REFERENCE}")
    payload = json.loads(MASK_JSON.read_text(encoding="utf-8"))

    front_mat = material_reference_emission("LPCV35_Mat_reference_projected_front", REFERENCE, strength=0.94)
    side_mat = material_principled("LPCV35_Mat_chamfered_side_low_poly_gray", (0.42, 0.48, 0.49, 1.0), roughness=0.72)
    obj = create_textured_reference_chamfered_cutout(
        collection,
        "LPCV35_Chamfered_reference_projection_single_mesh",
        payload,
        rings=[
            (-0.245, 1.000, 1.000),
            (-0.120, 0.955, 0.985),
            (0.030, 0.885, 0.945),
        ],
        front_mat=front_mat,
        side_mat=side_mat,
    )
    obj["source_reference"] = "v35 chamfered projection: exact front silhouette/texture plus tapered low-poly side thickness"
    obj["target_mode"] = "HYBRID_HERO"
    obj["quality_focus"] = "v35 preserves v26/v29 front likeness while improving side/3-4 readability without protruding semantic volumes"
    obj["mask_json"] = str(MASK_JSON)
    obj["reference_image"] = str(REFERENCE)
    return [obj]


def create_preview_stage(scene: bpy.types.Scene, collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    floor = create_faceted_box(
        collection,
        "LPC_Preview_floor_red_not_exported",
        (0.0, 0.0, -0.045),
        (2.8, 2.2, 0.035),
        (0.0, 0.0, 0.0),
        [mats["floor"]],
        exportable=False,
    )
    floor.hide_render = True

    key_data = bpy.data.lights.new("LPC_Key_large_softbox_data", "AREA")
    key_data.energy = 380
    key_data.size = 4.0
    key = bpy.data.objects.new("LPC_Key_large_softbox_not_exported", key_data)
    key.location = (-2.0, -3.6, 4.0)
    collection.objects.link(key)
    set_exportable(key, False)

    fill_data = bpy.data.lights.new("LPC_Cool_fill_data", "AREA")
    fill_data.energy = 80
    fill_data.size = 5.5
    fill_data.color = (0.62, 0.76, 1.0)
    fill = bpy.data.objects.new("LPC_Cool_fill_not_exported", fill_data)
    fill.location = (3.0, -2.0, 2.8)
    collection.objects.link(fill)
    set_exportable(fill, False)

    rim_data = bpy.data.lights.new("LPC_Rim_light_data", "POINT")
    rim_data.energy = 120
    rim_data.shadow_soft_size = 3.0
    rim = bpy.data.objects.new("LPC_Rim_light_not_exported", rim_data)
    rim.location = (1.6, 2.8, 3.0)
    collection.objects.link(rim)
    set_exportable(rim, False)

    camera_data = bpy.data.cameras.new("LPC_Camera_data")
    camera = bpy.data.objects.new("LPC_Camera_not_exported", camera_data)
    camera.location = (0.6, -5.0, 1.55)
    look_at(camera, Vector((0.02, -0.12, 1.28)))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 3.20
    if REFERENCE.exists():
        camera_data.show_background_images = True
        bg = camera_data.background_images.new()
        bg.image = bpy.data.images.load(str(REFERENCE))
        bg.alpha = 0.16
    collection.objects.link(camera)
    set_exportable(camera, False)
    scene.camera = camera

    world = scene.world or bpy.data.worlds.new("LPC_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.24, 0.24, 0.23, 1.0)
        bg_node.inputs["Strength"].default_value = 0.42
    return camera


def render_to(scene: bpy.types.Scene, camera: bpy.types.Object, path: Path, *, view: str) -> None:
    if view == "front":
        camera.location = (0.0, -5.2, 1.55)
        look_at(camera, Vector((0.02, -0.12, 1.28)))
        camera.data.ortho_scale = 3.20
    elif view == "side":
        camera.location = (5.2, 0.0, 1.55)
        look_at(camera, Vector((0.02, -0.12, 1.28)))
        camera.data.ortho_scale = 3.20
    elif view == "back":
        camera.location = (0.0, 5.2, 1.55)
        look_at(camera, Vector((0.02, -0.12, 1.28)))
        camera.data.ortho_scale = 3.20
    else:
        camera.location = (0.6, -5.0, 1.55)
        look_at(camera, Vector((0.02, -0.12, 1.28)))
        camera.data.ortho_scale = 3.20
    scene.camera = camera
    scene.render.filepath = str(ensure_allowed_path(path))
    bpy.ops.render.render(write_still=True)


def mesh_triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            total += sum(len(poly.vertices) - 2 for poly in mesh.polygons)
        finally:
            evaluated.to_mesh_clear()
    return total


def validation_report(export_objects: list[bpy.types.Object]) -> dict:
    triangles = mesh_triangle_count(export_objects)
    errors: list[str] = []
    warnings: list[str] = []
    if not export_objects:
        errors.append("No exportable objects")
    if triangles > TRIANGLE_BUDGET:
        warnings.append(f"Triangle count {triangles} exceeds target {TRIANGLE_BUDGET}")
    for obj in export_objects:
        if obj.type == "MESH" and not obj.data.materials:
            errors.append(f"{obj.name}: missing material")
        if any(value < 0 for value in obj.scale):
            warnings.append(f"{obj.name}: negative scale")
    return {
        "schema_version": "1.0",
        "asset": ASSET,
        "triangles": triangles,
        "object_count": len(export_objects),
        "errors": errors,
        "warnings": warnings,
        "export_objects": [obj.name for obj in export_objects],
    }


def write_scene_graph(path: Path) -> dict:
    graph = {
        "schema_version": "1.0",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "primary_reference": str(REFERENCE),
        "mask_json": str(MASK_JSON),
        "goal": "Chamfered projection low-poly humanoid from the user's primary fighting-pose screenshot: exact textured front silhouette with tapered low-poly side thickness for better 3/4 readability.",
        "parts": [
            {"id": "reference_projection", "name": "LPCV35_Chamfered_reference_projection_single_mesh", "material_group": "image_projected_front_plus_chamfered_gray_sides", "source_confidence": 0.98},
            {"id": "side_depth", "name": "Three-ring tapered contour shell", "material_group": "faceted_low_poly_side", "source_confidence": 0.90},
            {"id": "silhouette", "name": "Reference mask contour from silhouette_contour.json", "material_group": "mesh_boundary", "source_confidence": 0.96},
            {"id": "front_texture", "name": "low_poly_character_fighting_pose_primary.png", "material_group": "emission_reference_texture", "source_confidence": 0.98},
        ],
        "relations": [
            {"a": "head", "type": "TOUCHES", "b": "torso", "tolerance": 0.08},
            {"a": "near_hand", "type": "OVERLAPS", "b": "arms", "minimum_overlap": 0.01},
            {"a": "far_hand", "type": "OVERLAPS", "b": "arms", "minimum_overlap": 0.01},
            {"a": "legs_feet", "type": "TOUCHES", "b": "torso", "tolerance": 0.10},
        ],
        "acceptance": {
            "must_have": [
                "editable hybrid semantic contour-guided low-poly parts",
                "hands built from palm, thumb and unequal embedded finger facets with wrist overlap",
                "faceted low-poly grey material with shallow occlusion facets",
                "upright fighting/guard pose",
                "near vertical hand at face and far vertical palm",
                "staggered standing legs and wedge feet visible in silhouette",
                "GLB exports only character mesh, not floor/camera/lights/reference",
                "hidden back side is inferred; target is contour-guided HYBRID_HERO, not true 360 reconstruction",
            ],
            "triangle_budget": TRIANGLE_BUDGET,
        },
    }
    write_json(path, graph)
    return graph


def export_glb(path: Path, objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(ensure_allowed_path(path)),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )


def main() -> None:
    scene, collection, mats = setup_scene()
    scene_graph_path = REPORTS / f"{ASSET}_scene_graph.json"
    write_scene_graph(scene_graph_path)

    create_chamfered_projection_v35(collection, mats)
    camera = create_preview_stage(scene, collection, mats)
    bpy.context.view_layer.update()

    export_objects = [obj for obj in collection.objects if obj.type == "MESH" and bool(obj.get("abt_export", False))]
    qa_path = REPORTS / f"{ASSET}_structural_qa.json"
    write_json(qa_path, scene_qa.audit_scene([obj.name for obj in export_objects]))

    validation = validation_report(export_objects)
    validation_path = REPORTS / f"{ASSET}_validation.json"
    write_json(validation_path, validation)
    if validation["errors"]:
        raise RuntimeError("Validation errors: " + "; ".join(validation["errors"]))

    render_main = RENDERS / f"{ASSET}_01_front_3q.png"
    render_front = RENDERS / f"{ASSET}_02_front.png"
    render_side = RENDERS / f"{ASSET}_03_side.png"
    render_back = RENDERS / f"{ASSET}_04_back.png"
    render_to(scene, camera, render_main, view="front_3q")
    render_to(scene, camera, render_front, view="front")
    render_to(scene, camera, render_side, view="side")
    render_to(scene, camera, render_back, view="back")

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(ensure_allowed_path(blend_path)))

    glb_path = EXPORTS / f"{ASSET}.glb"
    export_glb(glb_path, export_objects)
    public_glb = PUBLIC_MODELS / f"{ASSET}.glb"
    shutil.copy2(glb_path, public_glb)

    scene_report = {
        "schema_version": "1.0",
        "asset": ASSET,
        "scene": scene.name,
        "source_video": "https://www.youtube.com/watch?v=J-nbY8B2oa4",
        "reference": str(REFERENCE),
        "blend": str(blend_path),
        "glb": str(glb_path),
        "public_glb": str(public_glb),
        "renders": [str(render_main), str(render_front), str(render_side), str(render_back)],
        "reports": [str(scene_graph_path), str(qa_path), str(validation_path)],
        "triangles": validation["triangles"],
        "object_count": validation["object_count"],
        "warnings": validation["warnings"],
        "notes": [
            "Built from scratch as a separate Blender file.",
            "Video transcript/download failed with YouTube connection reset; the user screenshot is the primary visual reference for this pass.",
            "Target mode HYBRID_HERO: front and limited 3/4 pose are targeted; hidden back details are inferred as a clean low-poly mannequin.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", scene_report)
    print(json.dumps(scene_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
