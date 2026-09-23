from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_pose_d_attached_attempt01.blend"
OUTPUT_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_palm_pose_attempt02.blend"
HERO_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt02-palm-pose-hero.png"
FRONT_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt02-palm-pose-front.png"
SIDE_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt02-palm-pose-side.png"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt02_report.json"
QA_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt02_structural_qa.json"
QA_MODULES = WORKBENCH / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


EXPECTED_SOURCE_SHA256 = "6D7E45E04FCE5827CFDD2FF859B40EE3B65A6155A314C518009990E65C7578D9"
WORLD_AXIS_ROTATION_DEGREES = -7.5
JOINT_BRIDGE_WORLD_AXIS_ROTATION_DEGREES = -3.75
HAND_OBJECTS = tuple(
    name
    for name in (
        "TEAMON_Ada_ForearmShell",
        "TEAMON_Ada_Palm",
        "TEAMON_Ada_Thumb",
        "TEAMON_Ada_Index",
        "TEAMON_Ada_Index_Joint01",
        "TEAMON_Ada_Middle",
        "TEAMON_Ada_Middle_Joint01",
        "TEAMON_Ada_Middle_Joint02",
        "TEAMON_Ada_Middle_Joint03",
        "TEAMON_Ada_Ring",
        "TEAMON_Ada_Ring_Joint01",
        "TEAMON_Ada_Ring_Joint02",
        "TEAMON_Ada_Ring_Joint03",
        "TEAMON_Ada_Little",
        "TEAMON_Ada_Little_Joint01",
        "TEAMON_Ada_Little_Joint02",
        "TEAMON_Ada_Little_Joint03",
    )
)
POSE_GROUP = tuple(name for name in HAND_OBJECTS if name not in {"TEAMON_Ada_Index", "TEAMON_Ada_Index_Joint01"})
EXPECTED_CHANGED_GROUP = POSE_GROUP + ("TEAMON_Ada_Index_Joint01",)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def mesh_coordinate_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        digest.update(repr(tuple(round(float(value), 9) for value in vertex.co)).encode("ascii"))
    return digest.hexdigest().upper()


def topology_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    digest.update(f"{len(obj.data.vertices)}:{len(obj.data.edges)}:{len(obj.data.polygons)}".encode("ascii"))
    for edge in obj.data.edges:
        digest.update(f"e{edge.vertices[0]},{edge.vertices[1]};".encode("ascii"))
    for polygon in obj.data.polygons:
        digest.update(("p" + ",".join(str(index) for index in polygon.vertices) + ";").encode("ascii"))
    return digest.hexdigest().upper()


def matrix_values(matrix: Matrix) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix]


def action_signature() -> dict[str, object]:
    actions = {}
    for action in sorted(bpy.data.actions, key=lambda item: item.name):
        actions[action.name] = {
            "frame_range": [float(value) for value in action.frame_range],
            "slots": [getattr(slot, "identifier", repr(slot)) for slot in action.slots],
        }
    assignments = {
        obj.name: {
            "action": obj.animation_data.action.name,
            "slot": obj.animation_data.action_slot.identifier
            if getattr(obj.animation_data, "action_slot", None)
            else None,
        }
        for obj in bpy.data.objects
        if obj.animation_data and obj.animation_data.action
    }
    return {"actions": actions, "assignments": assignments}


def mesh_world_data(obj: bpy.types.Object) -> tuple[list[Vector], list[tuple[int, ...]]]:
    return (
        [obj.matrix_world @ vertex.co for vertex in obj.data.vertices],
        [tuple(polygon.vertices) for polygon in obj.data.polygons],
    )


def pair_metrics(first: bpy.types.Object, second: bpy.types.Object) -> dict[str, object]:
    first_points, first_polygons = mesh_world_data(first)
    second_points, second_polygons = mesh_world_data(second)
    first_bvh = BVHTree.FromPolygons(first_points, first_polygons, all_triangles=False)
    second_bvh = BVHTree.FromPolygons(second_points, second_polygons, all_triangles=False)
    distances = []
    for point in first_points:
        nearest = second_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    for point in second_points:
        nearest = first_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    return {
        "overlap_pairs": len(first_bvh.overlap(second_bvh)),
        "surface_distance": min(distances) if distances else None,
    }


def contact_metrics() -> dict[str, object]:
    index = bpy.data.objects["TEAMON_Ada_Index"]
    keycap = bpy.data.objects["TEAMON_Keycap"]
    metrics = pair_metrics(index, keycap)
    index_points, _ = mesh_world_data(index)
    keycap_points, _ = mesh_world_data(keycap)
    metrics["vertical_gap"] = min(point.z for point in index_points) - max(point.z for point in keycap_points)
    return metrics


