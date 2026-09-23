import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_robot_hand_button_v2.glb"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_robot_hand_button_v2_glb_validation.json"


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector((min(point.x for point in corners), min(point.y for point in corners), min(point.z for point in corners)))
    maximum = Vector((max(point.x for point in corners), max(point.y for point in corners), max(point.z for point in corners)))
    return minimum, maximum


def aabb_gap(name_a, name_b):
    obj_a = bpy.data.objects.get(name_a)
    obj_b = bpy.data.objects.get(name_b)
    if obj_a is None or obj_b is None:
        return None
    min_a, max_a = world_bounds(obj_a)
    min_b, max_b = world_bounds(obj_b)
    delta = Vector((
        max(0.0, min_a.x - max_b.x, min_b.x - max_a.x),
        max(0.0, min_a.y - max_b.y, min_b.y - max_a.y),
        max(0.0, min_a.z - max_b.z, min_b.z - max_a.z),
    ))
    return delta.length


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(GLB_PATH))

required = {
    "TEAMON_Root",
    "TEAMON_PressGroup",
    "TEAMON_HandRoot",
    "TEAMON_HandPressGroup",
    "TEAMON_Palm_Shell",
    "TEAMON_Index_Tip",
    "TEAMON_Wrist_Cuff",
}
objects = list(bpy.context.scene.objects)
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
names = {obj.name for obj in objects}

topology = []
triangle_count = 0
for obj in mesh_objects:
    obj.data.calc_loop_triangles()
    triangle_count += len(obj.data.loop_triangles)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    topology.append({
        "name": obj.name,
        "vertices": len(bm.verts),
        "faces": len(bm.faces),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
        "loose_vertices": sum(1 for vertex in bm.verts if not vertex.link_edges),
        "degenerate_faces": sum(1 for face in bm.faces if face.calc_area() <= 1e-10),
        "negative_scale": any(value < 0 for value in obj.scale),
        "non_uniform_scale": max(obj.scale) - min(obj.scale) > 1e-5,
    })
    bm.free()

contacts = [
    ("TEAMON_Index_Tip", "TEAMON_Keycap", 0.035),
    ("TEAMON_Index_Distal", "TEAMON_Index_Joint_01", 0.06),
    ("TEAMON_Index_Middle", "TEAMON_Index_Joint_02", 0.06),
    ("TEAMON_Index_Proximal", "TEAMON_Palm_Shell", 0.14),
    ("TEAMON_Middle_Proximal", "TEAMON_Palm_Shell", 0.14),
    ("TEAMON_Ring_Proximal", "TEAMON_Palm_Shell", 0.14),
    ("TEAMON_Pinky_Proximal", "TEAMON_Palm_Shell", 0.14),
    ("TEAMON_Thumb_Proximal", "TEAMON_Palm_Shell", 0.14),
    ("TEAMON_Palm_Shell", "TEAMON_Wrist_Joint", 0.14),
    ("TEAMON_Wrist_Joint", "TEAMON_Wrist_Cuff", 0.14),
]
contact_results = []
for name_a, name_b, tolerance in contacts:
    gap = aabb_gap(name_a, name_b)
    contact_results.append({
        "a": name_a,
        "b": name_b,
        "gap": round(gap, 5) if gap is not None else None,
        "tolerance": tolerance,
        "pass": gap is not None and gap <= tolerance,
    })

errors = []
missing = sorted(required - names)
if missing:
    errors.append("Missing required nodes")
if triangle_count > 100000:
    errors.append("Desktop triangle budget exceeded")
if any(not result["pass"] for result in contact_results):
    errors.append("One or more expected contacts failed")
if any(item["negative_scale"] for item in topology):
    errors.append("Negative scale found")
if any(item["loose_vertices"] or item["degenerate_faces"] for item in topology):
    errors.append("Loose vertices or degenerate faces found")

payload = {
    "asset": "TEAMON robot hand button v2",
    "glb": str(GLB_PATH),
    "file_size_bytes": GLB_PATH.stat().st_size,
    "object_count": len(objects),
    "mesh_count": len(mesh_objects),
    "triangle_count": triangle_count,
    "desktop_budget": 100000,
    "mobile_budget": 30000,
    "within_desktop_budget": triangle_count <= 100000,
    "within_mobile_budget": triangle_count <= 30000,
    "missing_required_nodes": missing,
    "contacts": contact_results,
    "topology": topology,
    "validation_errors": errors,
}
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("TEAMON_HAND_V2_GLB_VALIDATION=" + json.dumps(payload, ensure_ascii=False))
