"""Geometry-only pass to shorten and soften the accepted v4 cat arms."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v4_arm_geometry_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v4_eye_materials_attempt2.blend").resolve()
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
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v4_before_arm_geometry_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def reshape_arm(obj: bpy.types.Object) -> dict[str, list[float]]:
    """Compress the capsule along its long axis while preserving sleeve contact."""

    before = [round(float(value), 6) for value in obj.dimensions]
    top_center = Vector((0.0, 0.105, 0.33))
    down_axis = Vector((0.0, -0.21, -0.66)).normalized()
    nominal_length = 0.692604
    axial_scale = 0.84
    for vertex in obj.data.vertices:
        delta = vertex.co - top_center
        axial_distance = delta.dot(down_axis)
        radial = delta - down_axis * axial_distance
        progress = max(0.0, min(1.0, axial_distance / nominal_length))
        radial_scale = 1.10 + 0.12 * progress
        vertex.co = (
            top_center
            + down_axis * (axial_distance * axial_scale)
            + radial * radial_scale
        )
    obj.data.update()
    bpy.context.view_layer.update()
    after = [round(float(value), 6) for value in obj.dimensions]
    return {"before": before, "after": after}


arm_changes = {
    name: reshape_arm(bpy.data.objects[name])
    for name in ("Cat_Arm_L", "Cat_Arm_R")
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V4_ArmGeometry"
scene["comforting_cat_v4_stage"] = "GEOMETRY"
scene["comforting_cat_v4_geometry_attempt"] = "arms_1"
scene["comforting_cat_v4_dominant_defect"] = "arms_too_long_and_thin"
scene["comforting_cat_v4_do_not_change"] = json.dumps(
    [
        "head and face",
        "eye geometry and materials",
        "robe and scarf geometry",
        "satchel",
        "tail",
        "lighting",
    ]
)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    scene["comforting_cat_v4_stage"] = "COMPOSITION_REVIEW"
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
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 2.00), 4.85)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.95), 4.85)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.95), 4.85)

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
    "goal": "Shorten and thicken both exposed forearms without changing the accepted face, clothing or materials.",
    "mode": "TRUE_360",
    "units": "METERS",
    "parts": [
        {
            "id": name,
            "name": name,
            "representation": "MESH",
            "dimensions": [
                max(0.0001, round(float(value), 5))
                for value in bpy.data.objects[name].dimensions
            ],
            "material_group": bpy.data.objects[name].data.materials[0].name,
            "source_confidence": 0.78,
            "notes": "Axially compressed capsule with a fuller lower radial profile.",
        }
        for name in ("Cat_Arm_L", "Cat_Arm_R")
    ],
    "relations": [
        {
            "a": "Cat_Arm_L",
            "type": "OVERLAPS",
            "b": "Cat_Sleeve_L",
            "minimum_overlap": 0.01,
            "tolerance": 0.004,
        },
        {
            "a": "Cat_Arm_R",
            "type": "OVERLAPS",
            "b": "Cat_Sleeve_R",
            "minimum_overlap": 0.01,
            "tolerance": 0.004,
        },
    ],
    "camera": {
        "type": "ORTHOGRAPHIC",
        "review_views": ["front", "front_3q", "side", "back"],
    },
    "acceptance": {
        "dominant_defect": "arms_too_long_and_thin",
        "requirements": [
            "both forearms terminate higher than the previous selected version",
            "lower forearms read as soft paws rather than thin tubes",
            "left and right silhouettes remain symmetrical in front view",
            "both arms remain visibly connected to their sleeves",
        ],
        "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
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
    "stage": "GEOMETRY",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "arms_too_long_and_thin",
    "changes": arm_changes,
    "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
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
scene["comforting_cat_v4_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V4_ARM_GEOMETRY=" + json.dumps(report, ensure_ascii=False))
