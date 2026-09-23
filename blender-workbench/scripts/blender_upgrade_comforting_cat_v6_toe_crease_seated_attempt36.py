"""Seat toe crease curves into paw surfaces without changing paw geometry."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_toe_crease_seated_attempt36"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_satchel_tall_soft_attempt35.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_toe_crease_seated_attempt36.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]

root = bpy.data.objects["CatV6_Root"]
toe_names = [
    f"V6_ToeCrease_{side}_{index}"
    for side in ("L", "R")
    for index in (0, 1)
]
before = {name: bounds(bpy.data.objects[name]) for name in toe_names}
preserved_sources = [
    preserve_copy(
        bpy.data.objects[name],
        "Comforting_Cat_V6",
        "A36",
        "toe_curve_hook_outside_paw_surface",
    )
    for name in toe_names
]

for name in toe_names:
    curve = bpy.data.objects[name].data
    curve.bevel_depth = 0.004
    points = curve.splines[0].bezier_points
    for point, y_value in zip(points, (-0.250, -0.257, -0.250)):
        point.co.y = y_value
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in toe_names}
scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ToeCreaseSeated_A36"
scene["comforting_cat_v6_stage"] = "TOE_CREASE_SEATED"
scene["comforting_cat_v6_attempt"] = 36
scene["comforting_cat_v6_dominant_defect"] = "toe_curve_side_hooks"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TOE_CREASE_SEATED",
    "attempt": 36,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "toe_curve_side_hooks",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "bevel_depth": 0.004,
    "curve_y": [-0.250, -0.257, -0.250],
}
finalize_pass(
    asset=ASSET,
    root=root,
    scene=scene,
    final_blend=FINAL_BLEND,
    glb_path=GLB_PATH,
    render_dir=RENDER_DIR,
    report_dir=REPORT_DIR,
    scene_qa_path=SCENE_QA_PATH,
    report=report,
)
