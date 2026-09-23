from __future__ import annotations

import importlib.util
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
V3_SCRIPT = WORKBENCH / "scripts" / "blender_create_network_symbol_logo_v3.py"
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"

ASSET = "network_symbol_lesson01_hero_loop"
SCENE_NAME = "NetworkSymbolLesson01HeroLoop"
WIDTH = 1100
HEIGHT = 900
END_FRAME = 144
PREVIEW_FRAMES = (1, 36, 72, 108, 144)

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


def load_v3_module():
    spec = importlib.util.spec_from_file_location("network_symbol_logo_v3_tools", V3_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {V3_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v3 = load_v3_module()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


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
    scene.view_settings.exposure = -0.08
    scene.view_settings.gamma = 1.0

    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 1.9),
            ("gtao_factor", 0.58),
            ("use_bloom", True),
            ("bloom_intensity", 0.03),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("NetworkLesson01World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        background.inputs["Strength"].default_value = 0.16
    return scene


def setup_camera() -> bpy.types.Object:
    camera_data = bpy.data.cameras.new("NSL01_Camera_FRONT")
    camera = bpy.data.objects.new("NSL01_Camera_FRONT", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (0.0, -6.4, 0.0)
    camera.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 2.75
    bpy.context.scene.camera = camera
    return tag(camera, "review_camera", False)


def setup_lights() -> None:
    specs = [
        ("NSL01_Key_not_exported", (-2.0, -4.2, 3.0), 130.0, 4.3),
        ("NSL01_Fill_not_exported", (2.4, -4.0, 1.6), 30.0, 5.8),
        ("NSL01_GreenRim_not_exported", (2.2, -2.4, 0.9), 26.0, 2.4),
    ]
    for name, location, power, size in specs:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = power
        light.size = size
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0.0, 0.0, 0.0)) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
        tag(obj, "studio_light", False)


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


def create_materials() -> dict[str, bpy.types.Material]:
    return {
        "dark": v3.material(
            "NSL01_DarkGraph",
            (0.004, 0.033, 0.038, 1.0),
            0.5,
            emission=(0.0, 0.022, 0.026, 1.0),
            emission_strength=0.035,
        ),
        "green": v3.material(
            "NSL01_SignalGreen",
            (0.0, 1.0, 0.06, 1.0),
            0.43,
            emission=(0.0, 0.96, 0.06, 1.0),
            emission_strength=0.46,
        ),
    }


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def animate_hero_loop(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> dict:
    parts = v3.build_logo(collection, "NSL01", mats)
    root = v3.create_empty(collection, "NSL01_GreenLayer_HeroLoop_ROOT")
    for obj in parts["green"]:
        parent_keep_world(obj, root)

    key(root, 1, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))
    key(root, 36, loc=(0.10, -0.06, 0.02), rot=(0.0, math.radians(-1.0), math.radians(0.6)), scale=(1.0, 1.0, 1.0))
    key(root, 72, loc=(0.30, -0.18, 0.06), rot=(0.0, math.radians(-3.0), math.radians(1.4)), scale=(1.0, 1.0, 1.0))
    key(root, 108, loc=(0.10, -0.06, 0.02), rot=(0.0, math.radians(1.0), math.radians(-0.6)), scale=(1.0, 1.0, 1.0))
    key(root, 144, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    animated = [root]
    smooth_keys(animated)
    return {"objects": parts["all"] + [root], "animated": animated}


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


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_render, hidden = previous[obj.name]
            obj.hide_set(hidden)


def render_frame(collection: bpy.types.Collection, frame: int, path: Path) -> dict:
    bpy.context.scene.frame_set(frame)
    previous = hide_except(collection)
    try:
        scene = bpy.context.scene
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "frame": frame}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def validate(collection: bpy.types.Collection) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    tris = triangle_count(meshes)
    errors = []
    warnings = []
    if not meshes:
        errors.append("No exportable meshes.")
    if tris > 35000:
        warnings.append(f"Triangle count above lesson target: {tris}/35000.")
    return {
        "asset": ASSET,
        "triangles": tris,
        "mesh_objects": len(meshes),
        "animated_objects": len([obj for obj in exportable if obj.animation_data]),
        "errors": errors,
        "warnings": warnings,
    }


def export_glb(collection: bpy.types.Collection) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    path = EXPORTS / f"{ASSET}.glb"
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
    return {"path": str(path), "public_path": str(public_path), "bytes": path.stat().st_size if path.is_file() else 0}


def glb_check(path: Path) -> dict:
    data = path.read_bytes()
    magic, _, _ = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        return {"file": path.name, "error": "not_glb"}
    chunk_len, _ = struct.unpack_from("<II", data, 12)
    gltf = json.loads(data[20 : 20 + chunk_len].decode("utf-8"))
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "animations": len(gltf.get("animations", [])),
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
    }


def write_lesson_notes(report: dict) -> Path:
    path = REPORTS / f"{ASSET}_lesson_notes.md"
    text = f"""# Lesson 01 - Network Hero Loop

Goal: one clean looping landing-page hero animation, not three rough variants.

What this lesson practices:

- front orthographic camera for icon/logo readability;
- real spherical nodes plus flat capsule connectors;
- single parented green signal layer for coherent motion;
- loop animation where frame 1 and frame {END_FRAME} match;
- black-background preview before GLB handoff;
- GLB animation track verification.

Result:

- triangles: {report['validation']['triangles']}
- validation errors: {len(report['validation']['errors'])}
- validation warnings: {len(report['validation']['warnings'])}
- GLB animations: {report['glb_animation_check'].get('animations')}

Next lesson:

- verify this GLB in the browser/Three.js scene with real page lighting and camera.
"""
    path.write_text(text, encoding="utf-8")
    return path


def build_scene() -> dict:
    scene = setup_scene()
    setup_camera()
    setup_lights()
    collection = v3.create_collection("NSL01_HeroLoop")
    mats = create_materials()
    animate_hero_loop(collection, mats)

    scene_graph = {
        "asset": ASSET,
        "lesson": "01",
        "goal": "single polished looping hero animation",
        "source_asset": "network_symbol_logo_v3",
        "frame_start": 1,
        "frame_end": END_FRAME,
        "camera": "orthographic front",
        "motion": "green signal layer detaches, hovers, and returns to exact start pose",
        "acceptance": [
            "frame 1 and 144 match for loop playback",
            "nodes remain real spheres",
            "no decorative rings, particles, orbit marks, or perspective molecule look",
            "GLB has animation tracks",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    renders = [render_frame(collection, frame, RENDERS / f"{ASSET}_frame_{frame:03d}.png") for frame in PREVIEW_FRAMES]
    validation = validate(collection)
    export = {} if validation["errors"] else export_glb(collection)
    glb_report = glb_check(Path(export["path"])) if export else {}

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "renders": renders,
        "validation": validation,
        "export": export,
        "glb_animation_check": glb_report,
        "warnings": ["Lesson asset; next step is browser/Three.js verification."],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    notes_path = write_lesson_notes(report)
    report["lesson_notes"] = str(notes_path)
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(build_scene(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
