"""Curve, taper and seat the rigid eyebrow rods into a softer worried expression."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_brow_emotion_integration_attempt74"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_upper_stack_settle_attempt73.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_brow_emotion_integration_attempt74.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
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
                digest.update(f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii"))
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                for point in spline.bezier_points:
                    digest.update(
                        f"{point.co.x:.9f},{point.co.y:.9f},{point.co.z:.9f},{point.radius:.9f};".encode("ascii")
                    )
    return digest.hexdigest()


root = bpy.data.objects["CatV6_Root"]
brow_names = ["V6_Eyebrow_L", "V6_Eyebrow_R"]
brows = [bpy.data.objects[name] for name in brow_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in brow_names]
locked_hash_before = object_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in brows}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A74", "rigid_floating_eyebrow_rod")
    for obj in brows
]

center_profiles = {}
for brow in brows:
    if len(brow.data.splines) != 1 or len(brow.data.splines[0].bezier_points) != 3:
        raise RuntimeError(f"Unexpected eyebrow topology for {brow.name}")
    points = list(brow.data.splines[0].bezier_points)
    ordered = sorted(points, key=lambda point: abs((brow.matrix_world @ point.co).x), reverse=True)
    outer, middle, inner = ordered
    world_points = {
        "outer": brow.matrix_world @ outer.co,
        "middle": brow.matrix_world @ middle.co,
        "inner": brow.matrix_world @ inner.co,
    }
    for point in points:
        world = brow.matrix_world @ point.co
        world.y += 0.006
        point.co = brow.matrix_world.inverted() @ world
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    for key, offset in (("outer", 0.002), ("middle", 0.014), ("inner", 0.004)):
        point = {"outer": outer, "middle": middle, "inner": inner}[key]
        world = brow.matrix_world @ point.co
        world.z += offset
        point.co = brow.matrix_world.inverted() @ world
    outer.radius = 0.35
    middle.radius = 0.90
    inner.radius = 0.50
    brow.data.bevel_depth = 0.013
    brow.data.bevel_resolution = 4
    brow.data.resolution_u = 8
    brow.data.update_tag()

    outer_world = brow.matrix_world @ outer.co
    middle_world = brow.matrix_world @ middle.co
    inner_world = brow.matrix_world @ inner.co
    interpolation = outer_world.z + (
        (middle_world.x - outer_world.x) / (inner_world.x - outer_world.x)
    ) * (inner_world.z - outer_world.z)
    center_profiles[brow.name] = {
        "outer": [round(float(v), 6) for v in outer_world],
        "middle": [round(float(v), 6) for v in middle_world],
        "inner": [round(float(v), 6) for v in inner_world],
        "inner_outer_rise": round(inner_world.z - outer_world.z, 6),
        "middle_arch_above_chord": round(middle_world.z - interpolation, 6),
        "radii": [outer.radius, middle.radius, inner.radius],
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in brows}
locked_hash_after = object_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("Brow pass changed A73 geometry or transforms outside the two brows")

for name, profile in center_profiles.items():
    if not 0.085 <= profile["inner_outer_rise"] <= 0.105:
        raise RuntimeError(f"{name} worried inner/outer rise outside target")
    if not 0.010 <= profile["middle_arch_above_chord"] <= 0.020:
        raise RuntimeError(f"{name} brow arch outside target")
    if max(
        abs(actual - expected)
        for actual, expected in zip(profile["radii"], [0.35, 0.9, 0.5], strict=True)
    ) > 0.00001:
        raise RuntimeError(f"{name} taper radii changed")

depth_shift = max(
    abs((before[name]["min"][1] + 0.006) - after[name]["min"][1])
    for name in brow_names
)
metrics = {
    "profiles": center_profiles,
    "maximum_bounds_depth_residual": round(depth_shift, 6),
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A74_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_BrowEmotionIntegration_A74"
scene["comforting_cat_v6_stage"] = "BROW_EMOTION_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 74
scene["comforting_cat_v6_dominant_defect"] = "rigid_floating_eyebrow_rods"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "BROW_EMOTION_INTEGRATION",
    "attempt": 74,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_floating_eyebrow_rods",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Eyebrow_L/R control points, radii and curve resolution"],
        "preserved": ["A73 proportions", "eyes", "head", "muzzle", "whiskers", "costume", "legs", "tail", "camera", "lights", "materials"],
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
