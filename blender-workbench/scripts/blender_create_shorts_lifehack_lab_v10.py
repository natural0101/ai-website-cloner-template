from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

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
PUBLIC_MODELS = REPO / "public" / "models"

ASSET = "blender_shorts_lifehack_lab_v10"
SCENE_NAME = "BlenderShortsLifehackLabV10"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-186", "name": "IK Needs Named Targets And Poles", "applied": "IK board names target, pole, chain and pole-angle markers."},
    {"id": "BH-187", "name": "Mechanical Rigs Need Locked Axes", "applied": "Mechanical hinge board shows locked axes, pivot hierarchy and limit arcs."},
    {"id": "BH-188", "name": "Constraint Motion Needs A Bake Gate", "applied": "Constraint bake gate shows driven motion before/after keyframe bake."},
    {"id": "BH-189", "name": "Held Props Need Constraint Handoff QA", "applied": "Held prop board marks grab, hold and release influence handoff."},
    {"id": "BH-190", "name": "Weights Need Pose-Based Proof", "applied": "Weight board shows transfer/mirror states and pose proof chips."},
    {"id": "BH-191", "name": "Foot IK Needs Contact Semantics", "applied": "Foot IK board shows planted contact, heel and toe pivot controls."},
    {"id": "BH-192", "name": "Root Motion Needs Export Separation", "applied": "Root-motion strip separates moving root from in-place body cycle."},
    {"id": "BH-193", "name": "Tail And Secondary Rigs Need Follow Order", "applied": "Tail/follow board numbers parent-space and controller order."},
    {"id": "BH-194", "name": "Drivers Need Named Variables And Ranges", "applied": "Driver board exposes variable names, ranges and gear ratio direction."},
    {"id": "BH-195", "name": "Loop Helpers Need First Last Match", "applied": "Loop board compares first/last frames and cyclic range guards."},
    {"id": "BH-196", "name": "Curve Cables Need Anchors", "applied": "Cable board uses named hook anchors and direction markers."},
    {"id": "BH-197", "name": "Linked Rigs Need Edit Policy", "applied": "Linked-rig policy chip records source link versus override branch."},
    {"id": "BH-198", "name": "Controller Rigs Need Reset Pose", "applied": "Controller board shows reset pose, handles and limit arcs."},
    {"id": "BH-199", "name": "Animation Cleanup Is Export QA", "applied": "Cleanup strip flags stale actions and intended export clips."},
    {"id": "BH-200", "name": "Deformation Modifiers Need Silhouette QA", "applied": "Deformation board compares before/after silhouette and stretch zones."},
    {"id": "BH-201", "name": "Cloth Pins Need Named Vertex Groups", "applied": "Cloth board names pin groups and animated hook anchors."},
    {"id": "BH-202", "name": "Cloth Sims Need Cache And Scale Notes", "applied": "Cloth cache board records scale, quality, collision, wind and cache state."},
    {"id": "BH-203", "name": "Secondary Physics Need Amplitude Limits", "applied": "Secondary physics board shows jiggle amplitude and pressure clamps."},
]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def tag(obj: bpy.types.Object, role: str, export: bool = True, bh: str | None = None) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    if bh:
        obj["lifehack"] = bh
    return obj


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object, location: bool = False, rotation: bool = False, scale: bool = True) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def make_mat(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.55,
    metallic: float = 0.0,
    alpha: float | None = None,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    if alpha is not None:
        color = (color[0], color[1], color[2], alpha)
        mat.blend_method = "BLEND"
        mat.show_transparent_back = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": color,
            "Roughness": roughness,
            "Metallic": metallic,
            "Alpha": color[3],
            "Specular IOR Level": 0.42,
            "Coat Weight": 0.04,
            "Coat Roughness": 0.22,
        }
        for key, value in values.items():
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def materials() -> dict[str, bpy.types.Material]:
    return {
        "base": make_mat("Lab10_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.60),
        "panel": make_mat("Lab10_PanelInk", (0.060, 0.075, 0.110, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab10_PanelSteelBlue", (0.035, 0.072, 0.108, 1.0), roughness=0.62),
        "cyan": make_mat("Lab10_ControlCyan", (0.02, 0.80, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.32, 0.78, 1.0), emission_strength=0.13),
        "green": make_mat("Lab10_DeformGreen", (0.10, 0.84, 0.42, 1.0), roughness=0.46),
        "gold": make_mat("Lab10_BakeGold", (1.0, 0.70, 0.16, 1.0), roughness=0.42, metallic=0.05),
        "magenta": make_mat("Lab10_WarningMagenta", (1.0, 0.11, 0.54, 1.0), roughness=0.36, emission=(0.45, 0.0, 0.22, 1.0), emission_strength=0.12),
        "blue": make_mat("Lab10_RigBlue", (0.11, 0.42, 0.95, 1.0), roughness=0.48),
        "white": make_mat("Lab10_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
        "ghost": make_mat("Lab10_DebugGhost", (0.48, 0.70, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "skin": make_mat("Lab10_DeformSkin", (0.78, 0.54, 0.41, 1.0), roughness=0.72),
        "cloth": make_mat("Lab10_ClothIndigo", (0.19, 0.28, 0.88, 1.0), roughness=0.66),
        "metal": make_mat("Lab10_MechanicMetal", (0.62, 0.70, 0.78, 1.0), roughness=0.31, metallic=0.35),
        "red": make_mat("Lab10_ResetRed", (1.0, 0.12, 0.08, 1.0), roughness=0.35, emission=(0.54, 0.02, 0.02, 1.0), emission_strength=0.10),
        "dark": make_mat("Lab10_DarkSocket", (0.015, 0.018, 0.025, 1.0), roughness=0.68),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB10_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.02,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "rounded_box",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB10_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB10_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export, bh)


def sphere(
    name: str,
    radius: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    segments: int = 14,
    ring_count: int = 7,
    scale: tuple[float, float, float] = (1, 1, 1),
    role: str = "sphere",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transform(obj)
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    vertices: int = 16,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "cylinder",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def torus(
    name: str,
    major: float,
    minor: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "ring",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=42, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def cone_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius1: float,
    radius2: float,
    mat: bpy.types.Material,
    vertices: int = 14,
    role: str = "cone_between",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    loc = a + direction * 0.5
    rot = direction.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=direction.length, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def arrow(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    mat: bpy.types.Material,
    radius: float = 0.010,
    role: str = "direction_arrow",
    bh: str | None = None,
) -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    mid = a.lerp(b, 0.78)
    return [
        cone_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, radius, mat, role=role, bh=bh),
        cone_between(f"{name}_Head", tuple(mid), tuple(b), radius * 2.8, 0.0, mat, role=role, bh=bh),
    ]


def curve_line(
    name: str,
    pts: list[tuple[float, float, float]],
    mat: bpy.types.Material,
    bevel: float = 0.008,
    role: str = "curve_line",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(pts) - 1)
    for p, co in zip(spline.points, pts):
        p.co = (co[0], co[1], co[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return tag(obj, role, export, bh)


def add_text(name: str, text: str, loc: tuple[float, float, float], size: float, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(63), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.006
    obj.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    return tag(obj, "preview_label", export=False)


def setup_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 96
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.world = scene.world or bpy.data.worlds.new("LAB10_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.3, -4.9, 4.8))
    key = bpy.context.object
    key.name = "LAB10_KeyArea_Warm"
    key.data.energy = 640
    key.data.size = 5.1
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.0, 2.7, 3.2))
    fill = bpy.context.object
    fill.name = "LAB10_FillArea_Cool"
    fill.data.energy = 130
    fill.data.size = 5.3
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.8, 3.1, 2.5))
    rim = bpy.context.object
    rim.name = "LAB10_RimPoint_Cyan"
    rim.data.energy = 240
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.8, -5.9, 3.55), rotation=(math.radians(58), 0, math.radians(41)))
    cam = bpy.context.object
    cam.name = "LAB10_Camera_Hero3Q"
    cam.data.lens = 34
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 10.0
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def linearize(obj: bpy.types.Object) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    fcurves = getattr(action, "fcurves", None)
    if not fcurves:
        return
    for curve in fcurves:
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"


def create_ik_mechanical_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB10_IKMechanicalConstraintBoard", (1.80, 0.08, 1.02), (-1.35, -0.82, 0.55), mats["panel"], 0.025, role="rig_lab_panel")
    parts.append(panel)

    joints = [(-1.96, -0.91, 0.30), (-1.76, -0.91, 0.56), (-1.48, -0.91, 0.62)]
    for i, loc in enumerate(joints):
        parts.append(sphere(f"LAB10_IKChainJoint_{i}", 0.042, loc, mats["blue"], role="ik_target_pole", bh="BH-186"))
    for i in range(len(joints) - 1):
        parts.append(cone_between(f"LAB10_IKChainBone_{i}", joints[i], joints[i + 1], 0.020, 0.020, mats["cyan"], role="ik_target_pole", bh="BH-186"))
    target = rounded_box("LAB10_IKTarget_CTRL_Named", (0.13, 0.040, 0.13), (-1.28, -0.91, 0.68), mats["green"], 0.008, role="ik_target_pole", bh="BH-186")
    target["chain_length"] = 2
    pole = sphere("LAB10_IKPole_CTRL_Named", 0.032, (-1.62, -1.02, 0.84), mats["magenta"], role="ik_target_pole", bh="BH-186")
    pole["pole_angle_degrees"] = -90
    parts.extend([target, pole])
    parts.extend(arrow("LAB10_IKPoleDirectionVector", (-1.70, -0.95, 0.66), (-1.62, -1.02, 0.82), mats["magenta"], radius=0.006, role="ik_target_pole", bh="BH-186"))

    hinge_a = sphere("LAB10_MechRootPivotLockedAxis", 0.055, (-1.10, -0.91, 0.33), mats["gold"], role="mechanical_locked_axis", bh="BH-187")
    hinge_b = sphere("LAB10_MechElbowPivotLockedAxis", 0.055, (-0.85, -0.91, 0.56), mats["gold"], role="mechanical_locked_axis", bh="BH-187")
    rod_a = cone_between("LAB10_MechUpperLink_LengthPreserved", (-1.10, -0.91, 0.33), (-0.85, -0.91, 0.56), 0.028, 0.028, mats["metal"], role="mechanical_locked_axis", bh="BH-187")
    rod_b = cone_between("LAB10_MechLowerLink_LengthPreserved", (-0.85, -0.91, 0.56), (-0.58, -0.91, 0.40), 0.028, 0.028, mats["metal"], role="mechanical_locked_axis", bh="BH-187")
    axis = cylinder("LAB10_MechHingeAxis_ZLocked", 0.018, 0.18, (-0.85, -0.91, 0.56), mats["magenta"], rot=(math.radians(90), 0, 0), role="mechanical_locked_axis", bh="BH-187")
    limit_arc = torus("LAB10_MechRotationLimitArc", 0.16, 0.006, (-0.85, -0.91, 0.56), mats["cyan"], rot=(math.radians(90), 0, 0), role="mechanical_locked_axis", bh="BH-187")
    parts.extend([hinge_a, hinge_b, rod_a, rod_b, axis, limit_arc])

    gate = rounded_box("LAB10_ConstraintBakeGate_RuntimeDecision", (0.46, 0.035, 0.16), (-1.82, -0.90, 0.88), mats["gold"], 0.008, role="constraint_bake_gate", bh="BH-188")
    gate["bake_when"] = "runtime lacks Blender constraints"
    parts.append(gate)
    for i, x in enumerate((-1.55, -1.43, -1.31, -1.19)):
        key = rounded_box(f"LAB10_BakedConstraintKeyframe_{i:02d}", (0.030, 0.035, 0.11), (x, -0.90, 0.90), mats["green"], 0.004, role="constraint_bake_gate", bh="BH-188")
        key["frame"] = 1 + i * 24
        parts.append(key)

    hand = sphere("LAB10_HeldPropHandAnchor", 0.060, (-0.72, -0.91, 0.82), mats["skin"], role="held_prop_handoff", bh="BH-189")
    prop = rounded_box("LAB10_HeldProp_ChildOfInfluenceQA", (0.16, 0.050, 0.10), (-0.55, -0.91, 0.82), mats["green"], 0.010, role="held_prop_handoff", bh="BH-189")
    prop["handoff_frames"] = "grab=18 hold=48 release=72"
    parts.extend([hand, prop])
    for i, x in enumerate((-0.82, -0.66, -0.50)):
        chip = rounded_box(f"LAB10_HeldPropInfluenceMarker_{i}", (0.050, 0.035, 0.050), (x, -0.91, 0.94), [mats["red"], mats["gold"], mats["cyan"]][i], 0.006, role="held_prop_handoff", bh="BH-189")
        parts.append(chip)
    return parts


def create_weights_motion_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB10_WeightsMotionExportBoard", (1.78, 0.08, 1.02), (0.34, -0.82, 0.55), mats["panel_alt"], 0.025, role="rig_lab_panel")
    parts.append(panel)

    body = sphere("LAB10_WeightTransferPoseProofBody", 0.12, (-0.24, -0.91, 0.70), mats["skin"], scale=(0.78, 0.42, 1.22), role="weight_pose_proof", bh="BH-190")
    cloth_l = rounded_box("LAB10_WeightTransferCloth_LeftMirror", (0.13, 0.040, 0.22), (-0.42, -0.93, 0.66), mats["cloth"], 0.010, role="weight_pose_proof", bh="BH-190")
    cloth_r = rounded_box("LAB10_WeightTransferCloth_RightMirror", (0.13, 0.040, 0.22), (-0.06, -0.93, 0.66), mats["cloth"], 0.010, role="weight_pose_proof", bh="BH-190")
    parts.extend([body, cloth_l, cloth_r])
    for i, (x, mat) in enumerate(((-0.42, mats["red"]), (-0.30, mats["gold"]), (-0.18, mats["green"]), (-0.06, mats["cyan"]))):
        dot = sphere(f"LAB10_WeightInfluencePoseDot_{i}", 0.025, (x, -0.96, 0.87), mat, role="weight_pose_proof", bh="BH-190")
        parts.append(dot)

    ground = rounded_box("LAB10_FootIKGroundContactPlane", (0.56, 0.030, 0.035), (0.40, -0.94, 0.25), mats["ghost"], 0.004, role="foot_ik_contact", bh="BH-191")
    foot = rounded_box("LAB10_FootIK_PlantedFoot", (0.28, 0.060, 0.075), (0.36, -0.94, 0.34), mats["blue"], 0.010, role="foot_ik_contact", bh="BH-191")
    heel = sphere("LAB10_FootIK_HeelPivot", 0.026, (0.22, -0.96, 0.32), mats["gold"], role="foot_ik_contact", bh="BH-191")
    toe = sphere("LAB10_FootIK_ToePivot", 0.026, (0.50, -0.96, 0.32), mats["green"], role="foot_ik_contact", bh="BH-191")
    parts.extend([ground, foot, heel, toe])
    parts.extend(arrow("LAB10_FootRollLimitVector", (0.22, -0.96, 0.40), (0.50, -0.96, 0.42), mats["cyan"], radius=0.006, role="foot_ik_contact", bh="BH-191"))

    root_strip = rounded_box("LAB10_RootMotionExportStrip", (0.72, 0.030, 0.11), (-0.14, -0.91, 0.28), mats["dark"], 0.006, role="root_motion_export", bh="BH-192")
    in_place = rounded_box("LAB10_InPlaceBodyCycleClip", (0.16, 0.040, 0.09), (-0.36, -0.91, 0.29), mats["green"], 0.008, role="root_motion_export", bh="BH-192")
    moving_root = sphere("LAB10_RootMotionMovingRoot_CTRL", 0.035, (-0.02, -0.91, 0.31), mats["magenta"], role="root_motion_export", bh="BH-192")
    moving_root.keyframe_insert(data_path="location", frame=1)
    moving_root.location.x += 0.36
    moving_root.keyframe_insert(data_path="location", frame=96)
    linearize(moving_root)
    parts.extend([root_strip, in_place, moving_root])
    parts.extend(arrow("LAB10_RootForwardAxisExport", (-0.36, -0.91, 0.19), (0.46, -0.91, 0.19), mats["magenta"], radius=0.006, role="root_motion_export", bh="BH-192"))

    tail_pts = [(0.74, -0.91, 0.78), (0.88, -0.91, 0.72), (1.04, -0.91, 0.64), (1.18, -0.91, 0.50)]
    parts.append(curve_line("LAB10_TailFollowOrderSpline", tail_pts, mats["cyan"], 0.010, role="tail_follow_order", bh="BH-193"))
    for i, loc in enumerate(tail_pts):
        ctrl = sphere(f"LAB10_TailControllerOrder_{i}", 0.032, loc, [mats["blue"], mats["green"], mats["gold"], mats["magenta"]][i], role="tail_follow_order", bh="BH-193")
        ctrl["follow_order"] = i
        parts.append(ctrl)
    namespace = rounded_box("LAB10_LinkedRigEditPolicy_SourceOrOverride", (0.32, 0.035, 0.11), (0.98, -0.91, 0.25), mats["gold"], 0.008, role="linked_rig_policy", bh="BH-197")
    namespace["policy"] = "source link or library override before editing"
    parts.append(namespace)
    return parts


def create_driver_loop_cable_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB10_DriverLoopCableBoard", (1.80, 0.08, 1.02), (1.98, -0.82, 0.55), mats["panel"], 0.025, role="rig_lab_panel")
    parts.append(panel)

    for i, (name, x, mat) in enumerate((("ratio", 1.34, mats["gold"]), ("speed", 1.56, mats["green"]), ("vis", 1.78, mats["magenta"]))):
        chip = rounded_box(f"LAB10_DriverVariable_{name}", (0.15, 0.035, 0.09), (x, -0.91, 0.88), mat, 0.006, role="driver_variable_range", bh="BH-194")
        chip["variable_name"] = name
        chip["range"] = "0..1" if name == "vis" else "-10..10"
        parts.append(chip)
    gear_a = torus("LAB10_DriverGearRatio_A", 0.085, 0.010, (2.02, -0.91, 0.88), mats["metal"], rot=(math.radians(90), 0, 0), role="driver_variable_range", bh="BH-194")
    gear_b = torus("LAB10_DriverGearRatio_B_Inverted", 0.060, 0.010, (2.21, -0.91, 0.88), mats["cyan"], rot=(math.radians(90), 0, 0), role="driver_variable_range", bh="BH-194")
    gear_a["gear_ratio"] = "2:-1"
    parts.extend([gear_a, gear_b])
    gear_a.keyframe_insert(data_path="rotation_euler", frame=1)
    gear_a.rotation_euler.z = math.tau
    gear_a.keyframe_insert(data_path="rotation_euler", frame=96)
    gear_b.keyframe_insert(data_path="rotation_euler", frame=1)
    gear_b.rotation_euler.z = -math.tau * 2
    gear_b.keyframe_insert(data_path="rotation_euler", frame=96)
    linearize(gear_a)
    linearize(gear_b)

    loop_strip = rounded_box("LAB10_CyclicLoopRangeGuard", (0.82, 0.030, 0.11), (1.72, -0.91, 0.62), mats["dark"], 0.006, role="loop_first_last_match", bh="BH-195")
    first = rounded_box("LAB10_LoopFirstFramePose", (0.12, 0.040, 0.10), (1.36, -0.91, 0.63), mats["green"], 0.008, role="loop_first_last_match", bh="BH-195")
    last = rounded_box("LAB10_LoopLastFramePoseMatched", (0.12, 0.040, 0.10), (2.08, -0.91, 0.63), mats["green"], 0.008, role="loop_first_last_match", bh="BH-195")
    spring = curve_line("LAB10_BouncySpringAmplitudeDamped", [(1.50 + i * 0.055, -0.91, 0.58 + math.sin(i * 1.4) * 0.045) for i in range(10)], mats["gold"], 0.007, role="loop_first_last_match", bh="BH-195")
    parts.extend([loop_strip, first, last, spring])

    cable_pts = [(1.28, -0.91, 0.31), (1.48, -0.91, 0.40), (1.72, -0.91, 0.28), (1.98, -0.91, 0.39), (2.20, -0.91, 0.30)]
    cable = curve_line("LAB10_CurveCableHookedDirectionChecked", cable_pts, mats["cyan"], 0.010, role="curve_cable_anchor", bh="BH-196")
    parts.append(cable)
    for i, loc in enumerate((cable_pts[0], cable_pts[-1])):
        hook = sphere(f"LAB10_CableHookAnchor_{i}", 0.035, loc, mats["magenta"], role="curve_cable_anchor", bh="BH-196")
        hook["hook_anchor"] = i
        parts.append(hook)

    reset = rounded_box("LAB10_ControllerResetPoseBoard", (0.44, 0.035, 0.16), (2.28, -0.91, 0.50), mats["ghost"], 0.008, role="controller_reset_pose", bh="BH-198")
    reset["reset_pose"] = "all controls zeroed"
    parts.append(reset)
    parts.extend(arrow("LAB10_ControllerLimitArcVector", (2.16, -0.91, 0.48), (2.38, -0.91, 0.60), mats["gold"], radius=0.006, role="controller_reset_pose", bh="BH-198"))

    cleanup = rounded_box("LAB10_AnimationCleanupExportQA", (0.40, 0.035, 0.10), (2.30, -0.91, 0.24), mats["red"], 0.008, role="animation_cleanup_export", bh="BH-199")
    cleanup["cleanup"] = "unused actions removed, intended clips retained"
    parts.append(cleanup)
    return parts


def create_deform_cloth_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB10_DeformClothPhysicsBoard", (3.95, 0.08, 1.12), (0.30, 0.52, 0.68), mats["panel_alt"], 0.025, role="rig_lab_panel")
    parts.append(panel)

    before = sphere("LAB10_DeformationBeforeSilhouette", 0.12, (-1.42, 0.45, 0.85), mats["skin"], scale=(0.80, 0.38, 1.10), role="deformation_silhouette_qa", bh="BH-200")
    after = sphere("LAB10_DeformationAfterSilhouetteStretchCheck", 0.12, (-1.12, 0.45, 0.85), mats["skin"], scale=(1.10, 0.34, 0.80), role="deformation_silhouette_qa", bh="BH-200")
    stretch = curve_line("LAB10_DeformationStretchWarningContour", [(-1.24, 0.42, 0.72), (-1.18, 0.42, 0.86), (-1.08, 0.42, 0.98)], mats["magenta"], 0.006, role="deformation_silhouette_qa", bh="BH-200")
    parts.extend([before, after, stretch])

    pole = cylinder("LAB10_ClothPinPole_AnimatedAnchor", 0.020, 0.62, (-0.60, 0.44, 0.72), mats["metal"], vertices=12, role="cloth_pin_group", bh="BH-201")
    parts.append(pole)
    flag_pts = [(-0.60, 0.40, 0.98), (-0.42, 0.40, 1.04), (-0.24, 0.40, 0.95), (-0.06, 0.40, 1.00)]
    flag_top = curve_line("LAB10_ClothFlagPinnedVertexGroup_Top", flag_pts, mats["cloth"], 0.014, role="cloth_pin_group", bh="BH-201")
    flag_mid = curve_line("LAB10_ClothFlagPinnedVertexGroup_Mid", [(x, y, z - 0.12) for x, y, z in flag_pts], mats["cloth"], 0.014, role="cloth_pin_group", bh="BH-201")
    pin_chip = rounded_box("LAB10_ClothPinGroup_PoleSideVertices", (0.12, 0.035, 0.26), (-0.60, 0.40, 0.88), mats["magenta"], 0.006, role="cloth_pin_group", bh="BH-201")
    pin_chip["vertex_group"] = "PIN_pole_side"
    parts.extend([flag_top, flag_mid, pin_chip])
    for i, z in enumerate((0.74, 0.86, 0.98)):
        pin = sphere(f"LAB10_ClothPinVertex_{i}", 0.021, (-0.60, 0.37, z), mats["gold"], role="cloth_pin_group", bh="BH-201")
        parts.append(pin)

    cache_board = rounded_box("LAB10_ClothCacheScaleWindBoard", (0.78, 0.035, 0.32), (0.38, 0.43, 0.88), mats["ghost"], 0.008, role="cloth_cache_scale", bh="BH-202")
    cache_board["scale"] = "applied"
    cache_board["quality_steps"] = 8
    cache_board["collision_margin"] = 0.015
    cache_board["cache_state"] = "baked"
    parts.append(cache_board)
    for i, (name, mat) in enumerate((("scale", mats["green"]), ("steps", mats["blue"]), ("collide", mats["gold"]), ("wind", mats["cyan"]), ("cache", mats["magenta"]))):
        chip = rounded_box(f"LAB10_ClothSettingChip_{name}", (0.10, 0.035, 0.07), (0.04 + i * 0.14, 0.40, 0.78), mat, 0.006, role="cloth_cache_scale", bh="BH-202")
        parts.append(chip)
    parts.extend(arrow("LAB10_ClothWindDirectionQA", (0.06, 0.38, 1.08), (0.70, 0.38, 1.02), mats["cyan"], radius=0.006, role="cloth_cache_scale", bh="BH-202"))

    jiggle = sphere("LAB10_SecondaryJiggleAmplitudeLimited", 0.11, (1.20, 0.42, 0.90), mats["skin"], scale=(1.0, 0.75, 1.2), role="secondary_physics_limit", bh="BH-203")
    clamp = torus("LAB10_SecondaryPhysicsAmplitudeClampRing", 0.16, 0.006, (1.20, 0.42, 0.90), mats["magenta"], rot=(math.radians(90), 0, 0), role="secondary_physics_limit", bh="BH-203")
    pressure = sphere("LAB10_ClothPressureBalloonLimit", 0.08, (1.54, 0.42, 0.88), mats["gold"], scale=(1.2, 0.85, 1.0), role="secondary_physics_limit", bh="BH-203")
    pressure["pressure_limit"] = 0.45
    parts.extend([jiggle, clamp, pressure])
    jiggle.location.z -= 0.03
    jiggle.keyframe_insert(data_path="location", frame=1)
    jiggle.location.z += 0.06
    jiggle.keyframe_insert(data_path="location", frame=48)
    jiggle.location.z -= 0.06
    jiggle.keyframe_insert(data_path="location", frame=96)
    linearize(jiggle)

    policy = rounded_box("LAB10_RigExportPolicySummary", (0.58, 0.035, 0.16), (1.78, 0.42, 0.56), mats["gold"], 0.008, role="animation_cleanup_export", bh="BH-199")
    policy["export_policy"] = "bake constraints, remove stale actions, keep intended clips"
    parts.append(policy)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB10_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-186..BH-203")
    floor = rounded_box("LAB10_StudioFloor_NotExported", (5.20, 3.34, 0.065), (0.22, -0.02, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_ik_mechanical_board(mats))
    export_parts.extend(create_weights_motion_board(mats))
    export_parts.extend(create_driver_loop_cable_board(mats))
    export_parts.extend(create_deform_cloth_board(mats))
    labels = [
        add_text("LAB10_Label_IKMechanical", "IK / MECHANICAL / BAKE", (-1.35, -1.25, 1.12), 0.050, mats["white"]),
        add_text("LAB10_Label_WeightsMotion", "WEIGHTS / FOOT IK / ROOT / TAIL", (0.34, -1.25, 1.12), 0.048, mats["white"]),
        add_text("LAB10_Label_DriversLoops", "DRIVERS / LOOPS / CABLES", (1.98, -1.25, 1.12), 0.050, mats["white"]),
        add_text("LAB10_Label_DeformCloth", "DEFORMATION / CLOTH PINS / CACHE / PHYSICS LIMITS", (0.30, 0.08, 1.28), 0.046, mats["white"]),
    ]
    helper_parts.extend(labels)
    for obj in export_parts + helper_parts:
        parent_keep_world(obj, root)
    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path="rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.tau)
    root.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize(root)
    for obj in export_parts:
        if obj.name == "LAB10_MechRotationLimitArc":
            obj.rotation_euler.z = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = math.tau * 0.33
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
        if obj.name == "LAB10_SecondaryPhysicsAmplitudeClampRing":
            obj.rotation_euler.z = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = math.tau
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
    setup_lights()
    setup_camera()
    return {
        "root": root,
        "export_object_names": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is True],
        "non_exported_helper_names": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False],
    }


def exportable_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.data.objects if obj.get("abt_export") is True]


def triangle_count(obj: bpy.types.Object, depsgraph: bpy.types.Depsgraph) -> int:
    if obj.type != "MESH":
        return 0
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    try:
        return sum(len(poly.vertices) - 2 for poly in mesh.polygons)
    finally:
        eval_obj.to_mesh_clear()


def validate_scene() -> dict:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objects = exportable_objects()
    meshes = [obj for obj in objects if obj.type == "MESH"]
    errors: list[str] = []
    warnings: list[str] = []
    if not meshes:
        errors.append("No exportable mesh objects.")
    triangles = sum(triangle_count(obj, depsgraph) for obj in meshes)
    if triangles > 50000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 50000.")
    roles = sorted({str(obj.get("role")) for obj in objects if obj.get("role")})
    required_roles = {
        "ik_target_pole",
        "mechanical_locked_axis",
        "constraint_bake_gate",
        "held_prop_handoff",
        "weight_pose_proof",
        "foot_ik_contact",
        "root_motion_export",
        "tail_follow_order",
        "driver_variable_range",
        "loop_first_last_match",
        "curve_cable_anchor",
        "linked_rig_policy",
        "controller_reset_pose",
        "animation_cleanup_export",
        "deformation_silhouette_qa",
        "cloth_pin_group",
        "cloth_cache_scale",
        "secondary_physics_limit",
    }
    missing_roles = sorted(required_roles - set(roles))
    if missing_roles:
        errors.append(f"Missing required roles: {missing_roles}")
    for obj in meshes:
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material.")
        for vertex in obj.data.vertices:
            co = obj.matrix_world @ vertex.co
            if not all(math.isfinite(v) for v in (co.x, co.y, co.z)):
                errors.append(f"{obj.name} has non-finite coordinates.")
                break
        if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
            errors.append(f"{obj.name} has negative scale.")
    helper_names = [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False]
    animated = [obj.name for obj in objects if obj.animation_data and obj.animation_data.action]
    if "LAB10_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    expected_animated = {
        "LAB10_DriverGearRatio_A",
        "LAB10_DriverGearRatio_B_Inverted",
        "LAB10_RootMotionMovingRoot_CTRL",
        "LAB10_SecondaryJiggleAmplitudeLimited",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        warnings.append(f"Expected animated QA markers missing: {missing_anim}")
    return {
        "asset": ASSET,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "triangles": triangles,
        "exportable_objects": len(objects),
        "exportable_meshes": len(meshes),
        "roles": roles,
        "non_exported_helpers": helper_names,
        "animation": {
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": bpy.context.scene.render.fps,
            "animated_roots": animated,
        },
    }


def render_frame(frame: int, suffix: str) -> Path:
    scene = bpy.context.scene
    scene.frame_set(frame)
    path = RENDERS / f"{ASSET}_{suffix}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path


def export_glb(path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable_objects():
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_lights=False,
        export_cameras=False,
        export_apply=True,
    )


def main() -> None:
    build = build_scene()
    scene_graph = {
        "asset": ASSET,
        "scene": SCENE_NAME,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "icon/hero object",
        "source_goal": "600-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "lifehack": obj.get("lifehack"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "IK target/pole and mechanical locked-axis QA boards are visible.",
            "Constraint bake, held-prop handoff and weight pose proof are visible.",
            "Foot IK, root motion, tail follow, drivers, loops and cable anchors are visible.",
            "Linked-rig policy, controller reset, cleanup and deformation silhouette QA are visible.",
            "Cloth pins, cache/scale notes and secondary physics limits are visible.",
            "Validation has no errors and no warnings.",
        ],
        "export_object_names": build["export_object_names"],
        "non_exported_helper_names": build["non_exported_helper_names"],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)
    preview = render_frame(24, "preview_frame_024")
    render_frame(1, "frame_001")
    render_frame(48, "frame_048")
    render_frame(96, "frame_096")
    validation = validate_scene()
    write_json(REPORTS / f"{ASSET}_validation.json", validation)
    if validation["errors"]:
        raise RuntimeError(f"Validation failed: {validation['errors']}")
    glb = EXPORTS / f"{ASSET}.glb"
    export_glb(glb)
    (PUBLIC_MODELS / f"{ASSET}.glb").write_bytes(glb.read_bytes())
    blend = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    report = {
        "asset": ASSET,
        "preview": str(preview),
        "frames": [
            str(RENDERS / f"{ASSET}_frame_001.png"),
            str(RENDERS / f"{ASSET}_preview_frame_024.png"),
            str(RENDERS / f"{ASSET}_frame_048.png"),
            str(RENDERS / f"{ASSET}_frame_096.png"),
        ],
        "glb": str(glb),
        "public_glb": str(PUBLIC_MODELS / f"{ASSET}.glb"),
        "blend": str(blend),
        "validation": validation,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
