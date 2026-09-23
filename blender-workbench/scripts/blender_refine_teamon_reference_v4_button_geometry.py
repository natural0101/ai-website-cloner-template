import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_button_refined.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_button_refined_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-button-refined-hero.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-button-refined-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def move_to_collection(obj, collection):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def rounded_box(name, dimensions, location, radius, material, collection, parent, segments=12):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.48)
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    apply_material(obj, material)
    move_to_collection(obj, collection)
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    obj["export"] = True
    return obj


def create_text(name, body, location, material, collection, parent):
    curve = bpy.data.curves.new(name=f"{name}_Curve", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 1.0
    curve.extrude = 0.042
    curve.bevel_depth = 0.006
    curve.bevel_resolution = 3
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    curve.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()
    scale = 3.20 / max(obj.dimensions.x, 0.001)
    obj.scale = (scale, scale, scale)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world
    obj["export"] = True
    return obj


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


output = bpy.data.collections.get("TEAMON_OUTPUT")
button_root = bpy.data.objects.get("TEAMON_ButtonRoot")
press_group = bpy.data.objects.get("TEAMON_PressGroup")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
camera = bpy.data.objects.get("TEAMON_Camera")
if None in (output, button_root, press_group, hand_root, camera):
    raise RuntimeError("TEAMON v4 composition checkpoint is incomplete")

materials = {
    "black": bpy.data.materials.get("TEAMON_Black_Monolith"),
    "recess": bpy.data.materials.get("TEAMON_Recess_Black"),
    "gradient": bpy.data.materials.get("TEAMON_RGB_Continuous_Gradient"),
    "acrylic": bpy.data.materials.get("TEAMON_Clear_Acrylic"),
    "text": bpy.data.materials.get("TEAMON_Text_White"),
}
if any(value is None for value in materials.values()):
    raise RuntimeError("TEAMON v4 materials are incomplete")

for name in ("TEAMON_Base", "TEAMON_Recess", "TEAMON_RGB_Underplate", "TEAMON_Keycap", "TEAMON_Text"):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)

base = rounded_box("TEAMON_Base", (6.10, 4.35, 0.86), (0.0, 0.0, 0.43), 0.32, materials["black"], output, button_root, 14)
recess = rounded_box("TEAMON_Recess", (5.56, 3.81, 0.12), (0.0, 0.0, 0.82), 0.20, materials["recess"], output, button_root, 10)
underplate = rounded_box("TEAMON_RGB_Underplate", (5.24, 3.50, 0.07), (0.0, 0.0, 0.89), 0.20, materials["gradient"], output, press_group, 10)
keycap = rounded_box("TEAMON_Keycap", (5.32, 3.58, 0.56), (0.0, 0.0, 1.12), 0.27, materials["acrylic"], output, press_group, 16)
text = create_text("TEAMON_Text", "TEAMON", (-0.08, -0.02, 1.412), materials["text"], output, press_group)
press_group["press_travel"] = 0.08

bpy.context.view_layer.update()
index_mesh = next(
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("mjcf_body") == "rh_ffdistal" and not obj.hide_render
)
key_top = bounds(keycap)["max"][2]
index_bottom = bounds(index_mesh)["min"][2]
hand_root.location.z += key_top + 0.004 - index_bottom
bpy.context.view_layer.update()

camera.location = (11.4, -13.2, 11.2)
camera.data.lens = 70
look_at(camera, (0.64, 0.08, 1.00))

scene = bpy.context.scene
scene.render.resolution_x = 768
scene.render.resolution_y = 432
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens
camera.location = (0.0, -0.5, 15.4)
camera.data.lens = 68
look_at(camera, (0.35, 0.0, 0.9))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens

report = {
    "asset": "TEAMON reference v4 refined button geometry",
    "stage": "GEOMETRY",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(TOP_PATH)],
    "dimensions": {
        "base": list(base.dimensions),
        "recess": list(recess.dimensions),
        "keycap": list(keycap.dimensions),
        "text": list(text.dimensions),
    },
    "press_travel": press_group["press_travel"],
    "rest_contact_gap": bounds(index_mesh)["min"][2] - bounds(keycap)["max"][2],
    "exported_glb": False,
    "status": "button_geometry_visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
