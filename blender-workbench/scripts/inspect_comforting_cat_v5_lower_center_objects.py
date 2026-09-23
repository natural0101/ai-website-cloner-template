"""Read-only identification of objects visible below the robe hem."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


EXPECTED = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend\comforting_cat_v5_cloak_leg_blockout_attempt2.blend"
).resolve()
if Path(bpy.data.filepath).resolve() != EXPECTED:
    raise RuntimeError(f"Expected already-open {EXPECTED}; got {bpy.data.filepath}")


def object_bounds(obj: bpy.types.Object) -> dict[str, object]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "hide_render": obj.hide_render,
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
    }


rows = []
for obj in bpy.data.objects:
    if not obj.name.startswith("Cat_") or obj.type not in {"MESH", "CURVE"}:
        continue
    row = object_bounds(obj)
    if row["min"][2] < 0.82 and row["max"][2] > 0.35:
        rows.append(row)
print(
    "COMFORTING_CAT_V5_LOWER_CENTER_OBJECTS="
    + json.dumps(sorted(rows, key=lambda row: row["name"]), ensure_ascii=False)
)
