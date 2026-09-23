"""Face pass: replace toy-gold eyes with a darker, tender worried expression."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_tender_expression_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_robe_soft_profile_attempt2.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_tender_expression_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def srgb_to_linear(channel: int) -> float:
    value = channel / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def color(hex_value: str) -> tuple[float, float, float, float]:
    value = hex_value.lstrip("#")
    return (
        srgb_to_linear(int(value[0:2], 16)),
        srgb_to_linear(int(value[2:4], 16)),
        srgb_to_linear(int(value[4:6], 16)),
        1.0,
    )


def set_principled(material_name: str, hex_value: str, roughness: float) -> None:
    material = bpy.data.materials[material_name]
    material.diffuse_color = color(hex_value)
    material.roughness = roughness
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color(hex_value)
    principled.inputs["Roughness"].default_value = roughness


set_principled("CAT_IrisWarmBrown", "#2D2017", 0.46)
set_principled("CAT_EyeDarkGlass", "#1B130F", 0.40)
set_principled("CAT_Pupil", "#060403", 0.24)

for suffix in ("L", "R"):
    pupil = bpy.data.objects[f"Cat_Pupil_{suffix}"]
    for vertex in pupil.data.vertices:
        vertex.co.x *= 1.20
        vertex.co.z *= 1.08
    pupil.data.update()

    brow = bpy.data.objects[f"Cat_Eyebrow_{suffix}"]
    xs = [abs(float(vertex.co.x)) for vertex in brow.data.vertices]
    min_x = min(xs)
    max_x = max(xs)
    for vertex in brow.data.vertices:
        outward = (abs(float(vertex.co.x)) - min_x) / max(max_x - min_x, 1e-6)
        vertex.co.z += 0.050 * (1.0 - outward) - 0.020 * outward
    brow.data.update()

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_TenderExpression_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_EXPRESSION"
scene["comforting_cat_v5_geometry_attempt"] = "tender_expression_1"
scene["comforting_cat_v5_dominant_defect"] = "toy_gold_neutral_expression"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head mesh and scale",
        "eye positions",
        "muzzle, nose and mouth",
        "robe, body and scarf",
        "limbs and tail",
        "satchel",
        "lighting",
        "review cameras",
    ]
)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)
qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "toy_gold_neutral_expression",
    "changed_materials": {
        "CAT_IrisWarmBrown": "#2D2017",
        "CAT_EyeDarkGlass": "#1B130F",
        "CAT_Pupil": "#060403",
    },
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": structural_qa["errors"],
        "warnings": structural_qa["warnings"],
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_TENDER_EXPRESSION=" + json.dumps(report, ensure_ascii=False))
