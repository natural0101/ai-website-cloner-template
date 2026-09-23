import importlib.util
import json

import bpy


payload = {
    "blender_version": bpy.app.version_string,
    "scene": bpy.context.scene.name,
    "object_count": len(bpy.context.scene.objects),
    "objects": [
        {"name": obj.name, "type": obj.type}
        for obj in bpy.context.scene.objects
    ],
    "ai_blender_toolkit_available": importlib.util.find_spec("ai_blender_toolkit") is not None,
    "render_engines": [item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items],
}

print("TEAMON_SCENE_PROBE=" + json.dumps(payload, ensure_ascii=False))
