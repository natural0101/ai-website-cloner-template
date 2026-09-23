from __future__ import annotations

import json
import math
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

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)

if str(SHAPE_TOOLS) not in sys.path:
    sys.path.insert(0, str(SHAPE_TOOLS))
if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import capability_probe
import scene_qa
import shape_tools as st


ASSET = "bottom_hand_part_v1"
SCENE_NAME = "BottomHandPartScene"
WIDTH = 1000
HEIGHT = 820


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
        if bpy.context.window is not None:
            bpy.context.window.scene = existing
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        if bpy.context.window is not None:
            scene = bpy.data.scenes.new(SCENE_NAME)
            bpy.context.window.scene = scene
        else:
            scene = bpy.context.scene
            scene.name = SCENE_NAME

    scene = bpy.context.scene
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.12
    scene.view_settings.gamma = 1.0

    engine = safe_set_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.4),
            ("gtao_factor", 0.52),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("BottomHandWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.68
    return scene


def create_collections() -> dict[str, bpy.types.Collection]:
    root = bpy.data.collections.new("ABT_BOTTOM_HAND_PART")
    bpy.context.scene.collection.children.link(root)
    source = bpy.data.collections.new("ABT_BOTTOM_HAND_SOURCE")
    output = bpy.data.collections.new("ABT_BOTTOM_HAND_OUTPUT")
    guides = bpy.data.collections.new("ABT_BOTTOM_HAND_GUIDES")
    root.children.link(source)
    root.children.link(output)
    root.children.link(guides)
    return {"root": root, "source": source, "output": output, "guides": guides}


def create_light(name: str, location: tuple[float, float, float], power: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    direction = Vector((0.0, 0.0, -0.36)) - Vector(location)
    obj.location = location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    st.tag_object(obj, role="studio_light", export=False)
    return obj


def setup_lighting() -> None:
    create_light("BHP_KeyLight_not_exported", (-3.2, -5.0, 4.0), 280.0, 4.6)
    create_light("BHP_FillLight_not_exported", (3.0, -3.4, 1.6), 48.0, 5.8)
    create_light("BHP_RimLight_not_exported", (2.8, 2.6, 2.8), 52.0, 4.4)


def setup_camera(name: str = "BHP_CAM_FRONT") -> dict:
    return st.setup_reference_camera(
        width=WIDTH,
        height=HEIGHT,
        world_height=2.62,
        distance=8.0,
        name=name,
        target=(0.12, 0.0, -0.48),
    )


def setup_orbit_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], ortho: float) -> dict:
    scene = bpy.context.scene
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None:
        camera = bpy.data.objects.new(name, data)
        scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho
    scene.camera = camera
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    st.tag_object(camera, role="review_camera", export=False)
    return {"status": "ok", "camera": camera.name, "view": name, "ortho_scale": camera.data.ortho_scale}


def material(name: str, color: tuple[float, float, float, float], roughness: float, alpha: float = 1.0) -> bpy.types.Material:
    mat = st.create_principled_material(name, base_color=color, metallic=0.0, roughness=roughness)
    nodes = mat.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        for socket_name, value in (
            ("Specular IOR Level", 0.34),
            ("Coat Weight", 0.04),
            ("Coat Roughness", 0.56),
        ):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value
        alpha_socket = principled.inputs.get("Alpha")
        if alpha_socket is not None:
            alpha_socket.default_value = alpha
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = True
    return mat


def add_tube(parts: list[bpy.types.Object], **kwargs) -> None:
    created = st.create_bezier_tube(**kwargs)
    parts.extend(created)


