"""Soften the scarf by tapering side edges and removing extra plate layers."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_soft_taper_attempt17"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_head_face_feline_attempt16.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_soft_taper_attempt17.blend"
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
    copy.name = f"{obj.name}_SOURCE_A17"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "rigid_armored_scarf"
    return copy.name


root = bpy.data.objects["CatV6_Root"]
scarf_names = [
    "V6_Scarf_FrontDrape",
    "V6_Scarf_FrontFold_Upper",
    "V6_Scarf_BackDrape",
    "V6_ScarfWrap_Upper",
    "V6_ScarfWrap_Lower",
]
before = {name: bounds(bpy.data.objects[name]) for name in scarf_names}
preserved_sources = [preserve_copy(bpy.data.objects[name]) for name in scarf_names]

front = bpy.data.objects["V6_Scarf_FrontDrape"]
if len(front.data.vertices) != 27:
    raise RuntimeError(f"Expected 27 scarf vertices, got {len(front.data.vertices)}")
bottom_z = [2.23, 2.16, 2.07, 1.98, 1.93, 1.90, 1.96, 2.09, 2.22]
for index, z_value in enumerate(bottom_z, start=18):
    front.data.vertices[index].co.z = z_value
middle_y_offsets = [0.000, -0.010, 0.008, -0.012, 0.010, -0.008, 0.012, -0.006, 0.000]
for index, offset in enumerate(middle_y_offsets, start=9):
    front.data.vertices[index].co.y += offset
front.data.update()
for polygon in front.data.polygons:
    polygon.use_smooth = True
thickness = front.modifiers.get("V6_Scarf_FrontDrape_Thickness")
if thickness is not None:
    thickness.thickness = 0.045

for name in ("V6_Scarf_FrontFold_Upper", "V6_Scarf_BackDrape"):
    obj = bpy.data.objects[name]
    obj.hide_render = True
    obj.hide_set(True)
    obj["comforting_cat_preserved_source"] = True
    obj["comforting_cat_rejection_reason"] = "extra_scarf_plate_layer"

for name in ("V6_ScarfWrap_Upper", "V6_ScarfWrap_Lower"):
    wrap = bpy.data.objects[name]
    wrap_bounds = bounds(wrap)
    center_z = (wrap_bounds["min"][2] + wrap_bounds["max"][2]) * 0.5
    inverse = wrap.matrix_world.inverted()
    for vertex in wrap.data.vertices:
        world = wrap.matrix_world @ vertex.co
        world.z = center_z + (world.z - center_z) * 0.78
        vertex.co = inverse @ world
    wrap.data.update()
    for polygon in wrap.data.polygons:
        polygon.use_smooth = True

bpy.context.view_layer.update()
after = {
    "front_drape": bounds(front),
    "upper_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Upper"]),
    "lower_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Lower"]),
    "hidden_layers": [
        "V6_Scarf_FrontFold_Upper",
        "V6_Scarf_BackDrape",
    ],
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfSoftTaper_A17"
scene["comforting_cat_v6_stage"] = "SCARF_SOFT_TAPER"
scene["comforting_cat_v6_attempt"] = 17
scene["comforting_cat_v6_dominant_defect"] = "rigid_armored_scarf"
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
    "stage": "SCARF_SOFT_TAPER",
    "attempt": 17,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_armored_scarf",
    "preserved_sources": preserved_sources,
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
print("COMFORTING_CAT_V6_SCARF_SOFT_TAPER_A17=" + json.dumps(report, ensure_ascii=False))
