from __future__ import annotations

import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v43_segmented_rigged.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v43_segmented_hand.glb"
REST_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v43-rest.png"
PRESSED_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v43-pressed.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v43_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v43_structural_qa.json"

for path in (BLEND_PATH, GLB_PATH, REST_PATH, PRESSED_PATH, REPORT_PATH, QA_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def evaluated_vertices_world(obj: bpy.types.Object) -> list[Vector]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def mesh_min_z(objects: list[bpy.types.Object]) -> float:
    return min(point.z for obj in objects for point in evaluated_vertices_world(obj))


def mesh_max_z(objects: list[bpy.types.Object]) -> float:
    return max(point.z for obj in objects for point in evaluated_vertices_world(obj))


def mesh_bvh_world(obj: bpy.types.Object) -> BVHTree:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
        return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()


def exact_mesh_distance(objects: list[bpy.types.Object], target: bpy.types.Object) -> float:
    bvh = mesh_bvh_world(target)
    distance = float("inf")
    for obj in objects:
        for point in evaluated_vertices_world(obj):
            nearest = bvh.find_nearest(point)
            if nearest is not None:
                distance = min(distance, nearest[3])
    return distance


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


def linearize(obj: bpy.types.Object) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    if action is None:
        return
    curves = getattr(action, "fcurves", None)
    if curves is None:
        return
    for curve in curves:
        for point in curve.keyframe_points:
            point.interpolation = "LINEAR"


def is_descendant(obj: bpy.types.Object, ancestor: bpy.types.Object) -> bool:
    current = obj.parent
    while current is not None:
        if current == ancestor:
            return True
        current = current.parent
    return False


scene = bpy.context.scene
composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_root = bpy.data.objects["TEAMON_ButtonRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
hand_group = bpy.data.objects["TEAMON_v41_HandPressGroup"]
keycap = bpy.data.objects["TEAMON_Keycap"]
index_meshes = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH"
    and obj.name.startswith("TEAMON_v41_Index_Shell_")
    and not obj.hide_render
]
if len(index_meshes) != 3:
    raise RuntimeError(f"Expected three v43 index shells, found {len(index_meshes)}")

# The earlier build report used rotated bound-box corners and falsely reported
# contact. Re-seat against evaluated mesh vertices, then verify with world BVH.
key_top = mesh_max_z([keycap])
actual_tip_bottom = mesh_min_z(index_meshes)
hand_group.location.z += (key_top + 0.004) - actual_tip_bottom
bpy.context.view_layer.update()
rest_mesh_distance_before_animation = exact_mesh_distance(index_meshes, keycap)
if rest_mesh_distance_before_animation > 0.006:
    raise RuntimeError(f"TEAMON v43 exact rest contact failed after re-seat: {rest_mesh_distance_before_animation}")

hand_group.name = "TEAMON_HandPressGroup"
hand_group["contact_measurement"] = "evaluated mesh vertices plus world-space BVH"
hand_group["asset_source"] = "reference-driven modular shells informed by Rebelia V2"
hand_group["asset_license"] = "CERN-OHL-S-2.0"

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
if button_action is None or hand_action is None:
    raise RuntimeError("TEAMON v43 animation action creation failed")
button_action.name = "TEAMON_PressGroup"
hand_action.name = "TEAMON_HandPressGroup"
linearize(button_group)
linearize(hand_group)

scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

scene.frame_set(1)
bpy.context.view_layer.update()
rest_distance = exact_mesh_distance(index_meshes, keycap)
scene.render.filepath = str(REST_PATH)
bpy.ops.render.render(write_still=True)

scene.frame_set(24)
bpy.context.view_layer.update()
pressed_distance = exact_mesh_distance(index_meshes, keycap)
scene.render.filepath = str(PRESSED_PATH)
bpy.ops.render.render(write_still=True)

if rest_distance > 0.006 or pressed_distance > 0.006:
    raise RuntimeError(f"TEAMON v43 animated contact failed: rest={rest_distance}, pressed={pressed_distance}")

scene.frame_set(1)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

excluded_prefixes = (
    "TEAMON_Ability_",
    "TEAMON_Ada_",
    "TEAMON_Rebelia_",
    "TEAMON_Shadow",
    "TEAMON_SOURCE_",
)
bpy.ops.object.select_all(action="DESELECT")
export_objects: list[bpy.types.Object] = []
required_empties = {composition_root, button_root, button_group, hand_group}
for obj in bpy.data.objects:
    include_empty = obj in required_empties
    include_mesh = (
        obj.type == "MESH"
        and obj.name.startswith("TEAMON_")
        and not obj.name.startswith(excluded_prefixes)
        and obj.name != "TEAMON_Studio_Floor"
        and not obj.hide_render
        and obj.get("export", True)
        and (obj == composition_root or is_descendant(obj, composition_root))
    )
    if include_empty or include_mesh:
        obj.hide_set(False)
        obj.select_set(True)
        export_objects.append(obj)

export_meshes = [obj for obj in export_objects if obj.type == "MESH"]
triangles = triangle_count(export_meshes)
if triangles > 150000:
    raise RuntimeError(f"TEAMON v43 exceeds 150k triangle budget: {triangles}")

qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in export_meshes],
    contact_tolerance=0.006,
    floating_tolerance=0.035,
)
qa["exact_contact"] = {
    "measurement": "world-space BVH vertex-to-surface nearest distance",
    "tolerance": 0.006,
    "rest_distance": rest_distance,
    "pressed_distance": pressed_distance,
    "rest_pass": rest_distance <= 0.006,
    "pressed_pass": pressed_distance <= 0.006,
}
qa["animation"] = {
    "clips": [button_action.name, hand_action.name],
    "frame_start": scene.frame_start,
    "frame_end": scene.frame_end,
    "fps": scene.render.fps,
    "press_travel": press_travel,
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if qa["errors"]:
    raise RuntimeError(f"TEAMON v43 structural QA errors: {qa['errors']}")

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
    "asset": "TEAMON v43 reference-driven segmented robot hand",
    "stage": "EXPORT_QA",
    "status": "glb_requires_browser_validation",
    "blend": str(BLEND_PATH),
    "glb": str(GLB_PATH),
    "glb_size_bytes": GLB_PATH.stat().st_size,
    "renders": [str(REST_PATH), str(PRESSED_PATH)],
    "animation_clips": [button_action.name, hand_action.name],
    "press_travel": press_travel,
    "triangle_count": triangles,
    "export_mesh_count": len(export_meshes),
    "rest_exact_contact_distance": rest_distance,
    "pressed_exact_contact_distance": pressed_distance,
    "contact_tolerance": 0.006,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "source_license": "CERN-OHL-S-2.0",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
