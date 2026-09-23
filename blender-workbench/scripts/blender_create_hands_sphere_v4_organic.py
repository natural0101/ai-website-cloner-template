from __future__ import annotations

import json
import math
import shutil
import sys
from datetime import datetime
from pathlib import Path

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
REFERENCE = WORKBENCH / "references" / "hands-sphere-primary.png"

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)

if str(SHAPE_TOOLS) not in sys.path:
    sys.path.insert(0, str(SHAPE_TOOLS))
if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import shape_tools as st
import capability_probe
import scene_qa


ASSET = "hands_sphere_icon_v4_organic"
SCENE_NAME = "HandsSphereV4OrganicScene"
WIDTH = 927
HEIGHT = 750
MASK_WIDTH = 309
MASK_HEIGHT = 250
WORLD_HEIGHT = 3.05


def safe_set_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def checkpoint_current_scene() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = CHECKPOINTS / f"{ASSET}_prechange_{timestamp}.blend"
    result = {"path": str(destination), "status": "skipped"}
    if bpy.context.scene.objects:
        bpy.ops.wm.save_as_mainfile(filepath=str(destination))
        result["status"] = "saved"
        result["bytes"] = destination.stat().st_size
    return result


def create_clean_scene() -> bpy.types.Scene:
    existing = bpy.data.scenes.get(SCENE_NAME)
    if existing is not None:
        bpy.context.window.scene = existing
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        scene = bpy.data.scenes.new(SCENE_NAME)
        bpy.context.window.scene = scene
    scene = bpy.context.scene
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
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
            ("gtao_factor", 0.85),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("HS_V4_World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 1.0
    return scene


def ensure_collection_tree() -> dict[str, bpy.types.Collection]:
    root = bpy.data.collections.new("ABT_HS_V4_ORGANIC")
    bpy.context.scene.collection.children.link(root)
    source = bpy.data.collections.new("ABT_HS_V4_ORGANIC_SOURCE")
    output = bpy.data.collections.new("ABT_HS_V4_ORGANIC_OUTPUT")
    stage = bpy.data.collections.new("ABT_HS_V4_ORGANIC_STAGE")
    root.children.link(source)
    root.children.link(output)
    root.children.link(stage)
    left = bpy.data.collections.new("ABT_HS_V4_LEFT_HAND_SOURCE")
    right = bpy.data.collections.new("ABT_HS_V4_RIGHT_HAND_SOURCE")
    source.children.link(left)
    source.children.link(right)
    return {"root": root, "source": source, "output": output, "stage": stage, "left": left, "right": right}


def create_light(name: str, location: tuple[float, float, float], power: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    direction = Vector((0.0, 0.0, 0.0)) - Vector(location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    st.tag_object(obj, role="studio_light", export=False)
    return obj


def setup_lighting() -> None:
    create_light("HS_V4_KeyLight_not_exported", (-3.4, -5.2, 4.6), 325.0, 4.8)
    create_light("HS_V4_FillLight_not_exported", (3.4, -4.3, 2.2), 80.0, 5.6)
    create_light("HS_V4_RimLight_not_exported", (1.6, 2.2, 3.6), 85.0, 3.8)


def setup_camera(width: int, height: int, name: str = "HS_V4_CAM_FRONT") -> dict:
    info = st.setup_reference_camera(
        width=width,
        height=height,
        world_height=WORLD_HEIGHT,
        distance=10.0,
        name=name,
        target=(0.02, 0.0, 0.0),
    )
    camera = bpy.context.scene.camera
    if camera is not None and REFERENCE.is_file():
        camera.data.show_background_images = True
        camera.data.background_images.clear()
        bg = camera.data.background_images.new()
        bg.image = bpy.data.images.load(str(REFERENCE), check_existing=True)
        bg.alpha = 0.22
        bg.display_depth = "BACK"
        bg.show_background_image = True
    return info


def material(name: str, color: tuple[float, float, float, float], roughness: float, metallic: float = 0.0) -> bpy.types.Material:
    mat = st.create_principled_material(name, base_color=color, metallic=metallic, roughness=roughness)
    nodes = mat.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        for socket_name, value in (
            ("Coat Weight", 0.07),
            ("Coat Roughness", 0.48),
            ("Specular IOR Level", 0.45),
        ):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value
    return mat


def add_smooth_modifiers(obj: bpy.types.Object, *, factor: float = 0.14, iterations: int = 2) -> None:
    if obj.type != "MESH":
        return
    smooth = obj.modifiers.new("HS_V4_Final_Organic_Smooth", "SMOOTH")
    smooth.factor = factor
    smooth.iterations = iterations
    st.apply_modifier(obj, smooth.name)
    weighted = obj.modifiers.new("HS_V4_Weighted_Normals", "WEIGHTED_NORMAL")
    if hasattr(weighted, "keep_sharp"):
        weighted.keep_sharp = True
    st.apply_modifier(obj, weighted.name)
    st.shade_smooth(obj)


def render(path: Path, visible: list[bpy.types.Object], *, width: int = WIDTH, height: int = HEIGHT, camera: str = "FRONT") -> dict:
    scene = bpy.context.scene
    if camera == "FRONT":
        setup_camera(width, height, "HS_V4_CAM_FRONT")
    elif camera == "FRONT_3Q":
        setup_orbit_camera(width, height, "HS_V4_CAM_FRONT_3Q", (2.1, -8.8, 0.72), (0.02, 0.0, 0.0), 4.25)
    elif camera == "SIDE":
        setup_orbit_camera(width, height, "HS_V4_CAM_SIDE", (7.8, -0.35, 0.45), (0.02, 0.0, 0.0), 4.25)
    target_names = {obj.name for obj in visible}
    previous = {obj.name: obj.hide_render for obj in scene.objects}
    previous_view = {obj.name: obj.hide_get() for obj in scene.objects}
    try:
        for obj in scene.objects:
            if obj.type in {"CAMERA", "LIGHT"}:
                obj.hide_render = False
                obj.hide_set(False)
            else:
                shown = obj.name in target_names
                obj.hide_render = not shown
                obj.hide_set(not shown)
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        for obj in scene.objects:
            if obj.name in previous:
                obj.hide_render = previous[obj.name]
            if obj.name in previous_view:
                obj.hide_set(previous_view[obj.name])
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "camera": camera, "objects": sorted(target_names)}


def setup_orbit_camera(
    width: int,
    height: int,
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float,
) -> None:
    scene = bpy.context.scene
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None:
        camera = bpy.data.objects.new(name, data)
        scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    st.tag_object(camera, role="review_camera", export=False)


def create_cuff(
    *,
    name: str,
    location: tuple[float, float, float],
    side: str,
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    angle_z: float,
) -> bpy.types.Object:
    sign = -1.0 if side == "LEFT" else 1.0
    length = 0.62
    radius = 0.31
    rotation = (0.0, math.radians(90), angle_z)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=72,
        radius=radius,
        depth=length,
        end_fill_type="NGON",
        location=location,
        rotation=rotation,
    )
    body = bpy.context.object
    body.name = f"{name}_Body"
    st.move_to_collection(body, collection)
    body.data.materials.append(mat)
    bevel = body.modifiers.new("HS_V4_Cuff_Bevel", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 8
    bevel.use_clamp_overlap = True
    st.apply_modifier(body, bevel.name)
    st.shade_smooth(body)

    outer_x = location[0] + sign * length * 0.49 * math.cos(angle_z)
    outer_z = location[2] + sign * length * 0.49 * math.sin(angle_z)
    bpy.ops.mesh.primitive_torus_add(
        major_segments=72,
        minor_segments=16,
        major_radius=radius * 0.88,
        minor_radius=0.045,
        location=(outer_x, location[1] - 0.015, outer_z),
        rotation=rotation,
    )
    rim = bpy.context.object
    rim.name = f"{name}_SoftRim"
    st.move_to_collection(rim, collection)
    rim.data.materials.append(mat)
    st.shade_smooth(rim)

    joined = st.join_objects_as_mesh([body, rim], name=name)
    st.move_to_collection(joined, collection)
    joined.data.materials.clear()
    joined.data.materials.append(mat)
    add_smooth_modifiers(joined, factor=0.04, iterations=1)
    st.tag_object(joined, role="final_part", export=True)
    return joined


def add_tube(parts: list[bpy.types.Object], **kwargs) -> None:
    created = st.create_bezier_tube(**kwargs)
    parts.extend(created)


def create_left_hand(source: bpy.types.Collection, hand_mat: bpy.types.Material) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for spec in (
        ("HS_V4_LeftHand_Palm", (-0.96, -0.50, 0.54), (0.36, 0.22, 0.17), (0.02, 0.0, math.radians(-6))),
        ("HS_V4_LeftHand_ThenarPad", (-0.72, -0.62, 0.22), (0.20, 0.15, 0.14), (0.0, 0.0, math.radians(18))),
        ("HS_V4_LeftHand_KnuckleMass", (-0.42, -0.54, 0.76), (0.25, 0.14, 0.10), (0.0, 0.0, math.radians(-4))),
        ("HS_V4_LeftHand_WristPad", (-1.25, -0.56, 0.50), (0.20, 0.18, 0.17), (0.0, 0.0, math.radians(5))),
    ):
        parts.append(
            st.create_ellipsoid(
                name=spec[0],
                location=spec[1],
                scale=spec[2],
                rotation=spec[3],
                segments=40,
                rings=24,
                collection=source,
                material=hand_mat,
                export=False,
            )
        )

    fingers = [
        (
            "HS_V4_LeftHand_Index",
            [(-0.58, -0.73, 0.88), (-0.16, -0.84, 1.03), (0.32, -0.72, 0.99), (0.65, -0.50, 0.78)],
            (0.120, 0.132, 0.118, 0.092),
        ),
        (
            "HS_V4_LeftHand_Middle",
            [(-0.60, -0.76, 0.68), (-0.22, -0.86, 0.80), (0.24, -0.72, 0.68), (0.53, -0.50, 0.49)],
            (0.122, 0.132, 0.114, 0.090),
        ),
        (
            "HS_V4_LeftHand_Ring",
            [(-0.66, -0.72, 0.50), (-0.36, -0.82, 0.55), (-0.04, -0.68, 0.41), (0.17, -0.49, 0.24)],
            (0.106, 0.108, 0.096, 0.078),
        ),
        (
            "HS_V4_LeftHand_Pinky",
            [(-0.78, -0.62, 0.36), (-0.58, -0.70, 0.39), (-0.38, -0.62, 0.29), (-0.24, -0.48, 0.17)],
            (0.082, 0.082, 0.074, 0.060),
        ),
    ]
    for name, points, radii in fingers:
        add_tube(
            parts,
            name=name,
            points=points,
            radii=radii,
            bevel_resolution=8,
            curve_resolution=28,
            collection=source,
            material=hand_mat,
            add_round_endcaps=True,
            export=False,
        )

    add_tube(
        parts,
        name="HS_V4_LeftHand_Thumb",
        points=[(-0.86, -0.78, 0.23), (-0.62, -0.88, -0.02), (-0.28, -0.73, -0.07), (0.02, -0.52, 0.08)],
        radii=(0.140, 0.128, 0.108, 0.086),
        bevel_resolution=8,
        curve_resolution=26,
        collection=source,
        material=hand_mat,
        add_round_endcaps=True,
        export=False,
    )
    add_tube(
        parts,
        name="HS_V4_LeftHand_Wrist",
        points=[(-1.78, -0.64, 0.50), (-1.42, -0.60, 0.50), (-1.06, -0.57, 0.49)],
        radii=(0.225, 0.228, 0.210),
        bevel_resolution=8,
        curve_resolution=20,
        collection=source,
        material=hand_mat,
        add_round_endcaps=True,
        export=False,
    )
    return parts


def create_right_hand(source: bpy.types.Collection, hand_mat: bpy.types.Material) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for spec in (
        ("HS_V4_RightHand_Palm", (0.76, -0.34, -0.50), (0.40, 0.23, 0.18), (0.02, 0.0, math.radians(9))),
        ("HS_V4_RightHand_ThenarPad", (0.76, -0.32, -0.34), (0.13, 0.11, 0.10), (0.0, 0.0, math.radians(-8))),
        ("HS_V4_RightHand_KnuckleMass", (0.18, -0.52, -0.74), (0.25, 0.14, 0.10), (0.0, 0.0, math.radians(2))),
        ("HS_V4_RightHand_WristPad", (1.18, -0.48, -0.40), (0.22, 0.18, 0.16), (0.0, 0.0, math.radians(-6))),
    ):
        parts.append(
            st.create_ellipsoid(
                name=spec[0],
                location=spec[1],
                scale=spec[2],
                rotation=spec[3],
                segments=40,
                rings=24,
                collection=source,
                material=hand_mat,
                export=False,
            )
        )

    fingers = [
        (
            "HS_V4_RightHand_Index",
            [(0.44, -0.78, -0.55), (0.10, -0.87, -0.74), (-0.34, -0.71, -0.76), (-0.60, -0.50, -0.58)],
            (0.116, 0.124, 0.108, 0.086),
        ),
        (
            "HS_V4_RightHand_Middle",
            [(0.54, -0.80, -0.67), (0.14, -0.89, -0.90), (-0.26, -0.72, -0.93), (-0.50, -0.50, -0.78)],
            (0.120, 0.128, 0.112, 0.090),
        ),
        (
            "HS_V4_RightHand_Ring",
            [(0.64, -0.76, -0.78), (0.32, -0.84, -0.98), (-0.04, -0.68, -1.01), (-0.26, -0.49, -0.88)],
            (0.106, 0.108, 0.098, 0.080),
        ),
        (
            "HS_V4_RightHand_Pinky",
            [(0.72, -0.68, -0.86), (0.50, -0.74, -1.00), (0.24, -0.62, -1.03), (0.06, -0.46, -0.94)],
            (0.084, 0.082, 0.076, 0.062),
        ),
    ]
    for name, points, radii in fingers:
        add_tube(
            parts,
            name=name,
            points=points,
            radii=radii,
            bevel_resolution=8,
            curve_resolution=28,
            collection=source,
            material=hand_mat,
            add_round_endcaps=True,
            export=False,
        )

    add_tube(
        parts,
        name="HS_V4_RightHand_Thumb",
        points=[(1.02, -0.78, -0.28), (0.94, -0.88, 0.02), (0.78, -0.74, 0.24), (0.58, -0.52, 0.30)],
        radii=(0.142, 0.132, 0.112, 0.088),
        bevel_resolution=8,
        curve_resolution=26,
        collection=source,
        material=hand_mat,
        add_round_endcaps=True,
        export=False,
    )
    add_tube(
        parts,
        name="HS_V4_RightHand_Wrist",
        points=[(1.74, -0.66, -0.36), (1.38, -0.55, -0.38), (1.00, -0.44, -0.43)],
        radii=(0.218, 0.220, 0.202),
        bevel_resolution=8,
        curve_resolution=20,
        collection=source,
        material=hand_mat,
        add_round_endcaps=True,
        export=False,
    )
    return parts


def set_sources_visible(parts: list[bpy.types.Object], visible: bool) -> None:
    for obj in parts:
        if bpy.data.objects.get(obj.name) is not None:
            obj.hide_render = not visible
            obj.hide_set(not visible)
            obj.display_type = "TEXTURED" if visible else "WIRE"


def final_export_objects() -> list[bpy.types.Object]:
    objects = []
    for name in (
        "HS_V4_GreenSphere",
        "HS_V4_LeftHand",
        "HS_V4_RightHand",
        "HS_V4_LeftCuff",
        "HS_V4_RightCuff",
    ):
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"Missing final object: {name}")
        objects.append(obj)
    return objects


def main() -> dict:
    initial_info = bpy.context.scene.name, len(bpy.context.scene.objects)
    checkpoint = checkpoint_current_scene()
    probe = capability_probe.probe()
    scene = create_clean_scene()
    collections = ensure_collection_tree()
    setup_lighting()
    camera_info = setup_camera(WIDTH, HEIGHT)

    scene_graph = {
        "schema_version": "local-v4-organic-1",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "reference": str(REFERENCE),
        "reference_resolution": [MASK_WIDTH, MASK_HEIGHT],
        "camera_type": "orthographic",
        "triangle_budget": 100000,
        "semantic_objects": [
            {"name": "green sphere", "output_object": "HS_V4_GreenSphere"},
            {"name": "left hand", "output_object": "HS_V4_LeftHand", "sources": "palm ellipsoid + unequal finger capsules + thumb + wrist"},
            {"name": "right hand", "output_object": "HS_V4_RightHand", "sources": "palm ellipsoid + unequal finger capsules + thumb + wrist"},
            {"name": "left cuff", "output_object": "HS_V4_LeftCuff"},
            {"name": "right cuff", "output_object": "HS_V4_RightCuff"},
        ],
        "expected_contacts": [
            {"a": "HS_V4_LeftHand", "b": "HS_V4_GreenSphere", "relation": "OVERLAPS/TOUCHES", "reason": "left hand wraps the top/front of the sphere"},
            {"a": "HS_V4_RightHand", "b": "HS_V4_GreenSphere", "relation": "OVERLAPS/TOUCHES", "reason": "right hand supports the sphere from below/front"},
            {"a": "HS_V4_LeftHand", "b": "HS_V4_LeftCuff", "relation": "TOUCHES", "reason": "wrist enters cuff"},
            {"a": "HS_V4_RightHand", "b": "HS_V4_RightCuff", "relation": "TOUCHES", "reason": "wrist enters cuff"},
        ],
        "hidden_side_assumptions": [
            "Single reference constrains only the front icon view.",
            "Depth is designed for plus/minus 15-20 degree hero orbit, not claimed as recovered true 360.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    sphere_mat = material("HS_V4_MAT_GreenSphere", (0.26, 0.66, 0.12, 1.0), 0.44)
    hand_mat = material("HS_V4_MAT_OrangeHands", (1.0, 0.32, 0.00, 1.0), 0.50)
    cuff_mat = material("HS_V4_MAT_PinkCuffs", (1.0, 0.55, 0.75, 1.0), 0.55)

    sphere = st.create_ellipsoid(
        name="HS_V4_GreenSphere",
        location=(0.06, 0.02, 0.03),
        scale=(0.75, 0.75, 0.75),
        segments=96,
        rings=56,
        collection=collections["output"],
        material=sphere_mat,
        role="final_part",
        export=True,
    )
    left_cuff = create_cuff(
        name="HS_V4_LeftCuff",
        location=(-1.78, -0.90, 0.50),
        side="LEFT",
        mat=cuff_mat,
        collection=collections["output"],
        angle_z=math.radians(-4),
    )
    right_cuff = create_cuff(
        name="HS_V4_RightCuff",
        location=(1.74, -0.90, -0.34),
        side="RIGHT",
        mat=cuff_mat,
        collection=collections["output"],
        angle_z=math.radians(4),
    )

    left_sources = create_left_hand(collections["left"], hand_mat)
    right_sources = create_right_hand(collections["right"], hand_mat)
    source_stage = [sphere, left_cuff, right_cuff] + left_sources + right_sources
    stage_renders = {
        "01_primitives": render(RENDERS / f"{ASSET}_01_primitives.png", source_stage),
    }

    left_hand = st.voxel_union(
        left_sources,
        name="HS_V4_LeftHand",
        voxel_size=0.022,
        adaptivity=0.0,
        smooth_factor=0.035,
        smooth_iterations=1,
        output_collection=collections["output"],
        keep_sources=True,
        material=hand_mat,
        export=True,
    )
    right_hand = st.voxel_union(
        right_sources,
        name="HS_V4_RightHand",
        voxel_size=0.022,
        adaptivity=0.0,
        smooth_factor=0.035,
        smooth_iterations=1,
        output_collection=collections["output"],
        keep_sources=True,
        material=hand_mat,
        export=True,
    )
    joined_stage = [sphere, left_hand, right_hand, left_cuff, right_cuff]
    stage_renders["02_joined_form"] = render(RENDERS / f"{ASSET}_02_joined_form.png", joined_stage)

    add_smooth_modifiers(left_hand, factor=0.035, iterations=1)
    add_smooth_modifiers(right_hand, factor=0.035, iterations=1)
    add_smooth_modifiers(sphere, factor=0.02, iterations=1)
    stage_renders["03_smoothed_form"] = render(RENDERS / f"{ASSET}_03_smoothed_form.png", joined_stage)

    final_objects = final_export_objects()
    stage_renders["04_final_front"] = render(RENDERS / f"{ASSET}_04_final_front.png", final_objects)
    stage_renders["05_final_front_3q"] = render(RENDERS / f"{ASSET}_05_final_front_3q.png", final_objects, camera="FRONT_3Q")
    stage_renders["06_final_side"] = render(RENDERS / f"{ASSET}_06_final_side.png", final_objects, camera="SIDE")
    setup_camera(MASK_WIDTH, MASK_HEIGHT, "HS_V4_CAM_MASK")
    silhouette = st.render_silhouette_mask(
        filepath=RENDERS / f"{ASSET}_silhouette_mask.png",
        object_names=[obj.name for obj in final_objects],
        width=MASK_WIDTH,
        height=MASK_HEIGHT,
    )
    setup_camera(WIDTH, HEIGHT, "HS_V4_CAM_FRONT")

    validation = st.validate_shape_asset(
        object_names=[obj.name for obj in final_objects],
        max_triangles=100000,
        require_closed=True,
    )
    structural = scene_qa.audit_scene(
        object_names=[obj.name for obj in final_objects],
        contact_tolerance=0.08,
        floating_tolerance=0.16,
    )
    export = {"status": "skipped"}
    if validation["status"] != "fail":
        export = st.export_glb(
            filepath=EXPORTS / f"{ASSET}.glb",
            object_names=[obj.name for obj in final_objects],
        )
        shutil.copyfile(EXPORTS / f"{ASSET}.glb", PUBLIC_MODELS / f"{ASSET}.glb")
        export["public_copy"] = str(PUBLIC_MODELS / f"{ASSET}.glb")

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "status": "ok" if validation["status"] != "fail" else "validation_failed",
        "initial_scene": {"name": initial_info[0], "object_count": initial_info[1]},
        "checkpoint": checkpoint,
        "probe": probe,
        "scene": scene.name,
        "target_mode": "HYBRID_HERO",
        "camera": camera_info,
        "stage_renders": stage_renders,
        "silhouette": silhouette,
        "validation": validation,
        "structural_qa": structural,
        "export": export,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "scene_report": st.scene_report(),
        "notes": [
            "V4 rebuild uses separate final objects: green sphere, left hand, right hand, left cuff, right cuff.",
            "Hands are not flat masks; each hand is fused from palm ellipsoid, wrist, unequal finger capsules and thumb capsule.",
            "SOURCE primitives are preserved under ABT_HS_V4_ORGANIC_SOURCE and not exported.",
            "Target mode is HYBRID_HERO, not claimed true 360 from one reference.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    write_json(REPORTS / f"{ASSET}_structural_qa.json", structural)
    return report


print(json.dumps(main(), ensure_ascii=False, indent=2, default=str))
