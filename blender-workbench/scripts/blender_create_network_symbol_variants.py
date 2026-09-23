from __future__ import annotations

import json
import math
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
REFERENCES = WORKBENCH / "references"
REFERENCE = REFERENCES / "network-symbol-primary.png"

ASSET = "network_symbol_detach_variants_v1"
SCENE_NAME = "NetworkSymbolDetachVariants"
WIDTH = 768
HEIGHT = 768
FRAMES = (1, 60, 120)

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, REFERENCES):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def set_socket(node: bpy.types.Node, names: Iterable[str], value) -> None:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def safe_render_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    principled = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        set_socket(principled, ("Base Color",), color)
        set_socket(principled, ("Metallic",), metallic)
        set_socket(principled, ("Roughness",), roughness)
        set_socket(principled, ("Specular IOR Level", "Specular"), 0.42)
        set_socket(principled, ("Coat Weight", "Clearcoat", "Coat"), 0.04)
        set_socket(principled, ("Coat Roughness",), 0.62)
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


def apply_scale(obj: bpy.types.Object) -> None:
    previous = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = previous


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_empty(collection: bpy.types.Collection, name: str, location: tuple[float, float, float]) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.18
    empty.location = location
    collection.objects.link(empty)
    tag(empty, "animation_parent", True)
    return empty


def create_node(
    collection: bpy.types.Collection,
    name: str,
    x: float,
    z: float,
    radius: float,
    y: float,
    mat: bpy.types.Material,
    depth_scale: float = 0.42,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1.0, location=(x, y, z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius, radius * depth_scale, radius)
    obj.data.materials.append(mat)
    shade_smooth(obj)
    apply_scale(obj)
    link_to(collection, obj)
    return tag(obj, "node", True)


def create_connector(
    collection: bpy.types.Collection,
    name: str,
    a: tuple[float, float],
    b: tuple[float, float],
    radius: float,
    y: float,
    mat: bpy.types.Material,
    z_lift: float = 0.0,
) -> bpy.types.Object:
    start = Vector((a[0], y, a[1] + z_lift))
    end = Vector((b[0], y, b[1] + z_lift))
    delta = end - start
    midpoint = (start + end) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=delta.length, location=midpoint)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    shade_smooth(obj)
    link_to(collection, obj)
    return tag(obj, "connector", True)


def create_torus_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    parent: bpy.types.Object | None = None,
) -> list[bpy.types.Object]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.065,
        minor_radius=0.012,
        major_segments=32,
        minor_segments=8,
        location=location,
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    shade_smooth(obj)
    link_to(collection, obj)
    if parent is not None:
        local_location = obj.location.copy()
        local_rotation = obj.rotation_euler.copy()
        obj.parent = parent
        obj.location = local_location
        obj.rotation_euler = local_rotation
    return [tag(obj, "floating_symbol", True)]


def create_plus_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    parent: bpy.types.Object | None = None,
) -> list[bpy.types.Object]:
    x, y, z = location
    horizontal = create_connector(collection, f"{name}_horizontal", (x - size, z), (x + size, z), 0.014, y, mat)
    vertical = create_connector(collection, f"{name}_vertical", (x, z - size), (x, z + size), 0.014, y, mat)
    for obj in (horizontal, vertical):
        if parent is not None:
            local_location = obj.location.copy()
            local_rotation = obj.rotation_euler.copy()
            obj.parent = parent
            obj.location = local_location
            obj.rotation_euler = local_rotation
        obj["role"] = "floating_symbol"
    return [horizontal, vertical]


def create_chevron_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    parent: bpy.types.Object | None = None,
) -> list[bpy.types.Object]:
    x, y, z = location
    upper = create_connector(collection, f"{name}_upper", (x - size * 0.55, z + size), (x + size * 0.55, z), 0.012, y, mat)
    lower = create_connector(collection, f"{name}_lower", (x - size * 0.55, z - size), (x + size * 0.55, z), 0.012, y, mat)
    for obj in (upper, lower):
        if parent is not None:
            local_location = obj.location.copy()
            local_rotation = obj.rotation_euler.copy()
            obj.parent = parent
            obj.location = local_location
            obj.rotation_euler = local_rotation
        obj["role"] = "floating_symbol"
    return [upper, lower]


