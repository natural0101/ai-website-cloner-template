from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v41_segmented_reference.blend"
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
HERO_PATH = PREVIEW_ROOT / "teamon-v41-segmented-reference-hero.png"
LEFT_PATH = PREVIEW_ROOT / "teamon-v41-segmented-reference-left.png"
SIDE_PATH = PREVIEW_ROOT / "teamon-v41-segmented-reference-side.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v41_build_report.json"

for directory in (BLEND_PATH.parent, PREVIEW_ROOT, REPORT_PATH.parent):
    directory.mkdir(parents=True, exist_ok=True)


def set_principled(material: bpy.types.Material, names: tuple[str, ...], value) -> None:
    material.use_nodes = True
    bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def world_bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return {
        "min": [min(point[axis] for point in points) for axis in range(3)],
        "max": [max(point[axis] for point in points) for axis in range(3)],
    }


def apply_scale(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


scene = bpy.context.scene
camera = bpy.data.objects["TEAMON_Camera"]
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
keycap = bpy.data.objects["TEAMON_Keycap"]
text_obj = bpy.data.objects["TEAMON_Text"]
output = bpy.data.collections.get("TEAMON_OUTPUT") or bpy.data.collections.new("TEAMON_OUTPUT")
if output.name not in {collection.name for collection in scene.collection.children}:
    scene.collection.children.link(output)

for obj in bpy.data.objects:
    if obj.name.startswith(("TEAMON_Ability_", "TEAMON_Ada_", "TEAMON_Rebelia_")) or obj.name == "TEAMON_HandPressGroup":
        obj.hide_render = True
        obj.hide_set(True)
        obj["export"] = False

white = bpy.data.materials.get("TEAMON_Robot_White") or bpy.data.materials.new("TEAMON_Robot_White")
rose = bpy.data.materials.get("TEAMON_Robot_Joint_Rose") or bpy.data.materials.new("TEAMON_Robot_Joint_Rose")
dark = bpy.data.materials.get("TEAMON_Robot_Joint_Dark") or bpy.data.materials.new("TEAMON_Robot_Joint_Dark")
set_principled(white, ("Base Color",), (0.955, 0.968, 0.99, 1.0))
set_principled(white, ("Metallic",), 0.0)
set_principled(white, ("Roughness",), 0.25)
set_principled(white, ("Coat Weight", "Clearcoat"), 0.34)
set_principled(white, ("Coat Roughness", "Clearcoat Roughness"), 0.065)
set_principled(rose, ("Base Color",), (0.47, 0.16, 0.20, 1.0))
set_principled(rose, ("Metallic",), 0.10)
set_principled(rose, ("Roughness",), 0.30)
set_principled(dark, ("Base Color",), (0.055, 0.045, 0.052, 1.0))
set_principled(dark, ("Metallic",), 0.20)
set_principled(dark, ("Roughness",), 0.28)

hand_root = bpy.data.objects.new("TEAMON_v41_HandPressGroup", None)
output.objects.link(hand_root)
hand_root.parent = composition_root
hand_root["representation_mode"] = "HYBRID_HERO"
hand_root["reference_pose"] = "fixed screen-space index contact with curled stepped fingers"
hand_root["source_asset"] = "Rebelia V2 form study plus reference-driven production shells"
hand_root["source_license"] = "CERN-OHL-S-2.0"

camera_q = camera.matrix_world.to_quaternion()
camera_right = (camera_q @ Vector((1.0, 0.0, 0.0))).normalized()
camera_up = (camera_q @ Vector((0.0, 1.0, 0.0))).normalized()
camera_back = (camera_q @ Vector((0.0, 0.0, 1.0))).normalized()

keycap_top = world_bounds([keycap])["max"][2]
anchor_world = Vector((0.800, 0.900, keycap_top + 0.18))
anchor_ndc = world_to_camera_view(scene, camera, anchor_world)
right_ndc = world_to_camera_view(scene, camera, anchor_world + camera_right)
up_ndc = world_to_camera_view(scene, camera, anchor_world + camera_up)
ndc_per_world_x = right_ndc.x - anchor_ndc.x
ndc_per_world_y = up_ndc.y - anchor_ndc.y
if abs(ndc_per_world_x) < 1e-6 or abs(ndc_per_world_y) < 1e-6:
    raise RuntimeError("Unable to calibrate TEAMON hero camera screen plane")


def screen_point(x: float, y_from_top: float, depth: float = 0.0) -> Vector:
    dx = (x - anchor_ndc.x) / ndc_per_world_x
    dy = ((1.0 - y_from_top) - anchor_ndc.y) / ndc_per_world_y
    return anchor_world + camera_right * dx + camera_up * dy + camera_back * depth


def screen_width(value: float) -> float:
    return value / abs(ndc_per_world_y)


def add_rounded_box_world(name: str, center: Vector, axis_x: Vector, axis_y: Vector, axis_z: Vector, dimensions: tuple[float, float, float], bevel_width: float, material: bpy.types.Material, role: str) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, output)
    rotation = Matrix((axis_x.normalized(), axis_y.normalized(), axis_z.normalized())).transposed().to_4x4()
    obj.matrix_world = Matrix.Translation(center) @ rotation
    obj.dimensions = dimensions
    apply_scale(obj)
    bevel = obj.modifiers.new("TEAMON_SoftRobotShell", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 8
    bevel.affect = "EDGES"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, hand_root)
    obj["export"] = True
    obj["role"] = role
    return obj


