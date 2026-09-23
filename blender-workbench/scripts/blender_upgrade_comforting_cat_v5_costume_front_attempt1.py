"""Turn the cyan chest patch into a wider muted linen tunic panel."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_costume_front_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_leg_paw_grounding_attempt1.blend"
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_costume_front_attempt1.blend"
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
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


inset = bpy.data.objects["Cat_RobeFrontInset"]
before_bounds = bounds(inset)
before_materials = [material.name for material in inset.data.materials]

inverse = inset.matrix_world.inverted()
for vertex in inset.data.vertices:
    point = inset.matrix_world @ vertex.co
    point.x *= 1.16
    vertex.co = inverse @ point
inset.data.update()

material = bpy.data.materials.get("CAT_MutedGrayLinen")
if material is None:
    material = bpy.data.materials.new("CAT_MutedGrayLinen")
material.use_nodes = True
principled = material.node_tree.nodes.get("Principled BSDF")
if principled is None:
    raise RuntimeError("Principled BSDF missing from CAT_MutedGrayLinen")
principled.inputs["Base Color"].default_value = (0.16, 0.19, 0.19, 1.0)
principled.inputs["Roughness"].default_value = 0.88
principled.inputs["Metallic"].default_value = 0.0
if "Sheen Weight" in principled.inputs:
    principled.inputs["Sheen Weight"].default_value = 0.10
inset.data.materials.clear()
inset.data.materials.append(material)

bpy.context.view_layer.update()
after_bounds = bounds(inset)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_CostumeFront_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "COSTUME_FRONT_LAYERING"
scene["comforting_cat_v5_geometry_attempt"] = "costume_front_1"
scene["comforting_cat_v5_dominant_defect"] = "cyan_narrow_chest_patch"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "overall proportions",
        "head, ears and face",
        "robe shell and scarf",
        "limbs and paw grounding",
        "satchel and tail",
        "lighting and cameras",
    ]
)


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


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
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
qa = runpy.run_path(str(SCENE_QA_PATH))["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "COSTUME_FRONT_LAYERING",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "cyan_narrow_chest_patch",
    "before_bounds": before_bounds,
    "after_bounds": after_bounds,
    "before_materials": before_materials,
    "after_materials": [material.name],
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
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_COSTUME_FRONT_A1=" + json.dumps(report, ensure_ascii=False))
