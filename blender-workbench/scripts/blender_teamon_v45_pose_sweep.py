from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_pose_d_attached_attempt01.blend"
PREVIEW_DIR = WORKBENCH / "artifacts" / "previews" / "teamon-v45-pose-sweep"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_pose_sweep.json"

CANDIDATES = (
    ("g08_p12", -8.0, -12.0),
    ("g10_p14", -10.0, -14.0),
    ("g11_p17", -11.0, -17.0),
    ("g12_p20", -12.0, -20.0),
)

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
PALM_GROUP = tuple(name for name in HAND_OBJECTS if name != "TEAMON_Ada_Index")
METRIC_GROUPS = {
    "all_hand": HAND_OBJECTS,
    "palm_forearm": ("TEAMON_Ada_Palm", "TEAMON_Ada_ForearmShell"),
    "thumb": ("TEAMON_Ada_Thumb",),
    "index": ("TEAMON_Ada_Index",),
    "mrl": tuple(name for name in HAND_OBJECTS if any(token in name for token in ("Middle", "Ring", "Little"))),
}


def screen_point(scene: bpy.types.Scene, camera: bpy.types.Object, point: Vector) -> Vector:
    projected = world_to_camera_view(scene, camera, point)
    return Vector((float(projected.x), 1.0 - float(projected.y)))


def object_world_center(obj: bpy.types.Object) -> Vector:
    if obj.type != "MESH" or not obj.data.vertices:
        return obj.matrix_world.translation.copy()
    return sum((obj.matrix_world @ vertex.co for vertex in obj.data.vertices), Vector()) / len(obj.data.vertices)


def group_points(names: tuple[str, ...]) -> list[Vector]:
    return [
        bpy.data.objects[name].matrix_world @ vertex.co
        for name in names
        for vertex in bpy.data.objects[name].data.vertices
        if bpy.data.objects[name].type == "MESH"
    ]


def group_metrics(scene: bpy.types.Scene, camera: bpy.types.Object, names: tuple[str, ...]) -> dict[str, object]:
    projected = [screen_point(scene, camera, point) for point in group_points(names)]
    count = len(projected)
    centroid = sum(projected, Vector((0.0, 0.0))) / count
    minimum = Vector((min(point.x for point in projected), min(point.y for point in projected)))
    maximum = Vector((max(point.x for point in projected), max(point.y for point in projected)))
    xx = sum((point.x - centroid.x) ** 2 for point in projected) / count
    yy = sum((point.y - centroid.y) ** 2 for point in projected) / count
    xy = sum((point.x - centroid.x) * (point.y - centroid.y) for point in projected) / count
    pca_angle = 0.5 * math.degrees(math.atan2(2.0 * xy, xx - yy))
    return {
        "centroid": [float(centroid.x), float(centroid.y)],
        "bbox": [float(minimum.x), float(minimum.y), float(maximum.x), float(maximum.y)],
        "pca_angle_top_origin_degrees": float(pca_angle),
        "vertex_samples": count,
    }


def transform_meshes(names: tuple[str, ...], world_transform: Matrix) -> None:
    for name in names:
        obj = bpy.data.objects[name]
        local_transform = obj.matrix_world.inverted_safe() @ world_transform @ obj.matrix_world
        obj.data.transform(local_transform)
        obj.data.update()


def rotation_about_screen_angle(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    pivot: Vector,
    desired_screen_degrees: float,
) -> Matrix:
    camera_forward = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    camera_right = camera.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    base_screen = screen_point(scene, camera, pivot)
    probe = pivot + camera_right
    best = None
    for step in range(-1200, 1201):
        axis_degrees = step * 0.05
        rotation = Matrix.Rotation(math.radians(axis_degrees), 4, camera_forward)
        transformed_probe = pivot + rotation.to_3x3() @ (probe - pivot)
        delta = screen_point(scene, camera, transformed_probe) - base_screen
        observed = math.degrees(math.atan2(delta.y, delta.x))
        error = abs(((observed - desired_screen_degrees + 180.0) % 360.0) - 180.0)
        if best is None or error < best[0]:
            best = (error, rotation, observed)
    if best is None or best[0] > 0.1:
        raise RuntimeError(f"Unable to map screen rotation {desired_screen_degrees}: {best}")
    return Matrix.Translation(pivot) @ best[1] @ Matrix.Translation(-pivot)


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
    raise RuntimeError(f"Expected attempt01 source, got {bpy.data.filepath}")

PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
camera = scene.camera
if camera is None or camera.name != "TEAMON_Camera":
    raise RuntimeError("Locked TEAMON_Camera is required")
missing = [name for name in HAND_OBJECTS if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing hand objects: {missing}")

snapshots = {
    name: [vertex.co.copy() for vertex in bpy.data.objects[name].data.vertices]
    for name in HAND_OBJECTS
}
contact_pivot = Vector((0.530239642, 0.779917419, 1.201036096))

def restore() -> None:
    for name, coordinates in snapshots.items():
        obj = bpy.data.objects[name]
        for vertex, coordinate in zip(obj.data.vertices, coordinates):
            vertex.co = coordinate
        obj.data.update()
    bpy.context.view_layer.update()


baseline = {
    group: group_metrics(scene, camera, names)
    for group, names in METRIC_GROUPS.items()
}
baseline["contact_screen"] = list(screen_point(scene, camera, contact_pivot))
baseline["index_joint_screen"] = list(screen_point(scene, camera, object_world_center(bpy.data.objects["TEAMON_Ada_Index_Joint01"])))

results = []
for candidate_id, global_screen_angle, palm_extra_screen_angle in CANDIDATES:
    restore()
    global_transform = rotation_about_screen_angle(scene, camera, contact_pivot, global_screen_angle)
    transform_meshes(HAND_OBJECTS, global_transform)
    bpy.context.view_layer.update()

    index_base_pivot = object_world_center(bpy.data.objects["TEAMON_Ada_Index_Joint01"])
    palm_transform = rotation_about_screen_angle(scene, camera, index_base_pivot, palm_extra_screen_angle)
    transform_meshes(PALM_GROUP, palm_transform)
    bpy.context.view_layer.update()

    render_path = PREVIEW_DIR / f"teamon-v45-sweep-{candidate_id}.png"
    render(render_path)
    metrics = {
        group: group_metrics(scene, camera, names)
        for group, names in METRIC_GROUPS.items()
    }
    metrics["contact_screen"] = list(screen_point(scene, camera, contact_pivot))
    metrics["index_joint_screen"] = list(screen_point(scene, camera, index_base_pivot))
    results.append(
        {
            "candidate_id": candidate_id,
            "global_screen_angle_degrees": global_screen_angle,
            "palm_extra_screen_angle_degrees": palm_extra_screen_angle,
            "palm_total_screen_angle_degrees": global_screen_angle + palm_extra_screen_angle,
            "render": str(render_path),
            "metrics": metrics,
        }
    )

restore()
report = {
    "stage": "GEOMETRY",
    "mode": "read_only_in_memory_pose_sweep",
    "source": str(SOURCE_BLEND),
    "camera": camera.name,
    "contact_pivot_world": list(contact_pivot),
    "baseline": baseline,
    "candidates": results,
    "source_saved": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
