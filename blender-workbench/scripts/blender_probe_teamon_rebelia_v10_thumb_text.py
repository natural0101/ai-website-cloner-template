from pathlib import Path
import math

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v10-rebelia-thumb-text-probe.png"

thumb = bpy.data.objects["TEAMON_Rebelia_Thumb_FullFinger"]
text = bpy.data.objects["TEAMON_Text"]
thumb.location += Vector((0.025, 0.0, -0.025))
text.rotation_euler.z = math.radians(92.0)

scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)
