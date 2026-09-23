"""TRUE_360 head pass: reduce helmet depth and taper the crown."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_head_silhouette_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_satchel_hip_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_head_silhouette_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def move_world(obj: bpy.types.Object, offset: tuple[float, float, float]) -> None:
    matrix = obj.matrix_world.copy()
    matrix.translation += Vector(offset)
    obj.matrix_world = matrix


head = bpy.data.objects["Cat_Head_Mesh"]
before_dimensions = [round(float(value), 6) for value in head.dimensions]
z_extent = max(abs(float(vertex.co.z)) for vertex in head.data.vertices)
for vertex in head.data.vertices:
    normalized_z = float(vertex.co.z) / max(z_extent, 1e-6)
    crown = max(0.0, min(1.0, (normalized_z - 0.12) / 0.88))
    vertex.co.x *= 1.0 - 0.085 * crown
    vertex.co.y *= 0.84
    vertex.co.z *= 1.02
head.data.update()

for suffix in ("L", "R"):
    for prefix in ("Cat_Ear_", "Cat_InnerEar_"):
        ear = bpy.data.objects[f"{prefix}{suffix}"]
        for vertex in ear.data.vertices:
            vertex.co.x *= 0.88
            vertex.co.y *= 0.84
            vertex.co.z *= 0.88
        ear.data.update()

face_names = [
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Iris_L",
    "Cat_Iris_R",
    "Cat_Pupil_L",
    "Cat_Pupil_R",
    "Cat_EyeHighlight_L",
    "Cat_EyeHighlight_R",
    "Cat_Eyebrow_L",
    "Cat_Eyebrow_R",
    "Cat_MuzzleUnified",
    "Cat_Nose",
    "Cat_MouthStem",
    "Cat_Mouth_L",
    "Cat_Mouth_R",
    "Cat_ForeheadStripe_0",
    "Cat_ForeheadStripe_1",
    "Cat_ForeheadStripe_2",
]
face_names.extend(
    f"Cat_Whisker_{side}_{index}"
    for side in ("L", "R")
    for index in range(3)
)
for name in face_names:
    move_world(bpy.data.objects[name], (0.0, 0.070, 0.0))

# Sparse radial stubble was a strong helmet cue; preserve it but do not render it.
fur_strands = bpy.data.objects.get("Cat_Head_FurStrands")
if fur_strands is not None:
    fur_strands.hide_render = True

bpy.context.view_layer.update()
after_dimensions = [round(float(value), 6) for value in head.dimensions]

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_HeadSilhouette_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "SILHOUETTE_HEAD_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "head_silhouette_1"
scene["comforting_cat_v5_dominant_defect"] = "smooth_deep_helmet_head"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "face x and z layout",
        "face material and expression",
        "robe, body and scarf",
        "limbs and tail",
        "satchel",
        "lighting",
        "review cameras",
    ]
)


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
    "dominant_defect": "smooth_deep_helmet_head",
    "head_dimensions_before": before_dimensions,
    "head_dimensions_after": after_dimensions,
    "face_y_offset": 0.070,
    "fur_strands_rendered": False,
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
print("COMFORTING_CAT_V5_HEAD_SILHOUETTE=" + json.dumps(report, ensure_ascii=False))
