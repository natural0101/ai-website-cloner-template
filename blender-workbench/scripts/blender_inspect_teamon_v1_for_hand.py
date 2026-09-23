import json

import bpy


scene = bpy.context.scene
mesh_objects = [obj for obj in scene.objects if obj.type == "MESH"]
for obj in mesh_objects:
    obj.data.calc_loop_triangles()

payload = {
    "scene": scene.name,
    "blender_version": bpy.app.version_string,
    "collections": sorted(collection.name for collection in bpy.data.collections),
    "object_count": len(scene.objects),
    "mesh_count": len(mesh_objects),
    "triangle_count": sum(len(obj.data.loop_triangles) for obj in mesh_objects),
    "objects": [
        {
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "location": [round(value, 4) for value in obj.location],
            "dimensions": [round(value, 4) for value in obj.dimensions],
        }
        for obj in sorted(scene.objects, key=lambda item: item.name)
    ],
    "ai_blender_toolkit_available": False,
}

print("TEAMON_V1_SCENE_INSPECT=" + json.dumps(payload, ensure_ascii=False))
