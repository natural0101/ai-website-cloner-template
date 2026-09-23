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

ASSET = "blender_shorts_lifehack_lab_v7"
SCENE_NAME = "BlenderShortsLifehackLabV7"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-133", "name": "Render Passes Are Contracts", "applied": "Mist, depth, mask and ID pass cards show planned deliverables."},
    {"id": "BH-134", "name": "Cryptomatte Needs Clean IDs", "applied": "Cryptomatte swatches are paired with named object/material ID chips."},
    {"id": "BH-135", "name": "Glow Is A Two-Stage Effect", "applied": "Emitter source, glare threshold and background checks are separate objects."},
    {"id": "BH-136", "name": "Denoise Must Preserve Detail", "applied": "Sample/denoise comparison bars include small detail check marks."},
    {"id": "BH-137", "name": "Color Management Needs Clipping Checks", "applied": "Exposure/look cards include a clipping meter."},
    {"id": "BH-138", "name": "Light Groups And Links Need Intent", "applied": "Light-group chips point to specific hero objects."},
    {"id": "BH-139", "name": "Comp Stacks Need Source Layers", "applied": "Layer stack separates source, mask, grade and final composite cards."},
    {"id": "BH-140", "name": "Camera Focus Needs A Named Target", "applied": "Camera focus target and focus-distance rail are visible."},
    {"id": "BH-141", "name": "Camera Paths Need Bakeable Controls", "applied": "Camera path, speed ticks and target lock are visible."},
    {"id": "BH-142", "name": "Orbit Cameras Need Loop Checks", "applied": "Orbit ring includes first/last frame markers."},
    {"id": "BH-143", "name": "Path Motion Needs Orientation Review", "applied": "Path object has banking/up-axis arrows."},
    {"id": "BH-144", "name": "Texture Transitions Need Masks", "applied": "Material transition card has start/end state and mask slider."},
    {"id": "BH-145", "name": "Procedural Surface Detail Needs Scale QA", "applied": "Close/far texture scale chips compare grid/rust/dust readability."},
    {"id": "BH-146", "name": "Edge Wear Is A Mask Pass", "applied": "Edge wear is represented as a controlled mask chip, not random dirt."},
    {"id": "BH-147", "name": "Bake What The Viewer Cannot Rebuild", "applied": "Bake/export cards list color, roughness, normal and opacity outputs."},
    {"id": "BH-148", "name": "Version-Specific Render Tricks Need Notes", "applied": "Version note card records Blender/render workflow assumption."},
    {"id": "BH-149", "name": "Highlight Control Beats Exposure Guessing", "applied": "Emitter strength, glare threshold and highlight compression are separated."},
    {"id": "BH-150", "name": "Post Flexibility Starts In The Scene", "applied": "Named passes, IDs, light groups and masks converge into a final comp board."},
]


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
        "base": make_mat("Lab7_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.58),
        "panel": make_mat("Lab7_PanelInk", (0.070, 0.084, 0.118, 1.0), roughness=0.62),
        "mist": make_mat("Lab7_MistDepthBlue", (0.12, 0.38, 0.92, 1.0), roughness=0.46),
        "mask": make_mat("Lab7_MaskGreen", (0.14, 0.86, 0.42, 1.0), roughness=0.48, emission=(0.02, 0.34, 0.10, 1.0), emission_strength=0.08),
        "crypto": make_mat("Lab7_CryptoMagenta", (1.0, 0.16, 0.58, 1.0), roughness=0.36, emission=(0.58, 0.02, 0.26, 1.0), emission_strength=0.12),
        "glow": make_mat("Lab7_EmitterGlowAmber", (1.0, 0.58, 0.08, 1.0), roughness=0.22, emission=(1.0, 0.34, 0.02, 1.0), emission_strength=0.65),
        "cyan": make_mat("Lab7_ControlCyan", (0.04, 0.78, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.34, 0.78, 1.0), emission_strength=0.12),
        "violet": make_mat("Lab7_OrbitViolet", (0.56, 0.28, 1.0, 1.0), roughness=0.34, emission=(0.26, 0.08, 0.74, 1.0), emission_strength=0.12),
        "gold": make_mat("Lab7_BakeGold", (1.0, 0.70, 0.16, 1.0), roughness=0.40, metallic=0.08),
        "rust": make_mat("Lab7_RustWear", (0.72, 0.30, 0.12, 1.0), roughness=0.70),
        "dust": make_mat("Lab7_DustShader", (0.76, 0.72, 0.58, 1.0), roughness=0.88),
        "white": make_mat("Lab7_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
        "ghost": make_mat("Lab7_DebugGhost", (0.42, 0.68, 1.0, 1.0), roughness=0.55, alpha=0.28, emission=(0.05, 0.20, 0.50, 1.0), emission_strength=0.06),
        "black": make_mat("Lab7_LineBlack", (0.02, 0.018, 0.016, 1.0), roughness=0.50),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB7_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.02,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "rounded_box",
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB7_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB7_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export)


def sphere(
    name: str,
    radius: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    segments: int = 20,
    ring_count: int = 10,
    scale: tuple[float, float, float] = (1, 1, 1),
    role: str = "sphere",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transform(obj)
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    vertices: int = 24,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "cylinder",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def torus(
    name: str,
    major: float,
    minor: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    rot: tuple[float, float, float] = (0, 0, 0),
    role: str = "ring",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=60, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def cone_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius1: float,
    radius2: float,
    mat: bpy.types.Material,
    vertices: int = 18,
    role: str = "cone_between",
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
    return tag(obj, role)


def arrow(name: str, start: tuple[float, float, float], end: tuple[float, float, float], mat: bpy.types.Material, radius: float = 0.012, role: str = "direction_arrow") -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    mid = a.lerp(b, 0.76)
    return [
        cone_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, radius, mat, role=role),
        cone_between(f"{name}_Head", tuple(mid), tuple(b), radius * 2.7, 0.0, mat, role=role),
    ]


def curve_line(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float = 0.009, role: str = "curve_line") -> bpy.types.Object:
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
    return tag(obj, role)


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
    scene.world = scene.world or bpy.data.worlds.new("LAB7_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.8, -4.8, 4.6))
    key = bpy.context.object
    key.name = "LAB7_KeyArea_Warm"
    key.data.energy = 570
    key.data.size = 4.8
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.8, 2.4, 3.2))
    fill = bpy.context.object
    fill.name = "LAB7_FillArea_Cool"
    fill.data.energy = 115
    fill.data.size = 5.2
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.9, 2.8, 2.4))
    rim = bpy.context.object
    rim.name = "LAB7_RimPoint_Cyan"
    rim.data.energy = 220
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.35, -5.75, 3.25), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB7_Camera_Hero3Q"
    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 9.5
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