def contacts_at_frames(frames: tuple[int, ...]) -> dict[str, object]:
    scene = bpy.context.scene
    original = scene.frame_current
    result = {}
    for frame in frames:
        scene.frame_set(frame)
        result[str(frame)] = contact_metrics()
    scene.frame_set(original)
    return result


def relationship_metrics() -> dict[str, object]:
    get = bpy.data.objects.__getitem__
    return {
        "palm_index": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Index")),
        "palm_index_joint": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Index_Joint01")),
        "index_index_joint": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Index_Joint01")),
        "palm_thumb": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Thumb")),
        "palm_middle": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Middle")),
        "palm_ring": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Ring")),
        "palm_little": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Little")),
        "index_middle": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Middle")),
        "middle_ring": pair_metrics(get("TEAMON_Ada_Middle"), get("TEAMON_Ada_Ring")),
        "ring_little": pair_metrics(get("TEAMON_Ada_Ring"), get("TEAMON_Ada_Little")),
        "thumb_keycap": pair_metrics(get("TEAMON_Ada_Thumb"), get("TEAMON_Keycap")),
    }


def nearest_index_contact_vertex() -> Vector:
    index = bpy.data.objects["TEAMON_Ada_Index"]
    keycap = bpy.data.objects["TEAMON_Keycap"]
    key_points, key_polygons = mesh_world_data(keycap)
    key_bvh = BVHTree.FromPolygons(key_points, key_polygons, all_triangles=False)
    candidates = []
    for vertex in index.data.vertices:
        world = index.matrix_world @ vertex.co
        nearest = key_bvh.find_nearest(world)
        if nearest is not None:
            candidates.append((float(nearest[3]), world))
    return min(candidates, key=lambda item: item[0])[1].copy()


def screen_point(scene: bpy.types.Scene, camera: bpy.types.Object, point: Vector) -> Vector:
    projected = world_to_camera_view(scene, camera, point)
    return Vector((float(projected.x), 1.0 - float(projected.y)))


def axis_rotation(scene: bpy.types.Scene, camera: bpy.types.Object, pivot: Vector, axis_degrees: float) -> tuple[Matrix, float]:
    camera_forward = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    camera_right = camera.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    base = screen_point(scene, camera, pivot)
    probe = pivot + camera_right
    rotation = Matrix.Rotation(math.radians(axis_degrees), 4, camera_forward)
    transformed = pivot + rotation.to_3x3() @ (probe - pivot)
    delta = screen_point(scene, camera, transformed) - base
    observed = math.degrees(math.atan2(delta.y, delta.x))
    world_transform = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)
    return world_transform, float(observed)


def transform_meshes(names: tuple[str, ...], world_transform: Matrix) -> None:
    for name in names:
        obj = bpy.data.objects[name]
        local_transform = obj.matrix_world.inverted_safe() @ world_transform @ obj.matrix_world
        obj.data.transform(local_transform)
        obj.data.update()


def render(path: Path, frame: int = 1) -> None:
    scene = bpy.context.scene
    scene.frame_set(frame)
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def render_orbit(path: Path, angle_degrees: float) -> None:
    scene = bpy.context.scene
    original_camera = scene.camera
    if original_camera is None:
        raise RuntimeError("TEAMON scene has no camera")
    points = [bpy.data.objects[name].matrix_world @ vertex.co for name in HAND_OBJECTS for vertex in bpy.data.objects[name].data.vertices]
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    target = (minimum + maximum) * 0.5
    camera_data = original_camera.data.copy()
    camera = bpy.data.objects.new(f"TEAMON_V45_QA_Camera_{int(angle_degrees)}", camera_data)
    scene.collection.objects.link(camera)
    offset = original_camera.matrix_world.translation - target
    camera.location = target + Matrix.Rotation(math.radians(angle_degrees), 4, "Z") @ offset
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    try:
        render(path, 1)
    finally:
        scene.camera = original_camera
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.cameras.remove(camera_data)


