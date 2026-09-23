import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

hand_root = bpy.data.objects["TEAMON_RUKA_HandRoot"]
wrist = bpy.data.objects["TEAMON_RUKA_LINK_backhand"]
tip = bpy.data.objects["TEAMON_RUKA_LINK_index_actual_tip"]
base_matrix = hand_root.matrix_world.copy()
pivot = tip.matrix_world.translation.copy()
axis = (pivot - wrist.matrix_world.translation).normalized()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

for delta_degrees in (-100, -70, 55, 85):
    rotation = Quaternion(axis, math.radians(delta_degrees)).to_matrix().to_4x4()
    hand_root.matrix_world = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ base_matrix
    bpy.context.view_layer.update()
    scene.render.filepath = str(PREVIEW_ROOT / f"teamon-v7-ruka-roll-{delta_degrees:+04d}.png")
    bpy.ops.render.render(write_still=True)

hand_root.matrix_world = base_matrix
bpy.context.view_layer.update()
