"""Remediate attempt28 cheek fins by embedding bases inside the head."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_cheek_tuft_embed_attempt29"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_face_readability_tufts_attempt28.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_cheek_tuft_embed_attempt29.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]

root = bpy.data.objects["CatV6_Root"]
tuft_specs = {
    "V6_CheekTuft_L_0": [(-0.480, 2.820), (-0.720, 2.730), (-0.500, 2.660)],
    "V6_CheekTuft_L_1": [(-0.500, 2.680), (-0.760, 2.580), (-0.460, 2.530)],
    "V6_CheekTuft_R_0": [(0.480, 2.820), (0.720, 2.730), (0.500, 2.660)],
    "V6_CheekTuft_R_1": [(0.500, 2.680), (0.760, 2.580), (0.460, 2.530)],
}
before = {name: bounds(bpy.data.objects[name]) for name in tuft_specs}
preserved_sources = [
    preserve_copy(
        bpy.data.objects[name],
        "Comforting_Cat_V6",
        "A29",
        "visible_horizontal_fin_tuft",
    )
    for name in tuft_specs
]

front_y = -0.22
back_y = 0.08
for name, outline in tuft_specs.items():
    obj = bpy.data.objects[name]
    inverse = obj.matrix_world.inverted()
    coordinates = [(x, front_y, z) for x, z in outline]
    coordinates.extend((x, back_y, z) for x, z in outline)
    for vertex, coordinate in zip(obj.data.vertices, coordinates):
        vertex.co = inverse @ Vector(coordinate)
    obj.data.update()
    bevel = obj.modifiers.get(f"{name}_SoftJoin")
    if bevel is not None:
        bevel.width = 0.014
        bevel.segments = 3

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in tuft_specs}
scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_CheekTuftEmbed_A29"
scene["comforting_cat_v6_stage"] = "CHEEK_TUFT_EMBED"
scene["comforting_cat_v6_attempt"] = 29
scene["comforting_cat_v6_dominant_defect"] = "visible_horizontal_fin_tuft"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "CHEEK_TUFT_EMBED",
    "attempt": 29,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "visible_horizontal_fin_tuft",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
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
