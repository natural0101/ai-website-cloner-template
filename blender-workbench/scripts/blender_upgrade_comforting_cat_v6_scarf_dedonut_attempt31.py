"""Turn duplicate scarf toruses into one dominant fold plus recessed support."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_dedonut_attempt31"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_integrated_cheek_fur_attempt30.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_dedonut_attempt31.blend"
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


root = bpy.data.objects["CatV6_Root"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
before = {
    "upper": bounds(upper),
    "lower": bounds(lower),
    "drape": bounds(drape),
}
preserved_sources = [
    preserve_copy(
        obj,
        "Comforting_Cat_V6",
        "A31",
        "duplicated_inflatable_scarf_ring",
    )
    for obj in (upper, lower)
]

upper_inverse = upper.matrix_world.inverted()
for vertex in upper.data.vertices:
    world = upper.matrix_world @ vertex.co
    world.x *= 0.66 / 0.678
    world.y = -0.02 + world.y * (0.76 / 0.88)
    world.z = 2.345 + (world.z - 2.36) * (0.31 / 0.3198)
    front_weight = clamp((-world.y) / 0.40, 0.0, 1.0)
    world.z += -0.04 * (world.x / 0.66) * front_weight
    vertex.co = upper_inverse @ world
upper.data.update()

lower_inverse = lower.matrix_world.inverted()
for vertex in lower.data.vertices:
    world = lower.matrix_world @ vertex.co
    world.x *= 0.900
    world.y = world.y * 0.783 + 0.040
    world.z = 2.175 + (world.z - 2.18) * (0.19 / 0.31512)
    x_weight = 1.0 - smoothstep(0.35, 0.59, abs(world.x))
    front_weight = clamp((-world.y) / 0.32, 0.0, 1.0)
    inset_weight = x_weight * front_weight
    world.y += 0.10 * inset_weight
    world.z += 0.03 * inset_weight
    vertex.co = lower_inverse @ world
lower.data.update()

bpy.context.view_layer.update()
after = {
    "upper": bounds(upper),
    "lower": bounds(lower),
    "drape": bounds(drape),
}
metrics = {
    "lower_over_upper_width": round(
        after["lower"]["dimensions"][0] / after["upper"]["dimensions"][0], 5
    ),
    "lower_over_upper_height": round(
        after["lower"]["dimensions"][2] / after["upper"]["dimensions"][2], 5
    ),
    "lower_over_upper_depth": round(
        after["lower"]["dimensions"][1] / after["upper"]["dimensions"][1], 5
    ),
    "lower_over_drape_width": round(
        after["lower"]["dimensions"][0] / after["drape"]["dimensions"][0], 5
    ),
    "upper_front_rim_delta_z": 0.08,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfDedonut_A31"
scene["comforting_cat_v6_stage"] = "SCARF_DEDONUT"
scene["comforting_cat_v6_attempt"] = 31
scene["comforting_cat_v6_dominant_defect"] = "duplicated_inflatable_scarf_rings"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_DEDONUT",
    "attempt": 31,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "duplicated_inflatable_scarf_rings",
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
