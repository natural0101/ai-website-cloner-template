"""TRUE_360 pose pass: fuse each hanging arm and bead-like paw."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_arm_union_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_muzzle_union_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_arm_union_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


root = bpy.data.objects["Cat_Root"]
before: dict[str, object] = {}
after: dict[str, object] = {}
source_names: list[str] = []

for side, suffix in ((-1.0, "L"), (1.0, "R")):
    arm_source = bpy.data.objects[f"Cat_Arm_{suffix}"]
    paw_source = bpy.data.objects[f"Cat_Paw_{suffix}"]
    before[suffix] = {
        "arm": world_bounds(arm_source),
        "paw": world_bounds(paw_source),
    }

    # Duplicate first, then preserve the originals outside the export hierarchy.
    arm_work = arm_source.copy()
    arm_work.data = arm_source.data.copy()
    arm_work.name = f"Cat_ArmUnionWork_{suffix}"
    bpy.context.scene.collection.objects.link(arm_work)
    arm_work.matrix_world = arm_source.matrix_world.copy()

    paw_work = paw_source.copy()
    paw_work.data = paw_source.data.copy()
    paw_work.name = f"Cat_PawUnionWork_{suffix}"
    bpy.context.scene.collection.objects.link(paw_work)
    paw_work.matrix_world = paw_source.matrix_world.copy()

    for source in (arm_source, paw_source):
        matrix = source.matrix_world.copy()
        source.parent = None
        source.matrix_world = matrix
        source.hide_viewport = True
        source.hide_render = True
        source.name = f"{source.name}_SOURCE_V5_A1"
        source_names.append(source.name)

    # Shorten and embed the paw deeply into the forearm before voxel fusion.
    for vertex in paw_work.data.vertices:
        vertex.co.x *= 0.78
        vertex.co.y *= 0.82
        vertex.co.z *= 0.70
    paw_work.data.update()
    paw_matrix = paw_work.matrix_world.copy()
    paw_matrix.translation = Vector((side * 0.58, -0.50, 0.90))
    paw_work.matrix_world = paw_matrix

    for vertex in arm_work.data.vertices:
        vertex.co.x *= 0.90
        vertex.co.y *= 0.90
        vertex.co.z *= 0.96
    arm_work.data.update()

    bpy.ops.object.select_all(action="DESELECT")
    arm_work.select_set(True)
    paw_work.select_set(True)
    bpy.context.view_layer.objects.active = arm_work
    bpy.ops.object.join()
    unified = bpy.context.object
    unified.name = f"Cat_ArmUnified_{suffix}"

    remesh = unified.modifiers.new(name="ArmPawVoxelUnion", type="REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = 0.018
    remesh.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth = unified.modifiers.new(name="ArmPawSmooth", type="SMOOTH")
    smooth.factor = 0.34
    smooth.iterations = 2
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    for polygon in unified.data.polygons:
        polygon.use_smooth = True

    matrix = unified.matrix_world.copy()
    unified.parent = root
    unified.matrix_world = matrix
    after[suffix] = world_bounds(unified)

bpy.context.view_layer.update()

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_ArmUnion_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "POSE_LIMB_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "arm_union_1"
scene["comforting_cat_v5_dominant_defect"] = "beaded_hanging_arms"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "sleeve geometry",
        "head and face",
        "robe and rear coverage",
        "scarf integration",
        "legs and feet",
        "satchel and strap",
        "tail",
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
    scene["comforting_cat_v5_stage"] = "POSE_LIMB_REVIEW"
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_render = False
    obj.hide_viewport = False
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
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "POSE_LIMB_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "beaded_hanging_arms",
    "source_parts": source_names,
    "before": before,
    "after": after,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
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
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_ARM_UNION=" + json.dumps(report, ensure_ascii=False))
