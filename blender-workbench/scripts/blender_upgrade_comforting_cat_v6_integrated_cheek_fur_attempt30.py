"""Replace separate cheek fins with connected deformation of the head mesh."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_integrated_cheek_fur_attempt30"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_cheek_tuft_embed_attempt29.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_integrated_cheek_fur_attempt30.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def gaussian(value: float, center: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - center) / sigma) ** 2)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
before = {"head": bounds(head)}
preserved_sources = [
    preserve_copy(
        head,
        "Comforting_Cat_V6",
        "A30",
        "smooth_cheek_without_connected_fur_mass",
    )
]

removed_tufts: list[str] = []
for side in ("L", "R"):
    for index in (0, 1):
        name = f"V6_CheekTuft_{side}_{index}"
        tuft = bpy.data.objects.get(name)
        if tuft is not None:
            tuft.parent = None
            tuft.hide_render = True
            tuft.hide_set(True)
            tuft.name = f"{name}_REJECTED_A30"
            tuft["comforting_cat_preserved_source"] = True
            tuft["comforting_cat_rejection_reason"] = "separate_fin_in_front_view"
            removed_tufts.append(tuft.name)

inverse = head.matrix_world.inverted()
max_displacement = 0.0
changed_vertices = 0
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    absolute_x = abs(world.x)
    if absolute_x < 0.40:
        continue
    side_weight = smoothstep(0.40, 0.60, absolute_x)
    front_side_weight = gaussian(world.y, -0.06, 0.30)
    upper = 0.060 * gaussian(world.z, 2.73, 0.075)
    lower = 0.085 * gaussian(world.z, 2.57, 0.070)
    displacement = (upper + lower) * side_weight * front_side_weight
    if displacement < 0.0005:
        continue
    world.x += math.copysign(displacement, world.x)
    vertex.co = inverse @ world
    max_displacement = max(max_displacement, displacement)
    changed_vertices += 1
head.data.update()

bpy.context.view_layer.update()
after = {"head": bounds(head)}
metrics = {
    "changed_vertices": changed_vertices,
    "max_displacement": round(max_displacement, 6),
    "head_width_before": before["head"]["dimensions"][0],
    "head_width_after": after["head"]["dimensions"][0],
    "removed_separate_tufts": removed_tufts,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_IntegratedCheekFur_A30"
scene["comforting_cat_v6_stage"] = "INTEGRATED_CHEEK_FUR"
scene["comforting_cat_v6_attempt"] = 30
scene["comforting_cat_v6_dominant_defect"] = "separate_cheek_fin_geometry"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "INTEGRATED_CHEEK_FUR",
    "attempt": 30,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "separate_cheek_fin_geometry",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
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