def add_screen_panel(name: str, x: float, y: float, width_x: float, height_y: float, depth_world: float, material: bpy.types.Material, role: str, depth_offset: float = 0.0) -> bpy.types.Object:
    center = screen_point(x, y, depth_offset)
    dim_x = width_x / abs(ndc_per_world_x)
    dim_y = height_y / abs(ndc_per_world_y)
    return add_rounded_box_world(
        name,
        center,
        camera_right,
        camera_up,
        camera_back,
        (dim_x, dim_y, depth_world),
        min(dim_x, dim_y, depth_world) * 0.23,
        material,
        role,
    )


def add_joint(name: str, x: float, y: float, radius_norm: float, depth_offset: float = -0.06) -> bpy.types.Object:
    center = screen_point(x, y, depth_offset)
    radius = screen_width(radius_norm)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=18, radius=radius, location=center)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, output)
    obj.scale = (1.0, 0.78, 1.0)
    apply_scale(obj)
    obj.data.materials.append(rose)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    parent_keep_world(obj, hand_root)
    obj["export"] = True
    obj["role"] = "visible rose articulation"
    return obj


def add_segment(name: str, start_xy: tuple[float, float], end_xy: tuple[float, float], width_norm: float, depth_world: float = 0.42, depth_offset: float = 0.0) -> bpy.types.Object:
    start = screen_point(*start_xy, depth_offset)
    end = screen_point(*end_xy, depth_offset)
    axis_x = (end - start).normalized()
    axis_z = camera_back
    axis_y = axis_z.cross(axis_x).normalized()
    length = (end - start).length
    width = screen_width(width_norm)
    return add_rounded_box_world(
        name,
        (start + end) * 0.5,
        axis_x,
        axis_y,
        axis_z,
        (length * 0.88, width, depth_world),
        min(width * 0.38, depth_world * 0.34),
        white,
        "rounded finger shell",
    )


hand_meshes: list[bpy.types.Object] = []

# Large palm/cuff bulk is pushed into the right crop. Two shells and four
# knuckle pads keep it mechanical instead of the swollen v39 mitten silhouette.
hand_meshes.append(add_screen_panel("TEAMON_v41_CuffShell", 1.015, 0.485, 0.255, 0.500, 0.78, white, "cropped forearm shell", 0.10))
hand_meshes.append(add_screen_panel("TEAMON_v41_PalmShell", 0.905, 0.455, 0.225, 0.410, 0.66, white, "segmented dorsal palm shell", 0.02))
hand_meshes.append(add_screen_panel("TEAMON_v41_PalmInset", 0.858, 0.455, 0.105, 0.315, 0.72, white, "raised palm edge shell", -0.035))

for index, (x, y) in enumerate(((0.815, 0.385), (0.855, 0.315), (0.900, 0.255), (0.945, 0.220))):
    hand_meshes.append(add_screen_panel(f"TEAMON_v41_KnucklePad_{index}", x, y, 0.075, 0.092, 0.76, white, "overlapping knuckle block", -0.055))
    hand_meshes.append(add_joint(f"TEAMON_v41_KnuckleJoint_{index}", x - 0.025, y + 0.028, 0.016, -0.09))

