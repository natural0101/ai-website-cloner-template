from __future__ import annotations

import json
import math
import random
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Matrix, Vector


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
WORKBENCH = REPO / "blender-workbench"
RESEARCH_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
PUBLIC_MODELS = REPO / "public" / "models"

for directory in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    directory.mkdir(parents=True, exist_ok=True)

if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import scene_qa


ASSET = "donut_2025_video_reference_v2"
SCENE_NAME = "Donut2025VideoReferenceScene"
COLLECTION_NAME = "ABT_DONUT_VIDEO_REFERENCE"
PRIMARY_REFERENCE = Path(r"C:\Users\se-20\AppData\Local\Temp\codex-clipboard-45d00342-9938-4a19-ad7b-ed92b91ada44.png")
WIDTH = 1600
HEIGHT = 900
TRIANGLE_BUDGET = 120_000
RANDOM_SEED = 20250623

DONUT_CENTER = Vector((-1.05, 0.02, 0.36))
MUG_CENTER = Vector((1.14, 0.10, 0.0))

random.seed(RANDOM_SEED)


def ensure_allowed_path(path: Path) -> Path:
    resolved = path.resolve()
    allowed = [REPO.resolve()]
    if not any(resolved == root or root in resolved.parents for root in allowed):
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


def material_principled(
    name: str,
    base_color: Sequence[float],
    *,
    roughness: float = 0.55,
    metallic: float = 0.0,
    alpha: float = 1.0,
    emission: Sequence[float] | None = None,
    emission_strength: float = 0.0,
    subsurface_weight: float = 0.0,
    subsurface_scale: float = 0.05,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (base_color[0], base_color[1], base_color[2], alpha)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (base_color[0], base_color[1], base_color[2], alpha)
        for socket_name in ("Alpha",):
            if socket_name in bsdf.inputs:
                bsdf.inputs[socket_name].default_value = alpha
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = subsurface_weight
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = subsurface_weight
        if "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = subsurface_scale
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.75, 0.45)
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
    return mat


