from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template")
DONOR_BLEND = PROJECT_ROOT / "blender-workbench" / "vendor" / "rebelia-v2" / "Rebelia - Hierarchic.blend"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v40_rebelia_clean.blend"
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
HERO_PATH = PREVIEW_ROOT / "teamon-v40-rebelia-clean-hero.png"
LEFT_PATH = PREVIEW_ROOT / "teamon-v40-rebelia-clean-left.png"
SIDE_PATH = PREVIEW_ROOT / "teamon-v40-rebelia-clean-side.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v40_build_report.json"

for directory in (BLEND_PATH.parent, PREVIEW_ROOT, REPORT_PATH.parent):
    directory.mkdir(parents=True, exist_ok=True)


DONOR_NAMES = [
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
        "angles_y": (0.0, 0.0, 0.0),
    },
    "Middle": {
        "objects": ("Middle Proximal Cover V4", "Middle Medial Cover V4", "Middle Distal Cover V4"),
        "pivots": ((0.0120, -0.0030, -0.0394), (0.0120, -0.0030, 0.0125), (0.0120, -0.0030, 0.0415)),
        "angles_y": (-18.0, 62.0, 38.0),
    },
    "Ring": {
        "objects": ("Ring Proximal Cover V4", "Ring Medial Cover V4", "Ring Distal Cover V4"),
        "pivots": ((-0.0090, -0.0030, -0.0442), (-0.0090, -0.0030, 0.0035), (-0.0090, -0.0030, 0.0301)),
        "angles_y": (-23.0, 72.0, 44.0),
    },
    "Little": {
        "objects": ("Little Proximal Cover V4", "Little Medial Cover V4", "Little Distal Cover V4"),
        "pivots": ((-0.0318, -0.0030, -0.0558), (-0.0318, -0.0030, -0.0168), (-0.0318, -0.0030, 0.0050)),
        "angles_y": (-28.0, 80.0, 50.0),
    },
}


def set_principled(material: bpy.types.Material, socket_names: tuple[str, ...], value) -> None:
    material.use_nodes = True
    bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    for name in socket_names:
        socket = bsdf.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            break


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def world_points(obj: bpy.types.Object) -> list[Vector]:
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    points = [point for obj in objects for point in world_points(obj)]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