def create_dot_symbol(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
    parent: bpy.types.Object | None = None,
) -> list[bpy.types.Object]:
    obj = create_node(collection, name, location[0], location[2], 0.045, location[1], mat, depth_scale=0.72)
    obj["role"] = "floating_symbol"
    if parent is not None:
        local_location = obj.location.copy()
        local_rotation = obj.rotation_euler.copy()
        obj.parent = parent
        obj.location = local_location
        obj.rotation_euler = local_rotation
    return [obj]


def keyframe(
    obj: bpy.types.Object,
    frame: int,
    location: tuple[float, float, float] | None = None,
    rotation: tuple[float, float, float] | None = None,
    scale: tuple[float, float, float] | None = None,
) -> None:
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


def set_bezier_animation(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        fcurves = getattr(action, "fcurves", None)
        if fcurves is not None:
            for fcurve in fcurves:
                for point in fcurve.keyframe_points:
                    point.interpolation = "BEZIER"


def build_network(
    collection: bpy.types.Collection,
    prefix: str,
    dark_mat: bpy.types.Material,
    green_mat: bpy.types.Material,
    symbol_mat: bpy.types.Material,
    symbol_variant: int,
) -> dict:
    dark_y = 0.045
    green_y = -0.075
    dark_nodes = {
        "top": (0.00, 0.92, 0.255),
        "left_top": (-0.88, 0.50, 0.255),
        "left_bottom": (-0.88, -0.50, 0.255),
        "bottom": (0.00, -0.92, 0.255),
    }
    dark_edges = [
        ("top", "left_top"),
        ("left_top", "left_bottom"),
        ("left_bottom", "bottom"),
        ("top", "bottom"),
        ("left_top", "center"),
        ("left_bottom", "center"),
        ("top", "right_top"),
        ("bottom", "right_bottom"),
    ]
    dark_points = {
        "top": (0.00, 0.92),
        "left_top": (-0.88, 0.50),
        "left_bottom": (-0.88, -0.50),
        "bottom": (0.00, -0.92),
        "center": (0.00, 0.00),
        "right_top": (0.86, 0.50),
        "right_bottom": (0.86, -0.50),
    }
    green_points = {
        "center": (0.02, 0.00),
        "right_top": (0.86, 0.50),
        "right_bottom": (0.86, -0.50),
    }

    dark_objects: list[bpy.types.Object] = []
    green_objects: list[bpy.types.Object] = []
    symbols: list[bpy.types.Object] = []
    named: dict[str, bpy.types.Object] = {}

    for edge_index, (a, b) in enumerate(dark_edges, start=1):
        obj = create_connector(
            collection,
            f"{prefix}_DarkEdge_{edge_index:02d}_{a}_to_{b}",
            dark_points[a],
            dark_points[b],
            0.072,
            dark_y,
            dark_mat,
        )
        dark_objects.append(obj)
    for name, (x, z, radius) in dark_nodes.items():
        obj = create_node(collection, f"{prefix}_DarkNode_{name}", x, z, radius, dark_y - 0.01, dark_mat)
        dark_objects.append(obj)

    green_connectors = [
        ("center_to_right_top", "center", "right_top"),
        ("center_to_right_bottom", "center", "right_bottom"),
        ("right_top_to_right_bottom", "right_top", "right_bottom"),
    ]
    for name, a, b in green_connectors:
        obj = create_connector(
            collection,
            f"{prefix}_GreenEdge_{name}",
            green_points[a],
            green_points[b],
            0.092,
            green_y + 0.01,
            green_mat,
        )
        green_objects.append(obj)
        named[f"green_edge_{name}"] = obj
    green_specs = {
        "center": (0.02, 0.00, 0.335),
        "right_top": (0.86, 0.50, 0.305),
        "right_bottom": (0.86, -0.50, 0.285),
    }
    for name, (x, z, radius) in green_specs.items():
        obj = create_node(collection, f"{prefix}_GreenNode_{name}", x, z, radius, green_y - 0.02, green_mat)
        green_objects.append(obj)
        named[f"green_node_{name}"] = obj

    if symbol_variant == 1:
        parent_a = create_empty(collection, f"{prefix}_SymbolParent_plus", (1.25, -0.16, 0.72))
        parent_b = create_empty(collection, f"{prefix}_SymbolParent_ring", (1.35, -0.17, -0.08))
        parent_c = create_empty(collection, f"{prefix}_SymbolParent_dot", (0.58, -0.18, -0.78))
        symbols.extend([parent_a, parent_b, parent_c])
        symbols.extend(create_plus_symbol(collection, f"{prefix}_Symbol_plus", (0.0, 0.0, 0.0), 0.075, symbol_mat, parent_a))
        symbols.extend(create_torus_symbol(collection, f"{prefix}_Symbol_ring", (0.0, 0.0, 0.0), symbol_mat, parent_b))
        symbols.extend(create_dot_symbol(collection, f"{prefix}_Symbol_dot", (0.0, 0.0, 0.0), symbol_mat, parent_c))
    elif symbol_variant == 2:
        for index, loc in enumerate(((1.18, -0.16, 0.82), (1.39, -0.18, 0.24), (1.18, -0.18, -0.66), (0.55, -0.18, -0.78)), start=1):
            parent = create_empty(collection, f"{prefix}_SymbolParent_scatter_{index}", loc)
            symbols.append(parent)
            if index % 3 == 1:
                symbols.extend(create_chevron_symbol(collection, f"{prefix}_Symbol_chevron_{index}", (0.0, 0.0, 0.0), 0.07, symbol_mat, parent))
            elif index % 3 == 2:
                symbols.extend(create_plus_symbol(collection, f"{prefix}_Symbol_plus_{index}", (0.0, 0.0, 0.0), 0.065, symbol_mat, parent))
            else:
                symbols.extend(create_dot_symbol(collection, f"{prefix}_Symbol_dot_{index}", (0.0, 0.0, 0.0), symbol_mat, parent))
    else:
        for index, angle in enumerate((18, 88, 158, 228, 300), start=1):
            radians = math.radians(angle)
            loc = (1.08 * math.cos(radians), -0.2, 1.02 * math.sin(radians))
            parent = create_empty(collection, f"{prefix}_SymbolParent_orbit_{index}", loc)
            symbols.append(parent)
            if index in (1, 4):
                symbols.extend(create_torus_symbol(collection, f"{prefix}_Symbol_orbit_ring_{index}", (0.0, 0.0, 0.0), symbol_mat, parent))
            else:
                symbols.extend(create_dot_symbol(collection, f"{prefix}_Symbol_orbit_dot_{index}", (0.0, 0.0, 0.0), symbol_mat, parent))

    return {
        "dark": dark_objects,
        "green": green_objects,
        "symbols": symbols,
        "named": named,
        "all": dark_objects + green_objects + symbols,
    }


def animate_variant_01(parts: dict, collection: bpy.types.Collection, prefix: str) -> None:
    parent = create_empty(collection, f"{prefix}_GreenClusterParent", (0.0, 0.0, 0.0))
    for obj in parts["green"]:
        obj.parent = parent
    keyframe(parent, 1, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    keyframe(parent, 42, location=(0.16, -0.18, 0.10), rotation=(0.0, math.radians(-8), math.radians(3)), scale=(1.0, 1.0, 1.0))
    keyframe(parent, 84, location=(0.24, -0.27, -0.03), rotation=(0.0, math.radians(11), math.radians(-4)), scale=(1.0, 1.0, 1.0))
    keyframe(parent, 120, location=(0.20, -0.21, 0.13), rotation=(0.0, math.radians(-6), math.radians(2)), scale=(1.0, 1.0, 1.0))
    parts["all"].append(parent)
    for index, obj in enumerate(parts["symbols"]):
        if obj.type == "EMPTY":
            start = obj.location.copy()
            keyframe(obj, 1, location=(start.x - 0.20, start.y, start.z - 0.12), scale=(0.05, 0.05, 0.05))
            keyframe(obj, 45, location=(start.x, start.y - 0.05, start.z + 0.06), rotation=(0.0, 0.0, math.radians(40 + index * 18)), scale=(0.75, 0.75, 0.75))
            keyframe(obj, 85, location=(start.x + 0.08, start.y - 0.08, start.z - 0.04), rotation=(0.0, 0.0, math.radians(130 + index * 22)), scale=(1.0, 1.0, 1.0))
            keyframe(obj, 120, location=(start.x + 0.02, start.y - 0.03, start.z + 0.08), rotation=(0.0, 0.0, math.radians(210 + index * 17)), scale=(0.88, 0.88, 0.88))
    set_bezier_animation(parts["all"])


def animate_variant_02(parts: dict) -> None:
    targets = {
        "green_node_center": (-0.14, -0.26, 0.14),
        "green_node_right_top": (0.10, -0.30, 0.27),
        "green_node_right_bottom": (0.12, -0.28, -0.26),
        "green_edge_center_to_right_top": (0.08, -0.24, 0.20),
        "green_edge_center_to_right_bottom": (0.09, -0.24, -0.18),
        "green_edge_right_top_to_right_bottom": (0.14, -0.25, 0.02),
    }
    for key, obj in parts["named"].items():
        start = obj.location.copy()
        dx, dy, dz = targets.get(key, (0.0, 0.0, 0.0))
        keyframe(obj, 1, location=(start.x, start.y, start.z), scale=(1.0, 1.0, 1.0))
        keyframe(obj, 52, location=(start.x + dx * 0.72, start.y + dy * 0.72, start.z + dz * 0.72), rotation=(0.0, math.radians(8), math.radians(-5)), scale=(0.96, 0.96, 0.96))
        if "edge" in key:
            keyframe(obj, 120, location=(start.x + dx, start.y + dy, start.z + dz), rotation=(math.radians(0), math.radians(18), math.radians(16)), scale=(0.62, 0.62, 0.62))
        else:
            keyframe(obj, 120, location=(start.x + dx, start.y + dy, start.z + dz), rotation=(0.0, math.radians(-14), math.radians(7)), scale=(1.0, 1.0, 1.0))
    for index, obj in enumerate(parts["symbols"]):
        if obj.type == "EMPTY":
            start = obj.location.copy()
            keyframe(obj, 1, location=(0.86, -0.16, 0.03), scale=(0.02, 0.02, 0.02))
            keyframe(obj, 48, location=(start.x - 0.06, start.y - 0.03, start.z + 0.05), rotation=(0.0, 0.0, math.radians(index * 55)), scale=(0.85, 0.85, 0.85))
            keyframe(obj, 120, location=(start.x + 0.08 * math.sin(index), start.y - 0.08, start.z + 0.08 * math.cos(index)), rotation=(0.0, 0.0, math.radians(140 + index * 38)), scale=(1.0, 1.0, 1.0))
    set_bezier_animation(parts["all"])


def animate_variant_03(parts: dict) -> None:
    outward = {
        "green_node_center": (0.00, -0.33, 0.36),
        "green_node_right_top": (0.16, -0.36, 0.18),
        "green_node_right_bottom": (0.15, -0.36, -0.22),
        "green_edge_center_to_right_top": (0.10, -0.29, 0.22),
        "green_edge_center_to_right_bottom": (0.10, -0.29, -0.22),
        "green_edge_right_top_to_right_bottom": (0.18, -0.30, 0.00),
    }
    for key, obj in parts["named"].items():
        start = obj.location.copy()
        dx, dy, dz = outward.get(key, (0.0, 0.0, 0.0))
        keyframe(obj, 1, location=(start.x, start.y, start.z), scale=(1.0, 1.0, 1.0))
        keyframe(obj, 45, location=(start.x + dx, start.y + dy, start.z + dz), rotation=(0.0, math.radians(22), math.radians(10)), scale=(1.04, 1.04, 1.04))
        keyframe(obj, 82, location=(start.x + dx * 0.35, start.y + dy * 0.35, start.z + dz * 0.35), rotation=(0.0, math.radians(-10), math.radians(-6)), scale=(0.98, 0.98, 0.98))
        keyframe(obj, 120, location=(start.x, start.y, start.z), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    for index, obj in enumerate(parts["symbols"]):
        if obj.type == "EMPTY":
            start = obj.location.copy()
            keyframe(obj, 1, location=(0.30, -0.18, 0.02), scale=(0.01, 0.01, 0.01))
            keyframe(obj, 45, location=(start.x, start.y - 0.09, start.z), rotation=(0.0, 0.0, math.radians(index * 72)), scale=(1.0, 1.0, 1.0))
            keyframe(obj, 82, location=(start.x * 0.82, start.y - 0.04, start.z * 0.82), rotation=(0.0, 0.0, math.radians(180 + index * 64)), scale=(0.82, 0.82, 0.82))
            keyframe(obj, 120, location=(0.30, -0.18, 0.02), rotation=(0.0, 0.0, math.radians(360)), scale=(0.01, 0.01, 0.01))
    set_bezier_animation(parts["all"])


def setup_scene() -> bpy.types.Scene:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.fps = 24
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.2
    scene.view_settings.gamma = 1.0
    engine = safe_render_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 80
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 96),
            ("use_gtao", True),
            ("gtao_distance", 2.0),
            ("gtao_factor", 0.65),
            ("use_bloom", True),
            ("bloom_intensity", 0.035),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)
    world = scene.world or bpy.data.worlds.new("NetworkSymbolWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        background.inputs["Strength"].default_value = 0.38
    return scene


def create_reference_plane() -> bpy.types.Object | None:
    if not REFERENCE.is_file():
        return None
    mat = bpy.data.materials.new("NSV_ReferenceImage_not_exported")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(REFERENCE))
    if principled is not None:
        mat.node_tree.links.new(tex.outputs["Color"], principled.inputs["Base Color"])
        set_socket(principled, ("Alpha",), 0.35)
    mat.blend_method = "BLEND"
    bpy.ops.mesh.primitive_plane_add(size=2.45, location=(0.0, 0.42, 0.0), rotation=(math.radians(90), 0.0, 0.0))
    plane = bpy.context.object
    plane.name = "NSV_PrimaryReferencePlane_not_exported"
    plane.data.materials.append(mat)
    plane.hide_render = True
    plane.hide_set(True)
    return tag(plane, "reference_plane", False)


def setup_lighting() -> list[bpy.types.Object]:
    lights = []
    specs = [
        ("NSV_Key_not_exported", (-2.9, -4.7, 3.8), 230.0, 3.7),
        ("NSV_Fill_not_exported", (2.5, -3.3, 2.3), 70.0, 5.2),
        ("NSV_GreenRim_not_exported", (2.7, -1.8, 1.6), 45.0, 2.7),
    ]
    for name, location, power, size in specs:
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = power
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
        tag(obj, "studio_light", False)
        lights.append(obj)
    return lights


def setup_camera() -> bpy.types.Object:
    data = bpy.data.cameras.new("NSV_Camera_FRONT")
    camera = bpy.data.objects.new("NSV_Camera_FRONT", data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (0.0, -6.3, 0.0)
    camera.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.95
    bpy.context.scene.camera = camera
    return tag(camera, "review_camera", False)


def visible_objects_for(collection: bpy.types.Collection) -> set[str]:
    return {obj.name for obj in collection.all_objects}


def render_collection(collection: bpy.types.Collection, frame: int, path: Path) -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    shown = visible_objects_for(collection)
    previous = {obj.name: (obj.hide_render, obj.hide_get()) for obj in scene.objects}
    for obj in scene.objects:
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_render = False
            obj.hide_set(False)
        else:
            is_shown = obj.name in shown
            obj.hide_render = not is_shown
            obj.hide_set(not is_shown)
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)
    for obj in scene.objects:
        if obj.name in previous:
            obj.hide_render, hidden = previous[obj.name]
            obj.hide_set(hidden)
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "frame": frame}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def export_glb(collection: bpy.types.Collection, name: str) -> dict:
    bpy.ops.object.select_all(action="DESELECT")
    exportable = [
        obj
        for obj in collection.all_objects
        if obj.type not in {"CAMERA", "LIGHT"} and obj.get("abt_export", True)
    ]
    for obj in exportable:
        obj.select_set(True)
    mesh_objects = [obj for obj in exportable if obj.type == "MESH"]
    bpy.context.view_layer.objects.active = mesh_objects[0]
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
    return {
        "path": str(destination),
        "bytes": destination.stat().st_size if destination.is_file() else 0,
        "objects": [obj.name for obj in exportable],
        "triangles": triangle_count(mesh_objects),
    }


