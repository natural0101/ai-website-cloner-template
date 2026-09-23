"""Read-only control-point probe for the accepted A72 brows."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_eye_stack_integration_attempt72.blend").resolve()
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

payload = {}
for name in ("V6_Eyebrow_L", "V6_Eyebrow_R"):
    obj = bpy.data.objects[name]
    points = []
    for spline in obj.data.splines:
        for point in spline.bezier_points:
            world = obj.matrix_world @ point.co
            points.append({
                "co": [round(float(v), 6) for v in world],
                "radius": round(float(point.radius), 6),
                "handle_left_type": point.handle_left_type,
                "handle_right_type": point.handle_right_type,
            })
    payload[name] = {
        "type": obj.type,
        "bevel_depth": round(float(obj.data.bevel_depth), 6),
        "bevel_resolution": int(obj.data.bevel_resolution),
        "resolution_u": int(obj.data.resolution_u),
        "points": points,
    }
print(json.dumps(payload, ensure_ascii=False))
