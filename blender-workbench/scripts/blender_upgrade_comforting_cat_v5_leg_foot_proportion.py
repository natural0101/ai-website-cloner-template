"""TRUE_360 pose pass: shorten exposed legs and reduce clown-like feet."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_leg_foot_proportion_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_tail_proportion_attempt3.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_leg_foot_proportion_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def record(obj: bpy.types.Object) -> dict[str, list[float]]:
    return {
        "location": [round(float(value), 6) for value in obj.matrix_world.translation],
        "dimensions": [round(float(value), 6) for value in obj.dimensions],
    }


before = {}
after = {}
for side, suffix in ((-1.0, "L"), (1.0, "R")):
    leg = bpy.data.objects[f"Cat_Leg_{suffix}"]
    foot = bpy.data.objects[f"Cat_Foot_{suffix}"]
    before[suffix] = {"leg": record(leg), "foot": record(foot)}

    for vertex in leg.data.vertices:
        vertex.co.x *= 0.82
        vertex.co.y *= 0.85
        vertex.co.z *= 0.80
    leg.data.update()
    leg_matrix = leg.matrix_world.copy()
    leg_matrix.translation.x = side * 0.20
    leg_matrix.translation.z = 0.50
    leg.matrix_world = leg_matrix

    for vertex in foot.data.vertices:
        vertex.co.x *= 0.72
        vertex.co.y *= 0.80
        vertex.co.z *= 0.78
    foot.data.update()
    foot_matrix = foot.matrix_world.copy()
    foot_matrix.translation = Vector((side * 0.20, -0.47, 0.18))
    foot.matrix_world = foot_matrix

    for index in range(3):
        toe = bpy.data.objects[f"Cat_ToeLine_{suffix}_{index}"]
        for vertex in toe.data.vertices:
            vertex.co.x = side * 0.20 + (vertex.co.x - side * 0.23) * 0.72
            vertex.co.y = -0.47 + (vertex.co.y + 0.49) * 0.80
            vertex.co.z = 0.18 + (vertex.co.z - 0.22) * 0.78
        toe.data.update()

    after[suffix] = {"leg": record(leg), "foot": record(foot)}

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_LegFootProportion_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "POSE_LEG_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "leg_foot_proportion_1"
scene["comforting_cat_v5_dominant_defect"] = "long_exposed_legs_and_oversized_feet"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head and face",
        "robe and rear coverage",
        "scarf integration",
        "arms and sleeves",
        "tail",
        "satchel and strap",
        "lighting",
        "review cameras",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
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
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
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
qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "long_exposed_legs_and_oversized_feet",
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
        "errors": structural_qa["errors"],
        "warnings": structural_qa["warnings"],
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_LEG_FOOT=" + json.dumps(report, ensure_ascii=False))
