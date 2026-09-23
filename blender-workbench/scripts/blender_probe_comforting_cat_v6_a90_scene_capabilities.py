"""Read-only A90 scene/capability/ear-contact report before A96 geometry."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_brow_surface_ribbon_attempt90.blend"
).resolve()
CAPABILITY_PROBE = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "capability_probe.py"
).resolve()
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
camera = bpy.data.objects["CAT_RenderCamera"]
payload = {
    "source": str(SOURCE_BLEND),
    "target_mode": "TRUE_360",
    "reference": str(WORKBENCH / "references" / "comforting_cat_front_target.png"),
    "camera": {
        "name": camera.name,
        "type": camera.data.type,
        "ortho_scale": round(float(camera.data.ortho_scale), 6),
        "render_resolution": [
            int(bpy.context.scene.render.resolution_x),
            int(bpy.context.scene.render.resolution_y),
        ],
    },
    "capabilities": runpy.run_path(str(CAPABILITY_PROBE))["probe"](),
    "scene": {
        "root": root.name,
        "objects": len(bpy.data.objects),
        "meshes": sum(1 for obj in bpy.data.objects if obj.type == "MESH"),
        "materials": len(bpy.data.materials),
    },
    "head": world_bounds(head),
    "ears": {},
    "expected_contacts": [
        {
            "relation": "OVERLAPS",
            "parts": ["V6_Ear_L", "V6_Head"],
            "minimum_hidden_root_depth": 0.025,
        },
        {
            "relation": "OVERLAPS",
            "parts": ["V6_Ear_R", "V6_Head"],
            "minimum_hidden_root_depth": 0.025,
        },
    ],
    "hidden_surface_assumption": (
        "The single front reference does not specify the rear ear shell. "
        "A96 interprets it as a shallow tapered cup whose hidden saddle remains inside the skull."
    ),
}
for name in ear_names:
    obj = bpy.data.objects[name]
    payload["ears"][name] = {
        "type": obj.type,
        "bounds": world_bounds(obj),
        "topology": [
            len(obj.data.vertices),
            len(obj.data.edges),
            len(obj.data.polygons),
        ],
        "parent": obj.parent.name if obj.parent else None,
        "collection": [collection.name for collection in obj.users_collection],
        "modifiers": [modifier.type for modifier in obj.modifiers],
        "material": obj.data.materials[0].name if obj.data.materials else None,
    }
print(json.dumps(payload, ensure_ascii=False, indent=2))
