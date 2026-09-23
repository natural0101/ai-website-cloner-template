import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v10-rebelia-thumb-only.png"


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


thumb = bpy.data.objects["TEAMON_Rebelia_Thumb_FullFinger"]
records = {"thumb": bounds(thumb)}
for name in (
    "TEAMON_Rebelia_03 FlexMods V6 (3DP)",
    "TEAMON_Rebelia_Middle_FullFinger",
    "TEAMON_Rebelia_Ring_FullFinger",
    "TEAMON_Rebelia_Little_FullFinger",
):
    records[name] = bounds(bpy.data.objects[name])

for obj in bpy.data.objects:
    if obj.name.startswith("TEAMON_Rebelia_") and obj != thumb:
        obj.hide_render = True

scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)
print(json.dumps(records, ensure_ascii=False, indent=2))
