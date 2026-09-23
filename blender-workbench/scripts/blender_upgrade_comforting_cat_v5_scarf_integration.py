"""TRUE_360 costume pass: integrate the oversized stacked scarf with the torso."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_scarf_integration_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_face_layout_attempt1.blend").resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_scarf_integration_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
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


required = [
    "Cat_Root",
    "Cat_Head_Mesh",
    "Cat_BlueRobe",
    "Cat_ScarfWrap",
    "Cat_ScarfUpperFold",
    "Cat_ScarfLowerDrape",
    "CAT_RenderCamera",
]
missing = [name for name in required if name not in bpy.data.objects]
if missing:
    raise RuntimeError(f"Missing costume nodes: {missing}")

scarf_names = ["Cat_ScarfWrap", "Cat_ScarfUpperFold", "Cat_ScarfLowerDrape"]
before = {name: bounds(bpy.data.objects[name]) for name in scarf_names}

# The torus remains the contact anchor, but no longer reads as an inflatable ring.
wrap = bpy.data.objects["Cat_ScarfWrap"]
for vertex in wrap.data.vertices:
    vertex.co.x *= 0.88
    vertex.co.y *= 0.83
    vertex.co.z *= 0.90
wrap.data.update()
wrap.location.z += 0.005


def reshape_front_panel(
    obj: bpy.types.Object,
    x_factor: float,
    y_factor: float,
    y_offset: float,
    z_factor: float,
    z_offset: float,
) -> None:
    center_y = sum(float(vertex.co.y) for vertex in obj.data.vertices) / len(
        obj.data.vertices
    )
    center_z = sum(float(vertex.co.z) for vertex in obj.data.vertices) / len(
        obj.data.vertices
    )
    for vertex in obj.data.vertices:
        vertex.co.x *= x_factor
        vertex.co.y = center_y + (vertex.co.y - center_y) * y_factor + y_offset
        vertex.co.z = center_z + (vertex.co.z - center_z) * z_factor + z_offset
    obj.data.update()


# Collapse the two shelf-like plates into close, soft folds against the chest.
reshape_front_panel(
    bpy.data.objects["Cat_ScarfUpperFold"],
    x_factor=0.86,
    y_factor=0.68,
    y_offset=0.095,
    z_factor=0.90,
    z_offset=-0.005,
)
reshape_front_panel(
    bpy.data.objects["Cat_ScarfLowerDrape"],
    x_factor=0.78,
    y_factor=0.68,
    y_offset=0.105,
    z_factor=0.92,
    z_offset=-0.030,
)

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in scarf_names}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_ScarfIntegration_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "COSTUME_CONTACT_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "scarf_integration_1"
scene["comforting_cat_v5_dominant_defect"] = (
    "oversized_stacked_scarf_detaches_head_from_torso"
)
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head group scale",
        "face layout",
        "head and ear meshes",
        "robe and rear coverage",
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
    scene["comforting_cat_v5_stage"] = "COSTUME_CONTACT_REVIEW"
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
    "stage": "COSTUME_CONTACT_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "oversized_stacked_scarf_detaches_head_from_torso",
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
print("COMFORTING_CAT_V5_SCARF_INTEGRATION=" + json.dumps(report, ensure_ascii=False))
