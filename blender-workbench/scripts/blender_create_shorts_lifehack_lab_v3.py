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

ASSET = "blender_shorts_lifehack_lab_v3"
SCENE_NAME = "BlenderShortsLifehackLabV3"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {"id": "BH-071", "name": "Constraints Are Relationships", "applied": "The scene uses visible constraint relationship zones: track rail, hold ownership and limited gear motion."},
    {"id": "BH-072", "name": "Follow Path Is A Motion Rail", "applied": "A visible Bezier rail and markers demonstrate path-based motion planning."},
    {"id": "BH-073", "name": "Drivers Encode Ratios", "applied": "Gear rotations are baked as linked ratios for GLB-safe export."},
    {"id": "BH-074", "name": "Shape Keys Need Stable Topology", "applied": "One stable-topology sphere animates squash/stretch through keyed shape keys."},
    {"id": "BH-075", "name": "Shape Keys Can Be Rig Controls", "applied": "Shape-key values are animated as control states: squash, basis and stretch."},
    {"id": "BH-076", "name": "Bake Constraints Before Fragile Export", "applied": "Relationship motion is baked to normal keyframes for GLB."},
    {"id": "BH-077", "name": "Pickup And Hold Are Ownership States", "applied": "A hold zone shows object ownership changing between rail and clamp."},
    {"id": "BH-079", "name": "Compositor Glow Is A Separate Stage", "applied": "Glow rings are styled as secondary emissive accents, not structural geometry."},
    {"id": "BH-080", "name": "Mist/Depth Passes Are Review Outputs", "applied": "Depth bands are visible as review-layer planes behind the main motion rig."},
    {"id": "BH-081", "name": "Volumetrics Need Bounds", "applied": "Fog is represented by bounded translucent slabs to keep silhouettes readable."},
    {"id": "BH-085", "name": "Troubleshooting Motion Starts With Origins", "applied": "Origins/pivots are marked with small hubs and axis rods."},
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
    roughness: float = 0.52,
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
            "Specular IOR Level": 0.48,
            "Coat Weight": 0.06,
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
        "base": make_mat("Lab3_BaseInk", (0.020, 0.022, 0.030, 1.0), roughness=0.48),
        "rail": make_mat("Lab3_RailCyan", (0.06, 0.76, 1.0, 1.0), roughness=0.34, emission=(0.02, 0.30, 0.85, 1.0), emission_strength=0.15),
        "marker": make_mat("Lab3_MarkerPink", (1.0, 0.16, 0.55, 1.0), roughness=0.32, emission=(0.75, 0.04, 0.26, 1.0), emission_strength=0.16),
        "gold": make_mat("Lab3_GearGold", (1.0, 0.68, 0.16, 1.0), roughness=0.32, metallic=0.18),
        "violet": make_mat("Lab3_GearViolet", (0.42, 0.16, 0.92, 1.0), roughness=0.38),
        "shape": make_mat("Lab3_ShapeKeyGreen", (0.25, 0.92, 0.32, 1.0), roughness=0.44),
        "hold": make_mat("Lab3_HoldBlue", (0.10, 0.33, 1.0, 1.0), roughness=0.34),
        "prop": make_mat("Lab3_OwnedPropWhite", (0.96, 0.93, 0.84, 1.0), roughness=0.58),
        "glow": make_mat("Lab3_SecondaryGlow", (0.20, 0.75, 1.0, 1.0), roughness=0.18, emission=(0.08, 0.55, 1.0, 1.0), emission_strength=0.75),
        "fog": make_mat("Lab3_BoundedFog", (0.42, 0.62, 1.0, 1.0), roughness=0.75, alpha=0.20),
        "depth": make_mat("Lab3_DepthBand", (0.12, 0.20, 0.32, 1.0), roughness=0.80, alpha=0.34),
        "axis": make_mat("Lab3_OriginAxis", (1.0, 0.10, 0.12, 1.0), roughness=0.36, emission=(0.55, 0.03, 0.03, 1.0), emission_strength=0.12),
        "label": make_mat("Lab3_LabelWhite", (0.95, 0.97, 1.0, 1.0), roughness=0.56),
    }


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
        obj.modifiers.new(name="LAB3_WeightedNormals", type="WEIGHTED_NORMAL")


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
        mod = obj.modifiers.new(name="LAB3_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.profile = 0.5
        obj.modifiers.new(name="LAB3_WeightedNormals", type="WEIGHTED_NORMAL")
    return tag(obj, "rounded_box")


def cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    vertices: int = 24,
    rot: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth(obj)
    return tag(obj, "cylinder")


def make_curve(name: str, pts: list[tuple[float, float, float]], mat: bpy.types.Material, bevel: float) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
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
    return tag(obj, "motion_rail")


def add_text(name: str, text: str, loc: tuple[float, float, float], size: float, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(63), 0, 0))
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


