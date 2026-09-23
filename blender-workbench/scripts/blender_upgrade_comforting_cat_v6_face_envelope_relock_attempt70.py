"""Relock the face X envelope to the accepted narrower A69 head volume."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_face_envelope_relock_attempt70"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_head_continuous_volume_attempt69.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_face_envelope_relock_attempt70.blend"
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


def geometry_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted((item for item in objects if item.type == "MESH"), key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for value in obj.matrix_world:
            for component in value:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def contract_mesh_world_x(obj: bpy.types.Object, factor: float) -> None:
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x *= factor
        vertex.co = inverse @ world
    obj.data.update()


def contract_curve_world_x(obj: bpy.types.Object, factor: float) -> None:
    inverse = obj.matrix_world.inverted()

    def transform(point):
        world = obj.matrix_world @ point
        world.x *= factor
        return inverse @ world

    for spline in obj.data.splines:
        for point in spline.bezier_points:
            point.co = transform(point.co)
            point.handle_left = transform(point.handle_left)
            point.handle_right = transform(point.handle_right)
        for point in spline.points:
            world = obj.matrix_world @ point.co.to_3d()
            world.x *= factor
            local = inverse @ world
            point.co.x, point.co.y, point.co.z = local.x, local.y, local.z
    obj.data.update_tag()


root = bpy.data.objects["CatV6_Root"]
mesh_names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
]
curve_names = ["V6_Eyebrow_L", "V6_Eyebrow_R"]
whisker_names = [f"V6_Whisker_{side}_{index}" for side in ("L", "R") for index in range(3)]
changed_names = mesh_names + curve_names + whisker_names
changed_objects = [bpy.data.objects[name] for name in changed_names]
unchanged_objects = [obj for obj in descendants(root) if obj.name not in changed_names]
unchanged_hash_before = geometry_hash(unchanged_objects)
before = {obj.name: bounds(obj) for obj in changed_objects}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A70", "face_envelope_relock_after_A69")
    for obj in changed_objects
]

for name in mesh_names:
    contract_mesh_world_x(bpy.data.objects[name], 0.96)
for name in curve_names:
    contract_curve_world_x(bpy.data.objects[name], 0.96)

# Contract the attachment zone only; retain the long organic whisker reach.
for name in whisker_names:
    obj = bpy.data.objects[name]
    inverse = obj.matrix_world.inverted()

    def root_transform(local_point):
        world = obj.matrix_world @ local_point
        absolute_x = abs(world.x)
        weight = max(0.0, min(1.0, (0.56 - absolute_x) / 0.26))
        world.x *= 1.0 - 0.04 * weight
        return inverse @ world

    for spline in obj.data.splines:
        for point in spline.bezier_points:
            point.co = root_transform(point.co)
            point.handle_left = root_transform(point.handle_left)
            point.handle_right = root_transform(point.handle_right)
    obj.data.update_tag()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in changed_objects}
unchanged_hash_after = geometry_hash(unchanged_objects)
if unchanged_hash_before != unchanged_hash_after:
    raise RuntimeError("Face relock changed the accepted A69 head or locked geometry")

yz_max_delta = 0.0
for name in changed_names:
    for key in ("min", "max", "dimensions"):
        for axis in (1, 2):
            yz_max_delta = max(yz_max_delta, abs(before[name][key][axis] - after[name][key][axis]))
if yz_max_delta > 0.002:
    raise RuntimeError(f"Face relock changed Y/Z bounds: {yz_max_delta}")

head_width = bounds(bpy.data.objects["V6_Head"])["dimensions"][0]
eye_width = after["V6_Eye_L"]["dimensions"][0]
left_eye_center = 0.5 * (after["V6_Eye_L"]["min"][0] + after["V6_Eye_L"]["max"][0])
right_eye_center = 0.5 * (after["V6_Eye_R"]["min"][0] + after["V6_Eye_R"]["max"][0])
muzzle_min = min(after["V6_Muzzle_L"]["min"][0], after["V6_Muzzle_R"]["min"][0])
muzzle_max = max(after["V6_Muzzle_L"]["max"][0], after["V6_Muzzle_R"]["max"][0])
pupil_fill = after["V6_Pupil_L"]["dimensions"][0] / eye_width
metrics = {
    "eye_width_over_head": round(eye_width / head_width, 5),
    "eye_geometric_center_separation_over_head": round((right_eye_center - left_eye_center) / head_width, 5),
    "combined_muzzle_width_over_head": round((muzzle_max - muzzle_min) / head_width, 5),
    "pupil_fill_x": round(pupil_fill, 5),
    "yz_lock_max_delta": round(yz_max_delta, 6),
    "unchanged_hash_before": unchanged_hash_before,
    "unchanged_hash_after": unchanged_hash_after,
}
print("A70_PRE_GATE_METRICS=" + repr(metrics))
if not 0.181 <= metrics["eye_width_over_head"] <= 0.186:
    raise RuntimeError(f"Eye/head ratio outside target: {metrics['eye_width_over_head']}")
if not 0.344 <= metrics["eye_geometric_center_separation_over_head"] <= 0.352:
    raise RuntimeError(
        f"Eye separation/head outside target: {metrics['eye_geometric_center_separation_over_head']}"
    )
if not 0.472 <= metrics["combined_muzzle_width_over_head"] <= 0.481:
    raise RuntimeError(f"Muzzle/head ratio outside target: {metrics['combined_muzzle_width_over_head']}")
if not 0.825 <= metrics["pupil_fill_x"] <= 0.840:
    raise RuntimeError(f"Pupil fill regressed: {metrics['pupil_fill_x']}")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FaceEnvelopeRelock_A70"
scene["comforting_cat_v6_stage"] = "FACE_ENVELOPE_RELOCK"
scene["comforting_cat_v6_attempt"] = 70
scene["comforting_cat_v6_dominant_defect"] = "face_envelope_too_wide_after_A69"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FACE_ENVELOPE_RELOCK",
    "attempt": 70,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "face_envelope_too_wide_after_A69",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": changed_names + ["whisker roots only"],
        "preserved": ["all Y/Z", "nose", "mouth", "philtrum", "A69 head", "ears", "costume", "tail", "camera", "lights", "materials"],
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
