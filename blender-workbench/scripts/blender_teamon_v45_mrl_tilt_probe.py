from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_thumb_pose_attempt03.blend"
OUT_DIR = WORKBENCH / "artifacts" / "previews" / "teamon-v45-mrl-tilt-sweep"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_mrl_tilt_probe.json"
CAMERA_RIGHT = Vector((0.6248648167, 0.7807329893, 0.0)).normalized()
CAMERA_UP = Vector((-0.4777820706, 0.3823961020, 0.7908840775)).normalized()
CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
PIVOTS = {
    "Middle": Vector((2.1240937710, 1.6367094517, 2.5313618183)),
    "Ring": Vector((2.4053313732, 2.4222147465, 2.6238908768)),
    "Little": Vector((2.7574174404, 3.0543124676, 2.7007515430)),
}
ROLLS = {"Middle": 15.0, "Ring": 85.0, "Little": 100.0}
ORIGINAL_TILTS = {
    "Middle": (20.0, 10.0),
    "Ring": (-20.0, -40.0),
    "Little": (-20.0, -10.0),
}
VARIANTS = {
    "flip_both": {f: (-yaw, -pitch) for f, (yaw, pitch) in ORIGINAL_TILTS.items()},
    "flip_pitch": {f: (yaw, -pitch) for f, (yaw, pitch) in ORIGINAL_TILTS.items()},
    "flip_yaw": {f: (-yaw, pitch) for f, (yaw, pitch) in ORIGINAL_TILTS.items()},
    "half_flip_both": {f: (-0.5 * yaw, -0.5 * pitch) for f, (yaw, pitch) in ORIGINAL_TILTS.items()},
}
SUFFIXES = ("", "_Joint01", "_Joint02", "_Joint03")
TARGET_NAMES = tuple(f"TEAMON_Ada_{finger}{suffix}" for finger in PIVOTS for suffix in SUFFIXES)


def world_data(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons]


def pair(first, second):
    ap, af = world_data(first)
    bp, bf = world_data(second)
    abvh = BVHTree.FromPolygons(ap, af, all_triangles=False)
    bbvh = BVHTree.FromPolygons(bp, bf, all_triangles=False)
    return len(abvh.overlap(bbvh))


def overlaps():
    get = bpy.data.objects.__getitem__
    pairs = {
        "palm_middle": ("TEAMON_Ada_Palm", "TEAMON_Ada_Middle"),
        "palm_ring": ("TEAMON_Ada_Palm", "TEAMON_Ada_Ring"),
        "palm_little": ("TEAMON_Ada_Palm", "TEAMON_Ada_Little"),
        "middle_ring": ("TEAMON_Ada_Middle", "TEAMON_Ada_Ring"),
        "ring_little": ("TEAMON_Ada_Ring", "TEAMON_Ada_Little"),
        "middle_little": ("TEAMON_Ada_Middle", "TEAMON_Ada_Little"),
        "index_middle": ("TEAMON_Ada_Index", "TEAMON_Ada_Middle"),
        "index_ring": ("TEAMON_Ada_Index", "TEAMON_Ada_Ring"),
        "index_little": ("TEAMON_Ada_Index", "TEAMON_Ada_Little"),
    }
    return {name: pair(get(a), get(b)) for name, (a, b) in pairs.items()}


def apply_transform(finger, yaw, pitch):
    pivot = PIVOTS[finger]
    rotation = (
        Matrix.Rotation(math.radians(ROLLS[finger]), 4, CAMERA_FORWARD)
        @ Matrix.Rotation(math.radians(yaw), 4, CAMERA_UP)
        @ Matrix.Rotation(math.radians(pitch), 4, CAMERA_RIGHT)
    )
    transform = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot)
    for suffix in SUFFIXES:
        obj = bpy.data.objects[f"TEAMON_Ada_{finger}{suffix}"]
        obj.data.transform(obj.matrix_world.inverted_safe() @ transform @ obj.matrix_world)
        obj.data.update()


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt03 source, got {bpy.data.filepath}")
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
snapshots = {name: [v.co.copy() for v in bpy.data.objects[name].data.vertices] for name in TARGET_NAMES}
results = {}

for label, tilts in VARIANTS.items():
    for name, coordinates in snapshots.items():
        obj = bpy.data.objects[name]
        for vertex, coordinate in zip(obj.data.vertices, coordinates):
            vertex.co = coordinate
        obj.data.update()
    for finger, (yaw, pitch) in tilts.items():
        apply_transform(finger, yaw, pitch)
    bpy.context.view_layer.update()
    output = OUT_DIR / f"teamon-v45-mrl-tilt-{label}.png"
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    results[label] = {"tilts": tilts, "render": str(output), "overlaps": overlaps()}

REPORT_PATH.write_text(json.dumps({"source": str(SOURCE_BLEND), "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, ensure_ascii=False, indent=2))
