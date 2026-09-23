import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v7_orca_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v7_orca_hand.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v7_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v7_structural_qa.json"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v7-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v7-pressed.png"

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
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_root = bpy.data.objects["TEAMON_ButtonRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
hand_root = bpy.data.objects["TEAMON_AbilityHandRoot"]
cuff = bpy.data.objects["TEAMON_ORCA_CuffShell"]
wrist = bpy.data.objects["TEAMON_ORCA_right_R-Carpals_8d1f1041"]
keycap = bpy.data.objects["TEAMON_Keycap"]
text = bpy.data.objects["TEAMON_Text"]
index_skin = next(
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("orca_mesh") == "right_I-FingerTipAssembly_I-DP-Skin"
)
if cuff.parent != hand_root:
    raise RuntimeError("TEAMON v7 cuff must be a descendant of TEAMON_AbilityHandRoot")

# Present the dorsal shell to the camera and keep the fingertip contact fixed.
index_bounds = bounds(index_skin)
pivot = Vector(
    (
        (index_bounds["min"][0] + index_bounds["max"][0]) * 0.5,
        (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5,
        index_bounds["min"][2],
    )
)
axis = (pivot - wrist.matrix_world.translation).normalized()
roll_degrees = 0.0
rotation = Quaternion(axis, math.radians(roll_degrees)).to_matrix().to_4x4()
around_contact = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)
hand_root.matrix_world = around_contact @ hand_root.matrix_world

# Re-seat the newly rotated fingertip on the acrylic instead of allowing an
# axis-aligned-bounds change to push it through the cap.
bpy.context.view_layer.update()
contact_correction = bounds(keycap)["max"][2] + 0.004 - bounds(index_skin)["min"][2]
hand_root.location.z += contact_correction

bpy.context.view_layer.update()

for obj in (button_group, hand_root):
    obj.animation_data_clear()

rest_button_location = button_group.location.copy()
rest_hand_location = hand_root.location.copy()
press_travel = 0.080
scene.frame_start = 1
scene.frame_end = 24
scene.render.fps = 30

scene.frame_set(1)
button_group.location = rest_button_location
hand_root.location = rest_hand_location
button_group.keyframe_insert(data_path="location", frame=1)
hand_root.keyframe_insert(data_path="location", frame=1)

scene.frame_set(24)
button_group.location = rest_button_location + Vector((0.0, 0.0, -press_travel))
hand_root.location = rest_hand_location + Vector((0.0, 0.0, -press_travel))
button_group.keyframe_insert(data_path="location", frame=24)
hand_root.keyframe_insert(data_path="location", frame=24)

button_action = button_group.animation_data.action
hand_action = hand_root.animation_data.action
button_action.name = "TEAMON_PressGroup"
hand_action.name = "TEAMON_HandPressGroup"
for action in (button_action, hand_action):
    if getattr(action, "fcurves", None):
        for curve in action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

scene.frame_set(1)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)
rest_gap = bounds(index_skin)["min"][2] - bounds(keycap)["max"][2]
rest_cuff_location = cuff.matrix_world.translation.copy()

scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_gap = bounds(index_skin)["min"][2] - bounds(keycap)["max"][2]
pressed_cuff_location = cuff.matrix_world.translation.copy()
cuff_press_travel = (pressed_cuff_location - rest_cuff_location).length

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
            "TEAMON_AbilityHandRoot",
        }
        or obj.name.startswith("TEAMON_ORCA_")
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

export_meshes = [obj for obj in export_objects if obj.type == "MESH"]
for obj in export_meshes:
    obj.data.validate(verbose=False, clean_customdata=True)
total_triangles = triangle_count(export_objects)
if total_triangles > 220000:
    raise RuntimeError(f"TEAMON v7 exceeds the 220k hero web triangle budget: {total_triangles}")

qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in export_meshes],
    contact_tolerance=0.015,
    floating_tolerance=0.035,
)
qa["expected_contacts"] = {
    "rest_index_to_keycap_gap": rest_gap,
    "pressed_index_to_keycap_gap": pressed_gap,
    "tolerance": 0.015,
    "rest_pass": abs(rest_gap) <= 0.015,
    "pressed_pass": abs(pressed_gap) <= 0.015,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
if qa["errors"]:
    raise RuntimeError(f"TEAMON v7 structural QA errors: {qa['errors']}")
if not qa["expected_contacts"]["rest_pass"] or not qa["expected_contacts"]["pressed_pass"]:
    raise RuntimeError(f"TEAMON v7 contact QA failed: {qa['expected_contacts']}")
if abs(cuff_press_travel - press_travel) > 0.001:
    raise RuntimeError(f"TEAMON v7 cuff press travel mismatch: {cuff_press_travel}")

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
    export_animation_mode="ACTIONS",
    export_frame_range=True,
    export_force_sampling=True,
)

report = {
    "asset": "TEAMON reference v7 ORCA hand with tapered cuff",
    "stage": "EXPORT_QA",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "hand_roll_degrees": roll_degrees,
    "press_travel": press_travel,
    "rest_contact_gap": rest_gap,
    "pressed_contact_gap": pressed_gap,
    "rest_contact_pass": abs(rest_gap) <= 0.015,
    "pressed_contact_pass": abs(pressed_gap) <= 0.015,
    "cuff_parent": cuff.parent.name,
    "cuff_press_travel": cuff_press_travel,
    "cuff_press_pass": abs(cuff_press_travel - press_travel) <= 0.001,
    "export_object_count": len(export_objects),
    "export_mesh_count": len(export_meshes),
    "triangle_count": total_triangles,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "animation_clips": ["TEAMON_PressGroup", "TEAMON_HandPressGroup"],
    "hand_source": "https://github.com/orcahand/orcahand_description",
    "hand_revision": "b9b349a21ee0238c62b6cf92ae7597027867adf8",
    "hand_license": "MIT",
    "status": "glb_requires_target_viewer_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
