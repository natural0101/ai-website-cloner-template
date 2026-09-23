import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_robot_hand_button_v2.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_robot_hand_button_v2.glb"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-robot-hand-v2-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-robot-hand-v2-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-robot-hand-v2-top.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_robot_hand_button_v2_scene_report.json"

for path in (BLEND_PATH, GLB_PATH, HERO_PATH, SIDE_PATH, TOP_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_collection(name):
    existing = bpy.data.collections.get(name)
    if existing is not None:
        return existing
    result = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(result)
    return result


def move_to_collection(obj, target):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def smooth(obj):
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def make_material(name, color, roughness, metallic=0.0, emission=None, emission_strength=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = 0.22
    bsdf.inputs["Coat Roughness"].default_value = 0.12
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return material


def rounded_box(name, dimensions, location, radius, material, target_collection, rotation=None, segments=6):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Rounded", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.48)
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    if hasattr(bevel, "harden_normals"):
        bevel.harden_normals = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    weighted = obj.modifiers.new(name=f"{name}_WeightedNormals", type="WEIGHTED_NORMAL")
    if hasattr(weighted, "keep_sharp"):
        weighted.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    if rotation is not None:
        obj.rotation_euler = rotation
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    apply_material(obj, material)
    move_to_collection(obj, target_collection)
    return obj


def ellipsoid(name, location, scale, material, target_collection, rotation=None, segments=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(12, segments // 2), radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if rotation is not None:
        obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj)
    apply_material(obj, material)
    move_to_collection(obj, target_collection)
    return obj


def segment_between(name, start, end, width, height, radius, material, target_collection, trim_start=0.06, trim_end=0.12):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    distance = direction.length
    unit = direction.normalized()
    trimmed_a = a + unit * min(trim_start, distance * 0.2)
    trimmed_b = b - unit * min(trim_end, distance * 0.2)
    center = (trimmed_a + trimmed_b) * 0.5
    length = max(0.05, (trimmed_b - trimmed_a).length)
    rotation = (trimmed_b - trimmed_a).to_track_quat("X", "Z").to_euler()
    return rounded_box(
        name,
        (length, width, height),
        center,
        radius,
        material,
        target_collection,
        rotation=rotation,
        segments=5,
    )


def joint(name, point, scale, material, target_collection):
    return ellipsoid(name, point, scale, material, target_collection, segments=18)


def guide_curve(name, points, target_collection):
    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.018
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for target, point in zip(spline.points, points, strict=True):
        target.co = (*point, 1.0)
    obj = bpy.data.objects.new(name, curve)
    target_collection.objects.link(obj)
    obj.hide_render = True
    obj["abt_export"] = False
    return obj


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def add_robot_finger(name, points, widths, white, joint_mat, output_collection, guide_collection, hand_root, press_group=None):
    guide_curve(f"TEAMON_{name}_Guide", points, guide_collection)
    labels = ("Distal", "Middle", "Proximal")
    parts = []
    for index, label in enumerate(labels):
        part = segment_between(
            f"TEAMON_{name}_{label}",
            points[index],
            points[index + 1],
            widths[index],
            widths[index] * 0.82,
            widths[index] * 0.24,
            white,
            output_collection,
            trim_start=0.05 if index == 0 else 0.14,
            trim_end=0.14 if index < 2 else 0.04,
        )
        parent_keep_world(part, press_group if press_group is not None and index == 0 else hand_root)
        parts.append(part)

    tip = joint(
        f"TEAMON_{name}_Tip",
        points[0],
        (widths[0] * 0.58, widths[0] * 0.52, widths[0] * 0.42),
        white,
        output_collection,
    )
    parent_keep_world(tip, press_group if press_group is not None else hand_root)
    parts.append(tip)

    for index, point in enumerate(points[1:3], start=1):
        hinge = joint(
            f"TEAMON_{name}_Joint_{index:02d}",
            point,
            (widths[index - 1] * 0.36, widths[index - 1] * 0.34, widths[index - 1] * 0.36),
            joint_mat,
            output_collection,
        )
        parent_keep_world(hinge, hand_root)
        parts.append(hinge)

    root_joint = joint(
        f"TEAMON_{name}_Root_Joint",
        points[3],
        (widths[2] * 0.40, widths[2] * 0.38, widths[2] * 0.40),
        joint_mat,
        output_collection,
    )
    parent_keep_world(root_joint, hand_root)
    parts.append(root_joint)
    return parts


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
asset_collection = bpy.data.collections.get("TEAMON_ASSET")
studio_collection = bpy.data.collections.get("TEAMON_STUDIO")
if asset_collection is None or studio_collection is None:
    raise RuntimeError("TEAMON v1 scene collections are missing")

source_collection = ensure_collection("TEAMON_HAND_SOURCE")
output_collection = ensure_collection("TEAMON_HAND_OUTPUT")

white = make_material("TEAMON_Robot_White", (0.94, 0.955, 0.98), roughness=0.28)
joint_mat = make_material("TEAMON_Robot_Joint_Rose", (0.34, 0.17, 0.18), roughness=0.42, metallic=0.05)
seam_mat = make_material("TEAMON_Robot_Seam", (0.035, 0.018, 0.022), roughness=0.5)

hand_root = bpy.data.objects.new("TEAMON_HandRoot", None)
output_collection.objects.link(hand_root)
hand_root["abt_export"] = True
press_group = bpy.data.objects.new("TEAMON_HandPressGroup", None)
output_collection.objects.link(press_group)
press_group.parent = hand_root
press_group["press_axis"] = "LOCAL_Z"
press_group["press_travel"] = 0.15

palm = ellipsoid(
    "TEAMON_Palm_Shell",
    (4.45, 2.25, 2.55),
    (1.28, 0.98, 0.66),
    white,
    output_collection,
    rotation=(math.radians(-8), math.radians(10), math.radians(-18)),
    segments=28,
)
parent_keep_world(palm, hand_root)

palm_plate = rounded_box(
    "TEAMON_Palm_Dorsal_Plate",
    (1.86, 1.48, 0.34),
    (4.32, 2.10, 2.91),
    0.26,
    white,
    output_collection,
    rotation=(math.radians(-8), math.radians(8), math.radians(-18)),
    segments=8,
)
parent_keep_world(palm_plate, hand_root)

wrist_joint = ellipsoid("TEAMON_Wrist_Joint", (5.35, 2.70, 2.48), (0.60, 0.58, 0.54), joint_mat, output_collection)
parent_keep_world(wrist_joint, hand_root)
wrist_cuff = segment_between(
    "TEAMON_Wrist_Cuff",
    (5.25, 2.65, 2.50),
    (6.72, 3.42, 2.38),
    1.55,
    1.12,
    0.38,
    white,
    output_collection,
    trim_start=0.0,
    trim_end=0.0,
)
parent_keep_world(wrist_cuff, hand_root)
wrist_seam = segment_between(
    "TEAMON_Wrist_Seam",
    (5.28, 2.67, 2.50),
    (5.54, 2.81, 2.48),
    1.62,
    1.18,
    0.18,
    seam_mat,
    output_collection,
    trim_start=0.0,
    trim_end=0.0,
)
parent_keep_world(wrist_seam, hand_root)

finger_specs = {
    "Index": {
        "points": [(1.78, -0.08, 1.82), (2.52, 0.25, 2.03), (3.23, 0.75, 2.25), (3.82, 1.35, 2.43)],
        "widths": (0.47, 0.53, 0.59),
        "press": True,
    },
    "Middle": {
        "points": [(2.55, 0.48, 2.38), (2.92, 0.95, 2.92), (3.43, 1.48, 3.08), (3.95, 1.76, 2.83)],
        "widths": (0.45, 0.51, 0.58),
        "press": False,
    },
    "Ring": {
        "points": [(3.00, 0.82, 2.46), (3.31, 1.22, 3.00), (3.79, 1.68, 3.15), (4.24, 2.00, 2.74)],
        "widths": (0.42, 0.48, 0.55),
        "press": False,
    },
    "Pinky": {
        "points": [(3.43, 1.18, 2.42), (3.72, 1.54, 2.88), (4.13, 1.94, 2.98), (4.55, 2.25, 2.63)],
        "widths": (0.38, 0.44, 0.50),
        "press": False,
    },
}

hand_parts = [palm, palm_plate, wrist_joint, wrist_cuff, wrist_seam]
for finger_name, spec in finger_specs.items():
    hand_parts.extend(
        add_robot_finger(
            finger_name,
            spec["points"],
            spec["widths"],
            white,
            joint_mat,
            output_collection,
            source_collection,
            hand_root,
            press_group=press_group if spec["press"] else None,
        )
    )

thumb_points = [(3.48, 0.35, 1.78), (3.90, 0.78, 1.94), (4.25, 1.27, 2.10), (4.55, 1.72, 2.26)]
hand_parts.extend(
    add_robot_finger(
        "Thumb",
        thumb_points,
        (0.48, 0.54, 0.60),
        white,
        joint_mat,
        output_collection,
        source_collection,
        hand_root,
    )
)

# Tighten the button construction: one dark monolithic base, one shallow inner rim.
rim = bpy.data.objects.get("TEAMON_Rim")
if rim is not None:
    rim.dimensions.z = 0.25
    rim.location.z = 0.785
    bpy.context.view_layer.objects.active = rim
    rim.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    rim.select_set(False)
edge_material = bpy.data.materials.get("TEAMON_Acrylic_Edge")
if edge_material and edge_material.use_nodes:
    edge_bsdf = edge_material.node_tree.nodes.get("Principled BSDF")
    edge_bsdf.inputs["Base Color"].default_value = (0.10, 0.20, 0.24, 1.0)
    edge_bsdf.inputs["Emission Strength"].default_value = 0.28

old_edge = bpy.data.objects.get("TEAMON_Keycap_Edge")
if old_edge is not None:
    bpy.data.objects.remove(old_edge, do_unlink=True)
button_press_group = bpy.data.objects.get("TEAMON_PressGroup")
new_edge = rounded_box(
    "TEAMON_Keycap_Edge",
    (5.0, 3.54, 0.075),
    (0.0, 0.0, 1.12),
    0.028,
    edge_material,
    asset_collection,
    segments=4,
)
parent_keep_world(new_edge, button_press_group)

camera = scene.camera
camera.location = (8.20, -9.70, 7.40)
camera.data.lens = 55
look_at(camera, (0.55, 0.42, 1.45))

scene.render.resolution_x = 1152
scene.render.resolution_y = 648
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.engine = "BLENDER_EEVEE"
scene.view_settings.look = "AgX - Medium High Contrast"

bpy.context.view_layer.update()
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
camera.location = (10.5, -1.7, 4.1)
look_at(camera, (1.6, 0.8, 1.8))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)

camera.location = (0.0, -0.6, 12.8)
look_at(camera, (1.1, 0.6, 1.1))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)

camera.location = hero_location
camera.rotation_euler = hero_rotation
scene.render.filepath = str(HERO_PATH)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = list(asset_collection.objects) + list(output_collection.objects)
for obj in export_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects.get("TEAMON_Root")
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)

