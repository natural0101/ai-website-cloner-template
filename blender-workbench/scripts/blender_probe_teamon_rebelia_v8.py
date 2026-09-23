import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
DONOR_BLEND = PROJECT_ROOT / "blender-workbench" / "vendor" / "rebelia-v2" / "Rebelia - Hierarchic.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v8-rebelia-probe.png"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v8_rebelia_probe.blend"

DONOR_NAMES = [
    "Cover Down V2",
    "Hand Back Cover - Safety",
    "Palm V2 - S1 - Safety",
    "Proximal Cover V4",
    "Medial Cover V4",
    "Distal Cover V4",
    "Middle Proximal Cover V4",
    "Middle Medial Cover V4",
    "Middle Distal Cover V4",
    "Ring Proximal Cover V4",
    "Ring Medial Cover V4",
    "Ring Distal Cover V4",
    "Little Proximal Cover V4",
    "Little Medial Cover V4",
    "Little Distal Cover V4",
    "ThumbBase V3 - Safety.002",
    "Thumb Proximal Cover V4",
    "Thumb Distal Cover V4",
]

FINGER_DATA = {
    "Index": {
        "objects": ("Proximal Cover V4", "Medial Cover V4", "Distal Cover V4"),
        "pivots": ((0.0319, -0.0030, -0.0405), (0.0319, -0.0030, 0.0075), (0.0319, -0.0030, 0.0340)),
        "angles": (0.0, 0.0, 0.0),
    },
    "Middle": {
        "objects": ("Middle Proximal Cover V4", "Middle Medial Cover V4", "Middle Distal Cover V4"),
        "pivots": ((0.0120, -0.0030, -0.0394), (0.0120, -0.0030, 0.0125), (0.0120, -0.0030, 0.0415)),
        "angles": (-55.0, -65.0, -30.0),
    },
    "Ring": {
        "objects": ("Ring Proximal Cover V4", "Ring Medial Cover V4", "Ring Distal Cover V4"),
        "pivots": ((-0.0090, -0.0030, -0.0442), (-0.0090, -0.0030, 0.0035), (-0.0090, -0.0030, 0.0301)),
        "angles": (-62.0, -75.0, -35.0),
    },
    "Little": {
        "objects": ("Little Proximal Cover V4", "Little Medial Cover V4", "Little Distal Cover V4"),
        "pivots": ((-0.0318, -0.0030, -0.0558), (-0.0318, -0.0030, -0.0168), (-0.0318, -0.0030, 0.0050)),
        "angles": (-70.0, -85.0, -40.0),
    },
}


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


def make_empty(name, location, parent, collection):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.matrix_world = Matrix.Translation(Vector(location))
    parent_keep_world(obj, parent)
    return obj


def make_joint(name, location, parent, collection, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.0095, location=location)
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.scale.y = 1.18
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, parent)
    obj["export"] = True
    return obj


output = bpy.data.collections.get("TEAMON_OUTPUT")
composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
keycap = bpy.data.objects.get("TEAMON_Keycap")
text = bpy.data.objects.get("TEAMON_Text")
white = bpy.data.materials.get("TEAMON_Robot_White")
rose = bpy.data.materials.get("TEAMON_Robot_Joint_Rose")
if None in (output, composition_root, keycap, text, white, rose):
    raise RuntimeError("TEAMON ORCA material checkpoint is incomplete")

# Remove the rejected ORCA donor from the working scene while preserving the
# previous checkpoint on disk.
for obj in list(bpy.data.objects):
    if obj.name.startswith("TEAMON_ORCA_") or obj.name == "TEAMON_AbilityHandRoot":
        bpy.data.objects.remove(obj, do_unlink=True)

temp = bpy.data.collections.new("TEAMON_REBELIA_IMPORT")
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
hand_root["pose"] = "index extended; middle/ring/little progressively curled"

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
        modifier.ratio = 0.22 if source_name == "Cover Down V2" else 0.32
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

# Rigid segment hierarchy around the actual Rebelia V2 cover boundaries.
finger_roots = {}
for finger_name, data in FINGER_DATA.items():
    mcp = make_empty(f"TEAMON_Rebelia_{finger_name}_MCP", data["pivots"][0], hand_root, output)
    pip = make_empty(f"TEAMON_Rebelia_{finger_name}_PIP", data["pivots"][1], mcp, output)
    dip = make_empty(f"TEAMON_Rebelia_{finger_name}_DIP", data["pivots"][2], pip, output)
    finger_roots[finger_name] = (mcp, pip, dip)
    for part_name, pivot in zip(data["objects"], (mcp, pip, dip)):
        parent_keep_world(parts[part_name], pivot)
    for pivot, angle in zip((mcp, pip, dip), data["angles"]):
        pivot.rotation_euler.x = math.radians(angle)
    make_joint(f"TEAMON_Rebelia_{finger_name}_MCP_Joint", data["pivots"][0], mcp, output, rose)
    make_joint(f"TEAMON_Rebelia_{finger_name}_PIP_Joint", data["pivots"][1], pip, output, rose)
    make_joint(f"TEAMON_Rebelia_{finger_name}_DIP_Joint", data["pivots"][2], dip, output, rose)

finger_part_names = {name for data in FINGER_DATA.values() for name in data["objects"]}
for source_name, obj in parts.items():
    if source_name not in finger_part_names:
        parent_keep_world(obj, hand_root)

# Orient the ready-made dorsal shells toward the hero camera. Rebelia is Z-long,
# X-wide and its dorsal surface points toward -Y.
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

index_tip = parts["Distal Cover V4"]
index_bounds = world_bounds([index_tip])
key_bounds = world_bounds([keycap])
index_contact = Vector(
    (
        (index_bounds["min"][0] + index_bounds["max"][0]) * 0.5,
        (index_bounds["min"][1] + index_bounds["max"][1]) * 0.5,
        index_bounds["min"][2],
    )
)
contact_target = Vector((1.95, -0.56, key_bounds["max"][2] + 0.004))
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

# The previous word ran away from the diagonal used in the reference.
text.rotation_euler.z = math.radians(90.0)

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

print(
    json.dumps(
        {
            "preview": str(PREVIEW_PATH),
            "blend": str(BLEND_PATH),
            "parts": len(parts),
            "hand_bounds": world_bounds([obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_Rebelia_") and obj.type == "MESH"]),
        },
        ensure_ascii=False,
    )
)
