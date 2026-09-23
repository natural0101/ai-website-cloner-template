"""Reveal the ears by lowering and narrowing only the upper head crown."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_crown_ear_emergence_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_arm_sleeve_integration_attempt2.blend"
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_crown_ear_emergence_attempt1.blend"
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


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


tracked_names = [
    "Cat_Head_Mesh",
    "Cat_Ear_L",
    "Cat_InnerEar_L",
    "Cat_Ear_R",
    "Cat_InnerEar_R",
]
before = {name: bounds(bpy.data.objects[name]) for name in tracked_names}

head = bpy.data.objects["Cat_Head_Mesh"]
points = [head.matrix_world @ vertex.co for vertex in head.data.vertices]
z_min = min(point.z for point in points)
z_max = max(point.z for point in points)
center_z = (z_min + z_max) * 0.5
radius_z = (z_max - z_min) * 0.5
inverse = head.matrix_world.inverted()
for vertex in head.data.vertices:
    point = head.matrix_world @ vertex.co
    zn = (point.z - center_z) / radius_z
    upper = smoothstep(0.30, 0.88, zn)
    point.x *= 1.0 - 0.05 * upper
    point.z -= 0.060 * upper
    vertex.co = inverse @ point
head.data.update()

ear_raise = 0.10
extra_outward_slope = 0.10
for suffix, side in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"Cat_Ear_{suffix}"]
    inner = bpy.data.objects[f"Cat_InnerEar_{suffix}"]
    outer_points = [outer.matrix_world @ vertex.co for vertex in outer.data.vertices]
    root_z = min(point.z for point in outer_points)
    for obj in (outer, inner):
        obj_inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            point = obj.matrix_world @ vertex.co
            point.x += side * extra_outward_slope * max(0.0, point.z - root_z)
            point.z += ear_raise
            vertex.co = obj_inverse @ point
        obj.data.update()

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in tracked_names}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_CrownEarEmergence_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "CROWN_EAR_EMERGENCE"
scene["comforting_cat_v5_geometry_attempt"] = "crown_ear_emergence_1"
scene["comforting_cat_v5_dominant_defect"] = "smooth_crown_absorbing_ears"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "lower 65 percent of head",
        "eyes, lids, brows and muzzle",
        "body proportions",
        "costume and integrated arms",
        "legs and paw grounding",
        "satchel and tail",
        "materials",
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
render(camera, "02_material_front", (0.0, -8.6, 3.20), (0.0, -0.04, 2.05), 4.70)
render(camera, "03_front_3q", (4.0, -7.4, 3.50), (0.0, -0.02, 2.00), 4.80)
render(camera, "04_side", (8.4, -0.35, 3.20), (0.0, 0.0, 1.94), 4.80)
render(camera, "05_back", (0.0, 8.4, 3.20), (0.0, 0.04, 1.94), 4.80)
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
    "stage": "CROWN_EAR_EMERGENCE",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "smooth_crown_absorbing_ears",
    "crown_drop": 0.060,
    "upper_x_narrowing": 0.05,
    "ear_raise": ear_raise,
    "extra_outward_slope": extra_outward_slope,
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
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_CROWN_EAR_A1=" + json.dumps(report, ensure_ascii=False))
