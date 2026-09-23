"""Seat the eye and muzzle layers into one shallow feline facial relief."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_face_relief_integration_attempt43"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_integrated_cheek_microtufts_attempt42.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_face_relief_integration_attempt43.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def object_center(obj: bpy.types.Object) -> Vector:
    obj_bounds = bounds(obj)
    return Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )


def fit_mesh_world(
    obj: bpy.types.Object,
    center: Vector,
    dimensions: Vector,
) -> None:
    old_center = object_center(obj)
    old_dimensions = Vector(bounds(obj)["dimensions"])
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        offset = world - old_center
        offset.x *= dimensions.x / old_dimensions.x
        offset.y *= dimensions.y / old_dimensions.y
        offset.z *= dimensions.z / old_dimensions.z
        vertex.co = inverse @ (center + offset)
    obj.data.update()


def fit_curve_world_y(obj: bpy.types.Object, y_min: float, y_max: float) -> None:
    old = bounds(obj)
    old_center = (old["min"][1] + old["max"][1]) * 0.5
    old_depth = max(old["dimensions"][1], 1e-6)
    new_center = (y_min + y_max) * 0.5
    new_depth = y_max - y_min
    inverse = obj.matrix_world.inverted()

    def transform(point: Vector) -> Vector:
        world = point.copy()
        world.y = new_center + (world.y - old_center) * (new_depth / old_depth)
        return world

    for spline in obj.data.splines:
        for point in spline.bezier_points:
            point.co = inverse @ transform(obj.matrix_world @ point.co)
            point.handle_left = inverse @ transform(obj.matrix_world @ point.handle_left)
            point.handle_right = inverse @ transform(obj.matrix_world @ point.handle_right)
    obj.data.update_tag()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
eyes = [bpy.data.objects["V6_Eye_L"], bpy.data.objects["V6_Eye_R"]]
pupils = [bpy.data.objects["V6_Pupil_L"], bpy.data.objects["V6_Pupil_R"]]
highlights = [
    bpy.data.objects["V6_EyeHighlight_L"],
    bpy.data.objects["V6_EyeHighlight_R"],
]
muzzles = [bpy.data.objects["V6_Muzzle_L"], bpy.data.objects["V6_Muzzle_R"]]
nose = bpy.data.objects["V6_Nose"]
mouth = bpy.data.objects["V6_Mouth"]
philtrum = bpy.data.objects["V6_Philtrum"]
whiskers = [
    bpy.data.objects[f"V6_Whisker_{side}_{index}"]
    for side in ("L", "R")
    for index in range(3)
]
affected = eyes + pupils + highlights + muzzles + [nose, mouth, philtrum] + whiskers
before = {obj.name: bounds(obj) for obj in affected}
head_before = bounds(head)
head_topology_before = (len(head.data.vertices), len(head.data.polygons))
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A43", "separated_face_relief_layer")
    for obj in affected
]

# Preserve the approved front eye footprint while reducing only relief depth.
for eye in eyes:
    center = object_center(eye)
    old_dimensions = Vector(bounds(eye)["dimensions"])
    fit_mesh_world(
        eye,
        Vector((center.x, -0.475, center.z)),
        Vector((old_dimensions.x, 0.060, old_dimensions.z)),
    )

# Fill the eye much more completely, matching the dark worried eyes in the
# reference while retaining a narrow iris rim and a convex depth overlap.
for pupil, eye in zip(pupils, eyes, strict=True):
    center = object_center(eye)
    fit_mesh_world(
        pupil,
        Vector((center.x, -0.506, 2.885)),
        Vector((0.215, 0.014, 0.240)),
    )

for highlight in highlights:
    center = object_center(highlight)
    old_dimensions = Vector(bounds(highlight)["dimensions"])
    fit_mesh_world(
        highlight,
        Vector((center.x, -0.515, center.z)),
        Vector((old_dimensions.x, 0.006, old_dimensions.z)),
    )

# Keep the approved combined muzzle width, but make it a shallow W-shaped
# relief embedded into the head instead of two forward white balls.
for muzzle in muzzles:
    center = object_center(muzzle)
    old_dimensions = Vector(bounds(muzzle)["dimensions"])
    fit_mesh_world(
        muzzle,
        Vector((center.x, -0.450, 2.550)),
        Vector((old_dimensions.x, 0.180, 0.220)),
    )

fit_mesh_world(
    nose,
    Vector((0.0, -0.548, 2.598)),
    Vector((0.080, 0.040, 0.070)),
)
fit_curve_world_y(mouth, -0.553, -0.547)
fit_curve_world_y(philtrum, -0.553, -0.548)
mouth.data.bevel_depth = 0.0065
philtrum.data.bevel_depth = 0.0055

for whisker in whiskers:
    fit_curve_world_y(whisker, -0.548, -0.505)
    whisker.data.bevel_depth = 0.00225

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in affected}
head_after = bounds(head)
head_topology_after = (len(head.data.vertices), len(head.data.polygons))

eye_width = after[eyes[0].name]["dimensions"][0]
pupil_width = after[pupils[0].name]["dimensions"][0]
muzzle_min_x = min(after[obj.name]["min"][0] for obj in muzzles)
muzzle_max_x = max(after[obj.name]["max"][0] for obj in muzzles)
metrics = {
    "head_bounds_unchanged": head_before == head_after,
    "head_topology_unchanged": head_topology_before == head_topology_after,
    "eye_width_over_head_width": round(eye_width / head_after["dimensions"][0], 5),
    "pupil_fill_eye_x": round(pupil_width / eye_width, 5),
    "combined_muzzle_width_over_head": round(
        (muzzle_max_x - muzzle_min_x) / head_after["dimensions"][0], 5
    ),
    "eye_pupil_y_overlap": round(
        overlap_1d(after[eyes[0].name], after[pupils[0].name], 1), 5
    ),
    "muzzle_head_y_overlap": round(
        overlap_1d(after[muzzles[0].name], head_after, 1), 5
    ),
    "nose_muzzle_y_overlap": round(
        overlap_1d(after[nose.name], after[muzzles[0].name], 1), 5
    ),
    "mouth_bevel": mouth.data.bevel_depth,
    "philtrum_bevel": philtrum.data.bevel_depth,
    "whisker_bevel": whiskers[0].data.bevel_depth,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FaceReliefIntegration_A43"
scene["comforting_cat_v6_stage"] = "FACE_RELIEF_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 43
scene["comforting_cat_v6_dominant_defect"] = "plastic_separated_eye_and_muzzle_layers"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FACE_RELIEF_INTEGRATION",
    "attempt": 43,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "plastic_separated_eye_and_muzzle_layers",
    "preserved_sources": preserved_sources,
    "do_not_change": [
        "V6_Head",
        "V6_Ear_L/R",
        "V6_InnerEar_L/R",
        "scarf/body/arms/bag/tail",
        "camera/light/materials",
    ],
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
