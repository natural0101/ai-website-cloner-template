from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v42_palm_thumb.blend"
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
HERO_PATH = PREVIEW_ROOT / "teamon-v42-palm-thumb-hero.png"
LEFT_PATH = PREVIEW_ROOT / "teamon-v42-palm-thumb-left.png"
SIDE_PATH = PREVIEW_ROOT / "teamon-v42-palm-thumb-side.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v42_build_report.json"

for directory in (BLEND_PATH.parent, PREVIEW_ROOT, REPORT_PATH.parent):
    directory.mkdir(parents=True, exist_ok=True)


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def apply_scale(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


scene = bpy.context.scene
camera = bpy.data.objects["TEAMON_Camera"]
hand_root = bpy.data.objects["TEAMON_v41_HandPressGroup"]
keycap = bpy.data.objects["TEAMON_Keycap"]
output = bpy.data.collections["TEAMON_OUTPUT"]
white = bpy.data.materials["TEAMON_Robot_White"]
dark = bpy.data.materials["TEAMON_Robot_Joint_Dark"]

for name in (
    "TEAMON_v41_CuffShell",
    "TEAMON_v41_PalmShell",
    "TEAMON_v41_PalmInset",
    "TEAMON_v41_WristSeam",
):
    obj = bpy.data.objects[name]
    obj.hide_render = True
    obj.hide_set(True)
    obj["export"] = False

camera_q = camera.matrix_world.to_quaternion()
camera_right = (camera_q @ Vector((1.0, 0.0, 0.0))).normalized()
camera_up = (camera_q @ Vector((0.0, 1.0, 0.0))).normalized()
camera_back = (camera_q @ Vector((0.0, 0.0, 1.0))).normalized()

keycap_top = bounds([keycap])["max"][2]
anchor_world = Vector((0.800, 0.900, keycap_top + 0.18)) + hand_root.location
anchor_ndc = world_to_camera_view(scene, camera, anchor_world)
right_ndc = world_to_camera_view(scene, camera, anchor_world + camera_right)
up_ndc = world_to_camera_view(scene, camera, anchor_world + camera_up)
ndc_per_world_x = right_ndc.x - anchor_ndc.x
ndc_per_world_y = up_ndc.y - anchor_ndc.y


def screen_point(x: float, y_from_top: float, depth: float = 0.0) -> Vector:
    dx = (x - anchor_ndc.x) / ndc_per_world_x
    dy = ((1.0 - y_from_top) - anchor_ndc.y) / ndc_per_world_y
    return anchor_world + camera_right * dx + camera_up * dy + camera_back * depth


def screen_dimensions(width: float, height: float) -> tuple[float, float]:
    return width / abs(ndc_per_world_x), height / abs(ndc_per_world_y)


def add_ellipsoid(name: str, x: float, y: float, width: float, height: float, depth: float, depth_offset: float, material: bpy.types.Material, role: str) -> bpy.types.Object:
    center = screen_point(x, y, depth_offset)
    dim_x, dim_y = screen_dimensions(width, height)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.5, location=center)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, output)
    rotation = Matrix((camera_right, camera_up, camera_back)).transposed().to_4x4()
    obj.matrix_world = Matrix.Translation(center) @ rotation
    obj.dimensions = (dim_x, dim_y, depth)
    apply_scale(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, hand_root)
    obj["export"] = True
    obj["role"] = role
    return obj


def add_round_panel(name: str, x: float, y: float, width: float, height: float, depth: float, depth_offset: float, material: bpy.types.Material, role: str, bevel_factor: float = 0.42) -> bpy.types.Object:
    center = screen_point(x, y, depth_offset)
    dim_x, dim_y = screen_dimensions(width, height)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, output)
    rotation = Matrix((camera_right, camera_up, camera_back)).transposed().to_4x4()
    obj.matrix_world = Matrix.Translation(center) @ rotation
    obj.dimensions = (dim_x, dim_y, depth)
    apply_scale(obj)
    bevel = obj.modifiers.new("TEAMON_v42_DeepRound", "BEVEL")
    bevel.width = min(dim_x, dim_y, depth) * bevel_factor
    bevel.segments = 10
    bevel.affect = "EDGES"
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, hand_root)
    obj["export"] = True
    obj["role"] = role
    return obj


new_shells = [
    add_round_panel("TEAMON_v42_CroppedForearmShell", 1.065, 0.485, 0.245, 0.470, 1.18, 0.02, white, "off-crop rounded rectangular forearm", 0.46),
    add_ellipsoid("TEAMON_v42_PalmDome", 0.922, 0.465, 0.245, 0.405, 1.10, 0.00, white, "continuous dorsal palm dome"),
    add_round_panel("TEAMON_v42_DorsalPlate", 0.900, 0.430, 0.170, 0.270, 0.72, 0.26, white, "segmented raised dorsal plate", 0.44),
    add_ellipsoid("TEAMON_v42_ThenarPad", 0.895, 0.602, 0.130, 0.170, 0.82, 0.31, white, "thumb-to-palm transition pad"),
    add_round_panel("TEAMON_v42_WristSeam", 0.988, 0.490, 0.022, 0.325, 1.03, 0.16, dark, "recessed wrist seam", 0.48),
]

# Pull the dedicated thumb in front of the palm and keep it in the lower-right
# silhouette instead of letting the palm hide it.
thumb_objects = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_Thumb_")]
for obj in thumb_objects:
    world = obj.matrix_world.copy()
    world.translation += camera_back * 0.72 + camera_right * 0.10 - camera_up * 0.05
    obj.matrix_world = world

bpy.context.view_layer.update()
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.frame_set(1)

hero_matrix = camera.matrix_world.copy()
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

visible_hand = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(("TEAMON_v41_", "TEAMON_v42_")) and not obj.hide_render]
hand_box = bounds(visible_hand)
hand_center = Vector(tuple((hand_box["min"][axis] + hand_box["max"][axis]) * 0.5 for axis in range(3)))
camera_offset = camera.location - hand_center
for angle_degrees, path in ((-20.0, LEFT_PATH), (42.0, SIDE_PATH)):
    camera.location = hand_center + Matrix.Rotation(math.radians(angle_degrees), 4, camera_up) @ camera_offset
    camera.rotation_euler = (hand_center - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
camera.matrix_world = hero_matrix
bpy.context.view_layer.update()

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

index_objects = [obj for obj in visible_hand if "Index_Shell" in obj.name]
final_gap = bounds(index_objects)["min"][2] - keycap_top
tip_projection = world_to_camera_view(scene, camera, screen_point(0.550, 0.435))
triangles = 0
for obj in visible_hand:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)

report = {
    "stage": "MATERIAL_PREVIEW",
    "status": "requires_visual_review_before_export",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(LEFT_PATH), str(SIDE_PATH)],
    "visible_hand_meshes": len(visible_hand),
    "triangles": triangles,
    "contact_gap": final_gap,
    "contact_pass": abs(final_gap - 0.004) <= 0.002,
    "contact_projection": {"x": tip_projection.x, "y_from_top": 1.0 - tip_projection.y},
    "palm_fix": "v41 slabs hidden; rounded cropped cuff, palm dome, dorsal plate and thenar pad added",
    "thumb_fix": "thumb moved toward hero camera and slightly right/down",
    "known_pending": ["visual signoff", "animation wiring", "GLB export", "browser validation"],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
