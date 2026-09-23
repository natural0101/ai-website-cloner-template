import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_articulated_fan.blend"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-articulated-fan-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_articulated_fan_report.json"

for path in (BLEND_PATH, HERO_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def require(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required TEAMON object is missing: {name}")
    return obj


def world_min_z(obj):
    return min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def world_max_z(obj):
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


fan_degrees = {"Middle": 10.0, "Ring": 16.0, "Pinky": 22.0}
rotated = {}
for finger, degrees in fan_degrees.items():
    proximal = require(f"TEAMON_{finger}_Proximal_Armor").matrix_world.translation.copy()
    middle = require(f"TEAMON_{finger}_Middle_Armor").matrix_world.translation.copy()
    pivot = proximal + (proximal - middle) * 0.52
    transform = (
        Matrix.Translation(pivot)
        @ Matrix.Rotation(math.radians(degrees), 4, "Y")
        @ Matrix.Translation(-pivot)
    )
    names = []
    for obj in bpy.data.objects:
        if obj.hide_render or not obj.name.startswith(f"TEAMON_{finger}_"):
            continue
        obj.matrix_world = transform @ obj.matrix_world
        names.append(obj.name)
    rotated[finger] = {"degrees": degrees, "pivot": list(pivot), "objects": names}

plate_scales = {
    "TEAMON_PalmDorsalPlate_V3": (0.96, 0.90, 0.84),
    "TEAMON_WristDorsalPlate_V3": (0.92, 0.86, 0.82),
    "TEAMON_WristHousing_V3": (0.95, 0.90, 0.86),
}
for name, factors in plate_scales.items():
    obj = require(name)
    obj.scale = tuple(obj.scale[index] * factors[index] for index in range(3))

keycap = require("TEAMON_Keycap")
press_group = require("TEAMON_PressGroup")
hand_press_group = require("TEAMON_HandPressGroup")
index_pad = require("TEAMON_Index_ContactPad")
bpy.context.view_layer.update()

gap_before = world_min_z(index_pad) - world_max_z(keycap)
target_overlap = 0.014
hand_matrix = hand_press_group.matrix_world.copy()
hand_matrix.translation.z += -gap_before - target_overlap
hand_press_group.matrix_world = hand_matrix
bpy.context.view_layer.update()
gap_after = world_min_z(index_pad) - world_max_z(keycap)

old_shadow = bpy.data.objects.get("TEAMON_ContactShadow")
if old_shadow is not None:
    bpy.data.objects.remove(old_shadow, do_unlink=True)
shadow_material = bpy.data.materials.get("TEAMON_ContactShadow_Material")
if shadow_material is None:
    shadow_material = bpy.data.materials.new("TEAMON_ContactShadow_Material")
    shadow_material.use_nodes = True
principled = next(
    (node for node in shadow_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
    None,
)
if principled:
    principled.inputs["Base Color"].default_value = (0.055, 0.018, 0.022, 1.0)
    principled.inputs["Roughness"].default_value = 0.72
    principled.inputs["Alpha"].default_value = 0.20
if hasattr(shadow_material, "surface_render_method"):
    shadow_material.surface_render_method = "DITHERED"

pad_center = index_pad.matrix_world.translation.copy()
key_top = world_max_z(keycap)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=1.0,
    location=(pad_center.x, pad_center.y, key_top + 0.002),
)
contact_shadow = bpy.context.object
contact_shadow.name = "TEAMON_ContactShadow"
contact_shadow.scale = (0.48, 0.28, 0.012)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
contact_shadow.data.materials.append(shadow_material)
contact_shadow["export"] = True
contact_shadow["role"] = "contact_cue_on_pressing_surface"
parent_keep_world(contact_shadow, press_group)

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
    "asset": "TEAMON reference v3 articulated finger fan",
    "blend": str(BLEND_PATH),
    "hero": str(HERO_PATH),
    "fan": rotated,
    "plateScaleFactors": plate_scales,
    "contactGapBefore": gap_before,
    "contactGapAfter": gap_after,
    "contactShadow": contact_shadow.name,
    "visibleAssetTriangles": triangle_count,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
