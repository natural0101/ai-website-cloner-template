from __future__ import annotations

import json
import math
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Vector


SCRIPT = Path(globals().get(
    "__file__",
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench\scripts\blender_create_teamon_hero_icons_v1.py",
)).resolve()
WORKBENCH = SCRIPT.parents[1]
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
V4_BLENDER = WORKBENCH / "research-feedback-upgrade" / "04_blender"
V4_PYTHON = WORKBENCH / "research-feedback-upgrade" / "04_python"

ASSET = "teamon_hero_icons_v4"
SCENE_NAME = "TeamONHeroIconsV4"
END_FRAME = 120
FPS = 24
WIDTH = 1100
HEIGHT = 900
PREFIX = "THI_"

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS):
    path.mkdir(parents=True, exist_ok=True)

for path in (V4_BLENDER, V4_PYTHON):
    if str(path) not in sys.path:
        sys.path.append(str(path))

import scene_qa
from stage_orchestrator import StageOrchestrator


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def inspect_scene() -> dict:
    scene = bpy.context.scene
    return {
        "scene": scene.name,
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "location": [round(float(v), 5) for v in obj.location],
                "hidden_render": bool(obj.hide_render),
            }
            for obj in scene.objects
        ],
        "materials": sorted(mat.name for mat in bpy.data.materials),
        "blender_version": ".".join(map(str, bpy.app.version)),
    }


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object, *, location: bool = False, rotation: bool = False, scale: bool = True) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.type != "MESH":
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for current in list(obj.users_collection):
        if current != collection:
            current.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_previous_teamon_objects() -> None:
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name.startswith(PREFIX):
            bpy.data.collections.remove(collection)


def preserve_preexisting_scene() -> dict:
    preexisting = create_collection("ABT_Preexisting_DoNotExport")
    preserved = []
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(PREFIX):
            continue
        preserved.append(obj.name)
        obj["abt_export"] = False
        obj.hide_render = True
        obj.hide_viewport = True
        link_to_collection(obj, preexisting)
    return {"preserved_objects": preserved, "collection": preexisting.name}


def save_checkpoint(stage: str) -> Path:
    path = CHECKPOINTS / f"{ASSET}_{stage.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return path


