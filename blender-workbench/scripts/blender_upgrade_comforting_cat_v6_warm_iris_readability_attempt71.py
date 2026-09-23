"""Restore a restrained warm iris rim while keeping the accepted A70 eye envelope."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_warm_iris_readability_attempt71"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_face_envelope_relock_attempt70.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_warm_iris_readability_attempt71.blend"
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


def principled(material: bpy.types.Material) -> bpy.types.ShaderNodeBsdfPrincipled:
    if not material.use_nodes or material.node_tree is None:
        raise RuntimeError(f"Material {material.name} has no node tree")
    node = next(
        (item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED"),
        None,
    )
    if node is None:
        raise RuntimeError(f"Material {material.name} has no Principled BSDF")
    return node


def material_snapshot(material: bpy.types.Material) -> dict[str, object]:
    shader = principled(material)
    return {
        "name": material.name,
        "base_color": [round(float(value), 6) for value in shader.inputs["Base Color"].default_value],
        "roughness": round(float(shader.inputs["Roughness"].default_value), 6),
    }


def fit_pupil_xz(obj: bpy.types.Object, target_x: float, target_z: float) -> None:
    before = bounds(obj)
    center_x = 0.5 * (before["min"][0] + before["max"][0])
    center_z = 0.5 * (before["min"][2] + before["max"][2])
    scale_x = target_x / before["dimensions"][0]
    scale_z = target_z / before["dimensions"][2]
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x = center_x + (world.x - center_x) * scale_x
        world.z = center_z + (world.z - center_z) * scale_z
        vertex.co = inverse @ world
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
eye_names = ["V6_Eye_L", "V6_Eye_R"]
pupil_names = ["V6_Pupil_L", "V6_Pupil_R"]
highlight_names = ["V6_EyeHighlight_L", "V6_EyeHighlight_R"]
eyes = [bpy.data.objects[name] for name in eye_names]
pupils = [bpy.data.objects[name] for name in pupil_names]
highlights = [bpy.data.objects[name] for name in highlight_names]
locked_geometry = [obj for obj in descendants(root) if obj.name not in pupil_names]
locked_hash_before = geometry_hash(locked_geometry)
before = {obj.name: bounds(obj) for obj in [*eyes, *pupils, *highlights]}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A71", "black_plastic_eye_disc")
    for obj in [*eyes, *pupils]
]

old_iris = eyes[0].data.materials[0]
old_pupil = pupils[0].data.materials[0]
materials_before = {
    "iris": material_snapshot(old_iris),
    "pupil": material_snapshot(old_pupil),
}

iris_material = old_iris.copy()
iris_material.name = "V6_EyeIrisWarmReadable_A71"
iris_shader = principled(iris_material)
iris_shader.inputs["Base Color"].default_value = (0.13, 0.047, 0.014, 1.0)
iris_shader.inputs["Roughness"].default_value = 0.30

pupil_material = old_pupil.copy()
pupil_material.name = "V6_EyePupilSoftBlack_A71"
pupil_shader = principled(pupil_material)
pupil_shader.inputs["Base Color"].default_value = (0.010, 0.006, 0.004, 1.0)
pupil_shader.inputs["Roughness"].default_value = 0.26

for eye in eyes:
    eye.data.materials[0] = iris_material
for pupil in pupils:
    fit_pupil_xz(pupil, 0.183, 0.228)
    pupil.data.materials[0] = pupil_material

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in [*eyes, *pupils, *highlights]}
locked_hash_after = geometry_hash(locked_geometry)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("Warm-iris pass changed the A70 eye lens, highlight, head or locked geometry")

eye_bounds_delta = 0.0
highlight_bounds_delta = 0.0
for name in eye_names:
    for key in ("min", "max", "dimensions"):
        eye_bounds_delta = max(
            eye_bounds_delta,
            max(abs(a - b) for a, b in zip(before[name][key], after[name][key], strict=True)),
        )
for name in highlight_names:
    for key in ("min", "max", "dimensions"):
        highlight_bounds_delta = max(
            highlight_bounds_delta,
            max(abs(a - b) for a, b in zip(before[name][key], after[name][key], strict=True)),
        )
if eye_bounds_delta > 0.00001 or highlight_bounds_delta > 0.00001:
    raise RuntimeError("Eye lens or highlight bounds changed")

y_lock_delta = 0.0
for name in pupil_names:
    for key in ("min", "max", "dimensions"):
        y_lock_delta = max(y_lock_delta, abs(before[name][key][1] - after[name][key][1]))
if y_lock_delta > 0.00001:
    raise RuntimeError("Pupil Y depth changed")

eye_width = after[eye_names[0]]["dimensions"][0]
eye_height = after[eye_names[0]]["dimensions"][2]
pupil_width = after[pupil_names[0]]["dimensions"][0]
pupil_height = after[pupil_names[0]]["dimensions"][2]
metrics = {
    "pupil_width": round(pupil_width, 6),
    "pupil_height": round(pupil_height, 6),
    "pupil_fill_x": round(pupil_width / eye_width, 5),
    "pupil_fill_z": round(pupil_height / eye_height, 5),
    "iris_rim_each_side_x": round((eye_width - pupil_width) * 0.5, 6),
    "iris_rim_each_side_z": round((eye_height - pupil_height) * 0.5, 6),
    "eye_bounds_delta": round(eye_bounds_delta, 8),
    "highlight_bounds_delta": round(highlight_bounds_delta, 8),
    "pupil_y_lock_delta": round(y_lock_delta, 8),
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
materials_after = {
    "iris": material_snapshot(iris_material),
    "pupil": material_snapshot(pupil_material),
}
print("A71_PRE_GATE_METRICS=" + repr(metrics))
if not 0.180 <= pupil_width <= 0.186:
    raise RuntimeError("Pupil X width outside target")
if not 0.224 <= pupil_height <= 0.232:
    raise RuntimeError("Pupil Z height outside target")
if not 0.772 <= metrics["pupil_fill_x"] <= 0.798:
    raise RuntimeError("Pupil X fill outside target")
if not 0.808 <= metrics["pupil_fill_z"] <= 0.837:
    raise RuntimeError("Pupil Z fill outside target")
if not 0.023 <= metrics["iris_rim_each_side_x"] <= 0.027:
    raise RuntimeError("Iris X rim outside target")
if not 0.022 <= metrics["iris_rim_each_side_z"] <= 0.027:
    raise RuntimeError("Iris Z rim outside target")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_WarmIrisReadability_A71"
scene["comforting_cat_v6_stage"] = "WARM_IRIS_READABILITY"
scene["comforting_cat_v6_attempt"] = 71
scene["comforting_cat_v6_dominant_defect"] = "black_plastic_eye_disc"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "WARM_IRIS_READABILITY",
    "attempt": 71,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "black_plastic_eye_disc",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "materials_before": materials_before,
    "materials_after": materials_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["pupil X/Z footprint", "dedicated visible iris and pupil materials"],
        "preserved": ["eye lens bounds", "pupil Y", "highlights", "A70 face envelope", "head", "costume", "tail", "camera", "lights"],
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
