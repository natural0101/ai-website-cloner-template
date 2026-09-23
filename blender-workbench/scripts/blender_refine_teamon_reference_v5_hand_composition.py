import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v5_orca_composition.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v5_orca_composition_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v5-orca-composition-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


hand_root = bpy.data.objects.get("TEAMON_AbilityHandRoot")
cuff = bpy.data.objects.get("TEAMON_ORCA_CuffShell")
wrist = bpy.data.objects.get("TEAMON_ORCA_right_R-Carpals_8d1f1041")
keycap = bpy.data.objects.get("TEAMON_Keycap")
index_skin = next(
    (
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.get("orca_mesh") == "right_I-FingerTipAssembly_I-DP-Skin"
    ),
    None,
)
if None in (hand_root, cuff, wrist, keycap, index_skin):
    raise RuntimeError("TEAMON v5 camera checkpoint is incomplete")

# COMPOSITION only: shrink the articulated hand around the fixed index contact.
hand_root.scale *= 0.84
bpy.context.view_layer.update()

index_bounds = world_bounds([index_skin])
index_contact = Vector(
    (
        (index_bounds["min"][0] + index_bounds["max"][0]) * 0.5,
        (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5,
        index_bounds["min"][2],
    )
)
key_top = world_bounds([keycap])["max"][2]
contact_target = Vector((1.95, -0.56, key_top + 0.004))
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

bpy.context.view_layer.update()

visible_hand = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH"
    and not obj.hide_render
    and obj.name.startswith("TEAMON_ORCA_")
]

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
    "asset": "TEAMON reference v5 ORCA hand composition",
    "stage": "COMPOSITION",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "hand_scale_factor": 0.84,
    "cuff_scale_factor": 1.0,
    "contact_target": list(contact_target),
    "index_tip_bounds": world_bounds([index_skin]),
    "visible_hand_bounds": world_bounds(visible_hand),
    "status": "composition_visual_gate"
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
