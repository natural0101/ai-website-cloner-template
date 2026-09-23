from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_hand_pose_attempt04.blend"
PREVIEW_DIR = WORKBENCH / "artifacts" / "previews" / "teamon-v45-mrl-depth-sweep"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_mrl_depth_probe.json"
CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
DEPTHS = (0.08, 0.14, 0.20, 0.26)
TARGET_NAMES = tuple(
    f"TEAMON_Ada_{finger}{suffix}"
    for finger in ("Middle", "Ring", "Little")
    for suffix in ("", "_Joint01", "_Joint02", "_Joint03")
)


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


def relationships() -> dict[str, object]:
    get = bpy.data.objects.__getitem__
    return {
        "palm_middle": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Middle")),
        "palm_ring": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Ring")),
        "palm_little": pair_metrics(get("TEAMON_Ada_Palm"), get("TEAMON_Ada_Little")),
        "index_middle": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Middle")),
        "index_ring": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Ring")),
        "index_little": pair_metrics(get("TEAMON_Ada_Index"), get("TEAMON_Ada_Little")),
        "middle_ring": pair_metrics(get("TEAMON_Ada_Middle"), get("TEAMON_Ada_Ring")),
        "ring_little": pair_metrics(get("TEAMON_Ada_Ring"), get("TEAMON_Ada_Little")),
        "middle_little": pair_metrics(get("TEAMON_Ada_Middle"), get("TEAMON_Ada_Little")),
    }


def transform_meshes(world_transform: Matrix) -> None:
    for name in TARGET_NAMES:
        obj = bpy.data.objects[name]
        local_transform = obj.matrix_world.inverted_safe() @ world_transform @ obj.matrix_world
        obj.data.transform(local_transform)
        obj.data.update()


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
    raise RuntimeError(f"Expected attempt04 source, got {bpy.data.filepath}")
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
snapshots = {
    name: [vertex.co.copy() for vertex in bpy.data.objects[name].data.vertices]
    for name in TARGET_NAMES
}


def restore() -> None:
    for name, coordinates in snapshots.items():
        obj = bpy.data.objects[name]
        for vertex, coordinate in zip(obj.data.vertices, coordinates):
            vertex.co = coordinate
        obj.data.update()
    bpy.context.view_layer.update()


results = []
for depth in DEPTHS:
    restore()
    translation = -CAMERA_FORWARD * depth
    transform_meshes(Matrix.Translation(translation))
    bpy.context.view_layer.update()
    path = PREVIEW_DIR / f"teamon-v45-mrl-depth-{int(round(depth * 100)):02d}.png"
    render(path)
    results.append(
        {
            "depth_toward_camera": depth,
            "translation_world": list(translation),
            "render": str(path),
            "relationships": relationships(),
        }
    )

restore()
report = {
    "stage": "GEOMETRY",
    "mode": "read_only_in_memory_mrl_depth_probe",
    "source": str(SOURCE_BLEND),
    "camera_forward": list(CAMERA_FORWARD),
    "results": results,
    "source_saved": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
