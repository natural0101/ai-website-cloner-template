import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_hero_camera.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_hero_camera_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-hero-camera.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
camera = bpy.data.objects.get("TEAMON_Camera")
if camera is None:
    raise RuntimeError("TEAMON camera is missing")

target = (0.30, 0.20, 0.90)
camera.location = (12.20, -11.70, 14.00)
camera.data.lens = 68
look_at(camera, target)
scene.camera = camera
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

horizontal = Vector((camera.location.x - target[0], camera.location.y - target[1], 0.0)).length
vertical = camera.location.z - target[2]
report = {
    "asset": "TEAMON reference v3 hero camera match",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "camera_location": list(camera.location),
    "camera_target": list(target),
    "lens_mm": camera.data.lens,
    "estimated_elevation_degrees": math.degrees(math.atan2(vertical, horizontal)),
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
