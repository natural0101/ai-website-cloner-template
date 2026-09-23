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
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_thumb_pose_attempt03.blend"
OUTPUT_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_hand_pose_attempt04.blend"
HERO_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt04-hand-pose-hero.png"
FRONT_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt04-hand-pose-front.png"
SIDE_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt04-hand-pose-side.png"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt04_report.json"
QA_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt04_structural_qa.json"
QA_MODULES = WORKBENCH / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


EXPECTED_SOURCE_SHA256 = "53ED11575254D4D3A90F5AD3925F5B61BF6AA823576737E45BFBF06FE362B5B7"
CAMERA_RIGHT = Vector((0.6248648167, 0.7807329893, 0.0)).normalized()
CAMERA_UP = Vector((-0.4777820706, 0.3823961020, 0.7908840775)).normalized()
CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
COMMON_TRANSLATION = Vector((0.2012306899, 0.0310708359, -0.1779489070))
FINGER_SPECS = {
    "Middle": {
        "pivot": Vector((2.1240937710, 1.6367094517, 2.5313618183)),
        "roll": 15.0,
        "yaw": 20.0,
        "pitch": 10.0,
    },
    "Ring": {
        "pivot": Vector((2.4053313732, 2.4222147465, 2.6238908768)),
        "roll": 85.0,
        "yaw": -20.0,
        "pitch": -40.0,
    },
    "Little": {
        "pivot": Vector((2.7574174404, 3.0543124676, 2.7007515430)),
        "roll": 100.0,
        "yaw": -20.0,
        "pitch": -10.0,
    },
}
TARGET_NAMES = tuple(
    f"TEAMON_Ada_{finger}{suffix}"
    for finger in FINGER_SPECS
    for suffix in ("", "_Joint01", "_Joint02", "_Joint03")
)
HAND_SHELLS = (
    "TEAMON_Ada_ForearmShell",
    "TEAMON_Ada_Palm",
    "TEAMON_Ada_Thumb",
    "TEAMON_Ada_Index",
    "TEAMON_Ada_Middle",
    "TEAMON_Ada_Ring",
    "TEAMON_Ada_Little",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def coordinate_hash(obj: bpy.types.Object) -> str:
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


def relationship_metrics() -> dict[str, object]:
    get = bpy.data.objects.__getitem__
    result = {
        "palm_middle": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Middle")),
        "palm_ring": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Ring")),
        "palm_little": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Little")),
        "index_middle": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Middle")),
        "index_ring": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Ring")),
        "index_little": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Little")),
        "middle_ring": pair_metrics(get("TEAMON_Ada_Middle"), get("TEAMON_Ada_Ring")),
        "ring_little": pair_metrics(get("TEAMON_Ada_Ring"), get("TEAMON_Ada_Little")),
        "middle_little": pair_metrics(get("TEAMON_Ada_Middle"), get("TEAMON_Ada_Little")),
        "thumb_keycap": pair_metrics(get("TEAMON_Ada_Thumb"), get("TEAMON_Keycap")),
        "palm_thumb": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Thumb")),
    }
    for finger in FINGER_SPECS:
        result[f"{finger.lower()}_keycap"] = pair_metrics(get(f"TEAMON_Ada_{finger}"), get("TEAMON_Keycap"))
    return result


def contact_at_frames() -> dict[str, object]:
    scene = bpy.context.scene
    original = scene.frame_current
    result = {}
    for frame in (1, 24):
        scene.frame_set(frame)
        result[str(frame)] = pair_metrics(bpy.data.objects["TEAMON_Ada_Index"], bpy.data.objects["TEAMON_Keycap"])
    scene.frame_set(original)
    return result


def screen_group_metrics(names: tuple[str, ...]) -> dict[str, object]:
    scene = bpy.context.scene
    camera = scene.camera
    if camera is None:
        raise RuntimeError("TEAMON camera missing")
    points = []
    for name in names:
        obj = bpy.data.objects[name]
        for vertex in obj.data.vertices:
            ndc = world_to_camera_view(scene, camera, obj.matrix_world @ vertex.co)
            points.append(Vector((float(ndc.x), 1.0 - float(ndc.y))))
    centroid = sum(points, Vector((0.0, 0.0))) / len(points)
    return {
        "centroid": list(centroid),
        "bbox": [
            min(point.x for point in points),
            min(point.y for point in points),
            max(point.x for point in points),
            max(point.y for point in points),
        ],
    }


def transform_group(names: tuple[str, ...], pivot: Vector, roll: float, yaw: float, pitch: float) -> None:
    rotation = (
        Matrix.Rotation(math.radians(roll), 4, CAMERA_FORWARD)
        @ Matrix.Rotation(math.radians(yaw), 4, CAMERA_UP)
        @ Matrix.Rotation(math.radians(pitch), 4, CAMERA_RIGHT)
    )
    world_transform = (
        Matrix.Translation(COMMON_TRANSLATION)
        @ Matrix.Translation(pivot)
        @ rotation
        @ Matrix.Translation(-pivot)
    )
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
    points = [bpy.data.objects[name].matrix_world @ vertex.co for name in HAND_SHELLS for vertex in bpy.data.objects[name].data.vertices]
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
    raise RuntimeError(f"Expected attempt03 source, got {bpy.data.filepath}")
if sha256(SOURCE_BLEND) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Unexpected attempt03 source hash")

scene = bpy.context.scene
scene.frame_set(1)
all_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
source_before = sha256(SOURCE_BLEND)
coordinates_before = {obj.name: coordinate_hash(obj) for obj in all_meshes}
topology_before = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_before = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_before = action_signature()
contacts_before = contact_at_frames()
relationships_before = relationship_metrics()
screen_before = screen_group_metrics(TARGET_NAMES)

for finger, spec in FINGER_SPECS.items():
    names = tuple(f"TEAMON_Ada_{finger}{suffix}" for suffix in ("", "_Joint01", "_Joint02", "_Joint03"))
    transform_group(names, spec["pivot"], spec["roll"], spec["yaw"], spec["pitch"])
bpy.context.view_layer.update()

contacts_after = contact_at_frames()
relationships_after = relationship_metrics()
screen_after = screen_group_metrics(TARGET_NAMES)
coordinates_after = {obj.name: coordinate_hash(obj) for obj in all_meshes}
topology_after = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_after = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_after = action_signature()
coordinate_changes = sorted(name for name in coordinates_before if coordinates_before[name] != coordinates_after[name])
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
qa["scope"] = {
    "coordinate_changes": coordinate_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
}
qa["contacts"] = {"before": contacts_before, "after": contacts_after}
qa["relationships"] = {"before": relationships_before, "after": relationships_after}
qa["screen"] = {"before": screen_before, "after": screen_after}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
source_after = sha256(SOURCE_BLEND)
report = {
    "stage": "GEOMETRY",
    "attempt": "v45-attempt04-mrl-pose",
    "source": str(SOURCE_BLEND),
    "output": str(OUTPUT_BLEND),
    "renders": {"hero": str(HERO_RENDER), "front": str(FRONT_RENDER), "side": str(SIDE_RENDER)},
    "source_sha256_before": source_before,
    "source_sha256_after": source_after,
    "output_sha256": sha256(OUTPUT_BLEND),
    "camera_axes": {"right": list(CAMERA_RIGHT), "up": list(CAMERA_UP), "forward": list(CAMERA_FORWARD)},
    "common_translation": list(COMMON_TRANSLATION),
    "finger_specs": {
        finger: {"pivot": list(spec["pivot"]), "roll": spec["roll"], "yaw": spec["yaw"], "pitch": spec["pitch"]}
        for finger, spec in FINGER_SPECS.items()
    },
    "coordinate_changes": coordinate_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
    "contacts_before": contacts_before,
    "contacts_after": contacts_after,
    "relationships_before": relationships_before,
    "relationships_after": relationships_after,
    "screen_before": screen_before,
    "screen_after": screen_after,
    "qa_report": str(QA_PATH),
    "gates": {
        "source_immutable": source_before == source_after,
        "only_mrl_coordinates_changed": set(coordinate_changes) == set(TARGET_NAMES),
        "topology_unchanged": not topology_changes,
        "matrices_unchanged": not matrix_changes,
        "actions_unchanged": actions_before == actions_after,
        "index_contact_unchanged": contacts_before == contacts_after,
        "palm_connections": all(relationships_after[key]["overlap_pairs"] >= 50 for key in ("palm_middle", "palm_ring", "palm_little")),
        "no_interfinger_intersections": all(relationships_after[key]["overlap_pairs"] == 0 for key in ("middle_ring", "ring_little", "middle_little")),
        "no_index_mrl_intersections": all(relationships_after[key]["overlap_pairs"] == 0 for key in ("index_middle", "index_ring", "index_little")),
        "no_mrl_keycap_intersections": all(relationships_after[key]["overlap_pairs"] == 0 for key in ("middle_keycap", "ring_keycap", "little_keycap")),
        "thumb_remains_clear": relationships_after["thumb_keycap"]["overlap_pairs"] == 0,
    },
    "status": "requires_visual_review",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
