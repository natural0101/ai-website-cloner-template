"""Desaturate the iris and seat the correctly sized pupil into one eye profile."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_eye_stack_integration_attempt72"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_eye_stack_integration_attempt72.blend"
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


def principled(material: bpy.types.Material):
    if not material.use_nodes or material.node_tree is None:
        raise RuntimeError(f"Material {material.name} has no nodes")
    node = next((item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED"), None)
    if node is None:
        raise RuntimeError(f"Material {material.name} has no Principled BSDF")
    return node


def fit_pupil(obj: bpy.types.Object, target_x: float, target_z: float, target_y_center: float) -> None:
    current = bounds(obj)
    center_x = 0.5 * (current["min"][0] + current["max"][0])
    center_z = 0.5 * (current["min"][2] + current["max"][2])
    center_y = 0.5 * (current["min"][1] + current["max"][1])
    scale_x = target_x / current["dimensions"][0]
    scale_z = target_z / current["dimensions"][2]
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x = center_x + (world.x - center_x) * scale_x
        world.z = center_z + (world.z - center_z) * scale_z
        world.y += target_y_center - center_y
        vertex.co = inverse @ world
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
eye_names = ["V6_Eye_L", "V6_Eye_R"]
pupil_names = ["V6_Pupil_L", "V6_Pupil_R"]
highlight_names = ["V6_EyeHighlight_L", "V6_EyeHighlight_R"]
eyes = [bpy.data.objects[name] for name in eye_names]
pupils = [bpy.data.objects[name] for name in pupil_names]
highlights = [bpy.data.objects[name] for name in highlight_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in pupil_names]
locked_hash_before = geometry_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in [*eyes, *pupils, *highlights]}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A72", "layered_black_eye_stack")
    for obj in [*eyes, *pupils]
]

iris_material = eyes[0].data.materials[0].copy()
iris_material.name = "V6_EyeIrisDeepWarm_A72"
iris_shader = principled(iris_material)
iris_shader.inputs["Base Color"].default_value = (0.075, 0.027, 0.012, 1.0)
iris_shader.inputs["Roughness"].default_value = 0.37

pupil_material = pupils[0].data.materials[0].copy()
pupil_material.name = "V6_EyePupilInsetBlack_A72"
pupil_shader = principled(pupil_material)
pupil_shader.inputs["Base Color"].default_value = (0.009, 0.005, 0.004, 1.0)
pupil_shader.inputs["Roughness"].default_value = 0.28

for eye in eyes:
    eye.data.materials[0] = iris_material
for pupil in pupils:
    fit_pupil(pupil, target_x=0.183, target_z=0.228, target_y_center=-0.500)
    pupil.data.materials[0] = pupil_material

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in [*eyes, *pupils, *highlights]}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A72 changed the A70 eye lens, highlight or locked geometry")

eye_width = after[eye_names[0]]["dimensions"][0]
eye_height = after[eye_names[0]]["dimensions"][2]
pupil_width = after[pupil_names[0]]["dimensions"][0]
pupil_height = after[pupil_names[0]]["dimensions"][2]
eye_front_y = after[eye_names[0]]["min"][1]
pupil_front_y = after[pupil_names[0]]["min"][1]
pupil_back_y = after[pupil_names[0]]["max"][1]
front_step = eye_front_y - pupil_front_y
overlap_y = min(after[eye_names[0]]["max"][1], pupil_back_y) - max(eye_front_y, pupil_front_y)

eye_highlight_delta = 0.0
for name in [*eye_names, *highlight_names]:
    for key in ("min", "max", "dimensions"):
        eye_highlight_delta = max(
            eye_highlight_delta,
            max(abs(a - b) for a, b in zip(before[name][key], after[name][key], strict=True)),
        )
metrics = {
    "pupil_fill_x": round(pupil_width / eye_width, 5),
    "pupil_fill_z": round(pupil_height / eye_height, 5),
    "iris_rim_each_side_x": round((eye_width - pupil_width) * 0.5, 6),
    "iris_rim_each_side_z": round((eye_height - pupil_height) * 0.5, 6),
    "pupil_front_step": round(front_step, 6),
    "eye_pupil_y_overlap": round(overlap_y, 6),
    "eye_highlight_bounds_delta": round(eye_highlight_delta, 8),
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A72_PRE_GATE_METRICS=" + repr(metrics))
if not 0.772 <= metrics["pupil_fill_x"] <= 0.798:
    raise RuntimeError("Pupil X fill outside target")
if not 0.808 <= metrics["pupil_fill_z"] <= 0.837:
    raise RuntimeError("Pupil Z fill outside target")
if not 0.001 <= front_step <= 0.003:
    raise RuntimeError(f"Pupil front step outside integrated target: {front_step}")
if overlap_y < 0.010:
    raise RuntimeError("Pupil is not sufficiently seated in the iris lens")
if eye_highlight_delta > 0.00001:
    raise RuntimeError("Eye lens or highlight bounds changed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EyeStackIntegration_A72"
scene["comforting_cat_v6_stage"] = "EYE_STACK_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 72
scene["comforting_cat_v6_dominant_defect"] = "layered_orange_eye_stack"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "EYE_STACK_INTEGRATION",
    "attempt": 72,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "layered_orange_eye_stack",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "materials": {
        "iris_base": [0.075, 0.027, 0.012, 1.0],
        "iris_roughness": 0.37,
        "pupil_base": [0.009, 0.005, 0.004, 1.0],
        "pupil_roughness": 0.28,
    },
    "metrics": metrics,
    "scope_lock": {
        "changed": ["pupil X/Z footprint and Y seating", "dedicated iris/pupil materials"],
        "preserved": ["eye lens bounds", "highlights", "A70 face envelope", "head", "costume", "tail", "camera", "lights"],
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
