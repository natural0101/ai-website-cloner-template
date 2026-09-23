"""TRUE_360 face pass: open the compressed eye layout and integrate the muzzle."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_face_layout_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_costume_silhouette_attempt2.blend"
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_face_layout_attempt1.blend"
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


def move_world(
    obj: bpy.types.Object,
    offset: tuple[float, float, float],
) -> None:
    set_world_location(
        obj,
        tuple(
            float(obj.matrix_world.translation[index]) + offset[index]
            for index in range(3)
        ),
    )


def object_record(name: str) -> dict[str, object]:
    obj = bpy.data.objects[name]
    return {
        "location_world": [
            round(float(value), 6) for value in obj.matrix_world.translation
        ],
        "dimensions_world": [
            round(float(value), 6) for value in obj.dimensions
        ],
    }


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
    "Cat_Eyebrow_L",
    "Cat_Eyebrow_R",
    "Cat_Muzzle_L",
    "Cat_Muzzle_R",
    "Cat_Nose",
    "Cat_MouthStem",
    "Cat_Mouth_L",
    "Cat_Mouth_R",
    "CAT_RenderCamera",
]
missing = [name for name in required if name not in bpy.data.objects]
if missing:
    raise RuntimeError(f"Missing face nodes: {missing}")

tracked = [
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Iris_L",
    "Cat_Iris_R",
    "Cat_Pupil_L",
    "Cat_Pupil_R",
    "Cat_Muzzle_L",
    "Cat_Muzzle_R",
    "Cat_Nose",
]
before = {name: object_record(name) for name in tracked}

# Keep eye size; correct the compressed spacing and lower the gaze slightly.
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    eye_x = side * 0.325
    set_world_location(
        bpy.data.objects[f"Cat_Eye_{suffix}"],
        (eye_x, -0.572, 3.025),
    )
    set_world_location(
        bpy.data.objects[f"Cat_Iris_{suffix}"],
        (eye_x, -0.592, 3.020),
    )
    set_world_location(
        bpy.data.objects[f"Cat_Pupil_{suffix}"],
        (eye_x, -0.600, 3.020),
    )
    set_world_location(
        bpy.data.objects[f"Cat_EyeHighlight_{suffix}"],
        (side * 0.290, -0.607, 3.095),
    )

    # Broad, low muzzle puffs overlap into one soft muzzle field.
    muzzle = bpy.data.objects[f"Cat_Muzzle_{suffix}"]
    for vertex in muzzle.data.vertices:
        vertex.co.x *= 1.25
        vertex.co.y *= 0.82
        vertex.co.z *= 0.88
    muzzle.data.update()
    set_world_location(muzzle, (side * 0.170, -0.590, 2.740))

    # Preserve the concerned brow gesture while aligning it with the eyes.
    move_world(
        bpy.data.objects[f"Cat_Eyebrow_{suffix}"],
        (side * 0.100, 0.018, -0.045),
    )

# Lower and partially embed the central nose/mouth instead of leaving a badge.
set_world_location(bpy.data.objects["Cat_Nose"], (0.0, -0.700, 2.790))
for name in ("Cat_MouthStem", "Cat_Mouth_L", "Cat_Mouth_R"):
    move_world(bpy.data.objects[name], (0.0, 0.040, -0.095))

# Turn the obvious W-smile into a subtle worried mouth by dropping its corners.
for name in ("Cat_Mouth_L", "Cat_Mouth_R"):
    obj = bpy.data.objects[name]
    max_x = max(abs(float(vertex.co.x)) for vertex in obj.data.vertices)
    for vertex in obj.data.vertices:
        edge_weight = min(1.0, abs(float(vertex.co.x)) / max(max_x, 1e-6))
        vertex.co.z -= 0.070 * edge_weight
    obj.data.update()

# Keep whiskers attached to the lowered muzzle but otherwise unchanged.
for side in ("L", "R"):
    for index in range(3):
        move_world(
            bpy.data.objects[f"Cat_Whisker_{side}_{index}"],
            (0.0, 0.035, -0.080),
        )

bpy.context.view_layer.update()
after = {name: object_record(name) for name in tracked}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_FaceLayout_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_LAYOUT_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "face_layout_1"
scene["comforting_cat_v5_dominant_defect"] = (
    "compressed_surface_mounted_face_cluster"
)
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head group scale",
        "head and ear meshes",
        "robe and rear coverage",
        "scarf geometry",
        "arms and legs",
        "satchel and strap",
        "tail",
        "materials",
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
    scene["comforting_cat_v5_stage"] = "FACE_LAYOUT_REVIEW"
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
render_view(
    camera,
    "02_material_front",
    (0.0, -8.6, 3.15),
    (0.0, -0.04, 2.03),
    4.65,
)
render_view(
    camera,
    "03_front_3q",
    (4.0, -7.4, 3.45),
    (0.0, -0.02, 1.98),
    4.75,
)
render_view(
    camera,
    "04_side",
    (8.4, -0.35, 3.15),
    (0.0, 0.0, 1.92),
    4.75,
)
render_view(
    camera,
    "05_back",
    (0.0, 8.4, 3.15),
    (0.0, 0.04, 1.92),
    4.75,
)

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
    "stage": "FACE_LAYOUT_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "compressed_surface_mounted_face_cluster",
    "before": before,
    "after": after,
    "eye_center_separation_world": round(
        abs(
            float(
                bpy.data.objects["Cat_Eye_R"].matrix_world.translation.x
                - bpy.data.objects["Cat_Eye_L"].matrix_world.translation.x
            )
        ),
        6,
    ),
    "head_width_world": round(
        float(bpy.data.objects["Cat_Head_Mesh"].dimensions.x),
        6,
    ),
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
print("COMFORTING_CAT_V5_FACE_LAYOUT=" + json.dumps(report, ensure_ascii=False))
