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

ASSET = "blender_shorts_lifehack_lab_v18"
SCENE_NAME = "BlenderShortsLifehackLabV18"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-340", "name": "Cloth Pinning Needs Vertex-Group Proof", "role": "cloth_pin_vertex_group_proof", "applied": "Cloth strip exposes pin group weights, locked vertices and cache-frame proof."},
    {"id": "BH-341", "name": "Cloth Collision Needs Pose Sweeps", "role": "cloth_collision_pose_sweeps", "applied": "Collision lane shows front, contact and side sweep markers before bake approval."},
    {"id": "BH-342", "name": "Soft Furnishing Sims Need Final Freeze Policy", "role": "soft_furnishing_final_freeze", "applied": "Pillow/blanket block records sim source, accepted frame and frozen output."},
    {"id": "BH-343", "name": "Hair Needs Strand Budget Discipline", "role": "hair_strand_budget_discipline", "applied": "Hair comb has density bars, viewport/render multipliers and triangle budget notes."},
    {"id": "BH-344", "name": "Hair Grooming Needs Fallbacks", "role": "hair_grooming_fallbacks", "applied": "Groom cards separate addon path, manual comb fallback and baked curve fallback."},
    {"id": "BH-345", "name": "Hair Dynamics Need Versioned Cache Proof", "role": "hair_dynamics_versioned_cache", "applied": "Wind control and cache rail show branch/version, seed and baked frame evidence."},
    {"id": "BH-346", "name": "Smoke Sims Need Memory Budgets", "role": "smoke_memory_budget", "applied": "Smoke domain gauge records voxel size, adaptive domain and memory ceiling."},
    {"id": "BH-347", "name": "Fluid Sims Need Domain/Flow Naming", "role": "fluid_domain_flow_naming", "applied": "Fluid mini-scene labels domain, inflow, effector, cache and mesh output."},
    {"id": "BH-348", "name": "Particles Need Seed And Density Gates", "role": "particle_seed_density_gates", "applied": "Particle scatter board shows seed slider, density rail and realization gate."},
    {"id": "BH-349", "name": "Render Passes Need Pass Accounting", "role": "render_pass_accounting_final", "applied": "Pass stack counts Beauty, Diffuse, Mist, Vector, Position and Shadow catcher outputs."},
    {"id": "BH-350", "name": "View Layers Need Collection Contracts", "role": "view_layer_collection_contracts", "applied": "Layer matrix maps collection ownership to foreground, FX and matte passes."},
    {"id": "BH-351", "name": "Depth/Position Passes Need Space Notes", "role": "depth_position_space_notes", "applied": "Depth ruler and position axes mark camera/world space before composite use."},
    {"id": "BH-352", "name": "Compositor Blur Needs Vector Proof", "role": "compositor_blur_vector_proof", "applied": "Vector blur arrow proves motion direction, shutter budget and preview toggle."},
    {"id": "BH-353", "name": "Shadow Catchers Need Destination Proof", "role": "shadow_catcher_destination_proof", "applied": "Shadow plate checks alpha destination, contact softness and exported floor exclusion."},
    {"id": "BH-354", "name": "Cinematic Composites Need Before/After Reviews", "role": "cinematic_composite_before_after", "applied": "Before/after split shows grade, glow, denoise and regression snapshot."},
    {"id": "BH-355", "name": "GLTF Export Needs Transform And Material Checks", "role": "gltf_transform_material_checks", "applied": "Export lane verifies applied transforms, simple PBR materials, axes and scale."},
    {"id": "BH-356", "name": "Vertex Animation Export Needs Viewer Tests", "role": "vertex_animation_viewer_tests", "applied": "Viewer scrubber checks vertex animation frames after GLB export."},
    {"id": "BH-357", "name": "Game Collision Exports Need Naming Discipline", "role": "game_collision_export_naming", "applied": "Collision proxies use UCX-style names and non-render gameplay material."},
    {"id": "BH-358", "name": "Texture Bake/Export Needs Relink QA", "role": "texture_export_relink_qa_final", "applied": "Texture cards track bake format, color space, packing and material relink."},
    {"id": "BH-359", "name": "Destructive Cleanup Needs Deform Proof", "role": "destructive_cleanup_deform_proof", "applied": "Cleanup lane stores pre/post deform checks before applying irreversible modifiers."},
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
            "Specular IOR Level": 0.36,
            "Coat Weight": 0.025,
            "Coat Roughness": 0.28,
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
        "base": make_mat("Lab18_BaseGraphite", (0.014, 0.016, 0.023, 1.0), roughness=0.68),
        "panel": make_mat("Lab18_PanelDeepBlue", (0.030, 0.042, 0.071, 1.0), roughness=0.62),
        "panel_green": make_mat("Lab18_PanelDeepGreen", (0.027, 0.063, 0.052, 1.0), roughness=0.62),
        "panel_warm": make_mat("Lab18_PanelMaroon", (0.082, 0.041, 0.053, 1.0), roughness=0.63),
        "panel_purple": make_mat("Lab18_PanelPurple", (0.058, 0.044, 0.088, 1.0), roughness=0.64),
        "white": make_mat("Lab18_LabelWhite", (0.93, 0.97, 1.0, 1.0), roughness=0.54),
        "cyan": make_mat("Lab18_Cyan", (0.03, 0.77, 0.96, 1.0), roughness=0.36, emission=(0.0, 0.22, 0.45, 1.0), emission_strength=0.10),
        "green": make_mat("Lab18_Green", (0.12, 0.76, 0.38, 1.0), roughness=0.48),
        "gold": make_mat("Lab18_Gold", (1.0, 0.68, 0.18, 1.0), roughness=0.42, metallic=0.04),
        "orange": make_mat("Lab18_Orange", (0.96, 0.42, 0.10, 1.0), roughness=0.44),
        "red": make_mat("Lab18_WarningRed", (0.95, 0.08, 0.06, 1.0), roughness=0.36, emission=(0.34, 0.015, 0.01, 1.0), emission_strength=0.08),
        "violet": make_mat("Lab18_Violet", (0.50, 0.25, 0.86, 1.0), roughness=0.46),
        "blue": make_mat("Lab18_Blue", (0.10, 0.38, 0.92, 1.0), roughness=0.48),
        "magenta": make_mat("Lab18_Magenta", (0.96, 0.14, 0.58, 1.0), roughness=0.38, emission=(0.32, 0.0, 0.16, 1.0), emission_strength=0.08),
        "cloth": make_mat("Lab18_ClothWarmWhite", (0.88, 0.76, 0.62, 1.0), roughness=0.70),
        "hair": make_mat("Lab18_HairCopper", (0.76, 0.36, 0.16, 1.0), roughness=0.58),
        "smoke": make_mat("Lab18_SmokeGhost", (0.56, 0.66, 0.76, 1.0), roughness=0.64, alpha=0.32),
        "shadow": make_mat("Lab18_ShadowCatcherAlpha", (0.02, 0.02, 0.025, 1.0), roughness=0.76, alpha=0.38),
        "ghost": make_mat("Lab18_GhostAlpha", (0.58, 0.78, 1.0, 1.0), roughness=0.54, alpha=0.26),
        "glow": make_mat("Lab18_GlowMint", (0.02, 0.95, 0.78, 1.0), roughness=0.30, emission=(0.0, 0.82, 0.62, 1.0), emission_strength=0.42),
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
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(major_segments=38, minor_segments=8, major_radius=major, minor_radius=minor, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, role, export, bh)


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
        cyl_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, mat, vertices=12, role=role, bh=bh),
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
    scene.world = scene.world or bpy.data.worlds.new("LAB18_World")
    scene.world.color = (0.013, 0.015, 0.023)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.8, -5.4, 4.9))
    key = bpy.context.object
    key.name = "LAB18_KeyArea_Warm"
    key.data.energy = 790
    key.data.size = 5.3
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.3, 2.9, 3.6))
    fill = bpy.context.object
    fill.name = "LAB18_FillArea_Cool"
    fill.data.energy = 145
    fill.data.size = 5.9
    fill.data.color = (0.58, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.0, 3.8, 2.9))
    rim = bpy.context.object
    rim.name = "LAB18_RimPoint_Mint"
    rim.data.energy = 330
    rim.data.color = (0.36, 0.92, 0.82)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    target = Vector((0.0, 0.0, 0.80))
    location = Vector((1.2, -6.2, 1.65))
    direction = target - location
    bpy.ops.object.camera_add(location=location, rotation=direction.to_track_quat("-Z", "Y").to_euler())
    cam = bpy.context.object
    cam.name = "LAB18_Camera_Hero3Q"
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 5.85
    cam.data.dof.use_dof = False
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def make_root() -> bpy.types.Object:
    root = bpy.data.objects.new("LAB18_Root_TurntableAnimated", None)
    bpy.context.collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.65
    tag(root, "final_checkpoint_turntable_proof", export=True, bh="BH-359")
    for frame, angle in ((1, -4), (48, 12), (96, 356)):
        bpy.context.scene.frame_set(frame)
        root.rotation_euler = (0, 0, math.radians(angle))
        root.keyframe_insert(data_path="rotation_euler", frame=frame)
    return root


