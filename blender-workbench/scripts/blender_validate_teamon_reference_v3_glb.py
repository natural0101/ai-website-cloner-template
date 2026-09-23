import json
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v3.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_glb_validation.json"
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min_z": min(point.z for point in corners),
        "max_z": max(point.z for point in corners),
    }


def contact_gap(frame):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    cap = bpy.data.objects.get("TEAMON_Keycap")
    pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
    if cap is None or pad is None:
        return None
    return world_bounds(pad)["min_z"] - world_bounds(cap)["max_z"]


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB_PATH))

objects = list(bpy.context.scene.objects)
meshes = [obj for obj in objects if obj.type == "MESH"]
names = {obj.name for obj in objects}
required = {
    "TEAMON_CompositionRoot",
    "TEAMON_ButtonRoot",
    "TEAMON_PressGroup",
    "TEAMON_Base",
    "TEAMON_Keycap",
    "TEAMON_Text",
    "TEAMON_HandRoot",
    "TEAMON_HandPressGroup",
    "TEAMON_PalmShell",
    "TEAMON_WristHousing_V3",
    "TEAMON_Index_ContactPad",
}
rejected_tokens = ("ContinuousShell", "DorsalArmor", "Proximal_Shell", "Middle_Shell", "Distal_Shell", "JointPin")
unexpected_rejected = sorted(name for name in names if any(token in name for token in rejected_tokens))

topology = []
triangle_count = 0
for obj in meshes:
    obj.data.calc_loop_triangles()
    triangle_count += len(obj.data.loop_triangles)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    topology.append({
        "name": obj.name,
        "triangles": len(obj.data.loop_triangles),
        "loose_vertices": sum(1 for vertex in bm.verts if not vertex.link_edges),
        "degenerate_faces": sum(1 for face in bm.faces if face.calc_area() <= 1e-10),
        "negative_scale": any(value < 0 for value in obj.scale),
    })
    bm.free()

actions = sorted(action.name for action in bpy.data.actions)
rest_gap = contact_gap(1)
pressed_gap = contact_gap(30)
missing = sorted(required - names)
errors = []
if missing:
    errors.append("missing required nodes")
if unexpected_rejected:
    errors.append("rejected checkpoint parts leaked into GLB")
if triangle_count > 25000:
    errors.append("mobile triangle budget exceeded")
if not actions:
    errors.append("animation missing")
if rest_gap is None or abs(rest_gap) > 0.015:
    errors.append("rest contact failed")
if pressed_gap is None or abs(pressed_gap) > 0.015:
    errors.append("pressed contact failed")
if any(item["loose_vertices"] or item["degenerate_faces"] or item["negative_scale"] for item in topology):
    errors.append("topology or transform error")

report = {
    "asset": "TEAMON reference v3 GLB validation",
    "glb": str(GLB_PATH),
    "file_size_bytes": GLB_PATH.stat().st_size,
    "object_count": len(objects),
    "mesh_count": len(meshes),
    "triangle_count": triangle_count,
    "within_mobile_budget": triangle_count <= 25000,
    "actions": actions,
    "missing_required_nodes": missing,
    "unexpected_rejected_nodes": unexpected_rejected,
    "contact": {
        "rest_gap": rest_gap,
        "pressed_gap": pressed_gap,
        "tolerance": 0.015,
    },
    "topology": topology,
    "validation_errors": errors,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
