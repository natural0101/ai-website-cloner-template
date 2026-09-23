"""TRUE_360 large-mass pass: correct the oversized pancake-like v4 head group."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_head_proportion_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v4_arm_geometry_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_head_proportion_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def world_bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    corners: list[Vector] = []
    for obj in objects:
        if obj.type not in {"MESH", "CURVE"}:
            continue
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6)
            for index in range(3)
        ],
    }


head_root = bpy.data.objects["Cat_Head"]
head_objects = descendants(head_root)
before_bounds = world_bounds(head_objects)
before_scale = [round(float(value), 6) for value in head_root.scale]
head_root.scale = (0.82, 0.88, 0.90)
bpy.context.view_layer.update()
after_bounds = world_bounds(head_objects)
after_scale = [round(float(value), 6) for value in head_root.scale]

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_HeadProportion"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "LARGE_MASS_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "head_proportion_1"
scene["comforting_cat_v5_dominant_defect"] = "oversized_wide_deep_head_group"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "body and legs",
        "robe and scarf geometry",
        "arms",
        "satchel and strap",
        "tail",
        "materials",
        "lighting",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    scene["comforting_cat_v5_stage"] = "SILHOUETTE_REVIEW"
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_render = False
    obj.hide_viewport = False
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

triangle_count = 0
for obj in export_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangle_count += sum(max(0, len(face.vertices) - 2) for face in mesh.polygons)
    evaluated.to_mesh_clear()

scene_graph = {
    "schema_version": "1.0",
    "goal": "Bring the head-to-garment silhouette ratio closer to the supplied cat turnaround without changing facial feature design yet.",
    "mode": "TRUE_360",
    "units": "METERS",
    "parts": [
        {
            "id": "Cat_Head",
            "name": "Cat_Head semantic group",
            "representation": "HIERARCHICAL_TRUE_3D",
            "dimensions_before": before_bounds["dimensions"],
            "dimensions_after": after_bounds["dimensions"],
            "source_confidence": 0.86,
            "notes": "All head children scale together around the existing scarf-contact pivot.",
        }
    ],
    "relations": [
        {
            "a": "Cat_Head_Mesh",
            "type": "OVERLAPS",
            "b": "Cat_Body",
            "minimum_overlap": 0.005,
            "tolerance": 0.004,
        },
        {
            "a": "Cat_ScarfWrap",
            "type": "OVERLAPS",
            "b": "Cat_Head_Mesh",
            "minimum_overlap": 0.005,
            "tolerance": 0.004,
        },
    ],
    "camera": {
        "type": "ORTHOGRAPHIC",
        "review_views": ["front", "front_3q", "side", "back"],
    },
    "acceptance": {
        "dominant_defect": "oversized_wide_deep_head_group",
        "requirements": [
            "head no longer dominates the garment width",
            "front head reads less like a broad pancake",
            "side depth is reduced without flattening into a relief",
            "head remains attached at the scarf/body junction",
        ],
        "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    },
}
(REPORT_DIR / f"{ASSET}_scene_graph.json").write_text(
    json.dumps(scene_graph, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
report = {
    "asset": ASSET,
    "stage": "LARGE_MASS_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "oversized_wide_deep_head_group",
    "head_group": {
        "scale_before": before_scale,
        "scale_after": after_scale,
        "bounds_before": before_bounds,
        "bounds_after": after_bounds,
    },
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "triangles": triangle_count,
    "exportable_objects": len(export_objects),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    },
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_HEAD_PROPORTION=" + json.dumps(report, ensure_ascii=False))
