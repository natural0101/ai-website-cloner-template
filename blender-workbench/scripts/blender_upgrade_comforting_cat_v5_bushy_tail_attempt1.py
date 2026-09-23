"""Replace the tubular hook tail with a reversible bushy multi-mass volume."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_bushy_tail_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_crown_ear_emergence_attempt1.blend"
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_bushy_tail_attempt1.blend"
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


root = bpy.data.objects["Cat_Root"]
old_base = bpy.data.objects["Cat_Tail_Base"]
old_tip = bpy.data.objects["Cat_Tail_CreamTip"]
before = {
    "base": bounds(old_base),
    "tip": bounds(old_tip),
}
orange_material = old_base.data.materials[0]
cream_material = old_tip.data.materials[0]
tail_collection = old_base.users_collection[0]

preserved_sources = []
for obj, source_name in (
    (old_base, "Cat_Tail_Base_SOURCE_V5_BUSHY_A1"),
    (old_tip, "Cat_Tail_CreamTip_SOURCE_V5_BUSHY_A1"),
):
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = world
    obj.name = source_name
    obj.hide_render = True
    obj.hide_set(True)
    preserved_sources.append(obj.name)


def add_mass(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    rotation_y: float,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40,
        ring_count=28,
        location=location,
        rotation=(0.0, rotation_y, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(orange_material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    for linked_collection in list(obj.users_collection):
        linked_collection.objects.unlink(obj)
    tail_collection.objects.link(obj)
    return obj


masses = [
    add_mass("Cat_TailMass_Root", (0.43, 0.16, 0.55), (0.20, 0.19, 0.27), -0.34),
    add_mass("Cat_TailMass_Mid", (0.61, 0.15, 0.38), (0.28, 0.22, 0.24), -0.28),
    add_mass("Cat_TailMass_Outer", (0.82, 0.13, 0.30), (0.29, 0.21, 0.20), -0.08),
]

bpy.ops.object.select_all(action="DESELECT")
for obj in masses:
    obj.select_set(True)
bpy.context.view_layer.objects.active = masses[0]
bpy.ops.object.join()
tail = bpy.context.object
tail.name = "Cat_Tail_Base"
remesh = tail.modifiers.new("BushyTailVoxelUnion", "REMESH")
remesh.mode = "VOXEL"
remesh.voxel_size = 0.018
remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = tail.modifiers.new("BushyTailSmooth", "SMOOTH")
smooth.factor = 0.28
smooth.iterations = 2
bpy.ops.object.modifier_apply(modifier=smooth.name)
world = tail.matrix_world.copy()
tail.parent = root
tail.matrix_world = world

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=40,
    ring_count=28,
    location=(1.01, 0.105, 0.29),
)
tip = bpy.context.object
tip.name = "Cat_Tail_CreamTip"
tip.scale = (0.19, 0.17, 0.17)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
tip.data.materials.append(cream_material)
for polygon in tip.data.polygons:
    polygon.use_smooth = True
for linked_collection in list(tip.users_collection):
    linked_collection.objects.unlink(tip)
tail_collection.objects.link(tip)
world = tip.matrix_world.copy()
tip.parent = root
tip.matrix_world = world

bpy.context.view_layer.update()
after = {
    "base": bounds(tail),
    "tip": bounds(tip),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_BushyTail_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "BUSHY_TAIL_VOLUME"
scene["comforting_cat_v5_geometry_attempt"] = "bushy_tail_1"
scene["comforting_cat_v5_dominant_defect"] = "tubular_hook_tail"
scene["comforting_cat_v5_preserved_sources"] = json.dumps(preserved_sources)
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head, ears and face",
        "body proportions and costume",
        "integrated arms",
        "legs and paw grounding",
        "satchel and strap",
        "materials except inherited tail materials",
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
    "stage": "BUSHY_TAIL_VOLUME",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "tubular_hook_tail",
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
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_BUSHY_TAIL_A1=" + json.dumps(report, ensure_ascii=False))
