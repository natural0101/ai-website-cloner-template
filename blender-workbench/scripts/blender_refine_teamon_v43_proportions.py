from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v43_proportions.blend"
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
HERO_PATH = PREVIEW_ROOT / "teamon-v43-proportions-hero.png"
LEFT_PATH = PREVIEW_ROOT / "teamon-v43-proportions-left.png"
SIDE_PATH = PREVIEW_ROOT / "teamon-v43-proportions-side.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v43_build_report.json"

for directory in (BLEND_PATH.parent, PREVIEW_ROOT, REPORT_PATH.parent):
    directory.mkdir(parents=True, exist_ok=True)


def bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


def apply_scale(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


scene = bpy.context.scene
camera = bpy.data.objects["TEAMON_Camera"]
hand_root = bpy.data.objects["TEAMON_v41_HandPressGroup"]
keycap = bpy.data.objects["TEAMON_Keycap"]
keycap_top = bounds([keycap])["max"][2]

camera_q = camera.matrix_world.to_quaternion()
camera_up = (camera_q @ Vector((0.0, 1.0, 0.0))).normalized()
camera_back = (camera_q @ Vector((0.0, 0.0, 1.0))).normalized()

finger_shells = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_") and "_Shell_" in obj.name and "Thumb" not in obj.name]
for obj in finger_shells:
    length_scale = 1.0 if obj.name == "TEAMON_v41_Index_Shell_0" else 1.11
    obj.scale = (length_scale, 1.52, 1.10)
    apply_scale(obj)

finger_joints = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_") and "Joint" in obj.name and "Knuckle" not in obj.name and "Thumb" not in obj.name]
for obj in finger_joints:
    obj.scale *= 0.78
    apply_scale(obj)

# Bring the four knuckle housings forward and enlarge them into overlapping
# transitions, breaking the palm's formerly monolithic top-left edge.
knuckle_pads = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_KnucklePad_")]
for index, obj in enumerate(knuckle_pads):
    obj.scale = (1.13, 1.18, 1.10)
    apply_scale(obj)
    world = obj.matrix_world.copy()
    world.translation += camera_back * (0.14 + index * 0.018) - camera_up * 0.012
    obj.matrix_world = world

for obj in [candidate for candidate in bpy.data.objects if candidate.name.startswith("TEAMON_v41_KnuckleJoint_")]:
    obj.scale *= 0.76
    apply_scale(obj)

# The raised dorsal plate becomes a smaller angled layer over the palm dome.
dorsal = bpy.data.objects["TEAMON_v42_DorsalPlate"]
dorsal.scale = (0.86, 0.90, 0.92)
apply_scale(dorsal)
dorsal.matrix_world = Matrix.Translation(dorsal.matrix_world.translation) @ Matrix.Rotation(math.radians(-7.0), 4, camera_back) @ Matrix.Translation(-dorsal.matrix_world.translation) @ dorsal.matrix_world

# Open the thumb: flatten the thenar puck, thicken its real segments, and make
# the distal shell longer toward the left without moving the thumb group.
thenar = bpy.data.objects["TEAMON_v42_ThenarPad"]
thenar.scale = (0.76, 0.63, 0.72)
apply_scale(thenar)

thumb_shells = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_Thumb_Shell_")]
for obj in thumb_shells:
    length_scale = 1.30 if obj.name.endswith("_0") else 1.10
    obj.scale = (length_scale, 1.32, 1.08)
    apply_scale(obj)

thumb_joints = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_Thumb_Joint_")]
for obj in thumb_joints:
    obj.scale *= 0.76
    apply_scale(obj)

bpy.context.view_layer.update()

# Thickness changes can move the physical underside. Re-seat only in world Z;
# the locked contact x/y and camera are unchanged.
index_objects = [obj for obj in finger_shells if "Index_Shell" in obj.name]
gap = bounds(index_objects)["min"][2] - keycap_top
hand_root.location.z += 0.004 - gap
bpy.context.view_layer.update()

scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.frame_set(1)
hero_matrix = camera.matrix_world.copy()
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

visible_hand = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(("TEAMON_v41_", "TEAMON_v42_")) and not obj.hide_render]
hand_box = bounds(visible_hand)
hand_center = Vector(tuple((hand_box["min"][axis] + hand_box["max"][axis]) * 0.5 for axis in range(3)))
camera_offset = camera.location - hand_center
for angle_degrees, path in ((-20.0, LEFT_PATH), (42.0, SIDE_PATH)):
    camera.location = hand_center + Matrix.Rotation(math.radians(angle_degrees), 4, camera_up) @ camera_offset
    camera.rotation_euler = (hand_center - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
camera.matrix_world = hero_matrix
bpy.context.view_layer.update()

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

final_gap = bounds(index_objects)["min"][2] - keycap_top
tip_point = min((point for obj in index_objects for point in [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]), key=lambda point: point.x + point.y)
tip_ndc = world_to_camera_view(scene, camera, tip_point)
triangles = 0
for obj in visible_hand:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)

report = {
    "stage": "MATERIAL_PREVIEW",
    "status": "requires_visual_review_before_export",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(LEFT_PATH), str(SIDE_PATH)],
    "visible_hand_meshes": len(visible_hand),
    "triangles": triangles,
    "contact_gap": final_gap,
    "contact_pass": abs(final_gap - 0.004) <= 0.002,
    "tip_projection_estimate": {"x": tip_ndc.x, "y_from_top": 1.0 - tip_ndc.y},
    "changes": [
        "finger thickness +52 percent with recessed joints",
        "overlapping forward knuckle housings",
        "smaller angled dorsal plate",
        "flattened thenar pad and opened thumb",
    ],
    "known_pending": ["visual signoff", "animation wiring", "GLB export", "browser validation"],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
