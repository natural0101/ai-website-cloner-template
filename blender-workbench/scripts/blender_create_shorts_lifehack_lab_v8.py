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

ASSET = "blender_shorts_lifehack_lab_v8"
SCENE_NAME = "BlenderShortsLifehackLabV8"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-151", "name": "Live Unwrap Is A Diagnostic Loop", "applied": "Seam board shows unwrap iteration and distortion checks."},
    {"id": "BH-152", "name": "Texel Density Is A Visual Consistency Gate", "applied": "Texel-density bars compare hero/detail scale."},
    {"id": "BH-153", "name": "UV Packing Needs Margin", "applied": "UV island board includes padding/margin markers."},
    {"id": "BH-154", "name": "UV Overlap Must Be Intentional", "applied": "Overlap warning chip separates intended mirror overlap from accidental overlap."},
    {"id": "BH-155", "name": "Texture Export Needs Image Accountability", "applied": "Texture output cards list packed/external image checks."},
    {"id": "BH-156", "name": "Bake Setup Needs Source And Target Names", "applied": "Bake board names high/low source, target UV and cage assumptions."},
    {"id": "BH-157", "name": "Material Atlases Need Remap QA", "applied": "Atlas remap cards show material slots before and after join."},
    {"id": "BH-158", "name": "Paint Isolation Starts In Mesh Organization", "applied": "Paint isolation chips show material IDs and geometry masks."},
    {"id": "BH-159", "name": "Spherical Seams Need View-Aware Placement", "applied": "Sphere seam ring is hidden from the front hero side."},
    {"id": "BH-160", "name": "Position Passes Need Stable Coordinates", "applied": "Coordinate axes and origin lock card mark position-pass assumptions."},
    {"id": "BH-161", "name": "Normal Bakes Need Moving-Light Review", "applied": "Normal-bake board includes rotating light-check ring."},
    {"id": "BH-162", "name": "Sculpt Detail Needs An Export Cage", "applied": "Dense sculpt proxy is paired with lower-poly cage lines."},
    {"id": "BH-163", "name": "Weighted Normals Are Shading QA", "applied": "Bevel/weighted-normal blocks are checked by grazing-light arrows."},
    {"id": "BH-164", "name": "Fix Normals Before Materials", "applied": "Normal reset and smoothing order is represented before material cards."},
    {"id": "BH-165", "name": "Straight Edges Support Everything Downstream", "applied": "Straight-edge cleanup rail feeds bevel and UV boards."},
    {"id": "BH-166", "name": "Origins Are Export And Animation Controls", "applied": "Origin markers sit at intended pivots on animated props."},
    {"id": "BH-167", "name": "Pivots Need Transform QA", "applied": "Pivot QA dials show transform/pivot verification."},
    {"id": "BH-168", "name": "Face-Aligned Placement Needs Normal Checks", "applied": "Face-aligned prop includes normal direction and scale/origin checks."},
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
        "base": make_mat("Lab8_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.58),
        "panel": make_mat("Lab8_PanelInk", (0.070, 0.084, 0.118, 1.0), roughness=0.62),
        "uv_a": make_mat("Lab8_UVIslandBlue", (0.10, 0.44, 0.95, 1.0), roughness=0.50),
        "uv_b": make_mat("Lab8_UVIslandGreen", (0.14, 0.86, 0.42, 1.0), roughness=0.48),
        "uv_c": make_mat("Lab8_UVIslandGold", (1.0, 0.70, 0.16, 1.0), roughness=0.42, metallic=0.04),
        "warn": make_mat("Lab8_WarningMagenta", (1.0, 0.14, 0.56, 1.0), roughness=0.36, emission=(0.52, 0.02, 0.25, 1.0), emission_strength=0.12),
        "cyan": make_mat("Lab8_ControlCyan", (0.04, 0.78, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.32, 0.78, 1.0), emission_strength=0.12),
        "ghost": make_mat("Lab8_DebugGhost", (0.42, 0.68, 1.0, 1.0), roughness=0.55, alpha=0.28),
        "sculpt": make_mat("Lab8_SculptClay", (0.78, 0.48, 0.34, 1.0), roughness=0.74),
        "cage": make_mat("Lab8_ExportCageWhite", (0.92, 0.96, 1.0, 1.0), roughness=0.46),
        "metal": make_mat("Lab8_WeightedNormalMetal", (0.62, 0.70, 0.78, 1.0), roughness=0.32, metallic=0.36),
        "origin": make_mat("Lab8_OriginRed", (1.0, 0.12, 0.09, 1.0), roughness=0.32, emission=(0.62, 0.02, 0.02, 1.0), emission_strength=0.10),
        "white": make_mat("Lab8_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB8_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(name: str, size: tuple[float, float, float], loc: tuple[float, float, float], mat: bpy.types.Material, bevel: float = 0.02, rot: tuple[float, float, float] = (0, 0, 0), role: str = "rounded_box", export: bool = True) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB8_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB8_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export)


def sphere(name: str, radius: float, loc: tuple[float, float, float], mat: bpy.types.Material, segments: int = 20, ring_count: int = 10, scale: tuple[float, float, float] = (1, 1, 1), role: str = "sphere") -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transform(obj)
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def cylinder(name: str, radius: float, depth: float, loc: tuple[float, float, float], mat: bpy.types.Material, vertices: int = 24, rot: tuple[float, float, float] = (0, 0, 0), role: str = "cylinder") -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def torus(name: str, major: float, minor: float, loc: tuple[float, float, float], mat: bpy.types.Material, rot: tuple[float, float, float] = (0, 0, 0), role: str = "ring") -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=56, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role)


def cone_between(name: str, start: tuple[float, float, float], end: tuple[float, float, float], radius1: float, radius2: float, mat: bpy.types.Material, vertices: int = 18, role: str = "cone_between") -> bpy.types.Object:
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


def curve_line(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float = 0.008, role: str = "curve_line") -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 10
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
    scene.world = scene.world or bpy.data.worlds.new("LAB8_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.8, -4.8, 4.6))
    key = bpy.context.object
    key.name = "LAB8_KeyArea_Warm"
    key.data.energy = 570
    key.data.size = 4.8
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.8, 2.4, 3.2))
    fill = bpy.context.object
    fill.name = "LAB8_FillArea_Cool"
    fill.data.energy = 115
    fill.data.size = 5.2
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.9, 2.8, 2.4))
    rim = bpy.context.object
    rim.name = "LAB8_RimPoint_Cyan"
    rim.data.energy = 220
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.35, -5.75, 3.25), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB8_Camera_Hero3Q"
    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 9.0
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


