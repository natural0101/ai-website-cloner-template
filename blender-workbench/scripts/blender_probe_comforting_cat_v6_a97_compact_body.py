"""Read-only capability and geometry probe for the bounded A98 body silhouette pass."""

from __future__ import annotations

import json

import bpy


def world_vertices(obj: bpy.types.Object) -> list[tuple[int, float, float, float]]:
    result = []
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        result.append((vertex.index, float(point.x), float(point.y), float(point.z)))
    return result


def band_profile(obj: bpy.types.Object, centers: list[float], half_band: float = 0.055) -> list[dict]:
    vertices = world_vertices(obj)
    result = []
    for center in centers:
        selected = [item for item in vertices if abs(item[3] - center) <= half_band]
        if not selected:
            continue
        result.append(
            {
                "z": center,
                "count": len(selected),
                "min_x": round(min(item[1] for item in selected), 6),
                "max_x": round(max(item[1] for item in selected), 6),
                "half_width": round(max(abs(item[1]) for item in selected), 6),
                "min_y": round(min(item[2] for item in selected), 6),
                "max_y": round(max(item[2] for item in selected), 6),
            }
        )
    return result


def object_summary(obj: bpy.types.Object) -> dict:
    used_by_material: dict[str, set[int]] = {}
    for polygon in obj.data.polygons:
        material_name = (
            obj.data.materials[polygon.material_index].name
            if polygon.material_index < len(obj.data.materials)
            else f"slot_{polygon.material_index}"
        )
        used_by_material.setdefault(material_name, set()).update(polygon.vertices)
    vertices = world_vertices(obj)
    return {
        "name": obj.name,
        "matrix_world": [[round(float(value), 7) for value in row] for row in obj.matrix_world],
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "polygons": len(obj.data.polygons),
        "materials": [material.name if material else None for material in obj.data.materials],
        "used_vertices_by_material": {
            name: len(indices) for name, indices in sorted(used_by_material.items())
        },
        "bounds": {
            "min": [round(min(item[axis + 1] for item in vertices), 6) for axis in range(3)],
            "max": [round(max(item[axis + 1] for item in vertices), 6) for axis in range(3)],
        },
        "modifiers": [modifier.type for modifier in obj.modifiers],
    }


def rounded_z_profile(obj: bpy.types.Object, precision: int = 3) -> list[dict]:
    groups: dict[float, list[tuple[int, float, float, float]]] = {}
    for item in world_vertices(obj):
        groups.setdefault(round(item[3], precision), []).append(item)
    return [
        {
            "z": z,
            "count": len(items),
            "min_x": round(min(item[1] for item in items), 6),
            "max_x": round(max(item[1] for item in items), 6),
        }
        for z, items in sorted(groups.items())
    ]


robe = bpy.data.objects["V6_Robe"]
left = bpy.data.objects["V6_ArmUnified_L"]
right = bpy.data.objects["V6_ArmUnified_R"]
head = bpy.data.objects["V6_Head"]

payload = {
    "objects": [object_summary(obj) for obj in (head, robe, left, right)],
    "robe_profile": band_profile(
        robe,
        [0.60, 0.68, 0.76, 0.90, 1.10, 1.30, 1.50, 1.70, 1.90, 2.05, 2.18],
    ),
    "robe_rounded_z_profile": rounded_z_profile(robe),
    "left_arm_profile": band_profile(left, [0.90, 1.10, 1.30, 1.50, 1.62, 1.75, 1.90]),
    "right_arm_profile": band_profile(right, [0.98, 1.15, 1.32, 1.50, 1.64, 1.78, 1.90]),
}
print("A97_COMPACT_BODY_PROBE=" + json.dumps(payload, ensure_ascii=False))
