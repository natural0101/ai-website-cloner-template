import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_optimized.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_optimized_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-optimized-hero.png"

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


def ratio_for(obj):
    name = obj.name
    if name == "TEAMON_Text":
        return 0.52
    if name.endswith("_Armor") or name.endswith("_ContactPad"):
        return 0.48
    if name.endswith("_InnerTendon"):
        return 0.38
    if "_RecessedPin_" in name:
        return 0.34
    if name.startswith("TEAMON_KnuckleRidge_"):
        return 0.56
    if name in ("TEAMON_PalmShell", "TEAMON_ThenarShell"):
        return 0.68
    if name.startswith("TEAMON_Thumb_") and name.endswith("_Armor"):
        return 0.46
    return 1.0


before_meshes = asset_meshes()
before = {obj.name: triangles(obj) for obj in before_meshes}
optimized = {}

# Hidden iterations remain editable in the source blend but are explicitly
# ineligible for export in this checkpoint.
excluded = []
for obj in bpy.data.objects:
    if obj.hide_render or obj.get("remediation_status"):
        obj["export"] = False
        excluded.append(obj.name)

for obj in before_meshes:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ratio = ratio_for(obj)
    if ratio < 0.999 and triangles(obj) > 180:
        modifier = obj.modifiers.new(name="TEAMON_Web_LOD", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = ratio
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        optimized[obj.name] = {
            "ratio": ratio,
            "before": before[obj.name],
            "after": triangles(obj),
        }
    obj["export"] = True

after_meshes = asset_meshes()
after = {obj.name: triangles(obj) for obj in after_meshes}
scene = bpy.context.scene
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v3 optimized checkpoint",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "before_triangles": sum(before.values()),
    "after_triangles": sum(after.values()),
    "target_under_25000": sum(after.values()) < 25000,
    "optimized_objects": optimized,
    "explicitly_excluded_object_count": len(excluded),
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