def create_guide_sphere(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    guide = st.create_ellipsoid(
        name="BHP_GuideSphere_not_exported",
        location=(0.0, 0.08, 0.0),
        scale=(0.92, 0.92, 0.92),
        segments=72,
        rings=36,
        collection=collection,
        material=mat,
        role="guide",
        export=False,
    )
    st.shade_smooth(guide)
    guide.display_type = "TEXTURED"
    return guide


def create_bottom_hand_sources(collection: bpy.types.Collection, mat: bpy.types.Material) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for spec in (
        ("BHP_Palm", (0.62, -0.50, -0.74), (0.42, 0.24, 0.18), (0.03, 0.0, math.radians(-8))),
        ("BHP_PalmHeel", (0.88, -0.50, -0.61), (0.24, 0.17, 0.14), (0.0, 0.0, math.radians(-10))),
        ("BHP_KnuckleMass", (0.22, -0.62, -0.86), (0.36, 0.14, 0.095), (0.0, 0.0, math.radians(-4))),
        ("BHP_FingerBaseBlend", (0.46, -0.66, -0.89), (0.52, 0.13, 0.145), (0.0, 0.0, math.radians(-10))),
        ("BHP_LowerFingerBlend", (0.54, -0.65, -1.02), (0.30, 0.105, 0.10), (0.0, 0.0, math.radians(-14))),
        ("BHP_WristPad", (1.28, -0.44, -0.62), (0.23, 0.17, 0.15), (0.0, 0.0, math.radians(-8))),
    ):
        parts.append(
            st.create_ellipsoid(
                name=spec[0],
                location=spec[1],
                scale=spec[2],
                rotation=spec[3],
                segments=40,
                rings=24,
                collection=collection,
                material=mat,
                export=False,
            )
        )

    fingers = [
        (
            "BHP_Index",
            [(0.34, -0.76, -0.70), (-0.02, -0.86, -0.88), (-0.42, -0.72, -0.84), (-0.68, -0.50, -0.62)],
            (0.118, 0.126, 0.108, 0.084),
        ),
        (
            "BHP_Middle",
            [(0.40, -0.79, -0.83), (0.02, -0.90, -1.02), (-0.36, -0.74, -1.00), (-0.62, -0.50, -0.78)],
            (0.124, 0.132, 0.112, 0.086),
        ),
        (
            "BHP_Ring",
            [(0.46, -0.78, -0.94), (0.18, -0.87, -1.10), (-0.14, -0.70, -1.10), (-0.38, -0.48, -0.93)],
            (0.098, 0.108, 0.096, 0.074),
        ),
        (
            "BHP_Pinky",
            [(0.50, -0.72, -1.03), (0.34, -0.79, -1.15), (0.12, -0.64, -1.15), (-0.05, -0.46, -1.03)],
            (0.078, 0.082, 0.074, 0.058),
        ),
    ]
    for name, points, radii in fingers:
        add_tube(
            parts,
            name=name,
            points=points,
            radii=radii,
            bevel_resolution=8,
            curve_resolution=30,
            collection=collection,
            material=mat,
            add_round_endcaps=True,
            export=False,
        )

    add_tube(
        parts,
        name="BHP_Thumb",
        points=[(0.98, -0.70, -0.48), (0.88, -0.82, -0.18), (0.70, -0.70, 0.04), (0.48, -0.50, 0.08)],
        radii=(0.146, 0.138, 0.118, 0.090),
        bevel_resolution=8,
        curve_resolution=28,
        collection=collection,
        material=mat,
        add_round_endcaps=True,
        export=False,
    )
    add_tube(
        parts,
        name="BHP_Wrist",
        points=[(1.92, -0.54, -0.58), (1.54, -0.48, -0.60), (1.12, -0.44, -0.64)],
        radii=(0.220, 0.222, 0.198),
        bevel_resolution=8,
        curve_resolution=20,
        collection=collection,
        material=mat,
        add_round_endcaps=True,
        export=False,
    )
    return parts


def add_smooth_modifiers(obj: bpy.types.Object, factor: float = 0.035, iterations: int = 1) -> None:
    if obj.type != "MESH":
        return
    smooth = obj.modifiers.new("BHP_Final_Organic_Smooth", "SMOOTH")
    smooth.factor = factor
    smooth.iterations = iterations
    st.apply_modifier(obj, smooth.name)
    weighted = obj.modifiers.new("BHP_Weighted_Normals", "WEIGHTED_NORMAL")
    if hasattr(weighted, "keep_sharp"):
        weighted.keep_sharp = True
    st.apply_modifier(obj, weighted.name)
    st.shade_smooth(obj)


def render(path: Path, visible: list[bpy.types.Object], camera: str = "FRONT") -> dict:
    if camera == "FRONT":
        setup_camera("BHP_CAM_FRONT")
    elif camera == "FRONT_3Q":
        setup_orbit_camera("BHP_CAM_FRONT_3Q", (2.4, -7.4, 0.45), (0.18, 0.0, -0.50), 2.72)
    elif camera == "SIDE":
        setup_orbit_camera("BHP_CAM_SIDE", (7.2, -0.25, -0.22), (0.18, 0.0, -0.50), 2.72)

    scene = bpy.context.scene
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


def main() -> dict:
    checkpoint = checkpoint_current_scene()
    probe = capability_probe.probe()
    create_clean_scene()
    collections = create_collections()
    setup_lighting()
    camera_info = setup_camera()

    scene_graph = {
        "schema_version": "bottom-hand-part-v1",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "part": "lower supporting hand only",
        "triangle_budget": 50000,
        "semantic_objects": [
            {"name": "bottom hand", "output_object": "BHP_BottomHand", "sources": "palm ellipsoid + palm heel + knuckle mass + 4 unequal finger capsules + thumb + wrist"},
            {"name": "approved green sphere guide", "output_object": "BHP_GuideSphere_not_exported", "export": False},
        ],
        "expected_contacts": [
            {"a": "BHP_Index/Middle/Ring/Pinky", "b": "BHP_Palm/BHP_KnuckleMass", "relation": "OVERLAPS", "minimum": "1.5-2 voxel widths before union"},
            {"a": "BHP_Thumb", "b": "BHP_Palm", "relation": "OVERLAPS", "minimum": "1.5-2 voxel widths before union"},
            {"a": "BHP_Wrist", "b": "BHP_WristPad/BHP_Palm", "relation": "OVERLAPS", "minimum": "1.5-2 voxel widths before union"},
        ],
        "acceptance_criteria": [
            "reads as lower/supporting hand, not parallel tubes",
            "fingers form a cup under the guide sphere",
            "fingertips, valleys and thumb remain visible after voxel union",
            "single closed smooth exported hand mesh",
            "guide sphere is not exported",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    hand_mat = material("BHP_MAT_OrangeHand", (1.0, 0.46, 0.03, 1.0), 0.54)
    guide_mat = material("BHP_MAT_GuideSphere", (0.18, 0.58, 0.08, 0.28), 0.58, alpha=0.28)
    guide = create_guide_sphere(collections["guides"], guide_mat)
    sources = create_bottom_hand_sources(collections["source"], hand_mat)
    source_stage = [guide] + sources

    stage_renders = {
        "01_primitives": render(RENDERS / f"{ASSET}_01_primitives.png", source_stage),
    }

    bottom_hand = st.voxel_union(
        sources,
        name="BHP_BottomHand",
        voxel_size=0.022,
        adaptivity=0.0,
        smooth_factor=0.022,
        smooth_iterations=1,
        output_collection=collections["output"],
        keep_sources=True,
        material=hand_mat,
        export=True,
    )
    joined_stage = [guide, bottom_hand]
    stage_renders["02_joined_form"] = render(RENDERS / f"{ASSET}_02_joined_form.png", joined_stage)
    add_smooth_modifiers(bottom_hand, factor=0.028, iterations=1)
    stage_renders["03_smoothed_form"] = render(RENDERS / f"{ASSET}_03_smoothed_form.png", joined_stage)
    stage_renders["04_final_front_with_guide"] = render(RENDERS / f"{ASSET}_04_final_front_with_guide.png", joined_stage)
    stage_renders["05_final_front_hand_only"] = render(RENDERS / f"{ASSET}_05_final_front_hand_only.png", [bottom_hand])
    stage_renders["06_final_front_3q"] = render(RENDERS / f"{ASSET}_06_final_front_3q.png", joined_stage, camera="FRONT_3Q")
    stage_renders["07_final_side"] = render(RENDERS / f"{ASSET}_07_final_side.png", joined_stage, camera="SIDE")

    validation = st.validate_shape_asset(
        object_names=[bottom_hand.name],
        max_triangles=50000,
        require_closed=True,
    )
    structural = scene_qa.audit_scene(object_names=[bottom_hand.name], contact_tolerance=0.08, floating_tolerance=0.16)

    export = {"status": "skipped"}
    if validation["status"] != "fail":
        export = st.export_glb(
            filepath=EXPORTS / f"{ASSET}.glb",
            object_names=[bottom_hand.name],
        )
        public_path = PUBLIC_MODELS / f"{ASSET}.glb"
        public_path.write_bytes((EXPORTS / f"{ASSET}.glb").read_bytes())
        export["public_copy"] = str(public_path)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "status": "ok",
        "checkpoint": checkpoint,
        "probe": probe,
        "scene": SCENE_NAME,
        "camera": camera_info,
        "stage_renders": stage_renders,
        "validation": validation,
        "structural_qa": structural,
        "export": export,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "notes": [
            "This is intentionally only the bottom/supporting hand part.",
            "The green sphere is a non-exported guide for fit review.",
            "Do not assemble with upper hand/cuffs until this lower hand is accepted.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


result = main()
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
