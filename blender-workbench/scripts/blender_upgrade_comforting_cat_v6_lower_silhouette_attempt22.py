"""Raise the garment hem and enlarge the exposed legs and feet to target ratios."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_lower_silhouette_attempt22"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_mouth_feline_worry_attempt21.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_lower_silhouette_attempt22.blend"
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


def preserve_copy(obj: bpy.types.Object) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A22"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "compressed_lower_silhouette"
    return copy.name


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def resize_mesh_to_bounds(
    obj: bpy.types.Object,
    target_dimensions: tuple[float, float, float],
    target_location: tuple[float, float, float],
) -> None:
    current = bounds(obj)["dimensions"]
    factors = [
        target_dimensions[index] / current[index]
        for index in range(3)
    ]
    for vertex in obj.data.vertices:
        vertex.co.x *= factors[0]
        vertex.co.y *= factors[1]
        vertex.co.z *= factors[2]
    obj.data.update()
    obj.location = target_location


root = bpy.data.objects["CatV6_Root"]
object_names = [
    "V6_Robe",
    "V6_FrontTunic",
    "V6_Leg_L",
    "V6_Leg_R",
    "V6_Foot_L",
    "V6_Foot_R",
]
before = {name: bounds(bpy.data.objects[name]) for name in object_names}
preserved_sources = [
    preserve_copy(bpy.data.objects[name])
    for name in object_names
]

robe = bpy.data.objects["V6_Robe"]
robe_inverse = robe.matrix_world.inverted()
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if world.z < 1.0:
        if world.z <= 0.70:
            offset = 0.14
        else:
            offset = 0.14 * (1.0 - smoothstep(0.70, 1.00, world.z))
        world.z += offset
        vertex.co = robe_inverse @ world
robe.data.update()

tunic = bpy.data.objects["V6_FrontTunic"]
tunic_inverse = tunic.matrix_world.inverted()
for vertex in tunic.data.vertices:
    world = tunic.matrix_world @ vertex.co
    if world.z < 1.05:
        if world.z <= 0.74:
            offset = 0.14
        else:
            offset = 0.14 * (1.0 - smoothstep(0.74, 1.05, world.z))
        world.z += offset
    world.y += 0.018
    vertex.co = tunic_inverse @ world
tunic.data.update()

resize_mesh_to_bounds(
    bpy.data.objects["V6_Leg_L"],
    (0.34, 0.30, 0.64),
    (-0.21, 0.0, 0.42),
)
resize_mesh_to_bounds(
    bpy.data.objects["V6_Leg_R"],
    (0.34, 0.30, 0.64),
    (0.21, 0.0, 0.42),
)
resize_mesh_to_bounds(
    bpy.data.objects["V6_Foot_L"],
    (0.44, 0.42, 0.24),
    (-0.23, -0.10, 0.13),
)
resize_mesh_to_bounds(
    bpy.data.objects["V6_Foot_R"],
    (0.44, 0.42, 0.24),
    (0.23, -0.10, 0.13),
)

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in object_names}
full_height = 3.60
metrics = {
    "robe_min_z_over_height": round(after["V6_Robe"]["min"][2] / full_height, 5),
    "hem_to_ground_over_height": round(after["V6_Robe"]["min"][2] / full_height, 5),
    "foot_width_over_robe_width": round(
        after["V6_Foot_L"]["dimensions"][0]
        / after["V6_Robe"]["dimensions"][0],
        5,
    ),
    "leg_width_over_robe_width": round(
        after["V6_Leg_L"]["dimensions"][0]
        / after["V6_Robe"]["dimensions"][0],
        5,
    ),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_LowerSilhouette_A22"
scene["comforting_cat_v6_stage"] = "LOWER_SILHOUETTE"
scene["comforting_cat_v6_attempt"] = 22
scene["comforting_cat_v6_dominant_defect"] = "compressed_lower_silhouette"
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
    "stage": "LOWER_SILHOUETTE",
    "attempt": 22,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "compressed_lower_silhouette",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
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
print("COMFORTING_CAT_V6_LOWER_SILHOUETTE_A22=" + json.dumps(report, ensure_ascii=False))
