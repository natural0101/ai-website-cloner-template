"""Replace the rigid shield-like scarf front with compact overlapping cloth folds."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_scarf_cloth_fold_attempt38"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_head_crown_muzzle_camera_attempt37.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_cloth_fold_attempt38.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
root = bpy.data.objects["CatV6_Root"]

before = {obj.name: bounds(obj) for obj in (upper, lower, drape)}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A38", "rigid_scarf_source")
    for obj in (upper, lower, drape)
]

# Keep the upper wrap as the main soft collar, but introduce a gentle diagonal
# overlap so it does not read as a perfectly inflated torus.
inverse = upper.matrix_world.inverted()
for vertex in upper.data.vertices:
    world = upper.matrix_world @ vertex.co
    front = clamp((-world.y + 0.03) / 0.43, 0.0, 1.0)
    side = world.x / 0.66
    world.z += front * (-0.035 * side + 0.012 * math.sin(side * math.pi))
    world.y += front * 0.018 * math.cos(side * math.pi)
    vertex.co = inverse @ world
upper.data.update()

# Recess and flatten the secondary wrap. It should support the collar, not
# appear as a second identical inflatable ring.
inverse = lower.matrix_world.inverted()
for vertex in lower.data.vertices:
    world = lower.matrix_world @ vertex.co
    world.x *= 0.91
    world.y = 0.075 + (world.y - 0.09) * 0.82
    world.z = 2.155 + (world.z - 2.184) * 0.74
    front = clamp((-world.y + 0.04) / 0.30, 0.0, 1.0)
    world.z += front * 0.022 * math.sin((world.x / 0.55 + 0.25) * math.pi)
    vertex.co = inverse @ world
lower.data.update()

# The old drape was a broad, nearly rigid triangular shield. Preserve its
# topology but turn it into one compact diagonal fold tucked under the collar.
inverse = drape.matrix_world.inverted()
for vertex in drape.data.vertices:
    world = drape.matrix_world @ vertex.co
    world.x = -0.06 + world.x * (0.82 / 1.288033843)
    world.y = -0.505 + (world.y + 0.454666331) * 0.58
    world.z = 2.145 + (world.z - 2.13608861) * (0.29 / 0.469727039)
    normalized_x = clamp((world.x + 0.47) / 0.82, 0.0, 1.0)
    world.z += 0.055 * (normalized_x - 0.5)
    world.y += 0.025 * math.sin(normalized_x * math.pi)
    vertex.co = inverse @ world
drape.data.update()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in (upper, lower, drape)}
metrics = {
    "front_drape_width_ratio": round(
        after[drape.name]["dimensions"][0] / before[drape.name]["dimensions"][0], 5
    ),
    "front_drape_height_ratio": round(
        after[drape.name]["dimensions"][2] / before[drape.name]["dimensions"][2], 5
    ),
    "lower_over_upper_height": round(
        after[lower.name]["dimensions"][2] / after[upper.name]["dimensions"][2], 5
    ),
    "scarf_visible_layers": 3,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfClothFold_A38"
scene["comforting_cat_v6_stage"] = "SCARF_CLOTH_FOLD"
scene["comforting_cat_v6_attempt"] = 38
scene["comforting_cat_v6_dominant_defect"] = "rigid_triangular_scarf_shield"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_CLOTH_FOLD",
    "attempt": 38,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_triangular_scarf_shield",
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
