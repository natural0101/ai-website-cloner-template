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

ASSET = "blender_shorts_lifehack_lab_v12"
SCENE_NAME = "BlenderShortsLifehackLabV12"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-221", "name": "Blend Files Need Collection Contracts", "applied": "Collection tree board exposes viewport/render/export states and cleanup gates."},
    {"id": "BH-222", "name": "UV Speed Needs Seam And Pin Audits", "applied": "UV island board shows seams, pins, padding and stretch check markers."},
    {"id": "BH-223", "name": "Smart UV Is A Draft Pass", "applied": "Smart UV area is marked as draft-only until intentional seams pass review."},
    {"id": "BH-224", "name": "Texture Painting Needs Channel Versioning", "applied": "Texture paint swatches show channel ownership, brush state and version chips."},
    {"id": "BH-225", "name": "Shader Speedups Need Node Hygiene", "applied": "Node Wrangler speed board ends in framed, labeled, cleanup-ready nodes."},
    {"id": "BH-226", "name": "Textures Need Scale And Resolution Rules", "applied": "Texture ruler displays texel density, material source and resolution gates."},
    {"id": "BH-227", "name": "Shading Modes Are QA Views", "applied": "QA view strip separates solid, material, rendered and face-orientation checks."},
    {"id": "BH-228", "name": "Procedural Materials Need Bake Decisions", "applied": "Gradient/PBR card records bake-vs-runtime decision before web delivery."},
    {"id": "BH-229", "name": "Asset Libraries Need Provenance", "applied": "Asset library shelf records root, catalog, license, cache and missing-file gates."},
    {"id": "BH-230", "name": "Reusable Assets Need Scale Proof", "applied": "Reusable asset thumbnail has origin, bounds and unit-scale ruler."},
    {"id": "BH-231", "name": "Mesh Cleanup Needs Before/After Metrics", "applied": "Cleanup board shows before/after mesh, removed edges and overlap check."},
    {"id": "BH-232", "name": "Poly Reduction Needs Silhouette Budget", "applied": "Poly reduction marker compares dense and budget silhouettes."},
    {"id": "BH-233", "name": "GLB Export Needs Transform And Material Audit", "applied": "GLB gate checks transforms, helper exclusion, materials, animation and filesize."},
    {"id": "BH-234", "name": "Normals Need Weighted And Autosmooth Discipline", "applied": "Normals rig shows face orientation, shade smooth, autosmooth and weighted-normal arrows."},
    {"id": "BH-235", "name": "Bevels Need Parameter Audits", "applied": "Bevel board exposes applied scale, clamp, width, segments, profile and highlight checks."},
    {"id": "BH-236", "name": "Solidify Needs Thickness And Normal QA", "applied": "Solidify shell shows thickness, offset, rim closing and normal direction."},
    {"id": "BH-237", "name": "Modifier Stacks Need Order Contracts", "applied": "Modifier stack board shows ordered live/apply decisions and animated count marker."},
    {"id": "BH-238", "name": "Hard Surface References Need Blockout Tags", "applied": "Hard-surface board converts inspiration into blockout modules and layer tags."},
    {"id": "BH-239", "name": "Fast Color Changes Need Palette Ownership", "applied": "Palette strip links color swatches to owned materials for late global edits."},
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
        "base": make_mat("Lab12_BaseGraphite", (0.020, 0.022, 0.030, 1.0), roughness=0.64),
        "panel": make_mat("Lab12_PanelInk", (0.055, 0.065, 0.092, 1.0), roughness=0.60),
        "panel_alt": make_mat("Lab12_PanelDeepAubergine", (0.090, 0.050, 0.095, 1.0), roughness=0.64),
        "cyan": make_mat("Lab12_AuditCyan", (0.02, 0.78, 0.96, 1.0), roughness=0.34, emission=(0.0, 0.25, 0.55, 1.0), emission_strength=0.10),
        "green": make_mat("Lab12_CheckGreen", (0.13, 0.83, 0.42, 1.0), roughness=0.46),
        "gold": make_mat("Lab12_LicenseGold", (1.0, 0.70, 0.18, 1.0), roughness=0.42, metallic=0.03),
        "magenta": make_mat("Lab12_PinMagenta", (0.98, 0.12, 0.52, 1.0), roughness=0.40, emission=(0.42, 0.0, 0.18, 1.0), emission_strength=0.08),
        "blue": make_mat("Lab12_UVBlue", (0.10, 0.36, 0.92, 1.0), roughness=0.48),
        "violet": make_mat("Lab12_ModifierViolet", (0.46, 0.25, 0.88, 1.0), roughness=0.46),
        "orange": make_mat("Lab12_BevelOrange", (0.96, 0.43, 0.12, 1.0), roughness=0.44),
        "red": make_mat("Lab12_WarningRed", (0.98, 0.10, 0.08, 1.0), roughness=0.35, emission=(0.45, 0.02, 0.02, 1.0), emission_strength=0.08),
        "white": make_mat("Lab12_LabelWhite", (0.94, 0.97, 1.0, 1.0), roughness=0.52),
        "dark": make_mat("Lab12_DarkSocket", (0.015, 0.017, 0.024, 1.0), roughness=0.70),
        "ghost": make_mat("Lab12_DebugGhost", (0.55, 0.72, 1.0, 1.0), roughness=0.54, alpha=0.28),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB12_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.015,
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
        mod = obj.modifiers.new(name="LAB12_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB12_WeightedNormals", type="WEIGHTED_NORMAL")
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


