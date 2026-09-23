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

ASSET = "blender_shorts_lifehack_lab_v9"
SCENE_NAME = "BlenderShortsLifehackLabV9"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-169", "name": "Geometry Nodes Need An Apply Boundary", "applied": "Apply/realize/mesh handoff board marks live procedural and export states."},
    {"id": "BH-170", "name": "Scatter Systems Need Exposed Density And Seed", "applied": "Scatter field exposes density, seed, scale and mask controls."},
    {"id": "BH-171", "name": "Curve Procedurals Need Orientation QA", "applied": "Curve array board includes tangent arrows, spacing and end-cap checks."},
    {"id": "BH-172", "name": "Set Position Needs Bounds", "applied": "Displacement strip is clamped by a visible amplitude cage."},
    {"id": "BH-173", "name": "Procedural Foliage Needs LOD Gates", "applied": "Foliage clusters show viewport/render density and LOD budget gates."},
    {"id": "BH-174", "name": "Instance Variation Needs Index Logic", "applied": "Index-switch strip cycles between distinct instance variants."},
    {"id": "BH-175", "name": "Surface Effects Need Contact Rules", "applied": "Raycast/droplet board shows hit distance, normals, falloff and miss state."},
    {"id": "BH-176", "name": "Node Materials Need Attribute Contracts", "applied": "Attribute swatches show named material channels and value ranges."},
    {"id": "BH-177", "name": "Simulation Zones Need Reset And Loop QA", "applied": "Loop board has reset state, first/last markers and animated trail points."},
    {"id": "BH-178", "name": "Repeat Networks Need Stop Conditions", "applied": "Repeat-zone meter shows bounded iterations and performance gate."},
    {"id": "BH-179", "name": "Procedural Grids Need Bounds", "applied": "Grid/countdown board uses an explicit boundary frame and camera-scale marker."},
    {"id": "BH-180", "name": "Procedural Damage Needs A Clean Exit", "applied": "Damage board preserves source crack curve, chunks and UV handoff strip."},
    {"id": "BH-181", "name": "Intersections Can Become Guide Geometry", "applied": "Intersection curves are generated as named guide trims."},
    {"id": "BH-182", "name": "Procedural Stroke Animation Needs Timing QA", "applied": "Stroke strip shows seed, timing ticks and animated reveal marker."},
    {"id": "BH-183", "name": "Geometry Nodes Need Frame Hygiene", "applied": "Node-map panel groups inputs, masks, realization, material attributes and export."},
    {"id": "BH-184", "name": "Procedural Bevels Need Shading QA", "applied": "Wireframe/bevel panel includes thickness and grazing-light checks."},
    {"id": "BH-185", "name": "Procedural Shape Controls Beat Destructive Fixes", "applied": "Shape control panel exposes radius, spacing, normal alignment and rivet placement."},
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
            "Specular IOR Level": 0.44,
            "Coat Weight": 0.04,
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
        "base": make_mat("Lab9_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.60),
        "panel": make_mat("Lab9_PanelInk", (0.060, 0.075, 0.110, 1.0), roughness=0.62),
        "panel_alt": make_mat("Lab9_PanelBlueBlack", (0.035, 0.075, 0.115, 1.0), roughness=0.62),
        "cyan": make_mat("Lab9_ControlCyan", (0.02, 0.80, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.32, 0.78, 1.0), emission_strength=0.14),
        "green": make_mat("Lab9_SeedGreen", (0.10, 0.86, 0.42, 1.0), roughness=0.44),
        "gold": make_mat("Lab9_BoundsGold", (1.0, 0.72, 0.16, 1.0), roughness=0.42, metallic=0.06),
        "magenta": make_mat("Lab9_WarningMagenta", (1.0, 0.10, 0.55, 1.0), roughness=0.36, emission=(0.45, 0.0, 0.22, 1.0), emission_strength=0.13),
        "blue": make_mat("Lab9_NodeBlue", (0.10, 0.42, 0.95, 1.0), roughness=0.48),
        "white": make_mat("Lab9_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
        "ghost": make_mat("Lab9_DebugGhost", (0.48, 0.70, 1.0, 1.0), roughness=0.54, alpha=0.30),
        "clay": make_mat("Lab9_ProceduralClay", (0.74, 0.50, 0.37, 1.0), roughness=0.70),
        "metal": make_mat("Lab9_BevelMetal", (0.62, 0.70, 0.78, 1.0), roughness=0.31, metallic=0.34),
        "red": make_mat("Lab9_ResetRed", (1.0, 0.12, 0.08, 1.0), roughness=0.35, emission=(0.54, 0.02, 0.02, 1.0), emission_strength=0.10),
        "dark": make_mat("Lab9_NodeSocketDark", (0.015, 0.018, 0.025, 1.0), roughness=0.68),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB9_WeightedNormals", type="WEIGHTED_NORMAL")


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
        mod = obj.modifiers.new(name="LAB9_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB9_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export, bh)


def sphere(
    name: str,
    radius: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    segments: int = 16,
    ring_count: int = 8,
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
    vertices: int = 18,
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
    vertices: int = 16,
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
    scene.world = scene.world or bpy.data.worlds.new("LAB9_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.2, -4.8, 4.8))
    key = bpy.context.object
    key.name = "LAB9_KeyArea_Warm"
    key.data.energy = 620
    key.data.size = 5.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.9, 2.8, 3.2))
    fill = bpy.context.object
    fill.name = "LAB9_FillArea_Cool"
    fill.data.energy = 125
    fill.data.size = 5.3
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.7, 3.0, 2.5))
    rim = bpy.context.object
    rim.name = "LAB9_RimPoint_Cyan"
    rim.data.energy = 235
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.8, -5.7, 3.55), rotation=(math.radians(58), 0, math.radians(41)))
    cam = bpy.context.object
    cam.name = "LAB9_Camera_Hero3Q"
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