def make_empty(name: str, source_location: tuple[float, float, float], parent: bpy.types.Object, collection: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.matrix_world = Matrix.Translation(Vector(source_location))
    parent_keep_world(obj, parent)
    return obj


def make_joint(name: str, source_location: tuple[float, float, float], radius: float, parent: bpy.types.Object, collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=16, radius=radius, location=source_location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    obj.scale.y = 1.16
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, parent)
    obj["export"] = True
    obj["role"] = "articulated rose joint"
    return obj


def make_rounded_box(name: str, source_location: tuple[float, float, float], dimensions: tuple[float, float, float], bevel_width: float, parent: bpy.types.Object, collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=source_location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    obj.dimensions = dimensions
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("TEAMON_RoundedShell", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 8
    bevel.affect = "EDGES"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, parent)
    obj["export"] = True
    obj["role"] = "compact segmented wrist shell"
    return obj


def camera_look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
camera = bpy.data.objects["TEAMON_Camera"]
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
keycap = bpy.data.objects["TEAMON_Keycap"]
text_obj = bpy.data.objects["TEAMON_Text"]
output = bpy.data.collections.get("TEAMON_OUTPUT")
if output is None:
    output = bpy.data.collections.new("TEAMON_OUTPUT")
    scene.collection.children.link(output)

white = bpy.data.materials.get("TEAMON_Robot_White") or bpy.data.materials.new("TEAMON_Robot_White")
rose = bpy.data.materials.get("TEAMON_Robot_Joint_Rose") or bpy.data.materials.new("TEAMON_Robot_Joint_Rose")
set_principled(white, ("Base Color",), (0.94, 0.955, 0.98, 1.0))
set_principled(white, ("Metallic",), 0.0)
set_principled(white, ("Roughness",), 0.27)
set_principled(white, ("Coat Weight", "Clearcoat"), 0.32)
set_principled(white, ("Coat Roughness", "Clearcoat Roughness"), 0.07)
set_principled(rose, ("Base Color",), (0.58, 0.24, 0.29, 1.0))
set_principled(rose, ("Metallic",), 0.05)
set_principled(rose, ("Roughness",), 0.34)

# Preserve every earlier checkpoint object in the file, but remove it from the
# hero render. The v20 button, studio, camera, typography and lights remain intact.
for obj in bpy.data.objects:
    if obj.name.startswith("TEAMON_Ability_") or obj.name.startswith("TEAMON_Ada_") or obj.name == "TEAMON_HandPressGroup":
        obj.hide_render = True
        obj.hide_set(True)
        obj["export"] = False

source_collection = bpy.data.collections.new("SOURCE_Rebelia_V2_v40")
scene.collection.children.link(source_collection)
source_collection.hide_render = True
source_collection.hide_viewport = True

requested_names = tuple(DONOR_NAMES)
with bpy.data.libraries.load(str(DONOR_BLEND), link=False) as (library, target):
    missing = [name for name in requested_names if name not in library.objects]
    if missing:
        raise RuntimeError(f"Rebelia donor objects missing: {missing}")
    target.objects = list(requested_names)

source_objects: dict[str, bpy.types.Object] = {}
for source_name, source_obj in zip(requested_names, target.objects):
    if source_obj is None:
        raise RuntimeError(f"Rebelia donor load failed: {source_name}")
    source_collection.objects.link(source_obj)
    source_obj.hide_render = True
    source_obj.hide_set(True)
    source_obj["source_preserved"] = True
    source_objects[source_name] = source_obj

bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()

hand_root = bpy.data.objects.new("TEAMON_Rebelia_v40_HandRoot", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["asset_source"] = "https://github.com/opsobot/rebelia"
hand_root["asset_revision"] = "41f2708999a01f8dd815642889281cea8bb1c0e9"
hand_root["asset_license"] = "CERN-OHL-S-2.0"
hand_root["representation_mode"] = "HYBRID_HERO"
hand_root["pose"] = "fixed index contact; middle/ring/little screen-plane curl; dedicated thumb"

parts: dict[str, bpy.types.Object] = {}
for source_name in requested_names:
    source_obj = source_objects[source_name]
    evaluated = source_obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=False, depsgraph=depsgraph)
    obj = bpy.data.objects.new(f"TEAMON_Rebelia_v40_{source_name}", mesh)
    output.objects.link(obj)
    obj.matrix_world = source_obj.matrix_world.copy()
    obj.data.materials.clear()
    obj.data.materials.append(white)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["rebelia_source_object"] = source_name
    obj["export"] = True
    parts[source_name] = obj

print("TEAMON_V40_PART_KEYS", json.dumps(sorted(parts.keys()), ensure_ascii=False))

# Build true segment hierarchies. Rotating about donor Y bends the fingers in
# the camera plane; the rejected v8/v10 work rotated about X and hid the curl in depth.
finger_roots: dict[str, tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]] = {}
for finger_name, data in FINGER_DATA.items():
    mcp = make_empty(f"TEAMON_Rebelia_v40_{finger_name}_MCP", data["pivots"][0], hand_root, output)
    pip = make_empty(f"TEAMON_Rebelia_v40_{finger_name}_PIP", data["pivots"][1], mcp, output)
    dip = make_empty(f"TEAMON_Rebelia_v40_{finger_name}_DIP", data["pivots"][2], pip, output)
    finger_roots[finger_name] = (mcp, pip, dip)
    for object_name, pivot in zip(data["objects"], (mcp, pip, dip)):
        parent_keep_world(parts[object_name], pivot)
    for pivot, angle in zip((mcp, pip, dip), data["angles_y"]):
        pivot.rotation_euler.y = math.radians(angle)
    for suffix, location, pivot, radius in zip(("MCP", "PIP", "DIP"), data["pivots"], (mcp, pip, dip), (0.0105, 0.0096, 0.0088)):
        make_joint(f"TEAMON_Rebelia_v40_{finger_name}_{suffix}_Joint", location, radius, pivot, output, rose)

finger_part_names = {name for data in FINGER_DATA.values() for name in data["objects"]}
for source_name in ("Hand Back Cover - Safety", "Palm V2 - S1 - Safety"):
    parent_keep_world(parts[source_name], hand_root)

# Keep the real Rebelia thumb geometry and rotate the whole thumb assembly into
# the lower-right-to-left gesture of the reference.
thumb_pivot = make_empty("TEAMON_Rebelia_v40_ThumbPivot", (0.047, -0.003, -0.105), hand_root, output)
for source_name in ("ThumbBase V3 - Safety.002", "Thumb Proximal Cover V4", "Thumb Distal Cover V4"):
    parent_keep_world(parts[source_name], thumb_pivot)
thumb_pivot.rotation_euler.y = math.radians(-52.0)
thumb_pivot.location += Vector((-0.004, -0.002, -0.012))
make_joint("TEAMON_Rebelia_v40_ThumbBase_Joint", (0.047, -0.003, -0.105), 0.013, thumb_pivot, output, rose)

# A pair of overlapping rounded shells extends the donor palm beyond the crop.
# They are deliberately rectangular and segmented, avoiding the v39 oval prosthesis.
palm_bridge = make_rounded_box(
    "TEAMON_Rebelia_v40_PalmBridge",
    (-0.004, 0.002, -0.087),
    (0.128, 0.052, 0.094),
    0.018,
    hand_root,
    output,
    white,
)
cuff_shell = make_rounded_box(
    "TEAMON_Rebelia_v40_CuffShell",
    (-0.012, 0.004, -0.184),
    (0.158, 0.060, 0.128),
    0.024,
    hand_root,
    output,
    white,
)

# Map the donor hand into the locked hero camera. +Z is finger-long, +X is
# knuckle-width. The index extends left while little finger rises upward.
camera_rotation = camera.matrix_world.to_quaternion()
camera_right = (camera_rotation @ Vector((1.0, 0.0, 0.0))).normalized()
camera_up = (camera_rotation @ Vector((0.0, 1.0, 0.0))).normalized()
target_z = (-camera_right - camera_up * 0.025).normalized()
target_x = (-camera_up - target_z * (-camera_up).dot(target_z)).normalized()
target_y = target_z.cross(target_x).normalized()
rotation = Matrix((target_x, target_y, target_z)).transposed()
hand_scale = 18.8
source_contact = Vector((0.0319, -0.0030, 0.0580))
keycap_top = bounds([keycap])["max"][2]
contact_target = Vector((0.800, 0.900, keycap_top + 0.004))
hand_root.matrix_world = (
    Matrix.Translation(contact_target)
    @ rotation.to_4x4()
    @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
    @ Matrix.Translation(-source_contact)
)
bpy.context.view_layer.update()

# Exact physical re-seat on the keycap while preserving the locked x/y anchor.
index_distal = parts["Distal Cover V4"]
vertical_gap = bounds([index_distal])["min"][2] - keycap_top
hand_root.location.z += 0.004 - vertical_gap
bpy.context.view_layer.update()

# TEAMON typography and the button/camera/studio remain the approved v20 values.
text_obj.rotation_euler.z = math.radians(90.0)
scene.camera = camera
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.frame_set(1)

hero_camera_matrix = camera.matrix_world.copy()
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hand_meshes = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_Rebelia_v40_") and obj.type == "MESH"]
hand_box = bounds(hand_meshes)
hand_center = Vector(tuple((hand_box["min"][axis] + hand_box["max"][axis]) * 0.5 for axis in range(3)))

# Two diagnostic oblique views. These are QA evidence only; the hero camera is restored.
offset = camera.location - hand_center
for angle_degrees, path in ((-24.0, LEFT_PATH), (52.0, SIDE_PATH)):
    camera.location = hand_center + Matrix.Rotation(math.radians(angle_degrees), 4, camera_up) @ offset
    camera_look_at(camera, hand_center)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
camera.matrix_world = hero_camera_matrix
scene.camera = camera
bpy.context.view_layer.update()

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

contact_ndc = world_to_camera_view(scene, camera, index_distal.matrix_world @ Vector((0.0, 0.0, 0.0)))
final_gap = bounds([index_distal])["min"][2] - keycap_top
triangle_count = 0
for obj in hand_meshes:
    obj.data.calc_loop_triangles()
    triangle_count += len(obj.data.loop_triangles)

report = {
    "stage": "MATERIAL_PREVIEW",
    "status": "requires_visual_review_before_export",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(LEFT_PATH), str(SIDE_PATH)],
    "source_blend": str(DONOR_BLEND),
    "source_license": "CERN-OHL-S-2.0",
    "source_objects_preserved": len(source_objects),
    "output_meshes": len(hand_meshes),
    "triangles_before_web_optimization": triangle_count,
    "contact_gap": final_gap,
    "contact_pass": abs(final_gap - 0.004) <= 0.002,
    "contact_projection": {"x": contact_ndc.x, "y_from_top": 1.0 - contact_ndc.y},
    "hand_bounds": hand_box,
    "do_not_change": [
        "TEAMON button dimensions/material",
        "camera framing",
        "studio lighting/background",
        "click animation timing",
    ],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