def create_uv_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB8_UVUnwrapQABoard", (1.36, 0.08, 0.78), (-1.42, -0.78, 0.44), mats["panel"], 0.025, role="uv_unwrap_qa_board")
    parts.append(panel)
    island_specs = [
        ("A", -1.86, 0.55, mats["uv_a"], (0.22, 0.035, 0.28)),
        ("B", -1.55, 0.38, mats["uv_b"], (0.24, 0.035, 0.20)),
        ("C", -1.22, 0.53, mats["uv_c"], (0.20, 0.035, 0.30)),
        ("D", -0.98, 0.26, mats["warn"], (0.16, 0.035, 0.16)),
    ]
    for name, x, z, mat, size in island_specs:
        island = rounded_box(f"LAB8_UVIsland_{name}_PackedWithMargin", size, (x, -0.84, z), mat, 0.010, role="uv_margin_pack_card")
        parts.append(island)
    for x in (-1.70, -1.38, -1.12):
        parts.append(curve_line(f"LAB8_LiveUnwrapSeamDiagnostic_{x:.2f}", [(x, -0.88, 0.18), (x + 0.06, -0.88, 0.66)], mats["cyan"], 0.006, role="uv_seam_diagnostic"))
    overlap = torus("LAB8_UVOverlapIntentionalMarker", 0.09, 0.006, (-0.94, -0.84, 0.50), mats["warn"], rot=(math.radians(90), 0, 0), role="uv_overlap_intent")
    parts.append(overlap)
    sphere_obj = sphere("LAB8_SphericalSeamHiddenFromHero", 0.12, (-1.82, -0.56, 0.16), mats["uv_b"], segments=20, ring_count=10, role="spherical_hidden_seam")
    seam_ring = torus("LAB8_SphericalHiddenSeam_BackRing", 0.12, 0.006, (-1.82, -0.585, 0.16), mats["warn"], rot=(math.radians(90), 0, 0), role="spherical_hidden_seam")
    parts.extend([sphere_obj, seam_ring])
    for i, height in enumerate((0.12, 0.20, 0.30, 0.18)):
        bar = rounded_box(f"LAB8_TexelDensityScaleBar_{i}", (0.08, 0.035, height), (-1.50 + i * 0.15, -0.56, 0.08 + height / 2), mats["uv_c"], 0.006, role="texel_density_gate")
        parts.append(bar)
    return parts


