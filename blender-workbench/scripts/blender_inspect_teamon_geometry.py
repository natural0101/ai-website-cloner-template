from __future__ import annotations

import json

import bpy


report = {}
for name in ("TEAMON_Base", "TEAMON_Recess", "TEAMON_RGB_Underplate", "TEAMON_Keycap"):
    obj = bpy.data.objects[name]
    report[name] = {
        "dimensions": [float(value) for value in obj.dimensions],
        "scale": [float(value) for value in obj.scale],
        "modifiers": [
            {
                "name": modifier.name,
                "type": modifier.type,
                "width": float(getattr(modifier, "width", 0.0)),
                "segments": int(getattr(modifier, "segments", 0)),
            }
            for modifier in obj.modifiers
        ],
    }

print(json.dumps(report, ensure_ascii=False, indent=2))
