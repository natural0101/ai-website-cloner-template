"""Replace the smiling U mouth with a small feline philtrum and worried arch."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_mouth_feline_worry_attempt21"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_ears_feline_volume_attempt20.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_mouth_feline_worry_attempt21.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def curve_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
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


def bezier_curve(
    name: str,
    coordinates: list[tuple[float, float, float]],
    bevel_depth: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 3
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(coordinates) - 1)
    for point, coordinate in zip(spline.bezier_points, coordinates):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    return obj


root = bpy.data.objects["CatV6_Root"]
mouth = bpy.data.objects["V6_Mouth"]
before = {"mouth": curve_bounds(mouth)}
source = mouth.copy()
source.data = mouth.data.copy()
bpy.data.collections["Comforting_Cat_V6"].objects.link(source)
source.parent = None
source.hide_render = True
source.hide_set(True)
source.name = "V6_Mouth_SOURCE_SMILE_A21"
source["comforting_cat_preserved_source"] = True
source["comforting_cat_rejection_reason"] = "smiling_u_expression"

coordinates = [
    (-0.10, -0.642, 2.480),
    (0.00, -0.648, 2.515),
    (0.10, -0.642, 2.480),
]
mouth.data.bevel_depth = 0.009
for point, coordinate in zip(
    mouth.data.splines[0].bezier_points,
    coordinates,
):
    point.co = coordinate
    point.handle_left_type = "AUTO"
    point.handle_right_type = "AUTO"

material = mouth.data.materials[0]
philtrum = bezier_curve(
    "V6_Philtrum",
    [
        (0.0, -0.648, 2.560),
        (0.0, -0.650, 2.535),
        (0.0, -0.648, 2.515),
    ],
    0.007,
    material,
)

bpy.context.view_layer.update()
after = {
    "mouth": curve_bounds(mouth),
    "philtrum": curve_bounds(philtrum),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_MouthFelineWorry_A21"
scene["comforting_cat_v6_stage"] = "MOUTH_FELINE_WORRY"
scene["comforting_cat_v6_attempt"] = 21
scene["comforting_cat_v6_dominant_defect"] = "smiling_u_expression"
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
    "stage": "MOUTH_FELINE_WORRY",
    "attempt": 21,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "smiling_u_expression",
    "preserved_source": source.name,
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
print("COMFORTING_CAT_V6_MOUTH_FELINE_WORRY_A21=" + json.dumps(report, ensure_ascii=False))