mesh_objects = [obj for obj in export_objects if obj.type == "MESH"]
for obj in mesh_objects:
    obj.data.calc_loop_triangles()
triangle_count = sum(len(obj.data.loop_triangles) for obj in mesh_objects)

keycap = bpy.data.objects.get("TEAMON_Keycap")
index_tip = bpy.data.objects.get("TEAMON_Index_Tip")
keycap_top = keycap.matrix_world.translation.z + keycap.dimensions.z * 0.5
tip_bottom = index_tip.matrix_world.translation.z - index_tip.dimensions.z * 0.5
contact_gap = tip_bottom - keycap_top

report = {
    "asset": "TEAMON robot hand button v2",
    "target_mode": "HYBRID_HERO",
    "blender_version": bpy.app.version_string,
    "outputs": {
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "hero": str(HERO_PATH),
        "side": str(SIDE_PATH),
        "top": str(TOP_PATH),
    },
    "object_count": len(export_objects),
    "mesh_count": len(mesh_objects),
    "triangle_count": triangle_count,
    "required_nodes": [
        "TEAMON_Root",
        "TEAMON_PressGroup",
        "TEAMON_HandRoot",
        "TEAMON_HandPressGroup",
        "TEAMON_Palm_Shell",
        "TEAMON_Index_Tip",
        "TEAMON_Wrist_Cuff"
    ],
    "missing_required_nodes": [
        name
        for name in (
            "TEAMON_Root",
            "TEAMON_PressGroup",
            "TEAMON_HandRoot",
            "TEAMON_HandPressGroup",
            "TEAMON_Palm_Shell",
            "TEAMON_Index_Tip",
            "TEAMON_Wrist_Cuff",
        )
        if bpy.data.objects.get(name) is None
    ],
    "contact_checks": {
        "keycap_top_z": round(keycap_top, 4),
        "index_tip_bottom_z": round(tip_bottom, 4),
        "index_tip_keycap_gap": round(contact_gap, 4),
        "contact_tolerance": 0.035,
        "contact_pass": abs(contact_gap) <= 0.035,
    },
    "warnings": [
        "Hidden back-of-hand mechanics are an authored assumption from a single hero reference.",
        "Only the distal index group is intended to move during the web press."
    ],
    "validation_errors": [],
}
if triangle_count > 100000:
    report["validation_errors"].append("Triangle budget exceeded")
if report["missing_required_nodes"]:
    report["validation_errors"].append("Missing required nodes")
if not report["contact_checks"]["contact_pass"]:
    report["validation_errors"].append("Index fingertip does not contact keycap")

REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print("TEAMON_ROBOT_HAND_V2_REPORT=" + json.dumps(report, ensure_ascii=False))
