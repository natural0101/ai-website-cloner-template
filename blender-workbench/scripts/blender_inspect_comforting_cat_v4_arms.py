"""Read-only inspection of the accepted v4 cat arm and sleeve geometry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
TOOLS = (WORKBENCH / "research-feedback-upgrade" / "04_blender").resolve()
TOOLS.relative_to(WORKBENCH)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import capability_probe


def object_record(name: str) -> dict[str, object]:
    obj = bpy.data.objects[name]
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "name": name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": [round(float(value), 6) for value in obj.location],
        "rotation_euler": [round(float(value), 6) for value in obj.rotation_euler],
        "scale": [round(float(value), 6) for value in obj.scale],
        "dimensions": [round(float(value), 6) for value in obj.dimensions],
        "world_aabb_min": [round(float(value), 6) for value in mins],
        "world_aabb_max": [round(float(value), 6) for value in maxs],
        "vertices": len(obj.data.vertices) if obj.type == "MESH" else None,
        "polygons": len(obj.data.polygons) if obj.type == "MESH" else None,
        "modifiers": [
            {"name": modifier.name, "type": modifier.type}
            for modifier in obj.modifiers
        ],
    }


names = [
    "Cat_Sleeve_L",
    "Cat_Arm_L",
    "Cat_Sleeve_R",
    "Cat_Arm_R",
    "Cat_BlueRobe",
    "Cat_Body",
]
report = {
    "filepath": str(Path(bpy.data.filepath).resolve()),
    "scene": bpy.context.scene.name,
    "scene_stage": bpy.context.scene.get("comforting_cat_v4_stage"),
    "scene_attempt": bpy.context.scene.get("comforting_cat_v4_geometry_attempt"),
    "capability_probe": capability_probe.probe(),
    "objects": [object_record(name) for name in names],
}
print("COMFORTING_CAT_V4_ARM_INSPECTION=" + json.dumps(report, ensure_ascii=False))
