"""Major head/face rebuild from accepted attempt31, not the rejected serration."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_head_face_feline_rebuild_attempt33"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_face_feline_rebuild_attempt33.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def interpolate_knots(value: float, knots: list[tuple[float, float]]) -> float:
    if value <= knots[0][0]:
        return knots[0][1]
    if value >= knots[-1][0]:
        return knots[-1][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            t = t * t * (3.0 - 2.0 * t)
            return y0 * (1.0 - t) + y1 * t
    return 1.0


def scale_mesh_local_world(
    obj: bpy.types.Object,
    scale_x: float,
    scale_z: float,
    translate_x: float = 0.0,
) -> None:
    obj_bounds = bounds(obj)
    center = Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x = center.x + (world.x - center.x) * scale_x + translate_x
        world.z = center.z + (world.z - center.z) * scale_z
        vertex.co = inverse @ world
    obj.data.update()


def band_half_width(
    obj: bpy.types.Object,
    z_min: float,
    z_max: float,
) -> float:
    values = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if z_min <= world.z <= z_max:
            values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
eye_names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
]
unified_muzzle = bpy.data.objects["V6_MuzzleUnified"]
nose = bpy.data.objects["V6_Nose"]
affected = [head, unified_muzzle, nose] + [
    bpy.data.objects[name] for name in eye_names
]
before = {obj.name: bounds(obj) for obj in affected}
preserved_sources = [
    preserve_copy(
        obj,
        "Comforting_Cat_V6",
        "A33",
        "mushroom_head_small_eyes_capsule_muzzle",
    )
    for obj in [head, nose] + [bpy.data.objects[name] for name in eye_names]
]

# Reduce the lower mushroom flare while carrying more mass into the crown.
head_profile = [
    (2.26, 0.78),
    (2.46, 0.84),
    (2.58, 0.90),
    (2.72, 0.92),
    (2.90, 0.98),
    (3.08, 1.10),
    (3.24, 1.14),
    (3.38, 1.00),
]
head_inverse = head.matrix_world.inverted()
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    world.x *= interpolate_knots(world.z, head_profile)
    vertex.co = head_inverse @ world
head.data.update()

# Eyes must carry the sad kitten expression instead of reading as small coins.
for side, sign in (("L", -1.0), ("R", 1.0)):
    for stem in ("V6_Eye", "V6_Pupil", "V6_EyeHighlight"):
        scale_mesh_local_world(
            bpy.data.objects[f"{stem}_{side}"],
            1.23,
            1.08,
            sign * 0.010,
        )

# Replace the single white pill with two strongly overlapping cheek volumes.
unified_muzzle.parent = None
unified_muzzle.hide_render = True
unified_muzzle.hide_set(True)
unified_muzzle.name = "V6_MuzzleUnified_SOURCE_A33"
unified_muzzle["comforting_cat_preserved_source"] = True
unified_muzzle["comforting_cat_rejection_reason"] = "single_stuck_on_white_capsule"
preserved_sources.append(unified_muzzle.name)
muzzle_material = unified_muzzle.data.materials[0]

created_muzzles: list[bpy.types.Object] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=24,
        location=(sign * 0.115, -0.535, 2.550),
    )
    muzzle = bpy.context.object
    muzzle.name = f"V6_Muzzle_{side}"
    muzzle.scale = (0.175, 0.110, 0.132)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    muzzle.parent = root
    muzzle.matrix_parent_inverse = root.matrix_world.inverted()
    muzzle.data.materials.append(muzzle_material)
    for polygon in muzzle.data.polygons:
        polygon.use_smooth = True
    created_muzzles.append(muzzle)

scale_mesh_local_world(nose, 0.90, 0.90)

bpy.context.view_layer.update()
after = {
    "head": bounds(head),
    "nose": bounds(nose),
    "eyes": {name: bounds(bpy.data.objects[name]) for name in eye_names},
    "muzzles": {obj.name: bounds(obj) for obj in created_muzzles},
}
crown_half = band_half_width(head, 3.03, 3.18)
cheek_half = band_half_width(head, 2.55, 2.75)
head_width = after["head"]["dimensions"][0]
combined_muzzle_min = min(bounds(obj)["min"][0] for obj in created_muzzles)
combined_muzzle_max = max(bounds(obj)["max"][0] for obj in created_muzzles)
metrics = {
    "cheek_over_crown_width": round(cheek_half / crown_half, 5),
    "head_width": head_width,
    "single_eye_width_over_head_width": round(
        after["eyes"]["V6_Eye_L"]["dimensions"][0] / head_width, 5
    ),
    "combined_muzzle_width_over_head_width": round(
        (combined_muzzle_max - combined_muzzle_min) / head_width, 5
    ),
    "head_vertex_count": len(head.data.vertices),
    "head_face_count": len(head.data.polygons),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadFaceFelineRebuild_A33"
scene["comforting_cat_v6_stage"] = "HEAD_FACE_FELINE_REBUILD"
scene["comforting_cat_v6_attempt"] = 33
scene["comforting_cat_v6_dominant_defect"] = "mushroom_head_small_eyes_capsule_muzzle"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_FACE_FELINE_REBUILD",
    "attempt": 33,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "mushroom_head_small_eyes_capsule_muzzle",
    "head_profile": head_profile,
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
