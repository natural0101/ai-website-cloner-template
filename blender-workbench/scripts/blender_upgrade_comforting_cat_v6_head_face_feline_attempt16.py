"""Reshape the v6 head and unify the muzzle into a more feline face."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_head_face_feline_attempt16"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_eye_layers_flush_attempt15.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_face_feline_attempt16.blend"
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


def preserve_copy(obj: bpy.types.Object, reason: str) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A16"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = reason
    return copy.name


def piecewise_scale(z_normalized: float) -> float:
    knots = [
        (-1.00, 0.78),
        (-0.58, 0.88),
        (-0.22, 1.00),
        (0.22, 1.03),
        (0.62, 0.99),
        (1.00, 0.91),
    ]
    if z_normalized <= knots[0][0]:
        return knots[0][1]
    if z_normalized >= knots[-1][0]:
        return knots[-1][1]
    for (z0, value0), (z1, value1) in zip(knots, knots[1:]):
        if z0 <= z_normalized <= z1:
            t = (z_normalized - z0) / (z1 - z0)
            t = t * t * (3.0 - 2.0 * t)
            return value0 * (1.0 - t) + value1 * t
    return 1.0


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
face_names = [
    "V6_Head",
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
    "V6_Nose",
]
before = {name: bounds(bpy.data.objects[name]) for name in face_names}
preserved_sources = [
    preserve_copy(bpy.data.objects[name], "capsule_head_and_split_muzzle")
    for name in face_names
]

local_z_extent = max(abs(vertex.co.z) for vertex in head.data.vertices)
for vertex in head.data.vertices:
    z_normalized = vertex.co.z / local_z_extent
    vertex.co.x *= piecewise_scale(z_normalized)
    vertex.co.z *= 1.015
head.data.update()

for side, sign in (("L", -1.0), ("R", 1.0)):
    eye = bpy.data.objects[f"V6_Eye_{side}"]
    for vertex in eye.data.vertices:
        vertex.co.x *= 0.90
        vertex.co.z *= 0.82
    eye.data.update()
    eye.location = (sign * 0.255, -0.490, 2.890)

    pupil = bpy.data.objects[f"V6_Pupil_{side}"]
    for vertex in pupil.data.vertices:
        vertex.co.x *= 0.88
        vertex.co.z *= 0.82
    pupil.data.update()
    pupil.location = (sign * 0.255, -0.540, 2.885)

    highlight = bpy.data.objects[f"V6_EyeHighlight_{side}"]
    for vertex in highlight.data.vertices:
        vertex.co.x *= 0.85
        vertex.co.z *= 0.85
    highlight.data.update()
    highlight.location = (sign * 0.218, -0.548, 2.955)

left_muzzle = bpy.data.objects["V6_Muzzle_L"]
muzzle_material = left_muzzle.data.materials[0]
unified_muzzle = left_muzzle.copy()
unified_muzzle.data = left_muzzle.data.copy()
bpy.data.collections["Comforting_Cat_V6"].objects.link(unified_muzzle)
unified_muzzle.name = "V6_MuzzleUnified"
unified_muzzle.data.name = "V6_MuzzleUnified_FelineMesh"
unified_muzzle.parent = root
unified_muzzle.matrix_parent_inverse = root.matrix_world.inverted()
for vertex in unified_muzzle.data.vertices:
    vertex.co.x *= 0.760 / 0.340
    vertex.co.y *= 0.200 / 0.210
    vertex.co.z *= 0.260 / 0.220
unified_muzzle.data.update()
unified_muzzle.location = (0.0, -0.530, 2.565)
unified_muzzle.data.materials.clear()
unified_muzzle.data.materials.append(muzzle_material)

for side in ("L", "R"):
    muzzle = bpy.data.objects[f"V6_Muzzle_{side}"]
    muzzle.parent = None
    muzzle.hide_render = True
    muzzle.hide_set(True)
    muzzle.name = f"V6_Muzzle_{side}_REPLACED_A16"
    muzzle["comforting_cat_preserved_source"] = True

nose = bpy.data.objects["V6_Nose"]
nose.location.z = 2.605

for name in [
    "V6_CheekTuft_L_0",
    "V6_CheekTuft_L_1",
    "V6_CheekTuft_R_0",
    "V6_CheekTuft_R_1",
]:
    tuft = bpy.data.objects.get(name)
    if tuft is not None:
        tuft.hide_render = True
        tuft.hide_set(True)
        tuft["comforting_cat_preserved_source"] = True
        tuft["comforting_cat_rejection_reason"] = "detached_diamond_tuft"

bpy.context.view_layer.update()
after = {
    "head": bounds(head),
    "left_eye": bounds(bpy.data.objects["V6_Eye_L"]),
    "right_eye": bounds(bpy.data.objects["V6_Eye_R"]),
    "unified_muzzle": bounds(unified_muzzle),
    "nose": bounds(nose),
}
head_width = after["head"]["dimensions"][0]
head_height = after["head"]["dimensions"][2]
metrics = {
    "head_width_height": round(head_width / head_height, 5),
    "eye_center_separation_over_head_width": round((0.510 / head_width), 5),
    "single_eye_width_over_head_width": round(
        after["left_eye"]["dimensions"][0] / head_width, 5
    ),
    "single_eye_height_over_head_height": round(
        after["left_eye"]["dimensions"][2] / head_height, 5
    ),
    "muzzle_width_over_head_width": round(
        after["unified_muzzle"]["dimensions"][0] / head_width, 5
    ),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadFaceFeline_A16"
scene["comforting_cat_v6_stage"] = "HEAD_FACE_FELINE"
scene["comforting_cat_v6_attempt"] = 16
scene["comforting_cat_v6_dominant_defect"] = "capsule_head_split_muzzle"
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
    "stage": "HEAD_FACE_FELINE",
    "attempt": 16,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "capsule_head_split_muzzle",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
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
print("COMFORTING_CAT_V6_HEAD_FACE_FELINE_A16=" + json.dumps(report, ensure_ascii=False))
