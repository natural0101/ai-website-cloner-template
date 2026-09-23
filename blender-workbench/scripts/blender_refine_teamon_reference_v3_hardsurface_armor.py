import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_hardsurface_hand.blend"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-hardsurface-hand-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_hardsurface_armor_report.json"

for path in (BLEND_PATH, HERO_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def local_size(obj):
    corners = [Vector(corner) for corner in obj.bound_box]
    return Vector(
        tuple(
            max(point[index] for point in corners) - min(point[index] for point in corners)
            for index in range(3)
        )
    )


def rounded_box_mesh(name, size, bevel_ratio):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    temp = bpy.context.object
    temp.name = f"{name}_Builder"
    temp.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = temp.modifiers.new(name=f"{name}_ArmorBevel", type="BEVEL")
    bevel.width = min(size.y, size.z) * bevel_ratio
    bevel.segments = 3
    bevel.limit_method = "NONE"
    bevel.harden_normals = True
    bpy.context.view_layer.objects.active = temp
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    mesh = temp.data.copy()
    mesh.name = f"{name}_HardSurfaceMesh"
    bpy.data.objects.remove(temp, do_unlink=True)
    return mesh


targets = []
for obj in bpy.data.objects:
    if obj.hide_render or obj.type != "MESH" or not obj.name.startswith("TEAMON_"):
        continue
    is_finger_armor = obj.name.endswith("_Armor")
    is_contact_pad = obj.name.endswith("_ContactPad")
    is_knuckle_ridge = obj.name.startswith("TEAMON_KnuckleRidge_")
    if is_finger_armor or is_contact_pad or is_knuckle_ridge:
        if is_contact_pad:
            bevel_ratio = 0.34
        elif is_knuckle_ridge:
            bevel_ratio = 0.28
        else:
            bevel_ratio = 0.26
        targets.append((obj, bevel_ratio))

replaced = {}
for obj, bevel_ratio in targets:
    size = local_size(obj)
    old_mesh = obj.data
    obj.data = rounded_box_mesh(obj.name, size, bevel_ratio)
    replaced[obj.name] = {
        "localSize": list(size),
        "bevelRatio": bevel_ratio,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
    }
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

for obj in bpy.data.objects:
    obj.select_set(False)
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

triangle_count = 0
for obj in bpy.data.objects:
    if obj.type == "MESH" and not obj.hide_render and obj.name.startswith("TEAMON_"):
        obj.data.calc_loop_triangles()
        triangle_count += len(obj.data.loop_triangles)

report = {
    "asset": "TEAMON reference v3 hard-surface robotic armor",
    "blend": str(BLEND_PATH),
    "hero": str(HERO_PATH),
    "replacedObjects": replaced,
    "visibleAssetTriangles": triangle_count,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
