import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v5_orca_camera.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_camera_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-camera-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


camera = bpy.data.objects.get("TEAMON_Camera")
base = bpy.data.objects.get("TEAMON_Base")
if camera is None or base is None:
    raise RuntimeError("TEAMON v5 geometry checkpoint is incomplete")

# COMPOSITION only. Blender ground plane is X/Y, so the measured Three.js
# X/Z azimuth ratio maps to camera X/abs(Y) here.
camera.location = (10.9, -7.8, 10.1)
camera.data.lens = 60
target = (0.30, -0.20, 0.55)
look_at(camera, target)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v5 ORCA camera",
    "stage": "COMPOSITION",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "camera_location": list(camera.location),
    "camera_target": list(target),
    "camera_lens_mm": camera.data.lens,
    "azimuth_ratio_x_to_abs_y": camera.location.x / abs(camera.location.y),
    "status": "composition_visual_gate"
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
