import json

import bpy
from mathutils import Vector


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


keycap = bpy.data.objects.get("TEAMON_Keycap")
index_meshes = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("mjcf_body") == "rh_ffdistal" and not obj.hide_render
]
report = {"index_candidates": [obj.name for obj in index_meshes], "frames": {}}
for frame in (1, 24):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    report["frames"][str(frame)] = {
        "keycap": bounds(keycap),
        "index": bounds(index_meshes[0]),
        "index_matrix_world": [list(row) for row in index_meshes[0].matrix_world],
        "index_matrix_local": [list(row) for row in index_meshes[0].matrix_local],
        "index_parent": index_meshes[0].parent.name if index_meshes[0].parent else None,
        "press_group_matrix_world": [list(row) for row in bpy.data.objects["TEAMON_HandPressGroup"].matrix_world],
    }
print(json.dumps(report, ensure_ascii=False, indent=2))
