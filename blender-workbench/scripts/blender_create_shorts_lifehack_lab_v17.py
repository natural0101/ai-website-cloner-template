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

ASSET = "blender_shorts_lifehack_lab_v17"
SCENE_NAME = "BlenderShortsLifehackLabV17"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-320", "name": "Line Art Needs Layer Ownership", "applied": "Line Art lane shows source collection, layer ownership, edge filters and render/export parity."},
    {"id": "BH-321", "name": "Comic Outlines Need Thickness Budgets", "applied": "Outline thickness rings show camera distance, occlusion and fallback policy."},
    {"id": "BH-322", "name": "Grease Pencil Cleanup Needs Frame-Range Proof", "applied": "Stroke cleanup board shows fill, extension, gap and frame-range checks."},
    {"id": "BH-323", "name": "Boiling Lines Need Loop Discipline", "applied": "Boiling line loop has amplitude, seed and first/last continuity markers."},
    {"id": "BH-324", "name": "Imported Sketches Need Source And Scale Notes", "applied": "Sketch import card has source, rights, trace cleanup and scale alignment."},
    {"id": "BH-325", "name": "Glow Outlines Need Separate Emission Controls", "applied": "Glow outline separates stroke visibility from bloom/emission controls."},
    {"id": "BH-326", "name": "Graph Editor Polish Needs F-Curve Evidence", "applied": "F-curve board shows handles, channel filters, spacing and overshoot guards."},
    {"id": "BH-327", "name": "Extrapolation Needs Endpoint Policy", "applied": "Endpoint strip marks cycle, linear, constant and duplicate-frame cleanup policy."},
    {"id": "BH-328", "name": "Procedural Sway Needs Phase Controls", "applied": "Animated sway bar exposes amplitude, phase and seed controls."},
    {"id": "BH-329", "name": "Seamless Loops Need Frame Proof", "applied": "Loop proof has first/last state, phase and material value indicators."},
    {"id": "BH-330", "name": "Motion Blur Needs Object Policy", "applied": "Motion blur board separates shutter, samples and per-object exclusions."},
    {"id": "BH-331", "name": "Camera Cuts Need Timeline Notes", "applied": "Camera cut lane shows markers, frame ranges and continuity notes."},
    {"id": "BH-332", "name": "Animation Add-Ons Need Manual Proof", "applied": "Addon lane routes through dependency notes and manual loop proof."},
    {"id": "BH-333", "name": "Asset Browser Needs Catalog Discipline", "applied": "Catalog cards show tags, preview thumbnails, version, dependencies and license fields."},
    {"id": "BH-334", "name": "Cross-File Reuse Needs Dependency Checks", "applied": "Linked asset lane shows material, scale, library path, override and animation dependencies."},
    {"id": "BH-335", "name": "Asset Switching Needs Realization Gates", "applied": "Collection/index switch has naming, seed, density, realization and export budget gates."},
    {"id": "BH-336", "name": "Material Reuse Needs Duplicate Cleanup", "applied": "Material catalog lane shows duplicate cleanup and color-space checks."},
    {"id": "BH-337", "name": "GLB Optimization Needs Visual Regression Checks", "applied": "GLB optimizer gate compares pre/post texture scale and preview regression."},
    {"id": "BH-338", "name": "Texture Export Needs Re-Link QA", "applied": "Texture export board shows format, color space, naming, packing and material relink."},
    {"id": "BH-339", "name": "Physics Scatter Needs Bake And Cleanup Policy", "applied": "Scatter lane has source library, simulation bake, cleanup, seed and instance/realize policy."},
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
    roughness: float = 0.56,
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
            "Specular IOR Level": 0.40,
            "Coat Weight": 0.03,
            "Coat Roughness": 0.24,
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
        "base": make_mat("Lab17_BaseInk", (0.016, 0.018, 0.026, 1.0), roughness=0.68),
        "panel": make_mat("Lab17_PanelBlueBlack", (0.036, 0.048, 0.076, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab17_PanelAubergine", (0.075, 0.043, 0.085, 1.0), roughness=0.63),
        "panel_green": make_mat("Lab17_PanelGreen", (0.030, 0.067, 0.058, 1.0), roughness=0.62),
        "ink": make_mat("Lab17_InkDark", (0.010, 0.012, 0.018, 1.0), roughness=0.74),
        "white": make_mat("Lab17_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.54),
        "cyan": make_mat("Lab17_LineCyan", (0.03, 0.77, 0.96, 1.0), roughness=0.34, emission=(0.0, 0.26, 0.52, 1.0), emission_strength=0.10),
        "green": make_mat("Lab17_CheckGreen", (0.12, 0.78, 0.38, 1.0), roughness=0.48),
        "gold": make_mat("Lab17_KeyGold", (1.0, 0.70, 0.18, 1.0), roughness=0.42, metallic=0.04),
        "magenta": make_mat("Lab17_Magenta", (0.96, 0.14, 0.58, 1.0), roughness=0.38, emission=(0.32, 0.0, 0.16, 1.0), emission_strength=0.08),
        "orange": make_mat("Lab17_Orange", (0.96, 0.42, 0.10, 1.0), roughness=0.44),
        "red": make_mat("Lab17_WarningRed", (0.95, 0.08, 0.06, 1.0), roughness=0.36, emission=(0.42, 0.02, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab17_Violet", (0.50, 0.25, 0.86, 1.0), roughness=0.46),
        "blue": make_mat("Lab17_Blue", (0.10, 0.38, 0.92, 1.0), roughness=0.48),
        "ghost": make_mat("Lab17_GhostAlpha", (0.58, 0.78, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "glow": make_mat("Lab17_GlowStroke", (0.02, 0.95, 0.78, 1.0), roughness=0.30, emission=(0.0, 0.85, 0.65, 1.0), emission_strength=0.45),
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
    vertices: int = 16,
    role: str = "link",
    bh: str | None = None,
    export: bool = True,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    mid = (a + b) * 0.5
    length = max((b - a).length, 0.001)
    rotation = (b - a).to_track_quat("Z", "Y").to_euler()
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
    vertices: int = 20,
    role: str = "arrow_head",
    bh: str | None = None,
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    mid = (a + b) * 0.5
    length = max((b - a).length, 0.001)
    rotation = (b - a).to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=length, location=mid, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, True, bh)


def sphere(
    name: str,
    loc: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    segments: int = 20,
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
    role: str = "ring",
    bh: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=42, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, True, bh)


def add_text(
    name: str,
    text: str,
    loc: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    role: str = "preview_label",
    export: bool = False,
) -> bpy.types.Object:
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
    return tag(obj, role, export)


def arrow(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    mat: bpy.types.Material,
    radius: float = 0.007,
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
    scene.world = scene.world or bpy.data.worlds.new("LAB17_World")
    scene.world.color = (0.014, 0.016, 0.024)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.7, -5.2, 4.8))
    key = bpy.context.object
    key.name = "LAB17_KeyArea_Warm"
    key.data.energy = 750
    key.data.size = 5.2
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.2, 2.9, 3.4))
    fill = bpy.context.object
    fill.name = "LAB17_FillArea_Cool"
    fill.data.energy = 150
    fill.data.size = 5.8
    fill.data.color = (0.58, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.0, 3.7, 2.9))
    rim = bpy.context.object
    rim.name = "LAB17_RimPoint_Cyan"
    rim.data.energy = 315
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.35, -5.65, 3.35), rotation=(math.radians(58), 0, math.radians(39)))
    cam = bpy.context.object
    cam.name = "LAB17_Camera_Hero3Q"
    cam.data.lens = 38
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 7.5
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def make_root() -> bpy.types.Object:
    root = bpy.data.objects.new("LAB17_Root_TurntableAnimated", None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.65
    tag(root, "seamless_loop_frame_proof", export=True, bh="BH-329")
    for frame, angle in ((1, -3), (48, 13), (96, 357)):
        bpy.context.scene.frame_set(frame)
        root.rotation_euler = (0, 0, math.radians(angle))
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    return root


def add_panel(mats: dict[str, bpy.types.Material], name: str, title: str, loc: tuple[float, float, float], size: tuple[float, float, float], mat_key: str) -> bpy.types.Object:
    panel = rounded_box(name, size, loc, mats[mat_key], 0.035, role="lab_panel", export=True)
    add_text(f"{name}_Title", title, (loc[0], loc[1] - 0.065, loc[2] + size[2] * 0.42), 0.058, mats["white"])
    return panel


def wavy_stroke(name: str, points: list[tuple[float, float, float]], mat: bpy.types.Material, radius: float, role: str, bh: str) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for index in range(len(points) - 1):
        parts.append(cyl_between(f"{name}_{index:02d}", points[index], points[index + 1], radius, mat, vertices=10, role=role, bh=bh))
    for index, point in enumerate(points):
        parts.append(sphere(f"{name}_Point_{index:02d}", point, radius * 2.2, mat, segments=12, role=role, bh=bh))
    return parts


def build_line_art_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB17_LineArtPanel_Backplate", "LINE ART / GREASE PENCIL", (-1.95, 0.06, 1.02), (1.42, 0.08, 1.08), "panel")
    parts.extend(wavy_stroke(
        "LAB17_LineArt_SourceStroke",
        [(-2.48, -0.06, 1.33), (-2.30, -0.06, 1.42), (-2.10, -0.06, 1.30), (-1.88, -0.06, 1.38)],
        mats["cyan"],
        0.010,
        "line_art_layer_ownership",
        "BH-320",
    ))
    for index, color in enumerate(["blue", "magenta", "green"]):
        parts.append(rounded_box(f"LAB17_LineArt_LayerOwner_{index+1}", (0.16, 0.030, 0.075), (-2.44 + index * 0.21, -0.078, 1.12), mats[color], 0.010, role="line_art_layer_ownership", bh="BH-320"))
    parts.append(torus("LAB17_ComicOutline_ThicknessBudget", (-1.70, -0.078, 1.30), 0.150, 0.007, mats["orange"], role="comic_outline_thickness_budget", bh="BH-321"))
    parts.append(torus("LAB17_ComicOutline_CameraDistanceRing", (-1.70, -0.078, 1.30), 0.205, 0.005, mats["white"], role="comic_outline_thickness_budget", bh="BH-321"))
    for index, label in enumerate(["fill", "extend", "gap", "range"]):
        parts.append(rounded_box(f"LAB17_GPCleanup_{label}", (0.17, 0.030, 0.070), (-2.44 + index * 0.22, -0.078, 0.82), mats[["green", "cyan", "red", "gold"][index]], 0.010, role="grease_pencil_frame_range_cleanup", bh="BH-322"))
    parts.extend(wavy_stroke(
        "LAB17_BoilingLine_LoopDiscipline",
        [(-2.44, -0.095, 0.58), (-2.25, -0.095, 0.66), (-2.04, -0.095, 0.56), (-1.82, -0.095, 0.65)],
        mats["magenta"],
        0.007,
        "boiling_line_loop_discipline",
        "BH-323",
    ))
    sketch = rounded_box("LAB17_ImportedSketch_SourceScaleCard", (0.29, 0.030, 0.16), (-1.55, -0.076, 0.82), mats["ghost"], 0.014, role="imported_sketch_source_scale", bh="BH-324")
    parts.append(sketch)
    parts.extend(arrow("LAB17_ImportedSketch_ScaleArrow", (-1.72, -0.085, 0.72), (-1.37, -0.085, 0.93), mats["white"], radius=0.0045, role="imported_sketch_source_scale", bh="BH-324"))
    parts.append(torus("LAB17_GlowOutline_VisibleStroke", (-1.50, -0.078, 1.12), 0.090, 0.005, mats["glow"], role="glow_outline_emission_controls", bh="BH-325"))
    parts.append(rounded_box("LAB17_GlowOutline_EmissionSlider", (0.22, 0.026, 0.055), (-1.25, -0.082, 1.12), mats["glow"], 0.010, role="glow_outline_emission_controls", bh="BH-325"))
    add_text("LAB17_LineChip_Layers", "source collection + layers", (-2.10, -0.095, 1.55), 0.035, mats["cyan"])
    add_text("LAB17_LineChip_Cleanup", "fills strokes loop", (-2.08, -0.095, 0.43), 0.034, mats["magenta"])
    return parts


def build_animation_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB17_AnimPanel_Backplate", "GRAPH EDITOR / LOOPS", (0.00, 0.07, 1.03), (1.52, 0.08, 1.08), "panel_alt")
    curve_points = [(-0.62, -0.076, 0.88), (-0.42, -0.076, 1.08), (-0.22, -0.076, 1.02), (-0.02, -0.076, 1.34), (0.18, -0.076, 1.26)]
    parts.extend(wavy_stroke("LAB17_FCurve_HandleEvidence", curve_points, mats["gold"], 0.007, "graph_editor_fcurve_evidence", "BH-326"))
    for point in [curve_points[1], curve_points[3]]:
        parts.append(cyl_between(f"LAB17_FCurve_TangentHandle_{len(parts)}", (point[0] - 0.11, -0.090, point[2] - 0.05), (point[0] + 0.11, -0.090, point[2] + 0.05), 0.004, mats["white"], vertices=8, role="graph_editor_fcurve_evidence", bh="BH-326"))
    for index, mode in enumerate(["cycle", "linear", "constant", "cleanup"]):
        parts.append(rounded_box(f"LAB17_EndpointPolicy_{mode}", (0.17, 0.030, 0.070), (-0.58 + index * 0.22, -0.078, 0.72), mats[["green", "cyan", "violet", "red"][index]], 0.010, role="extrapolation_endpoint_policy", bh="BH-327"))
    sway = sphere("LAB17_SwayPhase_AnimatedControl", (0.44, -0.078, 1.28), 0.046, mats["magenta"], segments=16, role="procedural_sway_phase_controls", bh="BH-328")
    parts.append(sway)
    parts.append(cyl_between("LAB17_Sway_AmplitudeRail", (0.34, -0.090, 0.95), (0.56, -0.090, 1.42), 0.006, mats["magenta"], vertices=8, role="procedural_sway_phase_controls", bh="BH-328"))
    for frame, z in ((1, 1.05), (48, 1.38), (96, 1.05)):
        bpy.context.scene.frame_set(frame)
        sway.location = (0.44, -0.078, z)
        sway.keyframe_insert(data_path="location", frame=frame)
    loop_slider = sphere("LAB17_LoopProof_EndpointSlider", (-0.50, -0.082, 0.48), 0.040, mats["green"], segments=16, role="seamless_loop_frame_proof", bh="BH-329")
    parts.append(loop_slider)
    parts.append(cyl_between("LAB17_LoopProof_FirstLastRail", (-0.62, -0.092, 0.48), (0.18, -0.092, 0.48), 0.006, mats["green"], vertices=8, role="seamless_loop_frame_proof", bh="BH-329"))
    parts.append(torus("LAB17_LoopProof_PhaseRing", (0.34, -0.080, 0.48), 0.090, 0.006, mats["cyan"], role="seamless_loop_frame_proof", bh="BH-329"))
    for frame, x in ((1, -0.50), (48, 0.08), (96, -0.50)):
        bpy.context.scene.frame_set(frame)
        loop_slider.location = (x, -0.082, 0.48)
        loop_slider.keyframe_insert(data_path="location", frame=frame)
    addon = rounded_box("LAB17_AnimationAddon_ManualProofGate", (0.32, 0.030, 0.080), (0.48, -0.078, 0.72), mats["violet"], 0.012, role="animation_addon_manual_proof", bh="BH-332")
    parts.append(addon)
    add_text("LAB17_AnimChip_FCurves", "f-curve handles + channels", (-0.15, -0.095, 1.55), 0.034, mats["gold"])
    add_text("LAB17_AnimChip_Loop", "first frame == last frame", (-0.10, -0.095, 0.30), 0.034, mats["green"])
    return parts


def build_camera_motion_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB17_MotionPanel_Backplate", "MOTION BLUR / CAMERA CUTS", (1.96, 0.06, 1.02), (1.40, 0.08, 1.08), "panel")
    shutter = rounded_box("LAB17_MotionBlur_ShutterControl", (0.40, 0.030, 0.085), (1.55, -0.078, 1.35), mats["orange"], 0.012, role="motion_blur_object_policy", bh="BH-330")
    samples = rounded_box("LAB17_MotionBlur_SampleBudget", (0.28, 0.030, 0.085), (2.02, -0.078, 1.35), mats["gold"], 0.012, role="motion_blur_object_policy", bh="BH-330")
    exclude = rounded_box("LAB17_MotionBlur_ObjectExclusion", (0.34, 0.030, 0.085), (2.26, -0.078, 1.18), mats["red"], 0.012, role="motion_blur_object_policy", bh="BH-330")
    parts.extend([shutter, samples, exclude])
    parts.extend(arrow("LAB17_MotionBlur_SmearDirection", (1.35, -0.085, 1.12), (2.30, -0.085, 1.12), mats["orange"], radius=0.006, role="motion_blur_object_policy", bh="BH-330"))
    for index, x in enumerate([1.45, 1.75, 2.05, 2.35]):
        parts.append(rounded_box(f"LAB17_CameraCut_Marker_{index+1}", (0.11, 0.030, 0.16), (x, -0.078, 0.78), mats[["cyan", "green", "magenta", "white"][index]], 0.010, role="camera_cut_timeline_notes", bh="BH-331"))
    parts.append(cyl_between("LAB17_CameraCut_TimelineRail", (1.35, -0.092, 0.60), (2.46, -0.092, 0.60), 0.006, mats["white"], vertices=8, role="camera_cut_timeline_notes", bh="BH-331"))
    parts.append(rounded_box("LAB17_CameraCut_ContinuityNote", (0.42, 0.030, 0.075), (1.84, -0.080, 0.44), mats["green"], 0.010, role="camera_cut_timeline_notes", bh="BH-331"))
    add_text("LAB17_MotionChip_Blur", "shutter samples exclusions", (1.94, -0.095, 1.55), 0.034, mats["orange"])
    add_text("LAB17_MotionChip_Cuts", "markers + frame ranges", (1.90, -0.095, 0.30), 0.034, mats["cyan"])
    return parts


def build_asset_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB17_AssetPanel_Backplate", "ASSET LIBRARY / GLB HANDOFF", (0.00, 0.08, 0.15), (4.05, 0.08, 0.62), "panel_green")
    for index, (label, color) in enumerate([("catalog", "blue"), ("tags", "cyan"), ("thumb", "gold"), ("license", "green"), ("version", "violet")]):
        parts.append(rounded_box(f"LAB17_AssetCatalog_{label}", (0.22, 0.030, 0.075), (-1.82 + index * 0.27, -0.078, 0.42), mats[color], 0.010, role="asset_browser_catalog_discipline", bh="BH-333"))
    for index, (label, color) in enumerate([("material", "orange"), ("scale", "white"), ("path", "cyan"), ("override", "magenta"), ("anim", "green")]):
        parts.append(rounded_box(f"LAB17_CrossFileDependency_{label}", (0.18, 0.030, 0.065), (-0.42 + index * 0.22, -0.078, 0.43), mats[color], 0.010, role="cross_file_dependency_checks", bh="BH-334"))
    switch = sphere("LAB17_AssetSwitch_IndexSlider_Animated", (0.85, -0.080, 0.42), 0.042, mats["magenta"], segments=16, role="asset_switch_realization_gates", bh="BH-335")
    parts.append(switch)
    parts.append(cyl_between("LAB17_AssetSwitch_RealizationRail", (0.64, -0.092, 0.42), (1.20, -0.092, 0.42), 0.006, mats["magenta"], vertices=8, role="asset_switch_realization_gates", bh="BH-335"))
    for frame, x in ((1, 0.70), (48, 1.10), (96, 0.70)):
        bpy.context.scene.frame_set(frame)
        switch.location = (x, -0.080, 0.42)
        switch.keyframe_insert(data_path="location", frame=frame)
    parts.append(rounded_box("LAB17_MaterialReuse_DuplicateCleanup", (0.34, 0.030, 0.075), (1.44, -0.078, 0.42), mats["orange"], 0.012, role="material_reuse_duplicate_cleanup", bh="BH-336"))
    parts.append(rounded_box("LAB17_GLBOptimization_PrePostRegression", (0.37, 0.030, 0.075), (1.86, -0.078, 0.42), mats["green"], 0.012, role="glb_optimization_visual_regression", bh="BH-337"))
    parts.append(rounded_box("LAB17_TextureExport_RelinkQA", (0.32, 0.030, 0.075), (2.27, -0.078, 0.42), mats["blue"], 0.012, role="texture_export_relink_qa", bh="BH-338"))
    scatter_points = [(1.80, -0.092, 0.18), (2.05, -0.092, 0.25), (2.32, -0.092, 0.18), (2.55, -0.092, 0.30)]
    for index, point in enumerate(scatter_points):
        parts.append(sphere(f"LAB17_PhysicsScatter_SeedInstance_{index+1}", point, 0.030, mats[["green", "cyan", "gold", "magenta"][index]], segments=12, role="physics_scatter_bake_cleanup", bh="BH-339"))
    parts.append(rounded_box("LAB17_PhysicsScatter_BakeCleanupGate", (0.42, 0.030, 0.070), (2.28, -0.078, 0.12), mats["violet"], 0.010, role="physics_scatter_bake_cleanup", bh="BH-339"))
    add_text("LAB17_AssetChip_Catalog", "catalog tags thumbs license", (-1.24, -0.095, 0.58), 0.034, mats["white"])
    add_text("LAB17_AssetChip_GLB", "realize optimize relink bake", (1.75, -0.095, 0.58), 0.034, mats["green"])
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    setup_lights()
    setup_camera()
    root = make_root()
    objects: list[bpy.types.Object] = []
    objects.append(rounded_box("LAB17_BaseAnimationAssetStage", (4.90, 0.13, 1.88), (0.0, 0.13, 0.74), mats["base"], 0.055, role="stage_base", export=True))
    add_text("LAB17_Title", "Blender Shorts Animation / Line Art / Asset Lab v17", (0.0, -0.11, 1.80), 0.081, mats["white"])
    add_text("LAB17_Subtitle", "grease pencil  f-curves  loops  motion blur  asset browser  GLB handoff", (0.0, -0.11, 1.66), 0.044, mats["cyan"])
    objects.extend(build_line_art_zone(mats))
    objects.extend(build_animation_zone(mats))
    objects.extend(build_camera_motion_zone(mats))
    objects.extend(build_asset_zone(mats))
    for index, info in enumerate(APPLIED_LIFEHACKS):
        row = index // 10
        col = index % 10
        objects.append(rounded_box(
            f"LAB17_AppliedTick_{info['id']}",
            (0.18, 0.025, 0.045),
            (-2.16 + col * 0.47, -0.075, -0.08 + row * 0.11),
            mats["green"] if row == 0 else mats["cyan"],
            0.006,
            role="applied_lifehack_tick",
            bh=info["id"],
            export=True,
        ))
    for obj in objects:
        parent_keep_world(obj, root)
    return {
        "export_object_names": [obj.name for obj in exportable_objects()],
        "non_exported_helper_names": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False],
    }


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
        "line_art_layer_ownership",
        "comic_outline_thickness_budget",
        "grease_pencil_frame_range_cleanup",
        "boiling_line_loop_discipline",
        "imported_sketch_source_scale",
        "glow_outline_emission_controls",
        "graph_editor_fcurve_evidence",
        "extrapolation_endpoint_policy",
        "procedural_sway_phase_controls",
        "seamless_loop_frame_proof",
        "motion_blur_object_policy",
        "camera_cut_timeline_notes",
        "animation_addon_manual_proof",
        "asset_browser_catalog_discipline",
        "cross_file_dependency_checks",
        "asset_switch_realization_gates",
        "material_reuse_duplicate_cleanup",
        "glb_optimization_visual_regression",
        "texture_export_relink_qa",
        "physics_scatter_bake_cleanup",
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
        "LAB17_Root_TurntableAnimated",
        "LAB17_SwayPhase_AnimatedControl",
        "LAB17_LoopProof_EndpointSlider",
        "LAB17_AssetSwitch_IndexSlider_Animated",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        errors.append(f"Expected animated animation/asset QA markers missing: {missing_anim}")
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
        "source_goal": "950-source Blender Shorts checkpoint test asset.",
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
            "Line Art/Grease Pencil layer ownership, cleanup, boiling lines and glow controls are visible.",
            "Graph editor F-curve evidence, extrapolation policy, sway phase controls and loop proof are visible.",
            "Motion blur object policy and camera-cut timeline notes are visible.",
            "Asset Browser catalog discipline, cross-file dependencies, asset switching and material reuse are visible.",
            "GLB optimization, texture relink and physics scatter bake/cleanup policy are visible.",
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