def add_panel(mats: dict[str, bpy.types.Material], name: str, title: str, loc: tuple[float, float, float], size: tuple[float, float, float], mat_key: str) -> bpy.types.Object:
    panel = rounded_box(name, size, loc, mats[mat_key], 0.035, role="lab_panel", export=True)
    add_text(f"{name}_Title", title, (loc[0], loc[1] - 0.065, loc[2] + size[2] * 0.42), 0.055, mats["white"])
    return panel


def polyline(name: str, points: list[tuple[float, float, float]], mat: bpy.types.Material, radius: float, role: str, bh: str) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for index in range(len(points) - 1):
        parts.append(cyl_between(f"{name}_{index:02d}", points[index], points[index + 1], radius, mat, vertices=10, role=role, bh=bh))
    for index, point in enumerate(points):
        parts.append(sphere(f"{name}_Point_{index:02d}", point, radius * 2.0, mat, segments=12, role=role, bh=bh))
    return parts


def build_cloth_hair_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB18_ClothHairPanel_Backplate", "CLOTH / HAIR CACHE PROOF", (-1.95, 0.06, 1.05), (1.46, 0.08, 1.08), "panel")
    parts.extend(polyline(
        "LAB18_ClothPin_WaveStrip",
        [(-2.50, -0.070, 1.37), (-2.28, -0.070, 1.45), (-2.06, -0.070, 1.34), (-1.84, -0.070, 1.43), (-1.63, -0.070, 1.36)],
        mats["cloth"],
        0.012,
        "cloth_pin_vertex_group_proof",
        "BH-340",
    ))
    for index, x in enumerate([-2.47, -2.25, -2.04]):
        parts.append(sphere(f"LAB18_ClothPin_VertexWeight_{index+1}", (x, -0.088, 1.26), 0.032, mats[["green", "gold", "red"][index]], segments=14, role="cloth_pin_vertex_group_proof", bh="BH-340"))
    collider = sphere("LAB18_ClothCollision_PoseSweepSphere", (-1.55, -0.084, 1.32), 0.090, mats["ghost"], segments=16, role="cloth_collision_pose_sweeps", bh="BH-341")
    parts.append(collider)
    for index, x in enumerate([-1.78, -1.62, -1.46]):
        parts.append(torus(f"LAB18_ClothCollision_SweepFrame_{index+1}", (x, -0.086, 1.32), 0.070 + index * 0.018, 0.0045, mats[["cyan", "orange", "white"][index]], role="cloth_collision_pose_sweeps", bh="BH-341"))
    pillow = rounded_box("LAB18_SoftFurnishing_FrozenPillowFrame", (0.38, 0.035, 0.150), (-2.34, -0.080, 1.03), mats["cloth"], 0.045, role="soft_furnishing_final_freeze", bh="BH-342")
    parts.append(pillow)
    parts.append(rounded_box("LAB18_SoftFurnishing_AcceptedFrameStamp", (0.28, 0.026, 0.052), (-1.92, -0.083, 1.04), mats["green"], 0.010, role="soft_furnishing_final_freeze", bh="BH-342"))
    for index, height in enumerate([0.20, 0.28, 0.36, 0.44]):
        x = -2.50 + index * 0.16
        parts.append(cyl_between(f"LAB18_HairBudget_Strand_{index+1}", (x, -0.089, 0.56), (x + 0.07, -0.089, 0.56 + height), 0.006, mats["hair"], vertices=8, role="hair_strand_budget_discipline", bh="BH-343"))
    for index, (label, mat_key) in enumerate([("addon", "violet"), ("manual", "cyan"), ("curves", "green")]):
        parts.append(rounded_box(f"LAB18_HairGroomFallback_{label}", (0.20, 0.030, 0.070), (-1.82 + index * 0.23, -0.080, 0.75), mats[mat_key], 0.010, role="hair_grooming_fallbacks", bh="BH-344"))
    wind = sphere("LAB18_HairWind_Control_Animated", (-1.72, -0.084, 0.49), 0.040, mats["magenta"], segments=16, role="hair_dynamics_versioned_cache", bh="BH-345")
    parts.append(wind)
    parts.append(cyl_between("LAB18_HairCache_VersionRail", (-1.98, -0.094, 0.49), (-1.35, -0.094, 0.49), 0.006, mats["magenta"], vertices=8, role="hair_dynamics_versioned_cache", bh="BH-345"))
    for frame, x in ((1, -1.94), (48, -1.40), (96, -1.94)):
        bpy.context.scene.frame_set(frame)
        wind.location = (x, -0.084, 0.49)
        wind.keyframe_insert(data_path="location", frame=frame)
    cache = sphere("LAB18_ClothCache_FrameSlider_Animated", (-2.39, -0.084, 0.49), 0.038, mats["green"], segments=16, role="soft_furnishing_final_freeze", bh="BH-342")
    parts.append(cache)
    parts.append(cyl_between("LAB18_ClothCache_AcceptedFrameRail", (-2.58, -0.094, 0.49), (-2.08, -0.094, 0.49), 0.006, mats["green"], vertices=8, role="soft_furnishing_final_freeze", bh="BH-342"))
    for frame, x in ((1, -2.54), (48, -2.12), (96, -2.54)):
        bpy.context.scene.frame_set(frame)
        cache.location = (x, -0.084, 0.49)
        cache.keyframe_insert(data_path="location", frame=frame)
    add_text("LAB18_ClothHairChip_Cloth", "pin group + collision sweep + frozen frame", (-2.04, -0.100, 1.58), 0.033, mats["cyan"])
    add_text("LAB18_ClothHairChip_Hair", "strand budget + fallback + versioned cache", (-2.02, -0.100, 0.30), 0.033, mats["gold"])
    return parts