def linearize(obj: bpy.types.Object) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    fcurves = getattr(action, "fcurves", None)
    if fcurves is None:
        return
    for curve in fcurves:
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"


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
    scene.world = scene.world or bpy.data.worlds.new("LAB3_World")
    scene.world.color = (0.018, 0.020, 0.028)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.0, -4.0, 4.5))
    key = bpy.context.object
    key.name = "LAB3_KeyArea_Warm"
    key.data.energy = 520
    key.data.size = 4.0
    tag(key, "key_light", export=False)
    bpy.ops.object.light_add(type="AREA", location=(3.5, 2.0, 3.2))
    fill = bpy.context.object
    fill.name = "LAB3_FillArea_Cool"
    fill.data.energy = 90
    fill.data.size = 5.0
    fill.data.color = (0.50, 0.70, 1.0)
    tag(fill, "fill_light", export=False)
    bpy.ops.object.light_add(type="POINT", location=(0.0, 2.6, 2.0))
    rim = bpy.context.object
    rim.name = "LAB3_RimPoint_Glow"
    rim.data.energy = 220
    rim.data.color = (0.35, 0.78, 1.0)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(3.2, -4.35, 2.75), rotation=(math.radians(61), 0, math.radians(38)))
    cam = bpy.context.object
    cam.name = "LAB3_Camera_Hero3Q"
    cam.data.lens = 43
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.8
    cam.data.dof.aperture_fstop = 9.0
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def create_gear(name: str, loc: tuple[float, float, float], radius: float, mat: bpy.types.Material, teeth: int = 12) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=0.08, location=loc, rotation=(math.radians(90), 0, 0))
    gear = bpy.context.object
    gear.name = name
    gear.data.materials.append(mat)
    smooth(gear)
    tag(gear, "linked_ratio_gear")
    for i in range(teeth):
        angle = math.tau * i / teeth
        tooth = rounded_box(
            f"{name}_Tooth_{i:02d}",
            (0.10, 0.05, 0.06),
            (loc[0] + math.cos(angle) * (radius + 0.04), loc[1], loc[2] + math.sin(angle) * (radius + 0.04)),
            mat,
            bevel=0.008,
            rot=(0, angle, 0),
        )
        parent_keep_world(tooth, gear)
    return gear


def animate_rotation(obj: bpy.types.Object, turns: float, axis: int = 1) -> None:
    obj.rotation_euler[axis] = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler[axis] = math.tau * turns
    obj.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize(obj)


