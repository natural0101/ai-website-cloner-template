import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_lod.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_lod_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-lod-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def triangles(obj):
    if obj.type != "MESH":
        return 0
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def asset_meshes():
    return [
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH"
        and not obj.hide_render
        and obj.name.startswith("TEAMON_")
        and "Studio" not in obj.name
        and "Floor" not in obj.name
    ]


before = {obj.name: triangles(obj) for obj in asset_meshes()}
changed = {}
for obj in asset_meshes():
    ratio = 1.0
    if obj.name == "TEAMON_Text":
        ratio = 0.70
    elif obj.name.endswith("_Armor") and not obj.name.startswith("TEAMON_Index_"):
        ratio = 0.88
    elif "_RecessedPin_" in obj.name:
        ratio = 0.82
    if ratio >= 0.999 or triangles(obj) < 180:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new(name="TEAMON_Web_LOD_Final", type="DECIMATE")
    modifier.decimate_type = "COLLAPSE"
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    changed[obj.name] = {"ratio": ratio, "before": before[obj.name], "after": triangles(obj)}

after = {obj.name: triangles(obj) for obj in asset_meshes()}
scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v3 final LOD checkpoint",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "before_triangles": sum(before.values()),
    "after_triangles": sum(after.values()),
    "target_under_25000": sum(after.values()) < 25000,
    "changed": changed,
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
