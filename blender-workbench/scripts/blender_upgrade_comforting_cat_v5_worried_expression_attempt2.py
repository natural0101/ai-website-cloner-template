"""Face pass: reduce the toy smile and build a quieter worried expression."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_worried_expression_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_cloak_leg_blockout_attempt3.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_worried_expression_attempt2.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


tracked_names = [
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Iris_L",
    "Cat_Iris_R",
    "Cat_Pupil_L",
    "Cat_Pupil_R",
    "Cat_Eyebrow_L",
    "Cat_Eyebrow_R",
    "Cat_Mouth_L",
    "Cat_Mouth_R",
    "Cat_MouthStem",
]
before = {name: world_bounds(bpy.data.objects[name]) for name in tracked_names}

# Reduce the startled circular opening while retaining the dark tender eyes.
for suffix in ("L", "R"):
    for name, z_factor in (
        (f"Cat_Eye_{suffix}", 0.94),
        (f"Cat_Iris_{suffix}", 0.94),
        (f"Cat_Pupil_{suffix}", 0.96),
    ):
        obj = bpy.data.objects[name]
        for vertex in obj.data.vertices:
            vertex.co.z *= z_factor
        obj.data.update()

    for name in (
        f"Cat_Eye_{suffix}",
        f"Cat_Iris_{suffix}",
        f"Cat_Pupil_{suffix}",
        f"Cat_EyeHighlight_{suffix}",
    ):
        obj = bpy.data.objects[name]
        matrix = obj.matrix_world.copy()
        matrix.translation += Vector((0.0, 0.012, -0.006))
        obj.matrix_world = matrix

# Raise the inner brow ends and lower the outer ends to create the target's
# worried tenderness without adding detached lid geometry.
for suffix in ("L", "R"):
    brow = bpy.data.objects[f"Cat_Eyebrow_{suffix}"]
    points = [brow.matrix_world @ vertex.co for vertex in brow.data.vertices]
    abs_x = [abs(point.x) for point in points]
    min_x = min(abs_x)
    max_x = max(abs_x)
    inverse = brow.matrix_world.inverted()
    for vertex in brow.data.vertices:
        point = brow.matrix_world @ vertex.co
        outward = (abs(point.x) - min_x) / max(max_x - min_x, 1e-6)
        point.z += 0.045 * (1.0 - outward) - 0.012 * outward
        point.y -= 0.006
        vertex.co = inverse @ point
    brow.data.update()

# Compress both mouth arcs toward the nose and flatten their vertical swing.
# This removes the obvious smile while preserving the original topology.
for name in ("Cat_Mouth_L", "Cat_Mouth_R"):
    mouth = bpy.data.objects[name]
    points = [mouth.matrix_world @ vertex.co for vertex in mouth.data.vertices]
    center_z = sum(point.z for point in points) / len(points)
    inverse = mouth.matrix_world.inverted()
    for vertex in mouth.data.vertices:
        point = mouth.matrix_world @ vertex.co
        point.x *= 0.70
        point.z = center_z + (point.z - center_z) * 0.38
        vertex.co = inverse @ point
    mouth.data.update()

stem = bpy.data.objects["Cat_MouthStem"]
for vertex in stem.data.vertices:
    vertex.co.z *= 0.82
stem.data.update()

bpy.context.view_layer.update()
after = {name: world_bounds(bpy.data.objects[name]) for name in tracked_names}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_WorriedExpression_A2"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_EXPRESSION"
scene["comforting_cat_v5_geometry_attempt"] = "worried_expression_2"
scene["comforting_cat_v5_dominant_defect"] = "neutral_toy_smile_and_startled_eyes"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head and ear geometry",
        "eye x separation",
        "muzzle and nose",
        "whiskers",
        "costume and scarf",
        "limbs and feet",
        "satchel",
        "tail",
        "materials",
        "lighting and cameras",
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
    obj.hide_set(False)
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
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "FACE_EXPRESSION",
    "attempt": 2,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "neutral_toy_smile_and_startled_eyes",
    "before": before,
    "after": after,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
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
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_WORRIED_EXPRESSION_A2=" + json.dumps(report, ensure_ascii=False))
