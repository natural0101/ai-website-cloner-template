"""Add connected cheek-fur serration to the existing manifold head."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_integrated_cheek_serration_attempt32"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_scarf_dedonut_attempt31.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_integrated_cheek_serration_attempt32.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def gaussian(value: float, center: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - center) / sigma) ** 2)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
before = {"head": bounds(head)}
preserved_source = preserve_copy(
    head,
    "Comforting_Cat_V6",
    "A32",
    "continuous_balloon_smooth_cheek_contour",
)

tips = [
    (0.030, 2.550, 0.024),
    (0.040, 2.640, 0.026),
    (0.034, 2.740, 0.027),
    (0.024, 2.840, 0.030),
]
valleys = [
    (-0.018, 2.595, 0.018),
    (-0.018, 2.690, 0.018),
    (-0.014, 2.790, 0.020),
]
inverse = head.matrix_world.inverted()
changed_vertices = 0
max_displacement = 0.0
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    absolute_x = abs(world.x)
    if absolute_x < 0.43 or not 2.48 <= world.z <= 2.92:
        continue
    side_weight = smoothstep(0.43, 0.60, absolute_x)
    front_weight = 1.0 - smoothstep(0.06, 0.32, world.y)
    profile = -0.006
    for amplitude, center, sigma in tips + valleys:
        profile += amplitude * gaussian(world.z, center, sigma)
    profile = clamp(profile, -0.022, 0.038)
    displacement = side_weight * front_weight * profile
    if abs(displacement) < 0.0001:
        continue
    world.x += math.copysign(displacement, world.x)
    vertex.co = inverse @ world
    changed_vertices += 1
    max_displacement = max(max_displacement, abs(displacement))
head.data.update()

bpy.context.view_layer.update()
after = {"head": bounds(head)}
metrics = {
    "changed_vertices": changed_vertices,
    "max_displacement": round(max_displacement, 6),
    "head_width_before": before["head"]["dimensions"][0],
    "head_width_after": after["head"]["dimensions"][0],
    "visible_object_delta": 0,
    "head_vertex_count": len(head.data.vertices),
    "head_face_count": len(head.data.polygons),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_IntegratedCheekSerration_A32"
scene["comforting_cat_v6_stage"] = "INTEGRATED_CHEEK_SERRATION"
scene["comforting_cat_v6_attempt"] = 32
scene["comforting_cat_v6_dominant_defect"] = "balloon_smooth_head_contour"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "INTEGRATED_CHEEK_SERRATION",
    "attempt": 32,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "balloon_smooth_head_contour",
    "preserved_source": preserved_source,
    "profile_tips": tips,
    "profile_valleys": valleys,
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
