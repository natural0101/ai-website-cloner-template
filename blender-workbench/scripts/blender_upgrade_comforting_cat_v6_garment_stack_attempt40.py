"""Make the long rigid body read as a compact stack of layered cloth."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_garment_stack_attempt40"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_fluffy_side_mass_attempt39.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_garment_stack_attempt40.blend"
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
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
left_arm = bpy.data.objects["V6_ArmUnified_L"]
right_arm = bpy.data.objects["V6_ArmUnified_R"]
objects = (robe, tunic, upper, left_arm, right_arm)
before = {obj.name: bounds(obj) for obj in objects}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A40", "long_rigid_garment_stack")
    for obj in objects
]

# Broaden the robe primarily through the torso rings. Keep the neck and hem
# nearly fixed so the result reads as cloth volume, not a globally scaled tube.
inverse = robe.matrix_world.inverted()
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    lower = smoothstep(0.70, 1.03, world.z)
    upper_falloff = 1.0 - smoothstep(2.02, 2.25, world.z)
    torso_weight = lower * upper_falloff
    asymmetry = 1.0 + 0.008 * math.sin((world.z - 0.66) * 5.0)
    world.x *= 1.0 + 0.065 * torso_weight * asymmetry
    vertex.co = inverse @ world
robe.data.update()

# Raise the pale tunic hem while keeping its upper attachment. A small
# center dip and unequal side heights prevent the panel from reading as a box.
tunic_top = before[tunic.name]["max"][2]
tunic_bottom = before[tunic.name]["min"][2]
target_bottom = 0.815
height_scale = (tunic_top - target_bottom) / (tunic_top - tunic_bottom)
inverse = tunic.matrix_world.inverted()
for vertex in tunic.data.vertices:
    world = tunic.matrix_world @ vertex.co
    bottom_weight = 1.0 - smoothstep(target_bottom + 0.06, 1.18, world.z)
    world.z = tunic_top - (tunic_top - world.z) * height_scale
    center_dip = 0.022 * (1.0 - clamp(abs(world.x) / 0.36, 0.0, 1.0))
    side_bias = 0.010 * (world.x / 0.36)
    world.z -= bottom_weight * (center_dip + side_bias)
    vertex.co = inverse @ world
tunic.data.update()

# Flatten only the main scarf roll. Attempt38 already converted the shield to
# a compact overlap; this removes the remaining inflated collar impression.
upper_center_z = (
    before[upper.name]["min"][2] + before[upper.name]["max"][2]
) * 0.5
inverse = upper.matrix_world.inverted()
for vertex in upper.data.vertices:
    world = upper.matrix_world @ vertex.co
    world.z = upper_center_z + (world.z - upper_center_z) * 0.82
    vertex.co = inverse @ world
upper.data.update()

# Preserve arm dimensions and only keep their contact with the broader robe.
for arm, shift in ((left_arm, -0.03), (right_arm, 0.03)):
    inverse = arm.matrix_world.inverted()
    for vertex in arm.data.vertices:
        world = arm.matrix_world @ vertex.co
        world.x += shift
        vertex.co = inverse @ world
    arm.data.update()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in objects}
metrics = {
    "robe_width_over_height": round(
        after[robe.name]["dimensions"][0] / after[robe.name]["dimensions"][2], 5
    ),
    "tunic_height_over_robe_height": round(
        after[tunic.name]["dimensions"][2] / after[robe.name]["dimensions"][2], 5
    ),
    "visible_blue_hem_height": round(
        after[tunic.name]["min"][2] - after[robe.name]["min"][2], 5
    ),
    "upper_scarf_height": after[upper.name]["dimensions"][2],
    "arm_outward_shift": 0.03,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_GarmentStack_A40"
scene["comforting_cat_v6_stage"] = "GARMENT_STACK"
scene["comforting_cat_v6_attempt"] = 40
scene["comforting_cat_v6_dominant_defect"] = "long_rigid_toy_column_body"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "GARMENT_STACK",
    "attempt": 40,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "long_rigid_toy_column_body",
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