def create_bake_export_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB8_BakeExportAccountabilityBoard", (1.30, 0.08, 0.78), (-0.12, -0.78, 0.44), mats["panel"], 0.025, role="bake_export_board")
    parts.append(panel)
    source = sphere("LAB8_BakeSourceHighPoly_Named", 0.12, (-0.52, -0.84, 0.56), mats["sculpt"], segments=24, ring_count=12, scale=(1.1, 0.8, 0.9), role="bake_source_target_name")
    target = rounded_box("LAB8_BakeTargetLowPoly_NamedUV", (0.24, 0.08, 0.24), (-0.18, -0.84, 0.48), mats["cage"], 0.018, role="bake_source_target_name")
    cage = torus("LAB8_BakeCageRayDistance_Check", 0.19, 0.007, (-0.18, -0.84, 0.48), mats["cyan"], rot=(math.radians(90), 0, 0), role="bake_cage_ray_check")
    parts.extend([source, target, cage])
    for i, (name, mat) in enumerate((("Color", mats["uv_a"]), ("Rough", mats["uv_b"]), ("Normal", mats["warn"]), ("Opacity", mats["ghost"]))):
        card = rounded_box(f"LAB8_TextureExportImageCard_{name}", (0.12, 0.035, 0.18), (0.20 + i * 0.16, -0.84, 0.42), mat, 0.008, role="texture_export_accountability")
        parts.append(card)
    for i, (x, mat) in enumerate(((-0.52, mats["uv_a"]), (-0.36, mats["uv_b"]), (-0.20, mats["uv_c"]))):
        slot = rounded_box(f"LAB8_MaterialAtlasRemapSlot_{i}", (0.12, 0.035, 0.11), (x, -0.56, 0.18), mat, 0.008, role="material_atlas_remap")
        parts.append(slot)
    for i, mat in enumerate((mats["uv_a"], mats["uv_b"], mats["uv_c"], mats["warn"])):
        chip = sphere(f"LAB8_PaintIsolationMaterialID_{i}", 0.035, (0.20 + i * 0.13, -0.56, 0.19), mat, segments=10, ring_count=5, role="paint_isolation_id")
        parts.append(chip)
    axes = [
        ((0.54, -0.58, 0.14), (0.72, -0.58, 0.14), mats["warn"]),
        ((0.54, -0.58, 0.14), (0.54, -0.58, 0.32), mats["uv_b"]),
        ((0.54, -0.58, 0.14), (0.54, -0.44, 0.14), mats["cyan"]),
    ]
    for i, (start, end, mat) in enumerate(axes):
        parts.extend(arrow(f"LAB8_PositionPassStableCoordinate_{i}", start, end, mat, radius=0.007, role="position_pass_coordinate"))
    return parts