finger_paths = {
    "Index": [(0.550, 0.435), (0.615, 0.430), (0.685, 0.418), (0.775, 0.405)],
    "Middle": [(0.705, 0.430), (0.712, 0.353), (0.758, 0.300), (0.825, 0.335)],
    "Ring": [(0.758, 0.372), (0.772, 0.292), (0.818, 0.245), (0.885, 0.275)],
    "Little": [(0.815, 0.318), (0.835, 0.248), (0.885, 0.205), (0.950, 0.232)],
}
finger_widths = {"Index": 0.054, "Middle": 0.058, "Ring": 0.056, "Little": 0.052}
for finger_name, points in finger_paths.items():
    width = finger_widths[finger_name]
    for segment_index in range(3):
        hand_meshes.append(add_segment(f"TEAMON_v41_{finger_name}_Shell_{segment_index}", points[segment_index], points[segment_index + 1], width, 0.43, -0.02 * segment_index))
    for joint_index, point in enumerate(points[1:]):
        hand_meshes.append(add_joint(f"TEAMON_v41_{finger_name}_Joint_{joint_index}", point[0], point[1], width * 0.34, -0.085))

# Thumb stays under and to the right of the index, matching the reference crop.
thumb_points = [(0.748, 0.705), (0.815, 0.692), (0.868, 0.632), (0.905, 0.555)]
for segment_index in range(3):
    hand_meshes.append(add_segment(f"TEAMON_v41_Thumb_Shell_{segment_index}", thumb_points[segment_index], thumb_points[segment_index + 1], 0.068, 0.50, -0.01 * segment_index))
for joint_index, point in enumerate(thumb_points[1:]):
    hand_meshes.append(add_joint(f"TEAMON_v41_Thumb_Joint_{joint_index}", point[0], point[1], 0.024, -0.10))

# A dark recessed wrist seam appears only between the palm and off-crop cuff.
hand_meshes.append(add_screen_panel("TEAMON_v41_WristSeam", 0.970, 0.490, 0.030, 0.355, 0.73, dark, "recessed wrist seam", -0.07))

bpy.context.view_layer.update()

# Re-seat the lowest index shell point on the keycap; this changes only Z and
# leaves the locked screen-space pose essentially unchanged.
index_objects = [obj for obj in hand_meshes if "Index_Shell" in obj.name]
gap = world_bounds(index_objects)["min"][2] - keycap_top
hand_root.location.z += 0.004 - gap
bpy.context.view_layer.update()

text_obj.rotation_euler.z = math.radians(90.0)
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.camera = camera
scene.frame_set(1)

hero_matrix = camera.matrix_world.copy()
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

all_hand_meshes = [obj for obj in bpy.data.objects if obj.name.startswith("TEAMON_v41_") and obj.type == "MESH"]
hand_box = world_bounds(all_hand_meshes)
hand_center = Vector(tuple((hand_box["min"][axis] + hand_box["max"][axis]) * 0.5 for axis in range(3)))
camera_offset = camera.location - hand_center
for angle_degrees, path in ((-20.0, LEFT_PATH), (42.0, SIDE_PATH)):
    camera.location = hand_center + Matrix.Rotation(math.radians(angle_degrees), 4, camera_up) @ camera_offset
    camera.rotation_euler = (hand_center - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
camera.matrix_world = hero_matrix
scene.camera = camera
bpy.context.view_layer.update()

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

index_tip_world = screen_point(0.550, 0.435) + hand_root.location
index_tip_ndc = world_to_camera_view(scene, camera, index_tip_world)
final_gap = world_bounds(index_objects)["min"][2] - keycap_top
triangles = 0
for obj in all_hand_meshes:
    obj.data.calc_loop_triangles()
    triangles += len(obj.data.loop_triangles)

report = {
    "stage": "MATERIAL_PREVIEW",
    "status": "requires_visual_review_before_export",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(LEFT_PATH), str(SIDE_PATH)],
    "output_meshes": len(all_hand_meshes),
    "triangles": triangles,
    "contact_gap": final_gap,
    "contact_pass": abs(final_gap - 0.004) <= 0.002,
    "contact_projection": {"x": index_tip_ndc.x, "y_from_top": 1.0 - index_tip_ndc.y},
    "target_contact_projection": {"x": 0.550, "y_from_top": 0.435},
    "hand_bounds": hand_box,
    "known_pending": ["visual signoff", "animation wiring", "web decimation", "GLB export", "browser validation"],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
