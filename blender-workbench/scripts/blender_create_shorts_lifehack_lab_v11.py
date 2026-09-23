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

ASSET = "blender_shorts_lifehack_lab_v11"
SCENE_NAME = "BlenderShortsLifehackLabV11"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-204", "name": "Viewport Compositing Needs Final Parity", "applied": "Viewport/final compositor cards share pass and color-management markers."},
    {"id": "BH-205", "name": "Glow Needs Threshold Control", "applied": "Glow board exposes emission strength, threshold and clipping meter."},
    {"id": "BH-206", "name": "Camera Shake Needs Limits", "applied": "Shake rig shows amplitude/frequency rails and a steady reference marker."},
    {"id": "BH-207", "name": "Tracking Needs Solve QA", "applied": "Tracking solve board shows markers, solve-error bar, outlier chip and ground plane."},
    {"id": "BH-208", "name": "Tracking Shortcuts Need Assumptions", "applied": "Shortcut/external-tracker chips record planar, lens, scale and coordinate assumptions."},
    {"id": "BH-209", "name": "Keying Needs Matte And Spill QA", "applied": "Keying board separates source, matte, spill suppression and edge review."},
    {"id": "BH-210", "name": "Shadow Catchers Need Contact Proof", "applied": "Shadow catcher board shows alpha, contact softness and light direction."},
    {"id": "BH-211", "name": "Camera Tracking Rigs Need Framing QA", "applied": "Camera-follow board shows target naming, distance, focal length and crop frame."},
    {"id": "BH-212", "name": "Grease Pencil Needs Layer Discipline", "applied": "Grease Pencil stack names layers, materials, timing holds and camera-depth rules."},
    {"id": "BH-213", "name": "Line Art Needs Scope And Thickness QA", "applied": "Line Art board marks collection scope, depth ordering and delivery-thickness checks."},
    {"id": "BH-214", "name": "Line Boil Needs Noise Limits", "applied": "Line boil board clamps noise amplitude, speed and hold frames."},
    {"id": "BH-215", "name": "Mixed 2D And 3D Needs Shared Space", "applied": "2D/3D board shows shared camera frame, parallax layers and timing rail."},
    {"id": "BH-216", "name": "Grease Pencil Rigs Need Pose Tests", "applied": "GP rig board has controller dots and pose-test ghost strokes."},
    {"id": "BH-217", "name": "Toon Style Needs A Pass Contract", "applied": "Toon board separates material bands, outline pass, texture and grade."},
    {"id": "BH-218", "name": "Fake Reflections Need Link Logic", "applied": "Reflection board links source stroke to mirrored offset/opacity controls."},
    {"id": "BH-219", "name": "2D To 3D Conversion Needs Cleanup", "applied": "Conversion board shows source cleanup, silhouette depth and mesh validation."},
    {"id": "BH-220", "name": "VFX Shots Need Pass Accounting", "applied": "VFX pipeline board accounts for solve, AOVs, shadow, key, grade, sound and final."},
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
        "base": make_mat("Lab11_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.60),
        "panel": make_mat("Lab11_PanelInk", (0.060, 0.075, 0.110, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab11_PanelDeepTeal", (0.030, 0.080, 0.105, 1.0), roughness=0.64),
        "cyan": make_mat("Lab11_ControlCyan", (0.02, 0.80, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.32, 0.78, 1.0), emission_strength=0.13),
        "green": make_mat("Lab11_MatteGreen", (0.12, 0.86, 0.42, 1.0), roughness=0.48),
        "gold": make_mat("Lab11_ThresholdGold", (1.0, 0.70, 0.16, 1.0), roughness=0.42, metallic=0.05),
        "magenta": make_mat("Lab11_WarningMagenta", (1.0, 0.11, 0.54, 1.0), roughness=0.36, emission=(0.45, 0.0, 0.22, 1.0), emission_strength=0.12),
        "blue": make_mat("Lab11_TrackBlue", (0.11, 0.42, 0.95, 1.0), roughness=0.48),
        "white": make_mat("Lab11_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
        "ghost": make_mat("Lab11_DebugGhost", (0.48, 0.70, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "shadow": make_mat("Lab11_ShadowCatcherSoft", (0.13, 0.15, 0.18, 1.0), roughness=0.76, alpha=0.46),
        "toon": make_mat("Lab11_ToonBand", (0.96, 0.53, 0.18, 1.0), roughness=0.55),
        "ink": make_mat("Lab11_InkLine", (0.005, 0.007, 0.012, 1.0), roughness=0.70),
        "red": make_mat("Lab11_ClipRed", (1.0, 0.12, 0.08, 1.0), roughness=0.35, emission=(0.54, 0.02, 0.02, 1.0), emission_strength=0.10),
        "dark": make_mat("Lab11_DarkSocket", (0.015, 0.018, 0.025, 1.0), roughness=0.68),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB11_WeightedNormals", type="WEIGHTED_NORMAL")


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
        mod = obj.modifiers.new(name="LAB11_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB11_WeightedNormals", type="WEIGHTED_NORMAL")
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
    scene.world = scene.world or bpy.data.worlds.new("LAB11_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.4, -4.9, 4.8))
    key = bpy.context.object
    key.name = "LAB11_KeyArea_Warm"
    key.data.energy = 650
    key.data.size = 5.2
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.0, 2.7, 3.2))
    fill = bpy.context.object
    fill.name = "LAB11_FillArea_Cool"
    fill.data.energy = 135
    fill.data.size = 5.4
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.8, 3.1, 2.5))
    rim = bpy.context.object
    rim.name = "LAB11_RimPoint_Cyan"
    rim.data.energy = 245
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.9, -6.05, 3.62), rotation=(math.radians(58), 0, math.radians(41)))
    cam = bpy.context.object
    cam.name = "LAB11_Camera_Hero3Q"
    cam.data.lens = 34
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.1
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


def create_comp_tracking_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB11_CompTrackingVFXBoard", (1.90, 0.08, 1.08), (-1.28, -0.84, 0.60), mats["panel"], 0.025, role="vfx_lab_panel")
    parts.append(panel)
    for i, (name, z, mat) in enumerate((("Viewport", 0.96, mats["blue"]), ("Final", 0.80, mats["green"]))):
        card = rounded_box(f"LAB11_CompositorParity_{name}Card", (0.30, 0.040, 0.10), (-1.88, -0.90, z), mat, 0.006, role="viewport_compositor_parity", bh="BH-204")
        card["pass_stack"] = "same passes, same color management"
        parts.append(card)
    parts.extend(arrow("LAB11_ViewportToFinalParityArrow", (-1.70, -0.90, 0.88), (-1.42, -0.90, 0.88), mats["cyan"], radius=0.006, role="viewport_compositor_parity", bh="BH-204"))

    glow = sphere("LAB11_GlowEmitter_ThresholdChecked", 0.075, (-1.20, -0.92, 0.88), mats["gold"], segments=16, ring_count=8, role="glow_threshold_control", bh="BH-205")
    glow["emission_strength"] = 2.4
    glow["glare_threshold"] = 0.72
    threshold = rounded_box("LAB11_GlowThresholdMeter_NoClip", (0.34, 0.035, 0.040), (-1.02, -0.90, 0.76), mats["dark"], 0.004, role="glow_threshold_control", bh="BH-205")
    clip = rounded_box("LAB11_GlowClipWarningCap", (0.045, 0.040, 0.110), (-0.84, -0.90, 0.80), mats["red"], 0.004, role="glow_threshold_control", bh="BH-205")
    parts.extend([glow, threshold, clip])
    glow.keyframe_insert(data_path="scale", frame=1)
    glow.scale = (1.18, 1.18, 1.18)
    glow.keyframe_insert(data_path="scale", frame=48)
    glow.scale = (1.0, 1.0, 1.0)
    glow.keyframe_insert(data_path="scale", frame=96)
    linearize(glow)

    rail = rounded_box("LAB11_CameraShakeAmplitudeFrequencyRail", (0.56, 0.030, 0.070), (-1.62, -0.91, 0.56), mats["dark"], 0.004, role="camera_shake_limit", bh="BH-206")
    steady = rounded_box("LAB11_CameraShakeSteadyReferenceFrame", (0.11, 0.040, 0.10), (-1.84, -0.91, 0.58), mats["green"], 0.006, role="camera_shake_limit", bh="BH-206")
    shake = sphere("LAB11_CameraShakeLimitedMarker", 0.030, (-1.55, -0.91, 0.58), mats["magenta"], role="camera_shake_limit", bh="BH-206")
    shake["amplitude"] = 0.035
    shake["frequency"] = "low"
    shake.keyframe_insert(data_path="location", frame=1)
    shake.location.x += 0.10
    shake.keyframe_insert(data_path="location", frame=48)
    shake.location.x -= 0.10
    shake.keyframe_insert(data_path="location", frame=96)
    linearize(shake)
    parts.extend([rail, steady, shake])

    track_plane = rounded_box("LAB11_TrackingGroundPlaneAligned", (0.64, 0.030, 0.26), (-0.92, -0.91, 0.48), mats["ghost"], 0.006, role="tracking_solve_qa", bh="BH-207")
    track_plane["solve_error_px"] = 0.43
    parts.append(track_plane)
    for i, (x, z) in enumerate(((-1.18, 0.57), (-1.05, 0.43), (-0.88, 0.52), (-0.72, 0.40), (-0.60, 0.58))):
        marker = sphere(f"LAB11_TrackMarker_SolveQA_{i}", 0.024, (x, -0.94, z), mats["cyan" if i != 3 else "red"], segments=10, ring_count=5, role="tracking_solve_qa", bh="BH-207")
        marker["outlier"] = i == 3
        parts.append(marker)
    solve_bar = rounded_box("LAB11_TrackingSolveErrorBar", (0.34, 0.035, 0.038), (-0.86, -0.91, 0.70), mats["gold"], 0.004, role="tracking_solve_qa", bh="BH-207")
    parts.append(solve_bar)

    assumption_names = ("planar", "lens", "scale", "axis")
    for i, name in enumerate(assumption_names):
        chip = rounded_box(f"LAB11_TrackingShortcutAssumption_{name}", (0.12, 0.035, 0.070), (-1.80 + i * 0.16, -0.91, 0.30), [mats["blue"], mats["green"], mats["gold"], mats["magenta"]][i], 0.006, role="tracking_shortcut_assumption", bh="BH-208")
        chip["assumption"] = name
        parts.append(chip)

    green_card = rounded_box("LAB11_KeyingSourceGreenScreenPlate", (0.28, 0.035, 0.20), (-0.98, -0.91, 0.26), mats["green"], 0.006, role="keying_matte_spill", bh="BH-209")
    matte = rounded_box("LAB11_KeyingMatteCleanupEdge", (0.16, 0.040, 0.18), (-0.78, -0.91, 0.26), mats["white"], 0.006, role="keying_matte_spill", bh="BH-209")
    spill = rounded_box("LAB11_KeyingSpillSuppressionChip", (0.10, 0.040, 0.10), (-0.61, -0.91, 0.26), mats["magenta"], 0.006, role="keying_matte_spill", bh="BH-209")
    parts.extend([green_card, matte, spill])

    shadow_plane = rounded_box("LAB11_ShadowCatcherAlphaContactPlane", (0.54, 0.030, 0.18), (-1.95, -0.91, 0.12), mats["shadow"], 0.006, role="shadow_catcher_contact", bh="BH-210")
    caster = sphere("LAB11_ShadowCasterContactObject", 0.050, (-1.95, -0.93, 0.25), mats["toon"], role="shadow_catcher_contact", bh="BH-210")
    parts.extend([shadow_plane, caster])
    parts.extend(arrow("LAB11_ShadowLightDirectionMatch", (-2.16, -0.90, 0.38), (-2.00, -0.90, 0.23), mats["gold"], radius=0.006, role="shadow_catcher_contact", bh="BH-210"))

    crop = rounded_box("LAB11_CameraFollowFramingCropBox", (0.46, 0.035, 0.26), (-0.84, -0.91, 0.08), mats["ghost"], 0.006, role="camera_framing_qa", bh="BH-211")
    target = sphere("LAB11_CameraTrackTarget_Named", 0.030, (-0.84, -0.94, 0.08), mats["cyan"], role="camera_framing_qa", bh="BH-211")
    focus = rounded_box("LAB11_CameraFocalDistanceChip", (0.12, 0.035, 0.06), (-0.58, -0.91, 0.08), mats["gold"], 0.004, role="camera_framing_qa", bh="BH-211")
    parts.extend([crop, target, focus])
    return parts


def create_grease_toon_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB11_GreasePencilToonBoard", (1.92, 0.08, 1.08), (0.55, -0.84, 0.60), mats["panel_alt"], 0.025, role="vfx_lab_panel")
    parts.append(panel)

    for i, (name, mat) in enumerate((("BG", mats["blue"]), ("Ink", mats["ink"]), ("Fill", mats["toon"]), ("FX", mats["magenta"]))):
        layer = rounded_box(f"LAB11_GPLayerDiscipline_{name}", (0.44 - i * 0.035, 0.035, 0.055), (0.00 + i * 0.035, -0.91, 0.96 - i * 0.075), mat, 0.004, role="grease_pencil_layer_discipline", bh="BH-212")
        layer["layer_order"] = i
        parts.append(layer)
    for i, x in enumerate((-0.10, 0.04, 0.18, 0.32)):
        tick = rounded_box(f"LAB11_GPTimingHoldTick_{i}", (0.020, 0.035, 0.090), (x, -0.91, 0.60), mats["white"], 0.003, role="grease_pencil_layer_discipline", bh="BH-212")
        parts.append(tick)

    cube = rounded_box("LAB11_LineArtScopeObjectHero", (0.17, 0.060, 0.17), (0.72, -0.91, 0.88), mats["toon"], 0.012, role="line_art_scope_thickness", bh="BH-213")
    outline = torus("LAB11_LineArtThicknessDepthCheck", 0.14, 0.006, (0.72, -0.91, 0.88), mats["ink"], rot=(math.radians(90), 0, 0), role="line_art_scope_thickness", bh="BH-213")
    scope = rounded_box("LAB11_LineArtCollectionScopeChip", (0.22, 0.035, 0.08), (0.98, -0.91, 0.88), mats["cyan"], 0.006, role="line_art_scope_thickness", bh="BH-213")
    parts.extend([cube, outline, scope])

    boil_pts = [(0.10 + i * 0.06, -0.91, 0.38 + math.sin(i * 1.8) * 0.035) for i in range(9)]
    boil = curve_line("LAB11_LineBoilNoiseLimitedStroke", boil_pts, mats["magenta"], 0.009, role="line_boil_noise_limit", bh="BH-214")
    boil["noise_amplitude"] = 0.035
    boil["hold_frames"] = 2
    cage = rounded_box("LAB11_LineBoilAmplitudeCage", (0.62, 0.025, 0.14), (0.35, -0.92, 0.38), mats["ghost"], 0.004, role="line_boil_noise_limit", bh="BH-214")
    parts.extend([boil, cage])

    frame = rounded_box("LAB11_Mixed2D3DSharedCameraFrame", (0.58, 0.035, 0.32), (1.06, -0.91, 0.38), mats["ghost"], 0.006, role="mixed_2d_3d_shared_space", bh="BH-215")
    card2d = rounded_box("LAB11_2DLayer_InSharedSpace", (0.20, 0.035, 0.16), (0.92, -0.94, 0.38), mats["blue"], 0.006, role="mixed_2d_3d_shared_space", bh="BH-215")
    obj3d = sphere("LAB11_3DObject_InSameCameraSpace", 0.060, (1.16, -0.91, 0.40), mats["gold"], role="mixed_2d_3d_shared_space", bh="BH-215")
    parts.extend([frame, card2d, obj3d])

    rig_pts = [(0.54, -0.91, 0.16), (0.66, -0.91, 0.25), (0.82, -0.91, 0.12), (0.96, -0.91, 0.23)]
    rig_stroke = curve_line("LAB11_GPRigPoseTestStroke", rig_pts, mats["cyan"], 0.010, role="grease_pencil_rig_pose", bh="BH-216")
    parts.append(rig_stroke)
    for i, loc in enumerate(rig_pts):
        ctrl = sphere(f"LAB11_GPRigControllerPose_{i}", 0.024, loc, [mats["blue"], mats["green"], mats["gold"], mats["magenta"]][i], role="grease_pencil_rig_pose", bh="BH-216")
        ctrl["pose_test"] = i
        parts.append(ctrl)

    pass_names = (("Band", mats["toon"]), ("Outline", mats["ink"]), ("Texture", mats["green"]), ("Grade", mats["magenta"]))
    for i, (name, mat) in enumerate(pass_names):
        chip = rounded_box(f"LAB11_ToonPassContract_{name}", (0.15, 0.035, 0.08), (1.30 + i * 0.16, -0.91, 0.80), mat, 0.006, role="toon_pass_contract", bh="BH-217")
        chip["pass"] = name
        parts.append(chip)

    source = curve_line("LAB11_FakeReflectionSourceStroke", [(1.28, -0.91, 0.50), (1.42, -0.91, 0.58), (1.58, -0.91, 0.50)], mats["cyan"], 0.008, role="fake_reflection_link", bh="BH-218")
    reflection = curve_line("LAB11_FakeReflectionLinkedOffsetOpacity", [(1.28, -0.91, 0.38), (1.42, -0.91, 0.32), (1.58, -0.91, 0.38)], mats["ghost"], 0.008, role="fake_reflection_link", bh="BH-218")
    reflection["opacity"] = 0.35
    parts.extend([source, reflection])

    src = rounded_box("LAB11_ConversionSourceCleanupCard", (0.18, 0.035, 0.14), (1.54, -0.91, 0.20), mats["white"], 0.006, role="conversion_cleanup", bh="BH-219")
    silhouette = curve_line("LAB11_ConversionSilhouetteDepthAssumption", [(1.42, -0.91, 0.14), (1.52, -0.91, 0.26), (1.66, -0.91, 0.18)], mats["ink"], 0.007, role="conversion_cleanup", bh="BH-219")
    mesh = rounded_box("LAB11_ConversionMeshValidationProxy", (0.12, 0.080, 0.11), (1.76, -0.91, 0.20), mats["gold"], 0.010, role="conversion_cleanup", bh="BH-219")
    parts.extend([src, silhouette, mesh])
    return parts


def create_vfx_pass_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB11_VFXPassAccountingBoard", (3.86, 0.08, 0.92), (0.08, 0.50, 0.66), mats["panel"], 0.025, role="vfx_lab_panel")
    parts.append(panel)
    pass_specs = [
        ("solve", mats["blue"]),
        ("aov", mats["cyan"]),
        ("shadow", mats["shadow"]),
        ("key", mats["green"]),
        ("grade", mats["magenta"]),
        ("sound", mats["gold"]),
        ("final", mats["white"]),
    ]
    previous_x = -1.54
    for i, (name, mat) in enumerate(pass_specs):
        x = -1.54 + i * 0.48
        card = rounded_box(f"LAB11_VFXPassAccounting_{name}", (0.28, 0.040, 0.16), (x, 0.44, 0.75), mat, 0.008, role="vfx_pass_accounting", bh="BH-220")
        card["pass_index"] = i
        parts.append(card)
        if i:
            parts.append(curve_line(f"LAB11_VFXPassConnector_{i}", [(previous_x + 0.16, 0.41, 0.75), (x - 0.16, 0.41, 0.75)], mats["cyan"], 0.005, role="vfx_pass_accounting", bh="BH-220"))
        previous_x = x
    for i, x in enumerate((-1.50, -0.90, -0.30, 0.30, 0.90, 1.50)):
        row = rounded_box(f"LAB11_VFXChecklistTick_{i}", (0.13, 0.035, 0.08), (x, 0.43, 0.42), [mats["green"], mats["gold"], mats["cyan"], mats["magenta"], mats["blue"], mats["white"]][i], 0.006, role="vfx_pass_accounting", bh="BH-220")
        parts.append(row)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB11_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-204..BH-220")
    floor = rounded_box("LAB11_StudioFloor_NotExported", (5.25, 3.34, 0.065), (0.15, -0.02, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_comp_tracking_board(mats))
    export_parts.extend(create_grease_toon_board(mats))
    export_parts.extend(create_vfx_pass_board(mats))
    labels = [
        add_text("LAB11_Label_CompTracking", "COMP / TRACK / KEY / SHADOW", (-1.28, -1.25, 1.18), 0.047, mats["white"]),
        add_text("LAB11_Label_GPToon", "GREASE PENCIL / LINE ART / TOON", (0.55, -1.25, 1.18), 0.047, mats["white"]),
        add_text("LAB11_Label_VFXPasses", "VFX PASS ACCOUNTING", (0.08, 0.15, 1.16), 0.050, mats["white"]),
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
        if obj.name == "LAB11_LineArtThicknessDepthCheck":
            obj.rotation_euler.z = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = math.tau
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
        if obj.name == "LAB11_CameraTrackTarget_Named":
            obj.location.x -= 0.05
            obj.keyframe_insert(data_path="location", frame=1)
            obj.location.x += 0.10
            obj.keyframe_insert(data_path="location", frame=96)
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
        "viewport_compositor_parity",
        "glow_threshold_control",
        "camera_shake_limit",
        "tracking_solve_qa",
        "tracking_shortcut_assumption",
        "keying_matte_spill",
        "shadow_catcher_contact",
        "camera_framing_qa",
        "grease_pencil_layer_discipline",
        "line_art_scope_thickness",
        "line_boil_noise_limit",
        "mixed_2d_3d_shared_space",
        "grease_pencil_rig_pose",
        "toon_pass_contract",
        "fake_reflection_link",
        "conversion_cleanup",
        "vfx_pass_accounting",
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
    if "LAB11_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    expected_animated = {
        "LAB11_GlowEmitter_ThresholdChecked",
        "LAB11_CameraShakeLimitedMarker",
        "LAB11_CameraTrackTarget_Named",
        "LAB11_LineArtThicknessDepthCheck",
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
        "source_goal": "650-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "lifehack": obj.get("lifehack"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Compositor parity, glow and camera-shake controls are visible.",
            "Tracking solve QA, shortcut assumptions, keying and shadow catcher boards are visible.",
            "Camera-follow, Grease Pencil layers, Line Art and line boil checks are visible.",
            "2D/3D shared space, GP rig pose tests, toon pass contract and fake reflection controls are visible.",
            "Conversion cleanup and VFX pass accounting are visible.",
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
