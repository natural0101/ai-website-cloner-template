from __future__ import annotations

import hashlib
import json
import os
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v44_surface_smoothed.blend"
DONOR_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v12_ada_pose_d.blend"
OUTPUT_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_pose_d_attached_attempt01.blend"
HERO_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt01-pose-d-hero.png"
FRONT_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt01-pose-d-front.png"
SIDE_RENDER = WORKBENCH / "artifacts" / "previews" / "teamon-v45-attempt01-pose-d-side.png"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt01_report.json"
QA_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt01_structural_qa.json"
QA_MODULES = WORKBENCH / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


EXPECTED_SOURCE_SHA256 = "CB0BD6915115FCCB1B4B1E6AA75F0A61C50D6CD250D674BEB8486CDB630697D4"
EXPECTED_DONOR_SHA256 = "69FFBADDC8AAA5A885BEC9D3196D09A48DC5D781EB78F153FF464ECE31FD6FDB"
TARGET_NAMES = tuple(
    f"TEAMON_Ada_{finger}{suffix}"
    for finger in ("Middle", "Ring", "Little")
    for suffix in ("", "_Joint01", "_Joint02", "_Joint03")
)
HAND_SHELLS = [
    "TEAMON_Ada_ForearmShell",
    "TEAMON_Ada_Palm",
    "TEAMON_Ada_Thumb",
    "TEAMON_Ada_Index",
    "TEAMON_Ada_Middle",
    "TEAMON_Ada_Ring",
    "TEAMON_Ada_Little",
]


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