def cylinder_between(
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
    radius: float = 0.008,
    role: str = "direction_arrow",
    bh: str | None = None,
) -> list[bpy.types.Object]:
    a = Vector(start)
    b = Vector(end)
    mid = a.lerp(b, 0.78)
    return [
        cylinder_between(f"{name}_Shaft", tuple(a), tuple(mid), radius, mat, role=role, bh=bh),
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
    scene.world = scene.world or bpy.data.worlds.new("LAB12_World")
    scene.world.color = (0.016, 0.018, 0.026)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-4.6, -5.2, 4.7))
    key = bpy.context.object
    key.name = "LAB12_KeyArea_Warm"
    key.data.energy = 690
    key.data.size = 5.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(4.4, 2.5, 3.2))
    fill = bpy.context.object
    fill.name = "LAB12_FillArea_Cool"
    fill.data.energy = 150
    fill.data.size = 5.2
    fill.data.color = (0.54, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.5, 3.4, 2.7))
    rim = bpy.context.object
    rim.name = "LAB12_RimPoint_Cyan"
    rim.data.energy = 260
    rim.data.color = (0.35, 0.86, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(4.10, -5.10, 3.15), rotation=(math.radians(58), 0, math.radians(40)))
    cam = bpy.context.object
    cam.name = "LAB12_Camera_Hero3Q"
    cam.data.lens = 41
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 5.15
    cam.data.dof.aperture_fstop = 16.0
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


def panel_base(name: str, loc: tuple[float, float, float], mat: bpy.types.Material, role: str) -> bpy.types.Object:
    return rounded_box(name, (2.04, 0.08, 1.12), loc, mat, 0.025, role=role)


