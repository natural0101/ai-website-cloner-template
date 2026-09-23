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
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v29_shadow_composed.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v29-thumb-restored.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v29_thumb_report.json"

source_matrices = {
    "rh_thdistal": Matrix((
        (-0.00022472163254860789, 0.008763520047068596, -0.014282860793173313, 2.040095806121826),
        (0.02000844106078148, -0.0028533940203487873, -0.0012607179814949632, 2.172968626022339),
        (-0.0032703897450119257, -0.018059412017464638, -0.006731715053319931, 0.7343488931655884),
        (0.0, 0.0, 0.0, 1.0),
    )),
    "rh_thmiddle": Matrix((
        (0.014358683489263058, 0.00022472493583336473, -0.01118201483041048, 2.3979201316833496),
        (-0.002151892287656665, -0.02000844106078148, -0.001931962207891047, 2.2347915172576904),
        (-0.014152075164020061, 0.0032703871838748455, -0.011051497422158718, 1.0879968404769897),
        (0.0, 0.0, 0.0, 1.0),
    )),
    "rh_thproximal": Matrix((
        (0.018480338156223297, 0.0002340525679755956, -0.006513298023492098, 2.645425796508789),
        (-0.0011428076541051269, -0.020004989579319954, -0.002417838666588068, 2.3266689777374268),
        (-0.008261638693511486, 0.003290778724476695, -0.01423504576086998, 1.628928542137146),
        (0.0, 0.0, 0.0, 1.0),
    )),
}
rigid_offset = Matrix.Translation(Vector((0.15, 0.15, 0.03)))
restored = []
for obj in bpy.data.objects:
    body = str(obj.get("mjcf_body", ""))
    if obj.type == "MESH" and body in source_matrices:
        obj.matrix_world = rigid_offset @ source_matrices[body]
        restored.append(obj.name)

if len(restored) != 3:
    raise RuntimeError(f"Expected three restored thumb meshes, received {len(restored)}")

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
    "asset": "TEAMON v29 restored undistorted thumb",
    "mode": "HYBRID_HERO",
    "changed_scope": "thumb matrices only",
    "restored_from": "teamon_reference_v25_shadow_composed.blend",
    "rigid_offset": [0.15, 0.15, 0.03],
    "index_pose_changed": False,
    "restored_objects": restored,
    "preview": str(PREVIEW_PATH),
    "checkpoint": str(BLEND_PATH),
    "status": "composition_visual_gate",
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
