"""Replace the segmented v6 tail with one continuous tapered plume curve."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_continuous_tail_attempt5"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tapered_ears_tufts_attempt4.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_continuous_tail_attempt5.blend"
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


root = bpy.data.objects["CatV6_Root"]
collection = bpy.data.collections["Comforting_Cat_V6"]
orange = bpy.data.objects["V6_Head"].data.materials[0]
cream = bpy.data.objects["V6_Muzzle_L"].data.materials[0]
source_names = ["V6_TailRoot", "V6_TailMid", "V6_TailEnd", "V6_TailTip"]
before = {name: bounds(bpy.data.objects[name]) for name in source_names}
for name in source_names:
    source = bpy.data.objects[name]
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = f"{name}_SOURCE_SEGMENTED_A5"
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "segmented_bead_tail"

curve = bpy.data.curves.new("V6_TailBase_TaperedBezier", "CURVE")
curve.dimensions = "3D"
curve.resolution_u = 8
curve.bevel_depth = 0.185
curve.bevel_resolution = 6
curve.resolution_u = 12
curve.use_fill_caps = True
spline = curve.splines.new("BEZIER")
path = [
    ((0.43, 0.24, 0.74), 0.78),
    ((0.67, 0.34, 0.48), 1.12),
    ((0.92, 0.43, 0.27), 1.28),
    ((1.14, 0.39, 0.29), 0.92),
]
spline.bezier_points.add(len(path) - 1)
for point, (coordinate, radius) in zip(spline.bezier_points, path):
    point.co = coordinate
    point.radius = radius
    point.handle_left_type = "AUTO"
    point.handle_right_type = "AUTO"
tail = bpy.data.objects.new("V6_TailBase", curve)
collection.objects.link(tail)
tail.parent = root
tail.matrix_parent_inverse = root.matrix_world.inverted()
tail.data.materials.append(orange)
tail["comforting_cat_role"] = "continuous_tapered_tail_plume"

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=48,
    ring_count=32,
    location=(1.19, 0.40, 0.29),
)
tip = bpy.context.object
tip.name = "V6_TailTip"
tip.scale = (0.22, 0.20, 0.18)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for linked in list(tip.users_collection):
    linked.objects.unlink(tip)
collection.objects.link(tip)
tip.parent = root
tip.matrix_parent_inverse = root.matrix_world.inverted()
tip.data.materials.append(cream)
for polygon in tip.data.polygons:
    polygon.use_smooth = True
tip["comforting_cat_role"] = "overlapping_cream_tail_tip"

bpy.context.view_layer.update()
after = {
    "V6_TailBase": bounds(tail),
    "V6_TailTip": bounds(tip),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ContinuousTail_A5"
scene["comforting_cat_v6_stage"] = "CONTINUOUS_TAIL"
scene["comforting_cat_v6_attempt"] = 5
scene["comforting_cat_v6_dominant_defect"] = "segmented_bead_tail"
scene["comforting_cat_v6_preserved_sources"] = json.dumps(
    [f"{name}_SOURCE_SEGMENTED_A5" for name in source_names]
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
    "stage": "CONTINUOUS_TAIL",
    "attempt": 5,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "segmented_bead_tail",
    "path": [{"coordinate": list(point), "radius": radius} for point, radius in path],
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
print("COMFORTING_CAT_V6_CONTINUOUS_TAIL_A5=" + json.dumps(report, ensure_ascii=False))
