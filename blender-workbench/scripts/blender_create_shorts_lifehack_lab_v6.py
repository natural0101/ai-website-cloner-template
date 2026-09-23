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

ASSET = "blender_shorts_lifehack_lab_v6"
SCENE_NAME = "BlenderShortsLifehackLabV6"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-116", "name": "Procedural Systems Need Exposed Controls", "applied": "Parameter sliders expose density, spacing, seed, profile and scale."},
    {"id": "BH-117", "name": "Realize Procedural Geometry Before Fragile Delivery", "applied": "A realized mesh gate separates procedural preview from export geometry."},
    {"id": "BH-118", "name": "Instance Distribution Needs Masks And Orientation", "applied": "Scatter dots use a density mask, orientation arrows and bounded variation."},
    {"id": "BH-119", "name": "Proximity Effects Need A Debug Layer", "applied": "Attractor/repulsor controls include falloff rings before beauty polish."},
    {"id": "BH-120", "name": "Procedural Materials Need Coordinates", "applied": "Material slot cards show coordinate/material handoff for export."},
    {"id": "BH-121", "name": "Cloth Starts With Pins", "applied": "A waving banner shows pinned anchors before wind/fold styling."},
    {"id": "BH-122", "name": "Cloth Motion Needs Frame Strips", "applied": "Frame-strip cards review cloth positions over time."},
    {"id": "BH-123", "name": "Thin Materials Need Physical Thickness Cues", "applied": "Banner edges, folds and wrinkles make the cloth read as thin fabric."},
    {"id": "BH-124", "name": "Drivers Need Visible Controls", "applied": "Gear/spring rig has visible control dials and amplitude markers."},
    {"id": "BH-125", "name": "Bake Constraints For Delivery", "applied": "Bake tick blocks mark constraint-to-keyframe review."},
    {"id": "BH-126", "name": "IK Needs Pole And Twist Planning", "applied": "IK pole and twist helpers are visible around a small limb rig."},
    {"id": "BH-127", "name": "Shape Keys Need Named Targets", "applied": "Morph target states are separated as named cards."},
    {"id": "BH-128", "name": "Expressions Need Multiple Small Keys", "applied": "Blink/expression states are split into small timed morph markers."},
    {"id": "BH-129", "name": "Shape Keys Can Be Rig Controls", "applied": "A bone-control proxy drives the shape-key board."},
    {"id": "BH-130", "name": "Line Art Must Be Scoped", "applied": "Outlines are grouped into object, foreground and background layers."},
    {"id": "BH-131", "name": "Line Boil Needs Controlled Noise", "applied": "Line-boil curves use small, bounded offsets over several frames."},
    {"id": "BH-132", "name": "Imported 2D Strokes Need Cleanup", "applied": "Sketch cleanup cards show scale, depth, layer and material checks."},
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
            "Coat Weight": 0.05,
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
        "base": make_mat("Lab6_BaseGraphite", (0.018, 0.020, 0.027, 1.0), roughness=0.56),
        "panel": make_mat("Lab6_PanelInk", (0.08, 0.095, 0.13, 1.0), roughness=0.62),
        "cyan": make_mat("Lab6_ControlCyan", (0.04, 0.78, 1.0, 1.0), roughness=0.34, emission=(0.0, 0.36, 0.8, 1.0), emission_strength=0.15),
        "green": make_mat("Lab6_MaskGreen", (0.18, 0.90, 0.46, 1.0), roughness=0.45, emission=(0.04, 0.42, 0.12, 1.0), emission_strength=0.08),
        "gold": make_mat("Lab6_BakeGold", (1.0, 0.70, 0.16, 1.0), roughness=0.40, metallic=0.06),
        "pink": make_mat("Lab6_MorphPink", (1.0, 0.16, 0.56, 1.0), roughness=0.38, emission=(0.55, 0.02, 0.25, 1.0), emission_strength=0.12),
        "violet": make_mat("Lab6_ProximityViolet", (0.56, 0.28, 1.0, 1.0), roughness=0.34, emission=(0.25, 0.08, 0.75, 1.0), emission_strength=0.16),
        "cloth": make_mat("Lab6_ClothCoral", (1.0, 0.34, 0.22, 1.0), roughness=0.76),
        "cloth_edge": make_mat("Lab6_ClothEdgeCream", (1.0, 0.86, 0.58, 1.0), roughness=0.60),
        "metal": make_mat("Lab6_DriverMetal", (0.62, 0.69, 0.78, 1.0), roughness=0.34, metallic=0.45),
        "line": make_mat("Lab6_LineArtBlack", (0.02, 0.018, 0.016, 1.0), roughness=0.50),
        "stroke": make_mat("Lab6_GreaseStrokeBlue", (0.10, 0.48, 1.0, 1.0), roughness=0.42, emission=(0.02, 0.25, 0.85, 1.0), emission_strength=0.14),
        "ghost": make_mat("Lab6_DebugGhost", (0.40, 0.70, 1.0, 1.0), roughness=0.55, alpha=0.25, emission=(0.05, 0.25, 0.55, 1.0), emission_strength=0.06),
        "white": make_mat("Lab6_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.55),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB6_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.02,
    rot: tuple[float, float, float] = (0, 0, 0),
    export: bool = True,
    role: str = "rounded_box",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB6_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB6_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export=export)


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
    bpy.ops.mesh.primitive_torus_add(major_segments=54, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
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


def arrow(name: str, start: tuple[float, float, float], end: tuple[float, float, float], mat: bpy.types.Material, radius: float = 0.014, role: str = "direction_arrow") -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    mid = a.lerp(b, 0.76)
    return [
        cone_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, radius, mat, role=role),
        cone_between(f"{name}_Head", tuple(mid), tuple(b), radius * 2.8, 0.0, mat, role=role),
    ]


