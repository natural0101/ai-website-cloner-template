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

ASSET = "blender_shorts_lifehack_lab_v13"
SCENE_NAME = "BlenderShortsLifehackLabV13"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-240", "name": "Scattering Needs Mask Seed Density Controls", "applied": "Scatter terrain has mask lanes, density slider, seed chip and overlap/collision dots."},
    {"id": "BH-241", "name": "Randomization Needs Stable IDs", "applied": "Stable ID color chips drive transform/color randomization and reset bounds."},
    {"id": "BH-242", "name": "Procedural Animation Needs Exposed Timing", "applied": "Timing board exposes speed, phase, offset and loop controls."},
    {"id": "BH-243", "name": "Curve Distribution Needs Tangent QA", "applied": "Curve rail has tangent arrows, spacing ticks and end-cap checks."},
    {"id": "BH-244", "name": "Simulation Nodes Need Cache Reset Notes", "applied": "Simulation board shows cache range, reset state and bounds cleanup."},
    {"id": "BH-245", "name": "Particle Trails Need Lifetime Cleanup", "applied": "Particle trail chain shows lifetime fade, size clamps and cleanup gate."},
    {"id": "BH-246", "name": "Realize Instances Is An Export Gate", "applied": "Instance cloud stays light until a measured realize/export gate."},
    {"id": "BH-247", "name": "Procedural Environments Need LOD Contracts", "applied": "City/landscape blocks show LOD tiers, seed and collection hierarchy."},
    {"id": "BH-248", "name": "Grass And Hair Need Distribution Masks", "applied": "Foliage strip has texture mask, viewport/render density split and collision marker."},
    {"id": "BH-249", "name": "Dissolves Need Progress And Final Cleanup", "applied": "Dissolve row shows progression mask, lifetime and final-state cleanup."},
    {"id": "BH-250", "name": "Data Transfer And Baking Need Projection QA", "applied": "Bake board exposes source/target projection distance, cage and tangent-space checks."},
    {"id": "BH-251", "name": "Noise Deformation Needs Strength Bounds", "applied": "Noise object has strength/frequency rails and silhouette limits."},
    {"id": "BH-252", "name": "Procedural Modules Need Measurement Rules", "applied": "Fence/spring modules expose length, spacing, caps and corner rules."},
    {"id": "BH-253", "name": "Heavy Effects Need File And Cache Warnings", "applied": "Heavy-effect warning card marks file-size, cache and fallback render risk."},
    {"id": "BH-254", "name": "Branching Systems Need Visual Pruning", "applied": "Branching links have neighbor/branch limits and line-count budget chips."},
    {"id": "BH-255", "name": "Procedural Text Needs Readability Gates", "applied": "Text/counter card checks conversion, frame mapping and delivery readability."},
    {"id": "BH-256", "name": "Geometry Nodes Need Statistics Overlays", "applied": "Statistics overlay records objects, triangles, instances and before/after budgets."},
    {"id": "BH-257", "name": "Looping Simulations Need First Last Proof", "applied": "Loop proof card compares first and last frame markers with no-pop seam."},
    {"id": "BH-258", "name": "Version Specific Nodes Need Compatibility Notes", "applied": "Compatibility card records Blender version, node availability and fallback state."},
    {"id": "BH-259", "name": "Addon Or Asset Node Tools Need License Boundaries", "applied": "Addon/tool card tracks license, dependency, cache path and replacement plan."},
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
            "Specular IOR Level": 0.40,
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
        "base": make_mat("Lab13_BaseGraphite", (0.018, 0.020, 0.030, 1.0), roughness=0.64),
        "panel": make_mat("Lab13_PanelInk", (0.045, 0.055, 0.086, 1.0), roughness=0.60),
        "panel_alt": make_mat("Lab13_PanelForest", (0.045, 0.076, 0.072, 1.0), roughness=0.62),
        "dark": make_mat("Lab13_DarkSocket", (0.012, 0.014, 0.020, 1.0), roughness=0.72),
        "white": make_mat("Lab13_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.52),
        "cyan": make_mat("Lab13_ControlCyan", (0.02, 0.77, 0.95, 1.0), roughness=0.34, emission=(0.0, 0.25, 0.55, 1.0), emission_strength=0.10),
        "green": make_mat("Lab13_MaskGreen", (0.12, 0.82, 0.42, 1.0), roughness=0.48),
        "gold": make_mat("Lab13_SeedGold", (1.0, 0.72, 0.16, 1.0), roughness=0.42, metallic=0.03),
        "magenta": make_mat("Lab13_IDMagenta", (1.0, 0.12, 0.56, 1.0), roughness=0.38, emission=(0.40, 0.0, 0.18, 1.0), emission_strength=0.07),
        "blue": make_mat("Lab13_NodeBlue", (0.10, 0.35, 0.92, 1.0), roughness=0.48),
        "orange": make_mat("Lab13_WarningOrange", (0.96, 0.42, 0.11, 1.0), roughness=0.44),
        "red": make_mat("Lab13_DangerRed", (0.96, 0.08, 0.06, 1.0), roughness=0.35, emission=(0.45, 0.02, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab13_SimViolet", (0.46, 0.24, 0.86, 1.0), roughness=0.46),
        "ghost": make_mat("Lab13_GhostTrail", (0.54, 0.72, 1.0, 1.0), roughness=0.54, alpha=0.34),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB13_WeightedNormals", type="WEIGHTED_NORMAL")


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
        mod = obj.modifiers.new(name="LAB13_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB13_WeightedNormals", type="WEIGHTED_NORMAL")
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
    scene.world = scene.world or bpy.data.worlds.new("LAB13_World")
    scene.world.color = (0.016, 0.018, 0.026)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.5, -5.1, 4.8))
    key = bpy.context.object
    key.name = "LAB13_KeyArea_Warm"
    key.data.energy = 680
    key.data.size = 5.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.1, 2.6, 3.2))
    fill = bpy.context.object
    fill.name = "LAB13_FillArea_Cool"
    fill.data.energy = 150
    fill.data.size = 5.4
    fill.data.color = (0.55, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.4, 3.4, 2.6))
    rim = bpy.context.object
    rim.name = "LAB13_RimPoint_Cyan"
    rim.data.energy = 265
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.15, -5.25, 3.22), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB13_Camera_Hero3Q"
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