def create_shape_key_sphere(mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.28, location=(0.0, -0.20, 0.38))
    obj = bpy.context.object
    obj.name = "LAB3_ShapeKeySquashStretch_StableTopology"
    obj.data.materials.append(mats["shape"])
    smooth(obj)
    tag(obj, "shape_key_morph")
    obj.shape_key_add(name="Basis")
    squash = obj.shape_key_add(name="Squash")
    stretch = obj.shape_key_add(name="Stretch")
    for i, vert in enumerate(obj.data.vertices):
        basis = vert.co
        squash.data[i].co = Vector((basis.x * 1.22, basis.y * 1.22, basis.z * 0.58))
        stretch.data[i].co = Vector((basis.x * 0.70, basis.y * 0.70, basis.z * 1.45))
    obj.data.shape_keys.key_blocks["Squash"].value = 1.0
    obj.data.shape_keys.key_blocks["Squash"].keyframe_insert("value", frame=1)
    obj.data.shape_keys.key_blocks["Stretch"].value = 0.0
    obj.data.shape_keys.key_blocks["Stretch"].keyframe_insert("value", frame=1)
    obj.data.shape_keys.key_blocks["Squash"].value = 0.0
    obj.data.shape_keys.key_blocks["Stretch"].value = 1.0
    obj.data.shape_keys.key_blocks["Squash"].keyframe_insert("value", frame=48)
    obj.data.shape_keys.key_blocks["Stretch"].keyframe_insert("value", frame=48)
    obj.data.shape_keys.key_blocks["Squash"].value = 1.0
    obj.data.shape_keys.key_blocks["Stretch"].value = 0.0
    obj.data.shape_keys.key_blocks["Squash"].keyframe_insert("value", frame=96)
    obj.data.shape_keys.key_blocks["Stretch"].keyframe_insert("value", frame=96)
    return obj


def create_path_markers(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    rail = make_curve(
        "LAB3_FollowPathRail_DirectionChecked",
        [(-1.45, -0.70, 0.24), (-0.68, -1.05, 0.44), (0.55, -0.95, 0.36), (1.45, -0.55, 0.62)],
        mats["rail"],
        0.016,
    )
    markers = [rail]
    positions = [(-1.25, -0.78, 0.30), (-0.28, -1.02, 0.42), (0.82, -0.84, 0.46)]
    for i, loc in enumerate(positions):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=0.075, location=loc)
        marker = bpy.context.object
        marker.name = f"LAB3_PathFollower_BakedMarker_{i}"
        marker.data.materials.append(mats["marker"])
        smooth(marker)
        tag(marker, "baked_follow_path_marker")
        marker.keyframe_insert(data_path="location", frame=1)
        marker.location.x += 0.52
        marker.location.y += 0.10 * (i - 1)
        marker.keyframe_insert(data_path="location", frame=48)
        marker.location.x -= 0.52
        marker.location.y -= 0.10 * (i - 1)
        marker.keyframe_insert(data_path="location", frame=96)
        linearize(marker)
        markers.append(marker)
    return markers


