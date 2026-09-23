"""Read-only probe of the A91 back-right robe/tail wedge contact."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_lower_garment_rehang_attempt91.blend"
).resolve()
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

tail = bpy.data.objects["V6_TailBase"]
robe = bpy.data.objects["V6_Robe"]
tail_points = []
for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    if 0.30 <= world.x <= 0.75 and 0.42 <= world.z <= 0.76:
        tail_points.append([round(float(value), 6) for value in world])
robe_points = []
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if 0.25 <= world.x <= 0.75 and 0.42 <= world.z <= 0.76 and world.y >= 0.0:
        robe_points.append([round(float(value), 6) for value in world])
payload = {
    "tail_count": len(tail_points),
    "tail_points_by_max_y": sorted(tail_points, key=lambda point: point[1], reverse=True)[:40],
    "robe_count": len(robe_points),
    "robe_points_by_min_z": sorted(robe_points, key=lambda point: point[2])[:40],
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
