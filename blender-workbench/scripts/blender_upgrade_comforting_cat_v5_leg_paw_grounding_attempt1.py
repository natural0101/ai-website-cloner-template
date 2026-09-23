"""Integrate the capsule legs with wider planted paws."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_leg_paw_grounding_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_head_crown_attempt7.blend").resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_leg_paw_grounding_attempt1.blend"
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


tracked = []
before = {}
after = {}
for suffix in ("L", "R"):
    leg = bpy.data.objects[f"Cat_Leg_{suffix}"]
    foot = bpy.data.objects[f"Cat_Foot_{suffix}"]
    tracked.extend((leg, foot))
    before[leg.name] = bounds(leg)
    before[foot.name] = bounds(foot)

    leg_points = [leg.matrix_world @ vertex.co for vertex in leg.data.vertices]
    z_min = min(point.z for point in leg_points)
    z_max = max(point.z for point in leg_points)
    center_x = sum(point.x for point in leg_points) / len(leg_points)
    center_y = sum(point.y for point in leg_points) / len(leg_points)
    inverse = leg.matrix_world.inverted()
    for vertex in leg.data.vertices:
        point = leg.matrix_world @ vertex.co
        t = max(0.0, min(1.0, (point.z - z_min) / (z_max - z_min)))
        lower_fullness = 0.20 * (1.0 - t) ** 1.5
        point.x = center_x + (point.x - center_x) * (1.08 + lower_fullness)
        point.y = center_y + (point.y - center_y) * (1.04 + 0.10 * (1.0 - t))
        point.z += 0.052 * t**3
        vertex.co = inverse @ point
    leg.data.update()

    foot_center = Vector(foot.matrix_world.translation)
    foot_inverse = foot.matrix_world.inverted()
    for vertex in foot.data.vertices:
        point = foot.matrix_world @ vertex.co
        point.x = foot_center.x + (point.x - foot_center.x) * 1.30
        point.y = foot_center.y + (point.y - foot_center.y) * 1.10
        point.z = foot_center.z + (point.z - foot_center.z) * 0.96
        vertex.co = foot_inverse @ point
    foot.data.update()

    for index in range(3):
        toe = bpy.data.objects[f"Cat_ToeLine_{suffix}_{index}"]
        toe_inverse = toe.matrix_world.inverted()
        for vertex in toe.data.vertices:
            point = toe.matrix_world @ vertex.co
            point.x = foot_center.x + (point.x - foot_center.x) * 1.30
            point.y = foot_center.y + (point.y - foot_center.y) * 1.10
            point.z = foot_center.z + (point.z - foot_center.z) * 0.96
            vertex.co = toe_inverse @ point
        toe.data.update()

    after[leg.name] = bounds(leg)
    after[foot.name] = bounds(foot)

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_LegPawGrounding_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "LEG_PAW_GROUNDING"
scene["comforting_cat_v5_geometry_attempt"] = "leg_paw_grounding_1"
scene["comforting_cat_v5_dominant_defect"] = "capsule_legs_and_bead_feet"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head, ears and face",
        "robe and scarf",
        "arms",
        "satchel and strap",
        "tail",
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
errors = list(qa["errors"])
warnings = list(qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "LEG_PAW_GROUNDING",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "capsule_legs_and_bead_feet",
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
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
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
print("COMFORTING_CAT_V5_LEG_PAW_A1=" + json.dumps(report, ensure_ascii=False))
