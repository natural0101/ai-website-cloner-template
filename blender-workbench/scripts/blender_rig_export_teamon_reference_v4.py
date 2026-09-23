import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v4_shadow_hand.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_rig_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_structural_qa.json"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-rig-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-rig-pressed.png"

for path in (BLEND_PATH, GLB_PATH, REPORT_PATH, QA_PATH, REST_PATH, PRESSED_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


def triangle_count(objects):
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            obj.data.calc_loop_triangles()
            total += len(obj.data.loop_triangles)
    return total


scene = bpy.context.scene
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
button_root = bpy.data.objects.get("TEAMON_ButtonRoot")
button_group = bpy.data.objects.get("TEAMON_PressGroup")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
distal_body = bpy.data.objects.get("TEAMON_SH_rh_ffdistal")
keycap = bpy.data.objects.get("TEAMON_Keycap")
underplate = bpy.data.objects.get("TEAMON_RGB_Underplate")
index_mesh = next(
    (
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.get("mjcf_body") == "rh_ffdistal" and not obj.hide_render
    ),
    None,
)
if None in (composition_root, button_root, button_group, hand_root, distal_body, keycap, underplate, index_mesh):
    raise RuntimeError("TEAMON v4 lighting checkpoint lacks required rig objects")

# LEDs are fixed in the housing. Only the acrylic key and lettering travel;
# otherwise the luminous plate sinks below the black recess during a press.
underplate_world = underplate.matrix_world.copy()
underplate.parent = button_root
underplate.matrix_world = underplate_world
underplate["interaction"] = "fixed_rgb_light_source"

# The upstream OBJ contains one zero-area face in the little-finger
# metacarpal. Preserve vendor files unchanged and repair only the Blender
# export copy so structural QA and glTF topology are clean.
little_metacarpal = next(
    (
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.get("mjcf_body") == "rh_lfmetacarpal" and not obj.hide_render
    ),
    None,
)
if little_metacarpal is None:
    raise RuntimeError("Shadow Hand little-finger metacarpal is missing")
little_metacarpal.data = little_metacarpal.data.copy()
bm = bmesh.new()
bm.from_mesh(little_metacarpal.data)
degenerate_faces = [face for face in bm.faces if face.calc_area() <= 1e-12]
if degenerate_faces:
    bmesh.ops.delete(bm, geom=degenerate_faces, context="FACES")
bm.to_mesh(little_metacarpal.data)
bm.free()
little_metacarpal.data.update()
little_metacarpal["source_mesh_repair"] = f"removed {len(degenerate_faces)} zero-area face(s)"

# Dedicated press pivot at the official distal joint. Reparenting preserves the
# visual mesh and keeps the imported MJCF hierarchy intact.
hand_press = bpy.data.objects.get("TEAMON_HandPressGroup")
if hand_press is None:
    hand_press = bpy.data.objects.new("TEAMON_HandPressGroup", None)
    bpy.data.collections["TEAMON_OUTPUT"].objects.link(hand_press)
hand_press.parent = distal_body
hand_press.matrix_local = Matrix.Identity(4)
mesh_local = index_mesh.matrix_local.copy()
index_mesh.parent = hand_press
index_mesh.matrix_local = mesh_local
hand_press.rotation_mode = "QUATERNION"
hand_press.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
bpy.context.view_layer.update()

rest_button_location = button_group.location.copy()
rest_hand_quaternion = hand_press.rotation_quaternion.copy()
rest_key_top = bounds(keycap)["max"][2]
rest_tip_bottom = bounds(index_mesh)["min"][2]
press_travel = float(button_group.get("press_travel", 0.08))
pressed_key_top = rest_key_top - press_travel


def tip_bottom_at(angle):
    hand_press.rotation_quaternion = Quaternion((1.0, 0.0, 0.0), angle)
    bpy.context.view_layer.update()
    return bounds(index_mesh)["min"][2]


positive = tip_bottom_at(math.radians(32.0))
negative = tip_bottom_at(math.radians(-32.0))
sign = 1.0 if positive < negative else -1.0
best_at_limit = min(positive, negative)
if best_at_limit > pressed_key_top + 0.005:
    raise RuntimeError(
        f"Distal joint cannot reach pressed key: limit bottom={best_at_limit:.6f}, target={pressed_key_top:.6f}"
    )

low = 0.0
high = math.radians(32.0)
for _ in range(30):
    mid = (low + high) * 0.5
    bottom = tip_bottom_at(sign * mid)
    if bottom > pressed_key_top:
        low = mid
    else:
        high = mid
press_angle = sign * (low + high) * 0.5
pressed_tip_bottom = tip_bottom_at(press_angle)
pressed_hand_quaternion = hand_press.rotation_quaternion.copy()

for obj in (button_group, hand_press):
    obj.animation_data_clear()

scene.frame_start = 1
scene.frame_end = 24
scene.render.fps = 30

scene.frame_set(1)
button_group.location = rest_button_location
hand_press.rotation_quaternion = rest_hand_quaternion
button_group.keyframe_insert(data_path="location", frame=1)
hand_press.keyframe_insert(data_path="rotation_quaternion", frame=1)

scene.frame_set(24)
button_group.location = rest_button_location + Vector((0.0, 0.0, -press_travel))
hand_press.rotation_quaternion = pressed_hand_quaternion
button_group.keyframe_insert(data_path="location", frame=24)
hand_press.keyframe_insert(data_path="rotation_quaternion", frame=24)

if button_group.animation_data and button_group.animation_data.action:
    button_group.animation_data.action.name = "TEAMON_PressGroup"
if hand_press.animation_data and hand_press.animation_data.action:
    hand_press.animation_data.action.name = "TEAMON_HandPressGroup"

for obj in (button_group, hand_press):
    action = obj.animation_data.action if obj.animation_data else None
    if action and getattr(action, "fcurves", None):
        for curve in action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"

scene.render.resolution_x = 768
scene.render.resolution_y = 432
scene.render.resolution_percentage = 100
scene.frame_set(1)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)
rest_gap = bounds(index_mesh)["min"][2] - bounds(keycap)["max"][2]
scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_gap = bounds(index_mesh)["min"][2] - bounds(keycap)["max"][2]

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = []
for obj in bpy.data.objects:
    include_empty = obj.type == "EMPTY" and (
        obj.name in {
            "TEAMON_CompositionRoot",
            "TEAMON_ButtonRoot",
            "TEAMON_PressGroup",
            "TEAMON_HandRoot",
            "TEAMON_HandPressGroup",
        }
        or obj.name.startswith("TEAMON_SH_")
    )
    include_mesh = (
        obj.type == "MESH"
        and obj.name.startswith("TEAMON_")
        and not obj.name.startswith("TEAMON_SOURCE_")
        and obj.name != "TEAMON_Studio_Floor"
        and not obj.hide_render
        and obj.get("export", True)
    )
    if include_empty or include_mesh:
        obj.hide_set(False)
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