def make_uv_texture_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    parts.append(panel_base("LAB12_UVTextureBoard", (-1.28, -0.82, 0.68), mats["panel"], "uv_material_lab_panel"))

    island_specs = [
        ("A", -1.78, 1.02, 0.33, 0.14, mats["blue"]),
        ("B", -1.28, 0.94, 0.28, 0.18, mats["cyan"]),
        ("C", -0.86, 1.03, 0.20, 0.22, mats["green"]),
    ]
    for label, x, z, sx, sz, mat in island_specs:
        island = rounded_box(f"LAB12_UVIsland_{label}_PinnedReviewed", (sx, 0.045, sz), (x, -0.88, z), mat, 0.012, role="uv_seam_pin_audit", bh="BH-222")
        island["uv_review"] = "seams, pins, padding, stretch"
        parts.append(island)
        parts.append(cylinder_between(f"LAB12_UVSeam_{label}_RedAudit", (x - sx / 2, -0.905, z + sz / 2), (x + sx / 2, -0.905, z - sz / 2), 0.006, mats["red"], role="uv_seam_pin_audit", bh="BH-222"))
        parts.append(sphere(f"LAB12_UVPin_{label}_Locked", 0.028, (x + sx * 0.28, -0.92, z + sz * 0.18), mats["magenta"], role="uv_seam_pin_audit", bh="BH-222"))

    draft = rounded_box("LAB12_SmartUVDraftGate_NotFinal", (0.40, 0.050, 0.13), (-1.80, -0.88, 0.70), mats["red"], 0.008, role="smart_uv_draft_gate", bh="BH-223")
    draft["status"] = "draft only until intentional seam review"
    parts.append(draft)

    channel_colors = [("Base", mats["blue"]), ("Rough", mats["green"]), ("Disp", mats["gold"]), ("V03", mats["magenta"])]
    for i, (label, mat) in enumerate(channel_colors):
        chip = rounded_box(f"LAB12_TextureChannel_{label}_Versioned", (0.18, 0.045, 0.11), (-1.48 + i * 0.22, -0.89, 0.60), mat, 0.006, role="texture_channel_versioning", bh="BH-224")
        chip["texture_paint_rule"] = "channel owner, brush state, backup image"
        parts.append(chip)

    node_positions = [(-0.96, 0.74), (-0.68, 0.74), (-0.40, 0.74), (-0.54, 0.58)]
    for i, (x, z) in enumerate(node_positions):
        node = rounded_box(f"LAB12_NodeHygiene_FrameLabel_{i}", (0.18, 0.045, 0.10), (x, -0.89, z), [mats["cyan"], mats["violet"], mats["green"], mats["gold"]][i], 0.006, role="shader_node_hygiene", bh="BH-225")
        node["node_state"] = "framed, labeled, preview cleanup"
        parts.append(node)
    parts.extend(arrow("LAB12_NodeWranglerCleanupFlow", (-0.86, -0.91, 0.74), (-0.50, -0.91, 0.66), mats["white"], radius=0.005, role="shader_node_hygiene", bh="BH-225"))

    ruler = rounded_box("LAB12_TextureScaleTexelDensityRuler", (0.70, 0.040, 0.045), (-1.55, -0.91, 0.38), mats["dark"], 0.004, role="texture_scale_resolution_rule", bh="BH-226")
    ruler["texture_rule"] = "texel density, source license, resolution"
    parts.append(ruler)
    for i in range(6):
        parts.append(rounded_box(f"LAB12_TextureScaleTick_{i}", (0.018, 0.044, 0.090 if i % 2 == 0 else 0.060), (-1.86 + i * 0.12, -0.925, 0.39), mats["gold"], 0.002, role="texture_scale_resolution_rule", bh="BH-226"))

    view_mats = [mats["dark"], mats["blue"], mats["orange"], mats["red"]]
    for i, mat in enumerate(view_mats):
        tile = rounded_box(f"LAB12_ShadingModeQAView_{i}", (0.18, 0.045, 0.13), (-0.90 + i * 0.23, -0.90, 0.38), mat, 0.006, role="shading_mode_qa_views", bh="BH-227")
        tile["qa_view"] = ["solid", "material", "rendered", "face orientation"][i]
        parts.append(tile)

    grad_steps = [mats["blue"], mats["cyan"], mats["green"], mats["gold"], mats["orange"]]
    for i, mat in enumerate(grad_steps):
        step = rounded_box(f"LAB12_ProceduralGradientBakeDecision_{i}", (0.11, 0.046, 0.12), (-0.42 + i * 0.12, -0.90, 0.96), mat, 0.004, role="procedural_bake_decision", bh="BH-228")
        step["delivery_decision"] = "bake texture or runtime PBR"
        parts.append(step)
    parts.append(rounded_box("LAB12_PrincipledPBRRuntimeCard", (0.30, 0.050, 0.11), (-0.18, -0.89, 0.80), mats["white"], 0.006, role="procedural_bake_decision", bh="BH-228"))
    return parts


