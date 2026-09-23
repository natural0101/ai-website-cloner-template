"""TRUE_360 scarf pass: replace stacked rigid plates with one soft diagonal drape."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_soft_scarf_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_head_silhouette_attempt1.blend"
).resolve()
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
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_soft_scarf_attempt2.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
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


required = [
    "Cat_Root",
    "Cat_ScarfWrap",
    "Cat_ScarfUpperFold",
    "Cat_ScarfLowerDrape",
    "CAT_WeatheredBlueCloth",
    "CAT_RenderCamera",
]
missing = [name for name in required if name not in bpy.data.objects and name not in bpy.data.materials]
if missing:
    raise RuntimeError(f"Missing scarf pass nodes: {missing}")

wrap = bpy.data.objects["Cat_ScarfWrap"]
upper = bpy.data.objects["Cat_ScarfUpperFold"]
drape = bpy.data.objects["Cat_ScarfLowerDrape"]
before = {obj.name: bounds(obj) for obj in (wrap, upper, drape)}

# Preserve the rejected shelf-like upper fold in the .blend, but remove it from
# both render and export hierarchy. The checkpoint retains the untouched source.
upper.parent = None
upper.hide_render = True
upper.hide_viewport = True
upper["comforting_cat_preserved_source"] = True
upper["comforting_cat_rejection_reason"] = "rigid_stacked_plate"

# Lower and slightly flatten the rear half of the ring so it reads as cloth
# hugging the neck rather than a fully exposed inflatable torus.
wrap_center_z = sum(
    float((wrap.matrix_world @ vertex.co).z) for vertex in wrap.data.vertices
) / len(wrap.data.vertices)
wrap_inverse = wrap.matrix_world.inverted()
for vertex in wrap.data.vertices:
    point = wrap.matrix_world @ vertex.co
    normalized_front = max(0.0, min(1.0, (-point.y - 0.05) / 0.38))
    point.z = wrap_center_z + (point.z - wrap_center_z) * 0.82
    point.z -= 0.018 * (1.0 - normalized_front)
    vertex.co = wrap_inverse @ point
wrap.data.update()

# Turn the remaining front panel into one broad, asymmetric cloth fold:
# wider, diagonally sloped, thinner in depth, and gently convex at the chest.
world_points = [drape.matrix_world @ vertex.co for vertex in drape.data.vertices]
center = sum(world_points, Vector()) / len(world_points)
inverse = drape.matrix_world.inverted()
target_half_width = 0.54
for vertex in drape.data.vertices:
    point = drape.matrix_world @ vertex.co
    point.x = center.x + (point.x - center.x) * 1.38
    point.z = center.z + (point.z - center.z) * 1.08 + 0.105
    point.z -= 0.14 * point.x
    point.y = center.y + (point.y - center.y) * 0.70
    edge_ratio = min(1.0, abs(point.x) / target_half_width)
    point.y -= 0.032 * (1.0 - edge_ratio * edge_ratio)
    vertex.co = inverse @ point
drape.data.update()

# One textile family removes the two-tone armour-plate reading.
drape.data.materials.clear()
drape.data.materials.append(bpy.data.materials["CAT_WeatheredBlueCloth"])
drape["comforting_cat_role"] = "soft_diagonal_scarf_drape"

# A very small bevel only softens the existing edge; it does not change the
# silhouette enough to hide contact defects.
bevel = drape.modifiers.get("SoftScarfEdge")
if bevel is None:
    bevel = drape.modifiers.new("SoftScarfEdge", "BEVEL")
bevel.width = 0.012
bevel.segments = 2
bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = {
    "Cat_ScarfWrap": bounds(wrap),
    "Cat_ScarfLowerDrape": bounds(drape),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_SoftScarf_A2"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "COSTUME_SOFT_SCARF"
scene["comforting_cat_v5_geometry_attempt"] = "soft_scarf_2"
scene["comforting_cat_v5_dominant_defect"] = "mechanical_stacked_scarf_plates"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head and face geometry",
        "eyes and expression",
        "robe and body",
        "arms and paws",
        "legs and feet",
        "satchel and strap",
        "tail",
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
    "stage": "COSTUME_SOFT_SCARF",
    "attempt": 2,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "mechanical_stacked_scarf_plates",
    "accepted_intermediate_predecessor": "comforting_cat_v5_head_silhouette_attempt1",
    "before": before,
    "after": after,
    "preserved_hidden_source": upper.name,
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
print("COMFORTING_CAT_V5_SOFT_SCARF=" + json.dumps(report, ensure_ascii=False))