def curve_line(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float = 0.010, role: str = "curve_line") -> bpy.types.Object:
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
    scene.world = scene.world or bpy.data.worlds.new("LAB6_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.8, -4.8, 4.6))
    key = bpy.context.object
    key.name = "LAB6_KeyArea_Warm"
    key.data.energy = 600
    key.data.size = 4.8
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.6, 2.6, 3.2))
    fill = bpy.context.object
    fill.name = "LAB6_FillArea_Cool"
    fill.data.energy = 120
    fill.data.size = 5.0
    fill.data.color = (0.56, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.2, 3.0, 2.5))
    rim = bpy.context.object
    rim.name = "LAB6_RimPoint_Cyan"
    rim.data.energy = 210
    rim.data.color = (0.38, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.35, -5.80, 3.25), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB6_Camera_Hero3Q"
    cam.data.lens = 35
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.2
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


def create_procedural_control_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    board = rounded_box("LAB6_ProceduralControlBoard", (0.95, 0.08, 0.74), (-1.72, -0.78, 0.44), mats["panel"], 0.025, role="procedural_control_board")
    parts.append(board)
    slider_specs = [("Density", 0.64), ("Spacing", 0.50), ("Seed", 0.36), ("Profile", 0.22), ("Scale", 0.08)]
    for i, (name, z) in enumerate(slider_specs):
        rail = rounded_box(f"LAB6_ProceduralInput_{name}_Rail", (0.58, 0.035, 0.025), (-1.72, -0.84, z), mats["ghost"], 0.006, role="procedural_control_input")
        knob_x = -1.94 + 0.11 * i
        knob = sphere(f"LAB6_ProceduralInput_{name}_Knob", 0.035, (knob_x, -0.84, z + 0.035), mats["cyan"], segments=14, ring_count=7, role="procedural_control_input")
        parts.extend([rail, knob])
    gate = rounded_box("LAB6_RealizedMeshExportGate", (0.28, 0.08, 0.32), (-1.18, -0.74, 0.36), mats["green"], 0.018, role="realized_mesh_gate")
    parts.append(gate)
    for i, mat in enumerate((mats["cyan"], mats["green"], mats["gold"])):
        slot = rounded_box(f"LAB6_MaterialCoordinateSlot_{i}", (0.13, 0.035, 0.13), (-1.40 + i * 0.15, -0.60, 0.14), mat, 0.010, role="procedural_material_coordinate")
        parts.append(slot)
    return parts