def make_asset_library_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    parts.append(panel_base("LAB12_AssetLibraryFileBoard", (1.02, -0.76, 0.68), mats["panel_alt"], "asset_library_lab_panel"))

    collection_x = 0.34
    for i, (name, mat) in enumerate((("SRC", mats["cyan"]), ("WORK", mats["blue"]), ("EXPORT", mats["green"]), ("ARCHIVE", mats["gold"]))):
        branch = rounded_box(f"LAB12_CollectionContract_{name}", (0.28, 0.045, 0.11), (collection_x, -0.83, 1.08 - i * 0.15), mat, 0.006, role="collection_contract", bh="BH-221")
        branch["visibility_contract"] = "viewport, render, export, cleanup"
        parts.append(branch)
        if i:
            parts.append(cylinder_between(f"LAB12_CollectionContractLink_{i}", (collection_x - 0.16, -0.85, 1.16 - (i - 1) * 0.15), (collection_x - 0.16, -0.85, 1.10 - i * 0.15), 0.005, mats["white"], role="collection_contract", bh="BH-221"))
    parts.append(rounded_box("LAB12_OrphanCleanupGate_Visible", (0.20, 0.050, 0.10), (0.72, -0.84, 0.62), mats["red"], 0.006, role="collection_contract", bh="BH-221"))

    shelf_y = -0.86
    for row, z in enumerate((1.00, 0.80, 0.60)):
        parts.append(rounded_box(f"LAB12_AssetLibraryShelf_{row}", (0.72, 0.045, 0.045), (1.25, shelf_y, z - 0.10), mats["dark"], 0.004, role="asset_library_provenance", bh="BH-229"))
        for col in range(4):
            x = 0.98 + col * 0.18
            asset = rounded_box(f"LAB12_AssetCatalogItem_R{row}_C{col}", (0.12, 0.055, 0.12), (x, shelf_y - 0.01, z), [mats["blue"], mats["green"], mats["gold"], mats["magenta"]][(row + col) % 4], 0.008, role="asset_library_provenance", bh="BH-229")
            asset["asset_metadata"] = "root, catalog, license, cache, missing-file gate"
            parts.append(asset)

    thumb = rounded_box("LAB12_ReusableAssetThumbnail_ScaleProof", (0.36, 0.055, 0.23), (1.75, -0.85, 1.03), mats["white"], 0.010, role="reusable_asset_scale_proof", bh="BH-230")
    thumb["scale_proof"] = "origin, bounds, unit scale"
    parts.append(thumb)
    cube = rounded_box("LAB12_ReusableAssetBoundsCube_UnitScale", (0.13, 0.050, 0.13), (1.70, -0.89, 1.04), mats["cyan"], 0.004, role="reusable_asset_scale_proof", bh="BH-230")
    origin = sphere("LAB12_ReusableAssetOriginDot", 0.022, (1.83, -0.91, 0.92), mats["magenta"], role="reusable_asset_scale_proof", bh="BH-230")
    parts.extend([cube, origin])
    parts.extend(arrow("LAB12_ReusableAssetScaleRuler", (1.58, -0.91, 0.82), (1.92, -0.91, 0.82), mats["gold"], radius=0.005, role="reusable_asset_scale_proof", bh="BH-230"))

    palette_mats = [mats["cyan"], mats["green"], mats["gold"], mats["orange"], mats["magenta"]]
    for i, mat in enumerate(palette_mats):
        swatch = rounded_box(f"LAB12_PaletteOwner_LinkedSwatch_{i}", (0.16, 0.050, 0.12), (0.92 + i * 0.20, -0.89, 0.35), mat, 0.006, role="palette_ownership", bh="BH-239")
        swatch["palette_owner"] = "linked material instance"
        parts.append(swatch)
    return parts


