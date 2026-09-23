"""Settle the intact upper character stack by 0.070 BU without scaling any geometry."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_upper_stack_settle_attempt73"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_eye_stack_integration_attempt72.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_upper_stack_settle_attempt73.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
finalize_pass = utils["finalize_pass"]


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def object_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
    return digest.hexdigest()


def z_overlap(a: bpy.types.Object, b: bpy.types.Object) -> float:
    first = bounds(a)
    second = bounds(b)
    return max(0.0, min(first["max"][2], second["max"][2]) - max(first["min"][2], second["min"][2]))


root = bpy.data.objects["CatV6_Root"]
canonical = descendants(root)
exact_names = {
    "V6_Head",
    "V6_Ear_L",
    "V6_Ear_R",
    "V6_InnerEar_L",
    "V6_InnerEar_R",
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Eyebrow_L",
    "V6_Eyebrow_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
    "V6_Nose",
    "V6_Mouth",
    "V6_Philtrum",
    "V6_ScarfWrap_Upper",
    "V6_ScarfWrap_Lower",
    "V6_Scarf_FrontDrape",
    "V6_Scarf_BackDrape",
    "V6_Scarf_FrontFold_Upper",
    "V6_Robe",
    "V6_FrontTunic",
    "V6_ArmUnified_L",
    "V6_ArmUnified_R",
    "V6_Satchel",
    "V6_SatchelFlap",
    "V6_SatchelHeart",
    "V6_SatchelStrap",
}
prefixes = ("V6_Whisker_", "V6_SatchelTassel_", "V6_SatchelTasselCord_")
selected = [
    obj
    for obj in canonical
    if obj.name in exact_names or any(obj.name.startswith(prefix) for prefix in prefixes)
]
selected_names = sorted(obj.name for obj in selected)
missing = sorted(name for name in exact_names if bpy.data.objects.get(name) is None)
if missing:
    raise RuntimeError(f"Missing required upper-stack objects: {missing}")
if len(selected) < len(exact_names) + 8:
    raise RuntimeError(f"Upper-stack selection unexpectedly small: {len(selected)}")

locked = [obj for obj in canonical if obj not in selected]
locked_hash_before = object_hash(locked)
before = {obj.name: bounds(obj) for obj in selected}
world_matrices_before = {obj.name: obj.matrix_world.copy() for obj in selected}
dimension_before = {obj.name: tuple(bounds(obj)["dimensions"]) for obj in selected if obj.type == "MESH"}

feet = [bpy.data.objects["V6_Foot_L"], bpy.data.objects["V6_Foot_R"]]
legs = [bpy.data.objects["V6_Leg_L"], bpy.data.objects["V6_Leg_R"]]
robe = bpy.data.objects["V6_Robe"]
tail = bpy.data.objects["V6_TailBase"]
head = bpy.data.objects["V6_Head"]
scarf = bpy.data.objects["V6_ScarfWrap_Upper"]
contacts_before = {
    "robe_leg_min_overlap": min(z_overlap(robe, leg) for leg in legs),
    "robe_tail_overlap": z_overlap(robe, tail),
    "head_scarf_overlap": z_overlap(head, scarf),
    "paw_min_z": min(bounds(foot)["min"][2] for foot in feet),
}

for obj in selected:
    matrix = world_matrices_before[obj.name].copy()
    matrix.translation.z -= 0.070
    obj.matrix_world = matrix

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in selected}
locked_hash_after = object_hash(locked)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("Upper-stack settle changed locked legs, feet, tail or other geometry/transforms")

max_x_y_shift = 0.0
max_z_error = 0.0
max_dimension_delta = 0.0
for obj in selected:
    old_matrix = world_matrices_before[obj.name]
    new_matrix = obj.matrix_world
    max_x_y_shift = max(
        max_x_y_shift,
        abs(new_matrix.translation.x - old_matrix.translation.x),
        abs(new_matrix.translation.y - old_matrix.translation.y),
    )
    max_z_error = max(max_z_error, abs((new_matrix.translation.z - old_matrix.translation.z) + 0.070))
    if obj.type == "MESH":
        current_dimensions = tuple(bounds(obj)["dimensions"])
        max_dimension_delta = max(
            max_dimension_delta,
            max(abs(a - b) for a, b in zip(dimension_before[obj.name], current_dimensions, strict=True)),
        )

contacts_after = {
    "robe_leg_min_overlap": min(z_overlap(robe, leg) for leg in legs),
    "robe_tail_overlap": z_overlap(robe, tail),
    "head_scarf_overlap": z_overlap(head, scarf),
    "paw_min_z": min(bounds(foot)["min"][2] for foot in feet),
}
relative_head_scarf_delta = abs(
    (after[head.name]["min"][2] - after[scarf.name]["max"][2])
    - (before[head.name]["min"][2] - before[scarf.name]["max"][2])
)
metrics = {
    "selected_count": len(selected),
    "translation_z": -0.070,
    "robe_hem_before": before[robe.name]["min"][2],
    "robe_hem_after": after[robe.name]["min"][2],
    "visible_leg_gap_reduction": round(before[robe.name]["min"][2] - after[robe.name]["min"][2], 6),
    "max_x_y_shift": round(max_x_y_shift, 8),
    "max_z_translation_error": round(max_z_error, 8),
    "max_mesh_dimension_delta": round(max_dimension_delta, 8),
    "relative_head_scarf_delta": round(relative_head_scarf_delta, 8),
    "contacts_before": {key: round(value, 6) for key, value in contacts_before.items()},
    "contacts_after": {key: round(value, 6) for key, value in contacts_after.items()},
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A73_PRE_GATE_METRICS=" + repr(metrics))
if max_x_y_shift > 0.00001 or max_z_error > 0.00001:
    raise RuntimeError("Upper stack did not receive one exact rigid Z translation")
if max_dimension_delta > 0.00001:
    raise RuntimeError("Upper-stack mesh dimensions changed")
if contacts_after["robe_leg_min_overlap"] < 0.12:
    raise RuntimeError("Robe/leg overlap below contact gate")
if contacts_after["robe_tail_overlap"] < 0.20:
    raise RuntimeError("Robe/tail overlap below contact gate")
if abs(contacts_after["paw_min_z"] - contacts_before["paw_min_z"]) > 0.00001:
    raise RuntimeError("Grounded paws moved")
if relative_head_scarf_delta > 0.00001:
    raise RuntimeError("Head/scarf relative placement changed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_UpperStackSettle_A73"
scene["comforting_cat_v6_stage"] = "UPPER_STACK_SETTLE"
scene["comforting_cat_v6_attempt"] = 73
scene["comforting_cat_v6_dominant_defect"] = "exposed_leg_and_head_body_stack_too_tall"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "UPPER_STACK_SETTLE",
    "attempt": 73,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "exposed_leg_and_head_body_stack_too_tall",
    "selected_objects": selected_names,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["rigid world Z translation for upper stack only"],
        "preserved": ["all mesh dimensions", "all X/Y", "legs", "feet", "toe curves", "tail", "floor", "camera", "lights", "materials"],
    },
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
