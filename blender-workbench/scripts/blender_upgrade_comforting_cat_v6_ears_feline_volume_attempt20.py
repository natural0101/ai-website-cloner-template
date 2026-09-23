"""Replace triangular ear prisms with rounded five-point feline ear volumes."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_ears_feline_volume_attempt20"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_arms_tucked_short_attempt19.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_ears_feline_volume_attempt20.blend"
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


def ear_volume(
    name: str,
    outline: list[tuple[float, float]],
    depths: list[float],
    center_y: float,
    material: bpy.types.Material,
    bevel_width: float,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for (x_value, z_value), depth in zip(outline, depths):
        vertices.append((x_value, center_y - depth * 0.5, z_value))
    for (x_value, z_value), depth in zip(outline, depths):
        vertices.append((x_value, center_y + depth * 0.5, z_value))
    count = len(outline)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(f"{name}_FelineVolumeMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    bevel = obj.modifiers.new(f"{name}_SoftFelineEdge", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 4
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


root = bpy.data.objects["CatV6_Root"]
outer_material = bpy.data.objects["V6_Ear_L"].data.materials[0]
inner_material = bpy.data.objects["V6_InnerEar_L"].data.materials[0]
source_names = [
    "V6_Ear_L",
    "V6_Ear_R",
    "V6_InnerEar_L",
    "V6_InnerEar_R",
]
before = {name: bounds(bpy.data.objects[name]) for name in source_names}
preserved_sources: list[str] = []
for name in source_names:
    source = bpy.data.objects[name]
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = f"{name}_SOURCE_A20"
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "triangular_pyramid_ear"
    preserved_sources.append(source.name)

created: list[bpy.types.Object] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    outer_outline = [
        (sign * 0.66, 3.15),
        (sign * 0.60, 3.36),
        (sign * 0.47, 3.60),
        (sign * 0.34, 3.38),
        (sign * 0.25, 3.17),
    ]
    created.append(
        ear_volume(
            f"V6_Ear_{side}",
            outer_outline,
            [0.34, 0.24, 0.055, 0.22, 0.33],
            0.0,
            outer_material,
            0.028,
        )
    )
    inner_outline = [
        (sign * 0.575, 3.22),
        (sign * 0.545, 3.37),
        (sign * 0.47, 3.52),
        (sign * 0.395, 3.38),
        (sign * 0.335, 3.23),
    ]
    created.append(
        ear_volume(
            f"V6_InnerEar_{side}",
            inner_outline,
            [0.014, 0.012, 0.008, 0.012, 0.014],
            -0.181,
            inner_material,
            0.007,
        )
    )

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in created}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EarsFelineVolume_A20"
scene["comforting_cat_v6_stage"] = "EARS_FELINE_VOLUME"
scene["comforting_cat_v6_attempt"] = 20
scene["comforting_cat_v6_dominant_defect"] = "triangular_pyramid_ears"
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
    "stage": "EARS_FELINE_VOLUME",
    "attempt": 20,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "triangular_pyramid_ears",
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
scene["comforting_cat_v6_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V6_EARS_FELINE_VOLUME_A20=" + json.dumps(report, ensure_ascii=False))
