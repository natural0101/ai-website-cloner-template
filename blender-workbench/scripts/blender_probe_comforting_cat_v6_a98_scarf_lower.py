"""Read-only measurements for the A98 lower scarf wrap."""

from __future__ import annotations

import bmesh
import hashlib
import json
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_compact_kitten_body_attempt98.blend"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")


def world_points(obj: bpy.types.Object):
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = world_points(obj)
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {
        "min": [round(value, 9) for value in minimum],
        "max": [round(value, 9) for value in maximum],
        "dimensions": [round(maximum[i] - minimum[i], 9) for i in range(3)],
    }


def topology(obj: bpy.types.Object) -> dict[str, int]:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    result = {
        "vertices": len(mesh.verts),
        "edges": len(mesh.edges),
        "faces": len(mesh.faces),
        "boundary_edges": sum(1 for edge in mesh.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in mesh.edges if not edge.is_manifold),
        "loose_vertices": sum(1 for vertex in mesh.verts if not vertex.link_edges),
    }
    mesh.free()
    return result


def points_hash(obj: bpy.types.Object) -> str:
    digest = hashlib.sha256()
    for index, point in enumerate(world_points(obj)):
        digest.update(f"{index}:{point.x:.9f},{point.y:.9f},{point.z:.9f};".encode("ascii"))
    return digest.hexdigest()


def region(obj: bpy.types.Object, predicate) -> dict[str, object]:
    selected = [(index, point) for index, point in enumerate(world_points(obj)) if predicate(point)]
    if not selected:
        return {"count": 0}
    xs = [point.x for _, point in selected]
    return {
        "count": len(selected),
        "indices": [index for index, _ in selected],
        "x_min": round(min(xs), 9),
        "x_max": round(max(xs), 9),
        "x_span": round(max(xs) - min(xs), 9),
    }


lower = bpy.data.objects["V6_ScarfWrap_Lower"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
robe = bpy.data.objects["V6_Robe"]
head = bpy.data.objects["V6_Head"]

result = {
    "source": str(SOURCE_BLEND),
    "lower_bounds": bounds(lower),
    "upper_bounds": bounds(upper),
    "robe_bounds": bounds(robe),
    "head_bounds": bounds(head),
    "lower_topology": topology(lower),
    "lower_hash": points_hash(lower),
    "frontmost": region(lower, lambda point: point.y <= -0.12),
    "front_transition": region(lower, lambda point: -0.12 < point.y < 0.10),
    "rear_locked": region(lower, lambda point: point.y >= 0.10),
    "scarf_objects": {
        obj.name: bounds(obj)
        for obj in bpy.data.objects
        if "Scarf" in obj.name and obj.type == "MESH" and not obj.hide_render
    },
}
print("A98_SCARF_PROBE=" + json.dumps(result, ensure_ascii=False))
