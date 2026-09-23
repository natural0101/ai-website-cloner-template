import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v10_rebelia_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v10_rebelia_hand.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v10_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v10_structural_qa.json"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v10-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v10-pressed.png"

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


def move_to_collection(obj, collection):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def make_knuckle(name, location, scale, hand_root, output, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.012)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, output)
    obj.parent = hand_root
    obj.matrix_local = Matrix.Translation(Vector(location)) @ Matrix.Diagonal((*scale, 1.0))
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["export"] = True
    obj["source"] = "editable knuckle bridge over Rebelia full-finger root"
    return obj


scene = bpy.context.scene
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_root = bpy.data.objects["TEAMON_ButtonRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
hand_root = bpy.data.objects["TEAMON_RebeliaHandRoot"]
output = bpy.data.collections["TEAMON_OUTPUT"]
keycap = bpy.data.objects["TEAMON_Keycap"]
text = bpy.data.objects["TEAMON_Text"]
white = bpy.data.materials["TEAMON_Robot_White"]
index = bpy.data.objects["TEAMON_Rebelia_03 FlexMods V6 (3DP)"]
cuff = bpy.data.objects["TEAMON_Rebelia_Cover Down V2"]

# The source upper thumb points through the table in the reference camera.
# Keep its original smooth Rebelia base as the visible thenar bridge, but replace
# the upper segment with a shortened complete pre-flexed Rebelia finger.
source_thumb_upper = bpy.data.objects.get("TEAMON_Rebelia_ThumbUpper - FlexMods (3DP)")
if source_thumb_upper is not None:
    bpy.data.objects.remove(source_thumb_upper, do_unlink=True)

finger_names = (
    "TEAMON_Rebelia_Middle_FullFinger",
    "TEAMON_Rebelia_Ring_FullFinger",
    "TEAMON_Rebelia_Little_FullFinger",
)
fingers = [bpy.data.objects[name] for name in finger_names]
factors = (0.76, 0.70, 0.64)
offsets = ((0.000, -0.035), (-0.012, -0.047), (-0.024, -0.059))
for obj, factor, (offset_x, offset_y) in zip(fingers, factors, offsets):
    obj.location.x += offset_x
    obj.location.y += offset_y
    obj.location.z -= 0.057 * (1.0 - factor)
    obj.scale.y *= factor
    obj["pose_role"] = "pre-flexed non-contact finger"

middle = fingers[0]
thumb = bpy.data.objects.new("TEAMON_Rebelia_Thumb_FullFinger", middle.data)
output.objects.link(thumb)
thumb.parent = hand_root
thumb.matrix_local = middle.matrix_local.copy()
thumb.scale.x *= 0.92
thumb.scale.y *= 0.62
thumb.scale.z *= 0.92
thumb.location += Vector((0.040, -0.020, -0.060))
thumb["rebelia_source_object"] = "03 FlexMods V6 (3DP) PF"
thumb["pose_role"] = "shortened angled thumb"
thumb["export"] = True

text.rotation_euler.z = math.radians(90.0)
bpy.context.view_layer.update()

# The production CAD contains zero-area construction remnants after web
# decimation. Remove only those degenerates; preserve the visible shell shape.
cleaned_meshes = set()
for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.startswith("TEAMON_Rebelia_") or obj.data in cleaned_meshes:
        continue
    mesh = obj.data
    editable = bmesh.new()
    editable.from_mesh(mesh)
    bmesh.ops.dissolve_degenerate(editable, dist=1e-6, edges=list(editable.edges))
    editable.to_mesh(mesh)
    editable.free()
    mesh.validate(verbose=False, clean_customdata=True)
    mesh.update()
    cleaned_meshes.add(mesh)

# Re-seat the index after all visual adjustments.
contact_correction = bounds(keycap)["max"][2] + 0.004 - bounds(index)["min"][2]
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
rest_gap = bounds(index)["min"][2] - bounds(keycap)["max"][2]
rest_cuff_location = cuff.matrix_world.translation.copy()

scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_gap = bounds(index)["min"][2] - bounds(keycap)["max"][2]
pressed_cuff_location = cuff.matrix_world.translation.copy()
cuff_press_travel = (pressed_cuff_location - rest_cuff_location).length

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = []
for obj in bpy.data.objects:
    include_empty = obj.type == "EMPTY" and obj.name in {
        "TEAMON_CompositionRoot",
        "TEAMON_ButtonRoot",
        "TEAMON_PressGroup",
        "TEAMON_RebeliaHandRoot",
    }
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
if total_triangles > 430000:
    raise RuntimeError(f"TEAMON v10 exceeds the 430k hero web triangle budget: {total_triangles}")

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
    raise RuntimeError(f"TEAMON v10 structural QA errors: {qa['errors']}")
if not qa["expected_contacts"]["rest_pass"] or not qa["expected_contacts"]["pressed_pass"]:
    raise RuntimeError(f"TEAMON v10 contact QA failed: {qa['expected_contacts']}")
if abs(cuff_press_travel - press_travel) > 0.001:
    raise RuntimeError(f"TEAMON v10 cuff press travel mismatch: {cuff_press_travel}")

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
    "asset": "TEAMON reference v10 Rebelia full-finger hand",
    "stage": "EXPORT_QA",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
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
    "hand_source": "https://github.com/opsobot/rebelia",
    "hand_revision": "41f2708999a01f8dd815642889281cea8bb1c0e9",
    "hand_license": "CERN-OHL-S-2.0",
    "status": "glb_requires_target_viewer_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
