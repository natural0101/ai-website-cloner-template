"""Add warm iris rims and inset pupils without changing the eye envelope."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_eye_iris_depth_attempt14"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_tail_pinned_sweep_attempt13.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_eye_iris_depth_attempt14.blend"
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


def set_base_color(material: bpy.types.Material, color: tuple[float, ...]) -> None:
    material.diffuse_color = color
    if not material.use_nodes or material.node_tree is None:
        return
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            node.inputs["Base Color"].default_value = color
            node.inputs["Roughness"].default_value = 0.24
            node.inputs["Metallic"].default_value = 0.0


root = bpy.data.objects["CatV6_Root"]
left_eye = bpy.data.objects["V6_Eye_L"]
dark_pupil_material = left_eye.data.materials[0]
iris_material = dark_pupil_material.copy()
iris_material.name = "V6_EyeIrisWarm_A14"
set_base_color(iris_material, (0.24, 0.075, 0.018, 1.0))

before = {
    "left_eye": bounds(left_eye),
    "right_eye": bounds(bpy.data.objects["V6_Eye_R"]),
}
pupils: list[bpy.types.Object] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    eye = bpy.data.objects[f"V6_Eye_{side}"]
    eye.data.materials.clear()
    eye.data.materials.append(iris_material)

    pupil = eye.copy()
    pupil.data = eye.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(pupil)
    pupil.name = f"V6_Pupil_{side}"
    pupil.data.name = f"V6_Pupil_{side}_InsetMesh"
    pupil.parent = root
    pupil.matrix_parent_inverse = root.matrix_world.inverted()
    for vertex in pupil.data.vertices:
        vertex.co.x *= 0.205 / 0.310
        vertex.co.y *= 0.035 / 0.090
        vertex.co.z *= 0.265 / 0.360
    pupil.data.update()
    pupil.location = (sign * 0.270, -0.548, 2.890)
    pupil.data.materials.clear()
    pupil.data.materials.append(dark_pupil_material)
    pupil["comforting_cat_eye_layer"] = "inset_pupil"
    pupils.append(pupil)

bpy.context.view_layer.update()
after = {
    "left_eye": bounds(bpy.data.objects["V6_Eye_L"]),
    "right_eye": bounds(bpy.data.objects["V6_Eye_R"]),
    "left_pupil": bounds(bpy.data.objects["V6_Pupil_L"]),
    "right_pupil": bounds(bpy.data.objects["V6_Pupil_R"]),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EyeIrisDepth_A14"
scene["comforting_cat_v6_stage"] = "EYE_IRIS_DEPTH"
scene["comforting_cat_v6_attempt"] = 14
scene["comforting_cat_v6_dominant_defect"] = "empty_black_eye_discs"
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
    "stage": "EYE_IRIS_DEPTH",
    "attempt": 14,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "empty_black_eye_discs",
    "before": before,
    "after": after,
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
print("COMFORTING_CAT_V6_EYE_IRIS_DEPTH_A14=" + json.dumps(report, ensure_ascii=False))