def create_pass_crypto_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB7_RenderPassContractBoard", (1.32, 0.08, 0.72), (-1.46, -0.78, 0.42), mats["panel"], 0.025, role="render_pass_contract_board")
    parts.append(panel)
    specs = [
        ("Mist", mats["mist"], -1.88, 0.58),
        ("Depth", mats["cyan"], -1.58, 0.46),
        ("Mask", mats["mask"], -1.28, 0.34),
        ("Crypto", mats["crypto"], -0.98, 0.22),
    ]
    for name, mat, x, z in specs:
        card = rounded_box(f"LAB7_RenderPassCard_{name}", (0.22, 0.035, 0.30), (x, -0.84, z), mat, 0.012, role="render_pass_card")
        chip = sphere(f"LAB7_CryptomatteCleanIDChip_{name}", 0.035, (x, -0.90, z + 0.18), mat, segments=12, ring_count=6, role="cryptomatte_id_chip")
        parts.extend([card, chip])
    stack_labels = [
        ("SRC", -1.91, 0.10, mats["mist"]),
        ("MASK", -1.70, 0.10, mats["mask"]),
        ("GRADE", -1.49, 0.10, mats["crypto"]),
        ("FINAL", -1.28, 0.10, mats["gold"]),
    ]
    for name, x, z, mat in stack_labels:
        layer = rounded_box(f"LAB7_CompositingLayerStack_{name}", (0.16, 0.035, 0.10), (x, -0.58, z), mat, 0.008, role="compositing_layer_stack")
        parts.append(layer)
    return parts


