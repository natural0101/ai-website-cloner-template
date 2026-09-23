from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_palm_pose_attempt02.blend"
OUTPUT_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_thumb_pose_attempt03.blend"
HERO_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt03-thumb-pose-hero.png"
FRONT_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt03-thumb-pose-front.png"
SIDE_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt03-thumb-pose-side.png"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt03_report.json"
QA_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt03_structural_qa.json"
QA_MODULES = WORKBENCH / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


EXPECTED_SOURCE_SHA256 = "2A41A7ABF927631B456FCF260FBF1EE8EBDB870080F4ADC49B1C352580F01C68"
THUMB_NAME = "TEAMON_Ada_Thumb"
HAND_SHELLS = (
    "TEAMON_Ada_ForearmShell",
    "TEAMON_Ada_Palm",
    "TEAMON_Ada_Thumb",
    "TEAMON_Ada_Index",
    "TEAMON_Ada_Middle",
    "TEAMON_Ada_Ring",
    "TEAMON_Ada_Little",
)
PIVOT = Vector((0.0967366993, -0.5283463001, 0.4927434921))
LONG_AXIS = Vector((-0.6385319829, -0.5465500951, -0.5418117642)).normalized()
CAMERA_AXIS = Vector((-0.6730940342, 0.4152613878, -0.6119660139)).normalized()
AXIS_LENGTH = 1.4557279633
T0 = 0.10
T1 = 0.70
END_SCALE = 0.60
THETA = math.radians(-15.0)


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


def vertical_gap(first: bpy.types.Object, second: bpy.types.Object) -> float:
    first_points, _ = mesh_world_data(first)
    second_points, _ = mesh_world_data(second)
    return min(point.z for point in first_points) - max(point.z for point in second_points)


def frame_metrics(frames: tuple[int, ...]) -> dict[str, object]:
    scene = bpy.context.scene
    original = scene.frame_current
    result = {}
    for frame in frames:
        scene.frame_set(frame)
        index = bpy.data.objects["TEAMON_Ada_Index"]
        keycap = bpy.data.objects["TEAMON_Keycap"]
        palm = bpy.data.objects["TEAMON_Ada_Palm"]
        thumb = bpy.data.objects[THUMB_NAME]
        result[str(frame)] = {
            "index_keycap": pair_metrics(index, keycap),
            "index_keycap_vertical_gap": vertical_gap(index, keycap),
            "palm_thumb": pair_metrics(palm, thumb),
            "thumb_keycap": pair_metrics(thumb, keycap),
            "thumb_keycap_vertical_gap": vertical_gap(thumb, keycap),
        }
    scene.frame_set(original)
    return result


def face_normal(coords: list[Vector], polygon: bpy.types.MeshPolygon) -> Vector:
    if len(polygon.vertices) < 3:
        return Vector((0.0, 0.0, 0.0))
    a, b, c = (coords[index] for index in polygon.vertices[:3])
    cross = (b - a).cross(c - a)
    return cross.normalized() if cross.length_squared else Vector((0.0, 0.0, 0.0))


def nonadjacent_self_overlaps(obj: bpy.types.Object) -> int:
    points = [vertex.co.copy() for vertex in obj.data.vertices]
    polygons = [tuple(polygon.vertices) for polygon in obj.data.polygons]
    bvh = BVHTree.FromPolygons(points, polygons, all_triangles=False)
    unique = set()
    for first, second in bvh.overlap(bvh):
        if first == second:
            continue
        pair = tuple(sorted((first, second)))
        if set(polygons[pair[0]]) & set(polygons[pair[1]]):
            continue
        unique.add(pair)
    return len(unique)


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
    raise RuntimeError(f"Expected attempt02 source, got {bpy.data.filepath}")
if sha256(SOURCE_BLEND) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Unexpected attempt02 source hash")

scene = bpy.context.scene
scene.frame_set(1)
thumb = bpy.data.objects[THUMB_NAME]
all_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
source_before = sha256(SOURCE_BLEND)
coordinates_before = {obj.name: coordinate_hash(obj) for obj in all_meshes}
topology_before = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_before = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_before = action_signature()
frames_before = frame_metrics((1, 24))
thumb_before = [vertex.co.copy() for vertex in thumb.data.vertices]
edge_lengths_before = [(thumb_before[edge.vertices[0]] - thumb_before[edge.vertices[1]]).length for edge in thumb.data.edges]
normals_before = [face_normal(thumb_before, polygon) for polygon in thumb.data.polygons]
self_overlaps_before = nonadjacent_self_overlaps(thumb)

