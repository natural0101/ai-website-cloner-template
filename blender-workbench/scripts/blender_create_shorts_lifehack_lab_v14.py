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

ASSET = "blender_shorts_lifehack_lab_v14"
SCENE_NAME = "BlenderShortsLifehackLabV14"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-260", "name": "Lighting Rigs Need Role Contracts", "applied": "Key, fill, rim and world controls are named with energy and softness ratios."},
    {"id": "BH-261", "name": "Lighting Before After Needs Fixed Exposure", "applied": "Before/after lighting comparator has locked camera/exposure state."},
    {"id": "BH-262", "name": "HDRI Needs Visibility And Reflection Policy", "applied": "HDRI card separates strength, rotation, blur, background and reflection behavior."},
    {"id": "BH-263", "name": "Lighting Tools Need Manual Fallback", "applied": "Addon/global light controls include generated-light cleanup and manual fallback chips."},
    {"id": "BH-264", "name": "Dark Backgrounds Need Separation Checks", "applied": "Dark-background test shows rim separation and shadow detail guard."},
    {"id": "BH-265", "name": "Camera DOF Needs Focus Ownership", "applied": "DOF board uses named focus target, f-stop and focus distance controls."},
    {"id": "BH-266", "name": "Lens Changes Need Perspective QA", "applied": "Lens board shows crop, perspective and aperture side-effect checks."},
    {"id": "BH-267", "name": "Aspect Ratio Needs Safe Frame Review", "applied": "Safe-frame board has thirds, center and text-readability guides."},
    {"id": "BH-268", "name": "Transparent Renders Need Alpha Edge QA", "applied": "Alpha board checks Film transparency, output format and edge premultiply."},
    {"id": "BH-269", "name": "Backplates Need Matchmove-Like Checks", "applied": "Backplate card shows horizon, color-temperature and contact-shadow proof."},
    {"id": "BH-270", "name": "Cryptomatte Needs Naming Discipline", "applied": "Cryptomatte row has object/material name chips and EXR pass delivery."},
    {"id": "BH-271", "name": "Compositor Masks Need Matte Edge QA", "applied": "Mask board exposes source, matte edge and final-render parity."},
    {"id": "BH-272", "name": "Denoise Needs Detail And Flicker Checks", "applied": "Denoise comparator shows sample budget, detail crop and flicker warning."},
    {"id": "BH-273", "name": "Render Optimization Needs Quality Comparison", "applied": "Render settings board compares speed knobs against quality proof."},
    {"id": "BH-274", "name": "Eevee Cycles Parity Needs Feature Checklist", "applied": "Engine parity strip checks SSR, AO, contact shadows, material and color management."},
    {"id": "BH-275", "name": "Volumetrics Need Density Budgets", "applied": "Volumetric beams expose density, bounds, step size and render-time budget."},
    {"id": "BH-276", "name": "Light Linking Needs Scope Notes", "applied": "Light linking board marks object/collection scope and proof frame."},
    {"id": "BH-277", "name": "Highlight Control Needs Display Review", "applied": "Highlight limiter meter shows clipping scope and display-transform review."},
    {"id": "BH-278", "name": "Transparent Shadow Work Needs Destination Proof", "applied": "Transparent shadow card compares alpha shadow against destination plate."},
    {"id": "BH-279", "name": "Render Reviews Need Pass Accounting", "applied": "Render accounting board lists beauty, alpha, masks, Cryptomatte, shadows, denoise and grade."},
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
        "base": make_mat("Lab14_BaseGraphite", (0.018, 0.020, 0.030, 1.0), roughness=0.64),
        "panel": make_mat("Lab14_PanelInk", (0.050, 0.058, 0.090, 1.0), roughness=0.60),
        "panel_alt": make_mat("Lab14_PanelDeepWine", (0.085, 0.044, 0.072, 1.0), roughness=0.62),
        "dark": make_mat("Lab14_DarkSocket", (0.012, 0.014, 0.020, 1.0), roughness=0.72),
        "white": make_mat("Lab14_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.52),
        "cyan": make_mat("Lab14_ControlCyan", (0.02, 0.78, 0.96, 1.0), roughness=0.34, emission=(0.0, 0.25, 0.55, 1.0), emission_strength=0.10),
        "green": make_mat("Lab14_CheckGreen", (0.13, 0.82, 0.42, 1.0), roughness=0.48),
        "gold": make_mat("Lab14_KeyGold", (1.0, 0.72, 0.17, 1.0), roughness=0.42, metallic=0.03),
        "magenta": make_mat("Lab14_MatteMagenta", (1.0, 0.12, 0.56, 1.0), roughness=0.38, emission=(0.40, 0.0, 0.18, 1.0), emission_strength=0.07),
        "blue": make_mat("Lab14_RenderBlue", (0.10, 0.35, 0.92, 1.0), roughness=0.48),
        "orange": make_mat("Lab14_ClipOrange", (0.96, 0.42, 0.11, 1.0), roughness=0.44),
        "red": make_mat("Lab14_WarningRed", (0.96, 0.08, 0.06, 1.0), roughness=0.35, emission=(0.45, 0.02, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab14_VolumeViolet", (0.48, 0.24, 0.86, 1.0), roughness=0.46),
        "ghost": make_mat("Lab14_GhostAlpha", (0.56, 0.72, 1.0, 1.0), roughness=0.54, alpha=0.34),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB14_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.014,
    role: str = "rounded_box",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB14_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB14_WeightedNormals", type="WEIGHTED_NORMAL")
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


def cyl_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    vertices: int = 12,
    role: str = "cylinder_between",
    export: bool = True,
    bh: str | None = None,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    loc = a + direction * 0.5
    rot = direction.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=loc, rotation=rot)
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
    radius: float = 0.006,
    role: str = "direction_arrow",
    bh: str | None = None,
) -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    mid = a.lerp(b, 0.78)
    return [
        cyl_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, mat, role=role, bh=bh),
        cone_between(f"{name}_Head", tuple(mid), tuple(b), radius * 2.8, 0.0, mat, role=role, bh=bh),
    ]


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
    scene.world = scene.world or bpy.data.worlds.new("LAB14_World")
    scene.world.color = (0.015, 0.017, 0.026)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.5, -5.0, 4.8))
    key = bpy.context.object
    key.name = "LAB14_KeyArea_Warm"
    key.data.energy = 690
    key.data.size = 5.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.2, 2.7, 3.1))
    fill = bpy.context.object
    fill.name = "LAB14_FillArea_Cool"
    fill.data.energy = 145
    fill.data.size = 5.4
    fill.data.color = (0.55, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.3, 3.5, 2.7))
    rim = bpy.context.object
    rim.name = "LAB14_RimPoint_Cyan"
    rim.data.energy = 270
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.15, -5.20, 3.25), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB14_Camera_Hero3Q"
    cam.data.lens = 40
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 5.25
    cam.data.dof.aperture_fstop = 15.0
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