def build_simulation_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB18_SimPanel_Backplate", "VOLUME / FLUID / PARTICLES", (0.00, 0.07, 1.05), (1.50, 0.08, 1.08), "panel_green")
    parts.append(rounded_box("LAB18_SmokeDomain_MemoryBox", (0.42, 0.030, 0.32), (-0.52, -0.080, 1.28), mats["ghost"], 0.018, role="smoke_memory_budget", bh="BH-346"))
    for index, radius in enumerate([0.045, 0.060, 0.075]):
        parts.append(sphere(f"LAB18_SmokeVoxelBudget_{index+1}", (-0.65 + index * 0.12, -0.088, 1.28 + index * 0.04), radius, mats["smoke"], segments=14, role="smoke_memory_budget", bh="BH-346"))
    parts.append(rounded_box("LAB18_SmokeMemory_MaxCeiling", (0.34, 0.026, 0.055), (-0.22, -0.082, 1.43), mats["red"], 0.010, role="smoke_memory_budget", bh="BH-346"))
    domain = rounded_box("LAB18_Fluid_DomainNamed", (0.36, 0.030, 0.26), (0.36, -0.080, 1.26), mats["blue"], 0.014, role="fluid_domain_flow_naming", bh="BH-347")
    inflow = sphere("LAB18_Fluid_InflowNamed", (0.18, -0.088, 1.36), 0.035, mats["cyan"], segments=14, role="fluid_domain_flow_naming", bh="BH-347")
    effector = rounded_box("LAB18_Fluid_EffectorNamed", (0.18, 0.026, 0.055), (0.54, -0.086, 1.12), mats["orange"], 0.010, role="fluid_domain_flow_naming", bh="BH-347")
    parts.extend([domain, inflow, effector])
    parts.extend(arrow("LAB18_Fluid_FlowDirection", (0.20, -0.090, 1.34), (0.54, -0.090, 1.16), mats["cyan"], radius=0.005, role="fluid_domain_flow_naming", bh="BH-347"))
    seed = sphere("LAB18_ParticleSeed_Slider_Animated", (-0.35, -0.084, 0.66), 0.040, mats["magenta"], segments=16, role="particle_seed_density_gates", bh="BH-348")
    parts.append(seed)
    parts.append(cyl_between("LAB18_ParticleSeed_DensityRail", (-0.62, -0.094, 0.66), (0.62, -0.094, 0.66), 0.006, mats["magenta"], vertices=8, role="particle_seed_density_gates", bh="BH-348"))
    scatter_points = [(-0.57, -0.088, 0.45), (-0.35, -0.088, 0.55), (-0.10, -0.088, 0.43), (0.18, -0.088, 0.58), (0.42, -0.088, 0.48), (0.58, -0.088, 0.56)]
    for index, point in enumerate(scatter_points):
        parts.append(sphere(f"LAB18_ParticleSeed_Instance_{index+1}", point, 0.025, mats[["green", "cyan", "gold", "orange", "violet", "white"][index]], segments=10, role="particle_seed_density_gates", bh="BH-348"))
    for frame, x in ((1, -0.55), (48, 0.55), (96, -0.55)):
        bpy.context.scene.frame_set(frame)
        seed.location = (x, -0.084, 0.66)
        seed.keyframe_insert(data_path="location", frame=frame)
    add_text("LAB18_SimChip_Volumes", "voxel budget + domain naming", (-0.02, -0.100, 1.58), 0.033, mats["cyan"])
    add_text("LAB18_SimChip_Particles", "seed density realization gate", (0.02, -0.100, 0.30), 0.033, mats["magenta"])
    return parts


