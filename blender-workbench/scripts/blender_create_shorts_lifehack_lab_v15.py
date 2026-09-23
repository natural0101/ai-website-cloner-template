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

ASSET = "blender_shorts_lifehack_lab_v15"
SCENE_NAME = "BlenderShortsLifehackLabV15"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-280", "name": "IK Chains Need Visible Control Proof", "applied": "IK limb has named target and pole controls plus ghost proof poses."},
    {"id": "BH-281", "name": "Constraints Need Axis And Owner Notes", "applied": "Constraint rings and chips expose owner, axis filters and influence gates."},
    {"id": "BH-282", "name": "Shape Keys Need Driver Maps", "applied": "Face board maps controller slider to blink/pupil/mirror targets."},
    {"id": "BH-283", "name": "Corrective Shapes Need Problem-Pose Snapshots", "applied": "Elbow board shows broken pose, corrective overlay and after silhouette."},
    {"id": "BH-284", "name": "Weight Transfer Needs Assumption Logs", "applied": "Transfer card shows source, target, group map and post-pose check."},
    {"id": "BH-285", "name": "Auto Weights Need Topology Preflight", "applied": "Auto-weight preflight chips mark scale, normals, loose parts and mirror names."},
    {"id": "BH-286", "name": "Armature Deform Needs Modifier QA", "applied": "Armature modifier board checks parenting, order, scale and vertex groups."},
    {"id": "BH-287", "name": "Mechanical Rigs Need Pivot Markers", "applied": "Robotic arm uses hinge pivots, axes and rigid part parenting."},
    {"id": "BH-288", "name": "Preserve Volume Is A Checkpoint", "applied": "Joint capsule compares twist collapse against preserve-volume guard."},
    {"id": "BH-289", "name": "Face And Eye Rigs Need Follow Policies", "applied": "Eye/face controls show independent aim and body-follow offset proof."},
    {"id": "BH-290", "name": "Rig Animation Cleanup Needs Action Accounting", "applied": "Action ledger separates keep, bake, delete and orphan cleanup."},
    {"id": "BH-291", "name": "Constraint Baking Needs Export Tests", "applied": "Bake gate has frame range, dependency arrow and exported motion proof."},
    {"id": "BH-292", "name": "NLA Mixing Needs Root And Foot Checks", "applied": "NLA lane shows clip overlap, root owner and footstep checks."},
    {"id": "BH-293", "name": "Motion Paths Are Timing QA", "applied": "Controller arcs show spacing and follow-through markers."},
    {"id": "BH-294", "name": "Controller Organization Prevents Animator Errors", "applied": "Control groups, selection sets and locked transforms are visible."},
    {"id": "BH-295", "name": "Clothing Deformation Needs Clipping Sweeps", "applied": "Cloth overlay has shoulder/elbow/torso sweep markers."},
    {"id": "BH-296", "name": "Symmetry Work Needs Naming Discipline", "applied": "L/R naming rail checks mirrored weights and shape keys."},
    {"id": "BH-297", "name": "Joining Rig Parts Needs Data Preservation Checks", "applied": "Join gate tracks UV, material, vertex group and normal preservation."},
    {"id": "BH-298", "name": "Neck And Head Rigs Need Isolation Switches", "applied": "Head/neck control tower shows deform/control split and isolation toggle."},
    {"id": "BH-299", "name": "Rig Export Gates Need Control Filtering", "applied": "Export funnel filters controls, helpers, constraints and baked action."},
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


def smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def make_mat(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.58,
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
            "Specular IOR Level": 0.38,
            "Coat Weight": 0.03,
            "Coat Roughness": 0.25,
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
        "base": make_mat("Lab15_BaseGraphite", (0.018, 0.022, 0.031, 1.0), roughness=0.66),
        "panel": make_mat("Lab15_PanelBlueBlack", (0.040, 0.052, 0.082, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab15_PanelPlum", (0.090, 0.050, 0.082, 1.0), roughness=0.64),
        "ink": make_mat("Lab15_InkDark", (0.010, 0.012, 0.018, 1.0), roughness=0.72),
        "white": make_mat("Lab15_LabelWhite", (0.92, 0.96, 1.0, 1.0), roughness=0.54),
        "cyan": make_mat("Lab15_ControlCyan", (0.02, 0.76, 0.96, 1.0), roughness=0.34, emission=(0.0, 0.28, 0.55, 1.0), emission_strength=0.12),
        "green": make_mat("Lab15_CheckGreen", (0.12, 0.78, 0.38, 1.0), roughness=0.48),
        "gold": make_mat("Lab15_PivotGold", (1.0, 0.70, 0.18, 1.0), roughness=0.42, metallic=0.04),
        "magenta": make_mat("Lab15_DriverMagenta", (1.0, 0.12, 0.56, 1.0), roughness=0.38, emission=(0.34, 0.0, 0.18, 1.0), emission_strength=0.08),
        "orange": make_mat("Lab15_BakeOrange", (0.96, 0.43, 0.10, 1.0), roughness=0.44),
        "red": make_mat("Lab15_WarningRed", (0.95, 0.09, 0.07, 1.0), roughness=0.36, emission=(0.42, 0.02, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab15_RigViolet", (0.50, 0.25, 0.86, 1.0), roughness=0.46),
        "blue": make_mat("Lab15_DeformBlue", (0.11, 0.36, 0.90, 1.0), roughness=0.48),
        "ghost": make_mat("Lab15_GhostAlpha", (0.58, 0.78, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "cloth": make_mat("Lab15_ClothTealAlpha", (0.03, 0.84, 0.70, 1.0), roughness=0.45, alpha=0.45),
    }


def rounded_box(
    name: str,
    scale: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.025,
    role: str = "box",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    apply_transform(obj)
    if bevel > 0:
        mod = obj.modifiers.new(f"{name}_Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.affect = "EDGES"
        obj.modifiers.new(f"{name}_WeightedNormals", "WEIGHTED_NORMAL")
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def cyl_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    vertices: int = 18,
    role: str = "link",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    mid = (a + b) * 0.5
    length = (b - a).length
    if length == 0:
        length = 0.001
    direction = b - a
    rotation = direction.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=mid, rotation=rotation)
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
    vertices: int = 24,
    role: str = "arrow_head",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    mid = (a + b) * 0.5
    length = (b - a).length
    direction = b - a
    rotation = direction.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=length, location=mid, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def sphere(
    name: str,
    loc: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    segments: int = 24,
    role: str = "sphere",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(8, segments // 2), radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def torus(
    name: str,
    loc: tuple[float, float, float],
    major: float,
    minor: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (math.pi / 2, 0, 0),
    role: str = "control_ring",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


def add_text(
    name: str,
    text: str,
    loc: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    align: str = "CENTER",
    role: str = "preview_label",
    export: bool = False,
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(63), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.006
    obj.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    return tag(obj, role, export)


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
        cyl_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, mat, role=role, bh=bh),
        cone_between(f"{name}_Head", tuple(mid), tuple(b), radius * 3.0, 0.0, mat, role=role, bh=bh),
    ]


def arc_segments(
    name: str,
    center: tuple[float, float, float],
    radius: float,
    start_deg: float,
    end_deg: float,
    segments: int,
    mat: bpy.types.Material,
    role: str,
    bh: str,
    y_offset: float = 0.0,
) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    cx, cy, cz = center
    angles = [math.radians(start_deg + (end_deg - start_deg) * i / segments) for i in range(segments + 1)]
    for index in range(segments):
        a = angles[index]
        b = angles[index + 1]
        start = (cx + math.cos(a) * radius, cy + y_offset, cz + math.sin(a) * radius)
        end = (cx + math.cos(b) * radius, cy + y_offset, cz + math.sin(b) * radius)
        objects.append(cyl_between(f"{name}_{index:02d}", start, end, 0.005, mat, vertices=10, role=role, bh=bh))
    return objects


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
    scene.world = scene.world or bpy.data.worlds.new("LAB15_World")
    scene.world.color = (0.014, 0.016, 0.026)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.8, -5.4, 4.9))
    key = bpy.context.object
    key.name = "LAB15_KeyArea_Warm"
    key.data.energy = 760
    key.data.size = 5.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.0, 2.8, 3.4))
    fill = bpy.context.object
    fill.name = "LAB15_FillArea_Cool"
    fill.data.energy = 145
    fill.data.size = 5.8
    fill.data.color = (0.58, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.0, 3.7, 2.8))
    rim = bpy.context.object
    rim.name = "LAB15_RimPoint_Cyan"
    rim.data.energy = 300
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.35, -5.65, 3.45), rotation=(math.radians(58), 0, math.radians(39)))
    cam = bpy.context.object
    cam.name = "LAB15_Camera_Hero3Q"
    cam.data.lens = 38
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 7.0
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def make_root() -> bpy.types.Object:
    root = bpy.data.objects.new("LAB15_Root_TurntableAnimated", None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.65
    tag(root, "rig_export_control_filtering", export=True, bh="BH-299")
    for frame, angle in ((1, -4), (48, 14), (96, 356)):
        bpy.context.scene.frame_set(frame)
        root.rotation_euler = (0, 0, math.radians(angle))
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    return root


def add_panel(
    mats: dict[str, bpy.types.Material],
    name: str,
    title: str,
    loc: tuple[float, float, float],
    size: tuple[float, float, float],
    mat_key: str,
    title_color: str = "white",
) -> bpy.types.Object:
    panel = rounded_box(name, size, loc, mats[mat_key], 0.035, role="lab_panel", export=True)
    add_text(f"{name}_Title", title, (loc[0], loc[1] - 0.065, loc[2] + size[2] * 0.42), 0.070, mats[title_color])
    return panel


def build_ik_constraints_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB15_IKPanel_Backplate", "IK / CONSTRAINT PROOF", (-1.95, 0.06, 1.02), (1.35, 0.08, 1.05), "panel")
    shoulder = (-2.35, -0.02, 1.18)
    elbow = (-2.03, -0.04, 0.88)
    wrist = (-1.65, -0.02, 1.06)
    pole = (-2.16, -0.26, 1.36)
    target = (-1.47, -0.06, 1.24)
    parts.append(sphere("LAB15_IK_Shoulder_Joint", shoulder, 0.055, mats["gold"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(sphere("LAB15_IK_Elbow_Joint", elbow, 0.052, mats["gold"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(sphere("LAB15_IK_Wrist_Joint", wrist, 0.052, mats["gold"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(cyl_between("LAB15_IK_UpperBone_Deform", shoulder, elbow, 0.032, mats["blue"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(cyl_between("LAB15_IK_LowerBone_Deform", elbow, wrist, 0.030, mats["blue"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(cyl_between("LAB15_IK_GhostUpper_ProofPose", (-2.35, 0.06, 1.18), (-2.02, 0.04, 1.02), 0.018, mats["ghost"], role="ik_visible_control_proof", bh="BH-280"))
    parts.append(cyl_between("LAB15_IK_GhostLower_ProofPose", (-2.02, 0.04, 1.02), (-1.62, 0.06, 0.90), 0.018, mats["ghost"], role="ik_visible_control_proof", bh="BH-280"))
    ctrl = torus("LAB15_IK_Target_Control_Animated", target, 0.090, 0.008, mats["cyan"], role="ik_visible_control_proof", bh="BH-280")
    pole_obj = sphere("LAB15_IK_Pole_Control_Named", pole, 0.040, mats["magenta"], role="ik_visible_control_proof", bh="BH-280")
    parts.extend([ctrl, pole_obj])
    parts.extend(arrow("LAB15_IK_TargetArrow", wrist, target, mats["cyan"], radius=0.008, role="ik_visible_control_proof", bh="BH-280"))
    parts.extend(arrow("LAB15_IK_PoleArrow", elbow, pole, mats["magenta"], radius=0.006, role="ik_visible_control_proof", bh="BH-280"))
    parts.extend(arc_segments("LAB15_IK_MotionPathArc", (-2.02, -0.04, 1.08), 0.38, 205, 315, 10, mats["green"], "motion_path_timing_qa", "BH-293"))
    for frame, dz in ((1, -0.04), (48, 0.12), (96, -0.04)):
        bpy.context.scene.frame_set(frame)
        ctrl.location = (target[0], target[1], target[2] + dz)
        ctrl.keyframe_insert(data_path="location", frame=frame)
    limit_ring = torus("LAB15_Constraint_LimitRotation_AxisRing", (-2.03, -0.07, 0.88), 0.155, 0.006, mats["orange"], role="constraint_axis_owner_notes", bh="BH-281")
    copy_chip = rounded_box("LAB15_Constraint_CopyRotationOwnerChip", (0.29, 0.026, 0.055), (-1.62, -0.075, 0.80), mats["orange"], 0.008, role="constraint_axis_owner_notes", bh="BH-281")
    damped_chip = rounded_box("LAB15_Constraint_DampedTrackOwnerChip", (0.29, 0.026, 0.055), (-2.32, -0.075, 0.80), mats["orange"], 0.008, role="constraint_axis_owner_notes", bh="BH-281")
    parts.extend([limit_ring, copy_chip, damped_chip])
    add_text("LAB15_IKChip_Target", "target + pole", (-1.54, -0.095, 1.40), 0.042, mats["cyan"])
    add_text("LAB15_IKChip_Axis", "axis filters", (-2.02, -0.095, 0.67), 0.040, mats["orange"])
    return parts


def build_shape_face_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB15_ShapePanel_Backplate", "SHAPE KEYS / FACE FOLLOW", (0.00, 0.07, 1.03), (1.45, 0.08, 1.05), "panel_alt")
    face = rounded_box("LAB15_FaceRig_BodyFollowPlate", (0.56, 0.045, 0.46), (-0.18, -0.02, 1.11), mats["ink"], 0.05, role="face_eye_follow_policy", bh="BH-289")
    parts.append(face)
    parts.append(torus("LAB15_EyeRig_LimitLocation_LeftEye", (-0.34, -0.062, 1.18), 0.080, 0.006, mats["white"], role="face_eye_follow_policy", bh="BH-289"))
    parts.append(torus("LAB15_EyeRig_LimitLocation_RightEye", (-0.02, -0.062, 1.18), 0.080, 0.006, mats["white"], role="face_eye_follow_policy", bh="BH-289"))
    parts.append(sphere("LAB15_EyeRig_LeftPupil_AimControl", (-0.31, -0.085, 1.18), 0.030, mats["cyan"], segments=16, role="face_eye_follow_policy", bh="BH-289"))
    parts.append(sphere("LAB15_EyeRig_RightPupil_AimControl", (0.01, -0.085, 1.18), 0.030, mats["cyan"], segments=16, role="face_eye_follow_policy", bh="BH-289"))
    parts.append(rounded_box("LAB15_ShapeKey_BlinkLeft_Delta", (0.19, 0.026, 0.028), (-0.34, -0.094, 1.25), mats["magenta"], 0.010, role="shape_key_driver_map", bh="BH-282"))
    parts.append(rounded_box("LAB15_ShapeKey_BlinkRight_Delta", (0.19, 0.026, 0.028), (-0.02, -0.094, 1.25), mats["magenta"], 0.010, role="shape_key_driver_map", bh="BH-282"))
    rail = cyl_between("LAB15_ShapeKeyDriver_Rail_MinMax", (0.34, -0.06, 0.88), (0.34, -0.06, 1.34), 0.009, mats["white"], role="shape_key_driver_map", bh="BH-282")
    knob = sphere("LAB15_ShapeKeyDriver_DebugSlider", (0.34, -0.08, 1.00), 0.042, mats["magenta"], role="shape_key_driver_map", bh="BH-282")
    parts.extend([rail, knob])
    for frame, z in ((1, 0.95), (48, 1.27), (96, 0.95)):
        bpy.context.scene.frame_set(frame)
        knob.location = (0.34, -0.08, z)
        knob.keyframe_insert(data_path="location", frame=frame)
    parts.extend(arrow("LAB15_DriverMap_SliderToBlink", (0.29, -0.08, 1.18), (0.05, -0.08, 1.23), mats["magenta"], radius=0.006, role="shape_key_driver_map", bh="BH-282"))
    parts.append(cyl_between("LAB15_Symmetry_NameRail_L_to_R", (-0.52, -0.07, 0.82), (0.18, -0.07, 0.82), 0.008, mats["gold"], role="symmetry_naming_discipline", bh="BH-296"))
    parts.append(sphere("LAB15_Symmetry_LeftNameDot", (-0.52, -0.08, 0.82), 0.032, mats["gold"], segments=16, role="symmetry_naming_discipline", bh="BH-296"))
    parts.append(sphere("LAB15_Symmetry_RightNameDot", (0.18, -0.08, 0.82), 0.032, mats["gold"], segments=16, role="symmetry_naming_discipline", bh="BH-296"))
    parts.append(rounded_box("LAB15_FaceFollow_ChildOfOffsetProof", (-0.01, 0.01, 0.01), (0, 0, 0), mats["cyan"], 0.004, role="face_eye_follow_policy", bh="BH-289"))
    parts[-1].dimensions = (0.27, 0.026, 0.070)
    parts[-1].location = (0.03, -0.085, 0.74)
    apply_transform(parts[-1])
    add_text("LAB15_ShapeChip_DriverMap", "driver map", (0.40, -0.095, 1.43), 0.040, mats["magenta"])
    add_text("LAB15_ShapeChip_FollowBody", "follow offset", (-0.12, -0.095, 0.67), 0.038, mats["cyan"])
    return parts


def build_deformation_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB15_DeformPanel_Backplate", "DEFORM / WEIGHT QA", (1.93, 0.06, 1.02), (1.42, 0.08, 1.05), "panel")
    shoulder = (1.50, -0.02, 1.22)
    elbow = (1.82, -0.04, 0.98)
    wrist = (2.28, -0.02, 1.07)
    parts.append(cyl_between("LAB15_Corrective_BrokenUpperGhost", shoulder, elbow, 0.034, mats["ghost"], role="corrective_problem_pose_snapshot", bh="BH-283"))
    parts.append(cyl_between("LAB15_Corrective_BrokenLowerGhost", elbow, wrist, 0.030, mats["ghost"], role="corrective_problem_pose_snapshot", bh="BH-283"))
    parts.append(cyl_between("LAB15_Corrective_AfterUpperSilhouette", (1.50, -0.09, 1.22), (1.82, -0.09, 1.05), 0.026, mats["green"], role="corrective_problem_pose_snapshot", bh="BH-283"))
    parts.append(cyl_between("LAB15_Corrective_AfterLowerSilhouette", (1.82, -0.09, 1.05), (2.26, -0.09, 1.20), 0.024, mats["green"], role="corrective_problem_pose_snapshot", bh="BH-283"))
    parts.append(torus("LAB15_PreserveVolume_JointCapsuleGuard", elbow, 0.128, 0.010, mats["violet"], role="preserve_volume_joint_qa", bh="BH-288"))
    for index, (x, color_key, group) in enumerate([(1.47, "blue", "SRC"), (1.70, "green", "GROUP"), (1.93, "orange", "TARGET"), (2.16, "magenta", "POSE")]):
        chip = rounded_box(f"LAB15_WeightTransfer_AssumptionChip_{group}", (0.18, 0.030, 0.075), (x, -0.075, 0.73), mats[color_key], 0.010, role="weight_transfer_assumption_log", bh="BH-284")
        parts.append(chip)
        if index < 3:
            parts.extend(arrow(f"LAB15_WeightTransfer_Arrow_{index}", (x + 0.08, -0.08, 0.73), (x + 0.18, -0.08, 0.73), mats["white"], radius=0.004, role="weight_transfer_assumption_log", bh="BH-284"))
    for index, label in enumerate(["scale", "normals", "loose", "mirror"]):
        x = 1.45 + index * 0.22
        parts.append(sphere(f"LAB15_AutoWeights_Preflight_{label}", (x, -0.078, 1.43), 0.035, mats["gold"], segments=16, role="auto_weights_topology_preflight", bh="BH-285"))
    parts.append(rounded_box("LAB15_ArmatureModifier_OrderStack", (0.62, 0.030, 0.095), (2.18, -0.078, 1.40), mats["blue"], 0.014, role="armature_modifier_qa", bh="BH-286"))
    parts.append(rounded_box("LAB15_Clothing_TransparentSweep_Overlay", (0.50, 0.026, 0.30), (2.22, -0.105, 0.93), mats["cloth"], 0.040, role="clothing_clipping_sweep", bh="BH-295"))
    for z in (0.82, 0.94, 1.06):
        parts.append(cyl_between(f"LAB15_Clothing_ClipSweep_{z:.2f}", (2.00, -0.125, z), (2.46, -0.125, z + 0.03), 0.006, mats["red"], vertices=10, role="clothing_clipping_sweep", bh="BH-295"))
    parts.append(rounded_box("LAB15_JoinParts_DataPreservationGate", (0.50, 0.030, 0.080), (1.58, -0.085, 0.88), mats["orange"], 0.012, role="join_parts_data_preservation", bh="BH-297"))
    add_text("LAB15_DeformChip_Corrective", "problem pose -> corrective", (1.92, -0.095, 1.56), 0.038, mats["green"])
    add_text("LAB15_DeformChip_Preflight", "scale normals loose mirror", (1.74, -0.095, 1.35), 0.033, mats["gold"])
    return parts


def build_mechanical_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB15_MechPanel_Backplate", "MECHANICAL RIG", (-1.70, 0.08, 0.16), (1.28, 0.08, 0.58), "panel_alt")
    base = (-2.05, -0.02, 0.18)
    hinge_a = (-1.82, -0.04, 0.38)
    hinge_b = (-1.42, -0.04, 0.23)
    tip = (-1.22, -0.04, 0.42)
    parts.append(sphere("LAB15_Mechanical_BasePivotMarker", base, 0.050, mats["gold"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(sphere("LAB15_Mechanical_HingeA_PivotMarker", hinge_a, 0.048, mats["gold"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(sphere("LAB15_Mechanical_HingeB_PivotMarker", hinge_b, 0.046, mats["gold"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(cyl_between("LAB15_Mechanical_RigidPart_A", base, hinge_a, 0.036, mats["cyan"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(cyl_between("LAB15_Mechanical_RigidPart_B", hinge_a, hinge_b, 0.032, mats["cyan"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(cyl_between("LAB15_Mechanical_RigidPart_C", hinge_b, tip, 0.030, mats["cyan"], role="mechanical_pivot_markers", bh="BH-287"))
    parts.append(cyl_between("LAB15_Piston_DampedTrackRod", (-2.05, -0.10, 0.10), (-1.42, -0.10, 0.23), 0.014, mats["orange"], vertices=14, role="constraint_axis_owner_notes", bh="BH-281"))
    parts.append(torus("LAB15_Mechanical_LimitRotation_StopArc", hinge_a, 0.17, 0.006, mats["orange"], role="constraint_axis_owner_notes", bh="BH-281"))
    parts.extend(arc_segments("LAB15_Mechanical_MotionPath_KeyArc", hinge_b, 0.23, 5, 80, 7, mats["green"], "motion_path_timing_qa", "BH-293"))
    add_text("LAB15_MechChip_Pivot", "pivots + hinge axes", (-1.70, -0.095, 0.56), 0.037, mats["gold"])
    return parts


def build_animation_export_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB15_AnimPanel_Backplate", "NLA / BAKE / EXPORT", (0.87, 0.08, 0.16), (2.50, 0.08, 0.58), "panel")
    for index, (name, color_key, role, bh) in enumerate([
        ("KEEP", "green", "animation_action_accounting", "BH-290"),
        ("BAKE", "orange", "constraint_baking_export_test", "BH-291"),
        ("DELETE", "red", "animation_action_accounting", "BH-290"),
        ("ORPHAN", "violet", "animation_action_accounting", "BH-290"),
    ]):
        x = -0.12 + index * 0.28
        parts.append(rounded_box(f"LAB15_ActionLedger_{name}", (0.22, 0.030, 0.070), (x, -0.07, 0.36), mats[color_key], 0.012, role=role, bh=bh))
    for index, color_key in enumerate(["blue", "magenta", "green"]):
        x = 0.90 + index * 0.34
        parts.append(rounded_box(f"LAB15_NLA_ClipLane_{index+1}", (0.42, 0.028, 0.060), (x, -0.072, 0.44 - index * 0.09), mats[color_key], 0.012, role="nla_root_foot_checks", bh="BH-292"))
    root_owner = rounded_box("LAB15_RootMotion_Owner_Animated", (0.18, 0.034, 0.11), (0.78, -0.095, 0.09), mats["gold"], 0.018, role="nla_root_foot_checks", bh="BH-292")
    parts.append(root_owner)
    for frame, x in ((1, 0.62), (48, 1.05), (96, 1.45)):
        bpy.context.scene.frame_set(frame)
        root_owner.location = (x, -0.095, 0.09)
        root_owner.keyframe_insert(data_path="location", frame=frame)
    for step, x in enumerate([0.66, 0.88, 1.12, 1.36]):
        parts.append(sphere(f"LAB15_Footstep_Check_{step+1}", (x, -0.105, 0.20 + (step % 2) * 0.08), 0.030, mats["white"], segments=14, role="nla_root_foot_checks", bh="BH-292"))
    bake_gate = torus("LAB15_BakeGate_Animated", (1.64, -0.07, 0.18), 0.105, 0.008, mats["orange"], role="constraint_baking_export_test", bh="BH-291")
    parts.append(bake_gate)
    for frame, rot in ((1, 0), (48, 80), (96, 0)):
        bpy.context.scene.frame_set(frame)
        bake_gate.rotation_euler = (math.pi / 2, 0, math.radians(rot))
        bake_gate.keyframe_insert(data_path="rotation_euler", frame=frame)
    for index, (label, color_key) in enumerate([("CTRL", "cyan"), ("HELP", "violet"), ("CONS", "orange"), ("BAKE", "green")]):
        x = 1.88 + index * 0.17
        parts.append(rounded_box(f"LAB15_ExportFilter_{label}", (0.13, 0.030, 0.070), (x, -0.075, 0.35), mats[color_key], 0.010, role="rig_export_control_filtering", bh="BH-299"))
    parts.extend(arrow("LAB15_ExportGate_FilterArrow", (1.85, -0.08, 0.20), (2.46, -0.08, 0.20), mats["green"], radius=0.006, role="rig_export_control_filtering", bh="BH-299"))
    for index, color_key in enumerate(["cyan", "green", "magenta"]):
        parts.append(torus(f"LAB15_ControllerGroup_SelectionSet_{index+1}", (0.28 + index * 0.21, -0.075, 0.10), 0.050, 0.005, mats[color_key], role="controller_organization", bh="BH-294"))
    parts.append(rounded_box("LAB15_HeadNeck_IsolationSwitch_DeformControlSplit", (-0.01, 0.01, 0.01), (0, 0, 0), mats["violet"], 0.010, role="neck_head_isolation_switches", bh="BH-298"))
    parts[-1].dimensions = (0.27, 0.030, 0.145)
    parts[-1].location = (0.18, -0.080, 0.47)
    apply_transform(parts[-1])
    add_text("LAB15_AnimChip_Actions", "actions / NLA / root", (0.72, -0.095, 0.58), 0.036, mats["white"])
    add_text("LAB15_AnimChip_Export", "filter helpers before GLB", (2.12, -0.095, 0.58), 0.035, mats["green"])
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    setup_lights()
    setup_camera()
    root = make_root()
    objects: list[bpy.types.Object] = []
    objects.append(rounded_box("LAB15_BaseRigQAStage", (4.65, 0.13, 1.82), (0.0, 0.13, 0.74), mats["base"], 0.055, role="stage_base", export=True))
    objects.append(rounded_box("LAB15_RigExport_FilterManifestRoot", (0.42, 0.045, 0.12), (2.45, -0.065, 1.58), mats["green"], 0.015, role="rig_export_control_filtering", bh="BH-299"))
    add_text("LAB15_Title", "Blender Shorts Rigging QA Lab v15", (0.0, -0.11, 1.76), 0.095, mats["white"])
    add_text("LAB15_Subtitle", "IK  constraints  shape keys  weights  NLA  export gates", (0.0, -0.11, 1.62), 0.048, mats["cyan"])
    objects.extend(build_ik_constraints_zone(mats))
    objects.extend(build_shape_face_zone(mats))
    objects.extend(build_deformation_zone(mats))
    objects.extend(build_mechanical_zone(mats))
    objects.extend(build_animation_export_zone(mats))
    # A visible internal proof strip: every BH in this batch gets a small tick on the base.
    for index, info in enumerate(APPLIED_LIFEHACKS):
        row = index // 10
        col = index % 10
        x = -2.05 + col * 0.45
        z = -0.03 + row * 0.11
        chip = rounded_box(
            f"LAB15_AppliedTick_{info['id']}",
            (0.18, 0.025, 0.045),
            (x, -0.075, z),
            mats["green"] if row == 0 else mats["cyan"],
            0.006,
            role="applied_lifehack_tick",
            bh=info["id"],
            export=True,
        )
        objects.append(chip)
    for obj in objects:
        parent_keep_world(obj, root)
    export_names = [obj.name for obj in exportable_objects()]
    helper_names = [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False]
    return {"export_object_names": export_names, "non_exported_helper_names": helper_names}


def exportable_objects() -> list[bpy.types.Object]:
    allowed = {"MESH", "EMPTY"}
    return [obj for obj in bpy.data.objects if obj.type in allowed and bool(obj.get("abt_export", True))]


def mesh_triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != "MESH":
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        if mesh:
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            eval_obj.to_mesh_clear()
    return total


def validate_scene() -> dict:
    objects = exportable_objects()
    meshes = [obj for obj in objects if obj.type == "MESH"]
    triangles = mesh_triangle_count(objects)
    errors: list[str] = []
    warnings: list[str] = []
    if triangles > 50000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 50000.")
    roles = sorted({str(obj.get("role")) for obj in objects if obj.get("role")})
    required_roles = {
        "ik_visible_control_proof",
        "constraint_axis_owner_notes",
        "shape_key_driver_map",
        "corrective_problem_pose_snapshot",
        "weight_transfer_assumption_log",
        "auto_weights_topology_preflight",
        "armature_modifier_qa",
        "mechanical_pivot_markers",
        "preserve_volume_joint_qa",
        "face_eye_follow_policy",
        "animation_action_accounting",
        "constraint_baking_export_test",
        "nla_root_foot_checks",
        "motion_path_timing_qa",
        "controller_organization",
        "clothing_clipping_sweep",
        "symmetry_naming_discipline",
        "join_parts_data_preservation",
        "neck_head_isolation_switches",
        "rig_export_control_filtering",
    }
    missing_roles = sorted(required_roles - set(roles))
    if missing_roles:
        errors.append(f"Missing required roles: {missing_roles}")
    for obj in meshes:
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material.")
        for vertex in obj.data.vertices:
            co = obj.matrix_world @ vertex.co
            if not all(math.isfinite(value) for value in (co.x, co.y, co.z)):
                errors.append(f"{obj.name} has non-finite coordinates.")
                break
        if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
            errors.append(f"{obj.name} has negative scale.")
    helper_names = [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False]
    animated = [obj.name for obj in objects if obj.animation_data and obj.animation_data.action]
    expected_animated = {
        "LAB15_Root_TurntableAnimated",
        "LAB15_IK_Target_Control_Animated",
        "LAB15_ShapeKeyDriver_DebugSlider",
        "LAB15_RootMotion_Owner_Animated",
        "LAB15_BakeGate_Animated",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        errors.append(f"Expected animated rig QA markers missing: {missing_anim}")
    exact_helper_leaks = sorted(set(helper_names) & {obj.name for obj in objects})
    if exact_helper_leaks:
        errors.append(f"Non-export helpers leaked into export set: {exact_helper_leaks}")
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
        "exact_helper_leaks": exact_helper_leaks,
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
        "source_goal": "850-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {
                "name": obj.name,
                "type": obj.type,
                "role": obj.get("role"),
                "lifehack": obj.get("lifehack"),
                "export": bool(obj.get("abt_export")),
            }
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "IK target, pole, constraint axis notes and motion-path arcs are visible.",
            "Shape-key driver map, face follow policy and symmetry naming checks are visible.",
            "Corrective pose, weight transfer, auto-weight preflight, armature modifier, clothing and join gates are visible.",
            "Mechanical pivots, NLA/root motion, bake gate, controller grouping and export filtering are visible.",
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
    if validation["errors"] or validation["warnings"]:
        raise RuntimeError(f"Validation failed: errors={validation['errors']} warnings={validation['warnings']}")
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
