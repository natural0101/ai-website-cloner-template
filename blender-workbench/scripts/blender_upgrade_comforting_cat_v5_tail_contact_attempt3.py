"""Corrective weighted tail contact that preserves the body attachment."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_tail_proportion_attempt3"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_tail_proportion_attempt2.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_tail_proportion_attempt3.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


tail = bpy.data.objects["Cat_Tail_Base"]
tip = bpy.data.objects["Cat_Tail_CreamTip"]

# Undo the rejected rigid drop.
tail_matrix = tail.matrix_world.copy()
tail_matrix.translation.z += 0.080
tail.matrix_world = tail_matrix
tip_matrix = tip.matrix_world.copy()
tip_matrix.translation.z += 0.080
tip.matrix_world = tip_matrix

# Keep the root fixed and lower only the distal arc.
anchor_x = 0.43
max_x = max(float(vertex.co.x) for vertex in tail.data.vertices)
for vertex in tail.data.vertices:
    weight = max(
        0.0,
        min(1.0, (float(vertex.co.x) - anchor_x) / max(max_x - anchor_x, 1e-6)),
    )
    vertex.co.z -= 0.085 * weight
tail.data.update()
tip_matrix = tip.matrix_world.copy()
tip_matrix.translation.z -= 0.080
tip.matrix_world = tip_matrix
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_TailProportion_A3"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "SILHOUETTE_TAIL_CONTACT"
scene["comforting_cat_v5_geometry_attempt"] = "tail_proportion_3"
scene["comforting_cat_v5_dominant_defect"] = "tail_contact_without_root_gap"
scene["comforting_cat_v5_rejected_attempt"] = "attempt2_rigid_drop_detached_root"


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
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
report = {
    "asset": ASSET,
    "attempt": 3,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "tail_contact_without_root_gap",
    "rejected_attempt": "attempt2_rigid_drop_detached_root",
    "weighted_drop": 0.085,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": structural_qa["errors"],
        "warnings": structural_qa["warnings"],
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_TAIL_CONTACT_A3=" + json.dumps(report, ensure_ascii=False))