def build_compositing_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB18_CompPanel_Backplate", "RENDER PASSES / COMPOSITING", (1.96, 0.06, 1.05), (1.40, 0.08, 1.08), "panel_purple")
    pass_names = [("beauty", "white"), ("mist", "cyan"), ("vector", "magenta"), ("pos", "gold"), ("shadow", "shadow")]
    for index, (label, mat_key) in enumerate(pass_names):
        parts.append(rounded_box(f"LAB18_RenderPass_{label}", (0.19, 0.030, 0.070), (1.42 + index * 0.21, -0.080, 1.44), mats[mat_key], 0.010, role="render_pass_accounting_final", bh="BH-349"))
    for row, role_name in enumerate(["fg", "fx", "matte"]):
        for col, mat_key in enumerate(["green", "cyan", "violet"]):
            parts.append(rounded_box(f"LAB18_ViewLayer_{role_name}_{col+1}", (0.16, 0.026, 0.060), (1.48 + col * 0.22, -0.082, 1.16 - row * 0.12), mats[mat_key], 0.008, role="view_layer_collection_contracts", bh="BH-350"))
    parts.append(cyl_between("LAB18_DepthPass_CameraSpaceRuler", (2.28, -0.090, 0.86), (2.28, -0.090, 1.28), 0.006, mats["gold"], vertices=8, role="depth_position_space_notes", bh="BH-351"))
    parts.extend(arrow("LAB18_PositionPass_WorldAxes", (2.05, -0.090, 0.86), (2.45, -0.090, 0.86), mats["cyan"], radius=0.005, role="depth_position_space_notes", bh="BH-351"))
    parts.extend(arrow("LAB18_VectorBlur_ProofArrow", (1.44, -0.090, 0.70), (2.18, -0.090, 0.70), mats["magenta"], radius=0.006, role="compositor_blur_vector_proof", bh="BH-352"))
    toggle = sphere("LAB18_PassPreview_Toggle_Animated", (1.36, -0.084, 0.52), 0.038, mats["glow"], segments=16, role="compositor_blur_vector_proof", bh="BH-352")
    parts.append(toggle)
    parts.append(cyl_between("LAB18_PassPreview_ToggleRail", (1.28, -0.094, 0.52), (1.86, -0.094, 0.52), 0.006, mats["glow"], vertices=8, role="compositor_blur_vector_proof", bh="BH-352"))
    for frame, x in ((1, 1.32), (48, 1.82), (96, 1.32)):
        bpy.context.scene.frame_set(frame)
        toggle.location = (x, -0.084, 0.52)
        toggle.keyframe_insert(data_path="location", frame=frame)
    parts.append(rounded_box("LAB18_ShadowCatcher_DestinationPlate", (0.48, 0.026, 0.075), (2.18, -0.082, 0.49), mats["shadow"], 0.012, role="shadow_catcher_destination_proof", bh="BH-353"))
    parts.append(rounded_box("LAB18_CinematicComposite_Before", (0.26, 0.030, 0.150), (1.48, -0.080, 0.30), mats["ghost"], 0.012, role="cinematic_composite_before_after", bh="BH-354"))
    parts.append(rounded_box("LAB18_CinematicComposite_After", (0.26, 0.030, 0.150), (1.82, -0.080, 0.30), mats["gold"], 0.012, role="cinematic_composite_before_after", bh="BH-354"))
    parts.extend(arrow("LAB18_CinematicComposite_ReviewArrow", (1.62, -0.090, 0.30), (1.70, -0.090, 0.30), mats["white"], radius=0.0045, role="cinematic_composite_before_after", bh="BH-354"))
    add_text("LAB18_CompChip_Passes", "pass accounting + layer contracts", (1.96, -0.100, 1.58), 0.033, mats["cyan"])
    add_text("LAB18_CompChip_Review", "vector blur + shadow + before/after", (1.93, -0.100, 0.30), 0.033, mats["gold"])
    return parts


