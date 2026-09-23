from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v9-rebelia-fingers-only.png"

for name in (
    "TEAMON_Rebelia_Cover Down V2",
    "TEAMON_Rebelia_Hand Back Cover - Safety",
    "TEAMON_Rebelia_Palm V2 - S1 - Safety",
    "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
    "TEAMON_Rebelia_ThumbUpper - FlexMods (3DP)",
):
    bpy.data.objects[name].hide_render = True

scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)
