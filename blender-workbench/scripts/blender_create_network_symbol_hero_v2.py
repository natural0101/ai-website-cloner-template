from __future__ import annotations

import json
import math
import shutil
import struct
from datetime import datetime
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
WORKBENCH = SCRIPT.parents[1]
REPO = SCRIPT.parents[2]
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"
REFERENCES = WORKBENCH / "references"
REFERENCE = REFERENCES / "network-symbol-primary.png"

ASSET = "network_symbol_hero_v2"
SCENE_NAME = "NetworkSymbolHeroV2"
WIDTH = 900
HEIGHT = 900
FRAMES = (1, 48, 96, 132)
END_FRAME = 132

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS, REFERENCES):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def set_socket(node: bpy.types.Node, names: Iterable[str], value) -> None:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def create_material(
    name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = base_color[0], base_color[1], base_color[2], alpha
    mat.use_nodes = True
    mat.blend_method = "BLEND" if alpha < 1.0 else "OPAQUE"
    mat.use_screen_refraction = False
    principled = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        set_socket(principled, ("Base Color",), (base_color[0], base_color[1], base_color[2], alpha))
        set_socket(principled, ("Alpha",), alpha)
        set_socket(principled, ("Metallic",), metallic)
        set_socket(principled, ("Roughness",), roughness)
        set_socket(principled, ("Specular IOR Level", "Specular"), 0.46)
        set_socket(principled, ("Coat Weight", "Clearcoat", "Coat"), 0.06)
        set_socket(principled, ("Coat Roughness",), 0.5)
        if emission is not None:
            set_socket(principled, ("Emission Color", "Emission"), emission)
            set_socket(principled, ("Emission Strength", "Emission Weight"), emission_strength)
    return mat


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def link_to(collection: bpy.types.Collection, obj: bpy.types.Object) -> bpy.types.Object:
    if collection.objects.get(obj.name) is None:
        collection.objects.link(obj)
    for coll in list(obj.users_collection):
        if coll != collection:
            coll.objects.unlink(obj)
    return obj


def shade_smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def parent_keep_world(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_empty(collection: bpy.types.Collection, name: str, location=(0.0, 0.0, 0.0), export: bool = True) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.12
    empty.location = location
    collection.objects.link(empty)
    return tag(empty, "animation_parent", export)


def apply_transform(obj: bpy.types.Object) -> None:
    active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)
    bpy.context.view_layer.objects.active = active


def create_flat_sphere(
    collection: bpy.types.Collection,
    name: str,
    point: tuple[float, float],
    radius: float,
    y: float,
    mat: bpy.types.Material,
    depth: float = 0.42,
    role: str = "node",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.0, location=(point[0], y, point[1]))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius, radius * depth, radius)
    obj.data.materials.append(mat)
    shade_smooth(obj)
    apply_transform(obj)
    link_to(collection, obj)
    return tag(obj, role, True)


def join_objects(name: str, objects: list[bpy.types.Object], collection: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = name
    joined.data.name = f"{name}_Mesh"
    link_to(collection, joined)
    return joined


def create_capsule(
    collection: bpy.types.Collection,
    name: str,
    a: tuple[float, float],
    b: tuple[float, float],
    radius: float,
    y: float,
    mat: bpy.types.Material,
    role: str = "connector",
) -> bpy.types.Object:
    start = Vector((a[0], y, a[1]))
    end = Vector((b[0], y, b[1]))
    delta = end - start
    mid = (start + end) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=delta.length, location=mid)
    cylinder = bpy.context.object
    cylinder.name = f"{name}_body"
    cylinder.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    cylinder.data.materials.append(mat)
    shade_smooth(cylinder)
    cap_objects = [cylinder]
    for index, point in enumerate((start, end), start=1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=point)
        cap = bpy.context.object
        cap.name = f"{name}_cap_{index}"
        cap.data.materials.append(mat)
        shade_smooth(cap)
        cap_objects.append(cap)
    obj = join_objects(name, cap_objects, collection)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return tag(obj, role, True)


