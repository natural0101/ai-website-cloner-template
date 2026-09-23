"""Make the square short satchel taller and narrower as one preserved group."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_satchel_tall_soft_attempt35"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_feline_paws_attempt34.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_satchel_tall_soft_attempt35.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def transform_world(
    obj: bpy.types.Object,
    pivot: Vector,
    scale_x: float,
    scale_z: float,
) -> None:
    inverse = obj.matrix_world.inverted()

    def transform(point: Vector) -> Vector:
        world = point.copy()
        world.x = pivot.x + (world.x - pivot.x) * scale_x
        world.z = pivot.z + (world.z - pivot.z) * scale_z
        return world

    if obj.type == "MESH":
        for vertex in obj.data.vertices:
            vertex.co = inverse @ transform(obj.matrix_world @ vertex.co)
        obj.data.update()
    elif obj.type == "CURVE":
        for spline in obj.data.splines:
            for point in spline.bezier_points:
                point.co = inverse @ transform(obj.matrix_world @ point.co)
                point.handle_left = inverse @ transform(
                    obj.matrix_world @ point.handle_left
                )
                point.handle_right = inverse @ transform(
                    obj.matrix_world @ point.handle_right
                )
        bpy.context.view_layer.update()
    else:
        raise RuntimeError(f"Unsupported satchel object type: {obj.type}")


root = bpy.data.objects["CatV6_Root"]
group_names = [
    "V6_Satchel",
    "V6_SatchelFlap",
    "V6_SatchelHeart",
    "V6_SatchelTasselCord_0",
    "V6_SatchelTasselCord_1",
    "V6_SatchelTassel_0",
    "V6_SatchelTassel_1",
]
objects = [bpy.data.objects[name] for name in group_names]
before = {obj.name: bounds(obj) for obj in objects}
preserved_sources = [
    preserve_copy(
        obj,
        "Comforting_Cat_V6",
        "A35",
        "short_square_hard_case_satchel",
    )
    for obj in objects
]

pivot = Vector((0.360, -0.550, 1.560))
for obj in objects:
    transform_world(obj, pivot, 0.887, 1.205)

# Keep the heart emblem compact after the bag's vertical elongation.
heart = bpy.data.objects["V6_SatchelHeart"]
heart_bounds = bounds(heart)
heart_center = Vector(
    (
        (heart_bounds["min"][0] + heart_bounds["max"][0]) * 0.5,
        (heart_bounds["min"][1] + heart_bounds["max"][1]) * 0.5,
        (heart_bounds["min"][2] + heart_bounds["max"][2]) * 0.5,
    )
)
transform_world(heart, heart_center, 1.0, 0.83)

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in objects}
bag = after["V6_Satchel"]
metrics = {
    "bag_width": bag["dimensions"][0],
    "bag_height": bag["dimensions"][2],
    "bag_width_height": round(
        bag["dimensions"][0] / bag["dimensions"][2], 5
    ),
    "bag_top_z": bag["max"][2],
    "bag_bottom_z": bag["min"][2],
    "group_scale_x": 0.887,
    "group_scale_z": 1.205,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_SatchelTallSoft_A35"
scene["comforting_cat_v6_stage"] = "SATCHEL_TALL_SOFT"
scene["comforting_cat_v6_attempt"] = 35
scene["comforting_cat_v6_dominant_defect"] = "short_square_hard_case_satchel"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SATCHEL_TALL_SOFT",
    "attempt": 35,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "short_square_hard_case_satchel",
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
