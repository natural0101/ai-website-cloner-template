import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "rebelia_v2_scene_inventory.json"


def object_record(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated.to_mesh() if obj.type == "MESH" else None
    try:
        vertices = len(evaluated_mesh.vertices) if evaluated_mesh else 0
        polygons = len(evaluated_mesh.polygons) if evaluated_mesh else 0
    finally:
        if evaluated_mesh is not None:
            evaluated.to_mesh_clear()
    world_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bounds_min = [min(point[axis] for point in world_corners) for axis in range(3)]
    bounds_max = [max(point[axis] for point in world_corners) for axis in range(3)]
    return {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": list(obj.matrix_world.translation),
        "dimensions": list(obj.dimensions),
        "bounds_min": bounds_min,
        "bounds_max": bounds_max,
        "vertices_evaluated": vertices,
        "polygons_evaluated": polygons,
        "hidden_render": obj.hide_render,
        "collections": [collection.name for collection in obj.users_collection],
    }


tokens = (
    "cover",
    "palm",
    "finger",
    "thumb",
    "mcp center",
    "pip center",
    "dip center",
    "hand back",
    "flexmods",
    "flex v",
    "3dp",
    "safety",
)
matches = [obj for obj in bpy.data.objects if any(token in obj.name.lower() for token in tokens)]
payload = {
    "source_blend": bpy.data.filepath,
    "scene_objects": len(bpy.data.objects),
    "matches": [object_record(obj) for obj in sorted(matches, key=lambda item: item.name.lower())],
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"report": str(REPORT_PATH), "matches": len(matches)}, ensure_ascii=False))