def panel(name: str, loc: tuple[float, float, float], mat: bpy.types.Material, role: str) -> bpy.types.Object:
    return rounded_box(name, (2.05, 0.075, 1.12), loc, mat, 0.026, role=role)


def lighting_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB14_LightingContractBoard", (-1.12, -0.84, 0.66), mats["panel_alt"], "lighting_lab_panel")]
    role_specs = [
        ("Key", -1.86, 1.02, mats["gold"], 1.0),
        ("Fill", -1.46, 0.90, mats["blue"], 0.38),
        ("Rim", -1.06, 1.06, mats["cyan"], 0.62),
        ("World", -0.70, 0.88, mats["green"], 0.22),
    ]
    for name, x, z, mat, ratio in role_specs:
        orb = sphere(f"LAB14_LightRole_{name}_Ratio", 0.062, (x, -0.91, z), mat, role="lighting_role_contract", bh="BH-260")
        orb["energy_ratio"] = ratio
        parts.append(orb)
        parts.append(rounded_box(f"LAB14_LightRole_{name}_SoftnessBar", (0.22, 0.045, 0.035), (x, -0.90, z - 0.16), mat, 0.004, role="lighting_role_contract", bh="BH-260"))
    parts.extend(arrow("LAB14_KeyFillRimBalanceFlow", (-1.78, -0.92, 0.74), (-0.82, -0.92, 0.74), mats["white"], radius=0.005, role="lighting_role_contract", bh="BH-260"))

    before = rounded_box("LAB14_LightingBefore_FixedExposure", (0.34, 0.050, 0.22), (-1.82, -0.90, 0.44), mats["dark"], 0.008, role="lighting_fixed_exposure", bh="BH-261")
    after = rounded_box("LAB14_LightingAfter_SameExposure", (0.34, 0.050, 0.22), (-1.36, -0.90, 0.44), mats["green"], 0.008, role="lighting_fixed_exposure", bh="BH-261")
    exposure_lock = rounded_box("LAB14_ExposureLock_NotAuto", (0.20, 0.052, 0.10), (-1.02, -0.90, 0.44), mats["gold"], 0.006, role="lighting_fixed_exposure", bh="BH-261")
    parts.extend([before, after, exposure_lock])

    fallback = rounded_box("LAB14_LightAddonManualFallback", (0.42, 0.050, 0.18), (-0.62, -0.90, 0.56), mats["orange"], 0.008, role="lighting_tool_fallback", bh="BH-263")
    fallback["tool_rule"] = "cleanup generated lights, grouping, fallback"
    parts.append(fallback)
    for i, mat in enumerate((mats["cyan"], mats["green"], mats["gold"])):
        parts.append(rounded_box(f"LAB14_LightGroupMultiplier_{i}", (0.12, 0.048, 0.08), (-0.78 + i * 0.16, -0.90, 0.34), mat, 0.004, role="lighting_tool_fallback", bh="BH-263"))

    dark_card = rounded_box("LAB14_DarkBackgroundRimSeparation", (0.46, 0.050, 0.24), (-1.62, -0.90, 0.20), mats["dark"], 0.010, role="dark_background_separation", bh="BH-264")
    rim_line = cyl_between("LAB14_DarkBackgroundRimLine", (-1.84, -0.93, 0.29), (-1.42, -0.93, 0.29), 0.010, mats["cyan"], role="dark_background_separation", bh="BH-264")
    shadow_chip = rounded_box("LAB14_DarkBackgroundShadowDetail", (0.18, 0.054, 0.08), (-1.62, -0.94, 0.09), mats["violet"], 0.004, role="dark_background_separation", bh="BH-264")
    parts.extend([dark_card, rim_line, shadow_chip])

    link = rounded_box("LAB14_LightLinkingScope_ObjectCollection", (0.40, 0.050, 0.16), (-0.86, -0.90, 0.18), mats["magenta"], 0.008, role="light_linking_scope_notes", bh="BH-276")
    link["scope"] = "object, collection, render layer proof"
    parts.append(link)
    parts.extend(arrow("LAB14_LightLinkProofArrow", (-1.05, -0.92, 0.18), (-0.68, -0.92, 0.18), mats["cyan"], radius=0.004, role="light_linking_scope_notes", bh="BH-276"))

    clip_meter = rounded_box("LAB14_HighlightLimiterDisplayReview", (0.48, 0.052, 0.12), (-0.66, -0.90, 1.10), mats["red"], 0.006, role="highlight_display_review", bh="BH-277")
    clip_meter["highlight_rule"] = "clipping scopes, display transform, final output"
    parts.append(clip_meter)
    for i, mat in enumerate((mats["green"], mats["gold"], mats["orange"], mats["red"])):
        parts.append(rounded_box(f"LAB14_HighlightScopeLevel_{i}", (0.08, 0.056, 0.05 + i * 0.035), (-0.86 + i * 0.10, -0.93, 1.00), mat, 0.003, role="highlight_display_review", bh="BH-277"))
    return parts