def scatter_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB13_ScatterRandomBoard", (-1.12, -0.84, 0.66), mats["panel_alt"], "scatter_lab_panel")]
    terrain = rounded_box("LAB13_ScatterSurface_MaskedTerrain", (0.82, 0.048, 0.34), (-1.64, -0.89, 0.94), mats["dark"], 0.010, role="scattering_mask_seed_density", bh="BH-240")
    terrain["scatter_controls"] = "mask, density, seed, collision"
    parts.append(terrain)
    for i in range(18):
        x = -1.98 + (i % 6) * 0.12
        z = 0.82 + (i // 6) * 0.10 + (0.02 if i % 2 else 0.0)
        dot = sphere(f"LAB13_ScatterInstance_Seeded_{i}", 0.026, (x, -0.925, z), [mats["green"], mats["cyan"], mats["gold"]][i % 3], segments=10, ring_count=5, role="scattering_mask_seed_density", bh="BH-240")
        dot["seed"] = 42
        parts.append(dot)
    density = rounded_box("LAB13_DensitySlider_ViewportRenderSplit", (0.52, 0.045, 0.045), (-1.28, -0.91, 0.76), mats["blue"], 0.004, role="scattering_mask_seed_density", bh="BH-240")
    seed = rounded_box("LAB13_SeedChip_Deterministic", (0.16, 0.050, 0.12), (-0.92, -0.90, 0.86), mats["gold"], 0.006, role="randomization_stable_ids", bh="BH-241")
    parts.extend([density, seed])
    id_mats = [mats["magenta"], mats["blue"], mats["cyan"], mats["green"], mats["gold"]]
    for i, mat in enumerate(id_mats):
        chip = rounded_box(f"LAB13_StableIDColorChip_{i}", (0.15, 0.050, 0.11), (-1.88 + i * 0.20, -0.90, 0.55), mat, 0.006, role="randomization_stable_ids", bh="BH-241")
        chip["stable_id"] = i
        parts.append(chip)
    for i in range(5):
        rail = rounded_box(f"LAB13_RandomAxisClamp_{i}", (0.12, 0.044, 0.06 + 0.018 * i), (-0.98 + i * 0.13, -0.90, 0.48), mats["violet"], 0.004, role="randomization_stable_ids", bh="BH-241")
        parts.append(rail)
    mask = rounded_box("LAB13_GrassHairTextureMask_AlignedUV", (0.58, 0.045, 0.18), (-1.62, -0.91, 0.30), mats["green"], 0.008, role="grass_hair_distribution_masks", bh="BH-248")
    mask["mask_rule"] = "texture mask, UV alignment, collision clipping"
    parts.append(mask)
    for i in range(8):
        blade = cone_between(f"LAB13_FoliageBlade_ClippingChecked_{i}", (-1.88 + i * 0.07, -0.925, 0.23), (-1.86 + i * 0.07, -0.925, 0.40 + (i % 3) * 0.03), 0.010, 0.0, mats["green"], role="grass_hair_distribution_masks", bh="BH-248")
        parts.append(blade)
    parts.append(rounded_box("LAB13_AddonLicenseBoundaryCard", (0.40, 0.048, 0.16), (-0.86, -0.90, 0.28), mats["orange"], 0.008, role="addon_license_boundaries", bh="BH-259"))
    return parts


def animation_sim_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB13_AnimationSimulationBoard", (1.12, -0.82, 0.66), mats["panel"], "simulation_lab_panel")]
    rail = rounded_box("LAB13_ProceduralTimingControlRail", (0.88, 0.045, 0.055), (0.62, -0.90, 1.04), mats["dark"], 0.004, role="procedural_timing_controls", bh="BH-242")
    parts.append(rail)
    control_mats = [mats["cyan"], mats["green"], mats["gold"], mats["magenta"]]
    for i, name in enumerate(("speed", "phase", "offset", "loop")):
        chip = rounded_box(f"LAB13_TimingControl_{name}", (0.16, 0.050, 0.12), (0.32 + i * 0.20, -0.91, 0.92), control_mats[i], 0.006, role="procedural_timing_controls", bh="BH-242")
        chip["timing_control"] = name
        parts.append(chip)
    needle = sphere("LAB13_TimingPhaseNeedle_Animated", 0.035, (0.34, -0.925, 1.04), mats["magenta"], role="procedural_timing_controls", bh="BH-242")
    parts.append(needle)
    needle.location.x = 0.34
    needle.keyframe_insert(data_path="location", frame=1)
    needle.location.x = 1.04
    needle.keyframe_insert(data_path="location", frame=72)
    needle.location.x = 0.34
    needle.keyframe_insert(data_path="location", frame=96)
    linearize(needle)

    curve_points = [(-0.02, -0.90, 0.72), (0.24, -0.90, 0.86), (0.54, -0.90, 0.74), (0.86, -0.90, 0.84)]
    for i in range(len(curve_points) - 1):
        parts.append(cyl_between(f"LAB13_CurveDistributionSegment_{i}", curve_points[i], curve_points[i + 1], 0.010, mats["cyan"], role="curve_distribution_tangent_qa", bh="BH-243"))
        parts.extend(arrow(f"LAB13_TangentArrow_{i}", curve_points[i], curve_points[i + 1], mats["white"], radius=0.004, role="curve_distribution_tangent_qa", bh="BH-243"))
    for i, p in enumerate(curve_points):
        parts.append(rounded_box(f"LAB13_CurveSpacingTick_{i}", (0.055, 0.050, 0.13), (p[0], -0.925, p[2] - 0.16), mats["gold"], 0.004, role="curve_distribution_tangent_qa", bh="BH-243"))

    cache = rounded_box("LAB13_SimulationCacheResetRange", (0.56, 0.050, 0.16), (1.48, -0.90, 1.00), mats["violet"], 0.008, role="simulation_cache_reset", bh="BH-244")
    cache["cache_rule"] = "frame range, reset state, timestep, bounds cleanup"
    parts.append(cache)
    reset = rounded_box("LAB13_SimulationResetStateButton", (0.16, 0.055, 0.14), (1.82, -0.91, 0.98), mats["red"], 0.008, role="simulation_cache_reset", bh="BH-244")
    parts.append(reset)
    for i in range(7):
        dot = sphere(f"LAB13_ParticleTrailLifetimeDot_{i}", 0.024 + i * 0.002, (1.18 + i * 0.10, -0.925, 0.66 + math.sin(i) * 0.06), [mats["ghost"], mats["cyan"], mats["blue"]][i % 3], segments=10, ring_count=5, role="particle_lifetime_cleanup", bh="BH-245")
        dot["lifetime_frame"] = i * 8
        parts.append(dot)
        if i:
            parts.append(cyl_between(f"LAB13_ParticleTrailConnector_{i}", (1.08 + i * 0.10, -0.925, 0.66 + math.sin(i - 1) * 0.06), (1.18 + i * 0.10, -0.925, 0.66 + math.sin(i) * 0.06), 0.004, mats["ghost"], role="particle_lifetime_cleanup", bh="BH-245"))
    cleanup = rounded_box("LAB13_ParticleFinalCleanupGate", (0.24, 0.050, 0.12), (1.86, -0.90, 0.58), mats["green"], 0.006, role="particle_lifetime_cleanup", bh="BH-245")
    parts.append(cleanup)

    loop_a = rounded_box("LAB13_LoopProof_FirstFrame", (0.20, 0.050, 0.14), (0.40, -0.91, 0.35), mats["cyan"], 0.006, role="loop_first_last_proof", bh="BH-257")
    loop_b = rounded_box("LAB13_LoopProof_LastFrame", (0.20, 0.050, 0.14), (0.70, -0.91, 0.35), mats["cyan"], 0.006, role="loop_first_last_proof", bh="BH-257")
    seam = rounded_box("LAB13_NoPopSeamComparator", (0.18, 0.052, 0.06), (1.00, -0.91, 0.35), mats["green"], 0.004, role="loop_first_last_proof", bh="BH-257")
    parts.extend([loop_a, loop_b, seam])
    seam.scale = (1.0, 1.0, 1.0)
    seam.keyframe_insert(data_path="scale", frame=1)
    seam.scale = (1.25, 1.25, 1.25)
    seam.keyframe_insert(data_path="scale", frame=48)
    seam.scale = (1.0, 1.0, 1.0)
    seam.keyframe_insert(data_path="scale", frame=96)
    linearize(seam)
    return parts


def export_opt_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB13_InstanceExportOptimizationBoard", (-1.12, 0.35, 0.66), mats["panel"], "instance_export_lab_panel")]
    for i in range(12):
        x = -1.92 + (i % 4) * 0.16
        z = 1.02 - (i // 4) * 0.13
        inst = rounded_box(f"LAB13_LightInstanceProxy_{i}", (0.09, 0.045, 0.09), (x, 0.30, z), [mats["blue"], mats["cyan"], mats["green"], mats["gold"]][i % 4], 0.006, role="realize_instance_export_gate", bh="BH-246")
        inst["instance_state"] = "proxy until export gate"
        parts.append(inst)
    gate = rounded_box("LAB13_RealizeInstancesExportGate_Measured", (0.42, 0.055, 0.28), (-1.05, 0.29, 0.90), mats["orange"], 0.010, role="realize_instance_export_gate", bh="BH-246")
    gate["gate_rule"] = "realize only at edit/export gate"
    parts.append(gate)
    parts.extend(arrow("LAB13_InstanceToRealizeFlow", (-1.36, 0.28, 0.90), (-1.14, 0.28, 0.90), mats["white"], radius=0.005, role="realize_instance_export_gate", bh="BH-246"))

    stats = rounded_box("LAB13_GNStatisticsOverlay_ObjectTriInstanceBudget", (0.64, 0.050, 0.32), (-0.54, 0.29, 0.94), mats["dark"], 0.010, role="gn_statistics_overlay", bh="BH-256")
    stats["statistics"] = "objects, triangles, instances, before/after"
    parts.append(stats)
    bar_mats = [mats["green"], mats["cyan"], mats["gold"], mats["magenta"]]
    for i, mat in enumerate(bar_mats):
        bar = rounded_box(f"LAB13_StatsBudgetBar_{i}", (0.09 + i * 0.04, 0.055, 0.055), (-0.74 + i * 0.13, 0.25, 0.82 + i * 0.06), mat, 0.004, role="gn_statistics_overlay", bh="BH-256")
        parts.append(bar)

    city_mats = [mats["blue"], mats["cyan"], mats["green"], mats["gold"], mats["orange"]]
    for i in range(5):
        block = rounded_box(f"LAB13_ProceduralEnvironmentLOD_Block_{i}", (0.18, 0.050, 0.14 + i * 0.05), (-1.84 + i * 0.22, 0.30, 0.45), city_mats[i], 0.006, role="environment_lod_contract", bh="BH-247")
        block["lod_contract"] = "block scale, seed, collection hierarchy"
        parts.append(block)
    bake_src = rounded_box("LAB13_DataTransferSourceHighPoly", (0.26, 0.052, 0.22), (-0.86, 0.29, 0.48), mats["red"], 0.010, role="data_transfer_bake_projection", bh="BH-250")
    bake_low = rounded_box("LAB13_DataTransferTargetLowPoly", (0.24, 0.052, 0.17), (-0.52, 0.29, 0.48), mats["green"], 0.008, role="data_transfer_bake_projection", bh="BH-250")
    cage = rounded_box("LAB13_BakeProjectionCageDistance", (0.42, 0.056, 0.05), (-0.69, 0.255, 0.66), mats["gold"], 0.004, role="data_transfer_bake_projection", bh="BH-250")
    parts.extend([bake_src, bake_low, cage])

    heavy = rounded_box("LAB13_HeavyEffectCacheWarning_FileSize", (0.36, 0.052, 0.22), (-0.22, 0.29, 0.50), mats["red"], 0.010, role="heavy_effect_cache_warning", bh="BH-253")
    heavy["risk_notes"] = "file size, cache cleanup, fallback render"
    parts.append(heavy)
    compat = rounded_box("LAB13_VersionCompatibilityNodeCard", (0.34, 0.052, 0.16), (-0.22, 0.29, 0.78), mats["violet"], 0.008, role="version_compatibility_notes", bh="BH-258")
    compat["version_note"] = "Blender version, node availability, fallback"
    parts.append(compat)
    return parts


def module_branch_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = [panel("LAB13_ModulesBranchesTextBoard", (1.12, 0.39, 0.66), mats["panel_alt"], "module_branch_lab_panel")]
    for i in range(6):
        x = 0.30 + i * 0.18
        post = rounded_box(f"LAB13_ProceduralFencePost_{i}", (0.045, 0.050, 0.30), (x, 0.34, 1.00), mats["gold"], 0.004, role="procedural_module_measurement", bh="BH-252")
        parts.append(post)
        if i:
            parts.append(cyl_between(f"LAB13_ProceduralFenceRail_{i}", (x - 0.18, 0.32, 1.08), (x, 0.32, 1.08), 0.006, mats["cyan"], role="procedural_module_measurement", bh="BH-252"))
    spring_center = (1.58, 0.33, 0.98)
    prev = None
    for i in range(10):
        x = spring_center[0] - 0.25 + i * 0.055
        z = spring_center[2] + math.sin(i * math.pi * 0.75) * 0.08
        p = (x, spring_center[1], z)
        parts.append(sphere(f"LAB13_ProceduralSpringTurn_{i}", 0.022, p, mats["orange"], segments=10, ring_count=5, role="procedural_module_measurement", bh="BH-252"))
        if prev:
            parts.append(cyl_between(f"LAB13_ProceduralSpringSegment_{i}", prev, p, 0.006, mats["orange"], role="procedural_module_measurement", bh="BH-252"))
        prev = p

    source = (0.54, 0.33, 0.66)
    branch_ends = [(0.26, 0.33, 0.46), (0.48, 0.33, 0.40), (0.74, 0.33, 0.44), (0.92, 0.33, 0.56), (0.80, 0.33, 0.74)]
    parts.append(sphere("LAB13_BranchRoot_NeighborLimited", 0.035, source, mats["magenta"], role="branch_pruning_controls", bh="BH-254"))
    for i, end in enumerate(branch_ends):
        parts.append(cyl_between(f"LAB13_BranchLine_PruneBudget_{i}", source, end, 0.006, [mats["cyan"], mats["green"], mats["gold"], mats["orange"], mats["red"]][i], role="branch_pruning_controls", bh="BH-254"))
        parts.append(sphere(f"LAB13_BranchEndpoint_{i}", 0.022, end, mats["white"], segments=10, ring_count=5, role="branch_pruning_controls", bh="BH-254"))
    parts.append(rounded_box("LAB13_BranchCountLimitChip", (0.20, 0.050, 0.10), (0.28, 0.32, 0.78), mats["red"], 0.006, role="branch_pruning_controls", bh="BH-254"))

    noise = rounded_box("LAB13_NoiseDeformStrengthBounds_Object", (0.32, 0.052, 0.22), (1.25, 0.33, 0.54), mats["violet"], 0.020, role="noise_strength_bounds", bh="BH-251")
    noise["noise_controls"] = "strength, frequency, axis, silhouette"
    parts.append(noise)
    for i in range(4):
        parts.append(rounded_box(f"LAB13_NoiseStrengthBoundTick_{i}", (0.035, 0.054, 0.06 + i * 0.035), (1.02 + i * 0.07, 0.30, 0.34), mats["cyan"], 0.003, role="noise_strength_bounds", bh="BH-251"))

    dissolve_steps = [mats["blue"], mats["cyan"], mats["green"], mats["gold"], mats["dark"]]
    for i, mat in enumerate(dissolve_steps):
        step = rounded_box(f"LAB13_DissolveProgressCleanupStep_{i}", (0.13, 0.052, 0.12), (1.58 + i * 0.11, 0.32, 0.58), mat, 0.006, role="dissolve_final_cleanup", bh="BH-249")
        step["dissolve_rule"] = "progress mask, lifetime, final cleanup"
        parts.append(step)

    text_card = rounded_box("LAB13_ProceduralTextReadabilityGate", (0.42, 0.052, 0.18), (1.62, 0.32, 0.34), mats["white"], 0.008, role="procedural_text_readability", bh="BH-255")
    text_card["text_rule"] = "conversion, frame mapping, delivery readability"
    parts.append(text_card)
    return parts


def rear_summary_marks(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    specs = [
        ("Scatter", -1.12, -0.765, 0.66, ["scattering_mask_seed_density", "randomization_stable_ids", "grass_hair_distribution_masks", "addon_license_boundaries"], "BH-240,BH-241,BH-248,BH-259"),
        ("Animation", 1.12, -0.745, 0.66, ["procedural_timing_controls", "simulation_cache_reset", "particle_lifetime_cleanup", "loop_first_last_proof"], "BH-242,BH-244,BH-245,BH-257"),
        ("Export", -1.12, 0.425, 0.66, ["realize_instance_export_gate", "gn_statistics_overlay", "data_transfer_bake_projection", "version_compatibility_notes"], "BH-246,BH-250,BH-256,BH-258"),
        ("Modules", 1.12, 0.465, 0.66, ["procedural_module_measurement", "branch_pruning_controls", "noise_strength_bounds", "procedural_text_readability"], "BH-251,BH-252,BH-254,BH-255"),
    ]
    swatches = [mats["cyan"], mats["green"], mats["gold"], mats["magenta"]]
    for board, x, y, z, roles, bh in specs:
        rail = rounded_box(f"LAB13_RearSummaryRail_{board}", (1.08, 0.040, 0.052), (x, y, z + 0.18), mats["dark"], 0.004, role=roles[0], bh=bh)
        rail["rear_summary"] = "backside turntable readability"
        parts.append(rail)
        for i, role in enumerate(roles):
            chip = rounded_box(f"LAB13_RearSummaryChip_{board}_{i}", (0.18, 0.046, 0.11), (x - 0.39 + i * 0.26, y + 0.01, z), swatches[i], 0.006, role=role, bh=bh)
            parts.append(chip)
        parts.extend(arrow(f"LAB13_RearSummaryArrow_{board}", (x - 0.53, y + 0.02, z - 0.18), (x + 0.53, y + 0.02, z - 0.18), mats["white"], radius=0.004, role=roles[-1], bh=bh))
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB13_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-240..BH-259")

    floor = rounded_box("LAB13_StudioFloor_NotExported", (5.35, 3.52, 0.065), (0.0, -0.08, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]

    export_parts.extend(scatter_board(mats))
    export_parts.extend(animation_sim_board(mats))
    export_parts.extend(export_opt_board(mats))
    export_parts.extend(module_branch_board(mats))
    export_parts.extend(rear_summary_marks(mats))

    labels = [
        add_text("LAB13_Label_Scatter", "SCATTER / RANDOM / MASKS", (-1.12, -1.26, 1.24), 0.046, mats["white"]),
        add_text("LAB13_Label_Simulation", "PROCEDURAL ANIMATION / SIM", (1.12, -1.26, 1.24), 0.044, mats["white"]),
        add_text("LAB13_Label_Export", "INSTANCES / STATS / BAKING", (-1.12, -0.03, 1.18), 0.046, mats["white"]),
        add_text("LAB13_Label_Modules", "MODULES / BRANCHES / TEXT", (1.12, 0.01, 1.18), 0.046, mats["white"]),
    ]
    helper_parts.extend(labels)

    for obj in export_parts + helper_parts:
        parent_keep_world(obj, root)

    for frame, rot in ((1, 0.0), (24, 0.0), (72, math.tau), (96, math.tau)):
        root.rotation_euler = (0, 0, rot)
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    linearize(root)

    for obj in export_parts:
        if obj.name == "LAB13_SeedChip_Deterministic":
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=1)
            obj.scale = (1.25, 1.25, 1.25)
            obj.keyframe_insert(data_path="scale", frame=48)
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=96)
            linearize(obj)
        if obj.name == "LAB13_RealizeInstancesExportGate_Measured":
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
        "scattering_mask_seed_density",
        "randomization_stable_ids",
        "procedural_timing_controls",
        "curve_distribution_tangent_qa",
        "simulation_cache_reset",
        "particle_lifetime_cleanup",
        "realize_instance_export_gate",
        "environment_lod_contract",
        "grass_hair_distribution_masks",
        "dissolve_final_cleanup",
        "data_transfer_bake_projection",
        "noise_strength_bounds",
        "procedural_module_measurement",
        "heavy_effect_cache_warning",
        "branch_pruning_controls",
        "procedural_text_readability",
        "gn_statistics_overlay",
        "loop_first_last_proof",
        "version_compatibility_notes",
        "addon_license_boundaries",
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
    if "LAB13_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    expected_animated = {
        "LAB13_Root_TurntableAnimated",
        "LAB13_TimingPhaseNeedle_Animated",
        "LAB13_NoPopSeamComparator",
        "LAB13_SeedChip_Deterministic",
        "LAB13_RealizeInstancesExportGate_Measured",
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
        "source_goal": "750-source Blender Shorts checkpoint test asset.",
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
            "Scattering, stable IDs, grass/hair masks and addon license boundaries are visible.",
            "Procedural timing, curve tangent QA, simulation cache, particle cleanup and loop proof are visible.",
            "Instance-realize gate, statistics overlay, environment LOD, data bake QA, heavy-effect warnings and version notes are visible.",
            "Noise bounds, procedural modules, branching pruning, dissolve cleanup and text readability gates are visible.",
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
