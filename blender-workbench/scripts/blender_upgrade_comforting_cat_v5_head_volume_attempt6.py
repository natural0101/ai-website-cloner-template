"""Replace the ring-pinched head shell with a smooth editable ellipsoid."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_head_volume_attempt6"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_head_fur_mass_attempt5.blend").resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_head_volume_attempt6.blend"
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


old_head = bpy.data.objects["Cat_Head_Mesh"]
before = world_bounds(old_head)
corners = [old_head.matrix_world @ Vector(corner) for corner in old_head.bound_box]
mins = Vector(tuple(min(corner[index] for corner in corners) for index in range(3)))
maxs = Vector(tuple(max(corner[index] for corner in corners) for index in range(3)))
center = (mins + maxs) * 0.5
dimensions = maxs - mins
parent = old_head.parent
collection = old_head.users_collection[0]
material = old_head.data.materials[0]

old_head.name = "Cat_Head_Mesh_SOURCE_V5_VOLUME_A6"
old_head.parent = None
old_head.hide_render = True
old_head.hide_set(True)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=48,
    location=tuple(center),
)
head = bpy.context.object
head.name = "Cat_Head_Mesh"
head.scale = (
    dimensions.x * 0.5,
    dimensions.y * 0.5,
    dimensions.z * 0.5,
)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Keep the cranium round. Add only a very mild, front-weighted lower-cheek
# fullness; no circumferential ridge and no rear deformation.
radius_z = dimensions.z * 0.5
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    z_normalized = (world.z - center.z) / radius_z
    cheek = math.exp(-((z_normalized + 0.18) / 0.34) ** 2)
    if world.y <= center.y - 0.20:
        front = 1.0
    elif world.y >= center.y + 0.10:
        front = 0.0
    else:
        front = (center.y + 0.10 - world.y) / 0.30
    vertex.co.x *= 1.0 + 0.024 * cheek * front
head.data.update()
for polygon in head.data.polygons:
    polygon.use_smooth = True
head.data.materials.append(material)

for linked_collection in list(head.users_collection):
    linked_collection.objects.unlink(head)
collection.objects.link(head)
world_matrix = head.matrix_world.copy()
head.parent = parent
head.matrix_world = world_matrix
bpy.context.view_layer.update()
after = world_bounds(head)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_HeadVolume_A6"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "HEAD_VOLUME_REBUILD"
scene["comforting_cat_v5_geometry_attempt"] = "head_volume_6"
scene["comforting_cat_v5_dominant_defect"] = "circumferential_pinched_cheek_ridge"
scene["comforting_cat_v5_preserved_source"] = old_head.name
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head group transform",
        "ears",
        "eyes, lids and brows",
        "muzzle, nose, mouth and whiskers",
        "costume and pear robe",
        "limbs",
        "satchel and tail",
        "materials",
        "lighting and cameras",
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
    "stage": "HEAD_VOLUME_REBUILD",
    "attempt": 6,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "circumferential_pinched_cheek_ridge",
    "preserved_source": old_head.name,
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
    json.dumps(structural_qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_HEAD_VOLUME_A6=" + json.dumps(report, ensure_ascii=False))
