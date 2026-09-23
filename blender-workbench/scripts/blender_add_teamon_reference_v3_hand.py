import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_clay_hand.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_clay_hand_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-clay-hand-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-clay-hand-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-clay-hand-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj, target):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def make_material(name, color, roughness, metallic=0.0, coat=0.0):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = 0.10
    return material


def smooth_mesh(obj):
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def ellipsoid(name, location, scale, material, collection, rotation=None, segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=max(16, segments // 2),
        radius=1.0,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if rotation is not None:
        obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    apply_material(obj, material)
    move_to_collection(obj, collection)
    return obj


def capsule_between(name, start, end, width, height, material, collection, overlap=0.10):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    distance = direction.length
    if distance <= 0.001:
        raise ValueError(f"{name}: capsule endpoints coincide")
    unit = direction.normalized()
    center = (a + b) * 0.5
    obj = ellipsoid(
        name,
        center,
        (distance * 0.5 + overlap, width * 0.5, height * 0.5),
        material,
        collection,
        segments=28,
    )
    obj.rotation_euler = unit.to_track_quat("X", "Z").to_euler()
    return obj


def joint_pin(name, location, radius, depth, material, collection, rotation=(math.radians(90.0), 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bevel = obj.modifiers.new(name=f"{name}_Edge", type="BEVEL")
    bevel.width = radius * 0.16
    bevel.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    smooth_mesh(obj)
    apply_material(obj, material)
    move_to_collection(obj, collection)
    return obj


def guide_curve(name, points, collection):
    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.016
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points, strict=True):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.hide_render = True
    obj["export"] = False
    return obj


def rounded_box(name, dimensions, location, radius, material, collection, rotation=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.45)
    bevel.segments = 6
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    if rotation is not None:
        obj.rotation_euler = rotation
    smooth_mesh(obj)
    apply_material(obj, material)
    move_to_collection(obj, collection)
    return obj


def build_finger(name, points, widths, heights, white, joint_material, output, guides, hand_root, press_group=None):
    guide_curve(f"TEAMON_{name}_Guide", points, guides)
    parts = []
    labels = ("Proximal", "Middle", "Distal")
    for index, label in enumerate(labels):
        segment = capsule_between(
            f"TEAMON_{name}_{label}_Shell",
            points[index],
            points[index + 1],
            widths[index],
            heights[index],
            white,
            output,
            overlap=widths[index] * 0.18,
        )
        parent_keep_world(segment, press_group if press_group is not None and index == 2 else hand_root)
        parts.append(segment)

    for index, point in enumerate(points[1:3], start=1):
        pin = joint_pin(
            f"TEAMON_{name}_JointPin_{index:02d}",
            point,
            radius=widths[index - 1] * 0.23,
            depth=widths[index - 1] * 0.54,
            material=joint_material,
            collection=output,
        )
        parent_keep_world(pin, hand_root)
        parts.append(pin)

    tip_direction = (Vector(points[-1]) - Vector(points[-2])).normalized()
    pad_center = Vector(points[-1]) + tip_direction * widths[-1] * 0.06
    pad = ellipsoid(
        f"TEAMON_{name}_TipPad",
        pad_center,
        (widths[-1] * 0.58, widths[-1] * 0.45, heights[-1] * 0.43),
        white,
        output,
        segments=28,
    )
    pad.rotation_euler = tip_direction.to_track_quat("X", "Z").to_euler()
    parent_keep_world(pad, press_group if press_group is not None else hand_root)
    parts.append(pad)
    return parts


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
output = ensure_collection("TEAMON_OUTPUT")
source = ensure_collection("TEAMON_SOURCE")
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
if composition_root is None or bpy.data.objects.get("TEAMON_Base") is None:
    raise RuntimeError("TEAMON v3 button blockout must be opened before adding the hand")

hand_root = bpy.data.objects.new("TEAMON_HandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["export"] = True
press_group = bpy.data.objects.new("TEAMON_HandPressGroup", None)
output.objects.link(press_group)
press_group.parent = hand_root
press_group["interaction"] = "index_distal_press"

white = make_material("TEAMON_Robot_White_V3", (0.92, 0.935, 0.955), 0.27, coat=0.22)
joint_material = make_material("TEAMON_Robot_Joint_Rose_V3", (0.34, 0.11, 0.13), 0.38, metallic=0.03, coat=0.08)
seam_material = make_material("TEAMON_Robot_Seam_V3", (0.028, 0.012, 0.016), 0.48)

# One dominant continuous palm mass, with overlapping thenar and dorsal shells.
palm = ellipsoid(
    "TEAMON_PalmShell",
    (4.62, 2.24, 2.38),
    (1.44, 1.02, 0.67),
    white,
    output,
    rotation=(math.radians(-6.0), math.radians(9.0), math.radians(-17.0)),
    segments=36,
)
parent_keep_world(palm, hand_root)
dorsal = ellipsoid(
    "TEAMON_PalmDorsalShell",
    (4.43, 2.08, 2.78),
    (1.08, 0.79, 0.24),
    white,
    output,
    rotation=(math.radians(-7.0), math.radians(8.0), math.radians(-17.0)),
    segments=32,
)
parent_keep_world(dorsal, hand_root)
thenar = ellipsoid(
    "TEAMON_ThenarShell",
    (4.35, 1.47, 2.03),
    (0.84, 0.68, 0.50),
    white,
    output,
    rotation=(math.radians(-18.0), math.radians(15.0), math.radians(-28.0)),
    segments=32,
)
parent_keep_world(thenar, hand_root)

# Wrist leaves the frame and overlaps the palm deeply, avoiding a detached joint.
wrist = capsule_between(
    "TEAMON_WristCuff",
    (5.25, 2.60, 2.42),
    (7.15, 3.63, 2.32),
    1.72,
    1.14,
    white,
    output,
    overlap=0.28,
)
parent_keep_world(wrist, hand_root)
wrist_band = joint_pin(
    "TEAMON_WristInsetBand",
    (5.70, 2.85, 2.39),
    radius=0.60,
    depth=0.20,
    material=seam_material,
    collection=output,
    rotation=(math.radians(62.0), math.radians(8.0), math.radians(-24.0)),
)
parent_keep_world(wrist_band, hand_root)

# Points are root -> PIP -> DIP -> tip. Roots extend into the palm shell.
finger_specs = {
    "Index": {
        "points": [(3.96, 1.32, 2.34), (3.10, 0.82, 2.02), (2.23, 0.31, 1.58), (1.38, -0.02, 1.30)],
        "widths": (0.62, 0.52, 0.43),
        "heights": (0.50, 0.43, 0.35),
        "press": True,
    },
    "Middle": {
        "points": [(4.22, 1.60, 2.61), (3.48, 1.08, 2.78), (2.89, 0.66, 2.55), (2.55, 0.39, 2.17)],
        "widths": (0.64, 0.53, 0.43),
        "heights": (0.51, 0.43, 0.35),
        "press": False,
    },
    "Ring": {
        "points": [(4.50, 1.88, 2.67), (3.86, 1.38, 2.88), (3.38, 0.99, 2.66), (3.12, 0.76, 2.30)],
        "widths": (0.60, 0.50, 0.40),
        "heights": (0.48, 0.40, 0.33),
        "press": False,
    },
    "Pinky": {
        "points": [(4.76, 2.15, 2.60), (4.24, 1.77, 2.78), (3.85, 1.46, 2.57), (3.65, 1.27, 2.25)],
        "widths": (0.53, 0.44, 0.35),
        "heights": (0.43, 0.36, 0.29),
        "press": False,
    },
}

hand_parts = [palm, dorsal, thenar, wrist, wrist_band]
for finger_name, spec in finger_specs.items():
    hand_parts.extend(
        build_finger(
            finger_name,
            spec["points"],
            spec["widths"],
            spec["heights"],
            white,
            joint_material,
            output,
            source,
            hand_root,
            press_group if spec["press"] else None,
        )
    )

# Broad two-link thumb grows from the thenar mass and curls below the palm.
thumb_points = [(4.48, 1.56, 2.02), (3.87, 0.95, 1.72), (3.15, 0.49, 1.62)]
guide_curve("TEAMON_Thumb_Guide", thumb_points, source)
thumb_proximal = capsule_between("TEAMON_Thumb_Proximal_Shell", thumb_points[0], thumb_points[1], 0.70, 0.55, white, output, overlap=0.16)
thumb_distal = capsule_between("TEAMON_Thumb_Distal_Shell", thumb_points[1], thumb_points[2], 0.58, 0.46, white, output, overlap=0.14)
thumb_pin = joint_pin("TEAMON_Thumb_JointPin_01", thumb_points[1], 0.16, 0.34, joint_material, output)
thumb_tip = ellipsoid("TEAMON_Thumb_TipPad", (3.05, 0.43, 1.59), (0.38, 0.31, 0.24), white, output, segments=28)
for part in (thumb_proximal, thumb_distal, thumb_pin, thumb_tip):
    parent_keep_world(part, hand_root)
    hand_parts.append(part)

# Small integrated knuckle ridges; they overlap the palm and do not create red gaps.
for index, location in enumerate(((3.95, 1.48, 2.71), (4.20, 1.72, 2.82), (4.46, 1.96, 2.82), (4.70, 2.18, 2.72)), start=1):
    ridge = ellipsoid(
        f"TEAMON_KnuckleRidge_{index:02d}",
        location,
        (0.38 - index * 0.018, 0.31, 0.15),
        white,
        output,
        rotation=(math.radians(-8.0), math.radians(8.0), math.radians(-18.0)),
        segments=24,
    )
    parent_keep_world(ridge, hand_root)
    hand_parts.append(ridge)

# Reduce the large disk reflection on the keycap without altering the interactive model.
fill_light = bpy.data.objects.get("TEAMON_Fill_Light")
if fill_light is not None and fill_light.type == "LIGHT":
    fill_light.data.energy = 340.0
    fill_light.data.size = 8.0

camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON camera is missing")
camera.location = (10.80, -12.20, 9.30)
camera.data.lens = 68
look_at(camera, (1.08, 0.34, 1.15))
scene.camera = camera

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens

camera.location = (8.9, -5.9, 4.35)
camera.data.lens = 72
look_at(camera, (2.0, 0.85, 1.55))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)

camera.location = (3.1, 0.2, 13.2)
camera.data.lens = 72
look_at(camera, (1.4, 0.65, 1.15))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)

camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v3 clay hand",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "exported_glb": False,
    "hand_part_count": len(hand_parts),
    "index_contact_target": [1.38, -0.02, 1.10],
    "keycap_top_z": 1.10,
    "shape_gate": [
        "continuous silhouette",
        "no fully exposed ball joints",
        "unequal fingers",
        "dominant palm mass",
        "index contact without red gap",
    ],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
