from __future__ import annotations

from collections import deque
import json
import math
import os
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_palm_pose_attempt02.blend"
PREVIEW_PATH = WORKBENCH / "artifacts" / "previews" / "teamon-v45-thumb-probe-similarity.png"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_thumb_probe.json"
TARGET_TIP_SCREEN = Vector((0.74325, 0.68795))


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


def screen_point(scene: bpy.types.Scene, camera: bpy.types.Object, point: Vector) -> Vector:
    projected = world_to_camera_view(scene, camera, point)
    return Vector((float(projected.x), 1.0 - float(projected.y)))


def overlap_vertex_indices(palm: bpy.types.Object, thumb: bpy.types.Object) -> tuple[set[int], int]:
    palm_points, palm_polygons = mesh_world_data(palm)
    thumb_points, thumb_polygons = mesh_world_data(thumb)
    palm_bvh = BVHTree.FromPolygons(palm_points, palm_polygons, all_triangles=False)
    thumb_bvh = BVHTree.FromPolygons(thumb_points, thumb_polygons, all_triangles=False)
    pairs = palm_bvh.overlap(thumb_bvh)
    indices = set()
    for _, thumb_polygon_index in pairs:
        indices.update(thumb.data.polygons[thumb_polygon_index].vertices)
    return indices, len(pairs)


def graph_rings(obj: bpy.types.Object, seeds: set[int]) -> list[int]:
    adjacency = [set() for _ in obj.data.vertices]
    for edge in obj.data.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    distances = [-1] * len(adjacency)
    queue = deque()
    for seed in seeds:
        distances[seed] = 0
        queue.append(seed)
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if distances[neighbor] == -1:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances


def feather_weight(ring: int) -> float:
    if ring < 0:
        return 1.0
    if ring <= 2:
        return 0.0
    return {3: 0.2, 4: 0.45, 5: 0.7}.get(ring, 1.0)


def render(path: Path) -> None:
    scene = bpy.context.scene
    scene.frame_set(1)
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt02 source, got {bpy.data.filepath}")

PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
camera = scene.camera
if camera is None or camera.name != "TEAMON_Camera":
    raise RuntimeError("Locked TEAMON_Camera is required")
palm = bpy.data.objects["TEAMON_Ada_Palm"]
thumb = bpy.data.objects["TEAMON_Ada_Thumb"]
keycap = bpy.data.objects["TEAMON_Keycap"]

base_indices, overlap_pairs_before = overlap_vertex_indices(palm, thumb)
if overlap_pairs_before < 50 or not base_indices:
    raise RuntimeError("Unable to identify a stable Palm-Thumb attachment")
rings = graph_rings(thumb, base_indices)
weights = [1.0 for _ in rings]
world_before = [thumb.matrix_world @ vertex.co for vertex in thumb.data.vertices]
pivot = sum((world_before[index] for index in base_indices), Vector()) / len(base_indices)

projected_before = [screen_point(scene, camera, point) for point in world_before]
minimum_x = min(point.x for point in projected_before)
maximum_x = max(point.x for point in projected_before)
tip_band_indices = [
    index
    for index, point in enumerate(projected_before)
    if point.x <= minimum_x + 0.025 * (maximum_x - minimum_x)
]
tip_anchor_world = sum((world_before[index] for index in tip_band_indices), Vector()) / len(tip_band_indices)
tip_screen_before = screen_point(scene, camera, tip_anchor_world)
camera_forward = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
thumb_long_axis = (tip_anchor_world - pivot).normalized()

best = None
for angle_step in range(-120, 41):
    axis_degrees = angle_step * 0.25
    rotation = Matrix.Rotation(math.radians(axis_degrees), 4, camera_forward).to_3x3()
    for scale_step in range(100, 181):
        scale = scale_step * 0.005
        transformed_tip = pivot + scale * (rotation @ (tip_anchor_world - pivot))
        screen = screen_point(scene, camera, transformed_tip)
        error = (screen - TARGET_TIP_SCREEN).length
        if best is None or error < best[0]:
            best = (error, axis_degrees, scale, transformed_tip, screen)
if best is None:
    raise RuntimeError("Thumb transform solve failed")

_, axis_degrees, scale, _, solved_screen = best
rotation = Matrix.Rotation(math.radians(axis_degrees), 4, camera_forward).to_3x3()
inverse_world = thumb.matrix_world.inverted_safe()
for index, vertex in enumerate(thumb.data.vertices):
    old_world = world_before[index]
    offset = old_world - pivot
    longitudinal = offset.dot(thumb_long_axis) * thumb_long_axis
    transverse = offset - longitudinal
    transformed_world = pivot + rotation @ (scale * longitudinal + transverse)
    new_world = old_world.lerp(transformed_world, weights[index])
    vertex.co = inverse_world @ new_world
thumb.data.update()
bpy.context.view_layer.update()

world_after = [thumb.matrix_world @ vertex.co for vertex in thumb.data.vertices]
tip_anchor_after = sum((world_after[index] for index in tip_band_indices), Vector()) / len(tip_band_indices)
tip_screen_after = screen_point(scene, camera, tip_anchor_after)
palm_thumb_after = pair_metrics(palm, thumb)
thumb_keycap_after = pair_metrics(thumb, keycap)
max_base_displacement = max((world_after[index] - world_before[index]).length for index in base_indices)
max_displacement = max((after - before).length for before, after in zip(world_before, world_after))

render(PREVIEW_PATH)
report = {
    "stage": "GEOMETRY",
    "mode": "read_only_in_memory_thumb_probe",
    "source": str(SOURCE_BLEND),
    "render": str(PREVIEW_PATH),
    "target_tip_screen": list(TARGET_TIP_SCREEN),
    "tip_screen_before": list(tip_screen_before),
    "tip_screen_solved_rigid": list(solved_screen),
    "tip_screen_after_weighted": list(tip_screen_after),
    "attachment_pivot_world": list(pivot),
    "axis_degrees": axis_degrees,
    "longitudinal_scale": scale,
    "tip_band_vertex_count": len(tip_band_indices),
    "protected_base_vertex_count": sum(1 for weight in weights if weight == 0.0),
    "feather_vertex_count": sum(1 for weight in weights if 0.0 < weight < 1.0),
    "max_base_displacement": max_base_displacement,
    "max_displacement": max_displacement,
    "palm_thumb_overlap_pairs_before": overlap_pairs_before,
    "palm_thumb_after": palm_thumb_after,
    "thumb_keycap_after": thumb_keycap_after,
    "source_saved": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
