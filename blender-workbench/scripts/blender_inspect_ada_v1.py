from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REPORT_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "reports"
    / "openbionics_ada_v1_scene_inventory.json"
)


def mesh_stats(obj: bpy.types.Object) -> dict[str, int]:
    if obj.type != "MESH":
        return {"vertices": 0, "edges": 0, "polygons": 0, "triangles": 0}
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
        }
    finally:
        evaluated.to_mesh_clear()


def world_bounds(obj: bpy.types.Object) -> tuple[list[float], list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        [min(point[axis] for point in corners) for axis in range(3)],
        [max(point[axis] for point in corners) for axis in range(3)],
    )


def record(obj: bpy.types.Object) -> dict[str, object]:
    bounds_min, bounds_max = world_bounds(obj)
    raw_mesh = {
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "polygons": len(obj.data.polygons),
    } if obj.type == "MESH" else None
    return {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "children": [child.name for child in obj.children],
        "location_world": list(obj.matrix_world.translation),
        "rotation_euler": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
        "bounds_min": bounds_min,
        "bounds_max": bounds_max,
        "mesh": mesh_stats(obj),
        "raw_mesh": raw_mesh,
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "modifiers": [
            {
                "name": modifier.name,
                "type": modifier.type,
                "levels": getattr(modifier, "levels", None),
                "render_levels": getattr(modifier, "render_levels", None),
                "operation": getattr(modifier, "operation", None),
                "operand": getattr(getattr(modifier, "object", None), "name", None),
            }
            for modifier in obj.modifiers
        ],
        "hidden_viewport": obj.hide_viewport,
        "hidden_render": obj.hide_render,
        "collections": [collection.name for collection in obj.users_collection],
    }


objects = sorted(bpy.data.objects, key=lambda item: item.name.lower())
payload = {
    "source_blend": bpy.data.filepath,
    "blender_version": bpy.app.version_string,
    "scene_name": bpy.context.scene.name,
    "scene_objects": len(objects),
    "collections": [collection.name for collection in bpy.data.collections],
    "actions": [action.name for action in bpy.data.actions],
    "objects": [record(obj) for obj in objects],
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"report": str(REPORT_PATH), "objects": len(objects)}, ensure_ascii=False))
