import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_contact_camera.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_contact_camera_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-contact-camera-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-contact-camera-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-contact-camera-top.png"

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
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def add_tip_pad(name, center, direction, scale, material, collection, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=18, radius=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = Vector(direction).normalized().to_track_quat("X", "Z").to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
output = bpy.data.collections.get("TEAMON_OUTPUT")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
white = bpy.data.materials.get("TEAMON_Robot_White_V3")
if None in (output, hand_root, press_group, white):
    raise RuntimeError("TEAMON articulated-shell checkpoint is incomplete")

# Recess the hinge pins further so they read as crescents, not exposed cylinders.
pin_names = []
for obj in bpy.data.objects:
    if "_RecessedPin_" in obj.name:
        obj.scale *= 0.70
        pin_names.append(obj.name)

tip_specs = {
    "Index": {
        "center": (1.64, 0.09, 1.235),
        "direction": (-0.69, -0.32, -0.315),
        "scale": (0.235, 0.185, 0.135),
        "parent": press_group,
    },
    "Middle": {
        "center": (2.58, 0.41, 2.10),
        "direction": (-0.32, -0.25, -0.34),
        "scale": (0.225, 0.180, 0.145),
        "parent": hand_root,
    },
    "Ring": {
        "center": (3.09, 0.73, 2.23),
        "direction": (-0.27, -0.24, -0.32),
        "scale": (0.210, 0.170, 0.135),
        "parent": hand_root,
    },
    "Pinky": {
        "center": (3.61, 1.22, 2.19),
        "direction": (-0.22, -0.20, -0.29),
        "scale": (0.185, 0.150, 0.120),
        "parent": hand_root,
    },
    "Thumb": {
        "center": (2.93, 0.38, 1.54),
        "direction": (-0.22, -0.12, -0.04),
        "scale": (0.235, 0.195, 0.155),
        "parent": hand_root,
    },
}

tip_names = []
for finger_name, spec in tip_specs.items():
    tip = add_tip_pad(
        f"TEAMON_{finger_name}_ContactPad",
        spec["center"],
        spec["direction"],
        spec["scale"],
        white,
        output,
        spec["parent"],
    )
    tip_names.append(tip.name)

# Soften the acrylic highlight while retaining the continuous RGB surface.
acrylic = bpy.data.materials.get("TEAMON_Clear_Acrylic")
if acrylic is not None and acrylic.use_nodes:
    bsdf = acrylic.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Roughness"].default_value = 0.17
        bsdf.inputs["Coat Weight"].default_value = 0.16
        bsdf.inputs["Coat Roughness"].default_value = 0.16

key_light = bpy.data.objects.get("TEAMON_Key_Light")
if key_light is not None and key_light.type == "LIGHT":
    key_light.data.energy = 1120.0
    key_light.data.size = 6.8

camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON camera is missing")
camera.location = (9.98, -11.08, 8.72)
camera.data.lens = 68
look_at(camera, (1.10, 0.32, 0.88))
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

index_pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
index_bottom = index_pad.location.z - tip_specs["Index"]["scale"][2] if index_pad else None
report = {
    "asset": "TEAMON reference v3 contact and camera refinement",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "tip_pads": tip_names,
    "recessed_pins": pin_names,
    "index_pad_bottom_z": index_bottom,
    "keycap_top_z": 1.10,
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