def create_ring_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    radius: float = 0.055,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=radius * 0.16,
        major_segments=36,
        minor_segments=8,
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    shade_smooth(obj)
    link_to(collection, obj)
    return tag(obj, "floating_symbol", True)


def create_docking_ring(
    collection: bpy.types.Collection,
    name: str,
    point: tuple[float, float],
    y: float,
    mat: bpy.types.Material,
    radius: float,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=max(0.009, radius * 0.045),
        major_segments=64,
        minor_segments=8,
        location=(point[0], y, point[1]),
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    shade_smooth(obj)
    link_to(collection, obj)
    return tag(obj, "docking_socket", True)


def create_tiny_dot(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    radius: float = 0.035,
) -> bpy.types.Object:
    obj = create_flat_sphere(collection, name, (location[0], location[2]), radius, location[1], mat, depth=0.8, role="floating_symbol")
    return obj


def create_short_bar_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    angle: float,
    mat: bpy.types.Material,
    length: float = 0.16,
) -> bpy.types.Object:
    x, y, z = location
    dx = math.cos(angle) * length * 0.5
    dz = math.sin(angle) * length * 0.5
    return create_capsule(collection, name, (x - dx, z - dz), (x + dx, z + dz), 0.016, y, mat, role="floating_symbol")


def key(obj: bpy.types.Object, frame: int, loc=None, rot=None, scale=None) -> None:
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


def make_animation_smooth(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        fcurves = getattr(action, "fcurves", None)
        if fcurves is None:
            continue
        for fcurve in fcurves:
            for point in fcurve.keyframe_points:
                point.interpolation = "BEZIER"


def build_base_icon(
    collection: bpy.types.Collection,
    prefix: str,
    mats: dict[str, bpy.types.Material],
) -> dict[str, list[bpy.types.Object] | dict[str, bpy.types.Object]]:
    dark_y = 0.08
    green_y = -0.12
    dark = []
    green = []
    sockets = []
    named: dict[str, bpy.types.Object] = {}

    points = {
        "top": (0.00, 0.91),
        "left_top": (-0.86, 0.47),
        "left_bottom": (-0.86, -0.47),
        "bottom": (0.00, -0.91),
        "center": (0.02, 0.00),
        "right_top": (0.84, 0.47),
        "right_bottom": (0.84, -0.47),
    }

    dark_edges = (
        ("top", "left_top"),
        ("left_top", "left_bottom"),
        ("left_bottom", "bottom"),
        ("top", "bottom"),
        ("left_top", "center"),
        ("left_bottom", "center"),
        ("top", "right_top"),
        ("bottom", "right_bottom"),
    )
    for index, (a, b) in enumerate(dark_edges, start=1):
        dark.append(create_capsule(collection, f"{prefix}_DarkEdge_{index:02d}_{a}_to_{b}", points[a], points[b], 0.065, dark_y, mats["dark"]))

    for name, radius in (("top", 0.245), ("left_top", 0.245), ("left_bottom", 0.245), ("bottom", 0.245)):
        dark.append(create_flat_sphere(collection, f"{prefix}_DarkNode_{name}", points[name], radius, dark_y - 0.01, mats["dark"]))

    for name, radius in (("center", 0.365), ("right_top", 0.33), ("right_bottom", 0.305)):
        sockets.append(create_docking_ring(collection, f"{prefix}_DockingRing_{name}", points[name], dark_y + 0.012, mats["socket"], radius))

    green_edges = (
        ("center_to_right_top", "center", "right_top"),
        ("center_to_right_bottom", "center", "right_bottom"),
        ("right_top_to_right_bottom", "right_top", "right_bottom"),
    )
    for edge_name, a, b in green_edges:
        obj = create_capsule(collection, f"{prefix}_GreenEdge_{edge_name}", points[a], points[b], 0.082, green_y, mats["green"], role="green_connector")
        green.append(obj)
        named[f"edge_{edge_name}"] = obj

    for name, radius in (("center", 0.35), ("right_top", 0.318), ("right_bottom", 0.292)):
        obj = create_flat_sphere(collection, f"{prefix}_GreenNode_{name}", points[name], radius, green_y - 0.012, mats["green"], role="green_node")
        green.append(obj)
        named[f"node_{name}"] = obj

    return {"dark": dark, "green": green, "sockets": sockets, "named": named, "all": dark + sockets + green}


def add_particle_field(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material], positions: list[tuple[float, float, float]]) -> list[bpy.types.Object]:
    particles = []
    for index, loc in enumerate(positions, start=1):
        if index % 4 == 0:
            particle = create_ring_symbol(collection, f"{prefix}_ParticleRing_{index:02d}", loc, mats["particle"], radius=0.048)
        elif index % 3 == 0:
            particle = create_short_bar_symbol(collection, f"{prefix}_ParticleBar_{index:02d}", loc, math.radians(22 + index * 19), mats["particle"], length=0.13)
        else:
            particle = create_tiny_dot(collection, f"{prefix}_ParticleDot_{index:02d}", loc, mats["particle"], radius=0.030 + 0.004 * (index % 2))
        particles.append(particle)
    return particles


