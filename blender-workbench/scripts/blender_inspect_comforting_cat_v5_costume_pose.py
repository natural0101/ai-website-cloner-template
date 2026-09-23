"""Read-only transform and bounds inspection for costume and pose nodes."""

from __future__ import annotations

import json

import bpy
from mathutils import Vector


NAMES = [
    "Cat_BlueRobe",
    "Cat_RobeFrontInset",
    "Cat_ScarfWrap",
    "Cat_ScarfUpperFold",
    "Cat_ScarfLowerDrape",
    "Cat_Sleeve_L",
    "Cat_Sleeve_R",
    "Cat_Arm_L",
    "Cat_Arm_R",
    "Cat_Paw_L",
    "Cat_Paw_R",
    "Cat_Leg_L",
    "Cat_Leg_R",
    "Cat_Foot_L",
    "Cat_Foot_R",
    "Cat_SatchelBag",
    "Cat_SatchelStrap",
    "Cat_Tail_Base",
    "Cat_Tail_CreamTip",
]


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
        "center": [
            round(float((mins[index] + maxs[index]) * 0.5), 6)
            for index in range(3)
        ],
    }


report = {
    "blend": bpy.data.filepath,
    "objects": {
        name: {
            "type": bpy.data.objects[name].type,
            "parent": (
                bpy.data.objects[name].parent.name
                if bpy.data.objects[name].parent
                else None
            ),
            "location_world": [
                round(float(value), 6)
                for value in bpy.data.objects[name].matrix_world.translation
            ],
            "bounds_world": bounds(bpy.data.objects[name]),
        }
        for name in NAMES
        if name in bpy.data.objects
    },
}
print("COMFORTING_CAT_V5_COSTUME_POSE_INSPECTION=" + json.dumps(report))