def make_mesh_export_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    parts.append(panel_base("LAB12_MeshCleanupExportBoard", (-1.28, 0.32, 0.64), mats["panel_alt"], "mesh_export_lab_panel"))

    before = rounded_box("LAB12_MeshCleanupBefore_DirtyEdges", (0.38, 0.050, 0.27), (-1.82, 0.25, 0.98), mats["red"], 0.004, role="mesh_cleanup_metrics", bh="BH-231")
    after = rounded_box("LAB12_MeshCleanupAfter_MetricsPass", (0.32, 0.050, 0.22), (-1.18, 0.25, 0.98), mats["green"], 0.010, role="mesh_cleanup_metrics", bh="BH-231")
    before["cleanup_metrics"] = "selected scope, merge threshold, overlap check"
    after["removed_edges"] = 12
    parts.extend([before, after])
    for i in range(5):
        parts.append(cylinder_between(f"LAB12_DirtyEdgeMetric_{i}", (-1.98 + i * 0.08, 0.22, 1.12), (-1.90 + i * 0.08, 0.22, 0.86), 0.004, mats["white"], role="mesh_cleanup_metrics", bh="BH-231"))
    parts.extend(arrow("LAB12_CleanupBeforeAfterArrow", (-1.58, 0.24, 0.98), (-1.36, 0.24, 0.98), mats["cyan"], radius=0.006, role="mesh_cleanup_metrics", bh="BH-231"))

    for i, scale in enumerate((1.0, 0.72, 0.50)):
        obj = rounded_box(f"LAB12_PolyReductionSilhouetteBudget_{i}", (0.30 * scale, 0.045, 0.22 * scale), (-1.86 + i * 0.32, 0.25, 0.60), [mats["blue"], mats["cyan"], mats["green"]][i], 0.006, role="poly_reduction_silhouette_budget", bh="BH-232")
        obj["triangle_budget"] = [2400, 1200, 640][i]
        parts.append(obj)

    gate = rounded_box("LAB12_GLBExportAudit_PulsingGate", (0.52, 0.060, 0.34), (-0.72, 0.22, 0.96), mats["dark"], 0.012, role="glb_transform_material_audit", bh="BH-233")
    gate["glb_audit"] = "transforms, materials, helpers, animation, filesize"
    parts.append(gate)
    for i, mat in enumerate((mats["green"], mats["green"], mats["gold"], mats["cyan"], mats["magenta"])):
        tick = rounded_box(f"LAB12_GLBExportAuditTick_{i}", (0.07, 0.066, 0.07), (-0.92 + i * 0.10, 0.18, 0.79), mat, 0.004, role="glb_transform_material_audit", bh="BH-233")
        parts.append(tick)
    gate.scale = (1.0, 1.0, 1.0)
    gate.keyframe_insert(data_path="scale", frame=1)
    gate.scale = (1.05, 1.05, 1.05)
    gate.keyframe_insert(data_path="scale", frame=48)
    gate.scale = (1.0, 1.0, 1.0)
    gate.keyframe_insert(data_path="scale", frame=96)
    linearize(gate)

    normal_card = rounded_box("LAB12_NormalsWeightedAutosmoothCard", (0.58, 0.050, 0.28), (-0.76, 0.24, 0.52), mats["blue"], 0.010, role="normals_weighted_autosmooth", bh="BH-234")
    normal_card["normal_pipeline"] = "face orientation, shade smooth, autosmooth, weighted normals"
    parts.append(normal_card)
    for i, x in enumerate((-0.96, -0.82, -0.68, -0.54)):
        parts.extend(arrow(f"LAB12_NormalDirectionQA_{i}", (x, 0.20, 0.43), (x + 0.06, 0.20, 0.63), [mats["cyan"], mats["green"], mats["gold"], mats["white"]][i], radius=0.004, role="normals_weighted_autosmooth", bh="BH-234"))
    return parts


