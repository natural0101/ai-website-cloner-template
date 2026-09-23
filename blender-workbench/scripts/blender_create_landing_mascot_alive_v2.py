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

ASSET = "landing_mascot_alive_v2"
SCENE_NAME = "LandingMascotAliveV2"
END_FRAME = 120
FPS = 24
WIDTH = 1200
HEIGHT = 1000
PREVIEW_FRAMES = (1, 24, 48, 72, 96, 120)

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
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
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
            ("gtao_distance", 2.4),
            ("gtao_factor", 0.62),
            ("use_bloom", True),
            ("bloom_intensity", 0.018),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("LandingMascotWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.018, 0.022, 0.027, 1.0)
        bg.inputs["Strength"].default_value = 0.18
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


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


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


def flat_object(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = False
    return obj


def shade_smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def ellipsoid(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    subdivisions: int = 2,
    smooth: bool = False,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    tag(obj, "semantic_mesh", True)
    return shade_smooth(obj) if smooth else flat_object(obj)


def cylinder_between(
    collection: bpy.types.Collection,
    name: str,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    radius_a: float,
    radius_b: float,
    mat: bpy.types.Material,
    vertices: int = 8,
) -> bpy.types.Object:
    start = Vector(a)
    end = Vector(b)
    mid = (start + end) * 0.5
    direction = end - start
    depth = direction.length
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius_a,
        radius2=radius_b,
        depth=depth,
        location=mid,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    tag(obj, "semantic_mesh", True)
    return flat_object(obj)


def rounded_box(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.04,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_material(obj, mat)
    bevel_mod = obj.modifiers.new(f"{name}_small_bevel", "BEVEL")
    bevel_mod.width = bevel
    bevel_mod.segments = 1
    bevel_mod.affect = "EDGES"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.modifier_apply(modifier=bevel_mod.name)
    link_to_collection(obj, collection)
    tag(obj, "semantic_mesh", True)
    return flat_object(obj)


def setup_camera_and_lights(collection: bpy.types.Collection) -> None:
    camera_data = bpy.data.cameras.new("LM_Camera_FRONT_3Q")
    camera = bpy.data.objects.new("LM_Camera_FRONT_3Q", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (2.25, -6.8, 2.35)
    target = Vector((0.0, 0.0, 1.42))
    camera.rotation_euler = (target - Vector(camera.location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 4.65
    bpy.context.scene.camera = camera
    tag(camera, "review_camera", False)

    lights = [
        ("LM_Key_not_exported", (-3.2, -4.8, 4.6), 440.0, 4.7),
        ("LM_Fill_not_exported", (2.8, -5.4, 2.2), 78.0, 6.0),
        ("LM_Rim_not_exported", (2.7, 2.4, 3.3), 180.0, 3.2),
    ]
    for name, location, power, size in lights:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = power
        light.size = size
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (target - Vector(location)).to_track_quat("-Z", "Y").to_euler()
        tag(obj, "studio_light", False)

    floor_mat = material("LM_PreviewFloor_MatteCharcoal", (0.055, 0.064, 0.075, 1.0), 0.72)
    bpy.ops.mesh.primitive_plane_add(size=4.8, location=(0.0, 0.0, 0.02))
    floor = bpy.context.object
    floor.name = "LM_Preview_Floor_not_exported"
    floor.rotation_euler = (0.0, 0.0, 0.0)
    assign_material(floor, floor_mat)
    tag(floor, "preview_floor", False)


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
        action.name = f"{ASSET}_{obj.name}_Loop"
        for fcurve in fcurves:
            for point in fcurve.keyframe_points:
                point.interpolation = "BEZIER"


def build_mascot(collection: bpy.types.Collection) -> dict:
    mats = {
        "body": material("LM_TealBody", (0.05, 0.72, 0.63, 1.0), 0.5),
        "body_dark": material("LM_DeepTealAccents", (0.015, 0.13, 0.16, 1.0), 0.58),
        "head": material("LM_WarmIvoryHead", (0.94, 0.89, 0.78, 1.0), 0.52),
        "coral": material("LM_CoralHandsFeet", (1.0, 0.42, 0.32, 1.0), 0.5),
        "yellow": material("LM_SignalYellow", (1.0, 0.78, 0.18, 1.0), 0.43, emission=(1.0, 0.55, 0.05, 1.0), emission_strength=0.08),
        "eye": material("LM_InkEyes", (0.015, 0.018, 0.027, 1.0), 0.46),
        "eye_glint": material("LM_EyeGlint", (1.0, 1.0, 0.92, 1.0), 0.3),
        "belly": material("LM_SoftBellyPanel", (0.98, 0.86, 0.62, 1.0), 0.58),
    }

    root = create_empty(collection, "LM_Root", (0.0, 0.0, 0.0))
    body_pivot = create_empty(collection, "LM_BodyPivot", (0.0, 0.0, 1.04))
    head_pivot = create_empty(collection, "LM_HeadPivot", (0.0, -0.02, 1.52))
    right_arm_pivot = create_empty(collection, "LM_RightArmPivot", (0.405, -0.09, 1.23))
    left_arm_pivot = create_empty(collection, "LM_LeftArmPivot", (-0.47, -0.01, 1.36))
    antenna_pivot = create_empty(collection, "LM_AntennaPivot", (0.06, -0.02, 1.72))
    tag(left_arm_pivot, "discarded_left_arm_pivot", False)

    for pivot in (body_pivot, head_pivot, right_arm_pivot, left_arm_pivot):
        parent_keep_world(pivot, root)
    parent_keep_world(antenna_pivot, head_pivot)

    body = ellipsoid(collection, "LM_Body_beany_core", (0.0, 0.0, 1.04), (0.47, 0.35, 0.62), mats["body"], 2)
    belly = ellipsoid(collection, "LM_Belly_soft_front_panel", (0.0, -0.31, 1.02), (0.27, 0.04, 0.31), mats["belly"], 2, smooth=True)
    collar = cylinder_between(collection, "LM_Collar_dark_band", (-0.34, -0.01, 1.56), (0.34, -0.01, 1.56), 0.074, 0.074, mats["body_dark"], 10)
    collar.scale.y = 0.18

    head = ellipsoid(collection, "LM_Head_soft_faceted", (0.0, -0.025, 1.55), (0.34, 0.28, 0.19), mats["body"], 2)
    tag(head, "discarded_source_lobe", False)
    head.hide_render = True
    head.hide_set(True)
    cheek_l = ellipsoid(collection, "LM_Cheek_left_coral", (-0.175, -0.365, 1.01), (0.045, 0.018, 0.035), mats["coral"], 1, smooth=True)
    cheek_r = ellipsoid(collection, "LM_Cheek_right_coral", (0.175, -0.365, 1.01), (0.045, 0.018, 0.035), mats["coral"], 1, smooth=True)

    eye_l = ellipsoid(collection, "LM_Eye_left_blinking", (-0.11, -0.375, 1.18), (0.047, 0.018, 0.068), mats["eye"], 2, smooth=True)
    eye_r = ellipsoid(collection, "LM_Eye_right_blinking", (0.11, -0.375, 1.18), (0.047, 0.018, 0.068), mats["eye"], 2, smooth=True)
    glint_l = ellipsoid(collection, "LM_Eye_left_glint", (-0.125, -0.39, 1.205), (0.013, 0.006, 0.016), mats["eye_glint"], 1, smooth=True)
    glint_r = ellipsoid(collection, "LM_Eye_right_glint", (0.095, -0.39, 1.205), (0.013, 0.006, 0.016), mats["eye_glint"], 1, smooth=True)

    mouth_a = ellipsoid(collection, "LM_Smile_left_corner", (-0.042, -0.386, 0.98), (0.019, 0.009, 0.013), mats["eye"], 1, smooth=True)
    mouth_b = ellipsoid(collection, "LM_Smile_center", (0.0, -0.39, 0.965), (0.026, 0.009, 0.014), mats["eye"], 1, smooth=True)
    mouth_c = ellipsoid(collection, "LM_Smile_right_corner", (0.042, -0.386, 0.98), (0.019, 0.009, 0.013), mats["eye"], 1, smooth=True)

    antenna_stem = cylinder_between(collection, "LM_Antenna_stem", (0.06, -0.015, 1.63), (0.11, -0.01, 1.86), 0.022, 0.016, mats["body_dark"], 7)
    antenna_tip = ellipsoid(collection, "LM_Antenna_signal_tip", (0.12, -0.01, 1.93), (0.07, 0.07, 0.07), mats["yellow"], 2, smooth=True)

    upper_r = cylinder_between(collection, "LM_RightArm_upper_segment", (0.39, -0.08, 1.2), (0.51, -0.09, 1.36), 0.085, 0.073, mats["coral"], 7)
    lower_r = cylinder_between(collection, "LM_RightArm_forearm_segment", (0.51, -0.09, 1.36), (0.57, -0.11, 1.55), 0.073, 0.058, mats["coral"], 7)
    right_socket = ellipsoid(collection, "LM_RightArm_body_socket", (0.365, -0.22, 1.18), (0.13, 0.055, 0.16), mats["coral"], 2, smooth=True)
    right_shoulder = ellipsoid(collection, "LM_RightShoulder_overlap_cap", (0.405, -0.095, 1.23), (0.115, 0.065, 0.115), mats["coral"], 1, smooth=True)
    elbow_r = ellipsoid(collection, "LM_RightElbow_soft_hinge", (0.51, -0.105, 1.36), (0.077, 0.047, 0.077), mats["coral"], 1, smooth=True)
    palm_r = ellipsoid(collection, "LM_RightHand_mitten_palm", (0.58, -0.12, 1.64), (0.102, 0.064, 0.108), mats["coral"], 2, smooth=True)
    finger_r1 = ellipsoid(collection, "LM_RightHand_finger_top", (0.525, -0.15, 1.715), (0.03, 0.019, 0.055), mats["coral"], 1, smooth=True)
    finger_r2 = ellipsoid(collection, "LM_RightHand_finger_mid", (0.602, -0.15, 1.73), (0.03, 0.019, 0.06), mats["coral"], 1, smooth=True)
    finger_r3 = ellipsoid(collection, "LM_RightHand_finger_side", (0.674, -0.14, 1.69), (0.028, 0.018, 0.052), mats["coral"], 1, smooth=True)

    upper_l = cylinder_between(collection, "LM_LeftArm_upper_segment", (-0.47, -0.015, 1.35), (-0.7, -0.04, 1.12), 0.094, 0.08, mats["body_dark"], 7)
    lower_l = cylinder_between(collection, "LM_LeftArm_forearm_segment", (-0.7, -0.04, 1.12), (-0.83, -0.08, 0.88), 0.08, 0.068, mats["body_dark"], 7)
    palm_l = ellipsoid(collection, "LM_LeftHand_relaxed_mitten", (-0.85, -0.1, 0.81), (0.105, 0.065, 0.112), mats["coral"], 2, smooth=True)
    left_stub = ellipsoid(collection, "LM_LeftSide_tiny_hand", (-0.43, -0.12, 0.98), (0.095, 0.055, 0.09), mats["coral"], 2, smooth=True)
    for discarded in (upper_l, lower_l, palm_l):
        tag(discarded, "discarded_left_arm_source", False)
        discarded.hide_render = True
        discarded.hide_set(True)

    leg_l = cylinder_between(collection, "LM_LeftLeg_short", (-0.19, 0.0, 0.49), (-0.22, -0.02, 0.22), 0.112, 0.09, mats["body_dark"], 7)
    leg_r = cylinder_between(collection, "LM_RightLeg_short", (0.19, 0.0, 0.49), (0.22, -0.02, 0.22), 0.112, 0.09, mats["body_dark"], 7)
    foot_l = rounded_box(collection, "LM_LeftFoot_soft_sneaker", (-0.31, -0.09, 0.13), (0.3, 0.22, 0.11), mats["coral"], 0.04)
    foot_r = rounded_box(collection, "LM_RightFoot_soft_sneaker", (0.31, -0.09, 0.13), (0.3, 0.22, 0.11), mats["coral"], 0.04)

    all_meshes = [
        body,
        belly,
        collar,
        cheek_l,
        cheek_r,
        eye_l,
        eye_r,
        glint_l,
        glint_r,
        mouth_a,
        mouth_b,
        mouth_c,
        antenna_stem,
        antenna_tip,
        upper_r,
        lower_r,
        right_socket,
        right_shoulder,
        elbow_r,
        palm_r,
        finger_r1,
        finger_r2,
        finger_r3,
        left_stub,
        leg_l,
        leg_r,
        foot_l,
        foot_r,
    ]

    for obj in (body, belly, collar, leg_l, leg_r, foot_l, foot_r, left_stub, right_socket):
        parent_keep_world(obj, body_pivot)
    for obj in (
        head,
    ):
        parent_keep_world(obj, head_pivot)
    for obj in (cheek_l, cheek_r, eye_l, eye_r, glint_l, glint_r, mouth_a, mouth_b, mouth_c):
        parent_keep_world(obj, body_pivot)
    for obj in (antenna_stem, antenna_tip):
        parent_keep_world(obj, antenna_pivot)
    for obj in (upper_r, lower_r, right_shoulder, elbow_r, palm_r, finger_r1, finger_r2, finger_r3):
        parent_keep_world(obj, right_arm_pivot)
    for obj in (upper_l, lower_l, palm_l):
        parent_keep_world(obj, left_arm_pivot)

    animated = [root, body_pivot, head_pivot, right_arm_pivot, left_arm_pivot, antenna_pivot, eye_l, eye_r, glint_l, glint_r]
    animate_character(root, body_pivot, head_pivot, right_arm_pivot, left_arm_pivot, antenna_pivot, eye_l, eye_r, glint_l, glint_r)
    smooth_keys(animated)

    return {
        "root": root,
        "meshes": all_meshes,
        "animated": animated,
        "pivots": [root, body_pivot, head_pivot, right_arm_pivot, antenna_pivot],
    }


def animate_character(
    root: bpy.types.Object,
    body_pivot: bpy.types.Object,
    head_pivot: bpy.types.Object,
    right_arm: bpy.types.Object,
    left_arm: bpy.types.Object,
    antenna: bpy.types.Object,
    eye_l: bpy.types.Object,
    eye_r: bpy.types.Object,
    glint_l: bpy.types.Object,
    glint_r: bpy.types.Object,
) -> None:
    for frame, z, tilt in (
        (1, 0.0, 0.0),
        (24, 0.035, math.radians(1.4)),
        (48, 0.012, math.radians(-0.8)),
        (72, 0.045, math.radians(1.1)),
        (96, 0.014, math.radians(-1.0)),
        (120, 0.0, 0.0),
    ):
        key(root, frame, loc=(0.0, 0.0, z), rot=(0.0, math.radians(0.8) * math.sin(frame / 16.0), tilt), scale=(1.0, 1.0, 1.0))

    for frame, scale_z in ((1, 1.0), (24, 1.025), (48, 0.99), (72, 1.03), (96, 0.992), (120, 1.0)):
        key(body_pivot, frame, loc=(0.0, 0.0, 1.04), rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, scale_z))

    for frame, rot_y, rot_z in (
        (1, 0.0, 0.0),
        (30, math.radians(-4.0), math.radians(2.8)),
        (60, math.radians(3.2), math.radians(-1.8)),
        (90, math.radians(-2.5), math.radians(2.2)),
        (120, 0.0, 0.0),
    ):
        key(head_pivot, frame, loc=(0.0, -0.02, 1.52), rot=(0.0, rot_y, rot_z), scale=(1.0, 1.0, 1.0))

    for frame, rot_y, rot_z in (
        (1, math.radians(-1.2), math.radians(-0.3)),
        (18, math.radians(2.6), math.radians(1.0)),
        (34, math.radians(-3.2), math.radians(-1.1)),
        (50, math.radians(3.0), math.radians(1.1)),
        (66, math.radians(-2.8), math.radians(-0.9)),
        (84, math.radians(1.0), math.radians(0.4)),
        (120, math.radians(-1.2), math.radians(-0.3)),
    ):
        key(right_arm, frame, loc=(0.405, -0.09, 1.23), rot=(0.0, rot_y, rot_z), scale=(1.0, 1.0, 1.0))

    for frame, rot_y, rot_z in (
        (1, math.radians(3.0), math.radians(-2.0)),
        (48, math.radians(0.0), math.radians(-5.0)),
        (86, math.radians(4.0), math.radians(-1.0)),
        (120, math.radians(3.0), math.radians(-2.0)),
    ):
        key(left_arm, frame, loc=(-0.47, -0.01, 1.36), rot=(0.0, rot_y, rot_z), scale=(1.0, 1.0, 1.0))

    for frame, rot_x, rot_z in (
        (1, 0.0, 0.0),
        (40, math.radians(3.0), math.radians(5.0)),
        (76, math.radians(-2.0), math.radians(-4.0)),
        (120, 0.0, 0.0),
    ):
        key(antenna, frame, loc=(0.06, -0.02, 1.72), rot=(rot_x, 0.0, rot_z), scale=(1.0, 1.0, 1.0))

    open_eye_l = (0.047, 0.018, 0.068)
    open_eye_r = (0.047, 0.018, 0.068)
    closed_eye = (0.052, 0.018, 0.01)
    glint_open = (0.013, 0.006, 0.016)
    glint_closed = (0.001, 0.001, 0.001)
    blink_frames = [1, 28, 31, 35, 78, 81, 85, 120]
    for frame in blink_frames:
        is_closed = frame in (31, 81)
        key(eye_l, frame, scale=closed_eye if is_closed else open_eye_l)
        key(eye_r, frame, scale=closed_eye if is_closed else open_eye_r)
        key(glint_l, frame, scale=glint_closed if is_closed else glint_open)
        key(glint_r, frame, scale=glint_closed if is_closed else glint_open)


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    names = {obj.name for obj in collection.all_objects}
    previous = {}
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_render, obj.hide_get())
        if obj.type in {"CAMERA", "LIGHT"} or obj.name == "LM_Preview_Floor_not_exported":
            obj.hide_render = False
            obj.hide_set(False)
            continue
        visible = obj.name in names and obj.get("abt_export", True)
        obj.hide_render = not visible
        obj.hide_set(not visible)
    return previous


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_render, hidden = previous[obj.name]
            obj.hide_set(hidden)


def render_frame(collection: bpy.types.Collection, frame: int, path: Path) -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    previous = hide_except(collection)
    try:
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"frame": frame, "path": str(path), "bytes": path.stat().st_size if path.is_file() else 0}


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def validate(collection: bpy.types.Collection) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type != "LIGHT" and obj.type != "CAMERA"]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    tris = triangle_count(meshes)
    errors = []
    warnings = []
    if not meshes:
        errors.append("No exportable meshes.")
    if tris > 25000:
        warnings.append(f"Triangle count above landing mascot target: {tris}/25000.")
    if not any(obj.animation_data for obj in exportable):
        errors.append("No animation data found on exportable hierarchy.")
    for obj in meshes:
        if any(v < 0 for v in obj.scale):
            errors.append(f"{obj.name}: negative scale.")
    return {
        "asset": ASSET,
        "target_mode": "HYBRID_HERO_FREEFORM",
        "frame_start": 1,
        "frame_end": END_FRAME,
        "fps": FPS,
        "triangles": tris,
        "mesh_objects": len(meshes),
        "exportable_objects": len(exportable),
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
    kwargs = {
        "filepath": str(path),
        "export_format": "GLB",
        "use_selection": True,
    }
    for option, value in (
        ("export_animations", True),
        ("export_frame_range", True),
        ("export_force_sampling", True),
        ("export_nla_strips", True),
        ("export_optimize_animation_size", True),
        ("export_anim_slide_to_zero", False),
    ):
        if option in props:
            kwargs[option] = value
    bpy.ops.export_scene.gltf(**kwargs)

    public_path = PUBLIC_MODELS / path.name
    shutil.copy2(path, public_path)
    return {
        "path": str(path),
        "public_path": str(public_path),
        "bytes": path.stat().st_size if path.is_file() else 0,
        "public_bytes": public_path.stat().st_size if public_path.is_file() else 0,
    }


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
        "animation_names": [animation.get("name", "") for animation in gltf.get("animations", [])],
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
    }


def write_scene_graph(parts: dict) -> dict:
    graph = {
        "asset": ASSET,
        "purpose": "simple living animated character for a landing hero",
        "target_mode": "HYBRID_HERO_FREEFORM",
        "youtube_reference_notes": [
            {
                "url": "https://www.youtube.com/watch?v=PTWV67qUX2k",
                "used_for": "low-poly character simplification, separated hard-surface style limbs, export-oriented workflow",
            },
            {
                "url": "https://www.youtube.com/watch?v=ltl4fPfuXGQ",
                "used_for": "idle-cycle idea: breathing, head drift, small personality motion",
            },
        ],
        "original_design": True,
        "parts": {
            "large_masses": ["LM_Body_beany_core", "LM_Belly_soft_front_panel"],
            "face": ["LM_Eye_left_blinking", "LM_Eye_right_blinking", "LM_Smile_center"],
            "animation_pivots": [obj.name for obj in parts["pivots"]],
            "right_wave_hand": [
                "LM_RightArm_body_socket",
                "LM_RightShoulder_overlap_cap",
                "LM_RightElbow_soft_hinge",
                "LM_RightArm_upper_segment",
                "LM_RightArm_forearm_segment",
                "LM_RightHand_mitten_palm",
            ],
            "feet": ["LM_LeftFoot_soft_sneaker", "LM_RightFoot_soft_sneaker"],
        },
        "expected_contacts": [
            "face panel overlaps body front",
            "eyes, cheeks and smile are embedded into face panel",
            "right arm socket overlaps the body front/side",
            "right shoulder remains anchored while the short arm waves",
            "arm segments overlap at shoulder/elbow/mitten",
            "legs overlap body and feet",
        ],
        "animation": {
            "name": "alive_loop_120f",
            "frames": END_FRAME,
            "fps": FPS,
            "motions": ["breathing body bob", "antenna drift", "right-hand wave", "two blinks"],
            "loop": "frame 1 and frame 120 use the same main root pose",
        },
        "acceptance": [
            "silhouette is readable at landing-page scale",
            "not a grey mannequin",
            "GLB contains animation data",
            "preview floor, camera and lights are not exported",
            "triangles under 25k",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", graph)
    return graph


def build_scene() -> dict:
    scene = setup_scene()
    collection = create_collection("LM_Output")
    parts = build_mascot(collection)
    setup_camera_and_lights(collection)
    scene_graph = write_scene_graph(parts)

    renders = [render_frame(collection, frame, RENDERS / f"{ASSET}_frame_{frame:03d}.png") for frame in PREVIEW_FRAMES]
    validation = validate(collection)

    object_names = [obj.name for obj in parts["meshes"]]
    qa = scene_qa.audit_scene(object_names=object_names, floating_tolerance=0.055) if scene_qa else {"warnings": ["scene_qa unavailable"], "errors": []}
    write_json(REPORTS / f"{ASSET}_structural_qa.json", qa)

    export = {} if validation["errors"] or qa.get("errors") else export_glb(collection)
    animation_check = glb_check(Path(export["path"])) if export else {}
    if export:
        write_json(REPORTS / f"{ASSET}_glb_animation_check.json", animation_check)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "scene": scene.name,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
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