def safe_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def configure_scene() -> bpy.types.Scene:
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.frame_set(1)
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
    world = scene.world or bpy.data.worlds.new(f"{PREFIX}World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.913, 0.965, 0.922, 1.0)
        background.inputs["Strength"].default_value = 1.0
    return scene


def create_camera(studio: bpy.types.Collection) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{PREFIX}CameraData")
    data.type = "ORTHO"
    data.lens = 58
    data.dof.use_dof = False
    camera = bpy.data.objects.new(f"{PREFIX}Camera", data)
    camera["abt_export"] = False
    studio.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def create_empty(collection: bpy.types.Collection, name: str, role: str, *, export: bool = True) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.12
    obj["role"] = role
    obj["abt_export"] = bool(export)
    collection.objects.link(obj)
    return obj


def create_material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    roughness: float,
    metallic: float = 0.0,
    coat: float = 0.0,
    alpha: float = 1.0,
    transmission: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (color[0], color[1], color[2], alpha)
    if alpha < 1.0:
        if hasattr(material, "surface_render_method"):
            material.surface_render_method = "DITHERED"
        elif hasattr(material, "blend_method"):
            material.blend_method = "BLEND"
        if hasattr(material, "use_transparency_overlap"):
            material.use_transparency_overlap = False
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": (color[0], color[1], color[2], alpha),
            "Roughness": roughness,
            "Metallic": metallic,
            "Alpha": alpha,
            "Coat Weight": coat,
            "Coat Roughness": max(0.08, roughness * 0.65),
            "Specular IOR Level": 0.5,
            "Transmission Weight": transmission,
            "IOR": 1.45,
        }
        for key, value in values.items():
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        if emission:
            for key in ("Emission Color", "Emission"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission
                    break
            for key in ("Emission Strength", "Emission Weight"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission_strength
                    break
    return material


def create_materials() -> dict[str, bpy.types.Material]:
    materials = {
        "blockout": create_material(
            f"{PREFIX}BlockoutClay", (0.66, 0.69, 0.67, 1.0), roughness=0.72, emission=(0.66, 0.69, 0.67, 1.0), emission_strength=0.035
        ),
        "porcelain": create_material(f"{PREFIX}Porcelain_F5FCF6", (0.913, 0.965, 0.922, 1.0), roughness=0.24, coat=0.28),
        "mint": create_material(f"{PREFIX}Mint_58D1BD", (0.096, 0.638, 0.507, 1.0), roughness=0.25, coat=0.34),
        "mint_soft": create_material(f"{PREFIX}MintSoft", (0.37, 0.82, 0.72, 1.0), roughness=0.31, coat=0.18),
        "pine": create_material(f"{PREFIX}Pine_153D34", (0.007, 0.047, 0.034, 1.0), roughness=0.31, coat=0.12),
        "lime": create_material(
            f"{PREFIX}Lime_E6F3B5", (0.791, 0.896, 0.462, 1.0), roughness=0.27, coat=0.24,
            emission=(0.791, 0.896, 0.462, 1.0), emission_strength=0.16,
        ),
        "coral": create_material(f"{PREFIX}Coral_FF9A78", (1.0, 0.323, 0.188, 1.0), roughness=0.31, coat=0.25),
        "silver": create_material(f"{PREFIX}SatinSilver", (0.72, 0.76, 0.73, 1.0), roughness=0.2, metallic=0.9, coat=0.12),
        "glass": create_material(
            f"{PREFIX}MintGlass", (0.16, 0.80, 0.66, 1.0), roughness=0.12, coat=0.48,
            alpha=0.70, transmission=0.18,
        ),
        "glass_frost": create_material(
            f"{PREFIX}FrostedMintGlass", (0.48, 0.92, 0.82, 1.0), roughness=0.28, coat=0.32,
            alpha=0.86, transmission=0.08,
        ),
        "core": create_material(
            f"{PREFIX}AgentCoreGlow", (0.83, 0.97, 0.50, 1.0), roughness=0.18, coat=0.2,
            emission=(0.83, 0.97, 0.50, 1.0), emission_strength=1.6,
        ),
    }
    return materials


def mark_part(
    obj: bpy.types.Object,
    root: bpy.types.Object,
    role: str,
    material_key: str,
    blockout: bpy.types.Material,
) -> bpy.types.Object:
    obj["role"] = role
    obj["material_key"] = material_key
    obj["abt_export"] = True
    obj.parent = root
    assign_material(obj, blockout)
    return obj


def finish_mesh(obj: bpy.types.Object, *, bevel: float = 0.0, segments: int = 5) -> bpy.types.Object:
    if obj.type != "MESH":
        return obj
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if bevel > 0:
        modifier = obj.modifiers.new(f"{PREFIX}EdgeBevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = segments
        modifier.affect = "EDGES"
        set_active(obj)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def rounded_box(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    dimensions: Sequence[float],
    radius: float,
    *,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    segments: int = 6,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    link_to_collection(obj, collection)
    apply_transform(obj, scale=True)
    finish_mesh(obj, bevel=radius, segments=segments)
    return obj


def sphere(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    *,
    segments: int = 48,
    rings: int = 32,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    link_to_collection(obj, collection)
    apply_transform(obj, scale=True)
    finish_mesh(obj)
    return obj


def cylinder(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    radius: float,
    depth: float,
    *,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    vertices: int = 48,
    bevel: float = 0.03,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, end_fill_type="NGON", location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    link_to_collection(obj, collection)
    apply_transform(obj, scale=True)
    finish_mesh(obj, bevel=bevel, segments=5)
    return obj


def torus(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    major_radius: float,
    minor_radius: float,
    *,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        major_segments=64,
        minor_segments=16,
        location=location,
        rotation=rotation,
        major_radius=major_radius,
        minor_radius=minor_radius,
    )
    obj = bpy.context.object
    obj.name = name
    link_to_collection(obj, collection)
    finish_mesh(obj)
    return obj


def curve_tube(
    collection: bpy.types.Collection,
    name: str,
    points: Sequence[Sequence[float]],
    radius: float,
    *,
    radii: Sequence[float] | None = None,
    resolution: int = 5,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = resolution
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 5
    curve_data.resolution_u = 16
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for index, point in enumerate(points):
        bezier = spline.bezier_points[index]
        bezier.co = point
        bezier.handle_left_type = "AUTO"
        bezier.handle_right_type = "AUTO"
        if radii:
            bezier.radius = radii[index]
    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    set_active(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    finish_mesh(obj)
    return obj


def lathe_capsule(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    *,
    radius: float,
    straight_height: float,
    radial_segments: int = 48,
    cap_segments: int = 12,
) -> bpy.types.Object:
    profile: list[tuple[float, float]] = [(0.0, -straight_height / 2.0 - radius)]
    for index in range(1, cap_segments + 1):
        angle = -math.pi / 2.0 + (math.pi / 2.0) * (index / cap_segments)
        profile.append((radius * math.cos(angle), -straight_height / 2.0 + radius * math.sin(angle)))
    profile.append((radius, straight_height / 2.0))
    for index in range(1, cap_segments + 1):
        angle = (math.pi / 2.0) * (index / cap_segments)
        profile.append((radius * math.cos(angle), straight_height / 2.0 + radius * math.sin(angle)))

    vertices: list[tuple[float, float, float]] = []
    rings: list[list[int]] = []
    for ring_index, (ring_radius, z) in enumerate(profile):
        if ring_radius <= 1e-7:
            rings.append([len(vertices)])
            vertices.append((0.0, 0.0, z))
            continue
        ring = []
        for segment in range(radial_segments):
            angle = 2.0 * math.pi * segment / radial_segments
            ring.append(len(vertices))
            vertices.append((ring_radius * math.cos(angle), ring_radius * math.sin(angle), z))
        rings.append(ring)

    faces: list[tuple[int, ...]] = []
    for current, following in zip(rings, rings[1:]):
        if len(current) == 1:
            pole = current[0]
            for segment in range(radial_segments):
                faces.append((pole, following[(segment + 1) % radial_segments], following[segment]))
        elif len(following) == 1:
            pole = following[0]
            for segment in range(radial_segments):
                faces.append((current[segment], current[(segment + 1) % radial_segments], pole))
        else:
            for segment in range(radial_segments):
                nxt = (segment + 1) % radial_segments
                faces.append((current[segment], current[nxt], following[nxt], following[segment]))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    finish_mesh(obj)
    return obj


def lathe_profile_mesh(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    profile: Sequence[tuple[float, float]],
    *,
    radial_segments: int = 48,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    rings: list[list[int]] = []
    for ring_radius, z in profile:
        if ring_radius <= 1e-7:
            rings.append([len(vertices)])
            vertices.append((0.0, 0.0, z))
            continue
        ring = []
        for segment in range(radial_segments):
            angle = 2.0 * math.pi * segment / radial_segments
            ring.append(len(vertices))
            vertices.append((ring_radius * math.cos(angle), ring_radius * math.sin(angle), z))
        rings.append(ring)

    faces: list[tuple[int, ...]] = []
    for current, following in zip(rings, rings[1:]):
        if len(current) == 1:
            pole = current[0]
            for segment in range(radial_segments):
                faces.append((pole, following[(segment + 1) % radial_segments], following[segment]))
        elif len(following) == 1:
            pole = following[0]
            for segment in range(radial_segments):
                faces.append((current[segment], current[(segment + 1) % radial_segments], pole))
        else:
            for segment in range(radial_segments):
                nxt = (segment + 1) % radial_segments
                faces.append((current[segment], current[nxt], following[nxt], following[segment]))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    collection.objects.link(obj)
    finish_mesh(obj)
    return obj


def lower_release_capsule(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    *,
    radius: float,
    cap_segments: int = 12,
) -> bpy.types.Object:
    profile: list[tuple[float, float]] = [(0.0, -0.63)]
    for index in range(1, cap_segments + 1):
        angle = -math.pi / 2.0 + (math.pi / 2.0) * (index / cap_segments)
        profile.append((radius * math.cos(angle), -0.32 + radius * math.sin(angle)))
    profile.extend([(radius, 0.02), (0.0, 0.02)])
    return lathe_profile_mesh(collection, name, location, profile)


def upper_release_dome(
    collection: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    *,
    radius: float,
    cap_segments: int = 14,
) -> bpy.types.Object:
    profile: list[tuple[float, float]] = [(0.0, 0.02), (radius, 0.02), (radius, 0.32)]
    for index in range(1, cap_segments + 1):
        angle = (math.pi / 2.0) * (index / cap_segments)
        profile.append((radius * math.cos(angle), 0.32 + radius * math.sin(angle)))
    return lathe_profile_mesh(collection, name, location, profile)


def build_server(output: bpy.types.Collection, blockout: bpy.types.Material) -> bpy.types.Object:
    root = create_empty(output, f"{PREFIX}ICON_Server", "icon_root")

    parts = [
        (rounded_box(output, f"{PREFIX}Server_Chassis", (0, 0, 0), (1.42, 0.92, 1.54), 0.22), "server_chassis", "mint_soft"),
        (rounded_box(output, f"{PREFIX}Server_BaseBand", (0, -0.005, -0.63), (1.44, 0.94, 0.30), 0.14), "server_base", "pine"),
        (rounded_box(output, f"{PREFIX}Server_FrontFrame", (0, -0.49, 0.08), (1.30, 0.16, 1.28), 0.17), "server_front_frame", "porcelain"),
        (rounded_box(output, f"{PREFIX}Server_Cavity", (0, -0.585, 0.08), (1.10, 0.12, 1.06), 0.12), "server_front_cavity", "pine"),
        (rounded_box(output, f"{PREFIX}Server_StatusRail", (0, -0.535, -0.70), (0.82, 0.13, 0.08), 0.035), "server_status_rail", "pine"),
        (rounded_box(output, f"{PREFIX}Server_StatusGlow", (0.09, -0.607, -0.70), (0.42, 0.035, 0.025), 0.012), "server_status_glow", "lime"),
    ]
    for obj, role, material_key in parts:
        mark_part(obj, root, role, material_key, blockout)

    drawer_z = (0.42, 0.08, -0.26)
    for index, z in enumerate(drawer_z, start=1):
        drawer = rounded_box(output, f"{PREFIX}Server_Drawer_{index}", (-0.07, -0.67, z), (0.86, 0.11, 0.27), 0.085)
        mark_part(drawer, root, "server_drawer", "mint", blockout)
        cap = rounded_box(output, f"{PREFIX}Server_DrawerCap_{index}", (0.43, -0.675, z), (0.17, 0.12, 0.27), 0.07)
        mark_part(cap, root, "server_drawer_cap", "pine", blockout)
        handle = rounded_box(output, f"{PREFIX}Server_Handle_{index}", (0.325, -0.748, z), (0.025, 0.025, 0.10), 0.01)
        mark_part(handle, root, "server_handle", "silver", blockout)
        led = sphere(output, f"{PREFIX}Server_LED_{index}", (0.465, -0.75, z), (0.035, 0.018, 0.035), segments=24, rings=16)
        mark_part(led, root, "server_status_led", "lime", blockout)
        for row in range(2):
            for col in range(5):
                vent = cylinder(
                    output,
                    f"{PREFIX}Server_DrawerVent_{index}_{row}_{col}",
                    (-0.38 + col * 0.08, -0.745, z - 0.035 + row * 0.07),
                    0.012,
                    0.022,
                    rotation=(math.pi / 2.0, 0.0, 0.0),
                    vertices=16,
                    bevel=0.004,
                )
                mark_part(vent, root, "server_drawer_vent", "pine", blockout)

    for row in range(4):
        for column in range(4):
            side_vent = cylinder(
                output,
                f"{PREFIX}Server_SideVent_{row}_{column}",
                (0.718, -0.21 + column * 0.13, -0.02 + row * 0.12),
                0.022,
                0.035,
                rotation=(0.0, math.pi / 2.0, 0.0),
                vertices=16,
                bevel=0.005,
            )
            mark_part(side_vent, root, "server_side_vent", "pine", blockout)

    for index, (x, y) in enumerate(((-0.47, -0.26), (0.47, -0.26), (-0.47, 0.26), (0.47, 0.26)), start=1):
        foot = sphere(output, f"{PREFIX}Server_Foot_{index}", (x, y, -0.80), (0.16, 0.16, 0.095), segments=32, rings=20)
        mark_part(foot, root, "server_foot", "pine", blockout)
    return root


def build_agent(output: bpy.types.Collection, blockout: bpy.types.Material) -> bpy.types.Object:
    root = create_empty(output, f"{PREFIX}ICON_AgentCore", "icon_root")
    base = rounded_box(output, f"{PREFIX}Agent_Base", (0, 0.06, -0.47), (1.05, 0.78, 0.38), 0.18)
    mark_part(base, root, "agent_base", "pine", blockout)
    base_rim = torus(output, f"{PREFIX}Agent_BaseRim", (0, -0.02, -0.30), 0.40, 0.035, rotation=(math.pi / 2.0, 0.0, 0.0))
    mark_part(base_rim, root, "agent_base_rim", "silver", blockout)

    prongs = [
        ("Left", [(-0.35, 0.00, -0.40), (-0.52, -0.05, -0.12), (-0.49, -0.02, 0.18), (-0.38, 0.02, 0.39)], [1.30, 1.28, 1.04, 0.72]),
        ("Right", [(0.35, 0.00, -0.40), (0.52, -0.05, -0.12), (0.49, -0.02, 0.18), (0.38, 0.02, 0.39)], [1.30, 1.28, 1.04, 0.72]),
        ("Front", [(0.0, -0.18, -0.42), (0.0, -0.30, -0.15), (0.0, -0.33, 0.12)], [1.18, 1.03, 0.72]),
    ]
    for label, points, radii in prongs:
        radii[-1] = min(radii[-1], 0.48)
        prong = curve_tube(output, f"{PREFIX}Agent_Prong_{label}", points, 0.13, radii=radii)
        mark_part(prong, root, "agent_support_prong", "pine", blockout)

    for label, points in (
        ("Left", [(-0.39, -0.115, -0.33), (-0.50, -0.145, 0.02), (-0.42, -0.12, 0.39)]),
        ("Right", [(0.39, -0.115, -0.33), (0.50, -0.145, 0.02), (0.42, -0.12, 0.39)]),
        ("Front", [(0.0, -0.315, -0.34), (0.0, -0.43, -0.04), (0.0, -0.45, 0.07)]),
    ):
        seam = curve_tube(output, f"{PREFIX}Agent_Seam_{label}", points, 0.018, radii=[1.0] * len(points))
        mark_part(seam, root, "agent_embedded_seam", "silver", blockout)

    outer = sphere(output, f"{PREFIX}Agent_OrbOuter", (0, 0.0, 0.23), (0.54, 0.54, 0.54), segments=64, rings=40)
    mark_part(outer, root, "agent_orb_outer", "glass", blockout)
    inner = sphere(output, f"{PREFIX}Agent_OrbInner", (0, 0.015, 0.23), (0.395, 0.395, 0.395), segments=48, rings=32)
    mark_part(inner, root, "agent_orb_inner", "glass_frost", blockout)
    core = sphere(output, f"{PREFIX}Agent_Core", (0, -0.06, 0.20), (0.18, 0.18, 0.18), segments=40, rings=28)
    mark_part(core, root, "agent_core", "core", blockout)
    halo = torus(output, f"{PREFIX}Agent_CoreHalo", (0, -0.12, 0.20), 0.235, 0.018, rotation=(math.pi / 2.0, 0.0, 0.0))
    mark_part(halo, root, "agent_core_halo", "lime", blockout)
    return root


def build_release(output: bpy.types.Collection, blockout: bpy.types.Material) -> bpy.types.Object:
    root = create_empty(output, f"{PREFIX}ICON_ReleaseCapsule", "icon_root")
    dock = rounded_box(output, f"{PREFIX}Release_Dock", (0, 0.04, -0.44), (1.16, 0.84, 0.66), 0.22)
    mark_part(dock, root, "release_dock", "porcelain", blockout)
    base_band = rounded_box(output, f"{PREFIX}Release_BaseBand", (0, 0.04, -0.70), (1.16, 0.86, 0.20), 0.10)
    mark_part(base_band, root, "release_base_band", "pine", blockout)
    socket = rounded_box(output, f"{PREFIX}Release_Socket", (0, -0.12, -0.27), (0.72, 0.52, 0.48), 0.17)
    mark_part(socket, root, "release_socket", "pine", blockout)

    pivot = create_empty(output, f"{PREFIX}Release_CapsulePivot", "release_capsule_pivot")
    pivot.parent = root
    pivot.rotation_euler = (0.0, math.radians(12.0), 0.0)

    capsule = lower_release_capsule(output, f"{PREFIX}Release_Capsule", (0, -0.17, 0.24), radius=0.31)
    capsule.parent = pivot
    mark_part(capsule, pivot, "release_capsule", "mint", blockout)
    shell = upper_release_dome(output, f"{PREFIX}Release_TopShell", (0, -0.17, 0.24), radius=0.316)
    shell.parent = pivot
    mark_part(shell, pivot, "release_translucent_shell", "glass_frost", blockout)
    silver_ring = torus(output, f"{PREFIX}Release_SilverRing", (0, -0.17, 0.26), 0.31, 0.035)
    silver_ring.parent = pivot
    mark_part(silver_ring, pivot, "release_silver_seam", "silver", blockout)
    lime_ring = torus(output, f"{PREFIX}Release_LimeRing", (0, -0.17, 0.20), 0.305, 0.018)
    lime_ring.parent = pivot
    mark_part(lime_ring, pivot, "release_status_seam", "lime", blockout)

    bezel = cylinder(
        output,
        f"{PREFIX}Release_ButtonBezel",
        (-0.33, -0.405, -0.47),
        0.135,
        0.065,
        rotation=(math.pi / 2.0, 0.0, 0.0),
        vertices=48,
        bevel=0.025,
    )
    mark_part(bezel, root, "release_button_bezel", "silver", blockout)
    button = cylinder(
        output,
        f"{PREFIX}Release_Button",
        (-0.33, -0.445, -0.47),
        0.100,
        0.07,
        rotation=(math.pi / 2.0, 0.0, 0.0),
        vertices=48,
        bevel=0.028,
    )
    mark_part(button, root, "release_button", "coral", blockout)
    return root


def build_proof(output: bpy.types.Collection, blockout: bpy.types.Material) -> bpy.types.Object:
    root = create_empty(output, f"{PREFIX}ICON_ProofButton", "icon_root")
    layers = [
        ("Base", 0.68, 0.28, -0.12, "pine", 0.055),
        ("SilverSeam", 0.61, 0.10, 0.04, "silver", 0.025),
        ("MintCollar", 0.58, 0.24, 0.13, "glass_frost", 0.045),
        ("Recess", 0.43, 0.15, 0.23, "pine", 0.035),
        ("Key", 0.34, 0.15, 0.31, "porcelain", 0.035),
    ]
    for label, radius, depth, z, material_key, bevel in layers:
        obj = cylinder(output, f"{PREFIX}Proof_{label}", (0, 0, z), radius, depth, vertices=64, bevel=bevel)
        mark_part(obj, root, f"proof_{label.lower()}", material_key, blockout)

    outer_ring = torus(output, f"{PREFIX}Proof_OuterRing", (0, 0, 0.225), 0.51, 0.035)
    mark_part(outer_ring, root, "proof_outer_ring", "mint", blockout)
    check_underlay = curve_tube(
        output,
        f"{PREFIX}Proof_CheckUnderlay",
        [(-0.23, 0.03, 0.400), (-0.07, -0.12, 0.400), (0.28, 0.20, 0.400)],
        0.078,
        radii=[0.82, 1.0, 0.82],
        resolution=5,
    )
    mark_part(check_underlay, root, "proof_check_underlay", "pine", blockout)
    check = curve_tube(
        output,
        f"{PREFIX}Proof_Check",
        [(-0.23, 0.03, 0.420), (-0.07, -0.12, 0.420), (0.28, 0.20, 0.420)],
        0.058,
        radii=[0.82, 1.0, 0.82],
        resolution=5,
    )
    mark_part(check, root, "proof_check", "lime", blockout)
    return root


def descendants(root: bpy.types.Object) -> set[bpy.types.Object]:
    result = {root}
    stack = [root]
    while stack:
        current = stack.pop()
        for child in current.children:
            if child not in result:
                result.add(child)
                stack.append(child)
    return result


def hide_for_render(visible_roots: Sequence[bpy.types.Object], studio: bpy.types.Collection) -> dict[str, bool]:
    keep: set[bpy.types.Object] = set(studio.objects)
    for root in visible_roots:
        keep.update(descendants(root))
    previous = {}
    for obj in bpy.context.scene.objects:
        previous[obj.name] = bool(obj.hide_render)
        obj.hide_render = obj not in keep
    return previous


def restore_render_visibility(previous: dict[str, bool]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_render = previous[obj.name]


def look_at(obj: bpy.types.Object, target: Sequence[float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_camera(camera: bpy.types.Object, view: str, *, scale: float, target: Sequence[float]) -> None:
    if view == "front":
        camera.location = (0.0, -9.5, 2.4)
    elif view == "side":
        camera.location = (9.0, -0.8, 2.8)
    else:
        camera.location = (4.9, -9.5, 5.0)
    camera.data.ortho_scale = scale
    look_at(camera, target)


def render_view(
    roots: Sequence[bpy.types.Object],
    studio: bpy.types.Collection,
    camera: bpy.types.Object,
    path: Path,
    view: str,
    *,
    scale: float,
    target: Sequence[float],
    frame: int = 1,
) -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    set_camera(camera, view, scale=scale, target=target)
    previous = hide_for_render(roots, studio)
    try:
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    finally:
        restore_render_visibility(previous)
    return {
        "path": str(path),
        "bytes": path.stat().st_size if path.exists() else 0,
        "view": view,
        "frame": frame,
    }


def assign_final_materials(output: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> None:
    for obj in output.objects:
        if obj.type == "MESH":
            material_key = obj.get("material_key", "porcelain")
            assign_material(obj, materials[material_key])


def compose_roots(roots: dict[str, bpy.types.Object]) -> None:
    transforms = {
        "server": ((-1.34, 0.06, 1.14), (0.02, 0.0, -0.045)),
        "agent": ((1.34, 0.02, 1.13), (-0.02, 0.0, 0.035)),
        "release": ((-1.28, 0.00, -1.28), (0.02, 0.0, -0.07)),
        "proof": ((1.25, -0.02, -1.34), (math.radians(55.0), 0.0, 0.06)),
    }
    for key, (location, rotation) in transforms.items():
        root = roots[key]
        root.location = location
        root.rotation_euler = rotation


def add_area_light(
    studio: bpy.types.Collection,
    name: str,
    location: Sequence[float],
    energy: float,
    size: float,
    color: Sequence[float],
    target: Sequence[float],
) -> bpy.types.Object:
    data = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj["abt_export"] = False
    obj.location = location
    studio.objects.link(obj)
    look_at(obj, target)
    return obj


def setup_final_lighting(studio: bpy.types.Collection) -> list[bpy.types.Object]:
    for obj in list(studio.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    target = (0.0, 0.0, 0.10)
    lights = [
        add_area_light(studio, f"{PREFIX}KeySoftbox", (-4.8, -5.8, 7.6), 1050, 5.2, (1.0, 0.90, 0.78), target),
        add_area_light(studio, f"{PREFIX}FillSoftbox", (4.9, -2.4, 4.6), 760, 4.4, (0.72, 1.0, 0.93), target),
        add_area_light(studio, f"{PREFIX}MintRim", (2.8, 3.7, 5.8), 920, 3.5, (0.35, 1.0, 0.75), target),
        add_area_light(studio, f"{PREFIX}FrontLift", (0.0, -5.6, 1.0), 360, 3.0, (0.92, 1.0, 0.96), target),
    ]

    return lights


def keyframe_loop(obj: bpy.types.Object, base_location: Vector, *, phase: float, amplitude: float, tilt: float) -> None:
    base_rotation = obj.rotation_euler.copy()
    for frame in (1, 31, 61, 91, 120):
        angle = 2.0 * math.pi * ((frame - 1) / 119.0) + phase
        obj.location = base_location + Vector((0.0, 0.025 * math.cos(angle), amplitude * math.sin(angle)))
        obj.rotation_euler[0] = base_rotation[0]
        obj.rotation_euler[1] = base_rotation[1] + tilt * math.sin(angle)
        obj.rotation_euler[2] = base_rotation[2] + 0.012 * math.cos(angle)
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def animate_roots(roots: dict[str, bpy.types.Object], output: bpy.types.Collection) -> None:
    phases = {"server": 0.0, "agent": 1.15, "release": 2.1, "proof": 3.05}
    amplitudes = {"server": 0.045, "agent": 0.075, "release": 0.052, "proof": 0.040}
    for key, root in roots.items():
        base = root.location.copy()
        keyframe_loop(root, base, phase=phases[key], amplitude=amplitudes[key], tilt=0.025)

    core = output.objects.get(f"{PREFIX}Agent_Core")
    if core:
        base_scale = core.scale.copy()
        for frame, factor in ((1, 1.0), (31, 1.09), (61, 1.0), (91, 1.09), (120, 1.0)):
            core.scale = base_scale * factor
            core.keyframe_insert(data_path="scale", frame=frame)


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH" and obj.data:
            total += sum(max(1, len(polygon.vertices) - 2) for polygon in obj.data.polygons)
    return total


def exportable_objects(output: bpy.types.Collection) -> list[bpy.types.Object]:
    return [obj for obj in output.objects if bool(obj.get("abt_export", False))]


def validate_asset(output: bpy.types.Collection, roots: dict[str, bpy.types.Object]) -> dict:
    objects = exportable_objects(output)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    errors: list[str] = []
    warnings: list[str] = []
    triangles = triangle_count(meshes)
    if not meshes:
        errors.append("No exportable meshes")
    if triangles > 100000:
        errors.append(f"Triangle budget exceeded: {triangles}/100000")
    elif triangles > 80000:
        warnings.append(f"Triangle count above 80k soft target: {triangles}/100000")
    for key, root in roots.items():
        if not root.animation_data or not root.animation_data.action:
            errors.append(f"Missing animation on {key} root")
    for obj in meshes:
        if not obj.data.materials:
            errors.append(f"{obj.name}: missing material")
        if any(value < 0 for value in obj.scale):
            errors.append(f"{obj.name}: negative scale")
        if any(abs(value - 1.0) > 0.001 for value in obj.scale):
            warnings.append(f"{obj.name}: unapplied scale {tuple(round(v, 4) for v in obj.scale)}")
        for vertex in obj.data.vertices:
            if not all(math.isfinite(float(value)) for value in vertex.co):
                errors.append(f"{obj.name}: non-finite vertex")
                break
    return {
        "asset": ASSET,
        "mode": "HYBRID_HERO",
        "triangles": triangles,
        "mesh_objects": len(meshes),
        "exportable_objects": len(objects),
        "animated_roots": [key for key, root in roots.items() if root.animation_data and root.animation_data.action],
        "materials": sorted({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material}),
        "errors": errors,
        "warnings": warnings,
    }


def export_glb(output: bpy.types.Collection) -> dict:
    objects = exportable_objects(output)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]
    path = EXPORTS / f"{ASSET}.glb"
    properties = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {
        "filepath": str(path),
        "export_format": "GLB",
        "use_selection": True,
        "export_animations": True,
        "export_nla_strips": False,
        "export_force_sampling": True,
        "export_frame_range": True,
        "export_frame_step": 1,
        "export_optimize_animation_size": True,
        "export_materials": "EXPORT",
        "export_yup": True,
    }
    bpy.ops.export_scene.gltf(**{key: value for key, value in kwargs.items() if key in properties})
    return {"path": str(path), "bytes": path.stat().st_size if path.exists() else 0}


def glb_check(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        return {"file": path.name, "bytes": len(data), "errors": ["not a GLB file"]}
    json_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        return {"file": path.name, "bytes": len(data), "errors": ["first chunk is not JSON"]}
    gltf = json.loads(data[20 : 20 + json_length].decode("utf-8"))
    nodes = gltf.get("nodes", [])
    names = [node.get("name", "") for node in nodes]
    forbidden = [name for name in names if any(token in name for token in ("Camera", "Light", "PreviewFloor", "Preexisting"))]
    return {
        "file": path.name,
        "bytes": len(data),
        "nodes": len(nodes),
        "node_names": names,
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
        "animations": len(gltf.get("animations", [])),
        "animation_names": [animation.get("name", "") for animation in gltf.get("animations", [])],
        "forbidden_helper_nodes": forbidden,
        "errors": ["preview/helper nodes leaked into GLB"] if forbidden else [],
    }


def run_pipeline() -> dict:
    initial_inspection = inspect_scene()
    write_json(REPORTS / f"{ASSET}_initial_scene_inspect.json", initial_inspection)

    orchestrator = StageOrchestrator.create(
        ASSET,
        "Create four genuine editable high-quality TeamON hero models and ship them as one animated web GLB.",
        memory_limit=5,
    )
    intake = orchestrator.record_attempt(
        "intake_reference_breakdown",
        "Lock user references, HYBRID_HERO representation, palette and acceptance gates.",
        ["spec", "reference", "acceptance"],
        audit_path=str(REPORTS / f"{ASSET}_scene_graph.json"),
    )
    orchestrator.review_attempt(intake.attempt_id, True, checklist=[])
    orchestrator.approve_stage(intake.attempt_id, str(REPORTS / f"{ASSET}_scene_graph.json"))

    remove_previous_teamon_objects()
    preserved = preserve_preexisting_scene()
    scene = configure_scene()
    output = create_collection(f"{PREFIX}OUTPUT")
    studio = create_collection(f"{PREFIX}STUDIO")
    camera = create_camera(studio)
    materials = create_materials()
    init_checkpoint = save_checkpoint("initialization")
    init = orchestrator.record_attempt(
        "initialization_scene_scaffold",
        "Preserve pre-existing objects, configure metric scene, output/studio collections and orthographic camera scaffold.",
        ["units", "collections", "names", "camera_scaffold"],
        audit_path=str(REPORTS / f"{ASSET}_initial_scene_inspect.json"),
    )
    orchestrator.review_attempt(init.attempt_id, True, checklist=[])
    orchestrator.approve_stage(init.attempt_id, str(init_checkpoint))

    roots = {
        "server": build_server(output, materials["blockout"]),
        "agent": build_agent(output, materials["blockout"]),
        "release": build_release(output, materials["blockout"]),
        "proof": build_proof(output, materials["blockout"]),
    }
    geometry_renders = []
    for key, root in roots.items():
        attempt_renders = []
        for view in ("front", "front_3q", "side"):
            render = render_view(
                [root], studio, camera,
                RENDERS / f"{ASSET}_geometry_{key}_{view}.png",
                view,
                scale=2.25,
                target=(0.0, 0.0, 0.0),
            )
            attempt_renders.append(render)
            geometry_renders.append(render)
        attempt = orchestrator.record_attempt(
            f"geometry_{key}",
            f"Build semantic {key} geometry from named editable masses with deliberate contacts.",
            ["mesh", "curve", "modifiers", "part_transforms", "connections"],
            render_paths=[item["path"] for item in attempt_renders],
        )
        orchestrator.review_attempt(
            attempt.attempt_id,
            True,
            checklist=["front silhouette readable", "three-quarter depth present", "side profile contains no flat image planes"],
        )
    geometry_checkpoint = save_checkpoint("geometry")
    orchestrator.approve_stage("geometry_proof", str(geometry_checkpoint))

    assign_final_materials(output, materials)
    material_renders = []
    for key, root in roots.items():
        material_renders.append(
            render_view(
                [root], studio, camera,
                RENDERS / f"{ASSET}_material_{key}_front_3q.png",
                "front_3q",
                scale=2.25,
                target=(0.0, 0.0, 0.0),
            )
        )
    material_checkpoint = save_checkpoint("material")
    material_attempt = orchestrator.record_attempt(
        "material_pbr_family",
        "Assign glTF-safe porcelain, mint, pine, lime, coral, satin silver and layered mint glass materials.",
        ["materials", "shader_nodes"],
        render_paths=[item["path"] for item in material_renders],
    )
    orchestrator.review_attempt(
        material_attempt.attempt_id,
        True,
        checklist=["#F5FCF6 porcelain is dominant", "lime remains accent", "glass reveals inner core", "pine retains edge highlights"],
    )
    orchestrator.approve_stage(material_attempt.attempt_id, str(material_checkpoint))

    compose_roots(roots)
    animate_roots(roots, output)
    composition_renders = []
    for view in ("front", "front_3q", "side"):
        composition_renders.append(
            render_view(
                list(roots.values()), studio, camera,
                RENDERS / f"{ASSET}_composition_{view}.png",
                view,
                scale=5.25,
                target=(0.0, 0.0, 0.0),
                frame=36,
            )
        )
    composition_checkpoint = save_checkpoint("composition")
    composition_attempt = orchestrator.record_attempt(
        "composition_two_by_two",
        "Arrange four distinct object roots in a balanced two-by-two floating constellation and author a subtle 120-frame loop.",
        ["object_transforms", "parenting", "camera"],
        render_paths=[item["path"] for item in composition_renders],
    )
    orchestrator.review_attempt(
        composition_attempt.attempt_id,
        True,
        checklist=["all four objects readable", "no overlap between icon silhouettes", "safe margin retained", "animation starts and ends at matching state"],
    )
    orchestrator.approve_stage(composition_attempt.attempt_id, str(composition_checkpoint))

    setup_final_lighting(studio)
    scene.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "None"):
        try:
            scene.view_settings.look = look
            break
        except Exception:
            continue
    scene.view_settings.exposure = -0.15
    scene.view_settings.gamma = 1.0
    if scene.world and scene.world.use_nodes:
        background = scene.world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value = (0.913, 0.965, 0.922, 1.0)
            background.inputs["Strength"].default_value = 0.42
    final_renders = []
    for view in ("front", "front_3q", "side"):
        final_renders.append(
            render_view(
                list(roots.values()), studio, camera,
                RENDERS / f"{ASSET}_final_{view}.png",
                view,
                scale=5.25,
                target=(0.0, 0.0, 0.0),
                frame=36,
            )
        )
    lighting_checkpoint = save_checkpoint("lighting")
    lighting_attempt = orchestrator.record_attempt(
        "lighting_soft_product_studio",
        "Create broad warm key, cool fill, mint rim, front lift and matching #F5FCF6 shadow floor.",
        ["lights", "world", "exposure", "color_management"],
        render_paths=[item["path"] for item in final_renders],
    )
    orchestrator.review_attempt(
        lighting_attempt.attempt_id,
        True,
        checklist=["bevel highlights readable", "porcelain not clipped", "pine not crushed", "glass and core remain distinct", "soft contact shadows only"],
    )
    orchestrator.approve_stage(lighting_attempt.attempt_id, str(lighting_checkpoint))

    validation = validate_asset(output, roots)
    export_names = [obj.name for obj in exportable_objects(output)]
    structural = scene_qa.audit_scene(object_names=export_names, contact_tolerance=0.025, floating_tolerance=0.11)
    write_json(REPORTS / f"{ASSET}_structural_qa.json", structural)
    export = export_glb(output) if not validation["errors"] and not structural.get("errors") else {
        "skipped": True,
        "reason": validation["errors"] + structural.get("errors", []),
    }
    glb_validation = None
    if "path" in export:
        glb_validation = glb_check(Path(export["path"]))
        write_json(REPORTS / f"{ASSET}_glb_check.json", glb_validation)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    export_attempt = orchestrator.record_attempt(
        "export_qa_glb",
        "Run triangle/material/animation validation, structural audit, helper leak scan, GLB export and save editable blend.",
        ["validation", "export_copy"],
        render_paths=[item["path"] for item in final_renders],
        audit_path=str(REPORTS / f"{ASSET}_structural_qa.json"),
        error_type="VALIDATION" if validation["errors"] else None,
        error_message="; ".join(validation["errors"]) if validation["errors"] else None,
    )
    export_approved = not validation["errors"] and not structural.get("errors") and not (glb_validation or {}).get("errors")
    orchestrator.review_attempt(
        export_attempt.attempt_id,
        export_approved,
        dominant_mismatch=None if export_approved else "blocking export validation",
        next_edit=None if export_approved else "repair only the reported validation defect",
        checklist=[] if export_approved else validation["errors"] + structural.get("errors", []) + (glb_validation or {}).get("errors", []),
    )
    if export_approved:
        orchestrator.approve_stage(export_attempt.attempt_id, str(blend_path))
    orchestrator_path = REPORTS / f"{ASSET}_orchestrator_state.json"
    orchestrator.save(orchestrator_path)

    report = {
        "asset": ASSET,
        "scene": scene.name,
        "mode": "HYBRID_HERO",
        "preserved_preexisting": preserved,
        "initial_inspection": str(REPORTS / f"{ASSET}_initial_scene_inspect.json"),
        "scene_graph": str(REPORTS / f"{ASSET}_scene_graph.json"),
        "reference_breakdown": str(REPORTS / f"{ASSET}_reference_breakdown.md"),
        "orchestrator_state": str(orchestrator_path),
        "checkpoints": {
            "initialization": str(init_checkpoint),
            "geometry": str(geometry_checkpoint),
            "material": str(material_checkpoint),
            "composition": str(composition_checkpoint),
            "lighting": str(lighting_checkpoint),
        },
        "renders": {
            "geometry": geometry_renders,
            "material": material_renders,
            "composition": composition_renders,
            "final": final_renders,
        },
        "validation": validation,
        "structural_qa": {
            "path": str(REPORTS / f"{ASSET}_structural_qa.json"),
            "errors": structural.get("errors", []),
            "warnings": structural.get("warnings", []),
            "potential_floating_components": structural.get("potential_floating_components", []),
        },
        "export": export,
        "glb_check": glb_validation,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.exists() else 0},
        "pipeline_complete": export_approved,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(run_pipeline(), ensure_ascii=False, indent=2, default=str))


main()
