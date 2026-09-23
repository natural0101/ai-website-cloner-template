import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_articulated_shells.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_articulated_shells_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-articulated-shells-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-articulated-shells-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-articulated-shells-top.png"

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


def ellipsoid_between(name, start, end, width, height, material, collection, parent, trim=0.04):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    distance = direction.length
    unit = direction.normalized()
    shell_a = a + unit * trim
    shell_b = b - unit * trim
    shell_direction = shell_b - shell_a
    center = (shell_a + shell_b) * 0.5
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=18, radius=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (shell_direction.length * 0.5, width * 0.5, height * 0.5)
    obj.rotation_euler = shell_direction.normalized().to_track_quat("X", "Z").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def tapered_tendon(name, points, radii, bevel_depth, material, collection, parent):
    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 4
    curve.use_fill_caps = True
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate, radius in zip(spline.bezier_points, points, radii, strict=True):
        point.co = coordinate
        point.radius = radius
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
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


def joint_pin(name, point, tangent, radius, depth, material, collection, parent):
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=radius, depth=depth, location=point)
    obj = bpy.context.object
    obj.name = name
    direction = Vector(tangent).normalized()
    # Pin axis crosses the finger and stays largely recessed in the shell gap.
    across = direction.cross(Vector((0.0, 0.0, 1.0)))
    if across.length < 0.05:
        across = Vector((0.0, 1.0, 0.0))
    obj.rotation_euler = across.normalized().to_track_quat("Z", "Y").to_euler()
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = radius * 0.18
    bevel.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def add_finger(name, points, widths, heights, white, inner, joint_material, collection, hand_root, press_group=None):
    parts = []
    tendon = tapered_tendon(
        f"TEAMON_{name}_InnerTendon",
        points,
        (1.0, 0.92, 0.82, 0.72),
        min(widths) * 0.33,
        inner,
        collection,
        hand_root,
    )
    parts.append(tendon)
    labels = ("Proximal", "Middle", "Distal")
    for index, label in enumerate(labels):
        shell = ellipsoid_between(
            f"TEAMON_{name}_{label}_Armor",
            points[index],
            points[index + 1],
            widths[index],
            heights[index],
            white,
            collection,
            press_group if press_group is not None and index == 2 else hand_root,
            trim=min(widths[index] * 0.105, 0.05),
        )
        parts.append(shell)
    vectors = [Vector(point) for point in points]
    for index in (1, 2):
        tangent = vectors[min(index + 1, 3)] - vectors[max(index - 1, 0)]
        pin = joint_pin(
            f"TEAMON_{name}_RecessedPin_{index:02d}",
            vectors[index],
            tangent,
            radius=widths[index - 1] * 0.19,
            depth=widths[index - 1] * 0.42,
            material=joint_material,
            collection=collection,
            parent=hand_root,
        )
        parts.append(pin)
    return parts


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
output = bpy.data.collections.get("TEAMON_OUTPUT")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
white = bpy.data.materials.get("TEAMON_Robot_White_V3")
joint_material = bpy.data.materials.get("TEAMON_Robot_Joint_Rose_V3")
inner = bpy.data.materials.get("TEAMON_Robot_Seam_V3")
if None in (output, hand_root, press_group, white, joint_material, inner):
    raise RuntimeError("TEAMON continuous hand checkpoint is incomplete")

# Preserve but hide the rubber-glove attempt.
hidden = []
for obj in bpy.data.objects:
    if obj.name.startswith("TEAMON_") and any(token in obj.name for token in ("ContinuousShell", "RecessedSeam", "DorsalArmor")):
        obj.hide_render = True
        obj.hide_viewport = True
        obj["remediation_status"] = "rejected_continuous_glove_preserved_hidden"
        hidden.append(obj.name)

finger_specs = {
    "Index": {
        "points": [(4.02, 1.34, 2.33), (3.13, 0.86, 1.98), (2.35, 0.42, 1.56), (1.66, 0.10, 1.245)],
        "widths": (0.52, 0.43, 0.34),
        "heights": (0.43, 0.36, 0.29),
        "press": True,
    },
    "Middle": {
        "points": [(4.27, 1.61, 2.58), (3.52, 1.10, 2.72), (2.94, 0.69, 2.46), (2.62, 0.44, 2.12)],
        "widths": (0.55, 0.45, 0.36),
        "heights": (0.45, 0.37, 0.30),
        "press": False,
    },
    "Ring": {
        "points": [(4.51, 1.88, 2.63), (3.88, 1.39, 2.81), (3.40, 1.01, 2.57), (3.13, 0.77, 2.25)],
        "widths": (0.52, 0.43, 0.34),
        "heights": (0.43, 0.35, 0.28),
        "press": False,
    },
    "Pinky": {
        "points": [(4.76, 2.14, 2.56), (4.25, 1.76, 2.71), (3.86, 1.45, 2.50), (3.64, 1.25, 2.21)],
        "widths": (0.46, 0.38, 0.30),
        "heights": (0.38, 0.31, 0.25),
        "press": False,
    },
}

new_parts = []
for finger_name, spec in finger_specs.items():
    parts = add_finger(
        finger_name,
        spec["points"],
        spec["widths"],
        spec["heights"],
        white,
        inner,
        joint_material,
        output,
        hand_root,
        press_group if spec["press"] else None,
    )
    new_parts.extend(part.name for part in parts)

thumb_points = [(4.50, 1.57, 2.00), (3.88, 0.98, 1.71), (3.18, 0.52, 1.59)]
thumb_parts = add_finger(
    "Thumb",
    thumb_points + [(2.96, 0.40, 1.55)],
    (0.60, 0.49, 0.38),
    (0.49, 0.40, 0.31),
    white,
    inner,
    joint_material,
    output,
    hand_root,
)
new_parts.extend(part.name for part in thumb_parts)

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
    "asset": "TEAMON reference v3 articulated shells",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "hidden_previous_parts": hidden,
    "new_articulated_parts": new_parts,
    "exported_glb": False,
    "contact": {"index_tip_z": 1.245, "keycap_top_z": 1.10, "distal_half_height": 0.145},
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
