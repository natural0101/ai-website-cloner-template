import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"

names = (
    "TEAMON_Rebelia_Middle_FullFinger",
    "TEAMON_Rebelia_Ring_FullFinger",
    "TEAMON_Rebelia_Little_FullFinger",
)
fingers = [bpy.data.objects[name] for name in names]
base_matrices = [obj.matrix_local.copy() for obj in fingers]
offsets = ((0.000, -0.035), (-0.012, -0.047), (-0.024, -0.059))
for obj, (offset_x, offset_y) in zip(fingers, offsets):
    obj.location.x += offset_x
    obj.location.y += offset_y
base_matrices = [obj.matrix_local.copy() for obj in fingers]

for name in (
    "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
    "TEAMON_Rebelia_ThumbUpper - FlexMods (3DP)",
):
    bpy.data.objects[name].hide_render = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for roll in (-70.0, -45.0, 45.0, 70.0):
    local_roll = Matrix.Rotation(math.radians(roll), 4, "Y")
    for obj, base_matrix in zip(fingers, base_matrices):
        obj.matrix_local = base_matrix @ local_roll
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v9-rebelia-finger-roll-{roll:+.0f}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