def hdri_camera_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB14_HDRICameraBoard", (1.12, -0.82, 0.66), mats["panel"], "hdri_camera_lab_panel")]
    hdr_ring = sphere("LAB14_HDRIStrengthRotationBlurCore", 0.12, (0.38, -0.91, 1.02), mats["cyan"], segments=18, ring_count=9, role="hdri_visibility_reflection_policy", bh="BH-262")
    hdr_ring["hdri_policy"] = "license, strength, rotation, blur, bg/diffuse/glossy"
    parts.append(hdr_ring)
    for i, (name, mat) in enumerate((("BG", mats["blue"]), ("Diffuse", mats["green"]), ("Glossy", mats["gold"]), ("Blur", mats["violet"]))):
        chip = rounded_box(f"LAB14_HDRIVisibility_{name}", (0.16, 0.050, 0.11), (0.70 + i * 0.18, -0.90, 1.02), mat, 0.006, role="hdri_visibility_reflection_policy", bh="BH-262")
        chip["hdri_channel"] = name
        parts.append(chip)
    parts.extend(arrow("LAB14_HDRIRotationDirection", (0.26, -0.92, 0.85), (0.66, -0.92, 0.85), mats["white"], radius=0.005, role="hdri_visibility_reflection_policy", bh="BH-262"))

    focus = sphere("LAB14_DOFFocusTarget_Named", 0.055, (0.36, -0.92, 0.60), mats["magenta"], role="camera_dof_focus_ownership", bh="BH-265")
    focus["focus_target"] = "named object, f-stop, distance, final parity"
    parts.append(focus)
    dof_rail = rounded_box("LAB14_DOFFStopDistanceRail", (0.58, 0.045, 0.055), (0.78, -0.90, 0.60), mats["dark"], 0.004, role="camera_dof_focus_ownership", bh="BH-265")
    parts.append(dof_rail)
    focus.location.x = 0.36
    focus.keyframe_insert(data_path="location", frame=1)
    focus.location.x = 0.52
    focus.keyframe_insert(data_path="location", frame=48)
    focus.location.x = 0.36
    focus.keyframe_insert(data_path="location", frame=96)
    linearize(focus)

    lens_cards = [("24mm", mats["orange"]), ("50mm", mats["blue"]), ("85mm", mats["cyan"])]
    for i, (label, mat) in enumerate(lens_cards):
        card = rounded_box(f"LAB14_LensPerspectiveQA_{label}", (0.20, 0.050, 0.13), (1.34 + i * 0.23, -0.90, 0.72), mat, 0.006, role="lens_perspective_qa", bh="BH-266")
        card["lens_rule"] = "perspective, crop, DOF side effects"
        parts.append(card)
    safe = rounded_box("LAB14_AspectRatioSafeFrameGuides", (0.54, 0.050, 0.34), (1.38, -0.90, 0.34), mats["dark"], 0.008, role="aspect_safe_frame_review", bh="BH-267")
    parts.append(safe)
    parts.append(cyl_between("LAB14_SafeFrameVerticalGuide", (1.38, -0.93, 0.18), (1.38, -0.93, 0.50), 0.004, mats["white"], role="aspect_safe_frame_review", bh="BH-267"))
    parts.append(cyl_between("LAB14_SafeFrameHorizontalGuide", (1.12, -0.93, 0.34), (1.64, -0.93, 0.34), 0.004, mats["white"], role="aspect_safe_frame_review", bh="BH-267"))
    for i, x in enumerate((1.22, 1.54)):
        parts.append(cyl_between(f"LAB14_ThirdsGuide_{i}", (x, -0.93, 0.18), (x, -0.93, 0.50), 0.003, mats["gold"], role="aspect_safe_frame_review", bh="BH-267"))
    return parts


