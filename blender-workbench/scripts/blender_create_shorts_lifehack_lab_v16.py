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

ASSET = "blender_shorts_lifehack_lab_v16"
SCENE_NAME = "BlenderShortsLifehackLabV16"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-300", "name": "Topology Cleanup Needs Before/After Mesh Proof", "applied": "Before/after mesh panels show duplicate, non-manifold and face-orientation checks."},
    {"id": "BH-301", "name": "N-Gons And Booleans Need Risk Maps", "applied": "Boolean and n-gon risk chips flag bevel, subdivision and export triangulation risk."},
    {"id": "BH-302", "name": "Automated Retopo Is Draft Topology", "applied": "Auto-retopo lane is labeled draft until edge flow, density and silhouette pass."},
    {"id": "BH-303", "name": "Sculpt Remesh Needs Resolution Budgets", "applied": "Voxel, quad and multires resolution bars show feature-loss and performance budgets."},
    {"id": "BH-304", "name": "High-Low Baking Needs A Cage Contract", "applied": "High/low/cage bake stack has name, scale, ray distance and margin checks."},
    {"id": "BH-305", "name": "Normal Details Need Seam-Safe Placement", "applied": "Normal stamp board marks orientation, scale and seam clearance."},
    {"id": "BH-306", "name": "UV Seams Need Intent", "applied": "UV seam plan follows hidden edges, deformation breaks and checker distortion proof."},
    {"id": "BH-307", "name": "UV Transfer And Mirror Need Orientation QA", "applied": "UV mirror rail checks object names, overlap and tangent direction."},
    {"id": "BH-308", "name": "UV Packing Needs Texel And Margin Proof", "applied": "Packed UV islands include texel-density bars, padding and stretch indicators."},
    {"id": "BH-309", "name": "UV Add-Ons Need Fallbacks", "applied": "Addon path and manual fallback are both represented in the UV workflow."},
    {"id": "BH-310", "name": "Bevel And Weighted Normals Need A Shading Contract", "applied": "Bevel/weighted-normal contract exposes width, segments, clamp and flat-light proof."},
    {"id": "BH-311", "name": "Hard-Surface Topology Needs Edge Policy", "applied": "Support loops, crease/subdivision and weighted-normal choices are separated."},
    {"id": "BH-312", "name": "Blockouts Need Cleanup Gates", "applied": "Blockout-to-asset lane shows seams, caps, bevels, material slots and modifier order."},
    {"id": "BH-313", "name": "Bevel Tricks Still Need Topology Review", "applied": "Bevel trick chip routes through n-gon, profile, segment and shading review."},
    {"id": "BH-314", "name": "Normals Need Face-Orientation Proof", "applied": "Face orientation board shows blue outside/red inside and GLB viewer check."},
    {"id": "BH-315", "name": "Edge Flow Is Shape QA", "applied": "Edge-flow rails show straightening, loop continuity and volume-preservation review."},
    {"id": "BH-316", "name": "Extrude And Dissolve Need Manifold Checks", "applied": "Extrude/dissolve lane includes duplicate-face, hole, manifold, UV and normal checks."},
    {"id": "BH-317", "name": "Modifier Stacks Need Export Order", "applied": "Modifier stack tower declares bevel, solidify, subdivision, normals and export/apply policy."},
    {"id": "BH-318", "name": "Simplification Needs Preservation Metrics", "applied": "Animated simplification slider reports triangle savings plus silhouette/UV/normal preservation."},
    {"id": "BH-319", "name": "Mesh Handoff Needs A Full Asset Checklist", "applied": "Final handoff gate collects topology, UV, normals, bake, modifiers, materials and GLB checks."},
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
            "Specular IOR Level": 0.38,
            "Coat Weight": 0.03,
            "Coat Roughness": 0.26,
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
        "base": make_mat("Lab16_BaseInk", (0.016, 0.018, 0.026, 1.0), roughness=0.68),
        "panel": make_mat("Lab16_PanelBlueBlack", (0.036, 0.048, 0.076, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab16_PanelDeepGreen", (0.030, 0.068, 0.060, 1.0), roughness=0.62),
        "ink": make_mat("Lab16_InkDark", (0.010, 0.012, 0.018, 1.0), roughness=0.74),
        "white": make_mat("Lab16_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.54),
        "cyan": make_mat("Lab16_UVCyan", (0.03, 0.77, 0.96, 1.0), roughness=0.34, emission=(0.0, 0.28, 0.52, 1.0), emission_strength=0.10),
        "green": make_mat("Lab16_CheckGreen", (0.12, 0.78, 0.38, 1.0), roughness=0.48),
        "gold": make_mat("Lab16_BakeGold", (1.0, 0.70, 0.18, 1.0), roughness=0.42, metallic=0.04),
        "magenta": make_mat("Lab16_RetopoMagenta", (0.96, 0.14, 0.58, 1.0), roughness=0.38, emission=(0.32, 0.0, 0.16, 1.0), emission_strength=0.08),
        "orange": make_mat("Lab16_BevelOrange", (0.96, 0.42, 0.10, 1.0), roughness=0.44),
        "red": make_mat("Lab16_WarningRed", (0.95, 0.08, 0.06, 1.0), roughness=0.36, emission=(0.42, 0.02, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab16_ModifierViolet", (0.50, 0.25, 0.86, 1.0), roughness=0.46),
        "blue": make_mat("Lab16_NormalBlue", (0.10, 0.38, 0.92, 1.0), roughness=0.48),
        "ghost": make_mat("Lab16_CageGhost", (0.58, 0.78, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "uv_a": make_mat("Lab16_UVIslandA", (0.14, 0.58, 0.95, 1.0), roughness=0.48),
        "uv_b": make_mat("Lab16_UVIslandB", (0.05, 0.82, 0.55, 1.0), roughness=0.48),
        "uv_c": make_mat("Lab16_UVIslandC", (0.95, 0.26, 0.54, 1.0), roughness=0.48),
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
    scene.world = scene.world or bpy.data.worlds.new("LAB16_World")
    scene.world.color = (0.014, 0.016, 0.024)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.7, -5.2, 4.8))
    key = bpy.context.object
    key.name = "LAB16_KeyArea_Warm"
    key.data.energy = 740
    key.data.size = 5.2
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.2, 2.9, 3.4))
    fill = bpy.context.object
    fill.name = "LAB16_FillArea_Cool"
    fill.data.energy = 150
    fill.data.size = 5.8
    fill.data.color = (0.58, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.0, 3.7, 2.9))
    rim = bpy.context.object
    rim.name = "LAB16_RimPoint_Cyan"
    rim.data.energy = 305
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.3, -5.7, 3.35), rotation=(math.radians(58), 0, math.radians(39)))
    cam = bpy.context.object
    cam.name = "LAB16_Camera_Hero3Q"
    cam.data.lens = 38
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 7.5
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def make_root() -> bpy.types.Object:
    root = bpy.data.objects.new("LAB16_Root_TurntableAnimated", None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.65
    tag(root, "mesh_handoff_full_checklist", export=True, bh="BH-319")
    for frame, angle in ((1, -3), (48, 12), (96, 357)):
        bpy.context.scene.frame_set(frame)
        root.rotation_euler = (0, 0, math.radians(angle))
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    return root


def add_panel(mats: dict[str, bpy.types.Material], name: str, title: str, loc: tuple[float, float, float], size: tuple[float, float, float], mat_key: str) -> bpy.types.Object:
    panel = rounded_box(name, size, loc, mats[mat_key], 0.035, role="lab_panel", export=True)
    add_text(f"{name}_Title", title, (loc[0], loc[1] - 0.065, loc[2] + size[2] * 0.42), 0.060, mats["white"])
    return panel


def build_topology_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB16_TopologyPanel_Backplate", "TOPOLOGY CLEANUP", (-1.95, 0.06, 1.02), (1.38, 0.08, 1.08), "panel")
    before_points = [(-2.48, -0.05, 1.15), (-2.31, -0.05, 1.36), (-2.13, -0.05, 1.12), (-1.98, -0.05, 1.30), (-1.79, -0.05, 1.08)]
    for index in range(len(before_points) - 1):
        parts.append(cyl_between(f"LAB16_BeforeMesh_BrokenEdge_{index}", before_points[index], before_points[index + 1], 0.010, mats["red"], vertices=8, role="topology_before_after_mesh_proof", bh="BH-300"))
    for loc in before_points:
        parts.append(sphere(f"LAB16_BeforeMesh_DuplicateDot_{len(parts)}", loc, 0.030, mats["red"], segments=12, role="topology_before_after_mesh_proof", bh="BH-300"))
    for col in range(4):
        x = -2.44 + col * 0.18
        parts.append(cyl_between(f"LAB16_AfterMesh_QuadVertical_{col}", (x, -0.070, 0.74), (x, -0.070, 1.00), 0.005, mats["green"], vertices=8, role="topology_before_after_mesh_proof", bh="BH-300"))
    for row in range(4):
        z = 0.74 + row * 0.085
        parts.append(cyl_between(f"LAB16_AfterMesh_QuadHorizontal_{row}", (-2.44, -0.070, z), (-1.90, -0.070, z), 0.005, mats["green"], vertices=8, role="topology_before_after_mesh_proof", bh="BH-300"))
    parts.append(rounded_box("LAB16_NGonRisk_BooleanPatch", (0.34, 0.030, 0.20), (-1.58, -0.070, 1.21), mats["orange"], 0.018, role="ngon_boolean_risk_map", bh="BH-301"))
    parts.append(torus("LAB16_BooleanCut_RiskRing", (-1.58, -0.090, 1.21), 0.145, 0.006, mats["red"], role="ngon_boolean_risk_map", bh="BH-301"))
    for index, color in enumerate(["magenta", "cyan", "green"]):
        parts.append(rounded_box(f"LAB16_AutoRetopo_DraftLane_{index}", (0.18, 0.028, 0.070), (-1.66 + index * 0.23, -0.075, 0.80), mats[color], 0.010, role="automated_retopo_draft_qa", bh="BH-302"))
    parts.extend(arrow("LAB16_Retopo_DraftToQAArrow", (-1.70, -0.085, 0.90), (-1.28, -0.085, 0.90), mats["magenta"], radius=0.006, role="automated_retopo_draft_qa", bh="BH-302"))
    for index, (name, height, color) in enumerate([("voxel", 0.18, "violet"), ("quad", 0.26, "blue"), ("multires", 0.34, "gold")]):
        parts.append(rounded_box(f"LAB16_SculptRemesh_ResolutionBudget_{name}", (0.055, 0.030, height), (-2.48 + index * 0.17, -0.075, 0.38 + height / 2), mats[color], 0.008, role="sculpt_remesh_resolution_budget", bh="BH-303"))
    add_text("LAB16_TopoChip_BeforeAfter", "before -> clean quads", (-2.18, -0.095, 1.50), 0.037, mats["green"])
    add_text("LAB16_TopoChip_Draft", "retopo draft, not final", (-1.48, -0.095, 0.64), 0.034, mats["magenta"])
    return parts


def build_uv_bake_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB16_UVPanel_Backplate", "UV / BAKE CONTRACT", (0.00, 0.07, 1.03), (1.50, 0.08, 1.08), "panel_alt")
    uv_frame = rounded_box("LAB16_UVFrame_CheckerDistortionProof", (0.62, 0.030, 0.47), (-0.32, -0.07, 1.18), mats["ink"], 0.024, role="uv_seam_intent", bh="BH-306")
    parts.append(uv_frame)
    for i in range(5):
        x = -0.58 + i * 0.13
        parts.append(cyl_between(f"LAB16_UVChecker_V_{i}", (x, -0.090, 0.97), (x, -0.090, 1.38), 0.0035, mats["white"], vertices=8, role="uv_seam_intent", bh="BH-306"))
        z = 0.97 + i * 0.10
        parts.append(cyl_between(f"LAB16_UVChecker_H_{i}", (-0.58, -0.090, z), (-0.05, -0.090, z), 0.0035, mats["white"], vertices=8, role="uv_seam_intent", bh="BH-306"))
    parts.append(cyl_between("LAB16_UVSeamIntent_HiddenEdge", (-0.56, -0.105, 1.02), (-0.12, -0.105, 1.34), 0.007, mats["red"], role="uv_seam_intent", bh="BH-306"))
    parts.append(rounded_box("LAB16_UVIsland_A_TexelDensity", (0.20, 0.026, 0.16), (0.24, -0.075, 1.30), mats["uv_a"], 0.018, role="uv_texel_margin_proof", bh="BH-308"))
    parts.append(rounded_box("LAB16_UVIsland_B_TexelDensity", (0.15, 0.026, 0.22), (0.48, -0.075, 1.08), mats["uv_b"], 0.018, role="uv_texel_margin_proof", bh="BH-308"))
    parts.append(rounded_box("LAB16_UVIsland_C_TexelDensity", (0.19, 0.026, 0.11), (0.19, -0.075, 0.92), mats["uv_c"], 0.018, role="uv_texel_margin_proof", bh="BH-308"))
    parts.append(cyl_between("LAB16_UVPadding_MarginProof_A", (0.10, -0.095, 0.78), (0.62, -0.095, 0.78), 0.006, mats["gold"], role="uv_texel_margin_proof", bh="BH-308"))
    parts.append(cyl_between("LAB16_UVMirror_OrientationRail", (0.06, -0.090, 1.45), (0.64, -0.090, 1.45), 0.006, mats["cyan"], role="uv_transfer_mirror_orientation", bh="BH-307"))
    parts.append(sphere("LAB16_UVMirror_LeftNameDot", (0.10, -0.105, 1.45), 0.030, mats["cyan"], segments=12, role="uv_transfer_mirror_orientation", bh="BH-307"))
    parts.append(sphere("LAB16_UVMirror_RightNameDot", (0.60, -0.105, 1.45), 0.030, mats["magenta"], segments=12, role="uv_transfer_mirror_orientation", bh="BH-307"))
    parts.append(rounded_box("LAB16_UVAddon_Path_MIO3", (0.22, 0.030, 0.075), (-0.58, -0.078, 0.78), mats["violet"], 0.012, role="uv_addon_fallback", bh="BH-309"))
    parts.append(rounded_box("LAB16_UVAddon_ManualFallback", (0.22, 0.030, 0.075), (-0.31, -0.078, 0.78), mats["green"], 0.012, role="uv_addon_fallback", bh="BH-309"))
    high = sphere("LAB16_Bake_HighPolySource_Named", (-0.18, -0.070, 0.46), 0.105, mats["gold"], role="bake_cage_contract", bh="BH-304")
    low = rounded_box("LAB16_Bake_LowPolyTarget_Named", (0.18, 0.030, 0.18), (0.10, -0.070, 0.46), mats["blue"], 0.018, role="bake_cage_contract", bh="BH-304")
    cage = rounded_box("LAB16_Bake_CageDistance_Ghost", (0.26, 0.026, 0.26), (0.10, -0.102, 0.46), mats["ghost"], 0.018, role="bake_cage_contract", bh="BH-304")
    parts.extend([high, low, cage])
    stamp = torus("LAB16_NormalStamp_SeamSafePlacement", (0.45, -0.070, 0.46), 0.080, 0.006, mats["magenta"], role="normal_detail_seam_safe", bh="BH-305")
    parts.append(stamp)
    for frame, scale in ((1, 0.90), (48, 1.18), (96, 0.90)):
        bpy.context.scene.frame_set(frame)
        cage.scale = (scale, scale, scale)
        cage.keyframe_insert(data_path="scale", frame=frame)
    add_text("LAB16_UVChip_Seams", "seams + checker", (-0.31, -0.095, 1.55), 0.035, mats["cyan"])
    add_text("LAB16_UVChip_Bake", "high / low / cage", (0.13, -0.095, 0.26), 0.035, mats["gold"])
    return parts


def build_normals_bevel_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB16_NormalsPanel_Backplate", "BEVEL / NORMALS / EDGES", (1.95, 0.06, 1.02), (1.42, 0.08, 1.08), "panel")
    hs = rounded_box("LAB16_HardSurface_Block_WithSupportLoops", (0.48, 0.060, 0.34), (1.70, -0.070, 1.17), mats["blue"], 0.030, role="hard_surface_edge_policy", bh="BH-311")
    parts.append(hs)
    for offset in (-0.17, 0.17):
        parts.append(cyl_between(f"LAB16_HardSurface_SupportLoop_{offset}", (1.70 + offset, -0.112, 0.98), (1.70 + offset, -0.112, 1.34), 0.005, mats["gold"], vertices=8, role="hard_surface_edge_policy", bh="BH-311"))
    for index, (label, color) in enumerate([("width", "orange"), ("segments", "green"), ("clamp", "cyan"), ("flat", "white")]):
        parts.append(rounded_box(f"LAB16_BevelWeightedNormal_Contract_{label}", (0.19, 0.030, 0.065), (2.25, -0.075, 1.39 - index * 0.11), mats[color], 0.010, role="bevel_weighted_normal_contract", bh="BH-310"))
    parts.append(torus("LAB16_BevelTrick_TopologyReviewRing", (2.18, -0.085, 0.88), 0.150, 0.006, mats["orange"], role="bevel_trick_topology_review", bh="BH-313"))
    parts.append(rounded_box("LAB16_FaceOrientation_BlueOutside", (0.24, 0.030, 0.16), (1.50, -0.078, 0.80), mats["blue"], 0.012, role="normals_face_orientation_proof", bh="BH-314"))
    parts.append(rounded_box("LAB16_FaceOrientation_RedInside", (0.24, 0.030, 0.16), (1.76, -0.082, 0.80), mats["red"], 0.012, role="normals_face_orientation_proof", bh="BH-314"))
    for row, z in enumerate([0.42, 0.52, 0.62]):
        parts.append(cyl_between(f"LAB16_EdgeFlow_StraightenedRail_{row}", (1.42, -0.090, z), (2.05, -0.090, z + 0.04), 0.006, mats["green"], vertices=8, role="edge_flow_shape_qa", bh="BH-315"))
    parts.append(cyl_between("LAB16_ExtrudeDissolve_ManifoldPath", (2.20, -0.080, 0.38), (2.48, -0.080, 0.66), 0.010, mats["magenta"], role="extrude_dissolve_manifold_checks", bh="BH-316"))
    parts.append(sphere("LAB16_ExtrudeDissolve_DuplicateFaceDot", (2.20, -0.095, 0.38), 0.032, mats["red"], segments=12, role="extrude_dissolve_manifold_checks", bh="BH-316"))
    add_text("LAB16_NormalChip_Bevel", "bevel + weighted normal", (1.93, -0.095, 1.55), 0.036, mats["orange"])
    add_text("LAB16_NormalChip_Orientation", "blue outside / red inside", (1.66, -0.095, 0.67), 0.032, mats["blue"])
    return parts


def build_handoff_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB16_HandoffPanel_Backplate", "MODIFIERS / SIMPLIFY / HANDOFF", (0.00, 0.08, 0.16), (3.92, 0.08, 0.62), "panel_alt")
    for index, (label, color) in enumerate([("blockout", "blue"), ("seams", "cyan"), ("caps", "gold"), ("slots", "green")]):
        parts.append(rounded_box(f"LAB16_BlockoutCleanupGate_{label}", (0.24, 0.030, 0.075), (-1.66 + index * 0.30, -0.075, 0.44), mats[color], 0.012, role="blockout_cleanup_gate", bh="BH-312"))
    stack_items = [("solidify", "blue"), ("bevel", "orange"), ("subdiv", "violet"), ("normals", "green"), ("export", "gold")]
    for index, (label, color) in enumerate(stack_items):
        parts.append(rounded_box(f"LAB16_ModifierStack_ExportOrder_{label}", (0.25, 0.032, 0.055), (-0.26, -0.075, 0.18 + index * 0.085), mats[color], 0.010, role="modifier_stack_export_order", bh="BH-317"))
    slider = sphere("LAB16_Simplification_PreservationMetricSlider", (0.55, -0.080, 0.22), 0.044, mats["magenta"], segments=16, role="simplification_preservation_metrics", bh="BH-318")
    parts.append(slider)
    parts.append(cyl_between("LAB16_Simplification_TriangleSavingsRail", (0.38, -0.090, 0.22), (1.10, -0.090, 0.22), 0.007, mats["white"], vertices=8, role="simplification_preservation_metrics", bh="BH-318"))
    parts.append(cyl_between("LAB16_Simplification_SilhouettePreserved", (0.38, -0.090, 0.36), (1.10, -0.090, 0.36), 0.006, mats["green"], vertices=8, role="simplification_preservation_metrics", bh="BH-318"))
    parts.append(cyl_between("LAB16_Simplification_NormalPreserved", (0.38, -0.090, 0.50), (1.10, -0.090, 0.50), 0.006, mats["cyan"], vertices=8, role="simplification_preservation_metrics", bh="BH-318"))
    for frame, x in ((1, 0.48), (48, 0.92), (96, 0.48)):
        bpy.context.scene.frame_set(frame)
        slider.location = (x, -0.080, 0.22)
        slider.keyframe_insert(data_path="location", frame=frame)
    handoff_labels = ["topo", "uv", "norm", "bake", "mods", "mats", "glb"]
    for index, label in enumerate(handoff_labels):
        color = ["green", "cyan", "blue", "gold", "violet", "orange", "white"][index]
        parts.append(rounded_box(f"LAB16_HandoffChecklist_{label}", (0.16, 0.030, 0.075), (1.38 + index * 0.18, -0.076, 0.40), mats[color], 0.010, role="mesh_handoff_full_checklist", bh="BH-319"))
    parts.extend(arrow("LAB16_Handoff_ToGLBArrow", (1.38, -0.085, 0.22), (2.62, -0.085, 0.22), mats["green"], radius=0.006, role="mesh_handoff_full_checklist", bh="BH-319"))
    add_text("LAB16_HandoffChip_Blockout", "cleanup gates", (-1.21, -0.095, 0.58), 0.035, mats["white"])
    add_text("LAB16_HandoffChip_Export", "topo uv normals bake mods mats glb", (1.98, -0.095, 0.58), 0.034, mats["green"])
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    setup_lights()
    setup_camera()
    root = make_root()
    objects: list[bpy.types.Object] = []
    objects.append(rounded_box("LAB16_BaseTopologyUVBakeStage", (4.85, 0.13, 1.88), (0.0, 0.13, 0.75), mats["base"], 0.055, role="stage_base", export=True))
    add_text("LAB16_Title", "Blender Shorts Topology / UV / Bake Lab v16", (0.0, -0.11, 1.80), 0.087, mats["white"])
    add_text("LAB16_Subtitle", "cleanup  retopo  UV seams  bake cage  bevel normals  mesh handoff", (0.0, -0.11, 1.66), 0.046, mats["cyan"])
    objects.extend(build_topology_zone(mats))
    objects.extend(build_uv_bake_zone(mats))
    objects.extend(build_normals_bevel_zone(mats))
    objects.extend(build_handoff_zone(mats))
    for index, info in enumerate(APPLIED_LIFEHACKS):
        row = index // 10
        col = index % 10
        chip = rounded_box(
            f"LAB16_AppliedTick_{info['id']}",
            (0.18, 0.025, 0.045),
            (-2.16 + col * 0.47, -0.075, -0.08 + row * 0.11),
            mats["green"] if row == 0 else mats["cyan"],
            0.006,
            role="applied_lifehack_tick",
            bh=info["id"],
            export=True,
        )
        objects.append(chip)
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
        "topology_before_after_mesh_proof",
        "ngon_boolean_risk_map",
        "automated_retopo_draft_qa",
        "sculpt_remesh_resolution_budget",
        "bake_cage_contract",
        "normal_detail_seam_safe",
        "uv_seam_intent",
        "uv_transfer_mirror_orientation",
        "uv_texel_margin_proof",
        "uv_addon_fallback",
        "bevel_weighted_normal_contract",
        "hard_surface_edge_policy",
        "blockout_cleanup_gate",
        "bevel_trick_topology_review",
        "normals_face_orientation_proof",
        "edge_flow_shape_qa",
        "extrude_dissolve_manifold_checks",
        "modifier_stack_export_order",
        "simplification_preservation_metrics",
        "mesh_handoff_full_checklist",
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
        "LAB16_Root_TurntableAnimated",
        "LAB16_Bake_CageDistance_Ghost",
        "LAB16_Simplification_PreservationMetricSlider",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        errors.append(f"Expected animated topology QA markers missing: {missing_anim}")
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
        "source_goal": "900-source Blender Shorts checkpoint test asset.",
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
            "Before/after topology cleanup, n-gon/boolean risks and retopo draft QA are visible.",
            "Sculpt remesh budgets, high/low/cage bake contract and seam-safe normal detail are visible.",
            "UV seam intent, transfer/mirror orientation, texel density, margins and addon fallback are visible.",
            "Bevel/weighted normals, hard-surface edge policy, face orientation and edge-flow QA are visible.",
            "Modifier order, simplification preservation metrics and mesh handoff checklist are visible.",
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
