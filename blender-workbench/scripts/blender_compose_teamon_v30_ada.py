from __future__ import annotations

import json
import os
from math import radians
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(
    os.environ.get(
        "TEAMON_PROJECT_ROOT",
        r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template",
    )
)
ADA_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v12_ada_pose_f.blend"
OUTPUT_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v39_ada_composed.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v39-ada-composed-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v39_ada_composed_report.json"


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def remove_old_hand() -> None:
    for obj in list(bpy.data.objects):
        if obj.name.startswith("TEAMON_Ability_"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name == "TEAMON_Ability_Pose_OUTPUT":
            bpy.data.collections.remove(collection)


def append_ada_collections() -> None:
    collection_names = ["SOURCE_Ada_v1_1", "TEAMON_Ada_Pose_OUTPUT"]
    with bpy.data.libraries.load(str(ADA_BLEND), link=False) as (available, requested):
        missing = sorted(set(collection_names) - set(available.collections))
        if missing:
            raise RuntimeError(f"Missing Ada collections: {missing}")
        requested.collections = collection_names
    for collection in requested.collections:
        if collection is not None and collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(collection)


def material(name: str, color: tuple[float, float, float, float], roughness: float, coat: float) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    result = existing or bpy.data.materials.new(name)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["IOR"].default_value = 1.45
    shader.inputs["Coat Weight"].default_value = coat
    shader.inputs["Coat Roughness"].default_value = 0.07
    return result


def fingertip_contact_local(index_obj: bpy.types.Object) -> Vector:
    points = [index_obj.matrix_world @ vertex.co for vertex in index_obj.data.vertices]
    minimum_x = min(point.x for point in points)
    maximum_x = max(point.x for point in points)
    tip_band = minimum_x + (maximum_x - minimum_x) * 0.09
    tip_points = [point for point in points if point.x <= tip_band]
    minimum_z = min(point.z for point in tip_points)
    contact_band = [point for point in tip_points if point.z <= minimum_z + 0.035]
    return sum(contact_band, Vector()) / len(contact_band)


remove_old_hand()
append_ada_collections()

composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
keycap = bpy.data.objects["TEAMON_Keycap"]
hand_root = bpy.data.objects["TEAMON_Ada_HandRoot"]
index_obj = bpy.data.objects["TEAMON_Ada_Index"]
thumb_obj = bpy.data.objects["TEAMON_Ada_Thumb"]

bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=(0.0, 0.0, 0.0))
forearm = bpy.context.object
forearm.name = "TEAMON_Ada_ForearmShell"
for collection in list(forearm.users_collection):
    collection.objects.unlink(forearm)
bpy.data.collections["TEAMON_Ada_Pose_OUTPUT"].objects.link(forearm)
forearm.data.transform(
    Matrix.Translation(Vector((2.25, 1.10, 0.58)))
    @ Matrix.Rotation(radians(45.0), 4, "Z")
    @ Matrix.Diagonal(Vector((2.0, 0.55, 0.50, 1.0)))
)
forearm.parent = hand_root
forearm["semantic_part"] = "forearm_shell"

white = material("TEAMON_Robot_White_Ada", (0.94, 0.955, 0.98, 1.0), 0.28, 0.34)
joint_rose = material("TEAMON_Robot_Joint_Rose_Ada", (0.55, 0.22, 0.25, 1.0), 0.31, 0.18)
ada_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith("TEAMON_Ada_")]
for obj in ada_meshes:
    obj.data.materials.clear()
    obj.data.materials.append(joint_rose if "_Joint" in obj.name else white)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["abt_export"] = True

source_collection = bpy.data.collections.get("SOURCE_Ada_v1_1")
if source_collection:
    source_collection.hide_render = True
    source_collection.hide_viewport = True

thumb_points = [vertex.co.copy() for vertex in thumb_obj.data.vertices]
thumb_max_y = max(point.y for point in thumb_points)
thumb_min_y = min(point.y for point in thumb_points)
thumb_base_points = [
    point for point in thumb_points
    if point.y >= thumb_max_y - (thumb_max_y - thumb_min_y) * 0.10
]
thumb_pivot = sum(thumb_base_points, Vector()) / len(thumb_base_points)
thumb_obj.data.transform(
    Matrix.Translation(thumb_pivot)
    @ Matrix.Rotation(radians(-58.0), 4, "Z")
    @ Matrix.Translation(-thumb_pivot)
)
thumb_obj.data.update()

finger_offsets = {
    "Middle": Vector((0.12, -0.14, -0.90)),
    "Ring": Vector((0.25, -0.30, -0.55)),
    "Little": Vector((0.38, -0.46, -0.20)),
}
for finger_name, offset in finger_offsets.items():
    for obj in ada_meshes:
        if obj.name.startswith(f"TEAMON_Ada_{finger_name}"):
            obj.data.transform(Matrix.Translation(offset))
            obj.data.update()

bpy.context.view_layer.update()
contact_local = fingertip_contact_local(index_obj)
keycap_top = world_bounds(keycap)[1].z
target_contact = Vector((0.54, 0.78, keycap_top + 0.033))
scale = 1.70
rotation = Matrix.Rotation(radians(-7.0), 4, "Z")
hand_matrix = Matrix.Translation(target_contact) @ rotation @ Matrix.Scale(scale, 4) @ Matrix.Translation(-contact_local)
hand_root.parent = composition_root
hand_root.matrix_world = hand_matrix
hand_root["asset_source"] = str(ADA_BLEND)
hand_root["asset_revision"] = "2dbf3cc6c5df112066f12c11af1d001e319a766f"
hand_root["asset_license"] = "CC BY-SA 4.0"
hand_root["asset_attribution"] = "OpenBionics Ada Hand v1.1, adapted for TEAMON"
hand_root["abt_export"] = True

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW_PATH)
scene.frame_set(1)
bpy.ops.render.render(write_still=True)

hand_min, hand_max = world_bounds(hand_root.children[0])
all_hand_points = [obj.matrix_world @ Vector(corner) for obj in ada_meshes for corner in obj.bound_box]
hand_min = Vector(tuple(min(point[axis] for point in all_hand_points) for axis in range(3)))
hand_max = Vector(tuple(max(point[axis] for point in all_hand_points) for axis in range(3)))
index_min, index_max = world_bounds(index_obj)
report = {
    "stage": "COMPOSITION",
    "source": str(ADA_BLEND),
    "source_license": "CC BY-SA 4.0",
    "output": str(OUTPUT_BLEND),
    "preview": str(PREVIEW_PATH),
    "target_contact": list(target_contact),
    "contact_source_local": list(contact_local),
    "scale": scale,
    "rotation_z_degrees": -7.0,
    "thumb_rotation_z_degrees": -58.0,
    "finger_offsets": {name: list(offset) for name, offset in finger_offsets.items()},
    "hand_bounds_world": {"min": list(hand_min), "max": list(hand_max)},
    "index_bounds_world": {"min": list(index_min), "max": list(index_max)},
    "mesh_count": len(ada_meshes),
    "status": "requires_visual_review",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
print(json.dumps(report, ensure_ascii=False, indent=2))
