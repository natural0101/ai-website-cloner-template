"""Read-only object/material inventory for the A47 material stage."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v6_tail_side_sweep_remediation_attempt47.blend"
).resolve()
REPORT_PATH = (
    WORKBENCH / "artifacts" / "reports" / "comforting_cat_v6_attempt47_material_probe.json"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")


def value(input_socket):
    item = input_socket.default_value
    if hasattr(item, "__len__") and not isinstance(item, str):
        return [round(float(component), 6) for component in item]
    return round(float(item), 6)


materials = {}
for material in bpy.data.materials:
    principled = None
    if material.use_nodes and material.node_tree is not None:
        principled = next(
            (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
            None,
        )
    materials[material.name] = {
        "users": material.users,
        "use_nodes": material.use_nodes,
        "principled": {
            socket.name: value(socket)
            for socket in principled.inputs
            if socket.name
            in {
                "Base Color",
                "Metallic",
                "Roughness",
                "IOR",
                "Alpha",
                "Coat Weight",
                "Coat Roughness",
                "Sheen Weight",
                "Sheen Roughness",
            }
        }
        if principled is not None
        else None,
        "node_types": sorted(node.type for node in material.node_tree.nodes)
        if material.use_nodes and material.node_tree is not None
        else [],
    }

objects = {}
for obj in bpy.context.scene.objects:
    if obj.name.startswith("V6_") and hasattr(obj.data, "materials"):
        objects[obj.name] = [slot.name for slot in obj.data.materials]

payload = {
    "source_blend": str(SOURCE_BLEND),
    "scene": bpy.context.scene.name,
    "materials": materials,
    "object_material_slots": objects,
}
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
