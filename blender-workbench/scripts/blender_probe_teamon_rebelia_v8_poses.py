import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"


def parent_keep_world(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


hand_root = bpy.data.objects["TEAMON_RebeliaHandRoot"]
output = bpy.data.collections["TEAMON_OUTPUT"]
text = bpy.data.objects["TEAMON_Text"]

# Move the fingertip contact from the near rim toward the panel centre. This is
# the largest screen-space placement difference from the supplied reference.
hand_root.location.y += 0.86
text.rotation_euler.z = math.radians(100.0)

for obj in bpy.data.objects:
    if obj.name.endswith("_Joint"):
        obj.scale = (0.52, 0.62, 0.52)

thumb_root = bpy.data.objects.get("TEAMON_Rebelia_ThumbPoseRoot")
if thumb_root is None:
    thumb_root = bpy.data.objects.new("TEAMON_Rebelia_ThumbPoseRoot", None)
    output.objects.link(thumb_root)
    thumb_root.parent = hand_root
    thumb_root.matrix_local = Matrix.Translation(Vector((0.055, 0.0, -0.098)))
    for name in (
        "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
        "TEAMON_Rebelia_Thumb Proximal Cover V4",
        "TEAMON_Rebelia_Thumb Distal Cover V4",
    ):
        parent_keep_world(bpy.data.objects[name], thumb_root)

profiles = {
    "positive-medium": {
        "Middle": (43.0, 55.0, 24.0),
        "Ring": (50.0, 64.0, 29.0),
        "Little": (58.0, 73.0, 34.0),
        "thumb": 32.0,
    },
    "positive-compact": {
        "Middle": (54.0, 68.0, 30.0),
        "Ring": (62.0, 77.0, 35.0),
        "Little": (70.0, 87.0, 40.0),
        "thumb": 38.0,
    },
    "positive-soft": {
        "Middle": (35.0, 46.0, 20.0),
        "Ring": (42.0, 54.0, 24.0),
        "Little": (49.0, 62.0, 28.0),
        "thumb": 26.0,
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
    for finger_name in ("Middle", "Ring", "Little"):
        angles = profile[finger_name]
        for joint_name, angle in zip(("MCP", "PIP", "DIP"), angles):
            pivot = bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_{joint_name}"]
            pivot.rotation_euler.x = math.radians(angle)
    thumb_root.rotation_euler.y = math.radians(profile["thumb"])
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v8-rebelia-{profile_name}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
