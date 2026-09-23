import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_continuous_hand.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_continuous_hand_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-continuous-hand-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-continuous-hand-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-continuous-hand-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def smooth_mesh(obj):
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def make_tapered_finger(name, points, radii, bevel_depth, material, collection, parent):
    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 5
    curve.resolution_u = 16
    curve.use_fill_caps = True
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bezier_point, coordinate, radius in zip(spline.bezier_points, points, radii, strict=True):
        bezier_point.co = coordinate
        bezier_point.radius = radius
        bezier_point.handle_left_type = "AUTO"
        bezier_point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    apply_material(obj, material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smooth_mesh(obj)
    parent_keep_world(obj, parent)
    return obj


def make_seam_ring(name, location, tangent, radius, material, collection, parent):
    bpy.ops.mesh.primitive_torus_add(
        align="WORLD",
        major_segments=32,
        minor_segments=8,
        location=location,
        major_radius=radius,
        minor_radius=radius * 0.105,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = Vector(tangent).normalized().to_track_quat("Z", "Y").to_euler()
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def ellipsoid(name, location, scale, material, collection, parent, rotation=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=16, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if rotation is not None:
        obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def capsule_plate(name, start, end, width, height, material, collection, parent):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    center = (a + b) * 0.5 + Vector((0.0, 0.0, height * 0.28))
    obj = ellipsoid(
        name,
        center,
        (direction.length * 0.47, width * 0.5, height * 0.5),
        material,
        collection,
        parent,
    )
    obj.rotation_euler = direction.normalized().to_track_quat("X", "Z").to_euler()
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
output = bpy.data.collections.get("TEAMON_OUTPUT")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
white = bpy.data.materials.get("TEAMON_Robot_White_V3")
joint_material = bpy.data.materials.get("TEAMON_Robot_Joint_Rose_V3")
if None in (output, hand_root, press_group, white, joint_material):
    raise RuntimeError("TEAMON v3 clay hand checkpoint is incomplete")

# Hide the rejected bead-like phalanges while preserving them as an editable source checkpoint.
finger_tokens = ("Index", "Middle", "Ring", "Pinky", "Thumb")
old_tokens = ("Proximal_Shell", "Middle_Shell", "Distal_Shell", "JointPin", "TipPad")
hidden = []
for obj in bpy.data.objects:
    if any(f"TEAMON_{finger}_" in obj.name for finger in finger_tokens) and any(token in obj.name for token in old_tokens):
        obj.hide_render = True
        obj.hide_viewport = True
        obj["remediation_status"] = "rejected_bead_shell_preserved_hidden"
        hidden.append(obj.name)

finger_specs = {
    "Index": {
        "points": [(4.02, 1.34, 2.34), (3.20, 0.90, 2.01), (2.48, 0.45, 1.59), (1.76, 0.10, 1.31)],
        "radii": (1.05, 0.95, 0.82, 0.70),
        "bevel": 0.31,
        "press": True,
    },
    "Middle": {
        "points": [(4.26, 1.60, 2.58), (3.58, 1.14, 2.75), (3.02, 0.73, 2.50), (2.70, 0.48, 2.16)],
        "radii": (1.03, 0.94, 0.82, 0.68),
        "bevel": 0.32,
        "press": False,
    },
    "Ring": {
        "points": [(4.51, 1.88, 2.64), (3.93, 1.42, 2.84), (3.47, 1.05, 2.61), (3.20, 0.80, 2.29)],
        "radii": (1.02, 0.92, 0.80, 0.66),
        "bevel": 0.30,
        "press": False,
    },
    "Pinky": {
        "points": [(4.76, 2.15, 2.57), (4.29, 1.80, 2.74), (3.91, 1.49, 2.54), (3.69, 1.29, 2.26)],
        "radii": (1.00, 0.90, 0.78, 0.64),
        "bevel": 0.265,
        "press": False,
    },
}

new_parts = []
for finger_name, spec in finger_specs.items():
    parent = press_group if spec["press"] else hand_root
    finger = make_tapered_finger(
        f"TEAMON_{finger_name}_ContinuousShell",
        spec["points"],
        spec["radii"],
        spec["bevel"],
        white,
        output,
        parent,
    )
    new_parts.append(finger.name)
    points = [Vector(point) for point in spec["points"]]
    for joint_index in (1, 2):
        tangent = points[min(joint_index + 1, 3)] - points[max(joint_index - 1, 0)]
        ring = make_seam_ring(
            f"TEAMON_{finger_name}_RecessedSeam_{joint_index:02d}",
            points[joint_index],
            tangent,
            spec["bevel"] * spec["radii"][joint_index] * 0.93,
            joint_material,
            output,
            hand_root,
        )
        new_parts.append(ring.name)
    # A low dorsal armor pad provides a robotic plane without breaking continuity.
    plate = capsule_plate(
        f"TEAMON_{finger_name}_DorsalArmor",
        spec["points"][0],
        spec["points"][1],
        spec["bevel"] * 1.64,
        spec["bevel"] * 0.42,
        white,
        output,
        hand_root,
    )
    new_parts.append(plate.name)

thumb_points = [(4.51, 1.58, 2.02), (3.92, 1.01, 1.74), (3.22, 0.55, 1.62)]
thumb = make_tapered_finger(
    "TEAMON_Thumb_ContinuousShell",
    thumb_points,
    (1.04, 0.90, 0.72),
    0.36,
    white,
    output,
    hand_root,
)
new_parts.append(thumb.name)
thumb_tangent = Vector(thumb_points[2]) - Vector(thumb_points[0])
thumb_ring = make_seam_ring(
    "TEAMON_Thumb_RecessedSeam_01",
    thumb_points[1],
    thumb_tangent,
    0.30,
    joint_material,
    output,
    hand_root,
)
new_parts.append(thumb_ring.name)

# Keep the TEAMON label clear of the contact pad.
text = bpy.data.objects.get("TEAMON_Text")
if text is not None:
    text.location.x -= 0.22

camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON camera is missing")
camera.location = (10.95, -12.35, 9.55)
camera.data.lens = 68
look_at(camera, (1.13, 0.37, 1.22))
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
    "asset": "TEAMON reference v3 continuous hand remediation",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "hidden_rejected_parts": hidden,
    "new_continuous_parts": new_parts,
    "exported_glb": False,
    "dominant_defects_targeted": [
        "bead-like disconnected phalanges",
        "oversized exposed joints",
        "index contact over TEAMON text",
    ],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