def create_glow_color_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB7_GlowColorManagementBoard", (1.10, 0.08, 0.72), (-0.18, -0.78, 0.42), mats["panel"], 0.025, role="glow_color_board")
    parts.append(panel)
    emitter = sphere("LAB7_EmitterSource_SeparateBrightness", 0.12, (-0.48, -0.84, 0.54), mats["glow"], segments=24, ring_count=12, role="glow_emitter_source")
    glare_ring = torus("LAB7_CompositorGlareThreshold_Ring", 0.26, 0.010, (-0.48, -0.84, 0.54), mats["gold"], rot=(math.radians(90), 0, 0), role="glow_compositor_threshold")
    background_check = rounded_box("LAB7_GlowBackgroundCheck_DarkLightSplit", (0.28, 0.035, 0.34), (-0.07, -0.84, 0.46), mats["ghost"], 0.012, role="glow_background_check")
    parts.extend([emitter, glare_ring, background_check])
    for i, (name, height, mat) in enumerate((("Samples", 0.22, mats["cyan"]), ("Denoise", 0.30, mats["mask"]), ("Detail", 0.17, mats["crypto"]))):
        bar = rounded_box(f"LAB7_DenoiseDetailCompare_{name}", (0.09, 0.035, height), (0.28 + i * 0.12, -0.80, 0.10 + height / 2), mat, 0.008, role="denoise_detail_compare")
        parts.append(bar)
    meter = rounded_box("LAB7_ColorClippingMeter_Base", (0.42, 0.035, 0.055), (-0.22, -0.58, 0.14), mats["white"], 0.008, role="color_clipping_meter")
    parts.append(meter)
    for i, mat in enumerate((mats["mask"], mats["gold"], mats["crypto"])):
        tick = rounded_box(f"LAB7_ColorClippingMeter_Tick_{i}", (0.045, 0.040, 0.11 + i * 0.035), (-0.36 + i * 0.14, -0.58, 0.20 + i * 0.018), mat, 0.006, role="color_clipping_meter")
        parts.append(tick)
    note = rounded_box("LAB7_RenderVersionNote_Blender51", (0.30, 0.035, 0.15), (0.34, -0.58, 0.18), mats["violet"], 0.010, role="version_render_note")
    parts.append(note)
    return parts