# Run the v4 read-only structural audit on exactly the visible export meshes.
qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

export_mesh_names = [obj.name for obj in export_objects if obj.type == "MESH"]
qa = scene_qa.audit_scene(object_names=export_mesh_names, contact_tolerance=0.015, floating_tolerance=0.035)
qa["expected_contacts"] = {
    "rest_index_to_keycap_gap": rest_gap,
    "pressed_index_to_keycap_gap": pressed_gap,
    "tolerance": 0.015,
    "rest_pass": abs(rest_gap) <= 0.015,
    "pressed_pass": abs(pressed_gap) <= 0.015,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")

report = {
    "asset": "TEAMON reference v4 rigged Shadow Hand export",
    "stage": "EXPORT_QA",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "press_travel": press_travel,
    "press_angle_degrees": math.degrees(press_angle),
    "rest_contact_gap": rest_gap,
    "pressed_contact_gap": pressed_gap,
    "rest_contact_pass": abs(rest_gap) <= 0.015,
    "pressed_contact_pass": abs(pressed_gap) <= 0.015,
    "export_object_count": len(export_objects),
    "export_mesh_count": len(export_mesh_names),
    "triangle_count": triangle_count(export_objects),
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "source_mesh_repair": little_metacarpal["source_mesh_repair"],
    "animation_objects": ["TEAMON_PressGroup", "TEAMON_HandPressGroup"],
    "exported_glb": True,
    "status": "glb_requires_target_viewer_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
