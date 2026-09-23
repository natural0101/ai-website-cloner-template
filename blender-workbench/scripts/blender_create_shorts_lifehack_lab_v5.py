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

ASSET = "blender_shorts_lifehack_lab_v5"
SCENE_NAME = "BlenderShortsLifehackLabV5"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-101", "name": "Physics Needs Roles", "applied": "Rigid body cards separate active, passive and collision roles."},
    {"id": "BH-102", "name": "Bake Simulations For Delivery", "applied": "A frame-strip cache rail shows that physics/particles need a reviewed baked range."},
    {"id": "BH-103", "name": "Copy Settings, Then Verify Exceptions", "applied": "Copied rigid-body blocks include one highlighted exception marker for mass/friction review."},
    {"id": "BH-104", "name": "Force Fields Are Art Direction", "applied": "Wind/vortex influence zones are visible as named rings and direction arrows."},
    {"id": "BH-105", "name": "Particle Density Needs A Mask", "applied": "Particles are concentrated over a visible mask ramp instead of uniform noise."},
    {"id": "BH-106", "name": "Particle Render Visibility Is A Gate", "applied": "Viewport, render and export visibility ticks are modeled as QA blocks."},
    {"id": "BH-107", "name": "Particle Paths Need Direction", "applied": "Particle drift follows explicit cyan wind arrows."},
    {"id": "BH-108", "name": "Smoke Starts With Domain Bounds", "applied": "Smoke plume sits inside a named non-export domain helper."},
    {"id": "BH-109", "name": "Simulation Resolution Is A Lookdev Control", "applied": "Low, medium and high resolution preview blocks compare detail/cost."},
    {"id": "BH-110", "name": "Fluid Needs Boundaries", "applied": "Fluid volume is contained by collision-wall geometry and a non-export domain cage."},
    {"id": "BH-111", "name": "Fire Is Three Layers", "applied": "Fire is separated into fuel core, smoke layer and light/glow shell."},
    {"id": "BH-112", "name": "Explosion Layers Stay Separate", "applied": "Debris, shockwave, smoke and glow are separate named mesh groups."},
    {"id": "BH-113", "name": "Shield FX Are Surface Plus Trigger", "applied": "Shield surface and impact trigger zone are distinct editable rings."},
    {"id": "BH-114", "name": "Dust Is Subtle Motion", "applied": "Dust is sparse, varied in scale and placed along the wind path."},
    {"id": "BH-115", "name": "Simulation Helpers Are Not Export Geometry", "applied": "Domains, field visualizers, labels, camera, lights and floor are marked non-export."},
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
        "base": make_mat("Lab5_BaseInk", (0.018, 0.020, 0.026, 1.0), roughness=0.55),
        "active": make_mat("Lab5_ActiveBody_Orange", (1.0, 0.43, 0.11, 1.0), roughness=0.48, emission=(0.55, 0.16, 0.02, 1.0), emission_strength=0.08),
        "passive": make_mat("Lab5_PassiveBody_Blue", (0.10, 0.42, 0.96, 1.0), roughness=0.50),
        "collision": make_mat("Lab5_CollisionWhite", (0.86, 0.92, 1.0, 1.0), roughness=0.58),
        "exception": make_mat("Lab5_ExceptionMagenta", (1.0, 0.12, 0.55, 1.0), roughness=0.35, emission=(0.70, 0.02, 0.28, 1.0), emission_strength=0.16),
        "cache": make_mat("Lab5_CacheGold", (1.0, 0.72, 0.18, 1.0), roughness=0.42, metallic=0.08),
        "field": make_mat("Lab5_FieldCyan", (0.02, 0.72, 1.0, 1.0), roughness=0.32, emission=(0.0, 0.52, 1.0, 1.0), emission_strength=0.25),
        "field_soft": make_mat("Lab5_FieldGhost", (0.12, 0.74, 1.0, 1.0), roughness=0.40, alpha=0.32, emission=(0.02, 0.35, 0.75, 1.0), emission_strength=0.12),
        "particle": make_mat("Lab5_ParticleGreen", (0.22, 0.95, 0.46, 1.0), roughness=0.38, emission=(0.05, 0.55, 0.16, 1.0), emission_strength=0.10),
        "mask": make_mat("Lab5_DensityMaskGradient", (0.16, 0.84, 0.54, 1.0), roughness=0.66),
        "dust": make_mat("Lab5_SubtleDust", (0.82, 0.77, 0.64, 1.0), roughness=0.86, alpha=0.56),
        "domain": make_mat("Lab5_DomainHelper_NotExport", (0.44, 0.64, 1.0, 1.0), roughness=0.72, alpha=0.13),
        "smoke": make_mat("Lab5_SmokeLayer", (0.42, 0.48, 0.58, 1.0), roughness=0.82, alpha=0.64),
        "fire_core": make_mat("Lab5_FireFuelCore", (1.0, 0.25, 0.06, 1.0), roughness=0.30, emission=(1.0, 0.12, 0.02, 1.0), emission_strength=0.45),
        "fire_flame": make_mat("Lab5_FireFlame", (1.0, 0.78, 0.08, 1.0), roughness=0.24, alpha=0.80, emission=(1.0, 0.46, 0.04, 1.0), emission_strength=0.36),
        "fluid": make_mat("Lab5_FluidTeal", (0.02, 0.68, 0.82, 1.0), roughness=0.22, alpha=0.72),
        "shock": make_mat("Lab5_ShockwaveViolet", (0.62, 0.26, 1.0, 1.0), roughness=0.33, emission=(0.36, 0.10, 0.85, 1.0), emission_strength=0.22),
        "shield": make_mat("Lab5_ShieldSurface", (0.22, 0.80, 1.0, 1.0), roughness=0.30, alpha=0.42, emission=(0.06, 0.52, 1.0, 1.0), emission_strength=0.32),
        "debris": make_mat("Lab5_DebrisCharcoal", (0.12, 0.10, 0.095, 1.0), roughness=0.74),
        "label": make_mat("Lab5_LabelWhite", (0.95, 0.97, 1.0, 1.0), roughness=0.55),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB5_WeightedNormals", type="WEIGHTED_NORMAL")


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
        mod = obj.modifiers.new(name="LAB5_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB5_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, role, export=export)


def sphere(
    name: str,
    radius: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    segments: int = 24,
    ring_count: int = 12,
    scale: tuple[float, float, float] = (1, 1, 1),
    export: bool = True,
    role: str = "sphere",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transform(obj)
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export=export)


def cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    vertices: int = 24,
    rot: tuple[float, float, float] = (0, 0, 0),
    export: bool = True,
    role: str = "cylinder",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export=export)


