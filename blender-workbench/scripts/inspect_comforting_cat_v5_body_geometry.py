"""Read-only inspection of the current body, robe, and leg geometry."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


EXPECTED = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend\comforting_cat_v5_head_fur_mass_attempt1.blend"
).resolve()
if Path(bpy.data.filepath).resolve() != EXPECTED:
    raise RuntimeError(f"Expected already-open {EXPECTED}; got {bpy.data.filepath}")


def describe(name: str) -> dict[str, object]:
    obj = bpy.data.objects[name]
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "name": name,
        "parent": obj.parent.name if obj.parent else None,
        "vertex_count": len(points),
        "bounds": {
            "min": [round(float(value), 5) for value in mins],
            "max": [round(float(value), 5) for value in maxs],
            "dimensions": [
                round(float(maxs[index] - mins[index]), 5) for index in range(3)
            ],
        },
    }


tokens = ("Body", "Robe", "Leg", "Foot", "Arm", "Paw", "Sleeve")
names = sorted(
    name
    for name, obj in bpy.data.objects.items()
    if name.startswith("Cat_") and obj.type == "MESH" and any(token in name for token in tokens)
)
report = {name: describe(name) for name in names}
print("COMFORTING_CAT_V5_BODY_GEOMETRY=" + json.dumps(report, ensure_ascii=False))