def alpha_composite_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB14_AlphaCompositeBoard", (-1.12, 0.36, 0.66), mats["panel"], "alpha_composite_lab_panel")]
    alpha_card = rounded_box("LAB14_TransparentAlphaEdgeQA", (0.48, 0.050, 0.24), (-1.82, 0.30, 1.02), mats["ghost"], 0.010, role="transparent_alpha_edge_qa", bh="BH-268")
    alpha_card["alpha_rule"] = "film transparent, PNG/EXR, premultiply, edge"
    parts.append(alpha_card)
    for i, mat in enumerate((mats["cyan"], mats["green"], mats["gold"], mats["red"])):
        parts.append(rounded_box(f"LAB14_AlphaEdgePixel_{i}", (0.07, 0.054, 0.07), (-2.02 + i * 0.12, 0.26, 0.84), mat, 0.003, role="transparent_alpha_edge_qa", bh="BH-268"))

    backplate = rounded_box("LAB14_BackplateMatch_HorizonColorShadow", (0.54, 0.050, 0.30), (-1.16, 0.30, 1.00), mats["blue"], 0.010, role="backplate_match_checks", bh="BH-269")
    backplate["match_checks"] = "camera, horizon, scale, color temp, contact"
    parts.append(backplate)
    parts.append(cyl_between("LAB14_BackplateHorizonLine", (-1.40, 0.26, 1.03), (-0.92, 0.26, 1.03), 0.004, mats["white"], role="backplate_match_checks", bh="BH-269"))
    parts.append(rounded_box("LAB14_TransparentShadowDestinationProof", (0.34, 0.050, 0.12), (-0.66, 0.30, 0.94), mats["dark"], 0.008, role="transparent_shadow_destination", bh="BH-278"))

    crypto_mats = [mats["magenta"], mats["cyan"], mats["green"], mats["gold"]]
    for i, mat in enumerate(crypto_mats):
        chip = rounded_box(f"LAB14_CryptomatteNameChip_{i}", (0.16, 0.052, 0.12), (-1.88 + i * 0.20, 0.30, 0.56), mat, 0.006, role="cryptomatte_naming_discipline", bh="BH-270")
        chip["crypto_rule"] = "stable object/material names, EXR channel"
        parts.append(chip)
    matte = rounded_box("LAB14_CompositorMaskEdgeQA", (0.52, 0.050, 0.20), (-0.92, 0.30, 0.56), mats["violet"], 0.010, role="compositor_matte_edge_qa", bh="BH-271")
    matte["mask_rule"] = "source, matte edge, pass isolation, final parity"
    parts.append(matte)
    for i in range(5):
        parts.append(sphere(f"LAB14_MatteEdgeSample_{i}", 0.018, (-1.14 + i * 0.10, 0.26, 0.65 + math.sin(i) * 0.03), mats["white"], segments=8, ring_count=4, role="compositor_matte_edge_qa", bh="BH-271"))

    pass_names = ["beauty", "alpha", "masks", "crypto", "shadow", "denoise", "grade"]
    for i, name in enumerate(pass_names):
        x = -1.92 + i * 0.24
        p = rounded_box(f"LAB14_RenderPassAccounting_{name}", (0.16, 0.050, 0.10), (x, 0.30, 0.26), [mats["blue"], mats["ghost"], mats["violet"], mats["magenta"], mats["dark"], mats["green"], mats["gold"]][i], 0.006, role="render_pass_accounting", bh="BH-279")
        p["pass"] = name
        parts.append(p)
        if i:
            parts.append(cyl_between(f"LAB14_RenderPassConnector_{i}", (x - 0.16, 0.27, 0.26), (x - 0.08, 0.27, 0.26), 0.004, mats["white"], role="render_pass_accounting", bh="BH-279"))
    return parts