def cone_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius1: float,
    radius2: float,
    mat: bpy.types.Material,
    vertices: int = 24,
    export: bool = True,
    role: str = "cone_between",
) -> bpy.types.Object:
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    loc = a + direction * 0.5
    depth = direction.length
    rot = direction.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export=export)


def arrow(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    mat: bpy.types.Material,
    radius: float = 0.018,
    export: bool = True,
    role: str = "direction_arrow",
) -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    shaft_end = a.lerp(b, 0.76)
    shaft = cone_between(f"{name}_Shaft", tuple(a), tuple(shaft_end), radius, radius, mat, vertices=18, export=export, role=role)
    head = cone_between(f"{name}_Head", tuple(shaft_end), tuple(b), radius * 2.8, 0.0, mat, vertices=22, export=export, role=role)
    return [shaft, head]


def torus(
    name: str,
    major: float,
    minor: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    rot: tuple[float, float, float] = (0, 0, 0),
    export: bool = True,
    role: str = "ring",
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export=export)


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
    scene.world = scene.world or bpy.data.worlds.new("LAB5_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.4, -4.6, 4.6))
    key = bpy.context.object
    key.name = "LAB5_KeyArea_Warm"
    key.data.energy = 560
    key.data.size = 4.5
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.5, 2.4, 3.0))
    fill = bpy.context.object
    fill.name = "LAB5_FillArea_Cool"
    fill.data.energy = 105
    fill.data.size = 5.0
    fill.data.color = (0.55, 0.74, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.4, 2.8, 2.3))
    rim = bpy.context.object
    rim.name = "LAB5_RimPoint_Cyan"
    rim.data.energy = 210
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(1.65, -0.4, 1.45))
    fire = bpy.context.object
    fire.name = "LAB5_FirePractical_NotExported"
    fire.data.energy = 95
    fire.data.color = (1.0, 0.47, 0.14)
    tag(fire, "practical_fire_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.20, -5.60, 3.30), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB5_Camera_Hero3Q"
    cam.data.lens = 36
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 6.0
    cam.data.dof.aperture_fstop = 9.0
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def linearize(obj: bpy.types.Object) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    fcurves = getattr(action, "fcurves", None)
    if fcurves is None:
        return
    for curve in fcurves:
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"


def create_rigid_body_role_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    base = rounded_box("LAB5_RigidRoleBoard_CollisionFloor", (1.22, 0.76, 0.06), (-1.48, -0.82, 0.04), mats["collision"], 0.025, role="collision_floor")
    parts.append(base)
    passive_specs = [
        ("A", (-1.80, -0.88, 0.20), (0.18, 0.18, 0.20)),
        ("B", (-1.56, -0.88, 0.20), (0.18, 0.18, 0.20)),
        ("C", (-1.68, -0.88, 0.42), (0.18, 0.18, 0.20)),
    ]
    for suffix, loc, size in passive_specs:
        block = rounded_box(f"LAB5_RigidBody_Passive_{suffix}", size, loc, mats["passive"], 0.018, role="passive_rigid_body")
        parts.append(block)
    active = rounded_box("LAB5_RigidBody_Active_FallingCube", (0.24, 0.24, 0.24), (-1.24, -0.80, 0.75), mats["active"], 0.025, rot=(0.18, 0.08, 0.28), role="active_rigid_body")
    active["mass"] = 3.0
    active["friction"] = 0.42
    parts.append(active)
    exception = rounded_box("LAB5_SettingsCopy_ExceptionMarker", (0.05, 0.05, 0.40), (-1.10, -0.80, 0.44), mats["exception"], 0.008, role="copied_settings_exception")
    parts.append(exception)
    trail_heights = [0.60, 0.47, 0.34]
    for i, z in enumerate(trail_heights):
        ghost = rounded_box(f"LAB5_BakedPhysicsGhostFrame_{i+1:02d}", (0.16, 0.16, 0.03), (-1.24 - i * 0.10, -0.80, z), mats["cache"], 0.008, rot=(0, 0, i * 0.18), role="baked_simulation_frame")
        ghost.scale.z = 0.22
        parts.append(ghost)
    for i, x in enumerate((-1.93, -1.72, -1.51, -1.30, -1.09)):
        tick = rounded_box(f"LAB5_CacheRail_FrameTick_{i:02d}", (0.055, 0.08, 0.10 + i * 0.018), (x, -0.44, 0.11 + i * 0.009), mats["cache"], 0.006, role="simulation_cache_tick")
        parts.append(tick)
    return parts


def create_force_particle_field(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    emitter = sphere("LAB5_ParticleEmitter_DensityMasked", 0.12, (-0.18, -0.12, 0.38), mats["particle"], role="particle_emitter")
    parts.append(emitter)
    mask_plate = rounded_box("LAB5_ParticleDensityMask_WeightPaintPlate", (1.20, 0.05, 0.64), (-0.18, -0.18, 0.28), mats["mask"], 0.020, rot=(0, 0, math.radians(-5)), role="particle_density_mask")
    parts.append(mask_plate)
    for i, radius in enumerate((0.32, 0.52, 0.74)):
        ring = torus(f"LAB5_ForceFieldInfluenceRing_{i+1}", radius, 0.010, (-0.18, -0.12, 0.42 + i * 0.025), mats["field_soft"], role="force_field_influence_ring")
        parts.append(ring)
    arrow_specs = [
        ((-0.72, -0.16, 0.36), (-0.14, -0.06, 0.62)),
        ((-0.62, -0.40, 0.26), (0.06, -0.16, 0.44)),
        ((-0.54, 0.04, 0.52), (0.23, 0.02, 0.58)),
        ((-0.38, 0.18, 0.22), (0.34, 0.02, 0.36)),
    ]
    for i, (start, end) in enumerate(arrow_specs):
        parts.extend(arrow(f"LAB5_WindDirectionVector_{i+1}", start, end, mats["field"], radius=0.012, role="particle_path_direction"))
    particle_positions = [
        (-0.55, -0.18, 0.34, 0.025),
        (-0.42, -0.11, 0.47, 0.018),
        (-0.30, -0.04, 0.60, 0.021),
        (-0.16, 0.02, 0.52, 0.015),
        (-0.02, -0.02, 0.42, 0.023),
        (0.14, -0.08, 0.34, 0.014),
        (0.24, -0.14, 0.28, 0.016),
        (-0.62, -0.32, 0.18, 0.013),
        (-0.42, -0.34, 0.22, 0.020),
        (-0.22, -0.28, 0.30, 0.026),
        (0.00, -0.30, 0.26, 0.018),
        (0.20, -0.30, 0.20, 0.013),
    ]
    for i, (x, y, z, radius) in enumerate(particle_positions):
        dot = sphere(f"LAB5_MaskedParticle_{i:02d}", radius, (x, y, z), mats["particle"], segments=12, ring_count=6, role="masked_particle")
        parts.append(dot)
    for i, (name, x) in enumerate((("VIEW", 0.48), ("RENDER", 0.66), ("EXPORT", 0.84))):
        pad = rounded_box(f"LAB5_ParticleVisibilityGate_{name}", (0.13, 0.045, 0.13), (x, -0.40, 0.18), mats["collision"], 0.012, role="particle_visibility_gate")
        tick = torus(f"LAB5_ParticleVisibilityTick_{name}", 0.060, 0.006, (x, -0.40, 0.30), mats["particle"], rot=(math.radians(90), 0, 0), role="particle_visibility_tick")
        parts.extend([pad, tick])
    for i, (x, y, z, radius) in enumerate(((-0.68, 0.20, 0.18, 0.012), (-0.48, 0.25, 0.24, 0.017), (-0.16, 0.22, 0.20, 0.010), (0.10, 0.18, 0.26, 0.014), (0.30, 0.26, 0.21, 0.011))):
        dust = sphere(f"LAB5_SubtleDustDrift_{i:02d}", radius, (x, y, z), mats["dust"], segments=10, ring_count=5, role="subtle_dust_particle")
        parts.append(dust)
    return parts


def create_domain_effects(mats: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    parts: list[bpy.types.Object] = []
    helpers: list[bpy.types.Object] = []
    smoke_domain = rounded_box("LAB5_SmokeDomain_Helper_NotExported", (0.56, 0.56, 0.88), (0.92, -0.80, 0.48), mats["domain"], 0.010, export=False, role="smoke_domain_helper")
    helpers.append(smoke_domain)
    for i, (z, scale) in enumerate(((0.20, (1.0, 0.80, 0.46)), (0.38, (0.86, 0.66, 0.52)), (0.58, (0.66, 0.48, 0.44)), (0.74, (0.46, 0.34, 0.30)))):
        puff = sphere(f"LAB5_SmokeLayer_DensityPuff_{i:02d}", 0.18, (0.92 + i * 0.035, -0.80, z), mats["smoke"], segments=20, ring_count=10, scale=scale, role="smoke_density_layer")
        parts.append(puff)
    fire_domain = rounded_box("LAB5_FireDomain_Helper_NotExported", (0.58, 0.52, 0.82), (1.60, -0.80, 0.45), mats["domain"], 0.010, export=False, role="fire_domain_helper")
    helpers.append(fire_domain)
    fuel = cylinder("LAB5_FireFuelSource_Core", 0.12, 0.10, (1.60, -0.80, 0.14), mats["fire_core"], vertices=28, role="fire_fuel_source")
    flame = cone_between("LAB5_FireFlame_Layer", (1.60, -0.80, 0.18), (1.60, -0.80, 0.78), 0.24, 0.02, mats["fire_flame"], vertices=32, role="fire_flame_layer")
    smoke = sphere("LAB5_FireSmokeCap_Layer", 0.20, (1.60, -0.80, 0.78), mats["smoke"], segments=20, ring_count=10, scale=(1.0, 0.70, 0.44), role="fire_smoke_layer")
    parts.extend([fuel, flame, smoke])
    fluid_domain = rounded_box("LAB5_FluidDomain_Helper_NotExported", (0.70, 0.52, 0.50), (2.24, -0.78, 0.28), mats["domain"], 0.010, export=False, role="fluid_domain_helper")
    helpers.append(fluid_domain)
    tank = rounded_box("LAB5_FluidCollisionTank_Walls", (0.62, 0.08, 0.38), (2.24, -0.80, 0.28), mats["collision"], 0.018, role="fluid_collision_boundary")
    water = rounded_box("LAB5_FluidVolume_Contained", (0.54, 0.12, 0.22), (2.24, -0.80, 0.24), mats["fluid"], 0.020, role="contained_fluid_volume")
    splash = sphere("LAB5_FluidSplash_FramePreview", 0.12, (2.12, -0.80, 0.52), mats["fluid"], segments=18, ring_count=8, scale=(0.70, 0.46, 1.20), role="fluid_splash_preview")
    parts.extend([tank, water, splash])
    for i, (x, height, mat) in enumerate(((0.76, 0.16, mats["collision"]), (0.92, 0.28, mats["mask"]), (1.08, 0.42, mats["field"]))):
        block = rounded_box(f"LAB5_SimResolutionPreview_{i+1}", (0.10, 0.10, height), (x, -0.32, 0.06 + height / 2), mat, 0.008, role="simulation_resolution_preview")
        parts.append(block)
    return parts, helpers


def create_explosion_shield_layers(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    center = (1.50, 0.58, 0.44)
    shock_a = torus("LAB5_ExplosionShockwave_OuterRing", 0.48, 0.014, center, mats["shock"], rot=(math.radians(90), 0, 0), role="explosion_shockwave_layer")
    shock_b = torus("LAB5_ExplosionShockwave_InnerRing", 0.30, 0.012, (1.50, 0.57, 0.44), mats["fire_flame"], rot=(math.radians(90), 0, 0), role="explosion_glow_layer")
    parts.extend([shock_a, shock_b])
    debris_points = [
        (1.10, 0.57, 0.22),
        (1.26, 0.58, 0.70),
        (1.55, 0.59, 0.90),
        (1.78, 0.57, 0.26),
        (1.92, 0.58, 0.62),
        (1.40, 0.57, 0.12),
    ]
    for i, loc in enumerate(debris_points):
        chunk = rounded_box(f"LAB5_ExplosionDebris_EditableChunk_{i:02d}", (0.08, 0.055, 0.06), loc, mats["debris"], 0.006, rot=(0.2 * i, 0.1 * i, 0.4 * i), role="explosion_debris_layer")
        parts.append(chunk)
    shield = torus("LAB5_ShieldSurface_FalloffRing", 0.38, 0.012, (0.82, 0.58, 0.44), mats["shield"], rot=(math.radians(90), 0, 0), role="shield_surface_layer")
    trigger = sphere("LAB5_ShieldImpactTrigger_Zone", 0.075, (0.58, 0.56, 0.45), mats["exception"], segments=18, ring_count=8, role="shield_trigger_zone")
    pulse = torus("LAB5_ShieldImpact_FalloffPulse", 0.15, 0.008, (0.59, 0.555, 0.45), mats["field"], rot=(math.radians(90), 0, 0), role="shield_trigger_falloff")
    parts.extend([shield, trigger, pulse])
    parts.extend(arrow("LAB5_ExplosionForceDirection", (1.02, 0.57, 0.42), (1.42, 0.57, 0.48), mats["shock"], radius=0.010, role="explosion_force_direction"))
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB5_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB5_StudioFloor_NotExported", (4.9, 3.3, 0.065), (0.24, -0.12, -0.045), mats["base"], 0.04, export=False, role="preview_floor")

    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]
    export_parts.extend(create_rigid_body_role_board(mats))
    export_parts.extend(create_force_particle_field(mats))
    domain_parts, domain_helpers = create_domain_effects(mats)
    export_parts.extend(domain_parts)
    helper_parts.extend(domain_helpers)
    export_parts.extend(create_explosion_shield_layers(mats))

    labels = [
        add_text("LAB5_Label_RigidRoles", "RIGID ROLES + CACHE", (-1.47, -1.17, 0.52), 0.060, mats["label"]),
        add_text("LAB5_Label_FieldsParticles", "FIELDS + MASKED PARTICLES", (-0.10, -0.70, 0.92), 0.058, mats["label"]),
        add_text("LAB5_Label_Domains", "DOMAINS HELP, NOT EXPORT", (1.42, -1.18, 0.94), 0.052, mats["label"]),
        add_text("LAB5_Label_ExplosionShield", "SEPARATE FX LAYERS", (1.18, 0.16, 1.03), 0.054, mats["label"]),
        add_text("LAB5_Label_NoExport", "FLOOR / DOMAINS / FIELDS: NOT GLB", (0.50, 1.06, 0.18), 0.046, mats["label"]),
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
        if obj.name == "LAB5_RigidBody_Active_FallingCube":
            obj.location.z += 0.04
            obj.keyframe_insert(data_path="location", frame=1)
            obj.location.z -= 0.18
            obj.rotation_euler.z += math.radians(16)
            obj.keyframe_insert(data_path="location", frame=48)
            obj.keyframe_insert(data_path="rotation_euler", frame=48)
            obj.location.z += 0.04
            obj.keyframe_insert(data_path="location", frame=96)
            linearize(obj)
        if obj.name == "LAB5_ShieldImpact_FalloffPulse":
            obj.scale = (0.8, 0.8, 0.8)
            obj.keyframe_insert(data_path="scale", frame=1)
            obj.scale = (1.25, 1.25, 1.25)
            obj.keyframe_insert(data_path="scale", frame=48)
            obj.scale = (0.8, 0.8, 0.8)
            obj.keyframe_insert(data_path="scale", frame=96)
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
    if triangles > 35000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 35000.")
    roles = sorted({str(obj.get("role")) for obj in objects if obj.get("role")})
    required_roles = {
        "active_rigid_body",
        "passive_rigid_body",
        "collision_floor",
        "force_field_influence_ring",
        "particle_density_mask",
        "smoke_density_layer",
        "fire_flame_layer",
        "contained_fluid_volume",
        "explosion_shockwave_layer",
        "shield_surface_layer",
    }
    missing_roles = sorted(required_roles - set(roles))
    if missing_roles:
        errors.append(f"Missing required roles: {missing_roles}")
    helper_names = [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False]
    if not any("Domain_Helper" in name for name in helper_names):
        errors.append("No non-export simulation domain helpers were found.")
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
    animated = [obj.name for obj in objects if obj.animation_data and obj.animation_data.action]
    if "LAB5_Root_TurntableAnimated" not in animated:
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
        "source_goal": "350-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Rigid-body roles are visibly separated into active/passive/collision objects.",
            "Simulation bake/cache is represented by frame ticks and ghosted positions.",
            "Force-field influence zones and particle direction are visible.",
            "Particle density, visibility gates and subtle dust are separated.",
            "Smoke, fire and fluid use domain/boundary thinking without exporting helper domains.",
            "Explosion and shield effects are editable layer stacks.",
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