def animate_layer_detach(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_base_icon(collection, prefix, mats)
    root = create_empty(collection, f"{prefix}_GreenSignalLayer_ROOT")
    for obj in parts["green"]:
        parent_keep_world(obj, root)

    particles = add_particle_field(
        collection,
        prefix,
        mats,
        [
            (1.17, -0.34, 0.66),
            (1.37, -0.32, 0.25),
            (1.10, -0.35, -0.64),
            (1.48, -0.34, -0.24),
            (0.68, -0.33, 0.76),
        ],
    )
    for particle in particles:
        key(particle, 1, scale=(0.01, 0.01, 0.01))
        key(particle, 56, scale=(0.72, 0.72, 0.72))
        key(particle, 132, scale=(1.0, 1.0, 1.0))

    key(root, 1, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0))
    key(root, 44, loc=(0.13, -0.08, 0.04), rot=(math.radians(1.0), math.radians(-4.0), math.radians(1.5)))
    key(root, 88, loc=(0.38, -0.26, 0.02), rot=(math.radians(2.0), math.radians(-10.0), math.radians(3.0)))
    key(root, 132, loc=(0.34, -0.22, 0.08), rot=(math.radians(-1.5), math.radians(-7.0), math.radians(-2.0)))

    animated = [root, *particles]
    make_animation_smooth(animated)
    return {"objects": parts["all"] + [root] + particles, "animated": animated}