def validate_collection(collection: bpy.types.Collection, name: str, max_triangles: int = 60000) -> dict:
    exportable = [
        obj
        for obj in collection.all_objects
        if obj.type not in {"CAMERA", "LIGHT"} and obj.get("abt_export", True)
    ]
    mesh_objects = [obj for obj in exportable if obj.type == "MESH"]
    tri_count = triangle_count(mesh_objects)
    errors = []
    warnings = []
    if not mesh_objects:
        errors.append("No exportable mesh objects.")
    if tri_count > max_triangles:
        warnings.append(f"Triangle budget above target: {tri_count}/{max_triangles}.")
    for obj in exportable:
        if obj.type in {"CAMERA", "LIGHT"}:
            errors.append(f"Unexpected export object type: {obj.name} {obj.type}.")
        if any(abs(value) < 1e-6 for value in obj.scale):
            warnings.append(f"Object has near-zero scale in current scene state: {obj.name}.")
    return {
        "asset": name,
        "triangles": tri_count,
        "mesh_objects": len(mesh_objects),
        "animated_empty_objects": len([obj for obj in exportable if obj.type == "EMPTY"]),
        "errors": errors,
        "warnings": warnings,
    }


def build_scene() -> dict:
    checkpoint = None
    if bpy.context.scene.objects:
        checkpoint = CHECKPOINTS / f"{ASSET}_prechange_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

    scene = setup_scene()
    create_reference_plane()
    setup_lighting()
    setup_camera()

    dark_mat = material("NSV_Mat_dark_ink", (0.002, 0.020, 0.026, 1.0), roughness=0.58)
    green_mat = material(
        "NSV_Mat_signal_green",
        (0.000, 0.92, 0.040, 1.0),
        roughness=0.48,
        emission=(0.000, 0.65, 0.030, 1.0),
        emission_strength=0.18,
    )
    symbol_mat = material(
        "NSV_Mat_floating_green_symbols",
        (0.080, 1.000, 0.120, 1.0),
        roughness=0.42,
        emission=(0.050, 0.850, 0.080, 1.0),
        emission_strength=0.42,
    )

    variants = [
        ("network_symbol_variant01_orbit_split", "Variant01_OrbitSplit", 1),
        ("network_symbol_variant02_node_scatter", "Variant02_NodeScatter", 2),
        ("network_symbol_variant03_pulse_reconnect", "Variant03_PulseReconnect", 3),
    ]
    collections = []
    parts_by_name = {}
    for index, (export_name, collection_name, symbol_variant) in enumerate(variants, start=1):
        collection = create_collection(f"NSV_{collection_name}")
        parts = build_network(collection, f"NSV{index:02d}", dark_mat, green_mat, symbol_mat, symbol_variant)
        if index == 1:
            animate_variant_01(parts, collection, f"NSV{index:02d}")
        elif index == 2:
            animate_variant_02(parts)
        else:
            animate_variant_03(parts)
        collections.append((export_name, collection))
        parts_by_name[export_name] = parts

    scene_graph = {
        "schema_version": "network-symbol-detach-v1",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "primary_reference": str(REFERENCE),
        "mode": "icon/hero object",
        "reference_breakdown": {
            "silhouette": "flat network/chemistry-like graph icon on black square crop",
            "palette": {
                "background": "#000000",
                "dark_network": "#001018-#001a20",
                "green_cluster": "#00e80a",
            },
            "occlusion_order": [
                "dark network sits behind",
                "green triangular subgraph covers center and right side",
                "floating green symbols detach in front of the green cluster",
            ],
            "camera": "orthographic front for icon match",
            "material": "smooth toy-like PBR, high roughness, subtle signal-green emission",
        },
        "animation_variants": [
            {
                "name": "variant01_orbit_split",
                "idea": "Green subnet stays connected, slides out of the dark graph and hovers with small symbols orbiting nearby.",
            },
            {
                "name": "variant02_node_scatter",
                "idea": "Each green node detaches as a separate semantic piece; link capsules shrink and float as data fragments.",
            },
            {
                "name": "variant03_pulse_reconnect",
                "idea": "Green symbols burst outward, circle the network, then magnetically reconnect to the original graph.",
            },
        ],
        "expected_contacts": {
            "frame_001": "green nodes and links intentionally overlap like the reference",
            "frames_060_120": "green parts are intentionally floating; reported as intended, not structural failure",
        },
        "acceptance_criteria": [
            "front frame reads as the supplied reference: dark graph plus bright green foreground subgraph",
            "green semantic parts are separate objects with keyframed transforms",
            "three animation variants are exported as GLB with animations",
            "reference plane, camera, and lights are not part of GLB exports",
            "each variant remains under 60k triangles",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    render_results = {}
    for export_name, collection in collections:
        render_results[export_name] = []
        for frame in FRAMES:
            render_results[export_name].append(
                render_collection(collection, frame, RENDERS / f"{export_name}_frame_{frame:03d}.png")
            )

    validation = {}
    exports = {}
    for export_name, collection in collections:
        validation[export_name] = validate_collection(collection, export_name)
        if validation[export_name]["errors"]:
            continue
        exports[export_name] = export_glb(collection, export_name)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "scene": scene.name,
        "checkpoint": str(checkpoint) if checkpoint else None,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "renders": render_results,
        "validation": validation,
        "exports": exports,
        "warnings": [
            "Blender MCP socket was unavailable, so this production pass ran in Blender background mode.",
            "Floating green components are intentional animation states, not accidental gaps.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    report = build_scene()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