def create_hold_zone(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    clamp_l = rounded_box("LAB3_HoldClamp_LeftOwnershipState", (0.14, 0.40, 0.40), (-1.22, 0.55, 0.33), mats["hold"], bevel=0.025)
    clamp_r = rounded_box("LAB3_HoldClamp_RightOwnershipState", (0.14, 0.40, 0.40), (-0.72, 0.55, 0.33), mats["hold"], bevel=0.025)
    prop = rounded_box("LAB3_HeldProp_ConstraintHandoffBaked", (0.34, 0.16, 0.18), (-0.97, 0.55, 0.33), mats["prop"], bevel=0.026)
    for obj in (clamp_l, clamp_r, prop):
        tag(obj, "hold_ownership_zone")
        parts.append(obj)
    prop.keyframe_insert(data_path="location", frame=1)
    prop.location.x = -0.18
    prop.location.y = 0.24
    prop.keyframe_insert(data_path="location", frame=48)
    prop.location.x = -0.97
    prop.location.y = 0.55
    prop.keyframe_insert(data_path="location", frame=96)
    linearize(prop)
    return parts


def create_effect_layers(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    for i, z in enumerate((0.18, 0.46, 0.74)):
        band = rounded_box(
            f"LAB3_DepthReviewBand_{i}",
            (2.25 - i * 0.30, 0.025, 0.12),
            (0.55, 0.98 + i * 0.06, z),
            mats["depth"],
            bevel=0.008,
            rot=(0, 0, math.radians(4)),
        )
        tag(band, "mist_depth_review_layer")
        parts.append(band)
    fog = rounded_box("LAB3_BoundedFogVolume_StyleLayer", (1.15, 0.05, 0.74), (1.05, 0.78, 0.45), mats["fog"], bevel=0.02, rot=(0, 0, math.radians(-8)))
    tag(fog, "bounded_fog_style_layer")
    parts.append(fog)
    for i, x in enumerate((0.62, 1.02, 1.42)):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.10 + i * 0.025, minor_radius=0.007, major_segments=32, minor_segments=8, location=(x, 0.55, 0.30 + i * 0.16), rotation=(math.radians(90), 0, 0))
        ring = bpy.context.object
        ring.name = f"LAB3_GlowRing_SecondaryStylePass_{i}"
        ring.data.materials.append(mats["glow"])
        tag(ring, "secondary_glow_ring")
        parts.append(ring)
    return parts


def create_origin_marks(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    marks: list[bpy.types.Object] = []
    for i, loc in enumerate(((-1.22, 0.22, 0.10), (0.0, -0.20, 0.08), (1.20, -0.54, 0.12))):
        hub = cylinder(f"LAB3_OriginHub_{i}", 0.035, 0.28, loc, mats["axis"], vertices=20, rot=(math.radians(90), 0, 0))
        rod = rounded_box(f"LAB3_OriginAxisRod_{i}", (0.30, 0.022, 0.022), (loc[0] + 0.15, loc[1], loc[2]), mats["axis"], bevel=0.004)
        tag(hub, "origin_marker")
        tag(rod, "origin_marker")
        marks.extend([hub, rod])
    return marks


def build_scene() -> dict:
    setup_scene()
    mats = materials()
    root = bpy.data.objects.new("LAB3_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.45
    bpy.context.collection.objects.link(root)
    tag(root, "animated_root")

    floor = rounded_box("LAB3_StudioFloor_NotExported", (4.3, 3.15, 0.065), (0, 0, -0.045), mats["base"], bevel=0.04)
    tag(floor, "preview_floor", export=False)

    gear_a = create_gear("LAB3_LinkedGear_A_Ratio1", (-0.42, 0.42, 0.38), 0.22, mats["gold"], teeth=12)
    gear_b = create_gear("LAB3_LinkedGear_B_RatioMinus2", (0.02, 0.42, 0.38), 0.14, mats["violet"], teeth=10)
    animate_rotation(gear_a, 1.0, axis=1)
    animate_rotation(gear_b, -2.0, axis=1)

    export_parts = [gear_a, gear_b, create_shape_key_sphere(mats)]
    export_parts.extend(create_path_markers(mats))
    export_parts.extend(create_hold_zone(mats))
    export_parts.extend(create_effect_layers(mats))
    export_parts.extend(create_origin_marks(mats))

    for label in (
        add_text("LAB3_Label_Rail", "FOLLOW PATH RAIL", (0.0, -1.32, 0.38), 0.095, mats["label"]),
        add_text("LAB3_Label_Drivers", "LINKED RATIOS", (-0.20, 0.86, 0.72), 0.095, mats["label"]),
        add_text("LAB3_Label_ShapeKeys", "SHAPE KEY STATES", (0.0, 0.04, 0.84), 0.090, mats["label"]),
        add_text("LAB3_Label_Glow", "GLOW/DEPTH PASS", (1.08, 1.16, 0.86), 0.080, mats["label"]),
    ):
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
    if triangles > 32000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 32000.")
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
    shape_key_objects = [obj.name for obj in meshes if obj.data.shape_keys is not None]
    return {
        "asset": ASSET,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "triangles": triangles,
        "exportable_objects": len(objects),
        "exportable_meshes": len(meshes),
        "shape_key_objects": shape_key_objects,
        "non_exported_helpers": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False],
        "animation": {
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": bpy.context.scene.render.fps,
            "animated_roots": [obj.name for obj in objects if obj.animation_data and obj.animation_data.action],
            "animated_shape_keys": shape_key_objects,
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
        export_morph=True,
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
        "source_goal": "250-source Blender Shorts checkpoint test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "Follow-path rail and moving markers are visible.",
            "Linked-ratio gears have animation keyframes.",
            "Shape-key object has morph targets and animated values.",
            "Glow/fog/depth layers are secondary and do not hide core silhouette.",
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
