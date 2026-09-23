from __future__ import annotations

import json
import math
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

import bpy
from mathutils import Vector


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
WORKBENCH = REPO / "blender-workbench"
SHAPE_TOOLS = WORKBENCH / "shape-reconstruction-upgrade" / "04_blender_tools"
RESEARCH_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"

for directory in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    directory.mkdir(parents=True, exist_ok=True)

if str(SHAPE_TOOLS) not in sys.path:
    sys.path.insert(0, str(SHAPE_TOOLS))
if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import capability_probe
import scene_qa
import shape_tools as st


ASSET = "low_poly_gas_station_v2"
SCENE_NAME = "LowPolyGasStation_GlowingSign"
COLLECTION_NAME = "ABT_LOW_POLY_GAS_STATION_GLOW"
WIDTH = 1200
HEIGHT = 900
TRIANGLE_BUDGET = 80_000


def ensure_allowed_path(path: Path) -> Path:
    resolved = path.resolve()
    allowed = [REPO.resolve()]
    if not any(resolved == root or root in resolved.parents for root in allowed):
        raise RuntimeError(f"Refusing to write outside allowlisted roots: {resolved}")
    return resolved


def write_json(path: Path, data: dict) -> None:
    target = ensure_allowed_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def safe_set_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def checkpoint_current_scene() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = CHECKPOINTS / f"{ASSET}_prechange_{timestamp}.blend"
    result = {"status": "skipped", "path": str(destination)}
    if bpy.context.scene.objects:
        bpy.ops.wm.save_as_mainfile(filepath=str(ensure_allowed_path(destination)))
        result["status"] = "saved"
        result["bytes"] = destination.stat().st_size
    return result