def make_modifier_hardsurface_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    parts.append(panel_base("LAB12_ModifierHardSurfaceBoard", (1.02, 0.38, 0.64), mats["panel"], "modifier_hardsurface_lab_panel"))

    bevel = rounded_box("LAB12_BevelParameterAudit_ProfileHighlight", (0.50, 0.050, 0.28), (0.38, 0.31, 1.00), mats["orange"], 0.035, role="bevel_parameter_audit", bh="BH-235")
    bevel["bevel_audit"] = "applied scale, clamp, width, segments, profile, highlights"
    parts.append(bevel)
    for i in range(4):
        parts.append(cylinder_between(f"LAB12_BevelHighlightStripe_{i}", (0.18 + i * 0.10, 0.26, 1.16), (0.22 + i * 0.10, 0.26, 0.85), 0.004, mats["white"], role="bevel_parameter_audit", bh="BH-235"))

    shell_outer = rounded_box("LAB12_SolidifyOuterShell_NormalQA", (0.42, 0.050, 0.30), (0.98, 0.30, 1.00), mats["cyan"], 0.018, role="solidify_thickness_normal_qa", bh="BH-236")
    shell_inner = rounded_box("LAB12_SolidifyInnerShell_OffsetVisible", (0.28, 0.052, 0.18), (0.98, 0.265, 1.00), mats["dark"], 0.010, role="solidify_thickness_normal_qa", bh="BH-236")
    shell_outer["solidify_qa"] = "thickness, offset, rim close, normal direction"
    parts.extend([shell_outer, shell_inner])
    parts.extend(arrow("LAB12_SolidifyThicknessArrow", (1.18, 0.25, 0.88), (1.18, 0.25, 1.13), mats["gold"], radius=0.005, role="solidify_thickness_normal_qa", bh="BH-236"))

    stack_names = ["CURVE", "ARRAY", "DISPLACE", "BEVEL", "WN", "APPLY?"]
    for i, name in enumerate(stack_names):
        block = rounded_box(f"LAB12_ModifierStackOrder_{i}_{name}", (0.32, 0.050, 0.095), (1.65, 0.30, 1.16 - i * 0.13), [mats["blue"], mats["cyan"], mats["violet"], mats["orange"], mats["green"], mats["gold"]][i], 0.006, role="modifier_stack_order_contract", bh="BH-237")
        block["stack_rule"] = "order, strength/count limits, live/apply decision"
        parts.append(block)
    marker = sphere("LAB12_ModifierStackOrder_TimedMarker", 0.035, (1.42, 0.25, 1.16), mats["magenta"], role="modifier_stack_order_contract", bh="BH-237")
    parts.append(marker)
    marker.location.z = 1.16
    marker.keyframe_insert(data_path="location", frame=1)
    marker.location.z = 0.51
    marker.keyframe_insert(data_path="location", frame=96)
    linearize(marker)

    module_mats = [mats["blue"], mats["cyan"], mats["green"], mats["gold"], mats["violet"]]
    for i in range(5):
        x = 0.32 + i * 0.26
        z = 0.45 + (0.10 if i % 2 else 0.0)
        module = rounded_box(f"LAB12_HardSurfaceBlockoutTag_Module_{i}", (0.22, 0.055, 0.18), (x, 0.30, z), module_mats[i], 0.012, role="hard_surface_blockout_tags", bh="BH-238")
        module["hard_surface_rule"] = "blockout module, layer tag, bevel/normal consistency"
        parts.append(module)
        if i:
            parts.append(cylinder_between(f"LAB12_HardSurfaceModuleSeam_{i}", (x - 0.15, 0.27, z), (x - 0.07, 0.27, z), 0.004, mats["white"], role="hard_surface_blockout_tags", bh="BH-238"))
    return parts