def render_volume_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB14_RenderVolumeBoard", (1.12, 0.39, 0.66), mats["panel_alt"], "render_volume_lab_panel")]
    noisy = rounded_box("LAB14_DenoiseBefore_NoiseCrop", (0.32, 0.050, 0.22), (0.34, 0.32, 1.02), mats["dark"], 0.008, role="denoise_detail_flicker", bh="BH-272")
    clean = rounded_box("LAB14_DenoiseAfter_DetailCrop", (0.32, 0.050, 0.22), (0.78, 0.32, 1.02), mats["green"], 0.008, role="denoise_detail_flicker", bh="BH-272")
    parts.extend([noisy, clean])
    for i in range(8):
        parts.append(sphere(f"LAB14_NoiseSampleDot_{i}", 0.014, (0.22 + (i % 4) * 0.07, 0.28, 1.08 - (i // 4) * 0.08), mats["white"], segments=8, ring_count=4, role="denoise_detail_flicker", bh="BH-272"))
    flicker = rounded_box("LAB14_DenoiseFlickerWarning", (0.22, 0.052, 0.10), (1.06, 0.31, 1.02), mats["red"], 0.006, role="denoise_detail_flicker", bh="BH-272")
    parts.append(flicker)

    settings = ["GPU", "samples", "paths", "threshold", "denoise"]
    for i, name in enumerate(settings):
        chip = rounded_box(f"LAB14_RenderQualityComparison_{name}", (0.16, 0.050, 0.10), (0.32 + i * 0.20, 0.32, 0.72), [mats["blue"], mats["cyan"], mats["violet"], mats["gold"], mats["green"]][i], 0.006, role="render_quality_comparison", bh="BH-273")
        chip["setting"] = name
        parts.append(chip)

    parity = rounded_box("LAB14_EeveeCyclesParityChecklist", (0.72, 0.050, 0.18), (1.44, 0.31, 0.88), mats["blue"], 0.010, role="eevee_cycles_parity", bh="BH-274")
    parity["parity"] = "SSR, AO, contact shadows, material, color management"
    parts.append(parity)
    for i, mat in enumerate((mats["cyan"], mats["green"], mats["gold"], mats["magenta"], mats["white"])):
        parts.append(rounded_box(f"LAB14_EngineParityTick_{i}", (0.07, 0.052, 0.07), (1.16 + i * 0.11, 0.27, 0.75), mat, 0.004, role="eevee_cycles_parity", bh="BH-274"))

    for i in range(4):
        start = (0.42 + i * 0.18, 0.30, 0.36)
        end = (0.54 + i * 0.18, 0.30, 0.62 + i * 0.03)
        beam = cone_between(f"LAB14_VolumetricBeam_DensityBudget_{i}", start, end, 0.035, 0.010, [mats["ghost"], mats["violet"], mats["cyan"], mats["gold"]][i], vertices=18, role="volumetric_density_budget", bh="BH-275")
        beam["volume_rule"] = "density, bounds, step size, light direction, time"
        parts.append(beam)
    volume_bounds = rounded_box("LAB14_VolumetricBoundsStepSizeCard", (0.40, 0.050, 0.16), (1.36, 0.31, 0.36), mats["violet"], 0.008, role="volumetric_density_budget", bh="BH-275")
    parts.append(volume_bounds)
    return parts


def rear_summary_marks(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    specs = [
        ("Light", -1.12, -0.765, 0.66, ["lighting_role_contract", "lighting_fixed_exposure", "lighting_tool_fallback", "highlight_display_review"], "BH-260..BH-263,BH-277"),
        ("HDRI", 1.12, -0.745, 0.66, ["hdri_visibility_reflection_policy", "camera_dof_focus_ownership", "lens_perspective_qa", "aspect_safe_frame_review"], "BH-262,BH-265..BH-267"),
        ("Alpha", -1.12, 0.435, 0.66, ["transparent_alpha_edge_qa", "backplate_match_checks", "cryptomatte_naming_discipline", "render_pass_accounting"], "BH-268..BH-271,BH-278,BH-279"),
        ("Render", 1.12, 0.465, 0.66, ["denoise_detail_flicker", "render_quality_comparison", "eevee_cycles_parity", "volumetric_density_budget"], "BH-272..BH-275"),
    ]
    swatches = [mats["cyan"], mats["green"], mats["gold"], mats["magenta"]]
    for board, x, y, z, roles, bh in specs:
        rail = rounded_box(f"LAB14_RearSummaryRail_{board}", (1.08, 0.040, 0.052), (x, y, z + 0.18), mats["dark"], 0.004, role=roles[0], bh=bh)
        rail["rear_summary"] = "backside turntable readability"
        parts.append(rail)
        for i, role in enumerate(roles):
            chip = rounded_box(f"LAB14_RearSummaryChip_{board}_{i}", (0.18, 0.046, 0.11), (x - 0.39 + i * 0.26, y + 0.01, z), swatches[i], 0.006, role=role, bh=bh)
            parts.append(chip)
        parts.extend(arrow(f"LAB14_RearSummaryArrow_{board}", (x - 0.53, y + 0.02, z - 0.18), (x + 0.53, y + 0.02, z - 0.18), mats["white"], radius=0.004, role=roles[-1], bh=bh))
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB14_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-260..BH-279")

    floor = rounded_box("LAB14_StudioFloor_NotExported", (5.35, 3.52, 0.065), (0.0, -0.08, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]

    export_parts.extend(lighting_board(mats))
    export_parts.extend(hdri_camera_board(mats))
    export_parts.extend(alpha_composite_board(mats))
    export_parts.extend(render_volume_board(mats))
    export_parts.extend(rear_summary_marks(mats))

    labels = [
        add_text("LAB14_Label_Lighting", "LIGHTING / EXPOSURE / LINKING", (-1.12, -1.26, 1.24), 0.045, mats["white"]),
        add_text("LAB14_Label_HDRICamera", "HDRI / CAMERA / SAFE FRAME", (1.12, -1.26, 1.24), 0.046, mats["white"]),
        add_text("LAB14_Label_AlphaComposite", "ALPHA / BACKPLATE / PASSES", (-1.12, -0.03, 1.18), 0.046, mats["white"]),
        add_text("LAB14_Label_RenderVolume", "DENOISE / ENGINE / VOLUME", (1.12, 0.01, 1.18), 0.046, mats["white"]),
    ]
    helper_parts.extend(labels)

    for obj in export_parts + helper_parts:
        parent_keep_world(obj, root)

    for frame, rot in ((1, 0.0), (24, 0.0), (72, math.tau), (96, math.tau)):
        root.rotation_euler = (0, 0, rot)
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    linearize(root)

    for obj in export_parts:
        if obj.name == "LAB14_ExposureLock_NotAuto":
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=1)
            obj.scale = (1.24, 1.24, 1.24)
            obj.keyframe_insert(data_path="scale", frame=48)
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=96)
            linearize(obj)
        if obj.name == "LAB14_HighlightLimiterDisplayReview":
            obj.location.z -= 0.02
            obj.keyframe_insert(data_path="location", frame=1)
            obj.location.z += 0.07
            obj.keyframe_insert(data_path="location", frame=48)
            obj.location.z -= 0.05
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
        "lighting_role_contract",
        "lighting_fixed_exposure",
        "hdri_visibility_reflection_policy",
        "lighting_tool_fallback",
        "dark_background_separation",
        "camera_dof_focus_ownership",
        "lens_perspective_qa",
        "aspect_safe_frame_review",
        "transparent_alpha_edge_qa",
        "backplate_match_checks",
        "cryptomatte_naming_discipline",
        "compositor_matte_edge_qa",
        "denoise_detail_flicker",
        "render_quality_comparison",
        "eevee_cycles_parity",
        "volumetric_density_budget",
        "light_linking_scope_notes",
        "highlight_display_review",
        "transparent_shadow_destination",
        "render_pass_accounting",
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
    if "LAB14_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    expected_animated = {
        "LAB14_Root_TurntableAnimated",
        "LAB14_DOFFocusTarget_Named",
        "LAB14_ExposureLock_NotAuto",
        "LAB14_HighlightLimiterDisplayReview",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        warnings.append(f"Expected animated QA markers missing: {missing_anim}")
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
        "source_goal": "800-source Blender Shorts checkpoint test asset.",
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
            "Lighting role contracts, fixed exposure, tool fallback, dark-background separation and light linking are visible.",
            "HDRI policy, DOF focus ownership, lens perspective and safe-frame checks are visible.",
            "Alpha edge QA, backplate checks, Cryptomatte naming, compositor masks and pass accounting are visible.",
            "Denoise, render-quality comparison, engine parity and volumetric density budget are visible.",
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