def create_light_camera_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB7_LightCameraRigBoard", (1.34, 0.08, 0.72), (1.18, -0.78, 0.42), mats["panel"], 0.025, role="light_camera_rig_board")
    parts.append(panel)
    hero = sphere("LAB7_HeroObject_LinkedLightTarget", 0.10, (0.74, -0.84, 0.45), mats["mask"], segments=20, ring_count=10, role="light_group_target_object")
    parts.append(hero)
    for i, (x, mat) in enumerate(((0.48, mats["gold"]), (0.70, mats["cyan"]), (0.92, mats["crypto"]))):
        light_chip = sphere(f"LAB7_LightGroupIntentChip_{i}", 0.045, (x, -0.82, 0.66), mat, segments=12, ring_count=6, role="light_group_intent_chip")
        parts.append(light_chip)
        parts.extend(arrow(f"LAB7_LightLinkDirection_{i}", (x, -0.82, 0.62), (0.74, -0.84, 0.50), mat, radius=0.007, role="light_linking_intent"))
    focus_target = sphere("LAB7_CameraFocusTarget_Named", 0.050, (1.18, -0.82, 0.46), mats["violet"], role="camera_focus_target")
    focus_rail = rounded_box("LAB7_CameraFocusDistanceRail", (0.54, 0.035, 0.035), (1.18, -0.82, 0.24), mats["ghost"], 0.006, role="camera_focus_target")
    parts.extend([focus_target, focus_rail])
    orbit = torus("LAB7_CameraOrbitLoopCheck_Ring", 0.32, 0.008, (1.48, -0.82, 0.44), mats["violet"], rot=(math.radians(90), 0, 0), role="camera_orbit_loop_check")
    first = sphere("LAB7_OrbitFirstFrameMarker", 0.030, (1.16, -0.82, 0.44), mats["mask"], segments=10, ring_count=5, role="camera_orbit_loop_check")
    last = sphere("LAB7_OrbitLastFrameMarker", 0.030, (1.80, -0.82, 0.44), mats["gold"], segments=10, ring_count=5, role="camera_orbit_loop_check")
    parts.extend([orbit, first, last])
    path_pts = [(1.02, -0.58, 0.14), (1.20, -0.56, 0.28), (1.46, -0.56, 0.23), (1.70, -0.58, 0.36)]
    path = curve_line("LAB7_CameraPath_BakeableCurve", path_pts, mats["cyan"], 0.008, role="camera_path_control")
    parts.append(path)
    for i, p in enumerate(path_pts):
        tick = rounded_box(f"LAB7_CameraPathSpeedTick_{i}", (0.045, 0.035, 0.09 + i * 0.025), (p[0], p[1] - 0.03, p[2] + 0.08), mats["gold"], 0.006, role="camera_path_control")
        parts.append(tick)
    for i, (start, end) in enumerate((((1.72, -0.66, 0.18), (1.86, -0.68, 0.30)), ((1.66, -0.70, 0.33), (1.80, -0.72, 0.48)))):
        parts.extend(arrow(f"LAB7_PathBankingUpAxis_{i}", start, end, mats["crypto"], radius=0.008, role="path_orientation_review"))
    return parts


