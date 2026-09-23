"""Read-only A89 brow control-point and head-surface probe for A90."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_front_cheek_taper_attempt89.blend"
).resolve()
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

head = bpy.data.objects["V6_Head"]
depsgraph = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(head, depsgraph)
payload: dict[str, object] = {}
for name in ("V6_Eyebrow_L", "V6_Eyebrow_R"):
    obj = bpy.data.objects[name]
    points = []
    for spline in obj.data.splines:
        for point in spline.bezier_points:
            world = obj.matrix_world @ point.co
            local_origin = head.matrix_world.inverted() @ Vector((world.x, -2.0, world.z))
            local_direction = head.matrix_world.inverted().to_3x3() @ Vector((0.0, 1.0, 0.0))
            hit, _normal, _index, _distance = bvh.ray_cast(local_origin, local_direction)
            surface = head.matrix_world @ hit if hit is not None else None
            points.append(
                {
                    "co": [round(float(value), 6) for value in world],
                    "surface_y": round(float(surface.y), 6) if surface is not None else None,
                    "front_gap": round(float(surface.y - world.y), 6) if surface is not None else None,
                    "radius": round(float(point.radius), 6),
                }
            )
    payload[name] = {
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "collections": [collection.name for collection in obj.users_collection],
        "material": obj.data.materials[0].name if obj.data.materials else None,
        "bevel_depth": round(float(obj.data.bevel_depth), 6),
        "points": points,
    }
print(json.dumps(payload, ensure_ascii=False, indent=2))