def create_clean_scene() -> bpy.types.Scene:
    existing = bpy.data.scenes.get(SCENE_NAME)
    if existing is None:
        scene = bpy.data.scenes.new(SCENE_NAME)
    else:
        scene = existing
        for obj in list(scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for child in list(scene.collection.children):
            scene.collection.children.unlink(child)
    bpy.context.window.scene = scene

    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.05
    scene.view_settings.gamma = 1.0

    engine = safe_set_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 96),
            ("use_gtao", True),
            ("gtao_distance", 3.0),
            ("gtao_factor", 0.55),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("LPGS_World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.86, 0.91, 0.96, 1.0)
        background.inputs["Strength"].default_value = 0.7
    return scene


def material(
    name: str,
    color: Sequence[float],
    roughness: float = 0.62,
    metallic: float = 0.0,
) -> bpy.types.Material:
    return st.create_principled_material(
        name,
        base_color=color,
        roughness=roughness,
        metallic=metallic,
    )


def emissive_material(
    name: str,
    color: Sequence[float],
    *,
    strength: float,
    roughness: float = 0.36,
) -> bpy.types.Material:
    mat = material(name, color, roughness=roughness, metallic=0.0)
    principled = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        for socket_name in ("Emission Color", "Emission"):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = tuple(color)
                break
        for socket_name in ("Emission Strength", "Emission Weight"):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = float(strength)
                break
    mat["lpgs_emissive"] = True
    mat["lpgs_emissive_strength"] = float(strength)
    return mat


def move_and_tag(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
    mat: bpy.types.Material | None,
    export: bool = True,
    role: str = "asset_part",
) -> bpy.types.Object:
    st.move_to_collection(obj, collection)
    if mat is not None:
        st.assign_material(obj, mat)
    st.tag_object(obj, role=role, export=export)
    return obj


def create_box(
    name: str,
    location: Sequence[float],
    dimensions: Sequence[float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    bevel: float = 0.0,
    bevel_segments: int = 1,
    export: bool = True,
    role: str = "asset_part",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=tuple(location))
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(float(value) / 2.0 for value in dimensions)
    st.apply_object_transform(obj, scale=True)
    if bevel > 0.0:
        modifier = obj.modifiers.new(f"{name}_Bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = max(1, bevel_segments)
        modifier.use_clamp_overlap = True
        if hasattr(modifier, "harden_normals"):
            modifier.harden_normals = True
        st.apply_modifier(obj, modifier.name)
    return move_and_tag(obj, collection, mat, export=export, role=role)


def create_cylinder(
    name: str,
    location: Sequence[float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    vertices: int = 12,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    export: bool = True,
    role: str = "asset_part",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=tuple(location),
        rotation=tuple(rotation),
    )
    obj = bpy.context.object
    obj.name = name
    st.apply_object_transform(obj, rotation=True, scale=True)
    return move_and_tag(obj, collection, mat, export=export, role=role)


def create_cone(
    name: str,
    location: Sequence[float],
    radius1: float,
    radius2: float,
    depth: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    vertices: int = 16,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=tuple(location),
    )
    obj = bpy.context.object
    obj.name = name
    st.apply_object_transform(obj, scale=True)
    return move_and_tag(obj, collection, mat, export=export)


def create_torus(
    name: str,
    location: Sequence[float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    major_radius: float = 0.32,
    minor_radius: float = 0.08,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_segments=18,
        minor_segments=6,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=tuple(location),
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    st.apply_object_transform(obj, rotation=True, scale=True)
    return move_and_tag(obj, collection, mat, export=export)


def create_bulb(
    name: str,
    location: Sequence[float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    radius: float = 0.045,
) -> bpy.types.Object:
    return st.create_ellipsoid(
        name=name,
        location=location,
        scale=(radius, radius, radius),
        radius=1.0,
        segments=14,
        rings=8,
        collection=collection,
        material=mat,
        role="glow_bulb",
        export=True,
    )


def create_roadside_bulbs(
    collection: bpy.types.Collection,
    bulb_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    bulbs: list[bpy.types.Object] = []
    x_values = [-4.30, -4.04, -3.78, -3.52, -3.26, -3.00, -2.86]
    for index, x in enumerate(x_values):
        bulbs.append(create_bulb(f"LPGS_RoadsideBulb_Top_{index:02d}", (x, -0.018, 2.80), bulb_mat, collection))
        bulbs.append(create_bulb(f"LPGS_RoadsideBulb_Bottom_{index:02d}", (x, -0.018, 2.05), bulb_mat, collection))
    for index, z in enumerate([2.20, 2.38, 2.56, 2.72]):
        bulbs.append(create_bulb(f"LPGS_RoadsideBulb_Left_{index:02d}", (-4.37, -0.018, z), bulb_mat, collection))
        bulbs.append(create_bulb(f"LPGS_RoadsideBulb_Right_{index:02d}", (-2.83, -0.018, z), bulb_mat, collection))
    return bulbs


def create_canopy_bulbs(
    collection: bpy.types.Collection,
    bulb_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    bulbs: list[bpy.types.Object] = []
    for index, x in enumerate([-1.36, -0.98, -0.60, -0.22, 0.22, 0.60, 0.98, 1.36]):
        bulbs.append(create_bulb(f"LPGS_CanopyBulb_Lower_{index:02d}", (x, -3.61, 2.50), bulb_mat, collection, radius=0.040))
    for index, x in enumerate([-1.12, -0.72, -0.32, 0.32, 0.72, 1.12]):
        bulbs.append(create_bulb(f"LPGS_CanopyBulb_Upper_{index:02d}", (x, -3.61, 2.99), bulb_mat, collection, radius=0.036))
    return bulbs


def create_tri_prism(
    name: str,
    points_xz: Sequence[Sequence[float]],
    y_center: float,
    thickness: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    export: bool = True,
) -> bpy.types.Object:
    if len(points_xz) != 3:
        raise ValueError("Tri prism needs exactly three X/Z points.")
    y_front = y_center - thickness / 2.0
    y_back = y_center + thickness / 2.0
    verts = [(float(x), y_front, float(z)) for x, z in points_xz]
    verts += [(float(x), y_back, float(z)) for x, z in points_xz]
    faces = [
        (0, 1, 2),
        (5, 4, 3),
        (0, 3, 4, 1),
        (1, 4, 5, 2),
        (2, 5, 3, 0),
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return move_and_tag(obj, collection, mat, export=export)


def create_text_mesh(
    name: str,
    text: str,
    location: Sequence[float],
    size: float,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    *,
    extrude: float = 0.025,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.object.text_add(
        location=tuple(location),
        rotation=(math.radians(90.0), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.resolution_u = 1
    st.assign_material(obj, mat)
    st.convert_to_mesh(obj)
    obj = bpy.context.object
    obj.name = name
    return move_and_tag(obj, collection, mat, export=export)


def create_hose(
    collection: bpy.types.Collection,
    rubber_mat: bpy.types.Material,
) -> list[bpy.types.Object]:
    parts = st.create_bezier_tube(
        name="LPGS_PumpHose",
        points=[
            (0.34, -2.54, 1.04),
            (0.82, -2.80, 0.72),
            (0.72, -2.36, 0.42),
            (0.47, -2.08, 0.70),
        ],
        radii=(0.035, 0.045, 0.042, 0.032),
        bevel_resolution=2,
        curve_resolution=14,
        collection=collection,
        material=rubber_mat,
        add_round_endcaps=True,
        export=True,
    )
    converted: list[bpy.types.Object] = []
    for part in parts:
        if part.type != "MESH":
            part = st.convert_to_mesh(part)
            part.name = part.name.replace("_Curve", "")
        st.tag_object(part, role="hose_part", export=True)
        converted.append(part)
    return converted


def create_lighting() -> None:
    def add_area(name: str, location: Sequence[float], power: float, size: float) -> None:
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = power
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
        target = Vector((0.0, -0.7, 1.1))
        direction = target - Vector(location)
        obj.location = tuple(location)
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        st.tag_object(obj, role="studio_light", export=False)

    add_area("LPGS_KeyLight_not_exported", (-4.5, -5.0, 7.2), 360.0, 6.0)
    add_area("LPGS_FillLight_not_exported", (4.8, -4.2, 3.0), 72.0, 7.0)
    add_area("LPGS_RimLight_not_exported", (3.5, 3.5, 4.5), 90.0, 5.0)

    for name, location, power, color in (
        ("LPGS_RoadsideGlow_not_exported", (-3.58, -0.55, 2.42), 120.0, (1.0, 0.74, 0.30)),
        ("LPGS_CanopyGlow_not_exported", (0.0, -4.0, 2.70), 165.0, (1.0, 0.68, 0.24)),
    ):
        data = bpy.data.lights.new(name, type="POINT")
        data.energy = power
        data.color = color
        data.shadow_soft_size = 2.0
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        st.tag_object(obj, role="preview_glow_light", export=False)


def point_camera(camera: bpy.types.Object, location: Sequence[float], target: Sequence[float]) -> None:
    camera.location = tuple(location)
    direction = Vector(target) - Vector(location)
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera(name: str, view: str) -> dict:
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None or camera.type != "CAMERA":
        camera = bpy.data.objects.new(name, cam_data)
        scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 8.0
    target = (-0.18, -0.8, 1.35)
    if view == "FRONT":
        point_camera(camera, (-0.18, -10.5, 3.1), target)
    elif view == "FRONT_3Q":
        camera.data.ortho_scale = 8.2
        point_camera(camera, (6.3, -8.8, 4.0), target)
    elif view == "SIDE":
        camera.data.ortho_scale = 8.0
        point_camera(camera, (9.4, -0.5, 3.2), target)
    else:
        raise ValueError(f"Unknown view: {view}")
    scene.camera = camera
    st.tag_object(camera, role="camera", export=False)
    return {
        "camera": camera.name,
        "view": view,
        "location": list(camera.location),
        "ortho_scale": float(camera.data.ortho_scale),
    }


def render_preview(path: Path, visible: Sequence[bpy.types.Object], view: str) -> dict:
    setup_camera(f"LPGS_CAM_{view}", view)
    scene = bpy.context.scene
    target_names = {obj.name for obj in visible}
    previous_render = {obj.name: bool(obj.hide_render) for obj in scene.objects}
    previous_view = {obj.name: bool(obj.hide_get()) for obj in scene.objects}
    try:
        for obj in scene.objects:
            if obj.type in {"CAMERA", "LIGHT"}:
                obj.hide_render = False
                obj.hide_set(False)
            else:
                shown = obj.name in target_names
                obj.hide_render = not shown
                obj.hide_set(not shown)
        scene.render.filepath = str(ensure_allowed_path(path))
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        for obj in scene.objects:
            if obj.name in previous_render:
                obj.hide_render = previous_render[obj.name]
            if obj.name in previous_view:
                obj.hide_set(previous_view[obj.name])
    return {
        "path": str(path),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "view": view,
        "object_count": len(target_names),
    }


def build_geometry(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    mats = {
        "asphalt": material("LPGS_MAT_Asphalt", (0.12, 0.13, 0.14, 1.0), 0.78),
        "concrete": material("LPGS_MAT_Concrete", (0.58, 0.61, 0.60, 1.0), 0.70),
        "wall": material("LPGS_MAT_WallWarmGray", (0.74, 0.72, 0.67, 1.0), 0.62),
        "roof": material("LPGS_MAT_CharcoalRoof", (0.18, 0.19, 0.20, 1.0), 0.65),
        "brand": material("LPGS_MAT_BrandRed", (0.86, 0.14, 0.09, 1.0), 0.54),
        "trim": material("LPGS_MAT_OrangeTrim", (1.0, 0.55, 0.13, 1.0), 0.58),
        "glass": material("LPGS_MAT_BlueGlass", (0.08, 0.18, 0.26, 1.0), 0.38),
        "metal": material("LPGS_MAT_DullMetal", (0.42, 0.44, 0.45, 1.0), 0.47, 0.1),
        "rubber": material("LPGS_MAT_Rubber", (0.025, 0.025, 0.025, 1.0), 0.86),
        "white": material("LPGS_MAT_WarmWhite", (0.92, 0.90, 0.84, 1.0), 0.56),
        "bulb": emissive_material("LPGS_MAT_WarmBulbGlow", (1.0, 0.70, 0.26, 1.0), strength=4.2),
        "sign_text_glow": emissive_material("LPGS_MAT_SignTextGlow", (1.0, 0.92, 0.66, 1.0), strength=2.4),
        "yellow": material("LPGS_MAT_SignYellow", (1.0, 0.82, 0.16, 1.0), 0.50),
        "green": material("LPGS_MAT_SignGreen", (0.08, 0.42, 0.30, 1.0), 0.55),
        "cone": material("LPGS_MAT_ConeOrange", (1.0, 0.33, 0.08, 1.0), 0.58),
        "person": material("LPGS_MAT_ScalePerson", (0.22, 0.28, 0.34, 1.0), 0.62),
    }

    objects: list[bpy.types.Object] = []
    add = objects.append
    extend = objects.extend

    # Ground and main building.
    add(create_box("LPGS_RoadBase", (0.0, -0.75, -0.04), (9.6, 8.0, 0.08), mats["asphalt"], collection, bevel=0.015))
    add(create_box("LPGS_BackSidewalk", (0.0, 1.1, 0.04), (6.8, 3.7, 0.08), mats["concrete"], collection, bevel=0.02))
    add(create_box("LPGS_BuildingBody", (0.0, 1.55, 1.25), (5.8, 2.7, 2.5), mats["wall"], collection, bevel=0.035))
    add(create_box("LPGS_BuildingRoof", (0.0, 1.55, 2.72), (6.35, 3.25, 0.34), mats["roof"], collection, bevel=0.04))
    add(create_box("LPGS_FrontAwning", (0.0, -0.04, 2.48), (6.65, 0.54, 0.30), mats["brand"], collection, bevel=0.025))
    add(create_box("LPGS_FrontOrangeStripe", (0.0, -0.34, 2.34), (6.5, 0.045, 0.08), mats["trim"], collection, bevel=0.004))
    for x in (-2.55, 2.55):
        add(create_box(f"LPGS_FacadePilaster_{x:+.1f}", (x, 0.12, 1.28), (0.28, 0.30, 2.34), mats["wall"], collection, bevel=0.02))
    add(create_box("LPGS_UpperFacadeBand", (0.0, 0.08, 2.08), (5.25, 0.24, 0.30), mats["wall"], collection, bevel=0.018))

    # Door and windows on the front facade.
    add(create_box("LPGS_DoubleDoorGlass", (0.0, 0.005, 0.93), (1.03, 0.06, 1.72), mats["glass"], collection, bevel=0.012))
    add(create_box("LPGS_DoorCenterDivider", (0.0, -0.035, 0.93), (0.045, 0.05, 1.66), mats["metal"], collection, bevel=0.004))
    add(create_box("LPGS_DoorTopFrame", (0.0, -0.04, 1.78), (1.16, 0.055, 0.08), mats["metal"], collection, bevel=0.004))
    for x in (-0.20, 0.20):
        add(create_box(f"LPGS_DoorHandle_{x:+.1f}", (x, -0.075, 1.02), (0.035, 0.045, 0.27), mats["yellow"], collection, bevel=0.006))
    for x in (-1.72, 1.72):
        add(create_box(f"LPGS_WindowGlass_{x:+.1f}", (x, 0.0, 1.34), (1.28, 0.06, 0.86), mats["glass"], collection, bevel=0.012))
        add(create_box(f"LPGS_WindowVerticalFrame_{x:+.1f}", (x, -0.04, 1.34), (0.045, 0.045, 0.82), mats["metal"], collection, bevel=0.003))
        add(create_box(f"LPGS_WindowSill_{x:+.1f}", (x, -0.045, 0.86), (1.42, 0.08, 0.08), mats["concrete"], collection, bevel=0.004))

    # Pump island and canopy.
    island = st.create_rounded_box(
        name="LPGS_PumpIsland",
        location=(0.0, -2.25, 0.08),
        dimensions=(4.8, 1.72, 0.16),
        radius=0.18,
        segments=3,
        collection=collection,
        material=mats["concrete"],
        role="asset_part",
        export=True,
    )
    add(island)
    add(create_box("LPGS_CanopyRoof", (0.0, -2.25, 2.86), (5.65, 2.45, 0.34), mats["roof"], collection, bevel=0.04))
    add(create_box("LPGS_CanopyFrontFascia", (0.0, -3.51, 2.75), (5.75, 0.15, 0.48), mats["brand"], collection, bevel=0.018))
    add(create_box("LPGS_CanopyBackFascia", (0.0, -0.99, 2.75), (5.75, 0.15, 0.48), mats["brand"], collection, bevel=0.018))
    add(create_box("LPGS_CanopyLeftFascia", (-2.91, -2.25, 2.75), (0.15, 2.45, 0.48), mats["brand"], collection, bevel=0.018))
    add(create_box("LPGS_CanopyRightFascia", (2.91, -2.25, 2.75), (0.15, 2.45, 0.48), mats["brand"], collection, bevel=0.018))
    add(create_text_mesh("LPGS_CanopyText_GAS", "GAS", (0.0, -3.605, 2.74), 0.46, mats["sign_text_glow"], collection, extrude=0.02))
    extend(create_canopy_bulbs(collection, mats["bulb"]))
    for x in (-2.28, 2.28):
        for y in (-3.05, -1.45):
            add(create_box(f"LPGS_CanopyColumn_{x:+.1f}_{y:+.1f}", (x, y, 1.43), (0.18, 0.18, 2.54), mats["metal"], collection, bevel=0.018))
            add(create_box(f"LPGS_ColumnFoot_{x:+.1f}_{y:+.1f}", (x, y, 0.22), (0.34, 0.34, 0.12), mats["concrete"], collection, bevel=0.015))
    for x in (-1.0, 1.0):
        add(create_box(f"LPGS_CanopyLight_{x:+.1f}", (x, -2.25, 2.63), (0.36, 0.18, 0.045), mats["yellow"], collection, bevel=0.01))

    # Fuel pump, inset screen, hose and nozzle.
    add(create_box("LPGS_FuelPumpBody", (0.0, -2.34, 0.82), (0.62, 0.46, 1.35), mats["white"], collection, bevel=0.045))
    add(create_box("LPGS_FuelPumpTopCap", (0.0, -2.34, 1.55), (0.72, 0.54, 0.16), mats["brand"], collection, bevel=0.025))
    add(create_box("LPGS_FuelPumpBase", (0.0, -2.34, 0.18), (0.76, 0.58, 0.14), mats["metal"], collection, bevel=0.018))
    add(create_box("LPGS_FuelPumpScreen", (0.0, -2.595, 1.08), (0.43, 0.045, 0.26), mats["glass"], collection, bevel=0.006))
    for label, x in (("Left", -0.16), ("Center", 0.0), ("Right", 0.16)):
        add(create_box(f"LPGS_PumpButton_{label}", (x, -2.62, 0.78), (0.07, 0.035, 0.07), mats["metal"], collection, bevel=0.006))
    add(create_box("LPGS_NozzleHandle", (0.47, -2.08, 0.70), (0.10, 0.16, 0.38), mats["rubber"], collection, bevel=0.015))
    add(create_box("LPGS_NozzleBarrel", (0.53, -2.02, 0.86), (0.10, 0.38, 0.10), mats["metal"], collection, bevel=0.012))
    extend(create_hose(collection, mats["rubber"]))

    # Props from the tutorial: trash bin, fence, cone, tire.
    add(create_cylinder("LPGS_TrashBinBody", (-3.35, -0.95, 0.42), 0.30, 0.84, mats["metal"], collection, vertices=8))
    add(create_box("LPGS_TrashBinLid", (-3.35, -0.95, 0.88), (0.75, 0.48, 0.12), mats["roof"], collection, bevel=0.025))
    add(create_box("LPGS_TrashBinSlot", (-3.35, -1.26, 0.65), (0.38, 0.035, 0.10), mats["rubber"], collection, bevel=0.004))
    for x in (-3.8, -2.6, -1.4, -0.2, 1.0, 2.2, 3.4):
        add(create_cylinder(f"LPGS_FencePost_{x:+.1f}", (x, 3.35, 0.48), 0.045, 0.96, mats["metal"], collection, vertices=8))
    for label, z in (("Lower", 0.34), ("Upper", 0.72)):
        add(create_box(f"LPGS_FenceRail_{label}", (-0.2, 3.35, z), (7.4, 0.07, 0.07), mats["metal"], collection, bevel=0.006))
    add(create_box("LPGS_TrafficConeBase", (2.95, -3.05, 0.06), (0.54, 0.54, 0.12), mats["rubber"], collection, bevel=0.012))
    add(create_cone("LPGS_TrafficConeBody", (2.95, -3.05, 0.42), 0.26, 0.07, 0.72, mats["cone"], collection, vertices=16))
    add(create_cone("LPGS_TrafficConeWhiteBand", (2.95, -3.05, 0.48), 0.18, 0.13, 0.10, mats["white"], collection, vertices=16))
    add(create_torus("LPGS_LeaningTire", (3.25, 0.08, 0.42), mats["rubber"], collection, major_radius=0.32, minor_radius=0.085))

    # Roadside logo sign with mountain shapes and text.
    add(create_cylinder("LPGS_RoadsideSignPole", (-3.6, 0.28, 1.22), 0.06, 2.44, mats["metal"], collection, vertices=10))
    add(create_box("LPGS_RoadsideSignBoard", (-3.6, 0.12, 2.42), (1.62, 0.15, 0.82), mats["green"], collection, bevel=0.025))
    add(create_tri_prism("LPGS_MountainLogo_Left", [(-4.25, 0.28), (-3.9, 2.65), (-3.56, 0.28)], 0.015, 0.055, mats["yellow"], collection))
    add(create_tri_prism("LPGS_MountainLogo_Right", [(-3.83, 0.28), (-3.42, 2.78), (-3.06, 0.28)], 0.010, 0.055, mats["trim"], collection))
    extend(create_roadside_bulbs(collection, mats["bulb"]))
    add(create_text_mesh("LPGS_RoadsideText", "Roadside", (-3.6, 0.005, 2.20), 0.20, mats["sign_text_glow"], collection, extrude=0.018))
    add(create_text_mesh("LPGS_BuildingRoadsideText", "Roadside", (0.0, -0.365, 2.36), 0.30, mats["sign_text_glow"], collection, extrude=0.018))

    # A 1.8m low-poly scale person, matching the first tutorial step.
    add(create_cylinder("LPGS_ScalePersonHead", (2.72, -0.15, 1.62), 0.13, 0.18, mats["person"], collection, vertices=10))
    add(create_box("LPGS_ScalePersonBody", (2.72, -0.15, 1.12), (0.32, 0.18, 0.82), mats["person"], collection, bevel=0.025))
    for label, x in (("Left", 2.62), ("Right", 2.82)):
        add(create_box(f"LPGS_ScalePersonLeg_{label}", (x, -0.15, 0.45), (0.11, 0.13, 0.72), mats["person"], collection, bevel=0.018))

    return objects


def scene_graph() -> dict:
    return {
        "schema_version": "1.0",
        "goal": "Rebuild the low-poly roadside gas station described in the supplied tutorial notes.",
        "mode": "FREEFORM",
        "units": "METERS",
        "parts": [
            {"id": "ground", "name": "Road base and sidewalk", "representation": "MESH", "dimensions": [9.6, 8.0, 0.16], "material_group": "asphalt/concrete", "source_confidence": 0.95},
            {"id": "building", "name": "Station building with extruded facade, doors and windows", "representation": "PRIMITIVES", "dimensions": [6.65, 3.25, 2.9], "material_group": "wall/glass/brand", "source_confidence": 0.95},
            {"id": "canopy", "name": "Pump canopy with four posts and fascia", "representation": "PRIMITIVES", "dimensions": [5.8, 2.7, 2.9], "material_group": "roof/brand/metal", "source_confidence": 0.95},
            {"id": "pump", "name": "Fuel pump with screen, buttons, nozzle and hose", "representation": "MESH", "dimensions": [1.0, 1.0, 1.6], "material_group": "white/metal/rubber", "source_confidence": 0.95},
            {"id": "sign", "name": "Roadside sign with text and mountain logo", "representation": "TEXT", "dimensions": [1.8, 0.3, 2.8], "material_group": "green/yellow/white", "source_confidence": 0.9},
            {"id": "props", "name": "Trash bin, fence, traffic cone and tire", "representation": "PRIMITIVES", "dimensions": [7.6, 4.5, 1.0], "material_group": "metal/rubber/cone", "source_confidence": 0.9},
            {"id": "scale_person", "name": "1.8m scale person from tutorial setup", "representation": "PRIMITIVES", "dimensions": [0.4, 0.2, 1.8], "material_group": "dark neutral", "source_confidence": 0.85},
        ],
        "relations": [
            {"a": "building", "type": "TOUCHES", "b": "ground", "tolerance": 0.02},
            {"a": "canopy", "type": "TOUCHES", "b": "ground", "tolerance": 0.02},
            {"a": "pump", "type": "TOUCHES", "b": "ground", "tolerance": 0.02},
            {"a": "pump", "type": "CONTAINS", "b": "hose", "tolerance": 0.05},
            {"a": "props", "type": "TOUCHES", "b": "ground", "tolerance": 0.05},
            {"a": "sign", "type": "TOUCHES", "b": "ground", "tolerance": 0.05},
            {"a": "scale_person", "type": "TOUCHES", "b": "ground", "tolerance": 0.02},
        ],
        "camera": {
            "views": ["FRONT", "FRONT_3Q", "SIDE"],
            "projection": "ORTHO",
        },
        "acceptance": {
            "required_objects": ["building", "canopy", "pump", "hose", "nozzle", "trash_bin", "fence", "traffic_cone", "tire", "roadside_sign", "glowing_bulbs"],
            "style": "low-poly primitive modeling with warm bulb-lit signs, readable from front and 3/4 views",
            "not_final_texture_pass": True,
        },
    }


def main() -> dict:
    checkpoint = checkpoint_current_scene()
    probe = capability_probe.probe()
    scene = create_clean_scene()
    root = st.ensure_collection(COLLECTION_NAME)
    if root.name not in scene.collection.children:
        try:
            scene.collection.children.link(root)
        except RuntimeError:
            pass
    create_lighting()
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph())

    objects = build_geometry(root)
    object_names = [obj.name for obj in objects]
    renders = {
        "front": render_preview(RENDERS / f"{ASSET}_01_front.png", objects, "FRONT"),
        "front_3q": render_preview(RENDERS / f"{ASSET}_02_front_3q.png", objects, "FRONT_3Q"),
        "side": render_preview(RENDERS / f"{ASSET}_03_side.png", objects, "SIDE"),
    }

    validation = st.validate_shape_asset(
        object_names=object_names,
        max_triangles=TRIANGLE_BUDGET,
        require_closed=False,
    )
    structural = scene_qa.audit_scene(
        object_names=object_names,
        contact_tolerance=0.055,
        floating_tolerance=0.12,
    )

    export = {"status": "skipped"}
    if validation["status"] != "fail":
        export = st.export_glb(
            filepath=EXPORTS / f"{ASSET}.glb",
            object_names=object_names,
        )
        public_path = ensure_allowed_path(PUBLIC_MODELS / f"{ASSET}.glb")
        shutil.copyfile(EXPORTS / f"{ASSET}.glb", public_path)
        export["public_copy"] = str(public_path)

    blend_path = ensure_allowed_path(BLENDS / f"{ASSET}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    qa = {
        "stage": "EXPORT_QA",
        "status": "review_ready" if validation["status"] != "fail" else "blocked",
        "source": "C:/Users/se-20/OneDrive/Desktop/blender/zapravka.txt (user-provided tutorial breakdown)",
        "visual_notes": [
            "Blockout follows the text breakdown: building, roof, insets, pump island, pump, hose/nozzle, sign, cone, tire, trash bin and fence.",
            "V2 adds warm emissive bulb rows to the Roadside sign and canopy GAS fascia.",
            "The result is a low-poly modeling pass with simple PBR colors, not a texture-detail pass.",
            "The 1.8m scale-person step from the tutorial is represented as a small low-poly figure beside the station.",
        ],
        "do_not_change_without_reason": [
            "semantic object names",
            "separate editable primitives",
            "export list excluding cameras and lights",
        ],
    }
    write_json(REPORTS / f"{ASSET}_qa.json", qa)

    report = {
        "status": "ok" if validation["status"] != "fail" else "validation_failed",
        "asset": ASSET,
        "scene": scene.name,
        "checkpoint": checkpoint,
        "probe": probe,
        "object_count": len(object_names),
        "renders": renders,
        "validation": validation,
        "structural_qa": structural,
        "export": export,
        "blend": {
            "path": str(blend_path),
            "bytes": blend_path.stat().st_size if blend_path.is_file() else 0,
        },
        "qa": qa,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


result = main()
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
