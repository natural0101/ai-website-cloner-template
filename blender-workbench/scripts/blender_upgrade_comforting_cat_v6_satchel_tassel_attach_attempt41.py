"""Attach the two floating pale satchel tassels to the bag bottom."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_satchel_tassel_attach_attempt41"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_garment_stack_attempt40.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_satchel_tassel_attach_attempt41.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def transform_world(
    obj: bpy.types.Object,
    center: Vector,
    new_center: Vector,
    scale: float,
) -> None:
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        vertex.co = inverse @ (new_center + (world - center) * scale)
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
bag = bpy.data.objects["V6_Satchel"]
tassels = [
    bpy.data.objects["V6_SatchelTassel_0"],
    bpy.data.objects["V6_SatchelTassel_1"],
]
before = {"bag": bounds(bag), **{obj.name: bounds(obj) for obj in tassels}}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A41", "floating_pale_tassel")
    for obj in tassels
]

bag_material = bag.data.materials[0] if bag.data.materials else None
target_centers = [
    Vector((0.245, -0.681, 0.715)),
    Vector((0.475, -0.681, 0.715)),
]
for tassel, target_center in zip(tassels, target_centers, strict=True):
    current = bounds(tassel)
    center = Vector(
        (
            (current["min"][0] + current["max"][0]) * 0.5,
            (current["min"][1] + current["max"][1]) * 0.5,
            (current["min"][2] + current["max"][2]) * 0.5,
        )
    )
    transform_world(tassel, center, target_center, 0.72)
    if bag_material is not None:
        tassel.data.materials.clear()
        tassel.data.materials.append(bag_material)

bpy.context.view_layer.update()
after = {"bag": bounds(bag), **{obj.name: bounds(obj) for obj in tassels}}
metrics = {
    "left_contact_overlap_z": round(
        after["V6_SatchelTassel_0"]["max"][2] - after["bag"]["min"][2], 5
    ),
    "right_contact_overlap_z": round(
        after["V6_SatchelTassel_1"]["max"][2] - after["bag"]["min"][2], 5
    ),
    "tassel_scale": 0.72,
    "material_matches_bag": bag_material is not None,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_SatchelTasselAttach_A41"
scene["comforting_cat_v6_stage"] = "SATCHEL_TASSEL_ATTACH"
scene["comforting_cat_v6_attempt"] = 41
scene["comforting_cat_v6_dominant_defect"] = "floating_white_ovals_below_bag"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SATCHEL_TASSEL_ATTACH",
    "attempt": 41,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "floating_white_ovals_below_bag",
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
