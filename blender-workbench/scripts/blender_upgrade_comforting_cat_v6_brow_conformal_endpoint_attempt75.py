"""Hide the A74 brow end-on spike while preserving its accepted front emotion profile."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_brow_conformal_endpoint_attempt75"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_brow_emotion_integration_attempt74.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_brow_conformal_endpoint_attempt75.blend"
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
    preserve_copy(obj, "Comforting_Cat_V6", "A75", "brow_outer_endpoint_side_spike")
    for obj in brows
]

profiles = {}
for brow in brows:
    points = list(brow.data.splines[0].bezier_points)
    outer = max(points, key=lambda point: abs((brow.matrix_world @ point.co).x))
    outer_before = brow.matrix_world @ outer.co
    outer_after = outer_before.copy()
    outer_after.x -= 0.025 if outer_after.x > 0.0 else -0.025
    outer.co = brow.matrix_world.inverted() @ outer_after
    outer.radius = 0.05
    outer.handle_left_type = "AUTO"
    outer.handle_right_type = "AUTO"
    brow.data.update_tag()
    profiles[brow.name] = {
        "outer_before": [round(float(v), 6) for v in outer_before],
        "outer_after": [round(float(v), 6) for v in outer_after],
        "inward_x_shift": round(abs(outer_after.x - outer_before.x), 6),
        "outer_radius": round(float(outer.radius), 6),
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in brows}
locked_hash_after = object_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A75 changed A73/A74 geometry outside the two brow curves")

for name, profile in profiles.items():
    if abs(profile["inward_x_shift"] - 0.025) > 0.00001:
        raise RuntimeError(f"{name} endpoint inward shift outside target")
    if abs(profile["outer_radius"] - 0.05) > 0.00001:
        raise RuntimeError(f"{name} endpoint radius outside target")

metrics = {
    "profiles": profiles,
    "left_brow_width_before": before["V6_Eyebrow_L"]["dimensions"][0],
    "left_brow_width_after": after["V6_Eyebrow_L"]["dimensions"][0],
    "right_brow_width_before": before["V6_Eyebrow_R"]["dimensions"][0],
    "right_brow_width_after": after["V6_Eyebrow_R"]["dimensions"][0],
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A75_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_BrowConformalEndpoint_A75"
scene["comforting_cat_v6_stage"] = "BROW_CONFORMAL_ENDPOINT"
scene["comforting_cat_v6_attempt"] = 75
scene["comforting_cat_v6_dominant_defect"] = "brow_outer_endpoint_side_spike"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "BROW_CONFORMAL_ENDPOINT",
    "attempt": 75,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "brow_outer_endpoint_side_spike",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["outer endpoint X and radius for V6_Eyebrow_L/R only"],
        "preserved": ["A74 brow Z/Y profile", "A73 proportions", "eyes", "head", "muzzle", "costume", "legs", "tail", "camera", "lights", "materials"],
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
