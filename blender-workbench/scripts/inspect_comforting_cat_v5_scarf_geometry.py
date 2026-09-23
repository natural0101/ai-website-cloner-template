"""Read-only inspection of the current scarf geometry."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v5_satchel_hip_attempt1.blend"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))


def describe(name: str) -> dict[str, object]:
    obj = bpy.data.objects[name]
    world_vertices = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    mins = [min(point[index] for point in world_vertices) for index in range(3)]
    maxs = [max(point[index] for point in world_vertices) for index in range(3)]
    samples = sorted(
        (
            [round(float(point.x), 5), round(float(point.y), 5), round(float(point.z), 5)]
            for point in world_vertices
        ),
        key=lambda value: (-value[2], value[0], value[1]),
    )
    return {
        "name": name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": [round(float(value), 5) for value in obj.location],
        "rotation": [round(float(value), 5) for value in obj.rotation_euler],
        "scale": [round(float(value), 5) for value in obj.scale],
        "vertex_count": len(obj.data.vertices),
        "bounds": {
            "min": [round(float(value), 5) for value in mins],
            "max": [round(float(value), 5) for value in maxs],
        },
        "top_vertices": samples[:12],
        "bottom_vertices": list(reversed(samples[-12:])),
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
    }


names = [
    "Cat_ScarfWrap",
    "Cat_ScarfUpperFold",
    "Cat_ScarfLowerDrape",
    "Cat_BlueRobe",
]
report = {name: describe(name) for name in names}
print("COMFORTING_CAT_V5_SCARF_GEOMETRY=" + json.dumps(report, ensure_ascii=False))
