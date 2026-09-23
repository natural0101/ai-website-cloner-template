import json
import math
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"

hand_root = bpy.data.objects["TEAMON_RebeliaHandRoot"]
text = bpy.data.objects["TEAMON_Text"]
hand_root.location.y += 0.86
text.rotation_euler.z = math.radians(100.0)

for obj in bpy.data.objects:
    if obj.name.endswith("_Joint"):
        obj.hide_render = True
    if obj.name in {
        "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
        "TEAMON_Rebelia_Thumb Proximal Cover V4",
        "TEAMON_Rebelia_Thumb Distal Cover V4",
    }:
        obj.hide_render = True

profiles = {
    "negative-soft": {
        "Middle": (-24.0, -32.0, -14.0),
        "Ring": (-29.0, -38.0, -17.0),
        "Little": (-34.0, -44.0, -20.0),
    },
    "negative-medium": {
        "Middle": (-34.0, -44.0, -19.0),
        "Ring": (-40.0, -52.0, -23.0),
        "Little": (-46.0, -60.0, -27.0),
    },
    "negative-mcp": {
        "Middle": (-48.0, -22.0, -10.0),
        "Ring": (-55.0, -26.0, -12.0),
        "Little": (-62.0, -30.0, -14.0),
    },
}

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for profile_name, profile in profiles.items():
    for finger_name, angles in profile.items():
        for joint_name, angle in zip(("MCP", "PIP", "DIP"), angles):
            bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_{joint_name}"].rotation_euler.x = math.radians(angle)
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v8-rebelia-{profile_name}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
