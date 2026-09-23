"""Read-only probe for A98 eye, pupil and highlight geometry before A99 lids."""

from __future__ import annotations

import json

import bpy
from mathutils import Vector


def summary(obj: bpy.types.Object) -> dict:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    result = {
        "name": obj.name,
        "type": obj.type,
        "bounds": {
            "min": [round(min(point[axis] for point in corners), 7) for axis in range(3)],
            "max": [round(max(point[axis] for point in corners), 7) for axis in range(3)],
        },
        "matrix_world": [[round(float(value), 7) for value in row] for row in obj.matrix_world],
    }
    if obj.type == "MESH":
        front_faces = 0
        back_faces = 0
        side_faces = 0
        for polygon in obj.data.polygons:
            normal = obj.matrix_world.to_3x3() @ polygon.normal
            if normal.y < -0.35:
                front_faces += 1
            elif normal.y > 0.35:
                back_faces += 1
            else:
                side_faces += 1
        result.update(
            {
                "vertices": len(obj.data.vertices),
                "edges": len(obj.data.edges),
                "faces": len(obj.data.polygons),
                "normal_face_groups": {
                    "front": front_faces,
                    "back": back_faces,
                    "side": side_faces,
                },
                "materials": [material.name if material else None for material in obj.data.materials],
                "modifiers": [modifier.type for modifier in obj.modifiers],
            }
        )
    return result


names = [
    "V6_Head",
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Eyebrow_L",
    "V6_Eyebrow_R",
]
print(
    "A98_UPPER_LID_PROBE="
    + json.dumps([summary(bpy.data.objects[name]) for name in names], ensure_ascii=False)
)
