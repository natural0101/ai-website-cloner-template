from __future__ import annotations

import json
import math
import random
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

ASSET = "blender_shorts_lifehack_lab_v2"
SCENE_NAME = "BlenderShortsLifehackLabV2"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-056", "name": "Pin Cloth Before Simulating", "applied": "Wavy banner keeps visible top pin points and weighted fold direction."},
    {"id": "BH-057", "name": "Cloth Is A Shot Asset", "applied": "The cloth is baked as editable geometry for web export, not runtime simulation."},
    {"id": "BH-058", "name": "Grease Pencil As Planning Layer", "applied": "Planning arcs are represented by non-export-helper labels plus exportable curve strokes."},
    {"id": "BH-064", "name": "Instance Rotation And Random Transform", "applied": "Small droplets/chips vary position, scale and rotation in a controlled field."},
    {"id": "BH-065", "name": "Product Shadows Ground Scale", "applied": "Contact-shadow floor and low object heights make the lab parts feel placed."},
    {"id": "BH-067", "name": "Glass Needs Both Material And Render Settings", "applied": "Glass/water droplets use transparent PBR material plus reflective lighting."},
    {"id": "BH-068", "name": "Physical Water Defaults", "applied": "Water material starts from IOR 1.333 and subtle roughness."},
    {"id": "BH-069", "name": "Two-Sided Material Logic", "applied": "Leaf/card panels expose distinct front/back colored layers."},
    {"id": "BH-070", "name": "Snap Surface Details To The Surface", "applied": "Small decals are aligned to a tilted surface normal instead of floating flat."},
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
    ior: float | None = None,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    if alpha is not None:
        color = (color[0], color[1], color[2], alpha)
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": color,
            "Roughness": roughness,
            "Metallic": metallic,
            "Alpha": color[3],
            "Specular IOR Level": 0.52,
            "Coat Weight": 0.08,
            "Coat Roughness": 0.20,
        }
        if ior is not None:
            values["IOR"] = ior
            if "Transmission Weight" in bsdf.inputs:
                values["Transmission Weight"] = 0.42
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
        "base": make_mat("Lab2_BaseInk", (0.025, 0.026, 0.032, 1.0), roughness=0.44),
        "cloth_front": make_mat("Lab2_ClothFront_Coral", (0.96, 0.25, 0.30, 1.0), roughness=0.72),
        "cloth_back": make_mat("Lab2_ClothBack_Gold", (1.0, 0.72, 0.20, 1.0), roughness=0.68),
        "pin": make_mat("Lab2_PinBlue", (0.07, 0.48, 1.0, 1.0), roughness=0.30, emission=(0.02, 0.16, 0.55, 1.0), emission_strength=0.12),
        "stroke": make_mat("Lab2_StrokeWhite", (0.95, 0.97, 1.0, 1.0), roughness=0.45, emission=(0.45, 0.62, 1.0, 1.0), emission_strength=0.16),
        "water": make_mat("Lab2_WaterGlassIOR1333", (0.35, 0.82, 1.0, 1.0), roughness=0.04, alpha=0.46, ior=1.333),
        "leaf_front": make_mat("Lab2_TwoSidedFrontGreen", (0.20, 0.90, 0.38, 1.0), roughness=0.52),
        "leaf_back": make_mat("Lab2_TwoSidedBackViolet", (0.50, 0.20, 0.95, 1.0), roughness=0.56),
        "decal": make_mat("Lab2_SurfaceDecalWhite", (0.96, 0.93, 0.84, 1.0), roughness=0.62),
        "pink": make_mat("Lab2_InstancePink", (1.0, 0.18, 0.62, 1.0), roughness=0.38),
        "cyan": make_mat("Lab2_InstanceCyan", (0.12, 0.82, 1.0, 1.0), roughness=0.36),
        "gold": make_mat("Lab2_InstanceGold", (1.0, 0.70, 0.15, 1.0), roughness=0.42, metallic=0.10),
        "shadow": make_mat("Lab2_ContactShadowMatte", (0.012, 0.012, 0.017, 1.0), roughness=0.86),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
            obj.modifiers.new(name="LAB2_WeightedNormals", type="WEIGHTED_NORMAL")


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.025,
    rot: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB2_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.profile = 0.5
        obj.modifiers.new(name="LAB2_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, "rounded_box")


def make_curve(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 10
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(pts) - 1)
    for p, co in zip(spline.bezier_points, pts):
        p.co = co
        p.handle_left_type = "AUTO"
        p.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return tag(obj, "planning_curve")


def add_text(name: str, text: str, loc: tuple[float, float, float], size: float, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(63), 0, math.radians(0)))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.008
    obj.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    return tag(obj, "preview_label", export=False)


