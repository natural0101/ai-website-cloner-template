from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
OUTPUT_VERSION = os.environ.get("TEAMON_OUTPUT_VERSION", "v19")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / f"teamon_reference_{OUTPUT_VERSION}_ability_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / f"teamon_reference_{OUTPUT_VERSION}_ability_hand.glb"
REST_PATH = PROJECT_ROOT / "public" / "images" / f"teamon-reference-{OUTPUT_VERSION}-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / f"teamon-reference-{OUTPUT_VERSION}-pressed.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_{OUTPUT_VERSION}_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_{OUTPUT_VERSION}_structural_qa.json"

for path in (BLEND_PATH, GLB_PATH, REST_PATH, PRESSED_PATH, REPORT_PATH, QA_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def world_bvh(obj: bpy.types.Object) -> tuple[BVHTree, list[Vector]]:
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
    tree = BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    evaluated.to_mesh_clear()
    return tree, vertices


def surface_gap(objects: list[bpy.types.Object], target: bpy.types.Object) -> float:
    target_tree, target_vertices = world_bvh(target)
    minimum = float("inf")
    for obj in objects:
        tree, vertices = world_bvh(obj)
        for point in vertices:
            nearest = target_tree.find_nearest(point)
            if nearest is not None:
                minimum = min(minimum, float(nearest[3]))
        for point in target_vertices:
            nearest = tree.find_nearest(point)
            if nearest is not None:
                minimum = min(minimum, float(nearest[3]))
    return minimum


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            obj.data.calc_loop_triangles()
            total += len(obj.data.loop_triangles)
    return total


scene = bpy.context.scene
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
hand_group = bpy.data.objects["TEAMON_Ability_ContactPivot"]
hand_group.name = "TEAMON_HandPressGroup"
keycap = bpy.data.objects["TEAMON_Keycap"]
index_objects = [
    bpy.data.objects["TEAMON_Ability_index_L1_index_mesh_1"],
    bpy.data.objects["TEAMON_Ability_index_L2_index_mesh_2"],
]

initial_surface_gap = surface_gap(index_objects, keycap)
target_surface_gap = 0.004
if initial_surface_gap > target_surface_gap:
    hand_group.location.z -= initial_surface_gap - target_surface_gap
    bpy.context.view_layer.update()

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

button_action = button_group.animation_data.action
hand_action = hand_group.animation_data.action
button_action.name = "TEAMON_PressGroup"
hand_action.name = "TEAMON_HandPressGroup"
for action in (button_action, hand_action):
    action["interpolation_intent"] = "smooth press; Blender 5 layered action"

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

scene.frame_set(1)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)
rest_low, rest_high = world_bounds(index_objects)
key_low, key_high = world_bounds([keycap])
rest_aabb_gap = rest_low.z - key_high.z
rest_surface_gap = surface_gap(index_objects, keycap)

scene.frame_set(24)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)
pressed_low, pressed_high = world_bounds(index_objects)
pressed_key_low, pressed_key_high = world_bounds([keycap])
pressed_aabb_gap = pressed_low.z - pressed_key_high.z
pressed_surface_gap = surface_gap(index_objects, keycap)

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

bpy.ops.object.select_all(action="DESELECT")
export_objects = [composition_root, *composition_root.children_recursive]
export_objects = [
    obj for obj in export_objects
    if obj.type not in {"CAMERA", "LIGHT"}
    and obj.name != "TEAMON_Studio_Floor"
    and not obj.hide_render
]
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)

export_meshes = [obj for obj in export_objects if obj.type == "MESH"]
cleaned_meshes = set()
for obj in export_meshes:
    if not obj.name.startswith("TEAMON_Ability_") or obj.data in cleaned_meshes:
        continue
    editable = bmesh.new()
    editable.from_mesh(obj.data)
    bmesh.ops.dissolve_degenerate(editable, dist=1e-7, edges=list(editable.edges))
    editable.to_mesh(obj.data)
    editable.free()
    obj.data.validate(verbose=False, clean_customdata=True)
    obj.data.update()
    cleaned_meshes.add(obj.data)
triangles = triangle_count(export_meshes)
if triangles > 150000:
    raise RuntimeError(f"TEAMON v19 exceeds 150k triangle budget: {triangles}")

qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in export_meshes],
    contact_tolerance=0.015,
    floating_tolerance=0.08,
)
qa["expected_contact"] = {
    "rest_aabb_gap": rest_aabb_gap,
    "pressed_aabb_gap": pressed_aabb_gap,
    "rest_sampled_surface_gap": rest_surface_gap,
    "pressed_sampled_surface_gap": pressed_surface_gap,
    "tolerance": 0.015,
    "rest_pass": rest_surface_gap <= 0.015,
    "pressed_pass": pressed_surface_gap <= 0.015,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if qa["errors"]:
    raise RuntimeError(f"TEAMON v19 structural QA errors: {qa['errors']}")
if not qa["expected_contact"]["rest_pass"] or not qa["expected_contact"]["pressed_pass"]:
    raise RuntimeError(f"TEAMON v19 contact QA failed: {qa['expected_contact']}")

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
    "asset": f"TEAMON {OUTPUT_VERSION} with PSYONIC Ability Hand",
    "stage": "EXPORT_QA",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "press_travel": press_travel,
    "animation_clips": ["TEAMON_PressGroup", "TEAMON_HandPressGroup"],
    "triangle_count": triangles,
    "export_object_count": len(export_objects),
    "export_mesh_count": len(export_meshes),
    "rest_sampled_surface_gap": rest_surface_gap,
    "pressed_sampled_surface_gap": pressed_surface_gap,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "hand_source": "https://github.com/psyonicinc/ability-hand-api",
    "hand_revision": "34c9a9324d3739d976e6de441e56ccefafd0000b",
    "hand_license": "MIT",
    "status": "glb_requires_browser_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