def build_export_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    add_panel(mats, "LAB18_ExportPanel_Backplate", "GLTF / GAME / CLEANUP HANDOFF", (0.00, 0.08, 0.15), (4.10, 0.08, 0.62), "panel_warm")
    for index, (label, mat_key) in enumerate([("apply", "green"), ("scale", "cyan"), ("pbr", "gold"), ("axis", "orange")]):
        parts.append(rounded_box(f"LAB18_GLTFCheck_{label}", (0.21, 0.030, 0.072), (-1.82 + index * 0.25, -0.080, 0.43), mats[mat_key], 0.010, role="gltf_transform_material_checks", bh="BH-355"))
    scrub = sphere("LAB18_VertexAnim_ViewerScrubber_Animated", (-0.62, -0.084, 0.43), 0.040, mats["magenta"], segments=16, role="vertex_animation_viewer_tests", bh="BH-356")
    parts.append(scrub)
    parts.append(cyl_between("LAB18_VertexAnim_ViewerRail", (-0.82, -0.094, 0.43), (-0.28, -0.094, 0.43), 0.006, mats["magenta"], vertices=8, role="vertex_animation_viewer_tests", bh="BH-356"))
    for frame, x in ((1, -0.78), (48, -0.32), (96, -0.78)):
        bpy.context.scene.frame_set(frame)
        scrub.location = (x, -0.084, 0.43)
        scrub.keyframe_insert(data_path="location", frame=frame)
    for index, (label, mat_key) in enumerate([("UCX", "ghost"), ("low", "blue"), ("trigger", "violet")]):
        parts.append(rounded_box(f"LAB18_GameCollision_{label}_Proxy", (0.22, 0.030, 0.082), (-0.02 + index * 0.27, -0.080, 0.43), mats[mat_key], 0.012, role="game_collision_export_naming", bh="BH-357"))
    for index, (label, mat_key) in enumerate([("bake", "orange"), ("sRGB", "white"), ("pack", "cyan"), ("relink", "green")]):
        parts.append(rounded_box(f"LAB18_TextureRelink_{label}", (0.20, 0.030, 0.072), (0.94 + index * 0.24, -0.080, 0.43), mats[mat_key], 0.010, role="texture_export_relink_qa_final", bh="BH-358"))
    parts.append(rounded_box("LAB18_DestructiveCleanup_PreDeform", (0.34, 0.030, 0.072), (2.04, -0.080, 0.43), mats["red"], 0.012, role="destructive_cleanup_deform_proof", bh="BH-359"))
    parts.append(rounded_box("LAB18_DestructiveCleanup_PostDeform", (0.34, 0.030, 0.072), (2.44, -0.080, 0.43), mats["green"], 0.012, role="destructive_cleanup_deform_proof", bh="BH-359"))
    parts.extend(arrow("LAB18_DestructiveCleanup_ApprovalArrow", (2.20, -0.090, 0.30), (2.34, -0.090, 0.30), mats["white"], radius=0.0045, role="destructive_cleanup_deform_proof", bh="BH-359"))
    add_text("LAB18_ExportChip_Left", "transform pbr viewer collision", (-0.82, -0.100, 0.58), 0.033, mats["cyan"])
    add_text("LAB18_ExportChip_Right", "texture relink + deform proof", (1.73, -0.100, 0.58), 0.033, mats["green"])
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    setup_lights()
    setup_camera()
    root = make_root()
    objects: list[bpy.types.Object] = []
    objects.append(rounded_box("LAB18_BaseProductionHandoffStage", (4.95, 0.13, 1.92), (0.0, 0.13, 0.74), mats["base"], 0.055, role="stage_base", export=True))
    add_text("LAB18_Title", "Blender Shorts Production Hygiene Lab v18", (0.0, -0.110, 1.82), 0.082, mats["white"])
    add_text("LAB18_Subtitle", "cloth  hair  sims  passes  compositor  GLTF  cleanup", (0.0, -0.110, 1.67), 0.043, mats["cyan"])
    objects.extend(build_cloth_hair_zone(mats))
    objects.extend(build_simulation_zone(mats))
    objects.extend(build_compositing_zone(mats))
    objects.extend(build_export_zone(mats))
    for index, info in enumerate(APPLIED_LIFEHACKS):
        row = index // 10
        col = index % 10
        objects.append(rounded_box(
            f"LAB18_AppliedTick_{info['id']}",
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
    required_roles = {item["role"] for item in APPLIED_LIFEHACKS}
    required_roles.add("stage_base")
    missing_roles = sorted(required_roles - set(roles))
    if missing_roles:
        errors.append(f"Missing required roles: {missing_roles}")
    lifehack_ids = sorted({str(obj.get("lifehack")) for obj in objects if obj.get("lifehack")})
    missing_lifehacks = sorted({item["id"] for item in APPLIED_LIFEHACKS} - set(lifehack_ids))
    if missing_lifehacks:
        errors.append(f"Missing applied lifehack IDs: {missing_lifehacks}")
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
        "LAB18_Root_TurntableAnimated",
        "LAB18_ClothCache_FrameSlider_Animated",
        "LAB18_HairWind_Control_Animated",
        "LAB18_ParticleSeed_Slider_Animated",
        "LAB18_PassPreview_Toggle_Animated",
        "LAB18_VertexAnim_ViewerScrubber_Animated",
    }
    missing_anim = sorted(expected_animated - set(animated))
    if missing_anim:
        errors.append(f"Expected animated production QA markers missing: {missing_anim}")
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
        "lifehack_ids": lifehack_ids,
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
        "mode": "icon/hero object + GLB export",
        "target_mode": "FREEFORM",
        "source_goal": "Final 1000-source Blender Shorts production-hygiene checkpoint test asset.",
        "stage_order": ["INITIALIZATION", "GEOMETRY", "MATERIAL", "COMPOSITION", "LIGHTING", "EXPORT_QA"],
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "expected_contacts": [
            {"a": "LAB18_BaseProductionHandoffStage", "b": "LAB18_*Panel_Backplate", "relation": "OVERLAPS", "status": "visual panel assembly"},
            {"a": "LAB18_TextureRelink_*", "b": "LAB18_ExportPanel_Backplate", "relation": "OVERLAPS", "status": "export QA group mounted"},
            {"a": "LAB18_ShadowCatcher_DestinationPlate", "b": "LAB18_CompPanel_Backplate", "relation": "OVERLAPS", "status": "shadow catcher proof mounted"},
        ],
        "acceptance": [
            "Cloth, collision, furnishing freeze, hair budget, grooming fallback and hair cache proof are visible.",
            "Smoke memory, fluid naming and particle seed/density gates are visible.",
            "Render pass accounting, view layer collection contracts, depth/position notes, vector blur proof, shadow catcher and before/after review are visible.",
            "GLTF transform/material checks, vertex animation viewer test, collision naming, texture relink QA and destructive cleanup deform proof are visible.",
            "Validation has no errors and no warnings.",
            "GLB excludes camera, lights and non-exported text helpers.",
        ],
        "export_object_names": build["export_object_names"],
        "non_exported_helper_names": build["non_exported_helper_names"],
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