def create_normals_sculpt_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB8_NormalsSculptQABoard", (1.34, 0.08, 0.78), (1.20, -0.78, 0.44), mats["panel"], 0.025, role="normal_sculpt_qa_board")
    parts.append(panel)
    sculpt = sphere("LAB8_SculptSourceDenseProxy", 0.18, (0.78, -0.84, 0.50), mats["sculpt"], segments=28, ring_count=14, scale=(1.15, 0.75, 0.9), role="sculpt_source_proxy")
    parts.append(sculpt)
    for z in (0.34, 0.50, 0.66):
        ring_pts = [(0.78 + math.cos(a) * 0.23, -0.84 + math.sin(a) * 0.035, z) for a in [math.tau * i / 28 for i in range(29)]]
        parts.append(curve_line(f"LAB8_ExportCageRetopoRing_{z:.2f}", ring_pts, mats["cage"], 0.006, role="export_cage_handoff"))
    bake_chip = rounded_box("LAB8_NormalBakeMovingLightReview", (0.20, 0.035, 0.22), (1.18, -0.84, 0.54), mats["warn"], 0.012, role="normal_bake_light_review")
    light_ring = torus("LAB8_NormalBakeMovingLightRing", 0.18, 0.007, (1.18, -0.84, 0.54), mats["uv_c"], rot=(math.radians(90), 0, 0), role="normal_bake_light_review")
    parts.extend([bake_chip, light_ring])
    for i, (x, mat) in enumerate(((1.48, mats["metal"]), (1.66, mats["metal"]), (1.84, mats["cage"]))):
        block = rounded_box(f"LAB8_BevelWeightedNormalBlock_{i}", (0.13, 0.11, 0.18 + i * 0.05), (x, -0.84, 0.30 + i * 0.025), mat, 0.020, rot=(0, 0, 0.12 * i), role="weighted_normal_bevel_check")
        parts.append(block)
    for i, (name, mat) in enumerate((("Reset", mats["warn"]), ("Sharp", mats["cyan"]), ("Smooth", mats["uv_b"]), ("Material", mats["uv_c"]))):
        step = rounded_box(f"LAB8_NormalFixOrder_{name}", (0.11, 0.035, 0.11), (0.88 + i * 0.16, -0.54, 0.16), mat, 0.008, role="normal_fix_order")
        parts.append(step)
    straight = curve_line("LAB8_StraightEdgeCleanupRail", [(1.48, -0.54, 0.14), (1.98, -0.54, 0.18)], mats["cyan"], 0.010, role="straight_edge_cleanup")
    parts.append(straight)
    parts.extend(arrow("LAB8_GrazingLightShadingCheck", (1.90, -0.70, 0.62), (1.52, -0.82, 0.45), mats["uv_c"], radius=0.009, role="weighted_normal_bevel_check"))
    return parts