for path in (OUTPUT_BLEND, HERO_RENDER, FRONT_RENDER, SIDE_RENDER, REPORT_PATH, QA_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt01 source, got: {bpy.data.filepath}")
if sha256(SOURCE_BLEND) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Unexpected attempt01 source hash")

scene = bpy.context.scene
scene.frame_set(1)
camera = scene.camera
if camera is None or camera.name != "TEAMON_Camera":
    raise RuntimeError("Locked TEAMON_Camera is required")
missing = [name for name in HAND_OBJECTS + ("TEAMON_Keycap", "TEAMON_HandPressGroup") if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing required objects: {missing}")

all_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
source_before = sha256(SOURCE_BLEND)
coordinates_before = {obj.name: mesh_coordinate_hash(obj) for obj in all_meshes}
topology_before = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_before = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_before = action_signature()
contact_before = contacts_at_frames((1, 24))
relationships_before = relationship_metrics()

scene.frame_set(1)
contact_pivot = nearest_index_contact_vertex()
contact_screen_before = list(screen_point(scene, camera, contact_pivot))
world_transform, observed_angle = axis_rotation(scene, camera, contact_pivot, WORLD_AXIS_ROTATION_DEGREES)
transform_meshes(POSE_GROUP, world_transform)
bridge_transform, bridge_observed_angle = axis_rotation(
    scene, camera, contact_pivot, JOINT_BRIDGE_WORLD_AXIS_ROTATION_DEGREES
)
transform_meshes(("TEAMON_Ada_Index_Joint01",), bridge_transform)
bpy.context.view_layer.update()

contact_after = contacts_at_frames((1, 24))
relationships_after = relationship_metrics()
coordinates_after = {obj.name: mesh_coordinate_hash(obj) for obj in all_meshes}
topology_after = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_after = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_after = action_signature()
changed_coordinates = sorted(name for name in coordinates_before if coordinates_before[name] != coordinates_after[name])
unexpected_coordinate_changes = sorted(set(changed_coordinates) - set(EXPECTED_CHANGED_GROUP))
missing_expected_changes = sorted(set(EXPECTED_CHANGED_GROUP) - set(changed_coordinates))
topology_changes = sorted(name for name in topology_before if topology_before[name] != topology_after[name])
matrix_changes = sorted(name for name in matrices_before if matrices_before[name] != matrices_after[name])

render(HERO_RENDER, 1)
render_orbit(FRONT_RENDER, -25.0)
render_orbit(SIDE_RENDER, 55.0)

hand_objects = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith("TEAMON_Ada_") and not obj.hide_render]
qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in hand_objects],
    contact_tolerance=0.006,
    floating_tolerance=0.04,
)
qa["index_keycap"] = {"before": contact_before, "after": contact_after}
qa["relationships"] = {"before": relationships_before, "after": relationships_after}
qa["scope"] = {
    "expected_changed_meshes": list(EXPECTED_CHANGED_GROUP),
    "actual_changed_meshes": changed_coordinates,
    "unexpected_coordinate_changes": unexpected_coordinate_changes,
    "missing_expected_changes": missing_expected_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
source_after = sha256(SOURCE_BLEND)
report = {
    "stage": "GEOMETRY",
    "attempt": "v45-attempt02-palm-pose",
    "source": str(SOURCE_BLEND),
    "output": str(OUTPUT_BLEND),
    "renders": {"hero": str(HERO_RENDER), "front": str(FRONT_RENDER), "side": str(SIDE_RENDER)},
    "source_sha256_before": source_before,
    "source_sha256_after": source_after,
    "output_sha256": sha256(OUTPUT_BLEND),
    "world_axis_rotation_degrees": WORLD_AXIS_ROTATION_DEGREES,
    "screen_rotation_observed_degrees": observed_angle,
    "joint_bridge_world_axis_rotation_degrees": JOINT_BRIDGE_WORLD_AXIS_ROTATION_DEGREES,
    "joint_bridge_screen_rotation_observed_degrees": bridge_observed_angle,
    "contact_pivot_world": list(contact_pivot),
    "contact_screen_before": contact_screen_before,
    "changed_coordinate_meshes": changed_coordinates,
    "unexpected_coordinate_changes": unexpected_coordinate_changes,
    "missing_expected_changes": missing_expected_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
    "contact_before": contact_before,
    "contact_after": contact_after,
    "relationships_before": relationships_before,
    "relationships_after": relationships_after,
    "qa_report": str(QA_PATH),
    "gates": {
        "source_immutable": source_before == source_after,
        "only_pose_group_coordinates_changed": not unexpected_coordinate_changes and not missing_expected_changes,
        "topology_unchanged": not topology_changes,
        "matrices_unchanged": not matrix_changes,
        "actions_unchanged": actions_before == actions_after,
        "index_contact_exactly_unchanged": contact_before == contact_after,
        "palm_index_still_connected": relationships_after["palm_index"]["overlap_pairs"] >= 50,
        "index_joint_bridges_both_sides": (
            relationships_after["palm_index_joint"]["overlap_pairs"] >= 20
            and relationships_after["index_index_joint"]["overlap_pairs"] >= 20
        ),
        "mrl_still_connected": all(relationships_after[key]["overlap_pairs"] >= 50 for key in ("palm_middle", "palm_ring", "palm_little")),
        "thumb_keycap_clear": relationships_after["thumb_keycap"]["overlap_pairs"] == 0,
    },
    "status": "requires_visual_review",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
