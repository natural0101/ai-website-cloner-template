import json
from pathlib import Path

import bpy


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
for name in (
    "TEAMON_Rebelia_ThumbBase V3 - Safety.002",
    "TEAMON_Rebelia_ThumbUpper - FlexMods (3DP)",
):
    bpy.data.objects[name].hide_render = True

profiles = {
    "short-a": (0.76, 0.70, 0.64),
    "short-b": (0.68, 0.62, 0.56),
    "short-c": (0.60, 0.54, 0.48),
}
offsets = ((0.000, -0.035), (-0.012, -0.047), (-0.024, -0.059))

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)

outputs = []
for profile_name, factors in profiles.items():
    for obj, base_location, base_scale, factor, (offset_x, offset_y) in zip(
        fingers, base_locations, base_scales, factors, offsets
    ):
        obj.location = base_location.copy()
        obj.location.x += offset_x
        obj.location.y += offset_y
        obj.location.z -= 0.057 * (1.0 - factor)
        obj.scale = base_scale.copy()
        obj.scale.y *= factor
    bpy.context.view_layer.update()
    output_path = PREVIEW_ROOT / f"teamon-v9-rebelia-{profile_name}.png"
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(output_path))

print(json.dumps({"outputs": outputs}, ensure_ascii=False))
