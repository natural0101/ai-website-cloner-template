from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


PROJECT_ROOT = Path(
    os.environ.get(
        "TEAMON_PROJECT_ROOT",
        r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template",
    )
)
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v39_ada_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v39_ada_hand.glb"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v39-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v39-pressed.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v39_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v39_structural_qa.json"


def bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


scene = bpy.context.scene
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
hand_group = bpy.data.objects["TEAMON_Ada_HandRoot"]
keycap = bpy.data.objects["TEAMON_Keycap"]
index_mesh = bpy.data.objects["TEAMON_Ada_Index"]
hand_group.name = "TEAMON_HandPressGroup"

for obj in (button_group, hand_group):
    obj.animation_data_clear()

rest_button = button_group.location.copy()
rest_hand = hand_group.location.copy()
press_travel = 0.085
scene.frame_start = 1
scene.frame_end = 24
scene.render.fps = 30

scene.frame_set(1)
button_group.location = rest_button
hand_group.location = rest_hand
button_group.keyframe_insert(data_path="location", frame=1)
hand_group.keyframe_insert(data_path="location", frame=1)

scene.frame_set(24)
button_group.location = rest_button + Vector((0.0, 0.0, -press_travel))
hand_group.location = rest_hand + Vector((0.0, 0.0, -press_travel))
button_group.keyframe_insert(data_path="location", frame=24)
hand_group.keyframe_insert(data_path="location", frame=24)

button_group.animation_data.action.name = "TEAMON_PressGroup"
hand_group.animation_data.action.name = "TEAMON_HandPressGroup"

scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

scene.frame_set(1)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)
rest_gap = bounds(index_mesh)[0].z - bounds(keycap)[1].z

scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_gap = bounds(index_mesh)[0].z - bounds(keycap)[1].z

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = [composition_root, *composition_root.children_recursive]
export_objects = [
    obj
    for obj in export_objects
    if obj.type not in {"CAMERA", "LIGHT"}
    and obj.name != "TEAMON_Studio_Floor"
    and not obj.hide_render
]
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)

export_meshes = [obj for obj in export_objects if obj.type == "MESH"]
repaired_degenerate_faces = 0
repaired_loose_vertices = 0
for obj in export_meshes:
    if not obj.name.startswith("TEAMON_Ada_"):
        continue
    obj.data = obj.data.copy()
    editable = bmesh.new()
    editable.from_mesh(obj.data)
    degenerate_faces = [face for face in editable.faces if face.calc_area() <= 1e-12]
    if degenerate_faces:
        repaired_degenerate_faces += len(degenerate_faces)
        bmesh.ops.delete(editable, geom=degenerate_faces, context="FACES")
    loose_vertices = [vertex for vertex in editable.verts if not vertex.link_edges and not vertex.link_faces]
    if loose_vertices:
        repaired_loose_vertices += len(loose_vertices)
        bmesh.ops.delete(editable, geom=loose_vertices, context="VERTS")
    bmesh.ops.recalc_face_normals(editable, faces=list(editable.faces))
    editable.to_mesh(obj.data)
    editable.free()
    obj.data.update()

triangles = triangle_count(export_meshes)
if triangles > 150000:
    raise RuntimeError(f"TEAMON v39 exceeds triangle budget: {triangles}")

qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in export_meshes],
    contact_tolerance=0.02,
    floating_tolerance=0.08,
)
qa["expected_contact"] = {
    "rest_gap": rest_gap,
    "pressed_gap": pressed_gap,
    "tolerance": 0.02,
    "rest_pass": abs(rest_gap) <= 0.02,
    "pressed_pass": abs(pressed_gap) <= 0.02,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if qa["errors"]:
    raise RuntimeError(f"TEAMON v39 structural QA errors: {qa['errors']}")
if not qa["expected_contact"]["rest_pass"] or not qa["expected_contact"]["pressed_pass"]:
    raise RuntimeError(f"TEAMON v39 contact failed: {qa['expected_contact']}")

bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=False,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
    export_extras=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_frame_range=True,
    export_force_sampling=True,
)

report = {
    "asset": "TEAMON v39 with OpenBionics Ada v1.1 hand",
    "source_license": "CC BY-SA 4.0",
    "source_revision": "2dbf3cc6c5df112066f12c11af1d001e319a766f",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "animation_clips": ["TEAMON_PressGroup", "TEAMON_HandPressGroup"],
    "press_travel": press_travel,
    "triangle_count": triangles,
    "rest_contact_gap": rest_gap,
    "pressed_contact_gap": pressed_gap,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "repaired_degenerate_faces": repaired_degenerate_faces,
    "repaired_loose_vertices": repaired_loose_vertices,
    "status": "glb_requires_browser_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
