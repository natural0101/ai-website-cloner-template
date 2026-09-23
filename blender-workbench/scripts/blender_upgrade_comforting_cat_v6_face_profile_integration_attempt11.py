"""Integrate v6 facial parts into the head without changing the front silhouette."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_face_profile_integration_attempt11"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_scarf_compact_wrapped_attempt10.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_face_profile_integration_attempt11.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


def preserve_copy(obj: bpy.types.Object) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A11"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "floating_face_components"
    return copy.name


def scale_mesh_axes(
    obj: bpy.types.Object,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    scale_z: float = 1.0,
) -> None:
    for vertex in obj.data.vertices:
        vertex.co.x *= scale_x
        vertex.co.y *= scale_y
        vertex.co.z *= scale_z
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
face_names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
    "V6_Nose",
    "V6_Eyebrow_L",
    "V6_Eyebrow_R",
]
before = {name: bounds(bpy.data.objects[name]) for name in face_names}
preserved_sources = [preserve_copy(bpy.data.objects[name]) for name in face_names]

for side, sign in (("L", -1.0), ("R", 1.0)):
    eye = bpy.data.objects[f"V6_Eye_{side}"]
    scale_mesh_axes(eye, scale_y=0.065 / 0.140)
    eye.location = (sign * 0.270, -0.470, 2.900)
    eye.rotation_euler = (0.0, 0.0, math.radians(-sign * 8.0))

    highlight = bpy.data.objects[f"V6_EyeHighlight_{side}"]
    scale_mesh_axes(
        highlight,
        scale_x=0.052 / 0.065,
        scale_y=0.020 / 0.035,
        scale_z=0.070 / 0.085,
    )
    highlight.location = (sign * 0.220, -0.535, 2.990)
    highlight.rotation_euler = eye.rotation_euler.copy()

    muzzle = bpy.data.objects[f"V6_Muzzle_{side}"]
    scale_mesh_axes(
        muzzle,
        scale_y=0.210 / 0.180,
        scale_z=0.220 / 0.230,
    )
    muzzle.location = (sign * 0.145, -0.525, 2.580)

nose = bpy.data.objects["V6_Nose"]
scale_mesh_axes(
    nose,
    scale_x=0.110 / 0.130,
    scale_y=0.060 / 0.080,
    scale_z=0.085 / 0.100,
)
nose.location = (0.0, -0.648, 2.640)

brow_points = {
    "V6_Eyebrow_L": [
        (-0.42, -0.335, 3.11),
        (-0.28, -0.345, 3.16),
        (-0.12, -0.350, 3.20),
    ],
    "V6_Eyebrow_R": [
        (0.12, -0.350, 3.20),
        (0.28, -0.345, 3.16),
        (0.42, -0.335, 3.11),
    ],
}
for name, coordinates in brow_points.items():
    brow = bpy.data.objects[name]
    brow.data.bevel_depth = 0.013
    points = brow.data.splines[0].bezier_points
    for point, coordinate in zip(points, coordinates):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in face_names}
profile_metrics = {
    "eye_outer_surface_y": round(
        min(after["V6_Eye_L"]["min"][1], after["V6_Eye_R"]["min"][1]), 5
    ),
    "muzzle_front_y": round(
        min(after["V6_Muzzle_L"]["min"][1], after["V6_Muzzle_R"]["min"][1]), 5
    ),
    "nose_front_y": round(after["V6_Nose"]["min"][1], 5),
}
profile_metrics["muzzle_ahead_of_eye"] = round(
    profile_metrics["eye_outer_surface_y"] - profile_metrics["muzzle_front_y"], 5
)
profile_metrics["nose_ahead_of_muzzle"] = round(
    profile_metrics["muzzle_front_y"] - profile_metrics["nose_front_y"], 5
)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FaceProfileIntegration_A11"
scene["comforting_cat_v6_stage"] = "FACE_PROFILE_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 11
scene["comforting_cat_v6_dominant_defect"] = "floating_face_components"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render(
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


camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 3.08), (0.0, 0.0, 1.88), 4.20)
render(camera, "03_front_3q", (4.0, -7.4, 3.35), (0.0, 0.02, 1.84), 4.30)
render(camera, "04_side", (8.4, -0.35, 3.08), (0.0, 0.08, 1.82), 4.30)
render(camera, "05_back", (0.0, 8.4, 3.08), (0.0, 0.12, 1.82), 4.30)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

export_objects = descendants(root)
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
qa = runpy.run_path(str(SCENE_QA_PATH))["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "FACE_PROFILE_INTEGRATION",
    "attempt": 11,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "floating_face_components",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "profile_metrics": profile_metrics,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(qa["errors"])),
        "warnings": sorted(set(qa["warnings"])),
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
scene["comforting_cat_v6_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V6_FACE_PROFILE_INTEGRATION_A11=" + json.dumps(report, ensure_ascii=False))
