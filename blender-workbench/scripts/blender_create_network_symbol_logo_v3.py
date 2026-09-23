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

ASSET = "network_symbol_logo_v3"
SCENE_NAME = "NetworkSymbolLogoV3"
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


def material(
    name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = base_color
    mat.use_nodes = True
    principled = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        set_socket(principled, ("Base Color",), base_color)
        set_socket(principled, ("Metallic",), 0.0)
        set_socket(principled, ("Roughness",), roughness)
        set_socket(principled, ("Specular IOR Level", "Specular"), 0.35)
        set_socket(principled, ("Coat Weight", "Clearcoat", "Coat"), 0.025)
        set_socket(principled, ("Coat Roughness",), 0.55)
        if emission is not None:
            set_socket(principled, ("Emission Color", "Emission"), emission)
            set_socket(principled, ("Emission Strength", "Emission Weight"), emission_strength)
    return mat


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def link_to(collection: bpy.types.Collection, obj: bpy.types.Object) -> bpy.types.Object:
    if collection.objects.get(obj.name) is None:
        collection.objects.link(obj)
    for coll in list(obj.users_collection):
        if coll != collection:
            coll.objects.unlink(obj)
    return obj


def create_empty(collection: bpy.types.Collection, name: str) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.08
    collection.objects.link(empty)
    return tag(empty, "animation_parent", True)


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def apply_soft_edges(obj: bpy.types.Object, bevel: float = 0.01, segments: int = 2) -> None:
    bevel_mod = obj.modifiers.new(f"{obj.name}_soft_bevel", "BEVEL")
    bevel_mod.width = bevel
    bevel_mod.segments = segments
    bevel_mod.affect = "EDGES"
    normal_mod = obj.modifiers.new(f"{obj.name}_weighted_normals", "WEIGHTED_NORMAL")
    active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
        bpy.ops.object.modifier_apply(modifier=normal_mod.name)
    finally:
        obj.select_set(False)
        bpy.context.view_layer.objects.active = active


def shade_smooth(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def make_extruded_polygon(
    collection: bpy.types.Collection,
    name: str,
    outline: list[tuple[float, float]],
    y: float,
    depth: float,
    mat: bpy.types.Material,
    role: str,
) -> bpy.types.Object:
    half = depth * 0.5
    verts = [(x, y - half, z) for x, z in outline] + [(x, y + half, z) for x, z in outline]
    n = len(outline)
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple(range(n, n * 2)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    apply_soft_edges(obj, bevel=0.012 if role != "particle" else 0.004, segments=2)
    return tag(obj, role, True)


def capsule_outline(a: tuple[float, float], b: tuple[float, float], radius: float, cap_segments: int = 20) -> list[tuple[float, float]]:
    ax, az = a
    bx, bz = b
    dx = bx - ax
    dz = bz - az
    length = math.hypot(dx, dz)
    if length < 1e-6:
        return circle_outline(a, radius, cap_segments * 2)
    ux, uz = dx / length, dz / length
    px, pz = -uz, ux
    points: list[tuple[float, float]] = []
    for i in range(cap_segments + 1):
        theta = -math.pi * 0.5 + math.pi * (i / cap_segments)
        lx = math.cos(theta) * radius
        lz = math.sin(theta) * radius
        points.append((bx + ux * lx + px * lz, bz + uz * lx + pz * lz))
    for i in range(cap_segments + 1):
        theta = math.pi * 0.5 + math.pi * (i / cap_segments)
        lx = math.cos(theta) * radius
        lz = math.sin(theta) * radius
        points.append((ax + ux * lx + px * lz, az + uz * lx + pz * lz))
    return points


def circle_outline(center: tuple[float, float], radius: float, segments: int = 56) -> list[tuple[float, float]]:
    cx, cz = center
    return [
        (cx + math.cos((math.tau * i) / segments) * radius, cz + math.sin((math.tau * i) / segments) * radius)
        for i in range(segments)
    ]


def create_capsule(
    collection: bpy.types.Collection,
    name: str,
    a: tuple[float, float],
    b: tuple[float, float],
    radius: float,
    y: float,
    depth: float,
    mat: bpy.types.Material,
    role: str,
) -> bpy.types.Object:
    return make_extruded_polygon(collection, name, capsule_outline(a, b, radius), y, depth, mat, role)


def create_disc(
    collection: bpy.types.Collection,
    name: str,
    center: tuple[float, float],
    radius: float,
    y: float,
    depth: float,
    mat: bpy.types.Material,
    role: str,
) -> bpy.types.Object:
    if role in {"dark_node", "green_node", "particle"}:
        segments = 48 if role != "particle" else 28
        rings = 24 if role != "particle" else 14
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=segments,
            ring_count=rings,
            radius=radius,
            location=(center[0], y, center[1]),
        )
        obj = bpy.context.object
        obj.name = name
        obj.data.name = f"{name}_Mesh"
        obj.data.materials.append(mat)
        shade_smooth(obj)
        link_to(collection, obj)
        return tag(obj, role, True)
    return make_extruded_polygon(collection, name, circle_outline(center, radius), y, depth, mat, role)


def create_dash(
    collection: bpy.types.Collection,
    name: str,
    center: tuple[float, float],
    length: float,
    radius: float,
    angle: float,
    y: float,
    depth: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    dx = math.cos(angle) * length * 0.5
    dz = math.sin(angle) * length * 0.5
    return create_capsule(collection, name, (center[0] - dx, center[1] - dz), (center[0] + dx, center[1] + dz), radius, y, depth, mat, "particle")


POINTS = {
    "top": (0.0, 0.92),
    "left_top": (-0.86, 0.48),
    "left_bottom": (-0.86, -0.48),
    "bottom": (0.0, -0.92),
    "center": (0.02, 0.0),
    "right_top": (0.86, 0.48),
    "right_bottom": (0.86, -0.48),
}


def build_logo(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    dark_y = 0.018
    green_y = -0.055
    depth = 0.075
    dark: list[bpy.types.Object] = []
    green: list[bpy.types.Object] = []
    named: dict[str, bpy.types.Object] = {}

    dark_edges = (
        ("top", "left_top"),
        ("top", "right_top"),
        ("left_top", "left_bottom"),
        ("left_top", "center"),
        ("left_bottom", "center"),
        ("left_bottom", "bottom"),
        ("top", "bottom"),
        ("bottom", "right_bottom"),
    )
    for index, (a, b) in enumerate(dark_edges, start=1):
        dark.append(
            create_capsule(
                collection,
                f"{prefix}_DarkEdge_{index:02d}_{a}_to_{b}",
                POINTS[a],
                POINTS[b],
                0.066,
                dark_y,
                depth,
                mats["dark"],
                "dark_edge",
            )
        )
    for name, radius in (("top", 0.245), ("left_top", 0.245), ("left_bottom", 0.245), ("bottom", 0.245)):
        dark.append(create_disc(collection, f"{prefix}_DarkNode_{name}", POINTS[name], radius, dark_y - 0.004, depth * 1.05, mats["dark"], "dark_node"))

    green_edges = (
        ("center_to_right_top", "center", "right_top"),
        ("center_to_right_bottom", "center", "right_bottom"),
        ("right_top_to_right_bottom", "right_top", "right_bottom"),
    )
    for edge_name, a, b in green_edges:
        obj = create_capsule(collection, f"{prefix}_GreenEdge_{edge_name}", POINTS[a], POINTS[b], 0.078, green_y, depth, mats["green"], "green_edge")
        green.append(obj)
        named[f"edge_{edge_name}"] = obj
    for name, radius in (("center", 0.345), ("right_top", 0.305), ("right_bottom", 0.292)):
        obj = create_disc(collection, f"{prefix}_GreenNode_{name}", POINTS[name], radius, green_y - 0.008, depth * 1.08, mats["green"], "green_node")
        green.append(obj)
        named[f"node_{name}"] = obj
    return {"dark": dark, "green": green, "named": named, "all": dark + green}


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


def smooth_keys(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        fcurves = getattr(action, "fcurves", None)
        if fcurves is None:
            continue
        for fcurve in fcurves:
            for point in fcurve.keyframe_points:
                point.interpolation = "BEZIER"


def add_particles(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    particles = [
        create_disc(collection, f"{prefix}_SignalDot_01", (1.32, 0.62), 0.030, -0.09, 0.045, mats["green"], "particle"),
        create_disc(collection, f"{prefix}_SignalDot_02", (1.27, -0.42), 0.022, -0.09, 0.045, mats["green"], "particle"),
        create_dash(collection, f"{prefix}_SignalDash_01", (1.14, 0.18), 0.105, 0.012, math.radians(4), -0.09, 0.04, mats["green"]),
        create_dash(collection, f"{prefix}_SignalDash_02", (1.06, -0.70), 0.100, 0.012, math.radians(86), -0.09, 0.04, mats["green"]),
    ]
    return particles


def animate_clean_detach(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_logo(collection, prefix, mats)
    root = create_empty(collection, f"{prefix}_GreenLayer_ROOT")
    for obj in parts["green"]:
        parent_keep_world(obj, root)
    particles = add_particles(collection, prefix, mats)
    for index, particle in enumerate(particles, start=1):
        key(particle, 1, scale=(0.01, 0.01, 0.01))
        key(particle, 58, scale=(0.55, 0.55, 0.55))
        key(particle, 132, scale=(0.92, 0.92, 0.92), loc=(particle.location.x + 0.02 * index, particle.location.y - 0.045, particle.location.z + 0.02 * math.sin(index)))

    key(root, 1, loc=(0, 0, 0), rot=(0, 0, 0))
    key(root, 48, loc=(0.10, -0.05, 0.02), rot=(0, 0, math.radians(1.0)))
    key(root, 96, loc=(0.32, -0.16, 0.04), rot=(0, math.radians(-3.0), math.radians(1.2)))
    key(root, 132, loc=(0.28, -0.13, 0.08), rot=(0, math.radians(-2.0), math.radians(-0.8)))
    animated = [root] + particles
    smooth_keys(animated)
    return {"objects": parts["all"] + [root] + particles, "animated": animated}


def animate_assemble(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_logo(collection, prefix, mats)
    animated = []
    for name, obj in parts["named"].items():
        final = obj.location.copy()
        if name.startswith("node_"):
            offset = {
                "node_center": (0.25, -0.12, 0.35),
                "node_right_top": (0.24, -0.12, 0.10),
                "node_right_bottom": (0.24, -0.12, -0.10),
            }.get(name, (0, 0, 0))
            key(obj, 1, loc=(final.x + offset[0], final.y + offset[1], final.z + offset[2]), scale=(0.82, 0.82, 0.82))
            key(obj, 48, loc=(final.x + offset[0] * 0.45, final.y + offset[1] * 0.5, final.z + offset[2] * 0.45), scale=(0.94, 0.94, 0.94))
            key(obj, 96, loc=(final.x, final.y, final.z), scale=(1, 1, 1))
            key(obj, 132, loc=(final.x, final.y, final.z), scale=(1, 1, 1))
        else:
            key(obj, 1, loc=(final.x, final.y, final.z), scale=(0.01, 0.01, 0.01))
            key(obj, 60, loc=(final.x, final.y, final.z), scale=(0.15, 0.15, 0.15))
            key(obj, 96, loc=(final.x, final.y, final.z), scale=(1, 1, 1))
            key(obj, 132, loc=(final.x, final.y, final.z), scale=(1, 1, 1))
        animated.append(obj)
    particles = add_particles(collection, prefix, mats)
    for index, particle in enumerate(particles, start=1):
        origin = particle.location.copy()
        key(particle, 1, scale=(0.85, 0.85, 0.85))
        key(particle, 72, loc=(0.98 + 0.04 * index, -0.10, 0.18 - 0.10 * index), scale=(0.35, 0.35, 0.35))
        key(particle, 132, loc=(0.95, -0.08, 0.0), scale=(0.01, 0.01, 0.01))
        animated.append(particle)
    smooth_keys(animated)
    return {"objects": parts["all"] + particles, "animated": animated}


def animate_reconnect(collection: bpy.types.Collection, prefix: str, mats: dict[str, bpy.types.Material]) -> dict:
    parts = build_logo(collection, prefix, mats)
    root = create_empty(collection, f"{prefix}_GreenLayerLoop_ROOT")
    for obj in parts["green"]:
        parent_keep_world(obj, root)
    particles = add_particles(collection, prefix, mats)
    key(root, 1, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1))
    key(root, 46, loc=(0.24, -0.18, 0.10), rot=(0, math.radians(-4), math.radians(2)), scale=(1.02, 1.02, 1.02))
    key(root, 88, loc=(0.08, -0.06, 0.02), rot=(0, math.radians(2), math.radians(-1)), scale=(0.99, 0.99, 0.99))
    key(root, 132, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1))
    for index, particle in enumerate(particles, start=1):
        origin = particle.location.copy()
        key(particle, 1, loc=(0.88, -0.08, 0.0), scale=(0.01, 0.01, 0.01))
        key(particle, 48, loc=(origin.x, origin.y - 0.04, origin.z), scale=(0.9, 0.9, 0.9))
        key(particle, 100, loc=(0.96 + 0.03 * index, -0.10, 0.08 - 0.06 * index), scale=(0.35, 0.35, 0.35))
        key(particle, 132, loc=(0.88, -0.08, 0.0), scale=(0.01, 0.01, 0.01))
    animated = [root] + particles
    smooth_keys(animated)
    return {"objects": parts["all"] + [root] + particles, "animated": animated}


def safe_engine(scene: bpy.types.Scene) -> str:
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
    scene.view_settings.exposure = -0.1
    scene.view_settings.gamma = 1.0
    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 80
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 1.8),
            ("gtao_factor", 0.5),
            ("use_bloom", True),
            ("bloom_intensity", 0.025),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)
    world = scene.world or bpy.data.worlds.new("NetworkSymbolLogoV3World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0, 0, 0, 1)
        background.inputs["Strength"].default_value = 0.18
    return scene


def setup_camera() -> bpy.types.Object:
    camera_data = bpy.data.cameras.new("NSL3_Camera_FRONT")
    camera = bpy.data.objects.new("NSL3_Camera_FRONT", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (0.0, -6.0, 0.0)
    camera.rotation_euler = (Vector((0, 0, 0)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.08
    bpy.context.scene.camera = camera
    return tag(camera, "review_camera", False)


def setup_lights() -> None:
    specs = [
        ("NSL3_Key_not_exported", (-2.2, -4.2, 3.0), 90.0, 4.0),
        ("NSL3_Fill_not_exported", (2.4, -4.0, 1.5), 24.0, 5.5),
        ("NSL3_GreenEdge_not_exported", (2.5, -2.5, 1.0), 18.0, 2.7),
    ]
    for name, loc, power, size in specs:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = power
        light.size = size
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        tag(obj, "studio_light", False)


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    names = {obj.name for obj in collection.all_objects}
    previous = {}
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_render, obj.hide_get())
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_render = False
            obj.hide_set(False)
        else:
            visible = obj.name in names
            obj.hide_render = not visible
            obj.hide_set(not visible)
    return previous


def restore(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_render, hide_view = previous[obj.name]
            obj.hide_set(hide_view)


def render(collection: bpy.types.Collection, frame: int, path: Path) -> dict:
    bpy.context.scene.frame_set(frame)
    previous = hide_except(collection)
    try:
        bpy.context.scene.render.filepath = str(path)
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore(previous)
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "frame": frame}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def validate(collection: bpy.types.Collection, name: str, budget: int = 35000) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    tris = triangle_count(meshes)
    warnings = []
    errors = []
    if not meshes:
        errors.append("No exportable mesh objects.")
    if tris > budget:
        warnings.append(f"Triangle budget above logo target: {tris}/{budget}.")
    return {"asset": name, "triangles": tris, "mesh_objects": len(meshes), "animated_objects": len([obj for obj in exportable if obj.animation_data]), "errors": errors, "warnings": warnings}


def export(collection: bpy.types.Collection, name: str) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    path = EXPORTS / f"{name}.glb"
    props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {"filepath": str(path), "export_format": "GLB", "use_selection": True}
    for option, value in (
        ("export_animations", True),
        ("export_frame_range", True),
        ("export_force_sampling", True),
        ("export_nla_strips", True),
        ("export_optimize_animation_size", True),
        ("export_apply", True),
    ):
        if option in props:
            kwargs[option] = value
    bpy.ops.export_scene.gltf(**kwargs)
    public_path = PUBLIC_MODELS / path.name
    shutil.copy2(path, public_path)
    return {"path": str(path), "public_path": str(public_path), "bytes": path.stat().st_size if path.is_file() else 0, "triangles": triangle_count(meshes)}


def glb_check(paths: Iterable[Path]) -> list[dict]:
    out = []
    for path in paths:
        data = path.read_bytes()
        magic, _, _ = struct.unpack_from("<4sII", data, 0)
        if magic != b"glTF":
            out.append({"file": path.name, "error": "not_glb"})
            continue
        chunk_len, _ = struct.unpack_from("<II", data, 12)
        gltf = json.loads(data[20 : 20 + chunk_len].decode("utf-8"))
        out.append({"file": path.name, "bytes": path.stat().st_size, "animations": len(gltf.get("animations", [])), "nodes": len(gltf.get("nodes", [])), "meshes": len(gltf.get("meshes", []))})
    return out


def build_scene() -> dict:
    scene = setup_scene()
    setup_camera()
    setup_lights()
    mats = {
        "dark": material("NSL3_DarkNearBlack", (0.004, 0.030, 0.035, 1), 0.52, emission=(0.0, 0.026, 0.030, 1), emission_strength=0.04),
        "green": material("NSL3_ReferenceGreen", (0.0, 1.0, 0.055, 1), 0.44, emission=(0.0, 0.95, 0.06, 1), emission_strength=0.42),
    }
    specs = [
        ("network_symbol_logo_v3_clean_detach", "NSL3_CleanDetach", animate_clean_detach),
        ("network_symbol_logo_v3_assemble", "NSL3_Assemble", animate_assemble),
        ("network_symbol_logo_v3_reconnect", "NSL3_Reconnect", animate_reconnect),
    ]
    collections = []
    for index, (export_name, collection_name, animator) in enumerate(specs, start=1):
        collection = create_collection(collection_name)
        animator(collection, f"NSL3_{index:02d}", mats)
        collections.append((export_name, collection))

    scene_graph = {
        "asset": ASSET,
        "scene": scene.name,
        "reference": str(REFERENCE),
        "visual_intent": "Front-facing 2.5D version of the supplied logo. No perspective molecule, no rings, no random rods.",
        "animation_variants": [
            "clean_detach: whole green layer detaches and hovers as one readable module",
            "assemble: green nodes glide into place and links draw in locally",
            "reconnect: green layer pulses out and returns cleanly",
        ],
        "acceptance": [
            "Frame 001 must read like the original flat mark.",
            "Green parts must stay graphic and controlled during motion.",
            "Preview must be checked on black background.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    renders = {}
    validations = {}
    exports = {}
    glbs = []
    for export_name, collection in collections:
        renders[export_name] = [render(collection, frame, RENDERS / f"{export_name}_frame_{frame:03d}.png") for frame in FRAMES]
        validations[export_name] = validate(collection, export_name)
        if not validations[export_name]["errors"]:
            exports[export_name] = export(collection, export_name)
            glbs.append(Path(exports[export_name]["path"]))

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    checks = glb_check(glbs)
    write_json(REPORTS / f"{ASSET}_glb_animation_check.json", {"checks": checks})

    report = {
        "asset": ASSET,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "renders": renders,
        "validation": validations,
        "exports": exports,
        "glb_animation_check": checks,
        "warnings": ["This v3 intentionally replaces v1/v2 perspective molecule attempts with a flat 2.5D logo-layer construction."],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(build_scene(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
