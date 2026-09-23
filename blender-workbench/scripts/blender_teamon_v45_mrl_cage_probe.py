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
OUT_DIR = WORKBENCH / "artifacts" / "previews" / "teamon-v45-mrl-cage-sweep"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_mrl_cage_probe.json"
CAMERA_UP = Vector((-0.4777820706, 0.3823961020, 0.7908840775)).normalized()
CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
PIVOTS = {
    "Middle": Vector((2.1240937710, 1.6367094517, 2.5313618183)),
    "Ring": Vector((2.4053313732, 2.4222147465, 2.6238908768)),
    "Little": Vector((2.7574174404, 3.0543124676, 2.7007515430)),
}
VARIANTS = {
    "a_proposed": {
        "Middle": (50.0, 8.0, 0.00), "Ring": (60.0, 12.0, 0.04), "Little": (65.0, 16.0, 0.08),
    },
    "b_conservative": {
        "Middle": (40.0, 8.0, 0.00), "Ring": (50.0, 10.0, 0.03), "Little": (55.0, 12.0, 0.06),
    },
    "c_balanced": {
        "Middle": (45.0, 6.0, 0.00), "Ring": (55.0, 10.0, 0.04), "Little": (60.0, 14.0, 0.07),
    },
}
SUFFIXES = ("", "_Joint01", "_Joint02", "_Joint03")
TARGET_NAMES = tuple(f"TEAMON_Ada_{finger}{suffix}" for finger in PIVOTS for suffix in SUFFIXES)
JOINT_WEIGHTS = {"_Joint01": 0.25, "_Joint02": 0.65, "_Joint03": 1.0}


def world_data(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons]


def pair(first, second):
    ap, af = world_data(first)
    bp, bf = world_data(second)
    abvh = BVHTree.FromPolygons(ap, af, all_triangles=False)
    bbvh = BVHTree.FromPolygons(bp, bf, all_triangles=False)
    return {"overlap_pairs": len(abvh.overlap(bbvh))}


def relationships():
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
        "middle_keycap": ("TEAMON_Ada_Middle", "TEAMON_Keycap"),
        "ring_keycap": ("TEAMON_Ada_Ring", "TEAMON_Keycap"),
        "little_keycap": ("TEAMON_Ada_Little", "TEAMON_Keycap"),
    }
    return {name: pair(get(a), get(b)) for name, (a, b) in pairs.items()}


def smoothstep(value):
    q = max(0.0, min(1.0, value))
    return q * q * (3.0 - 2.0 * q)


def rotate_offset(point, pivot, yaw, roll, offset, weight):
    rotation = (
        Matrix.Rotation(math.radians(roll * weight), 3, CAMERA_FORWARD)
        @ Matrix.Rotation(math.radians(yaw * weight), 3, CAMERA_UP)
    )
    return pivot + rotation @ (point - pivot) + CAMERA_UP * (offset * weight)


def deform_finger(finger, yaw, roll, offset):
    pivot = PIVOTS[finger]
    shell = bpy.data.objects[f"TEAMON_Ada_{finger}"]
    points = [shell.matrix_world @ vertex.co for vertex in shell.data.vertices]
    centroid = sum(points, Vector()) / len(points)
    axis = (centroid - pivot).normalized()
    length = max((point - pivot).dot(axis) for point in points)
    inverse = shell.matrix_world.inverted_safe()
    for vertex, point in zip(shell.data.vertices, points):
        t = (point - pivot).dot(axis) / length if length > 1.0e-9 else 0.0
        weight = 0.0 if t <= 0.25 else smoothstep((t - 0.25) / 0.45)
        vertex.co = inverse @ rotate_offset(point, pivot, yaw, roll, offset, weight)
    shell.data.update()
    for suffix, weight in JOINT_WEIGHTS.items():
        obj = bpy.data.objects[f"TEAMON_Ada_{finger}{suffix}"]
        inverse = obj.matrix_world.inverted_safe()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            vertex.co = inverse @ rotate_offset(point, pivot, yaw, roll, offset, weight)
        obj.data.update()


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt03 source, got {bpy.data.filepath}")
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
snapshots = {name: [v.co.copy() for v in bpy.data.objects[name].data.vertices] for name in TARGET_NAMES}
results = {}

for label, specs in VARIANTS.items():
    for name, coordinates in snapshots.items():
        obj = bpy.data.objects[name]
        for vertex, coordinate in zip(obj.data.vertices, coordinates):
            vertex.co = coordinate
        obj.data.update()
    for finger, (yaw, roll, offset) in specs.items():
        deform_finger(finger, yaw, roll, offset)
    bpy.context.view_layer.update()
    output = OUT_DIR / f"teamon-v45-mrl-cage-{label}.png"
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    results[label] = {"specs": specs, "render": str(output), "relationships": relationships()}

REPORT_PATH.write_text(json.dumps({"source": str(SOURCE_BLEND), "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, ensure_ascii=False, indent=2))
