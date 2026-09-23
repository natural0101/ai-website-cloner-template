from __future__ import annotations

import json
from mathutils import Vector
import bpy


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {"min": minimum, "max": maximum}


payload = {
    "scene": bpy.data.filepath,
    "collections": [collection.name for collection in bpy.data.collections],
    "objects": [],
}
for obj in bpy.data.objects:
    item = {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
    }
    if obj.type == "MESH":
        item["bounds"] = world_bounds(obj)
    payload["objects"].append(item)

print("TEAMON_INSPECT_BEGIN")
print(json.dumps(payload, ensure_ascii=False))
print("TEAMON_INSPECT_END")
