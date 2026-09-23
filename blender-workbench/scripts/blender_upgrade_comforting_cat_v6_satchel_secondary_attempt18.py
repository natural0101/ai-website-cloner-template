"""Reduce the satchel to a secondary hip accessory while preserving its details."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_satchel_secondary_attempt18"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_scarf_soft_taper_attempt17.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_satchel_secondary_attempt18.blend"
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
    copy.name = f"{obj.name}_SOURCE_A18"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "dominant_oversized_satchel"
    return copy.name


root = bpy.data.objects["CatV6_Root"]
bag_names = [
    "V6_Satchel",
    "V6_SatchelFlap",
    "V6_SatchelHeart",
    "V6_SatchelTasselCord_0",
    "V6_SatchelTasselCord_1",
    "V6_SatchelTassel_0",
    "V6_SatchelTassel_1",
]
before = {name: bounds(bpy.data.objects[name]) for name in bag_names}
preserved_sources = [preserve_copy(bpy.data.objects[name]) for name in bag_names]

scale_x = 0.62 / 0.71
scale_y = 0.17 / 0.20
scale_z = 0.68 / 0.82
anchor = Vector((0.36, -0.545, 1.21))

for name in ("V6_Satchel", "V6_SatchelFlap"):
    obj = bpy.data.objects[name]
    for vertex in obj.data.vertices:
        vertex.co.x *= scale_x
        vertex.co.y *= scale_y
        vertex.co.z *= scale_z
    obj.data.update()

satchel_bevel = bpy.data.objects["V6_Satchel"].modifiers.get(
    "V6_Satchel_RoundedEdges"
)
if satchel_bevel is not None:
    satchel_bevel.width = 0.062
flap_bevel = bpy.data.objects["V6_SatchelFlap"].modifiers.get(
    "V6_SatchelFlap_RoundedEdges"
)
if flap_bevel is not None:
    flap_bevel.width = 0.045

curve_names = [
    "V6_SatchelHeart",
    "V6_SatchelTasselCord_0",
    "V6_SatchelTasselCord_1",
]
for name in curve_names:
    curve_obj = bpy.data.objects[name]
    for spline in curve_obj.data.splines:
        if spline.type == "POLY":
            for point in spline.points:
                point.co.x = anchor.x + (point.co.x - anchor.x) * scale_x
                point.co.z = anchor.z + (point.co.z - anchor.z) * scale_z
        elif spline.type == "BEZIER":
            for point in spline.bezier_points:
                point.co.x = anchor.x + (point.co.x - anchor.x) * scale_x
                point.co.z = anchor.z + (point.co.z - anchor.z) * scale_z

for index in range(2):
    bead = bpy.data.objects[f"V6_SatchelTassel_{index}"]
    bead.location.x = anchor.x + (bead.location.x - anchor.x) * scale_x
    bead.location.z = anchor.z + (bead.location.z - anchor.z) * scale_z
    for vertex in bead.data.vertices:
        vertex.co.x *= scale_x
        vertex.co.z *= scale_z
    bead.data.update()

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in bag_names}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_SatchelSecondary_A18"
scene["comforting_cat_v6_stage"] = "SATCHEL_SECONDARY"
scene["comforting_cat_v6_attempt"] = 18
scene["comforting_cat_v6_dominant_defect"] = "dominant_oversized_satchel"
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
    if not obj.hide_render:
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
    object_names=[
        obj.name
        for obj in export_objects
        if obj.type == "MESH" and not obj.hide_render
    ],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "SATCHEL_SECONDARY",
    "attempt": 18,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "dominant_oversized_satchel",
    "preserved_sources": preserved_sources,
    "scale_factors": [scale_x, scale_y, scale_z],
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
print("COMFORTING_CAT_V6_SATCHEL_SECONDARY_A18=" + json.dumps(report, ensure_ascii=False))