def create_scatter_proximity_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    plate = rounded_box("LAB6_ScatterDensityMaskPlate", (1.28, 0.06, 0.58), (-0.42, -0.72, 0.30), mats["green"], 0.025, rot=(0, 0, math.radians(-3)), role="scatter_density_mask")
    parts.append(plate)
    positions = [
        (-0.92, -0.74, 0.22, 0.025), (-0.78, -0.72, 0.34, 0.034), (-0.62, -0.70, 0.45, 0.020),
        (-0.44, -0.72, 0.40, 0.030), (-0.28, -0.76, 0.28, 0.023), (-0.12, -0.74, 0.52, 0.036),
        (0.04, -0.70, 0.36, 0.018), (0.18, -0.73, 0.24, 0.024), (-0.66, -0.54, 0.25, 0.016),
        (-0.42, -0.52, 0.49, 0.021), (-0.16, -0.56, 0.18, 0.018),
    ]
    for i, (x, y, z, radius) in enumerate(positions):
        inst = sphere(f"LAB6_ScatterInstance_Realized_{i:02d}", radius, (x, y, z), mats["cyan"], segments=12, ring_count=6, role="scatter_instance_realized")
        parts.append(inst)
    orientation_arrows = [
        ((-0.84, -0.50, 0.54), (-0.30, -0.56, 0.64)),
        ((-0.64, -0.42, 0.16), (0.10, -0.54, 0.30)),
        ((-0.18, -0.44, 0.54), (0.24, -0.58, 0.42)),
    ]
    for i, (start, end) in enumerate(orientation_arrows):
        parts.extend(arrow(f"LAB6_InstanceOrientationVector_{i}", start, end, mats["cyan"], radius=0.010, role="scatter_orientation_rule"))
    attractor = sphere("LAB6_ProximityAttractor_DebugControl", 0.07, (0.38, -0.62, 0.42), mats["violet"], role="proximity_debug_control")
    repulsor = sphere("LAB6_ProximityRepulsor_DebugControl", 0.055, (-0.98, -0.61, 0.42), mats["pink"], role="proximity_debug_control")
    parts.extend([attractor, repulsor])
    for i, radius in enumerate((0.22, 0.38, 0.54)):
        parts.append(torus(f"LAB6_ProximityFalloff_DebugRing_{i}", radius, 0.008, (0.38, -0.62, 0.42), mats["violet"], rot=(math.radians(90), 0, 0), role="proximity_debug_layer"))
    return parts