def make_rear_summary_marks(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    board_specs = [
        ("UVTexture", -1.28, -0.755, 0.68, ["uv_seam_pin_audit", "texture_channel_versioning", "shader_node_hygiene", "procedural_bake_decision"], "BH-222..BH-228"),
        ("Assets", 1.02, -0.695, 0.68, ["collection_contract", "asset_library_provenance", "reusable_asset_scale_proof", "palette_ownership"], "BH-221,BH-229,BH-230,BH-239"),
        ("MeshExport", -1.28, 0.385, 0.64, ["mesh_cleanup_metrics", "poly_reduction_silhouette_budget", "glb_transform_material_audit", "normals_weighted_autosmooth"], "BH-231..BH-234"),
        ("Modifiers", 1.02, 0.445, 0.64, ["bevel_parameter_audit", "solidify_thickness_normal_qa", "modifier_stack_order_contract", "hard_surface_blockout_tags"], "BH-235..BH-238"),
    ]
    swatches = [mats["cyan"], mats["green"], mats["gold"], mats["magenta"]]
    for board_name, x, y, z, roles, bh in board_specs:
        rail = rounded_box(f"LAB12_RearSummaryRail_{board_name}", (1.14, 0.040, 0.055), (x, y, z + 0.18), mats["dark"], 0.004, role=roles[0], bh=bh)
        rail["rear_summary"] = "backside turntable readability marker"
        parts.append(rail)
        for i, role in enumerate(roles):
            chip = rounded_box(f"LAB12_RearSummaryChip_{board_name}_{i}", (0.20, 0.046, 0.12), (x - 0.42 + i * 0.28, y + 0.01, z), swatches[i], 0.007, role=role, bh=bh)
            chip["rear_summary"] = "visible on half-turn so backs are not blank"
            parts.append(chip)
        parts.extend(arrow(f"LAB12_RearSummaryFlow_{board_name}", (x - 0.56, y + 0.02, z - 0.18), (x + 0.56, y + 0.02, z - 0.18), mats["white"], radius=0.004, role=roles[-1], bh=bh))
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB12_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root", bh="BH-221..BH-239")

    floor = rounded_box("LAB12_StudioFloor_NotExported", (5.35, 3.46, 0.065), (0.05, -0.08, -0.045), mats["base"], 0.04, role="preview_floor", export=False)
    export_parts: list[bpy.types.Object] = []
    helper_parts: list[bpy.types.Object] = [floor]

    export_parts.extend(make_uv_texture_board(mats))
    export_parts.extend(make_asset_library_board(mats))
    export_parts.extend(make_mesh_export_board(mats))
    export_parts.extend(make_modifier_hardsurface_board(mats))
    export_parts.extend(make_rear_summary_marks(mats))
    labels = [
        add_text("LAB12_Label_UVTexture", "UV / TEXTURE / MATERIAL QA", (-1.28, -1.25, 1.25), 0.046, mats["white"]),
        add_text("LAB12_Label_Assets", "ASSET LIBRARY / FILE CONTRACTS", (1.02, -1.25, 1.25), 0.045, mats["white"]),
        add_text("LAB12_Label_MeshExport", "MESH CLEANUP / GLB EXPORT", (-1.28, -0.05, 1.18), 0.046, mats["white"]),
        add_text("LAB12_Label_Modifiers", "MODIFIERS / HARD SURFACE", (1.02, 0.00, 1.18), 0.046, mats["white"]),
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
        if obj.name == "LAB12_UVPin_A_Locked":
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=1)
            obj.scale = (1.28, 1.28, 1.28)
            obj.keyframe_insert(data_path="scale", frame=48)
            obj.scale = (1.0, 1.0, 1.0)
            obj.keyframe_insert(data_path="scale", frame=96)
            linearize(obj)
        if obj.name == "LAB12_PaletteOwner_LinkedSwatch_2":
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
        "collection_contract",
        "uv_seam_pin_audit",
        "smart_uv_draft_gate",
        "texture_channel_versioning",
        "shader_node_hygiene",
        "texture_scale_resolution_rule",
        "shading_mode_qa_views",
        "procedural_bake_decision",
        "asset_library_provenance",
        "reusable_asset_scale_proof",
        "mesh_cleanup_metrics",
        "poly_reduction_silhouette_budget",
        "glb_transform_material_audit",
        "normals_weighted_autosmooth",
        "bevel_parameter_audit",
        "solidify_thickness_normal_qa",
        "modifier_stack_order_contract",
        "hard_surface_blockout_tags",
        "palette_ownership",
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
    if "LAB12_Root_TurntableAnimated" not in animated:
        errors.append("Root turntable animation is missing.")
    expected_animated = {
        "LAB12_GLBExportAudit_PulsingGate",
        "LAB12_ModifierStackOrder_TimedMarker",
        "LAB12_PaletteOwner_LinkedSwatch_2",
        "LAB12_UVPin_A_Locked",
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
        "source_goal": "700-source Blender Shorts checkpoint test asset.",
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
            "UV seam/pin audit, Smart UV draft gate and texture/channel versioning are visible.",
            "Shader node hygiene, texture scale rules, shading-mode QA and procedural bake decision are visible.",
            "Collection contracts, asset-library provenance, reusable scale proof and palette ownership are visible.",
            "Mesh cleanup metrics, poly silhouette budget, GLB audit and normal discipline are visible.",
            "Bevel, Solidify, modifier-stack and hard-surface blockout checks are visible.",
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
