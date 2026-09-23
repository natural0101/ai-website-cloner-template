from __future__ import annotations

import json
import math
import shutil
import struct
import sys
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
V4_BLENDER_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"

ASSET = "landing_mascot_alive_v8_companion"
SCENE_NAME = "LandingMascotAliveV8Companion"
END_FRAME = 120
FPS = 24
WIDTH = 1200
HEIGHT = 1000
PREVIEW_FRAMES = (1, 30, 60, 90, 120)

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)

if str(V4_BLENDER_TOOLS) not in sys.path:
    sys.path.append(str(V4_BLENDER_TOOLS))

try:
    import scene_qa
except Exception:  # pragma: no cover - Blender runtime fallback
    scene_qa = None


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object, location: bool = False, rotation: bool = False, scale: bool = True) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def safe_engine(scene: bpy.types.Scene) -> str:
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
    roughness: float = 0.55,
    metallic: float = 0.0,
    alpha: float = 1.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (color[0], color[1], color[2], alpha)
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = False
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], alpha)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission is not None:
            for key in ("Emission Color", "Emission"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission
                    break
            for key in ("Emission Strength", "Emission Weight"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission_strength
                    break
    return mat


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
    scene.frame_set(1)
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.1),
            ("gtao_factor", 0.72),
            ("use_bloom", True),
            ("bloom_intensity", 0.015),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("LandingMascotV5World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.015, 0.021, 0.023, 1.0)
        bg.inputs["Strength"].default_value = 0.20
    return scene


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_empty(collection: bpy.types.Collection, name: str, location=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.12
    obj.location = location
    collection.objects.link(obj)
    return tag(obj, "animation_pivot", True)


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for user_collection in list(obj.users_collection):
        if user_collection != collection:
            user_collection.objects.unlink(obj)
    if obj.name not in collection.objects.keys():
        try:
            collection.objects.link(obj)
        except RuntimeError:
            pass


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def shade_smooth(obj: bpy.types.Object, weighted_normals: bool = True) -> bpy.types.Object:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if weighted_normals:
            set_active(obj)
            modifier = obj.modifiers.new("weighted_soft_normals", "WEIGHTED_NORMAL")
            modifier.keep_sharp = True
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except Exception:
                pass
    return obj


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def rounded_box(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    segments: int = 10,
    role: str = "semantic_mesh",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    apply_transform(obj, location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("large_soft_bevel", "BEVEL")
    bevel.width = radius
    bevel.segments = segments
    bevel.affect = "EDGES"
    obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    if "weighted_normals" in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier="weighted_normals")
    tag(obj, role, True)
    return shade_smooth(obj)


def ellipsoid(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    segments: int = 32,
    rings: int = 16,
    role: str = "semantic_mesh",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    apply_transform(obj, location=False, rotation=False, scale=True)
    tag(obj, role, True)
    return shade_smooth(obj)


def cylinder(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int = 32,
    role: str = "semantic_mesh",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    tag(obj, role, True)
    return shade_smooth(obj)


def tube_mesh(
    collection: bpy.types.Collection,
    name: str,
    points: list[tuple[float, float, float]],
    radii: list[float],
    mat: bpy.types.Material,
    radial_segments: int = 14,
    role: str = "semantic_mesh",
) -> bpy.types.Object:
    if len(points) < 2 or len(points) != len(radii):
        raise ValueError("tube_mesh needs matching points/radii with at least two sections")

    vectors = [Vector(p) for p in points]
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    for index, center in enumerate(vectors):
        if index == 0:
            tangent = vectors[1] - center
        elif index == len(vectors) - 1:
            tangent = center - vectors[index - 1]
        else:
            tangent = vectors[index + 1] - vectors[index - 1]
        tangent.normalize()
        reference = Vector((0.0, 0.0, 1.0))
        if abs(tangent.dot(reference)) > 0.92:
            reference = Vector((1.0, 0.0, 0.0))
        normal = tangent.cross(reference)
        normal.normalize()
        binormal = normal.cross(tangent)
        binormal.normalize()
        for segment in range(radial_segments):
            angle = math.tau * segment / radial_segments
            offset = normal * math.cos(angle) * radii[index] + binormal * math.sin(angle) * radii[index]
            vertices.append(tuple(center + offset))

    for index in range(len(vectors) - 1):
        base = index * radial_segments
        nxt = (index + 1) * radial_segments
        for segment in range(radial_segments):
            faces.append((base + segment, base + (segment + 1) % radial_segments, nxt + (segment + 1) % radial_segments, nxt + segment))

    start_center = len(vertices)
    vertices.append(tuple(vectors[0]))
    end_center = len(vertices)
    vertices.append(tuple(vectors[-1]))
    last_ring = (len(vectors) - 1) * radial_segments
    for segment in range(radial_segments):
        faces.append((start_center, (segment + 1) % radial_segments, segment))
        faces.append((end_center, last_ring + segment, last_ring + (segment + 1) % radial_segments))

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, mat)
    tag(obj, role, True)
    return shade_smooth(obj)


def curve_tube(
    collection: bpy.types.Collection,
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
    bevel_resolution: int = 6,
    resolution_u: int = 18,
    role: str = "semantic_mesh",
) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_curve", "CURVE")
    curve.dimensions = "3D"
    curve.fill_mode = "FULL"
    curve.resolution_u = resolution_u
    curve.bevel_depth = radius
    curve.bevel_resolution = bevel_resolution
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points, strict=True):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    set_active(obj)
    bpy.ops.object.convert(target="MESH")
    converted = bpy.context.object
    converted.name = name
    converted.data.name = f"{name}_mesh"
    link_to_collection(converted, collection)
    assign_material(converted, mat)
    tag(converted, role, True)
    return shade_smooth(converted)


def setup_camera_and_lights(collection: bpy.types.Collection) -> dict[str, bpy.types.Object]:
    camera_data = bpy.data.cameras.new("LM5_Camera_data")
    camera = bpy.data.objects.new("LM5_Camera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (3.2, -6.4, 2.55)
    camera.rotation_euler = (math.radians(66.0), 0.0, math.radians(26.0))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.85
    bpy.context.scene.camera = camera
    tag(camera, "preview_camera", False)

    floor_mat = material("LM5_PreviewFloorMat", (0.035, 0.044, 0.047, 1.0), roughness=0.8)
    floor = rounded_box(collection, "LM5_preview_floor_not_exported", (0.0, 0.18, -0.105), (3.4, 2.8, 0.04), 0.025, floor_mat, segments=3, role="preview_floor")
    floor["abt_export"] = False

    def light(name: str, kind: str, loc: tuple[float, float, float], energy: float, color: tuple[float, float, float]) -> bpy.types.Object:
        data = bpy.data.lights.new(name=f"{name}_data", type=kind)
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        data.energy = energy
        data.color = color
        if hasattr(data, "size"):
            data.size = 4.6
        bpy.context.scene.collection.objects.link(obj)
        tag(obj, "preview_light", False)
        return obj

    key = light("LM5_Key_softbox", "AREA", (-3.6, -4.8, 5.0), 520.0, (1.0, 0.88, 0.74))
    fill = light("LM5_Fill_teal", "AREA", (3.6, -3.2, 2.4), 100.0, (0.45, 0.98, 0.92))
    rim = light("LM5_Rim_warm", "AREA", (2.8, 2.6, 4.1), 175.0, (1.0, 0.66, 0.48))
    return {"camera": camera, "floor": floor, "key": key, "fill": fill, "rim": rim}


def key(obj: bpy.types.Object, frame: int, loc=None, rot=None, scale=None) -> None:
    bpy.context.scene.frame_set(frame)
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
        if not obj.animation_data or not obj.animation_data.action:
            continue
        obj.animation_data.action.name = f"{ASSET}_{obj.name}_Loop"
        for curve in getattr(obj.animation_data.action, "fcurves", []):
            for item in curve.keyframe_points:
                item.interpolation = "BEZIER"


def build_mascot(collection: bpy.types.Collection) -> dict:
    mats = {
        "body": material("LM5_TealBody_PBR", (0.045, 0.78, 0.72, 1.0), roughness=0.48),
        "body_dark": material("LM5_DeepTealPants_PBR", (0.05, 0.25, 0.30, 1.0), roughness=0.58),
        "face": material("LM5_WarmFace_PBR", (0.98, 0.86, 0.70, 1.0), roughness=0.50),
        "coral": material("LM5_CoralHandsShoes_PBR", (1.0, 0.49, 0.39, 1.0), roughness=0.50),
        "cream": material("LM5_CreamPanels_PBR", (0.93, 0.91, 0.80, 1.0), roughness=0.56),
        "eye": material("LM5_GlossyEyes_PBR", (0.025, 0.033, 0.040, 1.0), roughness=0.28),
        "glint": material("LM5_EyeGlints_PBR", (1.0, 0.97, 0.87, 1.0), roughness=0.18),
        "line": material("LM5_DarkLine_PBR", (0.035, 0.052, 0.058, 1.0), roughness=0.45),
        "signal": material("LM5_SignalAmber_PBR", (1.0, 0.68, 0.18, 1.0), roughness=0.42, emission=(1.0, 0.55, 0.13, 1.0), emission_strength=0.08),
    }

    root = create_empty(collection, "LM5_Root", (0.0, 0.0, 0.0))
    body_pivot = create_empty(collection, "LM5_BodyPivot", (0.0, 0.0, 1.02))
    head_pivot = create_empty(collection, "LM5_HeadPivot", (0.0, -0.01, 1.78))
    antenna_left_pivot = create_empty(collection, "LM5_AntennaLeftPivot", (-0.33, -0.02, 2.64))
    antenna_right_pivot = create_empty(collection, "LM5_AntennaRightPivot", (0.33, -0.02, 2.64))
    parent_keep_world(body_pivot, root)
    parent_keep_world(head_pivot, root)
    parent_keep_world(antenna_left_pivot, head_pivot)
    parent_keep_world(antenna_right_pivot, head_pivot)

    body = rounded_box(collection, "LM5_Body_single_soft_core", (0.0, 0.0, 1.03), (0.98, 0.62, 1.18), 0.24, mats["body"], segments=14)
    belly = rounded_box(collection, "LM5_Belly_embedded_front_panel", (0.0, -0.345, 1.05), (0.54, 0.14, 0.56), 0.045, mats["cream"], segments=8)
    badge = rounded_box(collection, "LM5_Chest_small_badge", (0.0, -0.445, 1.16), (0.22, 0.040, 0.13), 0.032, mats["signal"], segments=6)
    neck = cylinder(collection, "LM5_Neck_soft_collar_overlap", (0.0, 0.0, 1.61), 0.43, 0.22, mats["body"], vertices=40)
    head = rounded_box(collection, "LM5_Head_rounded_helper_block", (0.0, -0.005, 2.12), (1.16, 0.70, 0.88), 0.22, mats["face"], segments=16)
    visor = rounded_box(collection, "LM5_Face_soft_visor_panel", (0.0, -0.385, 2.13), (0.82, 0.07, 0.50), 0.12, mats["cream"], segments=10)

    eye_l = ellipsoid(collection, "LM5_Eye_left_blinking", (-0.23, -0.435, 2.22), (0.088, 0.026, 0.125), mats["eye"], segments=28, rings=12)
    eye_r = ellipsoid(collection, "LM5_Eye_right_blinking", (0.23, -0.435, 2.22), (0.088, 0.026, 0.125), mats["eye"], segments=28, rings=12)
    glint_l = ellipsoid(collection, "LM5_Eye_left_glint", (-0.258, -0.458, 2.275), (0.022, 0.008, 0.032), mats["glint"], segments=16, rings=8)
    glint_r = ellipsoid(collection, "LM5_Eye_right_glint", (0.202, -0.458, 2.275), (0.022, 0.008, 0.032), mats["glint"], segments=16, rings=8)
    cheek_l = ellipsoid(collection, "LM5_Cheek_left_soft_dot", (-0.39, -0.432, 2.02), (0.055, 0.018, 0.040), mats["coral"], segments=16, rings=8)
    cheek_r = ellipsoid(collection, "LM5_Cheek_right_soft_dot", (0.39, -0.432, 2.02), (0.055, 0.018, 0.040), mats["coral"], segments=16, rings=8)
    smile = tube_mesh(collection, "LM5_Smile_one_piece_curve", [(-0.12, -0.46, 1.98), (-0.04, -0.475, 1.94), (0.04, -0.475, 1.94), (0.12, -0.46, 1.98)], [0.018, 0.019, 0.019, 0.018], mats["line"], radial_segments=8)

    left_rod = curve_tube(collection, "LM5_Antenna_left_flexible_rod", [(-0.33, -0.02, 2.62), (-0.43, -0.025, 2.78), (-0.55, -0.035, 2.80)], 0.021, mats["body_dark"], bevel_resolution=4)
    right_rod = curve_tube(collection, "LM5_Antenna_right_flexible_rod", [(0.33, -0.02, 2.62), (0.43, -0.025, 2.78), (0.55, -0.035, 2.80)], 0.021, mats["body_dark"], bevel_resolution=4)
    left_orb = ellipsoid(collection, "LM5_Antenna_left_signal_orb", (-0.60, -0.04, 2.80), (0.055, 0.055, 0.055), mats["signal"], segments=18, rings=8)
    right_orb = ellipsoid(collection, "LM5_Antenna_right_signal_orb", (0.60, -0.04, 2.80), (0.055, 0.055, 0.055), mats["signal"], segments=18, rings=8)

    left_arm = curve_tube(collection, "LM5_LeftArm_one_piece_relaxed_tube", [(-0.56, -0.04, 1.42), (-0.86, -0.09, 1.08), (-0.74, -0.12, 0.76)], 0.103, mats["coral"], bevel_resolution=6)
    right_arm = curve_tube(collection, "LM5_RightArm_one_piece_attached_gesture_tube", [(0.56, -0.04, 1.42), (0.85, -0.10, 1.78), (0.76, -0.15, 2.10)], 0.105, mats["coral"], bevel_resolution=6)
    shoulder_l = ellipsoid(collection, "LM5_LeftShoulder_integrated_socket", (-0.55, -0.060, 1.42), (0.22, 0.165, 0.22), mats["coral"], segments=28, rings=12)
    shoulder_r = ellipsoid(collection, "LM5_RightShoulder_integrated_socket", (0.55, -0.060, 1.42), (0.22, 0.165, 0.22), mats["coral"], segments=28, rings=12)
    elbow_l = ellipsoid(collection, "LM5_LeftElbow_soft_transition", (-0.86, -0.10, 1.08), (0.18, 0.135, 0.18), mats["coral"], segments=24, rings=10)
    elbow_r = ellipsoid(collection, "LM5_RightElbow_soft_transition", (0.85, -0.11, 1.78), (0.18, 0.135, 0.18), mats["coral"], segments=24, rings=10)
    wrist_l = ellipsoid(collection, "LM5_LeftWrist_clean_overlap_band", (-0.74, -0.135, 0.76), (0.125, 0.085, 0.125), mats["coral"], segments=20, rings=8)
    wrist_r = ellipsoid(collection, "LM5_RightWrist_clean_overlap_band", (0.76, -0.165, 2.10), (0.125, 0.085, 0.125), mats["coral"], segments=20, rings=8)

    hand_l = ellipsoid(collection, "LM5_LeftHand_attached_mitten", (-0.73, -0.16, 0.66), (0.18, 0.10, 0.16), mats["coral"], rotation=(0.0, 0.0, math.radians(-8)), segments=24, rings=10)
    hand_r = ellipsoid(collection, "LM5_RightHand_attached_mitten", (0.74, -0.19, 2.22), (0.18, 0.10, 0.19), mats["coral"], rotation=(0.0, 0.0, math.radians(11)), segments=24, rings=10)
    for i, (x, z, s) in enumerate(((0.64, 2.35, 0.062), (0.74, 2.39, 0.065), (0.85, 2.34, 0.058)), start=1):
        ellipsoid(collection, f"LM5_RightHand_soft_finger_{i}", (x, -0.205, z), (s, 0.045, 0.105), mats["coral"], rotation=(0.0, 0.0, math.radians(8 + i * 6)), segments=16, rings=8)
    thumb_r = ellipsoid(collection, "LM5_RightHand_thumb_bump", (0.58, -0.19, 2.18), (0.080, 0.052, 0.105), mats["coral"], rotation=(0.0, 0.0, math.radians(-30)), segments=16, rings=8)
    thumb_l = ellipsoid(collection, "LM5_LeftHand_thumb_bump", (-0.58, -0.16, 0.67), (0.070, 0.047, 0.095), mats["coral"], rotation=(0.0, 0.0, math.radians(28)), segments=16, rings=8)

    leg_l = curve_tube(collection, "LM5_LeftLeg_single_tapered_support", [(-0.24, 0.00, 0.50), (-0.30, -0.02, 0.20)], 0.115, mats["body_dark"], bevel_resolution=5)
    leg_r = curve_tube(collection, "LM5_RightLeg_single_tapered_support", [(0.24, 0.00, 0.50), (0.32, -0.02, 0.20)], 0.115, mats["body_dark"], bevel_resolution=5)
    foot_l = rounded_box(collection, "LM5_LeftFoot_flat_soft_sneaker", (-0.38, -0.13, 0.03), (0.48, 0.32, 0.16), 0.055, mats["coral"], rotation=(0.0, 0.0, math.radians(2)), segments=7)
    foot_r = rounded_box(collection, "LM5_RightFoot_flat_soft_sneaker", (0.42, -0.13, 0.03), (0.50, 0.32, 0.16), 0.055, mats["coral"], rotation=(0.0, 0.0, math.radians(-2)), segments=7)

    head_members = [head, visor, eye_l, eye_r, glint_l, glint_r, cheek_l, cheek_r, smile]
    body_members = [
        body,
        belly,
        badge,
        neck,
        left_arm,
        right_arm,
        shoulder_l,
        shoulder_r,
        elbow_l,
        elbow_r,
        wrist_l,
        wrist_r,
        hand_l,
        hand_r,
        thumb_l,
        thumb_r,
        leg_l,
        leg_r,
        foot_l,
        foot_r,
    ]
    body_members.extend([obj for obj in collection.objects if obj.name.startswith("LM5_RightHand_soft_finger_")])
    for obj in body_members:
        parent_keep_world(obj, body_pivot)
    for obj in head_members:
        parent_keep_world(obj, head_pivot)
    for obj in (left_rod, left_orb):
        parent_keep_world(obj, antenna_left_pivot)
    for obj in (right_rod, right_orb):
        parent_keep_world(obj, antenna_right_pivot)

    parts = {
        "pivots": [root.name, body_pivot.name, head_pivot.name, antenna_left_pivot.name, antenna_right_pivot.name],
        "large_masses": [body.name, belly.name, neck.name, head.name, visor.name],
        "face": [eye_l.name, eye_r.name, glint_l.name, glint_r.name, cheek_l.name, cheek_r.name, smile.name],
        "attached_arms": [left_arm.name, right_arm.name, shoulder_l.name, shoulder_r.name, elbow_l.name, elbow_r.name, wrist_l.name, wrist_r.name, hand_l.name, hand_r.name, thumb_l.name, thumb_r.name],
        "right_mitten_fingers": [obj.name for obj in collection.objects if obj.name.startswith("LM5_RightHand_soft_finger_")],
        "legs_and_feet": [leg_l.name, leg_r.name, foot_l.name, foot_r.name],
        "antenna": [left_rod.name, right_rod.name, left_orb.name, right_orb.name],
        "animation_objects": {
            "root": root.name,
            "body": body_pivot.name,
            "head": head_pivot.name,
            "antenna_left": antenna_left_pivot.name,
            "antenna_right": antenna_right_pivot.name,
            "eyes": [eye_l.name, eye_r.name, glint_l.name, glint_r.name],
        },
    }
    return {"parts": parts, "pivots": {"root": root, "body": body_pivot, "head": head_pivot, "antenna_left": antenna_left_pivot, "antenna_right": antenna_right_pivot}, "eyes": [eye_l, eye_r, glint_l, glint_r]}


def animate_character(pivots: dict[str, bpy.types.Object], eyes: list[bpy.types.Object]) -> None:
    root = pivots["root"]
    body = pivots["body"]
    head = pivots["head"]
    antenna_left = pivots["antenna_left"]
    antenna_right = pivots["antenna_right"]

    for frame, z, rot in ((1, 0.0, 0.0), (30, 0.035, math.radians(-0.6)), (60, 0.010, math.radians(0.9)), (90, 0.030, math.radians(-0.4)), (120, 0.0, 0.0)):
        key(root, frame, loc=(0.0, 0.0, z), rot=(0.0, 0.0, rot))

    for frame, scale in ((1, (1.0, 1.0, 1.0)), (30, (1.015, 1.0, 0.985)), (60, (0.995, 1.0, 1.015)), (90, (1.010, 1.0, 0.990)), (120, (1.0, 1.0, 1.0))):
        key(body, frame, scale=scale)

    for frame, rot in (
        (1, (0.0, 0.0, 0.0)),
        (30, (math.radians(1.5), 0.0, math.radians(-1.2))),
        (60, (math.radians(-1.0), 0.0, math.radians(1.1))),
        (90, (math.radians(0.9), 0.0, math.radians(-0.6))),
        (120, (0.0, 0.0, 0.0)),
    ):
        key(head, frame, rot=rot)

    for pivot, sign in ((antenna_left, 1.0), (antenna_right, -1.0)):
        for frame, rot_z in ((1, 0.0), (40, math.radians(6.0 * sign)), (80, math.radians(-4.5 * sign)), (120, 0.0)):
            key(pivot, frame, rot=(0.0, 0.0, rot_z))

    for eye in eyes:
        for frame, scale in (
            (1, (1.0, 1.0, 1.0)),
            (34, (1.0, 1.0, 1.0)),
            (37, (1.0, 1.0, 0.08)),
            (41, (1.0, 1.0, 1.0)),
            (82, (1.0, 1.0, 1.0)),
            (85, (1.0, 1.0, 0.08)),
            (89, (1.0, 1.0, 1.0)),
            (120, (1.0, 1.0, 1.0)),
        ):
            key(eye, frame, scale=scale)

    smooth_keys([root, body, head, antenna_left, antenna_right, *eyes])


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    previous: dict[str, tuple[bool, bool]] = {}
    keep = set(collection.objects)
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_viewport, obj.hide_render)
        if obj not in keep and obj.type not in {"CAMERA", "LIGHT"}:
            obj.hide_viewport = True
            obj.hide_render = True
    return previous


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_viewport, obj.hide_render = previous[obj.name]


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_camera_view(camera: bpy.types.Object, view: str) -> None:
    if view == "front":
        camera.location = (0.0, -6.8, 1.62)
        camera.data.ortho_scale = 3.72
    elif view == "side":
        camera.location = (5.9, -0.18, 1.58)
        camera.data.ortho_scale = 3.72
    else:
        camera.location = (3.2, -6.4, 2.55)
        camera.data.ortho_scale = 3.92
    look_at(camera, (0.0, -0.02, 1.40))


def render_frame(collection: bpy.types.Collection, camera: bpy.types.Object, frame: int, path: Path, view: str = "front_3q") -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    set_camera_view(camera, view)
    previous = hide_except(collection)
    try:
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"frame": frame, "view": view, "path": str(path), "bytes": path.stat().st_size if path.exists() else 0}


def exportable_objects(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    return [obj for obj in collection.objects if bool(obj.get("abt_export", True))]


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    count = 0
    for obj in objects:
        if obj.type == "MESH" and obj.data is not None:
            count += sum(len(poly.vertices) - 2 for poly in obj.data.polygons)
    return count


def validate(collection: bpy.types.Collection) -> dict:
    objects = exportable_objects(collection)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    errors: list[str] = []
    warnings: list[str] = []
    triangles = triangle_count(meshes)
    if not meshes:
        errors.append("No exportable mesh objects")
    if triangles > 30000:
        warnings.append(f"Triangle budget above mobile target: {triangles}/30000")
    for obj in meshes:
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material")
        if any(value < 0 for value in obj.scale):
            errors.append(f"{obj.name} has negative scale")
        if any(abs(value - 1.0) > 0.001 for value in obj.scale):
            warnings.append(f"{obj.name} has unapplied scale {tuple(round(v, 3) for v in obj.scale)}")
        for vertex in obj.data.vertices:
            if not all(math.isfinite(v) for v in vertex.co):
                errors.append(f"{obj.name} has non-finite coordinates")
                break
    animated = [obj for obj in objects if obj.animation_data and obj.animation_data.action]
    return {
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "dominant_fix": "replace rejected blob-with-arm architecture with a cohesive rounded helper character; v8 softens the head/body contact and restores visible chest badge",
        "frame_start": 1,
        "frame_end": END_FRAME,
        "fps": FPS,
        "triangles": triangles,
        "mesh_objects": len(meshes),
        "exportable_objects": len(objects),
        "animated_objects": len(animated),
        "errors": errors,
        "warnings": warnings,
    }


def export_glb(collection: bpy.types.Collection) -> dict:
    objects = exportable_objects(collection)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]
    path = EXPORTS / f"{ASSET}.glb"
    props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {
        "filepath": str(path),
        "export_format": "GLB",
        "use_selection": True,
        "export_animations": True,
        "export_nla_strips": False,
        "export_force_sampling": True,
        "export_frame_range": True,
        "export_frame_step": 1,
        "export_optimize_animation_size": False,
    }
    filtered = {key: value for key, value in kwargs.items() if key in props}
    bpy.ops.export_scene.gltf(**filtered)
    public_path = PUBLIC_MODELS / path.name
    shutil.copy2(path, public_path)
    return {
        "path": str(path),
        "public_path": str(public_path),
        "bytes": path.stat().st_size,
        "public_bytes": public_path.stat().st_size,
    }


def glb_check(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        return {"file": path.name, "bytes": len(data), "errors": ["not a GLB file"]}
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        return {"file": path.name, "bytes": len(data), "errors": ["first chunk is not JSON"]}
    payload = data[20 : 20 + chunk_length].decode("utf-8")
    gltf = json.loads(payload)
    return {
        "file": path.name,
        "bytes": len(data),
        "animations": len(gltf.get("animations", [])),
        "animation_names": [item.get("name", "") for item in gltf.get("animations", [])],
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
    }


def write_scene_graph(parts: dict) -> dict:
    graph = {
        "asset": ASSET,
        "purpose": "more polished simple living character for a landing hero after rejecting v1-v7 quality",
        "target_mode": "HYBRID_HERO",
        "original_design": True,
        "dominant_defect_from_previous_best": "v7 cleaned arm joints, but the head/body contact still read as a hard dark separation and the chest badge was hidden by the front panel",
        "parts": parts,
        "expected_contacts": [
            "head overlaps neck collar; collar overlaps torso",
            "visor, eyes, cheeks and smile sit embedded on the head front",
            "shoulder sockets overlap body sides and one-piece arm tubes",
            "elbow transition volumes overlap arm tubes",
            "mitten hands overlap wrist ends; right hand fingers overlap right palm",
            "legs overlap lower body and feet",
            "antenna rods overlap head through animated pivots",
        ],
        "animation": {
            "name": "alive_loop_120f",
            "frames": END_FRAME,
            "fps": FPS,
            "motions": [
                "root bob",
                "body breathing scale",
                "small head nod",
                "antenna drift",
                "two blinks",
            ],
            "loop": "frame 1 and frame 120 return to the same primary pose",
        },
        "acceptance": [
            "not a grey mannequin or a loose collection of parts",
            "limbs are visibly attached in front, 3/4 and side views",
            "right greeting hand does not float away from the arm",
            "face reads at landing scale",
            "GLB contains animation data",
            "preview floor, camera and lights are not exported",
            "triangles under 30k mobile hero budget",
        ],
        "self_review_policy": {
            "do_not_call_done": "If this still reads as cheap, detached or blob-like, keep it as an artifact only and do not present it as final.",
            "compare_against": "landing_mascot_alive_v4_companion self-review board",
        },
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", graph)
    return graph


def build_scene() -> dict:
    scene = setup_scene()
    collection = create_collection("LM5_Output")
    setup = setup_camera_and_lights(collection)
    result = build_mascot(collection)
    animate_character(result["pivots"], result["eyes"])
    scene_graph = write_scene_graph(result["parts"])

    renders = [
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_front.png", "front"),
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_front_3q.png", "front_3q"),
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_side.png", "side"),
    ]
    for frame in PREVIEW_FRAMES:
        renders.append(render_frame(collection, setup["camera"], frame, RENDERS / f"{ASSET}_frame_{frame:03d}.png", "front_3q"))

    validation = validate(collection)
    object_names = [obj.name for obj in exportable_objects(collection)]
    qa = scene_qa.audit_scene(object_names=object_names, floating_tolerance=0.075) if scene_qa else {"warnings": ["scene_qa unavailable"], "errors": []}
    write_json(REPORTS / f"{ASSET}_structural_qa.json", qa)
    export = export_glb(collection) if not validation["errors"] else {"skipped": True, "reason": validation["errors"]}
    animation_check = None
    if "path" in export:
        animation_check = glb_check(Path(export["path"]))
        write_json(REPORTS / f"{ASSET}_glb_animation_check.json", animation_check)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    report = {
        "asset": ASSET,
        "scene": scene.name,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.exists() else 0},
        "scene_graph": scene_graph,
        "renders": renders,
        "validation": validation,
        "structural_qa": {
            "path": str(REPORTS / f"{ASSET}_structural_qa.json"),
            "errors": qa.get("errors", []),
            "warnings": qa.get("warnings", []),
            "potential_floating_components": qa.get("potential_floating_components", []),
        },
        "export": export,
        "glb_animation_check": animation_check,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(build_scene(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