k = (END_SCALE - T0) / (1.0 - T0)
hinge = PIVOT + LONG_AXIS * (T0 * AXIS_LENGTH)
for vertex in thumb.data.vertices:
    value = vertex.co.copy()
    delta = value - PIVOT
    axial = delta.dot(LONG_AXIS)
    t = axial / AXIS_LENGTH
    radial = delta - LONG_AXIS * axial
    if t <= T0:
        new_value = value
    else:
        new_axial = AXIS_LENGTH * (T0 + k * (t - T0))
        q = max(0.0, min(1.0, (t - T0) / (T1 - T0)))
        weight = q * q * (3.0 - 2.0 * q)
        rotation = Matrix.Rotation(THETA * weight, 3, CAMERA_AXIS)
        new_value = hinge + rotation @ (LONG_AXIS * (new_axial - T0 * AXIS_LENGTH) + radial)
    vertex.co = new_value
thumb.data.update()
bpy.context.view_layer.update()

thumb_after = [vertex.co.copy() for vertex in thumb.data.vertices]
edge_lengths_after = [(thumb_after[edge.vertices[0]] - thumb_after[edge.vertices[1]]).length for edge in thumb.data.edges]
edge_ratios = [after / before for before, after in zip(edge_lengths_before, edge_lengths_after) if before > 1e-12]
normals_after = [face_normal(thumb_after, polygon) for polygon in thumb.data.polygons]
flipped_faces = sum(
    1
    for before, after in zip(normals_before, normals_after)
    if before.length_squared and after.length_squared and before.dot(after) <= 0.0
)
self_overlaps_after = nonadjacent_self_overlaps(thumb)
frames_after = frame_metrics((1, 24))

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
qa["frames_before"] = frames_before
qa["frames_after"] = frames_after
qa["thumb_deformation"] = {
    "edge_ratio_min": min(edge_ratios),
    "edge_ratio_median": sorted(edge_ratios)[len(edge_ratios) // 2],
    "edge_ratio_max": max(edge_ratios),
    "flipped_faces": flipped_faces,
    "self_overlaps_before": self_overlaps_before,
    "self_overlaps_after": self_overlaps_after,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
source_after = sha256(SOURCE_BLEND)
report = {
    "stage": "GEOMETRY",
    "attempt": "v45-attempt03-thumb-pose",
    "source": str(SOURCE_BLEND),
    "output": str(OUTPUT_BLEND),
    "renders": {"hero": str(HERO_RENDER), "front": str(FRONT_RENDER), "side": str(SIDE_RENDER)},
    "source_sha256_before": source_before,
    "source_sha256_after": source_after,
    "output_sha256": sha256(OUTPUT_BLEND),
    "parameters": {
        "pivot": list(PIVOT),
        "long_axis": list(LONG_AXIS),
        "camera_axis": list(CAMERA_AXIS),
        "axis_length": AXIS_LENGTH,
        "t0": T0,
        "t1": T1,
        "end_scale": END_SCALE,
        "rotation_degrees": math.degrees(THETA),
    },
    "coordinate_changes": coordinate_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
    "frames_before": frames_before,
    "frames_after": frames_after,
    "thumb_deformation": qa["thumb_deformation"],
    "qa_report": str(QA_PATH),
    "gates": {
        "source_immutable": source_before == source_after,
        "only_thumb_coordinates_changed": coordinate_changes == [THUMB_NAME],
        "topology_unchanged": not topology_changes,
        "matrices_unchanged": not matrix_changes,
        "actions_unchanged": actions_before == actions_after,
        "index_contact_unchanged": frames_before["1"]["index_keycap"] == frames_after["1"]["index_keycap"] and frames_before["24"]["index_keycap"] == frames_after["24"]["index_keycap"],
        "palm_thumb_connected": all(frames_after[frame]["palm_thumb"]["overlap_pairs"] >= 50 for frame in ("1", "24")),
        "thumb_keycap_clear": all(frames_after[frame]["thumb_keycap"]["overlap_pairs"] == 0 for frame in ("1", "24")),
        "no_face_flips": flipped_faces == 0,
        "no_new_self_overlaps": self_overlaps_after <= self_overlaps_before,
    },
    "status": "requires_visual_review",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