def junction_metrics() -> dict[str, object]:
    palm = bpy.data.objects["TEAMON_Ada_Palm"]
    return {
        "palm_middle": pair_metrics(palm, bpy.data.objects["TEAMON_Ada_Middle"]),
        "palm_ring": pair_metrics(palm, bpy.data.objects["TEAMON_Ada_Ring"]),
        "palm_little": pair_metrics(palm, bpy.data.objects["TEAMON_Ada_Little"]),
        "index_middle": pair_metrics(bpy.data.objects["TEAMON_Ada_Index"], bpy.data.objects["TEAMON_Ada_Middle"]),
        "middle_ring": pair_metrics(bpy.data.objects["TEAMON_Ada_Middle"], bpy.data.objects["TEAMON_Ada_Ring"]),
        "ring_little": pair_metrics(bpy.data.objects["TEAMON_Ada_Ring"], bpy.data.objects["TEAMON_Ada_Little"]),
    }


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


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
    target_objects = [bpy.data.objects[name] for name in HAND_SHELLS]
    points = [obj.matrix_world @ Vector(corner) for obj in target_objects for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    target = (minimum + maximum) * 0.5
    camera_data = original_camera.data.copy()
    camera = bpy.data.objects.new(f"TEAMON_V45_QA_Camera_{int(angle_degrees)}", camera_data)
    scene.collection.objects.link(camera)
    offset = original_camera.matrix_world.translation - target
    camera.location = target + Matrix.Rotation(radians(angle_degrees), 4, "Z") @ offset
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
    raise RuntimeError(f"Expected immutable v44 source, got: {bpy.data.filepath}")
if sha256(SOURCE_BLEND) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Unexpected v44 source hash")
if sha256(DONOR_BLEND) != EXPECTED_DONOR_SHA256:
    raise RuntimeError("Unexpected pose-d donor hash")

scene = bpy.context.scene
scene.frame_set(1)
missing = [
    name
    for name in list(TARGET_NAMES) + HAND_SHELLS + ["TEAMON_Keycap", "TEAMON_HandPressGroup"]
    if bpy.data.objects.get(name) is None
]
if missing:
    raise RuntimeError(f"Missing required objects: {missing}")

source_before = {
    "v44_sha256": sha256(SOURCE_BLEND),
    "pose_d_sha256": sha256(DONOR_BLEND),
}
all_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
coordinates_before = {obj.name: mesh_coordinate_hash(obj) for obj in all_meshes}
topology_before = {obj.name: topology_hash(obj) for obj in all_meshes}
matrices_before = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_before = action_signature()
contact_before = contacts_at_frames((1, 24))
junctions_before = junction_metrics()
triangles_before = triangle_count([obj for obj in bpy.data.objects if obj.get("abt_export", False)])

with bpy.data.libraries.load(str(DONOR_BLEND), link=False) as (available, requested):
    donor_missing = sorted(set(TARGET_NAMES) - set(available.objects))
    if donor_missing:
        raise RuntimeError(f"Missing donor objects: {donor_missing}")
    requested.objects = list(TARGET_NAMES)

donors = {requested_name: donor for requested_name, donor in zip(TARGET_NAMES, requested.objects) if donor is not None}
if set(donors) != set(TARGET_NAMES):
    raise RuntimeError("Pose-d donor load was incomplete")

copy_report = {}
for name in TARGET_NAMES:
    destination = bpy.data.objects[name]
    donor = donors[name]
    if destination.type != "MESH" or donor.type != "MESH":
        raise RuntimeError(f"Expected mesh pair for {name}")
    operation = "vertex_coordinate_copy"
    delta = None
    if "_Joint" in name:
        if len(destination.data.vertices) != len(donor.data.vertices):
            raise RuntimeError(f"Joint vertex-count mismatch for {name}")
        destination_center = sum((vertex.co for vertex in destination.data.vertices), Vector()) / len(destination.data.vertices)
        donor_center = sum((vertex.co for vertex in donor.data.vertices), Vector()) / len(donor.data.vertices)
        delta = donor_center - destination_center
        destination.data.transform(Matrix.Translation(delta))
        operation = "rigid_center_translation_preserving_target_topology"
    else:
        if topology_hash(destination) != topology_hash(donor):
            raise RuntimeError(f"Finger-shell topology mismatch for {name}")
        for destination_vertex, donor_vertex in zip(destination.data.vertices, donor.data.vertices):
            destination_vertex.co = donor_vertex.co
    destination.data.update()
    copy_report[name] = {
        "vertices": len(destination.data.vertices),
        "operation": operation,
        "translation": list(delta) if delta is not None else None,
        "coordinate_hash_before": coordinates_before[name],
        "coordinate_hash_after": mesh_coordinate_hash(destination),
    }

for donor in donors.values():
    mesh = donor.data
    bpy.data.objects.remove(donor, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

bpy.context.view_layer.update()
scene.frame_set(1)
contact_after = contacts_at_frames((1, 24))
junctions_after = junction_metrics()
triangles_after = triangle_count([obj for obj in bpy.data.objects if obj.get("abt_export", False)])
topology_after = {obj.name: topology_hash(obj) for obj in all_meshes}
coordinates_after = {obj.name: mesh_coordinate_hash(obj) for obj in all_meshes}
matrices_after = {obj.name: matrix_values(obj.matrix_world) for obj in bpy.data.objects}
actions_after = action_signature()

non_target_coordinate_changes = sorted(
    name for name in coordinates_before
    if name not in TARGET_NAMES and coordinates_before[name] != coordinates_after[name]
)
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
qa["expected_contacts"] = {
    "before": junctions_before,
    "after": junctions_after,
    "pass": all(junctions_after[key]["overlap_pairs"] >= 50 for key in ("palm_middle", "palm_ring", "palm_little")),
}
qa["index_keycap"] = {
    "before": contact_before,
    "after": contact_after,
    "unchanged_within_1um": all(
        abs(contact_before[frame]["surface_distance"] - contact_after[frame]["surface_distance"]) <= 1e-6
        for frame in ("1", "24")
    ),
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

source_after = {
    "v44_sha256": sha256(SOURCE_BLEND),
    "pose_d_sha256": sha256(DONOR_BLEND),
}
report = {
    "stage": "GEOMETRY",
    "attempt": "v45-attempt01-restore-attached-pose-d",
    "source": str(SOURCE_BLEND),
    "donor": str(DONOR_BLEND),
    "output": str(OUTPUT_BLEND),
    "renders": {"hero": str(HERO_RENDER), "front": str(FRONT_RENDER), "side": str(SIDE_RENDER)},
    "copy_report": copy_report,
    "source_before": source_before,
    "source_after": source_after,
    "source_immutable": source_before == source_after,
    "non_target_coordinate_changes": non_target_coordinate_changes,
    "topology_changes": topology_changes,
    "matrix_changes": matrix_changes,
    "actions_unchanged": actions_before == actions_after,
    "triangles_before": triangles_before,
    "triangles_after": triangles_after,
    "contact_before": contact_before,
    "contact_after": contact_after,
    "junctions_before": junctions_before,
    "junctions_after": junctions_after,
    "qa_report": str(QA_PATH),
    "gates": {
        "source_immutable": source_before == source_after,
        "only_target_coordinates_changed": not non_target_coordinate_changes,
        "topology_unchanged": not topology_changes,
        "matrices_unchanged": not matrix_changes,
        "actions_unchanged": actions_before == actions_after,
        "triangles_unchanged": triangles_before == triangles_after,
        "contact_unchanged_within_1um": qa["index_keycap"]["unchanged_within_1um"],
        "three_finger_palm_overlap": qa["expected_contacts"]["pass"],
    },
    "status": "requires_visual_review",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
