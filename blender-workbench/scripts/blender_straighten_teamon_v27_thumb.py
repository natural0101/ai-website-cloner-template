from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(
    os.environ.get(
        "TEAMON_PROJECT_ROOT",
        r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template",
    )
)
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v27_shadow_composed.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v27-thumb-straightened.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v27_thumb_report.json"

thumb_meshes = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and str(obj.get("mjcf_body", "")).startswith("rh_th")
]
proximal = next(obj for obj in thumb_meshes if obj.get("mjcf_body") == "rh_thproximal")
distal = next(obj for obj in thumb_meshes if obj.get("mjcf_body") == "rh_thdistal")
pivot = proximal.matrix_world.translation.copy()
direction = distal.matrix_world.translation - pivot
horizontal = Vector((direction.x, direction.y, 0.0)).normalized()
tilt_axis = Vector((-horizontal.y, horizontal.x, 0.0)).normalized()

# v26 over-flexed the thumb into a vertical hook.  Open the chain back toward
# the reference diagonal, then move the attached base toward the camera so the
# complete thumb sits in the lower-right silhouette while still overlapping
# the enlarged palm shell.
open_degrees = -28.0
translation = Vector((0.78, 0.78, 0.08))
transform = (
    Matrix.Translation(pivot + translation)
    @ Matrix.Rotation(open_degrees * 3.141592653589793 / 180.0, 4, tilt_axis)
    @ Matrix.Translation(-pivot)
)
for obj in thumb_meshes:
    obj.matrix_world = transform @ obj.matrix_world

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW_PATH)
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON v27 straightened lower thumb",
    "mode": "HYBRID_HERO",
    "changed_scope": "thumb transforms only",
    "index_pose_changed": False,
    "open_degrees": open_degrees,
    "translation": list(translation),
    "preview": str(PREVIEW_PATH),
    "checkpoint": str(BLEND_PATH),
    "status": "composition_visual_gate"
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