def create_material_bake_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB7_MaterialBakeDeliveryBoard", (2.05, 0.08, 0.78), (-0.12, 0.48, 0.42), mats["panel"], 0.025, role="material_bake_delivery_board")
    parts.append(panel)
    start = rounded_box("LAB7_TextureTransition_StartState", (0.20, 0.035, 0.28), (-0.98, 0.42, 0.52), mats["mist"], 0.012, role="texture_transition_mask")
    mask = rounded_box("LAB7_TextureTransition_NamedMask", (0.28, 0.035, 0.08), (-0.70, 0.42, 0.34), mats["mask"], 0.008, role="texture_transition_mask")
    end = rounded_box("LAB7_TextureTransition_EndState", (0.20, 0.035, 0.28), (-0.42, 0.42, 0.52), mats["rust"], 0.012, role="texture_transition_mask")
    parts.extend([start, mask, end])
    for i, (name, x, mat) in enumerate((("Grid", -0.12, mats["cyan"]), ("Rust", 0.08, mats["rust"]), ("Dust", 0.28, mats["dust"]))):
        close = rounded_box(f"LAB7_SurfaceScaleQA_{name}_Close", (0.12, 0.035, 0.22), (x, 0.42, 0.56), mat, 0.008, role="procedural_surface_scale_qa")
        far = rounded_box(f"LAB7_SurfaceScaleQA_{name}_Far", (0.12, 0.035, 0.09), (x, 0.42, 0.28), mat, 0.006, role="procedural_surface_scale_qa")
        parts.extend([close, far])
    wear_base = rounded_box("LAB7_EdgeWearMaskPass_Base", (0.35, 0.035, 0.28), (0.68, 0.42, 0.50), mats["mist"], 0.012, role="edge_wear_mask_pass")
    parts.append(wear_base)
    for i, z in enumerate((0.40, 0.54, 0.64)):
        edge = curve_line(f"LAB7_EdgeWearControlledMaskLine_{i}", [(0.52, 0.39, z), (0.84, 0.39, z + 0.02)], mats["gold"], 0.006, role="edge_wear_mask_pass")
        parts.append(edge)
    bake_specs = [("Color", 1.08, mats["mask"]), ("Rough", 1.25, mats["dust"]), ("Normal", 1.42, mats["violet"]), ("Opacity", 1.59, mats["ghost"])]
    for name, x, mat in bake_specs:
        card = rounded_box(f"LAB7_TextureBakeExportCard_{name}", (0.13, 0.035, 0.20), (x, 0.42, 0.47), mat, 0.010, role="texture_bake_export_card")
        parts.append(card)
    normal_light = torus("LAB7_NormalMapMovingLightCheck", 0.15, 0.008, (1.42, 0.41, 0.70), mats["gold"], rot=(math.radians(90), 0, 0), role="normal_map_light_check")
    parts.append(normal_light)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB7_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB7_StudioFloor_NotExported", (4.9, 3.25, 0.065), (0.0, -0.08, -0.045), mats["base"], 0.04, export=False, role="preview_floor")
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_pass_crypto_board(mats))
    export_parts.extend(create_glow_color_board(mats))
    export_parts.extend(create_light_camera_board(mats))
    export_parts.extend(create_material_bake_board(mats))
    labels = [
        add_text("LAB7_Label_Passes", "PASSES + CRYPTOMATTE", (-1.46, -1.18, 0.82), 0.052, mats["white"]),
        add_text("LAB7_Label_Glow", "GLOW + CLIPPING QA", (-0.16, -1.18, 0.82), 0.052, mats["white"]),
        add_text("LAB7_Label_LightCamera", "LIGHT GROUPS + CAMERA PATH", (1.20, -1.18, 0.82), 0.052, mats["white"]),
        add_text("LAB7_Label_Materials", "MASKS + BAKE DELIVERY", (-0.10, 0.13, 0.92), 0.052, mats["white"]),
    ]
    helper_parts.extend(labels)
    for obj in export_parts + helper_parts:
        parent_keep_world(obj, root)

    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path="rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.tau)
    root.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize(root)
    for obj in bpy.data.objects:
        if obj.name == "LAB7_EmitterSource_SeparateBrightness":
            obj.scale = (1, 1, 1)
            obj.keyframe_insert(data_path="scale", frame=1)
            obj.scale = (1.18, 1.18, 1.18)
            obj.keyframe_insert(data_path="scale", frame=48)
            obj.scale = (1, 1, 1)
            obj.keyframe_insert(data_path="scale", frame=96)
            linearize(obj)
        if obj.name == "LAB7_CameraOrbitLoopCheck_Ring":
            obj.rotation_euler.z = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = math.tau
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
        if obj.name == "LAB7_NormalMapMovingLightCheck":
            obj.rotation_euler.y = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.y = math.tau
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
    if triangles > 45000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 45000.")
    roles = sorted({str(obj.get("role")) for obj in objects if obj.get("role")})
    required_roles = {
        "render_pass_card",
        "cryptomatte_id_chip",
        "compositing_layer_stack",
        "glow_emitter_source",
        "glow_compositor_threshold",
        "denoise_detail_compare",
        "color_clipping_meter",
        "light_group_intent_chip",
        "light_linking_intent",
        "camera_focus_target",
        "camera_path_control",
        "camera_orbit_loop_check",
        "path_orientation_review",
        "texture_transition_mask",
        "procedural_surface_scale_qa",
        "edge_wear_mask_pass",
        "texture_bake_export_card",
        "normal_map_light_check",
        "version_render_note",
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
    if "LAB7_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
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
        "source_goal": "450-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Render pass and Cryptomatte cards are visible.",
            "Glow chain separates emitter, glare threshold and highlight checks.",
            "Denoise/color clipping QA is represented by comparison bars and meter.",
            "Light group/linking intent and camera path/focus controls are visible.",
            "Material masks, edge wear and bake/export cards are grouped.",
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