def create_origin_pivot_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB8_OriginPivotExportBoard", (2.00, 0.08, 0.76), (-0.10, 0.50, 0.42), mats["panel"], 0.025, role="origin_pivot_board")
    parts.append(panel)
    for i, x in enumerate((-0.86, -0.54, -0.22)):
        prop = rounded_box(f"LAB8_OriginControlledProp_{i}", (0.20, 0.12, 0.24), (x, 0.44, 0.42), mats["uv_a" if i == 0 else "uv_b"], 0.018, role="origin_export_control")
        origin = sphere(f"LAB8_OriginMarker_IntentionalPivot_{i}", 0.030, (x - 0.14, 0.44, 0.26), mats["origin"], segments=10, ring_count=5, role="origin_export_control")
        parts.extend([prop, origin])
    for i, x in enumerate((0.12, 0.34, 0.56)):
        dial = torus(f"LAB8_PivotTransformQADial_{i}", 0.10, 0.008, (x, 0.44, 0.42), mats["cyan"], rot=(math.radians(90), 0, 0), role="pivot_transform_qa")
        marker = sphere(f"LAB8_PivotTransformQAMarker_{i}", 0.025, (x + 0.10, 0.44, 0.42), mats["origin"], segments=10, ring_count=5, role="pivot_transform_qa")
        parts.extend([dial, marker])
    face = rounded_box("LAB8_FaceAlignedSurface_NormalChecked", (0.44, 0.08, 0.32), (1.00, 0.44, 0.35), mats["ghost"], 0.012, rot=(0, math.radians(-16), 0), role="face_align_normal_check")
    prop = cylinder("LAB8_FaceAlignedProp_ScaleOriginChecked", 0.055, 0.22, (1.08, 0.39, 0.62), mats["uv_c"], vertices=18, rot=(math.radians(90), 0, math.radians(12)), role="face_align_normal_check")
    parts.extend([face, prop])
    parts.extend(arrow("LAB8_FaceNormalDirectionCheck", (1.04, 0.39, 0.52), (1.22, 0.30, 0.72), mats["warn"], radius=0.009, role="face_align_normal_check"))
    gltf = rounded_box("LAB8_GLTFImportReorganizedCollection", (0.26, 0.035, 0.18), (1.48, 0.44, 0.48), mats["uv_b"], 0.010, role="gltf_reorganization_check")
    parts.append(gltf)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB8_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")
    floor = rounded_box("LAB8_StudioFloor_NotExported", (4.9, 3.25, 0.065), (0.0, -0.08, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_uv_board(mats))
    export_parts.extend(create_bake_export_board(mats))
    export_parts.extend(create_normals_sculpt_board(mats))
    export_parts.extend(create_origin_pivot_board(mats))
    labels = [
        add_text("LAB8_Label_UV", "UV / TEXEL / MARGIN", (-1.42, -1.18, 0.84), 0.052, mats["white"]),
        add_text("LAB8_Label_Bake", "BAKE / TEXTURE EXPORT", (-0.12, -1.18, 0.84), 0.052, mats["white"]),
        add_text("LAB8_Label_Normals", "SCULPT CAGE + NORMALS", (1.20, -1.18, 0.84), 0.052, mats["white"]),
        add_text("LAB8_Label_Origins", "ORIGINS / PIVOTS / FACE ALIGN", (-0.10, 0.14, 0.90), 0.052, mats["white"]),
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
        if obj.name == "LAB8_NormalBakeMovingLightRing":
            obj.rotation_euler.z = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = math.tau
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
        if obj.name.startswith("LAB8_PivotTransformQADial_"):
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
    if triangles > 45000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 45000.")
    roles = sorted({str(obj.get("role")) for obj in objects if obj.get("role")})
    required_roles = {
        "uv_seam_diagnostic",
        "texel_density_gate",
        "uv_margin_pack_card",
        "uv_overlap_intent",
        "spherical_hidden_seam",
        "texture_export_accountability",
        "bake_source_target_name",
        "bake_cage_ray_check",
        "material_atlas_remap",
        "paint_isolation_id",
        "position_pass_coordinate",
        "sculpt_source_proxy",
        "export_cage_handoff",
        "normal_bake_light_review",
        "weighted_normal_bevel_check",
        "normal_fix_order",
        "straight_edge_cleanup",
        "origin_export_control",
        "pivot_transform_qa",
        "face_align_normal_check",
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
    if "LAB8_Root_TurntableAnimated" not in animated:
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
        "source_goal": "500-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "UV seam, texel-density, margin and overlap checks are visible.",
            "Bake/export source-target, texture card and atlas remap checks are visible.",
            "Sculpt source, export cage, normal bake and weighted-normal checks are visible.",
            "Origins, pivots, transform QA and face-align normal checks are visible.",
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