def create_apply_scatter_curve_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB9_ApplyScatterCurveBoard", (1.70, 0.08, 1.02), (-1.30, -0.82, 0.55), mats["panel"], 0.025, role="node_lab_panel")
    parts.append(panel)
    chips = [
        ("Live", -1.88, 0.86, mats["blue"]),
        ("Realize", -1.56, 0.86, mats["cyan"]),
        ("Mesh", -1.24, 0.86, mats["green"]),
    ]
    for label, x, z, mat in chips:
        chip = rounded_box(f"LAB9_ApplyBoundary_{label}", (0.22, 0.045, 0.13), (x, -0.88, z), mat, 0.010, role="apply_boundary", bh="BH-169")
        chip["handoff_state"] = label
        parts.append(chip)
    parts.extend(arrow("LAB9_ApplyRealizeMeshFlow", (-1.76, -0.88, 0.76), (-1.06, -0.88, 0.76), mats["cyan"], radius=0.006, role="apply_boundary", bh="BH-169"))

    mask = rounded_box("LAB9_ScatterMaskDensitySeedPlane", (0.66, 0.035, 0.27), (-1.62, -0.90, 0.47), mats["ghost"], 0.008, role="scatter_density_seed", bh="BH-170")
    mask["density"] = 0.68
    mask["seed"] = 42
    mask["scale_range"] = "0.65..1.35"
    parts.append(mask)
    for i in range(24):
        x = -1.90 + (i % 8) * 0.075 + math.sin(i * 1.7) * 0.010
        z = 0.36 + (i // 8) * 0.075 + math.cos(i * 1.3) * 0.012
        radius = 0.016 + (i % 4) * 0.004
        mat = [mats["green"], mats["cyan"], mats["gold"], mats["magenta"]][i % 4]
        dot = sphere(f"LAB9_ScatterInstance_densitySeed_{i:02d}", radius, (x, -0.94, z), mat, segments=10, ring_count=5, role="scatter_density_seed", bh="BH-170")
        parts.append(dot)
    for i, height in enumerate((0.12, 0.20, 0.16)):
        slider = rounded_box(f"LAB9_ScatterControlSlider_{i}", (0.040, 0.035, height), (-1.08 + i * 0.08, -0.91, 0.34 + height / 2), mats["gold"], 0.006, role="scatter_density_seed", bh="BH-170")
        parts.append(slider)

    curve_pts = [(-1.86, -0.91, 0.17), (-1.66, -0.91, 0.25), (-1.42, -0.91, 0.16), (-1.16, -0.91, 0.27), (-0.92, -0.91, 0.18)]
    parts.append(curve_line("LAB9_CurveArrayOrientationGuide", curve_pts, mats["cyan"], 0.007, role="curve_orientation_qa", bh="BH-171"))
    for i, (x, _, z) in enumerate(curve_pts):
        inst = cylinder(f"LAB9_CurveArrayTangentInstance_{i}", 0.030, 0.14, (x, -0.91, z + 0.03), mats["blue" if i % 2 else "green"], vertices=14, rot=(math.radians(90), 0, math.radians(i * 18)), role="curve_orientation_qa", bh="BH-171")
        parts.append(inst)
    parts.extend(arrow("LAB9_CurveTangentEndCapCheck", (-1.00, -0.91, 0.15), (-0.84, -0.91, 0.25), mats["gold"], radius=0.006, role="curve_orientation_qa", bh="BH-171"))
    return parts


def create_displace_foliage_instance_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB9_DisplaceFoliageInstanceBoard", (1.66, 0.08, 1.02), (0.30, -0.82, 0.55), mats["panel_alt"], 0.025, role="node_lab_panel")
    parts.append(panel)
    base_line = [(-0.34 + i * 0.075, -0.88, 0.86 + math.sin(i * 0.9) * 0.045) for i in range(14)]
    parts.append(curve_line("LAB9_SetPositionBoundedDisplacementWave", base_line, mats["cyan"], 0.009, role="set_position_bounds", bh="BH-172"))
    cage = rounded_box("LAB9_SetPositionAmplitudeCage", (1.03, 0.028, 0.20), (0.15, -0.88, 0.86), mats["ghost"], 0.004, role="set_position_bounds", bh="BH-172")
    cage["amplitude_limit"] = 0.05
    parts.append(cage)
    for i, x in enumerate((-0.28, 0.15, 0.58)):
        parts.extend(arrow(f"LAB9_SetPositionClampArrow_{i}", (x, -0.91, 0.74), (x, -0.91, 0.82), mats["gold"], radius=0.005, role="set_position_bounds", bh="BH-172"))

    for i, (x, count, mat) in enumerate(((-0.28, 5, mats["green"]), (0.12, 8, mats["cyan"]), (0.52, 11, mats["gold"]))):
        gate = rounded_box(f"LAB9_FoliageLODGate_{i}", (0.26, 0.035, 0.08 + i * 0.05), (x, -0.90, 0.45), mat, 0.007, role="foliage_lod_gate", bh="BH-173")
        gate["viewport_density"] = 0.25 + i * 0.25
        gate["render_density"] = 0.50 + i * 0.35
        parts.append(gate)
        for j in range(count):
            dx = (j % 4) * 0.045 - 0.070
            dz = (j // 4) * 0.040
            blade = cone_between(f"LAB9_FoliageBlade_LOD{i}_{j}", (x + dx, -0.92, 0.49 + dz), (x + dx + math.sin(j) * 0.020, -0.92, 0.58 + dz + j * 0.002), 0.007, 0.0, mat, vertices=8, role="foliage_lod_gate", bh="BH-173")
            parts.append(blade)

    variants = [
        ("Cube", -0.22, mats["blue"]),
        ("Sphere", 0.02, mats["green"]),
        ("Cone", 0.26, mats["gold"]),
        ("Ring", 0.50, mats["magenta"]),
    ]
    for i, (label, x, mat) in enumerate(variants):
        chip = rounded_box(f"LAB9_InstanceIndexChip_{i}_{label}", (0.10, 0.035, 0.07), (x, -0.90, 0.21), mat, 0.006, role="instance_index_logic", bh="BH-174")
        chip["index"] = i
        parts.append(chip)
        if label == "Sphere":
            parts.append(sphere(f"LAB9_InstanceVariant_{label}", 0.040, (x, -0.90, 0.31), mat, segments=12, ring_count=6, role="instance_index_logic", bh="BH-174"))
        elif label == "Cone":
            parts.append(cone_between(f"LAB9_InstanceVariant_{label}", (x, -0.90, 0.27), (x, -0.90, 0.36), 0.045, 0.0, mat, vertices=12, role="instance_index_logic", bh="BH-174"))
        elif label == "Ring":
            parts.append(torus(f"LAB9_InstanceVariant_{label}", 0.042, 0.006, (x, -0.90, 0.32), mat, rot=(math.radians(90), 0, 0), role="instance_index_logic", bh="BH-174"))
        else:
            parts.append(rounded_box(f"LAB9_InstanceVariant_{label}", (0.075, 0.045, 0.075), (x, -0.90, 0.31), mat, 0.010, role="instance_index_logic", bh="BH-174"))
    return parts


def create_surface_attribute_sim_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB9_SurfaceAttributeSimulationBoard", (1.72, 0.08, 1.02), (1.88, -0.82, 0.55), mats["panel"], 0.025, role="node_lab_panel")
    parts.append(panel)
    surface = rounded_box("LAB9_SurfaceContactRaycastTarget", (0.58, 0.050, 0.26), (1.42, -0.90, 0.83), mats["ghost"], 0.012, rot=(0, math.radians(-12), 0), role="surface_contact_rule", bh="BH-175")
    surface["hit_distance_limit"] = 0.18
    parts.append(surface)
    for i in range(7):
        x = 1.18 + i * 0.075
        z = 0.84 + math.sin(i) * 0.030
        droplet = sphere(f"LAB9_SurfaceDropletContact_{i}", 0.025 + (i % 3) * 0.004, (x, -0.935, z + 0.09), mats["cyan"], segments=12, ring_count=6, role="surface_contact_rule", bh="BH-175")
        parts.append(droplet)
    parts.extend(arrow("LAB9_RaycastHitDistanceNormal", (1.72, -0.92, 1.02), (1.56, -0.91, 0.89), mats["gold"], radius=0.006, role="surface_contact_rule", bh="BH-175"))
    miss = rounded_box("LAB9_RaycastMissFallbackColor", (0.12, 0.035, 0.08), (1.98, -0.90, 0.78), mats["red"], 0.006, role="surface_contact_rule", bh="BH-175")
    parts.append(miss)

    attr_names = ("mask", "height", "variant", "heat")
    for i, attr in enumerate(attr_names):
        swatch = rounded_box(f"LAB9_AttributeContract_{attr}", (0.15, 0.035, 0.10), (1.18 + i * 0.20, -0.90, 0.52), [mats["blue"], mats["green"], mats["magenta"], mats["gold"]][i], 0.007, role="attribute_contract", bh="BH-176")
        swatch["attribute_name"] = attr
        swatch["value_range"] = "0..1" if attr != "variant" else "0..3"
        parts.append(swatch)
        socket = sphere(f"LAB9_AttributeSocket_{attr}", 0.018, (1.18 + i * 0.20, -0.93, 0.62), mats["dark"], segments=8, ring_count=4, role="attribute_contract", bh="BH-176")
        parts.append(socket)

    ring = torus("LAB9_SimulationLoopContinuityRing", 0.20, 0.006, (1.50, -0.90, 0.24), mats["cyan"], rot=(math.radians(90), 0, 0), role="simulation_reset_loop", bh="BH-177")
    parts.append(ring)
    reset = rounded_box("LAB9_SimulationResetStateButton", (0.13, 0.035, 0.08), (1.18, -0.90, 0.24), mats["red"], 0.008, role="simulation_reset_loop", bh="BH-177")
    reset["reset_frame"] = 1
    parts.append(reset)
    for i, angle in enumerate((0, math.tau * 0.25, math.tau * 0.50, math.tau * 0.75)):
        dot = sphere(f"LAB9_SimulationTrailPoint_{i}", 0.030, (1.50 + math.cos(angle) * 0.20, -0.90, 0.24 + math.sin(angle) * 0.20), [mats["green"], mats["gold"], mats["magenta"], mats["cyan"]][i], segments=10, ring_count=5, role="simulation_reset_loop", bh="BH-177")
        dot["loop_checkpoint"] = i
        parts.append(dot)
    return parts


def create_back_procedural_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB9_BackProceduralSystemsBoard", (3.70, 0.08, 0.96), (0.30, 0.52, 0.58), mats["panel_alt"], 0.025, role="node_lab_panel")
    parts.append(panel)
    for i, height in enumerate((0.13, 0.22, 0.31, 0.40)):
        step = rounded_box(f"LAB9_RepeatStopConditionStep_{i}", (0.12, 0.035, height), (-1.34 + i * 0.15, 0.46, 0.24 + height / 2), mats["gold" if i < 3 else "magenta"], 0.007, role="repeat_stop_condition", bh="BH-178")
        step["iteration"] = i + 1
        step["max_iterations"] = 4
        parts.append(step)
    limit_line = curve_line("LAB9_RepeatDepthLimitGate", [(-1.42, 0.45, 0.74), (-0.78, 0.45, 0.74)], mats["magenta"], 0.006, role="repeat_stop_condition", bh="BH-178")
    parts.append(limit_line)

    grid_frame = rounded_box("LAB9_ProceduralGridBoundsFrame", (0.64, 0.030, 0.44), (-0.40, 0.45, 0.46), mats["ghost"], 0.006, role="procedural_grid_bounds", bh="BH-179")
    parts.append(grid_frame)
    for ix in range(4):
        for iz in range(3):
            cube = rounded_box(f"LAB9_BoundedIsoGridCell_{ix}_{iz}", (0.055, 0.040, 0.055), (-0.62 + ix * 0.13 + iz * 0.035, 0.43, 0.34 + iz * 0.08), mats["blue" if (ix + iz) % 2 else "green"], 0.006, rot=(0, 0, math.radians(45)), role="procedural_grid_bounds", bh="BH-179")
            parts.append(cube)

    damage_block = rounded_box("LAB9_DamageCleanExitSourceBlock", (0.42, 0.040, 0.32), (0.32, 0.44, 0.49), mats["clay"], 0.012, role="damage_clean_exit", bh="BH-180")
    damage_block["clean_exit"] = "source curve + chunks + uv handoff"
    parts.append(damage_block)
    crack_pts = [(0.16, 0.40, 0.64), (0.25, 0.40, 0.56), (0.31, 0.40, 0.61), (0.40, 0.40, 0.45), (0.50, 0.40, 0.53)]
    parts.append(curve_line("LAB9_SourceCrackCurvePreserved", crack_pts, mats["magenta"], 0.007, role="damage_clean_exit", bh="BH-180"))
    for i, x in enumerate((0.14, 0.29, 0.44)):
        chunk = rounded_box(f"LAB9_FractureChunkNamed_{i}", (0.08, 0.035, 0.08), (x, 0.40, 0.30), mats["gold"], 0.006, role="damage_clean_exit", bh="BH-180")
        parts.append(chunk)

    inter_a = torus("LAB9_IntersectionSourceA_NotJustVisual", 0.14, 0.006, (0.82, 0.45, 0.56), mats["ghost"], rot=(math.radians(90), 0, 0), role="intersection_guide_curve", bh="BH-181")
    inter_b = cylinder("LAB9_IntersectionSourceB_NotJustVisual", 0.10, 0.40, (0.82, 0.44, 0.56), mats["ghost"], vertices=20, rot=(math.radians(90), 0, 0), role="intersection_guide_curve", bh="BH-181")
    inter_curve = curve_line("LAB9_NamedIntersectionGuideCurve", [(0.68, 0.38, 0.56), (0.75, 0.38, 0.64), (0.90, 0.38, 0.64), (0.97, 0.38, 0.56)], mats["cyan"], 0.007, role="intersection_guide_curve", bh="BH-181")
    parts.extend([inter_a, inter_b, inter_curve])

    stroke_pts = [(1.14, 0.43, 0.34), (1.28, 0.43, 0.54), (1.48, 0.43, 0.48), (1.66, 0.43, 0.66)]
    parts.append(curve_line("LAB9_ProceduralStrokeTimingPath", stroke_pts, mats["magenta"], 0.010, role="procedural_stroke_timing", bh="BH-182"))
    for i, x in enumerate((1.16, 1.34, 1.52, 1.70)):
        tick = rounded_box(f"LAB9_StrokeTimingTick_{i}", (0.020, 0.035, 0.13), (x, 0.40, 0.26), mats["white"], 0.003, role="procedural_stroke_timing", bh="BH-182")
        parts.append(tick)
    marker = sphere("LAB9_ProceduralStrokeRevealMarker", 0.035, (1.14, 0.42, 0.34), mats["gold"], segments=10, ring_count=5, role="procedural_stroke_timing", bh="BH-182")
    marker.keyframe_insert(data_path="location", frame=1)
    marker.location = (1.66, 0.42, 0.66)
    marker.keyframe_insert(data_path="location", frame=96)
    linearize(marker)
    parts.append(marker)
    return parts


def create_node_hygiene_bevel_controls(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB9_NodeHygieneBevelControlsBoard", (3.70, 0.08, 0.64), (0.30, 0.94, 1.20), mats["panel"], 0.025, role="node_lab_panel")
    parts.append(panel)
    frame_specs = [
        ("Inputs", -1.28, mats["blue"]),
        ("Masks", -0.78, mats["green"]),
        ("Realize", -0.25, mats["cyan"]),
        ("Attrs", 0.30, mats["magenta"]),
        ("Export", 0.82, mats["gold"]),
    ]
    for i, (label, x, mat) in enumerate(frame_specs):
        frame = rounded_box(f"LAB9_NodeFrameHygiene_{label}", (0.34, 0.035, 0.22), (x, 0.90, 1.20), mats["ghost"], 0.006, role="node_frame_hygiene", bh="BH-183")
        node = rounded_box(f"LAB9_NodeFrameSocket_{label}", (0.14, 0.040, 0.07), (x, 0.86, 1.20), mat, 0.006, role="node_frame_hygiene", bh="BH-183")
        frame["frame_order"] = i
        parts.extend([frame, node])
        if i:
            parts.append(curve_line(f"LAB9_NodeFrameConnector_{i}", [(frame_specs[i - 1][1] + 0.18, 0.86, 1.20), (x - 0.18, 0.86, 1.20)], mats["cyan"], 0.005, role="node_frame_hygiene", bh="BH-183"))

    bevel_block = rounded_box("LAB9_ProceduralBevelShadingBlock", (0.26, 0.11, 0.22), (1.32, 0.89, 1.20), mats["metal"], 0.035, role="procedural_bevel_shading", bh="BH-184")
    wire = torus("LAB9_ProceduralWireThicknessCheck", 0.13, 0.008, (1.70, 0.89, 1.20), mats["cyan"], rot=(math.radians(90), 0, 0), role="procedural_bevel_shading", bh="BH-184")
    parts.extend([bevel_block, wire])
    parts.extend(arrow("LAB9_BevelGrazingLightCheck", (1.86, 0.82, 1.38), (1.42, 0.88, 1.25), mats["gold"], radius=0.007, role="procedural_bevel_shading", bh="BH-184"))

    control_names = ("radius", "spacing", "normal")
    for i, name in enumerate(control_names):
        rail = rounded_box(f"LAB9_ShapeControlRail_{name}", (0.28, 0.030, 0.026), (-1.28 + i * 0.38, 0.88, 0.98), mats["dark"], 0.004, role="shape_control_exposed", bh="BH-185")
        knob = sphere(f"LAB9_ShapeControlKnob_{name}", 0.030, (-1.38 + i * 0.38 + i * 0.035, 0.86, 0.98), [mats["gold"], mats["green"], mats["magenta"]][i], segments=10, ring_count=5, role="shape_control_exposed", bh="BH-185")
        rail["control"] = name
        parts.extend([rail, knob])
    for i, x in enumerate((-0.05, 0.10, 0.25, 0.40)):
        rivet = sphere(f"LAB9_ProceduralRivetSpacingControl_{i}", 0.030, (x, 0.86, 0.98), mats["gold"], segments=10, ring_count=5, role="shape_control_exposed", bh="BH-185")
        parts.append(rivet)
    normal_plate = rounded_box("LAB9_NormalAlignedPlacementSample", (0.26, 0.035, 0.12), (0.72, 0.86, 0.98), mats["ghost"], 0.006, rot=(0, math.radians(-14), 0), role="shape_control_exposed", bh="BH-185")
    parts.append(normal_plate)
    parts.extend(arrow("LAB9_NormalAlignedControlArrow", (0.72, 0.84, 1.02), (0.86, 0.82, 1.16), mats["magenta"], radius=0.006, role="shape_control_exposed", bh="BH-185"))
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB9_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-169..BH-185")
    floor = rounded_box("LAB9_StudioFloor_NotExported", (5.10, 3.30, 0.065), (0.22, -0.02, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_apply_scatter_curve_board(mats))
    export_parts.extend(create_displace_foliage_instance_board(mats))
    export_parts.extend(create_surface_attribute_sim_board(mats))
    export_parts.extend(create_back_procedural_board(mats))
    export_parts.extend(create_node_hygiene_bevel_controls(mats))
    labels = [
        add_text("LAB9_Label_ApplyScatterCurve", "APPLY / SCATTER / CURVES", (-1.30, -1.23, 1.14), 0.050, mats["white"]),
        add_text("LAB9_Label_DisplaceFoliageInstances", "BOUNDS / LOD / INSTANCES", (0.30, -1.23, 1.14), 0.050, mats["white"]),
        add_text("LAB9_Label_SurfaceAttrsSim", "SURFACE / ATTRS / SIM LOOP", (1.88, -1.23, 1.14), 0.050, mats["white"]),
        add_text("LAB9_Label_ProceduralSystems", "REPEAT / GRID / DAMAGE / GUIDES / STROKES", (0.30, 0.13, 1.16), 0.046, mats["white"]),
        add_text("LAB9_Label_NodeHygiene", "FRAMED NODE MAP + BEVEL + EXPOSED CONTROLS", (0.30, 0.70, 1.56), 0.044, mats["white"]),
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
        if obj.name.startswith("LAB9_SimulationTrailPoint_"):
            angle_offset = int(obj.name.rsplit("_", 1)[-1]) * math.tau / 4
            obj.rotation_euler.z = angle_offset
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = angle_offset + math.tau
            obj.keyframe_insert(data_path="rotation_euler", frame=96)
            linearize(obj)
        if obj.name == "LAB9_ProceduralWireThicknessCheck":
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
        "apply_boundary",
        "scatter_density_seed",
        "curve_orientation_qa",
        "set_position_bounds",
        "foliage_lod_gate",
        "instance_index_logic",
        "surface_contact_rule",
        "attribute_contract",
        "simulation_reset_loop",
        "repeat_stop_condition",
        "procedural_grid_bounds",
        "damage_clean_exit",
        "intersection_guide_curve",
        "procedural_stroke_timing",
        "node_frame_hygiene",
        "procedural_bevel_shading",
        "shape_control_exposed",
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
    if "LAB9_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    if "LAB9_ProceduralStrokeRevealMarker" not in animated:
        warnings.append("Stroke timing marker is not animated.")
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
        "source_goal": "550-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "lifehack": obj.get("lifehack"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Apply/realize/mesh boundary is visible.",
            "Scatter density/seed, curve orientation, Set Position bounds and foliage LOD checks are visible.",
            "Instance variation, surface contact and attribute contracts are visible.",
            "Simulation loop/reset, repeat bounds, grid bounds, damage exit and guide curves are visible.",
            "Node frame hygiene, bevel shading and exposed shape controls are visible.",
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
