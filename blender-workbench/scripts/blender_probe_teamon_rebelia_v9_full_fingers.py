import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
DONOR_BLEND = PROJECT_ROOT / "blender-workbench" / "vendor" / "rebelia-v2" / "Rebelia - Hierarchic.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v9-rebelia-full-fingers-probe.png"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v9_rebelia_full_fingers_probe.blend"

DONOR_NAMES = [
    "Cover Down V2",
    "Hand Back Cover - Safety",
    "Palm V2 - S1 - Safety",
    "03 FlexMods V6 (3DP)",
    "03 FlexMods V6 (3DP) PF",
    "ThumbBase V3 - Safety.002",
    "ThumbUpper - FlexMods (3DP)",
]


def world_bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


def parent_keep_world(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def place_source_part(obj, center_x, center_y, base_z):
    box = world_bounds([obj])
    center = Vector(
        (
            (box["min"][0] + box["max"][0]) * 0.5,
            (box["min"][1] + box["max"][1]) * 0.5,
            box["min"][2],
        )
    )
    obj.location += Vector((center_x, center_y, base_z)) - center


output = bpy.data.collections.get("TEAMON_OUTPUT")
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
keycap = bpy.data.objects.get("TEAMON_Keycap")
text = bpy.data.objects.get("TEAMON_Text")
white = bpy.data.materials.get("TEAMON_Robot_White")
if None in (output, composition_root, keycap, text, white):
    raise RuntimeError("TEAMON ORCA material checkpoint is incomplete")

for obj in list(bpy.data.objects):
    if obj.name.startswith("TEAMON_ORCA_") or obj.name == "TEAMON_AbilityHandRoot":
        bpy.data.objects.remove(obj, do_unlink=True)

temp = bpy.data.collections.new("TEAMON_REBELIA_FULL_IMPORT")
bpy.context.scene.collection.children.link(temp)
requested_names = list(DONOR_NAMES)
with bpy.data.libraries.load(str(DONOR_BLEND), link=False) as (source, target):
    missing = [name for name in requested_names if name not in source.objects]
    if missing:
        raise RuntimeError(f"Rebelia donor is missing expected objects: {missing}")
    target.objects = list(requested_names)

loaded = {}
for source_name, source_obj in zip(requested_names, target.objects):
    if source_obj is None:
        continue
    temp.objects.link(source_obj)
    loaded[source_name] = source_obj
bpy.context.view_layer.update()

hand_root = bpy.data.objects.new("TEAMON_RebeliaHandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["asset_source"] = "https://github.com/opsobot/rebelia/tree/41f2708999a01f8dd815642889281cea8bb1c0e9"
hand_root["asset_license"] = "CERN-OHL-S-2.0"
hand_root["asset_revision"] = "41f2708999a01f8dd815642889281cea8bb1c0e9"
hand_root["pose"] = "straight full index; three pre-flexed full fingers"

depsgraph = bpy.context.evaluated_depsgraph_get()
parts = {}
for source_name in requested_names:
    source_obj = loaded[source_name]
    evaluated = source_obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=False, depsgraph=depsgraph)
    obj = bpy.data.objects.new(f"TEAMON_Rebelia_{source_name}", mesh)
    output.objects.link(obj)
    obj.matrix_world = source_obj.matrix_world.copy()
    obj.data.materials.clear()
    obj.data.materials.append(white)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if len(mesh.polygons) > 1200:
        modifier = obj.modifiers.new("TEAMON_WebDecimate", "DECIMATE")
        if source_name == "Cover Down V2":
            modifier.ratio = 0.18
        elif "FlexMods" in source_name:
            modifier.ratio = 0.20
        else:
            modifier.ratio = 0.32
        modifier.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
    obj["rebelia_source_object"] = source_name
    obj["export"] = True
    parts[source_name] = obj

for source_obj in list(temp.objects):
    bpy.data.objects.remove(source_obj, do_unlink=True)
bpy.data.collections.remove(temp)

index = parts["03 FlexMods V6 (3DP)"]
place_source_part(index, 0.0318, -0.004, -0.0405)

preflexed_template = parts["03 FlexMods V6 (3DP) PF"]
preflexed_template.matrix_world = Matrix.Rotation(math.radians(90.0), 4, "X") @ preflexed_template.matrix_world
place_source_part(preflexed_template, 0.0120, -0.006, -0.0394)
preflexed_template.name = "TEAMON_Rebelia_Middle_FullFinger"

free_fingers = [preflexed_template]
for name, center_x, base_z, scale_value in (
    ("Ring", -0.0090, -0.0442, 0.96),
    ("Little", -0.0318, -0.0558, 0.88),
):
    obj = bpy.data.objects.new(f"TEAMON_Rebelia_{name}_FullFinger", preflexed_template.data)
    output.objects.link(obj)
    obj.matrix_world = preflexed_template.matrix_world.copy()
    obj.scale *= scale_value
    place_source_part(obj, center_x, -0.008, base_z)
    obj["rebelia_source_object"] = "03 FlexMods V6 (3DP) PF"
    obj["export"] = True
    free_fingers.append(obj)

for obj in parts.values():
    parent_keep_world(obj, hand_root)
for obj in free_fingers[1:]:
    parent_keep_world(obj, hand_root)

# Bring the complete thumb assembly toward the visible dorsal side.
for name in ("ThumbBase V3 - Safety.002", "ThumbUpper - FlexMods (3DP)"):
    parts[name].location.y -= 0.020

source_long = Vector((0.0, 0.0, 1.0))
source_width = Vector((1.0, 0.0, 0.0))
source_normal = Vector((0.0, -1.0, 0.0))
target_long = Vector((-1.0, -0.10, -0.55)).normalized()
target_width = Vector((-0.08, -0.05, -1.0))
target_width = (target_width - target_long * target_width.dot(target_long)).normalized()
target_normal = target_long.cross(target_width).normalized()
target_width = target_normal.cross(target_long).normalized()
source_basis = Matrix((source_long, source_width, source_normal)).transposed()
target_basis = Matrix((target_long, target_width, target_normal)).transposed()
rotation = target_basis @ source_basis.transposed()
hand_scale = 15.6
hand_root.matrix_world = rotation.to_4x4() @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
bpy.context.view_layer.update()

index_bounds = world_bounds([index])
key_bounds = world_bounds([keycap])
index_contact = Vector(
    (
        (index_bounds["min"][0] + index_bounds["max"][0]) * 0.5,
        (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5,
        index_bounds["min"][2],
    )
)
contact_target = Vector((1.95, 0.30, key_bounds["max"][2] + 0.004))
hand_root.location += contact_target - index_contact
text.rotation_euler.z = math.radians(100.0)
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(PREVIEW_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

export_meshes = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_Rebelia_") and obj.type == "MESH"]
print(
    json.dumps(
        {
            "preview": str(PREVIEW_PATH),
            "blend": str(BLEND_PATH),
            "meshes": len(export_meshes),
            "triangles": sum(len(obj.data.loop_triangles) for obj in export_meshes),
            "hand_bounds": world_bounds(export_meshes),
        },
        ensure_ascii=False,
    )
)
