"""TRUE_360 face pass: seat the eyes in the skull and add soft upper lids."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_eye_integration_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_scarf_integration_attempt1.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_eye_integration_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def set_world_location(
    obj: bpy.types.Object,
    location: tuple[float, float, float],
) -> None:
    matrix = obj.matrix_world.copy()
    matrix.translation = Vector(location)
    obj.matrix_world = matrix


required = [
    "Cat_Root",
    "Cat_Head",
    "Cat_Head_Mesh",
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Iris_L",
    "Cat_Iris_R",
    "Cat_Pupil_L",
    "Cat_Pupil_R",
    "Cat_EyeHighlight_L",
    "Cat_EyeHighlight_R",
    "CAT_RenderCamera",
]
missing = [name for name in required if name not in bpy.data.objects]
if missing:
    raise RuntimeError(f"Missing eye nodes: {missing}")
if any(name in bpy.data.objects for name in ("Cat_UpperLid_L", "Cat_UpperLid_R")):
    raise RuntimeError("Upper lids already exist in this source")

before_depths: dict[str, float] = {}
after_depths: dict[str, float] = {}
head_root = bpy.data.objects["Cat_Head"]
fur_material = bpy.data.objects["Cat_Head_Mesh"].data.materials[0]

for side, suffix in ((-1.0, "L"), (1.0, "R")):
    eye = bpy.data.objects[f"Cat_Eye_{suffix}"]
    iris = bpy.data.objects[f"Cat_Iris_{suffix}"]
    pupil = bpy.data.objects[f"Cat_Pupil_{suffix}"]
    highlight = bpy.data.objects[f"Cat_EyeHighlight_{suffix}"]
    for obj in (eye, iris, pupil, highlight):
        before_depths[obj.name] = round(
            float(obj.matrix_world.translation.y),
            6,
        )

    # Preserve x/z layout and dimensions; only reduce the surface-mounted stack.
    set_world_location(eye, (side * 0.325, -0.548, 3.025))
    set_world_location(iris, (side * 0.325, -0.570, 3.020))
    set_world_location(pupil, (side * 0.325, -0.579, 3.020))
    set_world_location(highlight, (side * 0.290, -0.585, 3.095))

    for obj in (eye, iris, pupil, highlight):
        after_depths[obj.name] = round(
            float(obj.matrix_world.translation.y),
            6,
        )

    # A shallow fur-colored ellipsoid masks the eye top and creates a soft lid.
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40,
        ring_count=24,
        location=(side * 0.325, -0.586, 3.145),
        scale=(0.155, 0.025, 0.083),
    )
    lid = bpy.context.object
    lid.name = f"Cat_UpperLid_{suffix}"
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    lid.rotation_euler.y = side * 0.12
    lid.data.materials.append(fur_material)
    for polygon in lid.data.polygons:
        polygon.use_smooth = True
    world_matrix = lid.matrix_world.copy()
    lid.parent = head_root
    lid.matrix_world = world_matrix

bpy.context.view_layer.update()

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_EyeIntegration_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_ORBIT_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "eye_integration_1"
scene["comforting_cat_v5_dominant_defect"] = "surface_mounted_disc_eyes"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head group scale",
        "eye x and z coordinates",
        "eye dimensions",
        "muzzle and mouth layout",
        "head and ear meshes",
        "robe and rear coverage",
        "scarf integration",
        "arms and legs",
        "satchel and strap",
        "tail",
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
    scene["comforting_cat_v5_stage"] = "FACE_ORBIT_REVIEW"
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
    obj.hide_render = False
    obj.hide_viewport = False
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
    "stage": "FACE_ORBIT_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "surface_mounted_disc_eyes",
    "eye_depths_before": before_depths,
    "eye_depths_after": after_depths,
    "new_parts": ["Cat_UpperLid_L", "Cat_UpperLid_R"],
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
print("COMFORTING_CAT_V5_EYE_INTEGRATION=" + json.dumps(report, ensure_ascii=False))
