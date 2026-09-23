import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)


def world_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": Vector(tuple(min(point[index] for point in points) for index in range(3))),
        "max": Vector(tuple(max(point[index] for point in points) for index in range(3))),
    }


hand_root = bpy.data.objects["TEAMON_AbilityHandRoot"]
cuff = bpy.data.objects["TEAMON_ORCA_CuffShell"]
wrist = bpy.data.objects["TEAMON_ORCA_right_R-Carpals_8d1f1041"]
index_skin = next(
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("orca_mesh") == "right_I-FingerTipAssembly_I-DP-Skin"
)

index_bounds = world_bounds(index_skin)
pivot = Vector(
    (
        (index_bounds["min"].x + index_bounds["max"].x) * 0.5,
        (index_bounds["min"].y + index_bounds["max"].y) * 0.5,
        index_bounds["min"].z,
    )
)
axis = (pivot - wrist.matrix_world.translation).normalized()
hand_matrix = hand_root.matrix_world.copy()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

for angle_degrees in (0, 15, 29):
    rotation = Quaternion(axis, math.radians(angle_degrees)).to_matrix().to_4x4()
    around_contact = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)
    hand_root.matrix_world = around_contact @ hand_matrix
    bpy.context.view_layer.update()
    scene.render.filepath = str(PREVIEW_ROOT / f"teamon-v7-orca-roll-{angle_degrees:02d}.png")
    bpy.ops.render.render(write_still=True)

hand_root.matrix_world = hand_matrix
bpy.context.view_layer.update()
