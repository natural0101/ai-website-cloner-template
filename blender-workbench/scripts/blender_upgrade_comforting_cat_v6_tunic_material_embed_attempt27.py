"""Remediate attempt26: embed tunic edges and replace inherited bright shader."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tunic_material_embed_attempt27"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_front_tunic_layering_attempt26.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tunic_material_embed_attempt27.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]

root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
before = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "material": tunic.data.materials[0].name,
}
preserved_source = preserve_copy(
    tunic,
    "Comforting_Cat_V6",
    "A27",
    "attempt26_side_edge_and_inherited_shader",
)

# Push only the two outer columns into the coat silhouette.
inverse = tunic.matrix_world.inverted()
edge_y = {
    0: -0.350,
    4: -0.350,
    5: -0.360,
    9: -0.360,
    10: -0.360,
    14: -0.360,
    15: -0.350,
    19: -0.350,
}
for index, y_value in edge_y.items():
    vertex = tunic.data.vertices[index]
    world = tunic.matrix_world @ vertex.co
    world.y = y_value
    vertex.co = inverse @ world
tunic.data.update()

# Do not inherit the old procedural shader: build a minimal independent linen.
material = bpy.data.materials.new("V6_TunicWarmLinen_A27")
material.use_nodes = True
material.diffuse_color = (0.23, 0.26, 0.25, 1.0)
material.roughness = 0.87
nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.inputs["Base Color"].default_value = (0.23, 0.26, 0.25, 1.0)
principled.inputs["Roughness"].default_value = 0.87
principled.inputs["Specular IOR Level"].default_value = 0.24
links.new(principled.outputs["BSDF"], output.inputs["Surface"])
tunic.data.materials.clear()
tunic.data.materials.append(material)

bpy.context.view_layer.update()
after = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "material": material.name,
}
metrics = {
    "tunic_width_over_robe_width": round(
        after["tunic"]["dimensions"][0] / after["robe"]["dimensions"][0], 5
    ),
    "tunic_depth": after["tunic"]["dimensions"][1],
    "edge_front_y": -0.36,
    "robe_front_y": before["robe"]["min"][1],
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TunicMaterialEmbed_A27"
scene["comforting_cat_v6_stage"] = "TUNIC_MATERIAL_EMBED"
scene["comforting_cat_v6_attempt"] = 27
scene["comforting_cat_v6_dominant_defect"] = "bright_apron_and_side_plate"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TUNIC_MATERIAL_EMBED",
    "attempt": 27,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "bright_apron_and_side_plate",
    "preserved_source": preserved_source,
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
