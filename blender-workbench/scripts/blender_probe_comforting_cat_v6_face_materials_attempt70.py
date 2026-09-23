"""Read-only material and bounds probe for the A70 face stack."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v6_face_envelope_relock_attempt70.blend"
).resolve()
REPORT_PATH = (
    WORKBENCH / "artifacts" / "reports" / "comforting_cat_v6_attempt70_face_material_probe.json"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")


def socket_value(socket):
    value = socket.default_value
    if hasattr(value, "__len__") and not isinstance(value, str):
        return [round(float(component), 6) for component in value]
    return round(float(value), 6)


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [round(float(maxs[i] - mins[i]), 6) for i in range(3)],
    }


names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
    "V6_Nose",
]
objects = {}
materials = {}
for name in names:
    obj = bpy.data.objects[name]
    slots = [material.name for material in obj.data.materials]
    objects[name] = {"bounds": bounds(obj), "materials": slots}
    for material in obj.data.materials:
        principled = None
        if material.use_nodes and material.node_tree is not None:
            principled = next(
                (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
                None,
            )
        materials[material.name] = {
            "users": material.users,
            "principled": {
                socket.name: socket_value(socket)
                for socket in principled.inputs
                if socket.name in {"Base Color", "Metallic", "Roughness", "IOR", "Coat Weight", "Coat Roughness"}
            }
            if principled is not None
            else None,
        }

payload = {
    "source_blend": str(SOURCE_BLEND),
    "objects": objects,
    "materials": materials,
}
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
