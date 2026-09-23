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
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v28_shadow_composed.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v28-hand-scale.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v28_hand_scale_report.json"


def mesh_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


hand_root = bpy.data.objects["TEAMON_ShadowBakedRoot"]
hand_meshes = [obj for obj in hand_root.children_recursive if obj.type == "MESH"]
index_mesh = next(obj for obj in hand_meshes if obj.get("shadow_index_distal"))
index_low, index_high = mesh_bounds(index_mesh)
contact = Vector(
    (
        (index_low.x + index_high.x) * 0.5,
        (index_low.y + index_high.y) * 0.5,
        index_low.z,
    )
)

hand_scale = 1.25
scale_transform = (
    Matrix.Translation(contact)
    @ Matrix.Scale(hand_scale, 4)
    @ Matrix.Translation(-contact)
)
for obj in hand_meshes:
    obj.matrix_world = scale_transform @ obj.matrix_world

# Keep the v26 thumb bend, but move the complete attached chain toward the
# lower-right hero silhouette.  The enlarged palm shell still covers its base.
thumb_translation = Vector((0.82, 0.82, 0.0))
for obj in hand_meshes:
    if str(obj.get("mjcf_body", "")).startswith("rh_th"):
        obj.matrix_world = Matrix.Translation(thumb_translation) @ obj.matrix_world

bpy.context.view_layer.update()
index_low, index_high = mesh_bounds(index_mesh)
resnapped_contact = Vector(
    (
        (index_low.x + index_high.x) * 0.5,
        (index_low.y + index_high.y) * 0.5,
        index_low.z,
    )
)
hand_root.location += contact - resnapped_contact
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
    "asset": "TEAMON v28 enlarged aligned hand",
    "mode": "HYBRID_HERO",
    "hand_scale_about_index_contact": hand_scale,
    "thumb_translation": list(thumb_translation),
    "index_contact_before": list(contact),
    "index_contact_after": list(mesh_bounds(index_mesh)[0]),
    "preview": str(PREVIEW_PATH),
    "checkpoint": str(BLEND_PATH),
    "status": "composition_visual_gate"
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