def create_cloth_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    cols = 9
    rows = 5
    verts = []
    faces = []
    for r in range(rows):
        for c in range(cols):
            x = 0.66 + c * 0.09
            y = -0.80
            z = 0.20 + r * 0.095 + 0.030 * math.sin(c * 0.95 + r * 0.65)
            verts.append((x, y, z))
    for r in range(rows - 1):
        for c in range(cols - 1):
            a = r * cols + c
            faces.append((a, a + 1, a + cols + 1, a + cols))
    mesh = bpy.data.meshes.new("LAB6_PinnedClothBannerMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    cloth = bpy.data.objects.new("LAB6_PinnedClothBanner_WavyThinSheet", mesh)
    bpy.context.collection.objects.link(cloth)
    cloth.data.materials.append(mats["cloth"])
    smooth(cloth)
    tag(cloth, "pinned_cloth_sheet")
    parts.append(cloth)
    for c in range(cols):
        x = 0.66 + c * 0.09
        pin = sphere(f"LAB6_ClothPinAnchor_{c:02d}", 0.018, (x, -0.815, 0.64), mats["gold"], segments=10, ring_count=5, role="pinned_cloth_anchor")
        parts.append(pin)
    top_edge = curve_line("LAB6_ClothPhysicalThickness_TopEdge", [(0.64, -0.82, 0.66), (1.42, -0.82, 0.64)], mats["cloth_edge"], 0.010, role="thin_material_thickness_cue")
    bottom_edge = curve_line("LAB6_ClothPhysicalThickness_BottomEdge", [(0.64, -0.82, 0.17), (1.42, -0.82, 0.20)], mats["cloth_edge"], 0.010, role="thin_material_thickness_cue")
    parts.extend([top_edge, bottom_edge])
    for i, start_z in enumerate((0.28, 0.40, 0.52)):
        fold = curve_line(f"LAB6_ClothFoldDirection_{i}", [(0.72 + i * 0.18, -0.84, start_z), (0.80 + i * 0.16, -0.84, start_z + 0.08), (0.90 + i * 0.12, -0.84, start_z - 0.02)], mats["cloth_edge"], 0.006, role="cloth_fold_direction")
        parts.append(fold)
    for i, (a, b) in enumerate((((0.42, -0.72, 0.30), (0.62, -0.78, 0.38)), ((0.42, -0.72, 0.48), (0.62, -0.78, 0.54)), ((0.42, -0.72, 0.64), (0.62, -0.78, 0.66)))):
        parts.extend(arrow(f"LAB6_ClothWindDirection_{i}", a, b, mats["cyan"], radius=0.010, role="cloth_wind_direction"))
    for i, z in enumerate((0.16, 0.25, 0.36, 0.28)):
        tick = rounded_box(f"LAB6_ClothFrameStrip_{i:02d}", (0.10, 0.035, z), (1.56 + i * 0.12, -0.76, 0.08 + z / 2), mats["gold"], 0.008, role="cloth_frame_strip")
        parts.append(tick)
    return parts


def create_driver_rig_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    panel = rounded_box("LAB6_DriverConstraintRigPanel", (1.10, 0.08, 0.70), (-1.38, 0.50, 0.38), mats["panel"], 0.025, role="driver_rig_panel")
    parts.append(panel)
    gear_a = torus("LAB6_DriverGear_A_RatioControl", 0.13, 0.018, (-1.74, 0.44, 0.46), mats["metal"], rot=(math.radians(90), 0, 0), role="driver_control")
    gear_b = torus("LAB6_DriverGear_B_LinkedRotation", 0.17, 0.018, (-1.42, 0.44, 0.46), mats["metal"], rot=(math.radians(90), 0, 0), role="driver_control")
    parts.extend([gear_a, gear_b])
    for gear, radius, count in ((gear_a, 0.16, 10), (gear_b, 0.20, 12)):
        base = gear.location.copy()
        for i in range(count):
            a = math.tau * i / count
            tooth = rounded_box(f"{gear.name}_Tooth_{i:02d}", (0.035, 0.035, 0.055), (base.x + math.cos(a) * radius, base.y, base.z + math.sin(a) * radius), mats["metal"], 0.004, rot=(0, a, 0), role="driver_control")
            parts.append(tooth)
    for i in range(14):
        a0 = i / 14 * math.tau * 1.8
        a1 = (i + 1) / 14 * math.tau * 1.8
        start = (-1.02 + math.cos(a0) * 0.075, 0.45, 0.22 + i * 0.018 + math.sin(a0) * 0.03)
        end = (-1.02 + math.cos(a1) * 0.075, 0.45, 0.22 + (i + 1) * 0.018 + math.sin(a1) * 0.03)
        parts.append(curve_line(f"LAB6_DriverSpringSegment_{i:02d}", [start, end], mats["cyan"], 0.007, role="driver_control"))
    control = sphere("LAB6_DriverAmplitudeControl_Knob", 0.060, (-1.05, 0.36, 0.66), mats["pink"], role="driver_control")
    parts.append(control)
    for i, x in enumerate((-1.84, -1.70, -1.56, -1.42, -1.28)):
        tick = rounded_box(f"LAB6_ConstraintBakeTick_{i:02d}", (0.070, 0.035, 0.16 + i * 0.025), (x, 0.66, 0.13 + i * 0.012), mats["gold"], 0.006, role="constraint_bake_tick")
        parts.append(tick)
    limb_a = cone_between("LAB6_IK_LimbUpper", (-0.88, 0.46, 0.28), (-0.64, 0.48, 0.48), 0.025, 0.025, mats["cloth_edge"], role="ik_limb_segment")
    limb_b = cone_between("LAB6_IK_LimbLower", (-0.64, 0.48, 0.48), (-0.42, 0.48, 0.30), 0.025, 0.025, mats["cloth_edge"], role="ik_limb_segment")
    pole = sphere("LAB6_IK_PoleTarget_Helper", 0.045, (-0.62, 0.28, 0.54), mats["violet"], role="ik_pole_helper")
    twist = torus("LAB6_IK_TwistAxis_HelperRing", 0.11, 0.008, (-0.64, 0.48, 0.48), mats["cyan"], rot=(math.radians(90), 0, 0), role="ik_twist_helper")
    parts.extend([limb_a, limb_b, pole, twist])
    return parts


def create_shape_line_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    board = rounded_box("LAB6_ShapeKeyLineArtBoard", (1.52, 0.08, 0.72), (0.70, 0.54, 0.40), mats["panel"], 0.025, role="shape_line_board")
    parts.append(board)
    for i, (name, x, scale) in enumerate((("Basis", 0.14, (1, 0.72, 1)), ("Blink", 0.38, (1.18, 0.50, 0.72)), ("Smile", 0.62, (1.32, 0.74, 0.88)), ("Morph", 0.86, (0.80, 0.82, 1.28)))):
        state = sphere(f"LAB6_ShapeKeyTarget_{name}", 0.075, (x, 0.48, 0.56), mats["pink"], segments=18, ring_count=9, scale=scale, role="shape_key_target_state")
        parts.append(state)
        outline = torus(f"LAB6_ShapeKeyTarget_{name}_ScopedOutline", 0.090, 0.006, (x, 0.475, 0.56), mats["line"], rot=(math.radians(90), 0, 0), role="line_art_scoped_layer")
        parts.append(outline)
    bone = cone_between("LAB6_BoneControlProxy_ShapeKeys", (1.12, 0.48, 0.25), (1.30, 0.48, 0.64), 0.030, 0.018, mats["gold"], role="shape_key_bone_control")
    parts.append(bone)
    for i, radius in enumerate((0.25, 0.34, 0.43)):
        layer = torus(f"LAB6_LineArtScopeLayer_{i}", radius, 0.006, (0.54, 0.47, 0.38), mats["stroke" if i == 1 else "line"], rot=(math.radians(90), 0, 0), role="line_art_scoped_layer")
        parts.append(layer)
    boil_sets = [
        [(1.05, 0.45, 0.26), (1.16, 0.45, 0.34), (1.28, 0.45, 0.28), (1.38, 0.45, 0.38)],
        [(1.05, 0.45, 0.34), (1.16, 0.45, 0.42), (1.28, 0.45, 0.36), (1.38, 0.45, 0.46)],
        [(1.05, 0.45, 0.42), (1.16, 0.45, 0.50), (1.28, 0.45, 0.44), (1.38, 0.45, 0.54)],
    ]
    for i, pts in enumerate(boil_sets):
        curve = curve_line(f"LAB6_ControlledLineBoil_Frame_{i:02d}", pts, mats["stroke"], 0.006, role="line_boil_control")
        parts.append(curve)
    cleanup_specs = [("Scale", 0.08), ("Depth", 0.22), ("Layer", 0.36), ("Mat", 0.50)]
    for name, z in cleanup_specs:
        card = rounded_box(f"LAB6_ImportedStrokeCleanup_{name}", (0.14, 0.035, 0.10), (1.50, 0.49, z), mats["cyan"], 0.008, role="imported_stroke_cleanup")
        parts.append(card)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB6_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB6_StudioFloor_NotExported", (4.9, 3.2, 0.065), (0.0, -0.08, -0.045), mats["base"], 0.04, export=False, role="preview_floor")
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_procedural_control_board(mats))
    export_parts.extend(create_scatter_proximity_board(mats))
    export_parts.extend(create_cloth_board(mats))
    export_parts.extend(create_driver_rig_board(mats))
    export_parts.extend(create_shape_line_board(mats))

    labels = [
        add_text("LAB6_Label_Procedural", "PROCEDURAL CONTROLS", (-1.55, -1.16, 0.78), 0.055, mats["white"]),
        add_text("LAB6_Label_Scatter", "MASKS + PROXIMITY DEBUG", (-0.34, -1.10, 0.84), 0.052, mats["white"]),
        add_text("LAB6_Label_Cloth", "PINS + FRAME STRIP", (1.10, -1.10, 0.82), 0.052, mats["white"]),
        add_text("LAB6_Label_Drivers", "DRIVERS / BAKE / IK", (-1.36, 0.18, 0.92), 0.052, mats["white"]),
        add_text("LAB6_Label_ShapeLine", "SHAPE KEYS + LINE ART", (0.70, 0.22, 0.96), 0.052, mats["white"]),
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
        if obj.name in {"LAB6_DriverGear_A_RatioControl", "LAB6_DriverGear_B_LinkedRotation"}:
            obj.rotation_euler.y = 0
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.y = math.tau if obj.name.endswith("RatioControl") else -math.tau * 1.35
            obj.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
            linearize(obj)
        if obj.name == "LAB6_DriverAmplitudeControl_Knob":
            obj.location.z += 0.02
            obj.keyframe_insert(data_path="location", frame=1)
            obj.location.z += 0.10
            obj.keyframe_insert(data_path="location", frame=48)
            obj.location.z -= 0.10
            obj.keyframe_insert(data_path="location", frame=96)
            linearize(obj)
        if obj.name == "LAB6_BoneControlProxy_ShapeKeys":
            obj.rotation_euler.z = -0.12
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.rotation_euler.z = 0.25
            obj.keyframe_insert(data_path="rotation_euler", frame=48)
            obj.rotation_euler.z = -0.12
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
        "procedural_control_input",
        "realized_mesh_gate",
        "scatter_density_mask",
        "scatter_orientation_rule",
        "proximity_debug_layer",
        "pinned_cloth_sheet",
        "pinned_cloth_anchor",
        "cloth_frame_strip",
        "driver_control",
        "constraint_bake_tick",
        "ik_pole_helper",
        "shape_key_target_state",
        "shape_key_bone_control",
        "line_art_scoped_layer",
        "line_boil_control",
        "imported_stroke_cleanup",
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
    if "LAB6_Root_TurntableAnimated" not in animated:
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
        "source_goal": "400-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Procedural controls are visible and named.",
            "Scatter and proximity debug layers are inspectable.",
            "Pinned cloth and frame-strip review are readable.",
            "Driver/constraint controls, bake ticks, IK pole and twist helpers are present.",
            "Shape-key targets and line-art layers are scoped and separated.",
            "Only exportable geometry goes into GLB.",
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
