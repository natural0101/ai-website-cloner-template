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
base_locations = [obj.location.copy() for obj in fingers]
base_scales = [obj.scale.copy() for obj in fingers]
base_matrices = [obj.matrix_local.copy() for obj in fingers]

for name in (
    "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
    "TEAMON_Rebelia_ThumbUpper - FlexMods (3DP)",
):
    bpy.data.objects[name].hide_render = True

profiles = {
    "curl-front-a": {
        "x": (0.000, -0.018, -0.036),
        "y": (-0.075, -0.095, -0.115),
        "roll": (-50.0, -42.0, -34.0),
    },
    "curl-front-b": {
        "x": (-0.010, -0.035, -0.060),
        "y": (-0.100, -0.122, -0.144),
        "roll": (-55.0, -45.0, -35.0),
    },
    "curl-front-positive": {
        "x": (-0.010, -0.035, -0.060),
        "y": (-0.100, -0.122, -0.144),
        "roll": (48.0, 38.0, 28.0),
    },
}
factors = (0.76, 0.70, 0.64)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for profile_name, profile in profiles.items():
    for index, obj in enumerate(fingers):
        obj.matrix_local = base_matrices[index].copy()
        obj.location = base_locations[index].copy()
        obj.scale = base_scales[index].copy()
        factor = factors[index]
        obj.location.x += profile["x"][index]
        obj.location.y += profile["y"][index]
        obj.location.z -= 0.057 * (1.0 - factor)
        obj.scale.y *= factor
        obj.matrix_local = obj.matrix_local @ Matrix.Rotation(math.radians(profile["roll"][index]), 4, "Y")
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v11-rebelia-{profile_name}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
