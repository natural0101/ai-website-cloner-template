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
OUT_DIR = WORKBENCH / "artifacts" / "previews" / "teamon-v45-mrl-roll-sweep"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_mrl_roll_probe.json"

CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
PIVOTS = {
    "Middle": Vector((2.1240937710, 1.6367094517, 2.5313618183)),
    "Ring": Vector((2.4053313732, 2.4222147465, 2.6238908768)),
    "Little": Vector((2.7574174404, 3.0543124676, 2.7007515430)),
}
VARIANTS = {
    "a_full": {"Middle": 15.0, "Ring": 85.0, "Little": 100.0},
    "b_medium": {"Middle": 15.0, "Ring": 60.0, "Little": 75.0},
    "c_gentle": {"Middle": 20.0, "Ring": 45.0, "Little": 60.0},
    "d_safe": {"Middle": 10.0, "Ring": 35.0, "Little": 50.0},
}
SUFFIXES = ("", "_Joint01", "_Joint02", "_Joint03")
TARGET_NAMES = tuple(f"TEAMON_Ada_{finger}{suffix}" for finger in PIVOTS for suffix in SUFFIXES)


def mesh_world_data(obj):
    return ([obj.matrix_world @ v.co for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons])


def pair_metrics(first, second):
    ap, af = mesh_world_data(first)
    bp, bf = mesh_world_data(second)
    abvh = BVHTree.FromPolygons(ap, af, all_triangles=False)
    bbvh = BVHTree.FromPolygons(bp, bf, all_triangles=False)
    distances = []
    for point in ap:
        hit = bbvh.find_nearest(point)
        if hit is not None:
            distances.append(float(hit[3]))
    for point in bp:
        hit = abvh.find_nearest(point)
        if hit is not None:
            distances.append(float(hit[3]))
    return {"overlap_pairs": len(abvh.overlap(bbvh)), "surface_distance": min(distances) if distances else None}


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
    return {name: pair_metrics(get(a), get(b)) for name, (a, b) in pairs.items()}


def apply_roll(finger, degrees):
    pivot = PIVOTS[finger]
    transform = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(degrees), 4, CAMERA_FORWARD) @ Matrix.Translation(-pivot)
    for suffix in SUFFIXES:
        obj = bpy.data.objects[f"TEAMON_Ada_{finger}{suffix}"]
        local = obj.matrix_world.inverted_safe() @ transform @ obj.matrix_world
        obj.data.transform(local)
        obj.data.update()


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt03 source, got {bpy.data.filepath}")

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
original = {name: [v.co.copy() for v in bpy.data.objects[name].data.vertices] for name in TARGET_NAMES}
report = {"source": str(SOURCE_BLEND), "variants": {}}

for label, rolls in VARIANTS.items():
    for name, coordinates in original.items():
        obj = bpy.data.objects[name]
        for vertex, coordinate in zip(obj.data.vertices, coordinates):
            vertex.co = coordinate
        obj.data.update()
    for finger, degrees in rolls.items():
        apply_roll(finger, degrees)
    bpy.context.view_layer.update()
    image_path = OUT_DIR / f"teamon-v45-mrl-roll-{label}.png"
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(image_path)
    bpy.ops.render.render(write_still=True)
    report["variants"][label] = {
        "rolls": rolls,
        "render": str(image_path),
        "relationships": relationships(),
    }

REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
