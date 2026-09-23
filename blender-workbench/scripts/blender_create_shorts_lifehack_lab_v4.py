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

ASSET = "blender_shorts_lifehack_lab_v4"
SCENE_NAME = "BlenderShortsLifehackLabV4"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-086", "name": "Retopo Is A Translation Layer", "applied": "Dense sculpt proxy is paired with a clean cage overlay."},
    {"id": "BH-087", "name": "Shrinkwrap Is Projection, Not Magic", "applied": "Projected decals show explicit offset from a tilted target surface."},
    {"id": "BH-088", "name": "Remesh By Purpose", "applied": "Voxel/remesh density blocks compare chunky, medium and refined cleanup."},
    {"id": "BH-089", "name": "Scale Controls Remesh Density", "applied": "Density blocks are arranged with visible scale steps."},
    {"id": "BH-090", "name": "UV Seams Are Strategy", "applied": "A seam board marks hidden seams and island direction."},
    {"id": "BH-091", "name": "Seam-Driven Detail Can Help", "applied": "Detail stripes follow seam/island planning instead of random placement."},
    {"id": "BH-093", "name": "Bad Topology Needs A Named Cleanup Stage", "applied": "The scene separates dense sculpt, cleanup cage and export-ready swatches."},
    {"id": "BH-094", "name": "Line Art Is Inspection And Style", "applied": "Cyan cage/outline curves make silhouette and edge-flow inspectable."},
    {"id": "BH-096", "name": "Asset Browser Is A Production Multiplier", "applied": "Reusable swatches and kit pieces are arranged as an asset shelf."},
    {"id": "BH-097", "name": "Collection Instances Need Clean Origins", "applied": "Instance modules include visible origin hubs."},
    {"id": "BH-098", "name": "Render Passes Are Planned Deliverables", "applied": "Render-pass cards show beauty, depth, mask and normals as planned outputs."},
    {"id": "BH-100", "name": "Automation Still Needs QA", "applied": "The script emits PNG, GLB, blend and validation reports."},
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
            "Specular IOR Level": 0.45,
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
        "base": make_mat("Lab4_BaseInk", (0.020, 0.022, 0.030, 1.0), roughness=0.50),
        "sculpt": make_mat("Lab4_DenseSculptClay", (0.78, 0.46, 0.30, 1.0), roughness=0.68),
        "cage": make_mat("Lab4_CageCyan", (0.04, 0.80, 1.0, 1.0), roughness=0.34, emission=(0.02, 0.45, 0.95, 1.0), emission_strength=0.18),
        "seam": make_mat("Lab4_SeamRed", (1.0, 0.10, 0.12, 1.0), roughness=0.35, emission=(0.70, 0.02, 0.02, 1.0), emission_strength=0.12),
        "uv_a": make_mat("Lab4_UVIslandA", (0.20, 0.84, 0.40, 1.0), roughness=0.62),
        "uv_b": make_mat("Lab4_UVIslandB", (0.35, 0.22, 0.94, 1.0), roughness=0.62),
        "uv_c": make_mat("Lab4_UVIslandC", (1.0, 0.72, 0.18, 1.0), roughness=0.58),
        "projection": make_mat("Lab4_ShrinkwrapTarget", (0.10, 0.14, 0.20, 1.0), roughness=0.72),
        "decal": make_mat("Lab4_ProjectionDecal", (0.95, 0.92, 0.82, 1.0), roughness=0.54),
        "swatch_1": make_mat("Lab4_AssetSwatchBlue", (0.10, 0.50, 1.0, 1.0), roughness=0.38),
        "swatch_2": make_mat("Lab4_AssetSwatchPink", (1.0, 0.18, 0.55, 1.0), roughness=0.40),
        "swatch_3": make_mat("Lab4_AssetSwatchGold", (1.0, 0.68, 0.16, 1.0), roughness=0.34, metallic=0.12),
        "pass_beauty": make_mat("Lab4_PassBeauty", (0.84, 0.86, 0.90, 1.0), roughness=0.56),
        "pass_depth": make_mat("Lab4_PassDepth", (0.18, 0.30, 0.48, 1.0), roughness=0.70),
        "pass_mask": make_mat("Lab4_PassMask", (0.95, 0.18, 0.22, 1.0), roughness=0.55),
        "pass_normals": make_mat("Lab4_PassNormals", (0.22, 0.78, 0.42, 1.0), roughness=0.55),
        "label": make_mat("Lab4_LabelWhite", (0.95, 0.97, 1.0, 1.0), roughness=0.55),
        "origin": make_mat("Lab4_OriginMarker", (1.0, 0.10, 0.10, 1.0), roughness=0.38, emission=(0.55, 0.02, 0.02, 1.0), emission_strength=0.10),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB4_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(name: str, size: tuple[float, float, float], loc: tuple[float, float, float], mat: bpy.types.Material, bevel: float = 0.02, rot: tuple[float, float, float] = (0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB4_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        obj.modifiers.new(name="LAB4_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, "rounded_box")


def cylinder(name: str, radius: float, depth: float, loc: tuple[float, float, float], mat: bpy.types.Material, vertices: int = 24, rot: tuple[float, float, float] = (0, 0, 0)) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, "cylinder")


def curve_line(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float = 0.008) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(pts) - 1)
    for p, co in zip(spline.points, pts):
        p.co = (co[0], co[1], co[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return tag(obj, "curve_line")


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
    scene.eevee.taa_render_samples = 96
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.world = scene.world or bpy.data.worlds.new("LAB4_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.0, 4.4))
    key = bpy.context.object
    key.name = "LAB4_KeyArea_Warm"
    key.data.energy = 530
    key.data.size = 4.2
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.2, 2.2, 3.0))
    fill = bpy.context.object
    fill.name = "LAB4_FillArea_Cool"
    fill.data.energy = 90
    fill.data.size = 4.8
    fill.data.color = (0.52, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.2, 2.6, 2.2))
    rim = bpy.context.object
    rim.name = "LAB4_RimPoint"
    rim.data.energy = 190
    rim.data.color = (0.35, 0.85, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(3.15, -4.45, 2.85), rotation=(math.radians(61), 0, math.radians(38)))
    cam = bpy.context.object
    cam.name = "LAB4_Camera_Hero3Q"
    cam.data.lens = 43
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.8
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


def create_dense_sculpt(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.38, location=(-1.05, 0.22, 0.46))
    blob = bpy.context.object
    blob.name = "LAB4_DenseSculptProxy_KeepAsSource"
    blob.scale = (1.05, 0.76, 0.86)
    apply_transform(blob)
    blob.data.materials.append(mats["sculpt"])
    for v in blob.data.vertices:
        wave = 0.045 * math.sin(v.co.x * 9.0) * math.cos(v.co.z * 8.0)
        v.co += v.co.normalized() * wave
    smooth(blob)
    tag(blob, "dense_sculpt_proxy")
    cage_parts = [blob]
    for z in (0.20, 0.46, 0.70):
        pts = []
        for i in range(33):
            a = math.tau * i / 32
            pts.append((-1.05 + math.cos(a) * 0.45, 0.22 + math.sin(a) * 0.31, z))
        cage_parts.append(curve_line(f"LAB4_RetopoCage_Ring_{z:.2f}", pts, mats["cage"], 0.006))
    for xoff in (-0.34, 0.0, 0.34):
        cage_parts.append(curve_line(f"LAB4_RetopoCage_Flow_{xoff:.2f}", [(-1.05 + xoff, -0.10, 0.18), (-1.05 + xoff * 0.4, 0.22, 0.48), (-1.05 - xoff * 0.2, 0.54, 0.74)], mats["cage"], 0.006))
    return cage_parts


def create_projection_demo(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts = []
    surface = rounded_box("LAB4_ShrinkwrapTarget_TiltedSurface", (0.95, 0.06, 0.62), (0.33, 0.20, 0.43), mats["projection"], 0.02, rot=(0, math.radians(-24), math.radians(-7)))
    tag(surface, "shrinkwrap_projection_target")
    parts.append(surface)
    for i, z in enumerate((0.24, 0.42, 0.60)):
        decal = rounded_box(f"LAB4_ProjectedDecal_OffsetCheck_{i}", (0.72, 0.018, 0.035), (0.30, 0.155 - i * 0.004, z), mats["decal"], 0.006, rot=(0, math.radians(-24), math.radians(-7)))
        tag(decal, "projected_decal_offset")
        parts.append(decal)
    return parts


def create_remesh_density_blocks(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts = []
    colors = [mats["swatch_1"], mats["swatch_2"], mats["swatch_3"]]
    for level, count in enumerate((2, 3, 4)):
        base_x = -1.38 + level * 0.36
        for ix in range(count):
            for iz in range(count):
                if (ix + iz + level) % 2 == 0 or count == 2:
                    cube = rounded_box(
                        f"LAB4_RemeshDensity_L{level}_{ix}_{iz}",
                        (0.09, 0.09, 0.09),
                        (base_x + ix * 0.085, -0.82, 0.12 + iz * 0.085),
                        colors[level],
                        0.006,
                    )
                    tag(cube, "remesh_density_block")
                    parts.append(cube)
    return parts


def create_uv_board(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts = []
    board = rounded_box("LAB4_UVSeamStrategyBoard", (1.12, 0.035, 0.70), (0.80, -0.82, 0.38), mats["uv_b"], 0.018, rot=(math.radians(0), 0, math.radians(4)))
    tag(board, "uv_strategy_board")
    parts.append(board)
    islands = [
        ("A", (-0.02, -0.84, 0.40), (0.32, 0.018, 0.44), mats["uv_a"]),
        ("B", (0.38, -0.84, 0.40), (0.22, 0.018, 0.52), mats["uv_c"]),
        ("C", (0.74, -0.84, 0.40), (0.28, 0.018, 0.36), mats["decal"]),
    ]
    for label, loc, size, mat in islands:
        island = rounded_box(f"LAB4_UVIsland_{label}", size, loc, mat, 0.010, rot=(0, 0, math.radians(4)))
        tag(island, "uv_island")
        parts.append(island)
    for x in (0.16, 0.58, 0.93):
        seam = curve_line(f"LAB4_RedSeamLine_{x:.2f}", [(x, -0.87, 0.10), (x + 0.05, -0.86, 0.72)], mats["seam"], 0.007)
        tag(seam, "uv_seam_line")
        parts.append(seam)
    return parts


def create_asset_shelf(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts = []
    shelf = rounded_box("LAB4_AssetBrowserShelf", (1.02, 0.08, 0.12), (-0.20, 0.94, 0.12), mats["projection"], 0.02)
    tag(shelf, "asset_library_shelf")
    parts.append(shelf)
    mats_list = [mats["swatch_1"], mats["swatch_2"], mats["swatch_3"]]
    for i, mat in enumerate(mats_list):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=0.095, location=(-0.58 + i * 0.28, 0.94, 0.28))
        swatch = bpy.context.object
        swatch.name = f"LAB4_MaterialAssetSwatch_{i}"
        swatch.data.materials.append(mat)
        smooth(swatch)
        tag(swatch, "asset_material_swatch")
        parts.append(swatch)
    for i, x in enumerate((0.44, 0.74)):
        module = rounded_box(f"LAB4_CollectionInstanceModule_{i}", (0.16, 0.12, 0.18), (x, 0.94, 0.25), mats_list[i], 0.018)
        origin = cylinder(f"LAB4_InstanceOriginHub_{i}", 0.026, 0.22, (x - 0.11, 0.94, 0.13), mats["origin"], 18, rot=(math.radians(90), 0, 0))
        tag(module, "collection_instance_module")
        tag(origin, "collection_origin_marker")
        parts.extend([module, origin])
    return parts


def create_render_pass_cards(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts = []
    specs = [
        ("Beauty", mats["pass_beauty"], (1.26, 0.74, 0.28)),
        ("Depth", mats["pass_depth"], (1.52, 0.74, 0.36)),
        ("Mask", mats["pass_mask"], (1.78, 0.74, 0.44)),
        ("Normals", mats["pass_normals"], (2.04, 0.74, 0.52)),
    ]
    for name, mat, loc in specs:
        card = rounded_box(f"LAB4_RenderPassCard_{name}", (0.22, 0.025, 0.30), loc, mat, 0.012, rot=(0, 0, math.radians(-8)))
        tag(card, "planned_render_pass_card")
        parts.append(card)
    return parts


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB4_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB4_StudioFloor_NotExported", (4.5, 3.2, 0.065), (0, 0, -0.045), mats["base"], 0.04)
    tag(floor, "preview_floor", export=False)

    export_parts: list[bpy.types.Object] = []
    export_parts.extend(create_dense_sculpt(mats))
    export_parts.extend(create_projection_demo(mats))
    export_parts.extend(create_remesh_density_blocks(mats))
    export_parts.extend(create_uv_board(mats))
    export_parts.extend(create_asset_shelf(mats))
    export_parts.extend(create_render_pass_cards(mats))

    labels = [
        add_text("LAB4_Label_Retopo", "DENSE -> RETOPO CAGE", (-1.02, 0.82, 0.94), 0.075, mats["label"]),
        add_text("LAB4_Label_Shrinkwrap", "SHRINKWRAP OFFSETS", (0.26, 0.72, 0.92), 0.070, mats["label"]),
        add_text("LAB4_Label_Remesh", "REMESH DENSITY", (-1.00, -1.08, 0.44), 0.070, mats["label"]),
        add_text("LAB4_Label_UV", "UV SEAM STRATEGY", (0.66, -1.10, 0.84), 0.070, mats["label"]),
        add_text("LAB4_Label_Assets", "ASSET SHELF", (-0.18, 1.18, 0.52), 0.070, mats["label"]),
        add_text("LAB4_Label_Passes", "PLANNED PASSES", (1.66, 1.02, 0.82), 0.065, mats["label"]),
    ]
    for label in labels:
        parent_keep_world(label, root)
    for obj in export_parts:
        parent_keep_world(obj, root)

    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path="rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.tau)
    root.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize(root)

    setup_lights()
    setup_camera()
    return {"root": root, "export_object_names": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is True]}


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
    return {
        "asset": ASSET,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "triangles": triangles,
        "exportable_objects": len(objects),
        "exportable_meshes": len(meshes),
        "roles": roles,
        "non_exported_helpers": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False],
        "animation": {
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": bpy.context.scene.render.fps,
            "animated_roots": [obj.name for obj in objects if obj.animation_data and obj.animation_data.action],
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
        "source_goal": "300-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Dense sculpt proxy and retopo cage are both visible.",
            "Projection target and decals show shrinkwrap offset thinking.",
            "Remesh density blocks show scale/density changes.",
            "UV seam board and render-pass cards are readable.",
            "Only exportable objects are in GLB.",
            "Validation has no errors and no warnings.",
        ],
        "export_object_names": build["export_object_names"],
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
        "glb": str(glb),
        "public_glb": str(PUBLIC_MODELS / f"{ASSET}.glb"),
        "blend": str(blend),
        "validation": validation,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
