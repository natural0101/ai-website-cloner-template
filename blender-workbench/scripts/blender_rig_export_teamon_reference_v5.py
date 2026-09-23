import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v5_orca_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v5_orca_hand.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_rig_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_structural_qa.json"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-rig-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-rig-pressed.png"

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
hand_root = bpy.data.objects.get("TEAMON_AbilityHandRoot")
distal_body = bpy.data.objects.get("TEAMON_ORCA_right_I-FingerTipAssembly_ec49c16c")
keycap = bpy.data.objects.get("TEAMON_Keycap")
index_skin = next(
    (
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.get("orca_mesh") == "right_I-FingerTipAssembly_I-DP-Skin"
    ),
    None,
)
if None in (composition_root, button_root, button_group, hand_root, distal_body, keycap, index_skin):
    raise RuntimeError("TEAMON v5 material checkpoint lacks required rig objects")

for obj in (button_group, hand_root, distal_body):
    obj.animation_data_clear()

rest_button_location = button_group.location.copy()
rest_hand_location = hand_root.location.copy()
rest_key_top = bounds(keycap)["max"][2]
rest_tip_bottom = bounds(index_skin)["min"][2]
press_travel = 0.080
press_angle = 0.0

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

if button_group.animation_data and button_group.animation_data.action:
    button_group.animation_data.action.name = "TEAMON_PressGroup"
if hand_root.animation_data and hand_root.animation_data.action:
    hand_root.animation_data.action.name = "TEAMON_HandPressGroup"

for obj in (button_group, hand_root):
    action = obj.animation_data.action if obj.animation_data else None
    if action and getattr(action, "fcurves", None):
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

scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_gap = bounds(index_skin)["min"][2] - bounds(keycap)["max"][2]

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = []
for obj in bpy.data.objects:
    include_empty = obj.type == "EMPTY" and (
        obj.name in {"TEAMON_CompositionRoot", "TEAMON_ButtonRoot", "TEAMON_PressGroup", "TEAMON_AbilityHandRoot"}
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
total_triangles = triangle_count(export_objects)
if total_triangles > 100000:
    raise RuntimeError(f"TEAMON v5 exceeds the 100k web triangle budget: {total_triangles}")

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
    raise RuntimeError(f"TEAMON v5 structural QA errors: {qa['errors']}")
if not qa["expected_contacts"]["rest_pass"] or not qa["expected_contacts"]["pressed_pass"]:
    raise RuntimeError(f"TEAMON v5 contact QA failed: {qa['expected_contacts']}")

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
    "asset": "TEAMON reference v5 rigged ORCA Hand export",
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
    "export_mesh_count": len(export_meshes),
    "triangle_count": total_triangles,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "animation_objects": ["TEAMON_PressGroup", "TEAMON_AbilityHandRoot"],
    "animation_clips": ["TEAMON_PressGroup", "TEAMON_HandPressGroup"],
    "hand_source": "https://github.com/orcahand/orcahand_description",
    "hand_revision": "b9b349a21ee0238c62b6cf92ae7597027867adf8",
    "hand_license": "MIT",
    "exported_glb": True,
    "status": "glb_requires_target_viewer_validation"
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
