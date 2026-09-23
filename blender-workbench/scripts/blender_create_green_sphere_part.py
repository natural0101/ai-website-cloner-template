from __future__ import annotations

import json
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


ASSET = "green_sphere_part_v1"
SCENE_NAME = "GreenSpherePartScene"
WIDTH = 900
HEIGHT = 900


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
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.18
    scene.view_settings.gamma = 1.0

    engine = safe_set_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.2),
            ("gtao_factor", 0.45),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("GreenSphereWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.62
    return scene


def create_collection() -> bpy.types.Collection:
    root = bpy.data.collections.new("ABT_GREEN_SPHERE_PART")
    bpy.context.scene.collection.children.link(root)
    return root


def create_light(name: str, location: tuple[float, float, float], power: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    direction = Vector((0.0, 0.0, 0.0)) - Vector(location)
    obj.location = location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    st.tag_object(obj, role="studio_light", export=False)
    return obj


def setup_lighting() -> None:
    create_light("GSP_KeyLight_not_exported", (-3.0, -4.8, 4.2), 230.0, 4.4)
    create_light("GSP_FillLight_not_exported", (3.2, -3.0, 1.7), 34.0, 5.8)
    create_light("GSP_RimLight_not_exported", (2.4, 2.6, 3.0), 42.0, 4.2)


def setup_camera(name: str = "GSP_CAM_FRONT") -> dict:
    return st.setup_reference_camera(
        width=WIDTH,
        height=HEIGHT,
        world_height=2.45,
        distance=8.0,
        name=name,
        target=(0.0, 0.0, 0.02),
    )


def setup_orbit_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float]) -> dict:
    scene = bpy.context.scene
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None:
        camera = bpy.data.objects.new(name, data)
        scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.45
    scene.camera = camera
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    st.tag_object(camera, role="review_camera", export=False)
    return {"status": "ok", "camera": camera.name, "view": name, "ortho_scale": camera.data.ortho_scale}


def render(path: Path, visible: list[bpy.types.Object], camera: str = "FRONT") -> dict:
    if camera == "FRONT":
        setup_camera("GSP_CAM_FRONT")
    elif camera == "FRONT_3Q":
        setup_orbit_camera("GSP_CAM_FRONT_3Q", (2.6, -7.2, 1.25), (0.0, 0.0, 0.0))
    elif camera == "SIDE":
        setup_orbit_camera("GSP_CAM_SIDE", (7.2, -0.15, 0.7), (0.0, 0.0, 0.0))

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
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "camera": camera}


def create_green_sphere(collection: bpy.types.Collection) -> bpy.types.Object:
    material = st.create_principled_material(
        "GSP_MAT_ReferenceGreen",
        base_color=(0.18, 0.58, 0.08, 1.0),
        metallic=0.0,
        roughness=0.58,
    )
    nodes = material.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        for socket_name, value in (
            ("Specular IOR Level", 0.38),
            ("Coat Weight", 0.035),
            ("Coat Roughness", 0.62),
        ):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value

    sphere = st.create_ellipsoid(
        name="GSP_GreenSphere",
        location=(0.0, 0.0, 0.0),
        scale=(0.92, 0.92, 0.92),
        segments=72,
        rings=36,
        collection=collection,
        material=material,
        role="final_part",
        export=True,
    )
    st.shade_smooth(sphere)
    return sphere


def main() -> dict:
    checkpoint = checkpoint_current_scene()
    probe = capability_probe.probe()
    create_clean_scene()
    collection = create_collection()
    setup_lighting()
    camera_info = setup_camera()

    scene_graph = {
        "schema_version": "green-sphere-part-v1",
        "asset": ASSET,
        "target_mode": "FREEFORM",
        "part": "green sphere only",
        "triangle_budget": 10000,
        "acceptance_criteria": [
            "single closed smooth sphere",
            "saturated green toy/clay material, not pale",
            "soft highlight without blown-out white patch",
            "transparent PNG preview and web-ready GLB",
            "no hands, cuffs, cameras or lights in GLB export",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    sphere = create_green_sphere(collection)
    stage_renders = {
        "01_geometry": render(RENDERS / f"{ASSET}_01_geometry.png", [sphere]),
        "02_final_front": render(RENDERS / f"{ASSET}_02_final_front.png", [sphere]),
        "03_final_front_3q": render(RENDERS / f"{ASSET}_03_final_front_3q.png", [sphere], camera="FRONT_3Q"),
        "04_final_side": render(RENDERS / f"{ASSET}_04_final_side.png", [sphere], camera="SIDE"),
    }

    validation = st.validate_shape_asset(
        object_names=[sphere.name],
        max_triangles=10000,
        require_closed=True,
    )
    structural = scene_qa.audit_scene(object_names=[sphere.name])

    export = {"status": "skipped"}
    if validation["status"] != "fail":
        export = st.export_glb(
            filepath=EXPORTS / f"{ASSET}.glb",
            object_names=[sphere.name],
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
            "This is intentionally only the green sphere part.",
            "Do not reintroduce hands until this part is visually accepted.",
            "Material is simple Principled BSDF for GLB compatibility.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


result = main()
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
