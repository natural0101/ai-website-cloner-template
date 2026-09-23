import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v3.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_rig_export_report.json"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-rig-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-rig-pressed.png"

for path in (BLEND_PATH, GLB_PATH, REPORT_PATH, REST_PATH, PRESSED_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min_z": min(point.z for point in corners),
        "max_z": max(point.z for point in corners),
    }


def linearize(obj):
    action = obj.animation_data.action if obj.animation_data else None
    if action is None:
        return
    curves = getattr(action, "fcurves", None)
    if curves is None:
        return
    for curve in curves:
        for point in curve.keyframe_points:
            point.interpolation = "LINEAR"


scene = bpy.context.scene
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
button_group = bpy.data.objects.get("TEAMON_PressGroup")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
hand_group = bpy.data.objects.get("TEAMON_HandPressGroup")
keycap = bpy.data.objects.get("TEAMON_Keycap")
pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
dip_pin = bpy.data.objects.get("TEAMON_Index_RecessedPin_02")
if None in (composition_root, button_group, hand_root, hand_group, keycap, pad, dip_pin):
    raise RuntimeError("TEAMON LOD checkpoint lacks required rig objects")

# Put the distal pivot at the actual DIP joint while preserving child world
# transforms. The previous world-origin empty could only tear the finger.
child_world = {child.name: child.matrix_world.copy() for child in hand_group.children}
pivot_world = dip_pin.matrix_world.translation.copy()
hand_group.matrix_world = Matrix.Translation(pivot_world)
for child in hand_group.children:
    child.matrix_world = child_world[child.name]
hand_group.rotation_mode = "QUATERNION"
hand_group.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
bpy.context.view_layer.update()

rest_button_location = button_group.location.copy()
rest_hand_quaternion = hand_group.rotation_quaternion.copy()
rest_key_top = world_bounds(keycap)["max_z"]
rest_pad_bottom = world_bounds(pad)["min_z"]
press_travel = 0.12
pressed_key_top = rest_key_top - press_travel

# Solve the DIP rotation numerically so the broad pad follows the depressed key
# surface. Choose the sign that actually moves the pad downward.
pad_center = pad.matrix_world.translation.copy()
distal_direction = (pad_center - pivot_world).normalized()
axis = distal_direction.cross(Vector((0.0, 0.0, -1.0)))
if axis.length < 1e-5:
    axis = Vector((0.0, 1.0, 0.0))
axis.normalize()


def pad_bottom_at(angle):
    hand_group.rotation_quaternion = Quaternion(axis, angle)
    bpy.context.view_layer.update()
    return world_bounds(pad)["min_z"]


positive_bottom = pad_bottom_at(math.radians(24.0))
negative_bottom = pad_bottom_at(math.radians(-24.0))
sign = 1.0 if positive_bottom < negative_bottom else -1.0
low = 0.0
high = math.radians(24.0)
for _ in range(28):
    mid = (low + high) * 0.5
    bottom = pad_bottom_at(sign * mid)
    if bottom > pressed_key_top:
        low = mid
    else:
        high = mid
press_angle = sign * (low + high) * 0.5
pressed_pad_bottom = pad_bottom_at(press_angle)
pressed_hand_quaternion = hand_group.rotation_quaternion.copy()

# Author two exact poses. Web scrubs this clip with its own spring progress.
for obj in (button_group, hand_group):
    obj.animation_data_clear()
scene.frame_start = 1
scene.frame_end = 30
scene.render.fps = 30

scene.frame_set(1)
button_group.location = rest_button_location
hand_group.rotation_quaternion = rest_hand_quaternion
button_group.keyframe_insert(data_path="location", frame=1)
hand_group.keyframe_insert(data_path="rotation_quaternion", frame=1)

scene.frame_set(30)
button_group.location = rest_button_location + Vector((0.0, 0.0, -press_travel))
hand_group.rotation_quaternion = pressed_hand_quaternion
button_group.keyframe_insert(data_path="location", frame=30)
hand_group.keyframe_insert(data_path="rotation_quaternion", frame=30)
if button_group.animation_data and button_group.animation_data.action:
    button_group.animation_data.action.name = "TEAMON_Press_Button"
if hand_group.animation_data and hand_group.animation_data.action:
    hand_group.animation_data.action.name = "TEAMON_Press_Hand"
linearize(button_group)
linearize(hand_group)

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.frame_set(1)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)
scene.frame_set(30)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

# Export only accepted visible asset nodes. SOURCE/STUDIO/camera/lights and all
# rejected hidden iterations are excluded regardless of collection ancestry.
bpy.ops.object.select_all(action="DESELECT")
export_objects = []
for obj in bpy.data.objects:
    include_empty = obj in (composition_root, bpy.data.objects.get("TEAMON_ButtonRoot"), hand_root, button_group, hand_group)
    include_mesh = (
        obj.type == "MESH"
        and not obj.hide_render
        and obj.get("export", True)
        and obj.name.startswith("TEAMON_")
        and obj.name != "TEAMON_Studio_Floor"
    )
    if include_empty or include_mesh:
        obj.select_set(True)
        export_objects.append(obj)

bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=False,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
    export_extras=True,
    export_animations=True,
    export_animation_mode="SCENE",
    export_nla_strips_merged_animation_name="TEAMON_Press",
    export_frame_range=True,
    export_force_sampling=True,
)

report = {
    "asset": "TEAMON reference v3 rigged export",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "pivot_world": list(pivot_world),
    "press_axis": list(axis),
    "press_angle_degrees": math.degrees(press_angle),
    "press_travel": press_travel,
    "rest_contact_gap": rest_pad_bottom - rest_key_top,
    "pressed_contact_gap": pressed_pad_bottom - pressed_key_top,
    "export_object_count": len(export_objects),
    "animation_name": "TEAMON_Press",
    "exported_glb": True,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
