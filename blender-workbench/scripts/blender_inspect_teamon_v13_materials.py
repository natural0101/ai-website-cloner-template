from __future__ import annotations

import json

import bpy


def socket_value(socket):
    value = getattr(socket, "default_value", None)
    if hasattr(value, "__len__") and not isinstance(value, str):
        return [float(item) for item in value]
    if isinstance(value, (int, float, bool, str)):
        return value
    return None


report = {"objects": {}, "materials": {}}
for name in (
    "TEAMON_Base",
    "TEAMON_Recess",
    "TEAMON_RGB_Underplate",
    "TEAMON_Keycap",
    "TEAMON_Text",
):
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    report["objects"][name] = {
        "dimensions": [float(value) for value in obj.dimensions],
        "location": [float(value) for value in obj.location],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
    }

for material in bpy.data.materials:
    if material.name != "TEAMON_RGB_Continuous_Gradient":
        continue
    nodes = []
    if material.use_nodes and material.node_tree:
        for node in material.node_tree.nodes:
            if node.type in {"BSDF_PRINCIPLED", "EMISSION", "TEX_GRADIENT", "VALTORGB", "TEX_COORD", "MAPPING", "MIX_RGB", "VECTOR_MATH"}:
                node_data = {
                    "name": node.name,
                    "type": node.type,
                    "inputs": {
                        socket.name: socket_value(socket)
                        for socket in node.inputs
                        if socket_value(socket) is not None
                    },
                }
                if node.type == "VALTORGB":
                    node_data["ramp"] = [
                        {"position": float(element.position), "color": [float(value) for value in element.color]}
                        for element in node.color_ramp.elements
                    ]
                nodes.append(node_data)
    report["materials"][material.name] = {
        "surface_render_method": getattr(material, "surface_render_method", None),
        "nodes": nodes,
        "links": [
            {
                "from": f"{link.from_node.name}.{link.from_socket.name}",
                "to": f"{link.to_node.name}.{link.to_socket.name}",
            }
            for link in material.node_tree.links
        ] if material.use_nodes and material.node_tree else [],
    }

print(json.dumps(report, ensure_ascii=False, indent=2))