def animate_signal_assembly(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_base_icon(collection, prefix, mats)
    named = parts["named"]
    start_offsets = {
        "node_center": (0.22, -0.28, 0.52),
        "node_right_top": (0.30, -0.30, 0.24),
        "node_right_bottom": (0.32, -0.30, -0.26),
    }

    for key_name, obj in named.items():
        final_loc = obj.location.copy()
        if key_name.startswith("edge_"):
            key(obj, 1, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(0.01, 0.01, 0.01))
            key(obj, 60, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(0.18, 0.18, 0.18))
            key(obj, 96, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
            key(obj, 132, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
        else:
            offset = start_offsets.get(key_name, (0.0, 0.0, 0.0))
            start_loc = (final_loc.x + offset[0], final_loc.y + offset[1], final_loc.z + offset[2])
            key(obj, 1, loc=start_loc, rot=(0.0, math.radians(12.0), math.radians(8.0)), scale=(0.86, 0.86, 0.86))
            key(obj, 52, loc=(final_loc.x + offset[0] * 0.35, final_loc.y + offset[1] * 0.5, final_loc.z + offset[2] * 0.34), rot=(0.0, math.radians(-6.0), math.radians(-3.0)), scale=(0.96, 0.96, 0.96))
            key(obj, 96, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
            key(obj, 132, loc=(final_loc.x, final_loc.y, final_loc.z), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    particles = add_particle_field(
        collection,
        prefix,
        mats,
        [
            (1.28, -0.36, 0.62),
            (1.42, -0.36, 0.18),
            (1.22, -0.36, -0.48),
            (0.72, -0.36, 0.72),
        ],
    )
    for index, particle in enumerate(particles, start=1):
        key(particle, 1, loc=particle.location.copy(), scale=(0.9, 0.9, 0.9), rot=(0.0, 0.0, math.radians(index * 30)))
        key(particle, 80, loc=(0.90 + 0.05 * index, -0.34, 0.10 - 0.08 * index), scale=(0.48, 0.48, 0.48), rot=(0.0, 0.0, math.radians(index * 80)))
        key(particle, 132, loc=(0.92, -0.34, 0.0), scale=(0.01, 0.01, 0.01), rot=(0.0, 0.0, math.radians(index * 140)))

    animated = list(named.values()) + particles
    make_animation_smooth(animated)
    return {"objects": parts["all"] + particles, "animated": animated}


def animate_magnetic_reconnect(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_base_icon(collection, prefix, mats)
    root = create_empty(collection, f"{prefix}_MagneticSignalLayer_ROOT")
    for obj in parts["green"]:
        parent_keep_world(obj, root)

    key(root, 1, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    key(root, 45, loc=(0.28, -0.30, 0.10), rot=(math.radians(1.0), math.radians(-13.0), math.radians(4.0)), scale=(1.04, 1.04, 1.04))
    key(root, 82, loc=(0.10, -0.14, 0.03), rot=(math.radians(-1.0), math.radians(7.0), math.radians(-2.5)), scale=(0.98, 0.98, 0.98))
    key(root, 132, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    particles = add_particle_field(
        collection,
        prefix,
        mats,
        [
            (1.05, -0.35, 0.74),
            (1.38, -0.36, 0.34),
            (1.36, -0.36, -0.35),
            (0.80, -0.35, -0.72),
            (0.58, -0.34, 0.22),
        ],
    )
    for index, particle in enumerate(particles, start=1):
        origin = particle.location.copy()
        key(particle, 1, loc=(0.55, -0.32, 0.02), scale=(0.01, 0.01, 0.01), rot=(0.0, 0.0, 0.0))
        key(particle, 50, loc=(origin.x, origin.y, origin.z), scale=(1.0, 1.0, 1.0), rot=(0.0, 0.0, math.radians(72 * index)))
        key(particle, 92, loc=(0.70 + index * 0.04, -0.35, 0.18 - index * 0.07), scale=(0.55, 0.55, 0.55), rot=(0.0, 0.0, math.radians(120 * index)))
        key(particle, 132, loc=(0.50, -0.32, 0.00), scale=(0.01, 0.01, 0.01), rot=(0.0, 0.0, math.radians(180 * index)))

    animated = [root] + particles
    make_animation_smooth(animated)
    return {"objects": parts["all"] + [root] + particles, "animated": animated}


def safe_render_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def setup_scene() -> bpy.types.Scene:
    if bpy.context.scene.objects:
        checkpoint = CHECKPOINTS / f"{ASSET}_prechange_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.render.fps = 24
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.24
    scene.view_settings.gamma = 1.0

    engine = safe_render_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.1),
            ("gtao_factor", 0.7),
            ("use_bloom", True),
            ("bloom_intensity", 0.04),
            ("bloom_radius", 4.0),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("NetworkHeroWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        background.inputs["Strength"].default_value = 0.22
    return scene


def setup_camera() -> bpy.types.Object:
    data = bpy.data.cameras.new("NSH_Camera_FRONT")
    camera = bpy.data.objects.new("NSH_Camera_FRONT", data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (0.0, -6.8, 0.0)
    camera.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.05
    bpy.context.scene.camera = camera
    return tag(camera, "review_camera", False)


def setup_lights() -> list[bpy.types.Object]:
    specs = [
        ("NSH_Key_not_exported", (-3.0, -4.3, 3.4), 260.0, 3.8),
        ("NSH_SoftFill_not_exported", (3.4, -3.2, 2.1), 76.0, 5.4),
        ("NSH_GreenRim_not_exported", (2.2, -2.0, 1.4), 55.0, 2.8),
    ]
    lights = []
    for name, location, power, size in specs:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = power
        light.size = size
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
        lights.append(tag(obj, "studio_light", False))
    return lights


def create_reference_plane() -> None:
    if not REFERENCE.is_file():
        return
    mat = create_material("NSH_ReferencePlaneMaterial_not_exported", (1.0, 1.0, 1.0, 1.0), 0.5, alpha=0.32)
    nodes = mat.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(REFERENCE))
    if principled is not None:
        mat.node_tree.links.new(tex.outputs["Color"], principled.inputs["Base Color"])
        set_socket(principled, ("Alpha",), 0.28)
    bpy.ops.mesh.primitive_plane_add(size=2.3, location=(0.0, 0.36, 0.0), rotation=(math.radians(90.0), 0.0, 0.0))
    plane = bpy.context.object
    plane.name = "NSH_PrimaryReferencePlane_not_exported"
    plane.data.materials.append(mat)
    plane.hide_render = True
    plane.hide_set(True)
    tag(plane, "reference_plane", False)


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    shown = {obj.name for obj in collection.all_objects}
    previous = {}
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_render, obj.hide_get())
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_render = False
            obj.hide_set(False)
        else:
            is_shown = obj.name in shown
            obj.hide_render = not is_shown
            obj.hide_set(not is_shown)
    return previous


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            hidden_render, hidden_view = previous[obj.name]
            obj.hide_render = hidden_render
            obj.hide_set(hidden_view)


def render_collection(collection: bpy.types.Collection, frame: int, destination: Path) -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    previous = hide_except(collection)
    try:
        scene.render.filepath = str(destination)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"path": str(destination), "bytes": destination.stat().st_size if destination.is_file() else 0, "frame": frame}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def validate_collection(collection: bpy.types.Collection, name: str, budget: int = 60000) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    triangles = triangle_count(meshes)
    errors = []
    warnings = []
    if not meshes:
        errors.append("No exportable mesh objects.")
    if triangles > budget:
        warnings.append(f"Triangle budget above target: {triangles}/{budget}.")
    return {
        "asset": name,
        "triangles": triangles,
        "mesh_objects": len(meshes),
        "animated_objects": len([obj for obj in exportable if obj.animation_data]),
        "errors": errors,
        "warnings": warnings,
    }


def export_collection(collection: bpy.types.Collection, name: str) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    destination = EXPORTS / f"{name}.glb"
    properties = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {
        "filepath": str(destination),
        "export_format": "GLB",
        "use_selection": True,
    }
    for option, value in (
        ("export_animations", True),
        ("export_frame_range", True),
        ("export_force_sampling", True),
        ("export_nla_strips", True),
        ("export_optimize_animation_size", True),
        ("export_apply", True),
    ):
        if option in properties:
            kwargs[option] = value
    bpy.ops.export_scene.gltf(**kwargs)
    public_path = PUBLIC_MODELS / destination.name
    shutil.copy2(destination, public_path)
    return {
        "path": str(destination),
        "public_path": str(public_path),
        "bytes": destination.stat().st_size if destination.is_file() else 0,
        "triangles": triangle_count(meshes),
        "objects": [obj.name for obj in exportable],
    }


def glb_animation_check(paths: Iterable[Path]) -> list[dict]:
    checks = []
    for path in paths:
        data = path.read_bytes()
        magic, _, _ = struct.unpack_from("<4sII", data, 0)
        if magic != b"glTF":
            checks.append({"file": path.name, "error": "not_glb"})
            continue
        chunk_len, _ = struct.unpack_from("<II", data, 12)
        gltf = json.loads(data[20 : 20 + chunk_len].decode("utf-8"))
        checks.append(
            {
                "file": path.name,
                "bytes": path.stat().st_size,
                "animations": len(gltf.get("animations", [])),
                "nodes": len(gltf.get("nodes", [])),
                "meshes": len(gltf.get("meshes", [])),
            }
        )
    return checks


def build_scene() -> dict:
    scene = setup_scene()
    setup_camera()
    setup_lights()
    create_reference_plane()

    mats = {
        "dark": create_material("NSH_DarkGraph_MatteBlueBlack", (0.006, 0.030, 0.037, 1.0), 0.55, emission=(0.0, 0.018, 0.022, 1.0), emission_strength=0.04),
        "green": create_material("NSH_SignalGreen_Glow", (0.0, 0.92, 0.05, 1.0), 0.43, emission=(0.0, 0.72, 0.05, 1.0), emission_strength=0.34),
        "socket": create_material("NSH_GreenDockingSocket_Dim", (0.0, 0.36, 0.07, 1.0), 0.6, emission=(0.0, 0.18, 0.04, 1.0), emission_strength=0.22, alpha=0.62),
        "particle": create_material("NSH_FloatingSignalParticle", (0.08, 1.0, 0.12, 1.0), 0.38, emission=(0.04, 0.9, 0.08, 1.0), emission_strength=0.58),
    }

    specs = [
        ("network_symbol_hero_v2_layer_detach", "NSH_Variant01_LayerDetach", animate_layer_detach),
        ("network_symbol_hero_v2_signal_assembly", "NSH_Variant02_SignalAssembly", animate_signal_assembly),
        ("network_symbol_hero_v2_magnetic_reconnect", "NSH_Variant03_MagneticReconnect", animate_magnetic_reconnect),
    ]

    collections: list[tuple[str, bpy.types.Collection]] = []
    for index, (export_name, collection_name, animator) in enumerate(specs, start=1):
        collection = create_collection(collection_name)
        animator(collection, f"NSH{index:02d}", mats)
        collections.append((export_name, collection))

    scene_graph = {
        "asset": ASSET,
        "scene": scene.name,
        "primary_reference": str(REFERENCE),
        "mode": "icon/hero object",
        "target": "landing-page hero GLB pack",
        "visual_intent": "A dark molecular/network mark stays as the base while the green signal layer separates, assembles, or magnetically reconnects.",
        "reference_breakdown": {
            "silhouette": "central/right green triangular module over a dark hexagonal network",
            "palette": "black background, blue-black dark graph, saturated neon green foreground",
            "occlusion_order": "dark graph behind, dim docking sockets in middle, green layer in front",
            "camera": "orthographic front crop, slightly wider than reference so animation has room",
            "material": "smooth high-roughness toy/web PBR with modest emissive green",
        },
        "animation_variants": [
            "layer_detach: green module remains intact and floats out from the dark graph",
            "signal_assembly: green pieces gather from the right and form the original mark",
            "magnetic_reconnect: green layer pulses outward, then snaps back into place",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    renders = {}
    for export_name, collection in collections:
        renders[export_name] = []
        for frame in FRAMES:
            renders[export_name].append(render_collection(collection, frame, RENDERS / f"{export_name}_frame_{frame:03d}.png"))

    validation = {}
    exports = {}
    glb_paths = []
    for export_name, collection in collections:
        validation[export_name] = validate_collection(collection, export_name)
        if not validation[export_name]["errors"]:
            exports[export_name] = export_collection(collection, export_name)
            glb_paths.append(Path(exports[export_name]["path"]))

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    animation_check = glb_animation_check(glb_paths)
    write_json(REPORTS / f"{ASSET}_glb_animation_check.json", {"checks": animation_check})

    report = {
        "asset": ASSET,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "renders": renders,
        "validation": validation,
        "exports": exports,
        "glb_animation_check": animation_check,
        "warnings": [
            "Blender MCP socket was unavailable in the previous pass; this script is designed for Blender background execution.",
            "Floating green parts are intentional animation states for landing-page motion.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(build_scene(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
