"""Read-only inspection of the current head and ear geometry."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


EXPECTED = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend\comforting_cat_v5_soft_scarf_attempt3.blend"
).resolve()
if Path(bpy.data.filepath).resolve() != EXPECTED:
    raise RuntimeError(f"Expected already-open {EXPECTED}; got {bpy.data.filepath}")


def describe(name: str) -> dict[str, object]:
    obj = bpy.data.objects[name]
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    z_slices = []
    for step in range(9):
        z0 = mins[2] + (maxs[2] - mins[2]) * step / 8
        tolerance = (maxs[2] - mins[2]) / 32
        selected = [point for point in points if abs(point.z - z0) <= tolerance]
        if selected:
            z_slices.append(
                {
                    "z": round(float(z0), 5),
                    "x_min": round(float(min(point.x for point in selected)), 5),
                    "x_max": round(float(max(point.x for point in selected)), 5),
                    "y_min": round(float(min(point.y for point in selected)), 5),
                    "y_max": round(float(max(point.y for point in selected)), 5),
                    "count": len(selected),
                }
            )
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
        "z_slices": z_slices,
    }


selected_names = ["Cat_Head_Mesh"]
selected_names.extend(
    sorted(name for name in bpy.data.objects.keys() if "Ear" in name and name.startswith("Cat_"))
)
report = {name: describe(name) for name in selected_names}
print("COMFORTING_CAT_V5_HEAD_GEOMETRY=" + json.dumps(report, ensure_ascii=False))
