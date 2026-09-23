import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_click_button_v1.glb"
VALIDATION_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_click_button_v1_glb_validation.json"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB_PATH))

required = {"TEAMON_Root", "TEAMON_PressGroup", "TEAMON_Base", "TEAMON_Keycap", "TEAMON_Text"}
objects = list(bpy.context.scene.objects)
names = {obj.name for obj in objects}
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
for obj in mesh_objects:
    obj.data.calc_loop_triangles()

payload = {
    "glb": str(GLB_PATH),
    "exists": GLB_PATH.exists(),
    "file_size_bytes": GLB_PATH.stat().st_size,
    "object_count": len(objects),
    "mesh_count": len(mesh_objects),
    "triangle_count": sum(len(obj.data.loop_triangles) for obj in mesh_objects),
    "objects": sorted(names),
    "missing_required_nodes": sorted(required - names),
    "validation_errors": [],
}

if payload["missing_required_nodes"]:
    payload["validation_errors"].append("Missing required named nodes")
if payload["triangle_count"] > 100000:
    payload["validation_errors"].append("Triangle budget exceeded")

VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
VALIDATION_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("TEAMON_GLB_VALIDATION=" + json.dumps(payload, ensure_ascii=False))