def apply_noise_color(
    mat: bpy.types.Material,
    dark: Sequence[float],
    light: Sequence[float],
    *,
    scale: float,
    detail: float = 10.0,
    bump_strength: float = 0.06,
    bump_distance: float = 0.07,
) -> bpy.types.Material:
    if not mat.use_nodes or mat.node_tree is None:
        return mat
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return mat

    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{mat.name}_mottle_noise"
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.58

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = f"{mat.name}_mottle_ramp"
    ramp.color_ramp.elements[0].position = 0.24
    ramp.color_ramp.elements[0].color = (dark[0], dark[1], dark[2], 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (light[0], light[1], light[2], 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    if "Base Color" in bsdf.inputs:
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    bump_noise = nodes.new("ShaderNodeTexNoise")
    bump_noise.name = f"{mat.name}_fine_bump_noise"
    bump_noise.inputs["Scale"].default_value = scale * 3.2
    bump_noise.inputs["Detail"].default_value = detail + 3.0
    bump_noise.inputs["Roughness"].default_value = 0.64
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"{mat.name}_fine_bump"
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    links.new(bump_noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def smooth_mesh(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def add_modifier(obj: bpy.types.Object, name: str, mod_type: str, **kwargs) -> bpy.types.Modifier:
    mod = obj.modifiers.new(name, mod_type)
    for key, value in kwargs.items():
        if hasattr(mod, key):
            setattr(mod, key, value)
    return mod


def torus_point(u: float, v: float, R: float, r: float, lump: float = 0.0) -> Vector:
    radial_noise = (
        0.04 * math.sin(3.0 * u + 0.8)
        + 0.025 * math.sin(7.0 * u - 1.2)
        + 0.018 * math.sin(5.0 * v + 2.0 * u)
    ) * lump
    tube_noise = (
        0.035 * math.sin(4.0 * u + 1.5 * v)
        + 0.015 * math.sin(9.0 * u - 0.4)
    ) * lump
    rr = r * (1.0 + tube_noise)
    radius = R * (1.0 + radial_noise) + rr * math.cos(v)
    z = rr * math.sin(v)
    return Vector((radius * math.cos(u), radius * math.sin(u), z))


def torus_normal(u: float, v: float) -> Vector:
    normal = Vector((math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v)))
    return normal.normalized()


def create_donut_mesh(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    R, r = 0.62, 0.20
    u_steps, v_steps = 120, 32
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for i in range(u_steps):
        u = 2 * math.pi * i / u_steps
        for j in range(v_steps):
            v = 2 * math.pi * j / v_steps
            p = torus_point(u, v, R, r, lump=1.0)
            world = p + DONUT_CENTER
            vertices.append((world.x, world.y, world.z))
    for i in range(u_steps):
        for j in range(v_steps):
            faces.append((
                i * v_steps + j,
                ((i + 1) % u_steps) * v_steps + j,
                ((i + 1) % u_steps) * v_steps + ((j + 1) % v_steps),
                i * v_steps + ((j + 1) % v_steps),
            ))
    mesh = bpy.data.meshes.new("DONUT_DoughMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("DONUT_Dough_lumpy_torus", mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    set_exportable(obj)
    smooth_mesh(obj)
    add_modifier(obj, "DONUT_SoftSubdivision", "SUBSURF", levels=1, render_levels=1)
    return obj


def create_icing_mesh(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    R, r = 0.62, 0.205
    u_steps, v_steps = 120, 16
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for i in range(u_steps):
        u = 2 * math.pi * i / u_steps
        outer_edge = -0.10 - 0.12 * math.sin(5.0 * u + 0.5) - 0.06 * math.sin(11.0 * u)
        inner_edge = math.pi + 0.10 + 0.08 * math.sin(4.0 * u + 1.4) + 0.05 * math.sin(9.0 * u)
        for j in range(v_steps + 1):
            t = j / v_steps
            v = outer_edge * (1.0 - t) + inner_edge * t
            p = torus_point(u, v, R, r, lump=0.8)
            n = torus_normal(u, v)
            p = p + n * 0.025
            world = p + DONUT_CENTER
            vertices.append((world.x, world.y, world.z))
    row = v_steps + 1
    for i in range(u_steps):
        for j in range(v_steps):
            faces.append((
                i * row + j,
                ((i + 1) % u_steps) * row + j,
                ((i + 1) % u_steps) * row + j + 1,
                i * row + j + 1,
            ))
    mesh = bpy.data.meshes.new("DONUT_IcingMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("DONUT_Icing_shrinkwrapped_upper_half", mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    set_exportable(obj)
    smooth_mesh(obj)
    add_modifier(obj, "DONUT_IcingThickness_solidify", "SOLIDIFY", thickness=0.032, offset=1.0)
    add_modifier(obj, "DONUT_IcingSoftSubdivision", "SUBSURF", levels=1, render_levels=1)
    return obj


def create_ellipsoid(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    mat: bpy.types.Material,
    *,
    segments: int = 32,
    rings: int = 16,
    exportable: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.scale = scale
    obj.data.materials.append(mat)
    link_to_collection(obj, collection)
    set_exportable(obj, exportable)
    smooth_mesh(obj)
    return obj


def create_cylinder_between(
    collection: bpy.types.Collection,
    name: str,
    start: Vector,
    end: Vector,
    radius: float,
    mat: bpy.types.Material,
    *,
    vertices: int = 16,
    bevel_segments: int = 5,
    exportable: bool = True,
) -> bpy.types.Object:
    center = (start + end) * 0.5
    direction = end - start
    depth = direction.length
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    link_to_collection(obj, collection)
    set_exportable(obj, exportable)
    smooth_mesh(obj)
    bevel = add_modifier(obj, f"{name}_soft_caps", "BEVEL", width=radius * 0.75, segments=bevel_segments)
    bevel.affect = "EDGES"
    add_modifier(obj, f"{name}_weighted_normals", "WEIGHTED_NORMAL")
    return obj


def create_drips(collection: bpy.types.Collection, mat: bpy.types.Material) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    R, r = 0.62, 0.214
    drip_specs = [
        (0.08, -0.08, 0.08, 0.020),
        (0.52, -0.16, 0.13, 0.025),
        (0.98, -0.05, 0.07, 0.019),
        (1.45, -0.18, 0.10, 0.022),
        (2.08, -0.10, 0.08, 0.020),
        (2.74, -0.15, 0.14, 0.026),
        (3.30, -0.08, 0.07, 0.019),
        (3.92, -0.17, 0.11, 0.023),
        (4.58, -0.07, 0.08, 0.020),
        (5.18, -0.13, 0.12, 0.025),
        (5.82, -0.06, 0.08, 0.019),
    ]
    for idx, (u, v_edge, length, radius) in enumerate(drip_specs, start=1):
        start = torus_point(u, v_edge, R, r, lump=0.7) + torus_normal(u, v_edge) * 0.018 + DONUT_CENTER
        downward = Vector((0, 0, -length))
        outward = Vector((math.cos(u), math.sin(u), 0)) * (0.02 + 0.02 * random.random())
        end = start + downward + outward
        body = create_cylinder_between(collection, f"DONUT_IcingDrip_{idx:02d}_body", start, end, radius, mat, vertices=18)
        tip = create_ellipsoid(
            collection,
            f"DONUT_IcingDrip_{idx:02d}_rounded_tip",
            end,
            (radius * 1.08, radius * 1.08, radius * 1.35),
            mat,
            segments=20,
            rings=10,
        )
        objects.extend([body, tip])
    return objects


def create_plate(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=128,
        radius=1.36,
        depth=0.075,
        location=(DONUT_CENTER.x, DONUT_CENTER.y, 0.095),
    )
    plate = bpy.context.object
    plate.name = "DONUT_Plate_wide_ceramic"
    plate.data.name = "DONUT_PlateMesh"
    plate.data.materials.append(mat)
    link_to_collection(plate, collection)
    set_exportable(plate)
    smooth_mesh(plate)
    add_modifier(plate, "DONUT_Plate_soft_bevel", "BEVEL", width=0.035, segments=6)
    add_modifier(plate, "DONUT_Plate_weighted_normals", "WEIGHTED_NORMAL")

    bpy.ops.mesh.primitive_torus_add(
        major_segments=128,
        minor_segments=12,
        major_radius=1.12,
        minor_radius=0.022,
        location=(DONUT_CENTER.x, DONUT_CENTER.y, 0.145),
    )
    inner_rim = bpy.context.object
    inner_rim.name = "DONUT_Plate_inner_raised_ring"
    inner_rim.data.name = "DONUT_PlateInnerRingMesh"
    inner_rim.data.materials.append(mat)
    link_to_collection(inner_rim, collection)
    set_exportable(inner_rim)
    smooth_mesh(inner_rim)

    bpy.ops.mesh.primitive_torus_add(
        major_segments=128,
        minor_segments=16,
        major_radius=1.33,
        minor_radius=0.055,
        location=(DONUT_CENTER.x, DONUT_CENTER.y, 0.158),
    )
    outer_rim = bpy.context.object
    outer_rim.name = "DONUT_Plate_outer_soft_lip"
    outer_rim.data.name = "DONUT_PlateOuterLipMesh"
    outer_rim.data.materials.append(mat)
    link_to_collection(outer_rim, collection)
    set_exportable(outer_rim)
    smooth_mesh(outer_rim)
    return plate


def create_mug(
    collection: bpy.types.Collection,
    ceramic: bpy.types.Material,
    coffee_mat: bpy.types.Material,
    reflection_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    segments = 96
    base_z = 0.085
    height = 0.72
    rings = [
        (base_z, 0.285),
        (base_z + height * 0.22, 0.335),
        (base_z + height * 0.72, 0.385),
        (base_z + height, 0.365),
    ]
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for z, radius in rings:
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            vertices.append((MUG_CENTER.x + radius * math.cos(angle), MUG_CENTER.y + radius * math.sin(angle), z))
    for ring_index in range(len(rings) - 1):
        row = ring_index * segments
        next_row = (ring_index + 1) * segments
        for i in range(segments):
            faces.append((row + i, row + (i + 1) % segments, next_row + (i + 1) % segments, next_row + i))
    faces.append(tuple(reversed(range(segments))))

    mesh = bpy.data.meshes.new("DONUT_MugBodyMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mug = bpy.data.objects.new("DONUT_Mug_rustic_brown_ceramic_body", mesh)
    mug.name = "DONUT_Mug_ceramic_body"
    mug.data.materials.append(ceramic)
    collection.objects.link(mug)
    set_exportable(mug)
    smooth_mesh(mug)
    add_modifier(mug, "DONUT_Mug_soft_bevels", "BEVEL", width=0.025, segments=5)
    add_modifier(mug, "DONUT_Mug_weighted_normals", "WEIGHTED_NORMAL")

    bpy.ops.mesh.primitive_torus_add(
        major_segments=96,
        minor_segments=12,
        major_radius=0.357,
        minor_radius=0.026,
        location=(MUG_CENTER.x, MUG_CENTER.y, base_z + height + 0.012),
    )
    lip = bpy.context.object
    lip.name = "DONUT_Mug_dark_ceramic_rounded_lip"
    lip.data.name = "DONUT_MugLipMesh"
    lip.data.materials.append(ceramic)
    link_to_collection(lip, collection)
    set_exportable(lip)
    smooth_mesh(lip)

    coffee = create_ellipsoid(
        collection,
        "DONUT_Mug_black_coffee_surface",
        (MUG_CENTER.x, MUG_CENTER.y, base_z + height + 0.017),
        (0.324, 0.324, 0.012),
        coffee_mat,
        segments=48,
        rings=8,
    )
    reflection = create_ellipsoid(
        collection,
        "DONUT_Mug_coffee_white_reflection_patch",
        (MUG_CENTER.x - 0.08, MUG_CENTER.y - 0.07, base_z + height + 0.031),
        (0.12, 0.026, 0.003),
        reflection_mat,
        segments=32,
        rings=6,
    )

    handle_points = [
        Vector((MUG_CENTER.x + 0.36, MUG_CENTER.y, base_z + 0.55)),
        Vector((MUG_CENTER.x + 0.66, MUG_CENTER.y, base_z + 0.50)),
        Vector((MUG_CENTER.x + 0.68, MUG_CENTER.y, base_z + 0.30)),
        Vector((MUG_CENTER.x + 0.37, MUG_CENTER.y, base_z + 0.24)),
    ]
    handle_parts: list[bpy.types.Object] = []
    for idx in range(len(handle_points) - 1):
        handle_parts.append(create_cylinder_between(
            collection,
            f"DONUT_Mug_handle_segment_{idx + 1:02d}",
            handle_points[idx],
            handle_points[idx + 1],
            0.040,
            ceramic,
            vertices=18,
        ))
    for idx, point in enumerate(handle_points, start=1):
        handle_parts.append(create_ellipsoid(
            collection,
            f"DONUT_Mug_handle_soft_joint_{idx:02d}",
            point,
            (0.046, 0.046, 0.046),
            ceramic,
            segments=16,
            rings=8,
        ))
    return [mug, lip, coffee, reflection, *handle_parts]


def create_table(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.02))
    table = bpy.context.object
    table.name = "DONUT_Table_concrete_pbr_plane"
    table.dimensions = (18.0, 32.0, 0.04)
    table.location = (0, 0, 0.02)
    table.data.materials.append(mat)
    link_to_collection(table, collection)
    set_exportable(table)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    add_modifier(table, "DONUT_Table_micro_bevel", "BEVEL", width=0.015, segments=2)
    add_modifier(table, "DONUT_Table_weighted_normals", "WEIGHTED_NORMAL")
    return table


def create_sprinkle_materials() -> list[bpy.types.Material]:
    palette = [
        ("DONUT_SprinkleMat_pastel_aqua", (0.32, 0.82, 0.86, 1.0)),
        ("DONUT_SprinkleMat_soft_purple", (0.65, 0.42, 0.86, 1.0)),
        ("DONUT_SprinkleMat_warm_yellow", (0.95, 0.79, 0.36, 1.0)),
        ("DONUT_SprinkleMat_milk_white", (0.95, 0.90, 0.82, 1.0)),
        ("DONUT_SprinkleMat_soft_pink", (0.95, 0.48, 0.70, 1.0)),
    ]
    return [
        material_principled(name, color, roughness=0.38, subsurface_weight=0.45, subsurface_scale=0.025)
        for name, color in palette
    ]


def create_sprinkles(collection: bpy.types.Collection, mats: list[bpy.types.Material]) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    R, r = 0.62, 0.205
    count = 125
    palette_weights = [0.32, 0.24, 0.16, 0.14, 0.14]
    for idx in range(count):
        u = random.random() * 2 * math.pi
        v = random.uniform(0.32, 2.50)
        # Keep most sprinkles on the camera-visible/top icing area and avoid the underside.
        if math.sin(v) < 0.08:
            v = random.uniform(0.55, 2.20)
        position = torus_point(u, v, R, r, lump=0.75) + DONUT_CENTER + torus_normal(u, v) * 0.055
        tangent_u = Vector((-math.sin(u), math.cos(u), 0)).normalized()
        tangent_v = Vector((-math.sin(v) * math.cos(u), -math.sin(v) * math.sin(u), math.cos(v))).normalized()
        angle = random.random() * 2 * math.pi
        direction = (math.cos(angle) * tangent_u + math.sin(angle) * tangent_v).normalized()
        length = random.uniform(0.085, 0.145)
        radius = random.uniform(0.008, 0.012)
        start = position - direction * length * 0.5
        end = position + direction * length * 0.5
        mat = random.choices(mats, weights=palette_weights, k=1)[0]
        sprinkle = create_cylinder_between(
            collection,
            f"DONUT_Sprinkle_scattered_{idx + 1:03d}",
            start,
            end,
            radius,
            mat,
            vertices=10,
            bevel_segments=1,
        )
        sprinkle.rotation_euler.rotate_axis("X", random.uniform(-0.06, 0.06))
        objects.append(sprinkle)
    return objects


def create_light_blocker(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    rotation: Sequence[float],
    scale: Sequence[float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    obj.data.materials.append(mat)
    link_to_collection(obj, collection)
    set_exportable(obj, False)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Keep the Blender file evidence of the planned blockers, but prevent them
    # from accidentally crossing the camera in preview/final renders.
    obj.hide_render = True
    return obj


def create_lighting(scene: bpy.types.Scene, collection: bpy.types.Collection, blocker_mat: bpy.types.Material) -> None:
    sun_data = bpy.data.lights.new("DONUT_Sun_warm_window_key_data", "SUN")
    sun_data.energy = 2.0
    sun_data.angle = math.radians(3.2)
    sun = bpy.data.objects.new("DONUT_Sun_warm_window_key_not_exported", sun_data)
    sun.rotation_euler = (math.radians(48), math.radians(0), math.radians(-38))
    collection.objects.link(sun)
    set_exportable(sun, False)

    sky_data = bpy.data.lights.new("DONUT_Sky_blue_fill_data", "POINT")
    sky_data.energy = 160
    sky_data.color = (0.58, 0.66, 0.90)
    sky_data.shadow_soft_size = 5.0
    sky = bpy.data.objects.new("DONUT_Sky_blue_fill_not_exported", sky_data)
    sky.location = (-2.7, -2.1, 4.6)
    collection.objects.link(sky)
    set_exportable(sky, False)

    bounce_data = bpy.data.lights.new("DONUT_Cafe_bounce_fill_data", "AREA")
    bounce_data.energy = 170
    bounce_data.size = 4.0
    bounce_data.color = (1.0, 0.86, 0.68)
    bounce = bpy.data.objects.new("DONUT_Cafe_bounce_fill_not_exported", bounce_data)
    bounce.location = (2.6, 2.2, 2.4)
    bounce.rotation_euler = (math.radians(65), 0, math.radians(140))
    collection.objects.link(bounce)
    set_exportable(bounce, False)

    create_light_blocker(
        collection,
        "DONUT_WindowShadowBlocker_A_not_exported",
        (-1.55, -2.15, 1.95),
        (math.radians(0), math.radians(0), math.radians(22)),
        (0.22, 2.4, 2.2),
        blocker_mat,
    )
    create_light_blocker(
        collection,
        "DONUT_WindowShadowBlocker_B_not_exported",
        (-0.25, -2.05, 1.95),
        (math.radians(0), math.radians(0), math.radians(22)),
        (0.24, 2.4, 2.2),
        blocker_mat,
    )

    world = scene.world or bpy.data.worlds.new("DONUT_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.03, 0.032, 0.035, 1.0)
        bg.inputs["Strength"].default_value = 0.08


def create_camera(scene: bpy.types.Scene, collection: bpy.types.Collection) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new("DONUT_Camera_data")
    camera = bpy.data.objects.new("DONUT_Camera_depth_of_field_not_exported", camera_data)
    camera.location = (0.02, -5.75, 3.05)
    look_at(camera, Vector((-0.16, 0.08, 0.34)))
    camera_data.lens = 37
    camera_data.dof.use_dof = True
    camera_data.dof.aperture_fstop = 7.5
    camera_data.dof.focus_distance = 4.0
    if PRIMARY_REFERENCE.exists():
        camera_data.show_background_images = True
        bg = camera_data.background_images.new()
        bg.image = bpy.data.images.load(str(PRIMARY_REFERENCE))
        bg.alpha = 0.18
    collection.objects.link(camera)
    set_exportable(camera, False)
    scene.camera = camera
    return camera


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - Vector(obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> tuple[bpy.types.Scene, bpy.types.Collection, dict[str, bpy.types.Material]]:
    remove_default_objects()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for engine in ("CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except Exception:
            continue
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 96),
            ("use_gtao", True),
            ("gtao_distance", 3.0),
            ("gtao_factor", 0.8),
        ):
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
    scene.view_settings.exposure = -0.25
    scene.view_settings.gamma = 1.0

    collection = make_collection(scene)
    mats = {
        "dough": material_principled(
            "DONUT_Mat_warm_fried_dough_subsurface",
            (0.93, 0.60, 0.25, 1.0),
            roughness=0.68,
            subsurface_weight=0.42,
            subsurface_scale=0.075,
        ),
        "icing": material_principled(
            "DONUT_Mat_strawberry_glaze_glossy_subsurface",
            (0.98, 0.34, 0.68, 1.0),
            roughness=0.24,
            subsurface_weight=0.52,
            subsurface_scale=0.045,
        ),
        "plate": material_principled("DONUT_Mat_cool_white_ceramic", (0.76, 0.75, 0.70, 1.0), roughness=0.42),
        "mug": material_principled("DONUT_Mat_rustic_brown_speckled_ceramic", (0.22, 0.12, 0.055, 1.0), roughness=0.68),
        "coffee": material_principled("DONUT_Mat_black_coffee_gloss", (0.004, 0.003, 0.002, 1.0), roughness=0.62),
        "coffee_reflection": material_principled("DONUT_Mat_soft_white_coffee_reflection", (0.92, 0.90, 0.84, 1.0), roughness=0.08),
        "table": material_principled("DONUT_Mat_dark_mottled_concrete_table", (0.22, 0.22, 0.21, 1.0), roughness=0.58),
        "blocker": material_principled("DONUT_Mat_shadow_blocker_not_exported", (0.035, 0.032, 0.030, 1.0), roughness=0.9),
    }
    apply_noise_color(mats["table"], (0.10, 0.10, 0.095), (0.42, 0.42, 0.39), scale=18.0, detail=14.0, bump_strength=0.10, bump_distance=0.09)
    apply_noise_color(mats["mug"], (0.07, 0.04, 0.02), (0.38, 0.23, 0.10), scale=42.0, detail=13.0, bump_strength=0.04, bump_distance=0.035)
    apply_noise_color(mats["dough"], (0.74, 0.37, 0.12), (1.0, 0.74, 0.32), scale=28.0, detail=9.0, bump_strength=0.025, bump_distance=0.018)
    return scene, collection, mats


def parent_keep_transform(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    child.matrix_world = world


def write_scene_graph(path: Path) -> dict:
    graph = {
        "schema_version": "1.0",
        "goal": "Editable Blender 5.0-style donut scene matched to the provided Blender Guru finale screenshot: compact donut on left plate, rustic coffee mug on right, gray mottled concrete table, camera-perspective tutorial frame.",
        "mode": "FREEFORM",
        "units": "METERS",
        "primary_reference": str(PRIMARY_REFERENCE),
        "parts": [
            {"id": "table", "name": "DONUT_Table_concrete_pbr_plane", "representation": "MESH", "dimensions": [18.0, 32.0, 0.04], "material_group": "dark_mottled_concrete", "source_confidence": 0.95},
            {"id": "plate", "name": "DONUT_Plate_wide_ceramic", "representation": "MESH", "dimensions": [2.8, 2.8, 0.18], "material_group": "cool_white_ceramic", "source_confidence": 0.9},
            {"id": "donut", "name": "DONUT_Dough_lumpy_torus", "representation": "MESH", "dimensions": [1.65, 1.65, 0.42], "material_group": "fried_dough", "source_confidence": 0.95},
            {"id": "icing", "name": "DONUT_Icing_shrinkwrapped_upper_half", "representation": "MESH", "dimensions": [1.7, 1.7, 0.28], "material_group": "strawberry_glaze", "source_confidence": 0.95},
            {"id": "drips", "name": "DONUT_IcingDrip_*", "representation": "PRIMITIVES", "dimensions": [0.08, 0.08, 0.2], "material_group": "strawberry_glaze", "source_confidence": 0.85},
            {"id": "sprinkles", "name": "DONUT_Sprinkle_scattered_*", "representation": "PRIMITIVES", "dimensions": [0.14, 0.02, 0.02], "material_group": "pastel_sprinkles", "source_confidence": 0.9},
            {"id": "mug", "name": "DONUT_Mug_ceramic_body", "representation": "MESH", "dimensions": [0.85, 0.85, 0.75], "material_group": "rustic_brown_ceramic", "source_confidence": 0.85},
            {"id": "coffee", "name": "DONUT_Mug_black_coffee_surface", "representation": "MESH", "dimensions": [0.65, 0.65, 0.02], "material_group": "black_coffee", "source_confidence": 0.8},
        ],
        "relations": [
            {"a": "plate", "type": "TOUCHES", "b": "table", "tolerance": 0.05},
            {"a": "donut", "type": "TOUCHES", "b": "plate", "tolerance": 0.08},
            {"a": "icing", "type": "OVERLAPS", "b": "donut", "minimum_overlap": 0.02},
            {"a": "drips", "type": "OVERLAPS", "b": "icing", "minimum_overlap": 0.02},
            {"a": "sprinkles", "type": "TOUCHES", "b": "icing", "tolerance": 0.12},
            {"a": "coffee", "type": "OVERLAPS", "b": "mug", "minimum_overlap": 0.01},
            {"a": "mug", "type": "TOUCHES", "b": "table", "tolerance": 0.08},
        ],
        "camera": {
            "view": "VIDEO_REFERENCE_WIDE",
            "depth_of_field": "subtle, both donut and mug readable",
        },
        "acceptance": {
            "must_have": [
                "lumpy torus dough, not perfect mathematical torus",
                "upper-half icing with uneven edge and visible drips",
                "many small pastel sprinkles only on icing top",
                "wide camera view similar to the video finale screenshot",
                "dark mottled concrete table fills the camera frame",
                "rustic brown mug stands to the right of the plate without covering the donut",
                "named editable objects and non-export lights/camera/blockers",
            ],
            "triangle_budget": TRIANGLE_BUDGET,
        },
    }
    write_json(path, graph)
    return graph


def render_to(scene: bpy.types.Scene, camera: bpy.types.Object, path: Path, *, view: str) -> None:
    if view == "front":
        camera.location = (-0.03, -5.85, 2.92)
        look_at(camera, Vector((-0.16, 0.08, 0.34)))
        camera.data.lens = 38
    elif view == "side":
        camera.location = (4.55, -0.05, 2.05)
        look_at(camera, Vector((-0.16, 0.08, 0.34)))
        camera.data.lens = 40
    else:
        camera.location = (0.02, -5.75, 3.05)
        look_at(camera, Vector((-0.16, 0.08, 0.34)))
        camera.data.lens = 37
    camera.data.dof.focus_distance = (Vector((-0.16, 0.08, 0.42)) - Vector(camera.location)).length
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

    table = create_table(collection, mats["table"])
    plate = create_plate(collection, mats["plate"])
    donut = create_donut_mesh(collection, mats["dough"])
    icing = create_icing_mesh(collection, mats["icing"])
    drips = create_drips(collection, mats["icing"])
    mug_parts = create_mug(collection, mats["mug"], mats["coffee"], mats["coffee_reflection"])
    sprinkle_mats = create_sprinkle_materials()
    sprinkles = create_sprinkles(collection, sprinkle_mats)

    parent_keep_transform(icing, donut)
    for obj in drips + sprinkles:
        parent_keep_transform(obj, icing)
    parent_keep_transform(donut, plate)
    for obj in mug_parts:
        parent_keep_transform(obj, table)
    parent_keep_transform(plate, table)

    create_lighting(scene, collection, mats["blocker"])
    camera = create_camera(scene, collection)

    export_objects = [
        obj for obj in collection.objects
        if obj.type == "MESH" and bool(obj.get("abt_export", False))
    ]

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
    render_to(scene, camera, render_main, view="front_3q")
    render_to(scene, camera, render_front, view="front")
    render_to(scene, camera, render_side, view="side")

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
        "blend": str(blend_path),
        "glb": str(glb_path),
        "public_glb": str(public_glb),
        "renders": [str(render_main), str(render_front), str(render_side)],
        "reports": [str(scene_graph_path), str(qa_path), str(validation_path)],
        "triangles": validation["triangles"],
        "object_count": validation["object_count"],
        "warnings": validation["warnings"],
        "notes": [
            "Built from scratch as a new Blender file.",
            "Icing and sprinkles follow the Blender Guru 2025 workflow conceptually: duplicate upper icing, uneven drips, weight-paint-like top-only scatter, pastel random-color sprinkles, food subsurface materials.",
            "Simple PBR materials are used for GLB robustness; procedural texture complexity is intentionally limited.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", scene_report)
    print(json.dumps(scene_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
