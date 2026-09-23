import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_finger_mass.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_finger_mass_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-finger-mass-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


scaled = {}
for obj in bpy.data.objects:
    if obj.hide_render:
        continue
    if obj.name.startswith("TEAMON_") and obj.name.endswith("_Armor"):
        obj.scale.y *= 1.30
        obj.scale.z *= 1.20
        scaled[obj.name] = list(obj.scale)
    elif obj.name.startswith("TEAMON_") and obj.name.endswith("_ContactPad"):
        obj.scale.x *= 1.12
        obj.scale.y *= 1.24
        scaled[obj.name] = list(obj.scale)


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min_z": min(point.z for point in corners),
        "max_z": max(point.z for point in corners),
    }


# Re-seat the index pad after local thickness scaling. The final world-space
# bottom must touch the cap instead of relying on an unrotated local radius.
bpy.context.view_layer.update()
keycap = bpy.data.objects.get("TEAMON_Keycap")
index_pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
if keycap is None or index_pad is None or press_group is None:
    raise RuntimeError("TEAMON keycap, index contact pad or hand press group is missing")
keycap_top = world_bounds(keycap)["max_z"]
index_bottom_before = world_bounds(index_pad)["min_z"]
press_group.location.z += keycap_top - index_bottom_before
bpy.context.view_layer.update()
index_bottom_after = world_bounds(index_pad)["min_z"]

scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v3 finger mass refinement",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "scaled_shells": scaled,
    "contact": {
        "keycap_top_z": keycap_top,
        "index_bottom_before": index_bottom_before,
        "index_bottom_after": index_bottom_after,
        "signed_gap_after": index_bottom_after - keycap_top,
    },
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
