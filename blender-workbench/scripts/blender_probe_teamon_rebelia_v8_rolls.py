import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


hand_root = bpy.data.objects["TEAMON_RebeliaHandRoot"]
text = bpy.data.objects["TEAMON_Text"]
index_tip = bpy.data.objects["TEAMON_Rebelia_Distal Cover V4"]
hand_root.location.y += 0.86
text.rotation_euler.z = math.radians(100.0)

angles = {
    "Middle": (-24.0, -32.0, -14.0),
    "Ring": (-29.0, -38.0, -17.0),
    "Little": (-34.0, -44.0, -20.0),
}
for finger_name, values in angles.items():
    for joint_name, angle in zip(("MCP", "PIP", "DIP"), values):
        bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_{joint_name}"].rotation_euler.x = math.radians(angle)
for obj in bpy.data.objects:
    if obj.name.endswith("_Joint") or obj.name in {
        "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
        "TEAMON_Rebelia_Thumb Proximal Cover V4",
        "TEAMON_Rebelia_Thumb Distal Cover V4",
    }:
        obj.hide_render = True

bpy.context.view_layer.update()
tip_bounds = bounds(index_tip)
pivot = Vector(
    (
        (tip_bounds["min"][0] + tip_bounds["max"][0]) * 0.5,
        (tip_bounds["min"][1] + tip_bounds["max"][1]) * 0.5,
        tip_bounds["min"][2],
    )
)
axis = Vector((-1.0, -0.10, -0.55)).normalized()
base_matrix = hand_root.matrix_world.copy()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for roll in (-45.0, -25.0, 25.0, 45.0):
    rotation = Quaternion(axis, math.radians(roll)).to_matrix().to_4x4()
    hand_root.matrix_world = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ base_matrix
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v8-rebelia-roll-{roll:+.0f}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
