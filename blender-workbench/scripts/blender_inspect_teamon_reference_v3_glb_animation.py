import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v3.glb"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB_PATH))

targets = [bpy.data.objects.get("TEAMON_PressGroup"), bpy.data.objects.get("TEAMON_HandPressGroup")]
payload = {"actions": [action.name for action in bpy.data.actions], "targets": {}}
for obj in targets:
    if obj is None:
        continue
    action = obj.animation_data.action if obj.animation_data else None
    frames = {}
    for frame in (0, 1, 29, 30):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        frames[str(frame)] = {
            "location": list(obj.location),
            "rotation_quaternion": list(obj.rotation_quaternion),
            "rotation_euler": list(obj.rotation_euler),
        }
    payload["targets"][obj.name] = {
        "action": action.name if action else None,
        "frames": frames,
    }
print(json.dumps(payload, ensure_ascii=False, indent=2))