def create_cloth_banner(mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    cols = 18
    rows = 8
    width = 2.15
    height = 0.72
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for r in range(rows + 1):
        v = r / rows
        for c in range(cols + 1):
            u = c / cols
            x = -width / 2 + u * width
            y = 0.18 + (v - 0.5) * height
            z = 0.52 + 0.16 * math.sin(u * math.tau * 1.45 + 0.5) * (0.25 + v) - 0.10 * v
            verts.append((x, y, z))
    for r in range(rows):
        for c in range(cols):
            a = r * (cols + 1) + c
            faces.append((a, a + 1, a + cols + 2, a + cols + 1))
    mesh = bpy.data.meshes.new("LAB2_PinnedClothBannerMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("LAB2_PinnedClothBanner_BakedShotMesh", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mats["cloth_front"])
    obj.data.materials.append(mats["cloth_back"])
    for i, poly in enumerate(obj.data.polygons):
        poly.material_index = 0 if i % 2 == 0 else 1
    tag(obj, "pinned_cloth_baked_mesh")
    return obj


def create_pin(name: str, loc: tuple[float, float, float], mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.065, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale.z = 0.55
    apply_transform(obj)
    obj.data.materials.append(mats["pin"])
    smooth(obj)
    return tag(obj, "visible_cloth_pin")


def create_leaf_panel(name: str, loc: tuple[float, float, float], rot_z: float, mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    front = rounded_box(f"{name}_FrontGreen", (0.36, 0.018, 0.72), loc, mats["leaf_front"], bevel=0.018, rot=(math.radians(10), 0, rot_z))
    back_loc = (loc[0], loc[1] + 0.012, loc[2] - 0.018)
    back = rounded_box(f"{name}_BackViolet", (0.34, 0.014, 0.68), back_loc, mats["leaf_back"], bevel=0.016, rot=(math.radians(10), 0, rot_z))
    tag(front, "two_sided_panel_front")
    tag(back, "two_sided_panel_back")
    return [front, back]


def create_droplets(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    random.seed(204)
    droplets: list[bpy.types.Object] = []
    for i in range(18):
        x = -0.95 + random.random() * 1.9
        y = -0.88 + random.random() * 0.58
        r = 0.028 + random.random() * 0.038
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=r, location=(x, y, 0.09 + r * 0.35))
        obj = bpy.context.object
        obj.name = f"LAB2_WaterDroplet_RandomScale_{i:02d}"
        obj.scale.z = 0.45 + random.random() * 0.55
        obj.rotation_euler[2] = random.random() * math.tau
        apply_transform(obj)
        obj.data.materials.append(mats["water"])
        smooth(obj)
        tag(obj, "random_water_droplet")
        droplets.append(obj)
    return droplets


def create_random_chips(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    random.seed(200)
    palette = [mats["pink"], mats["cyan"], mats["gold"]]
    chips: list[bpy.types.Object] = []
    for i in range(16):
        angle = math.tau * i / 16.0
        radius = 1.45 + random.uniform(-0.10, 0.12)
        loc = (math.cos(angle) * radius, math.sin(angle) * radius * 0.78, 0.13 + random.random() * 0.18)
        obj = rounded_box(
            f"LAB2_RandomizedInstanceChip_{i:02d}",
            (0.12 + random.random() * 0.09, 0.07 + random.random() * 0.04, 0.035 + random.random() * 0.045),
            loc,
            palette[i % len(palette)],
            bevel=0.014,
            rot=(random.uniform(-0.12, 0.12), random.uniform(-0.12, 0.12), angle + random.uniform(-0.45, 0.45)),
        )
        tag(obj, "randomized_transform_instance")
        chips.append(obj)
    return chips


def create_surface_decals(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    panel_rot = (math.radians(0), math.radians(-22), math.radians(-9))
    surface = rounded_box("LAB2_TiltedSurface_TargetForSnappedDecals", (0.82, 0.05, 0.56), (0.92, 0.22, 0.33), mats["shadow"], bevel=0.02, rot=panel_rot)
    tag(surface, "tilted_decal_surface")
    decals = [surface]
    for i, dz in enumerate((-0.18, 0.0, 0.18)):
        decal = rounded_box(
            f"LAB2_SurfaceAlignedDecal_{i}",
            (0.58, 0.018, 0.035),
            (0.91, 0.185 - 0.005 * i, 0.33 + dz),
            mats["decal"],
            bevel=0.006,
            rot=panel_rot,
        )
        tag(decal, "surface_aligned_decal")
        decals.append(decal)
    return decals


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
    scene.world = scene.world or bpy.data.worlds.new("LAB2_World")
    scene.world.color = (0.022, 0.025, 0.035)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.2, 4.2))
    key = bpy.context.object
    key.name = "LAB2_KeyArea_Warm"
    key.data.energy = 520
    key.data.size = 4.1
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.4, 2.3, 2.8))
    fill = bpy.context.object
    fill.name = "LAB2_FillArea_Blue"
    fill.data.energy = 90
    fill.data.size = 4.8
    fill.data.color = (0.55, 0.72, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.2, 2.8, 1.7))
    rim = bpy.context.object
    rim.name = "LAB2_RimPoint_GlassSpark"
    rim.data.energy = 170
    rim.data.color = (0.55, 0.85, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(3.0, -4.25, 2.45), rotation=(math.radians(61), 0, math.radians(37)))
    cam = bpy.context.object
    cam.name = "LAB2_Camera_Hero3Q"
    cam.data.lens = 42
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.6
    cam.data.dof.aperture_fstop = 8.5
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


def animate_root(root: bpy.types.Object) -> None:
    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path="rotation_euler", frame=1)
    root.rotation_euler = (0, 0, math.tau)
    root.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize(root)


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB2_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB2_ContactShadowFloor_NotExported", (4.2, 3.1, 0.065), (0, 0, -0.045), mats["shadow"], bevel=0.04)
    tag(floor, "preview_floor", export=False)

    cloth = create_cloth_banner(mats)
    parent_keep_world(cloth, root)
    for name, loc in (
        ("LAB2_Pin_LeftAnchor", (-1.08, -0.18, 0.63)),
        ("LAB2_Pin_RightAnchor", (1.08, -0.18, 0.55)),
    ):
        parent_keep_world(create_pin(name, loc, mats), root)

    for curve in (
        make_curve("LAB2_PlanningStroke_ClothFallArc", [(-1.25, -0.50, 0.72), (-0.35, -0.78, 0.48), (0.52, -0.62, 0.55), (1.18, -0.44, 0.48)], mats["stroke"], 0.014),
        make_curve("LAB2_PlanningStroke_GlassFocusArc", [(-0.82, -1.02, 0.22), (-0.12, -1.24, 0.34), (0.72, -1.05, 0.22)], mats["stroke"], 0.010),
    ):
        parent_keep_world(curve, root)

    for obj in create_droplets(mats) + create_random_chips(mats) + create_surface_decals(mats):
        parent_keep_world(obj, root)

    for obj in create_leaf_panel("LAB2_TwoSidedPanel_A", (-1.30, 0.38, 0.31), math.radians(22), mats):
        parent_keep_world(obj, root)
    for obj in create_leaf_panel("LAB2_TwoSidedPanel_B", (1.35, -0.34, 0.29), math.radians(-26), mats):
        parent_keep_world(obj, root)

    labels = [
        add_text("LAB2_Label_PinnedCloth", "PINNED CLOTH", (0.0, 0.74, 0.83), 0.11, mats["stroke"]),
        add_text("LAB2_Label_WaterIOR", "WATER IOR 1.333", (-0.18, -1.43, 0.32), 0.09, mats["stroke"]),
        add_text("LAB2_Label_SnappedDecals", "SURFACE-SNAPPED", (1.05, 0.72, 0.63), 0.08, mats["stroke"]),
    ]
    for label in labels:
        parent_keep_world(label, root)

    animate_root(root)
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
    if triangles > 30000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 30000.")
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
        "source_goal": "200-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Pinned cloth mesh and pins are visible.",
            "Glass/water droplets render with transparent material.",
            "Surface decals align to the tilted panel.",
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
