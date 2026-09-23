"""Lower only the robe hem to match the target's short exposed-leg zone."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_lower_robe_hem_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_head_cheek_wedge_attempt1.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_lower_robe_hem_attempt1.blend"
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
    p = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return p * p * (3.0 - 2.0 * p)


robe = bpy.data.objects["Cat_BlueRobe"]
before = bounds(robe)
inverse = robe.matrix_world.inverted()
center_y = 0.040
hem_drop = 0.300

for vertex in robe.data.vertices:
    point = robe.matrix_world @ vertex.co
    original_z = point.z
    lower_weight = 1.0 - smoothstep(0.72, 1.35, original_z)
    # Keep the front center slightly higher than the sides/back so the longer
    # garment does not become a rigid cylindrical cut.
    frontness = max(0.0, min(1.0, (center_y - point.y) / 0.455))
    front_arch = 0.050 * frontness * lower_weight
    point.z = original_z - hem_drop * lower_weight + front_arch
    vertex.co = inverse @ point

robe.data.update()
bpy.context.view_layer.update()
after = bounds(robe)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_LowerRobeHem_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "LOWER_ROBE_HEM"
scene["comforting_cat_v5_geometry_attempt"] = "lower_robe_hem_1"
scene["comforting_cat_v5_dominant_defect"] = "exposed_leg_zone_more_than_twice_target_ratio"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "upper 65 percent of robe",
        "scarf and collar",
        "front inset",
        "body, legs and paws",
        "head and face",
        "arms",
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
    "stage": "LOWER_ROBE_HEM",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "exposed_leg_zone_more_than_twice_target_ratio",
    "deform": {
        "hem_drop": hem_drop,
        "falloff_z": [0.72, 1.35],
        "front_arch_max": 0.050,
    },
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
print("COMFORTING_CAT_V5_LOWER_ROBE_HEM_A1=" + json.dumps(report, ensure_ascii=False))
