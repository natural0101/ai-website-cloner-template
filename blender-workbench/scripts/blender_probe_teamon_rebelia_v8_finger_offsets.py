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
hand_root.location.y += 0.86
text.rotation_euler.z = math.radians(100.0)

angles = {
    "Middle": (-32.0, -40.0, -17.0),
    "Ring": (-38.0, -48.0, -21.0),
    "Little": (-44.0, -56.0, -25.0),
}
base_mcp_y = {}
for finger_name, values in angles.items():
    mcp = bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_MCP"]
    base_mcp_y[finger_name] = mcp.location.y
    for joint_name, angle in zip(("MCP", "PIP", "DIP"), values):
        bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_{joint_name}"].rotation_euler.x = math.radians(angle)

for obj in bpy.data.objects:
    if obj.name.endswith("_Joint"):
        obj.scale = (0.34, 0.40, 0.34)

thumb_root = bpy.data.objects.new("TEAMON_Rebelia_ThumbOffsetRoot", None)
output.objects.link(thumb_root)
thumb_root.parent = hand_root
thumb_root.matrix_local = Matrix.Translation(Vector((0.055, -0.032, -0.098)))
for name in (
    "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
    "TEAMON_Rebelia_Thumb Proximal Cover V4",
    "TEAMON_Rebelia_Thumb Distal Cover V4",
):
    parent_keep_world(bpy.data.objects[name], thumb_root)
thumb_root.rotation_euler.y = math.radians(32.0)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for offset in (0.018, 0.030, 0.042):
    for finger_name in angles:
        bpy.data.objects[f"TEAMON_Rebelia_{finger_name}_MCP"].location.y = base_mcp_y[finger_name] - offset
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v8-rebelia-finger-offset-{offset:.3f}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
