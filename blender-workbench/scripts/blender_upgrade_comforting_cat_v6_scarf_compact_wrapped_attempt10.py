"""Rebuild only the v6 scarf as compact cloth wrapping the chest and neck."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_compact_wrapped_attempt10"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_unified_arms_attempt8.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_compact_wrapped_attempt10.blend"
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


def preserve_source(obj: bpy.types.Object, reason: str) -> None:
    obj.parent = None
    obj.hide_render = True
    obj.hide_set(True)
    obj.name = f"{obj.name}_SOURCE_A10"
    obj["comforting_cat_preserved_source"] = True
    obj["comforting_cat_rejection_reason"] = reason


def cloth_surface(
    name: str,
    rows: list[list[tuple[float, float, float]]],
    material: bpy.types.Material,
    thickness: float,
) -> bpy.types.Object:
    column_count = len(rows[0])
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for row in rows:
        if len(row) != column_count:
            raise RuntimeError(f"Inconsistent row width for {name}")
        vertices.extend(row)
    for row_index in range(len(rows) - 1):
        for column_index in range(column_count - 1):
            a = row_index * column_count + column_index
            b = a + 1
            c = (row_index + 1) * column_count + column_index + 1
            d = (row_index + 1) * column_count + column_index
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(f"{name}_WrappedClothMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    solidify = obj.modifiers.new(f"{name}_Thickness", "SOLIDIFY")
    solidify.thickness = thickness
    solidify.offset = 0.0
    bevel = obj.modifiers.new(f"{name}_SoftEdge", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 3
    return obj


root = bpy.data.objects["CatV6_Root"]
front_source = bpy.data.objects["V6_Scarf_FrontDrape"]
material = front_source.data.materials[0]
source_names = [
    "V6_Scarf_FrontDrape",
    "V6_Scarf_FrontFold_Upper",
    "V6_Scarf_BackDrape",
]
before = {name: bounds(bpy.data.objects[name]) for name in source_names}
for name in source_names:
    preserve_source(bpy.data.objects[name], "rigid_scarf_shield")

columns = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]


def front_row(
    half_width: float,
    z_values: list[float],
    center_y: float,
    edge_rear_curve: float,
) -> list[tuple[float, float, float]]:
    row: list[tuple[float, float, float]] = []
    for column, z in zip(columns, z_values):
        edge = abs(column)
        y = center_y + edge_rear_curve * edge * edge
        row.append((half_width * column, y, z))
    return row


front_rows = [
    front_row(
        0.64,
        [2.30, 2.32, 2.34, 2.36, 2.37, 2.36, 2.34, 2.32, 2.30],
        -0.555,
        0.225,
    ),
    front_row(
        0.61,
        [2.20, 2.21, 2.22, 2.22, 2.21, 2.20, 2.19, 2.19, 2.20],
        -0.570,
        0.220,
    ),
    front_row(
        0.55,
        [2.10, 2.08, 2.04, 1.99, 1.94, 1.90, 1.96, 2.03, 2.09],
        -0.545,
        0.195,
    ),
]
front_drape = cloth_surface(
    "V6_Scarf_FrontDrape",
    front_rows,
    material,
    thickness=0.065,
)

upper_rows = [
    front_row(
        0.65,
        [2.42, 2.43, 2.44, 2.45, 2.45, 2.44, 2.42, 2.40, 2.38],
        -0.545,
        0.220,
    ),
    front_row(
        0.63,
        [2.30, 2.31, 2.32, 2.32, 2.31, 2.29, 2.27, 2.25, 2.24],
        -0.565,
        0.215,
    ),
]
upper_fold = cloth_surface(
    "V6_Scarf_FrontFold_Upper",
    upper_rows,
    material,
    thickness=0.060,
)

back_columns = [-1.0, -0.66, -0.33, 0.0, 0.33, 0.66, 1.0]


def back_row(
    half_width: float,
    z_values: list[float],
    center_y: float,
    edge_forward_curve: float,
) -> list[tuple[float, float, float]]:
    row: list[tuple[float, float, float]] = []
    for column, z in zip(back_columns, z_values):
        edge = abs(column)
        y = center_y - edge_forward_curve * edge * edge
        row.append((half_width * column, y, z))
    return row


back_rows = [
    back_row(
        0.43,
        [2.34, 2.36, 2.37, 2.38, 2.37, 2.36, 2.34],
        0.505,
        0.125,
    ),
    back_row(
        0.42,
        [2.23, 2.24, 2.25, 2.25, 2.24, 2.23, 2.22],
        0.515,
        0.125,
    ),
    back_row(
        0.39,
        [2.12, 2.11, 2.10, 2.08, 2.10, 2.11, 2.12],
        0.480,
        0.105,
    ),
]
back_drape = cloth_surface(
    "V6_Scarf_BackDrape",
    back_rows,
    material,
    thickness=0.060,
)

bpy.context.view_layer.update()
after = {
    "front_drape": bounds(front_drape),
    "front_upper_fold": bounds(upper_fold),
    "back_drape": bounds(back_drape),
    "upper_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Upper"]),
    "lower_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Lower"]),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfCompactWrapped_A10"
scene["comforting_cat_v6_stage"] = "SCARF_COMPACT_WRAPPED"
scene["comforting_cat_v6_attempt"] = 10
scene["comforting_cat_v6_dominant_defect"] = "rigid_scarf_shields"
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
    "stage": "SCARF_COMPACT_WRAPPED",
    "attempt": 10,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_scarf_shields",
    "preserved_sources": [f"{name}_SOURCE_A10" for name in source_names],
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
print("COMFORTING_CAT_V6_SCARF_COMPACT_WRAPPED_A10=" + json.dumps(report, ensure_ascii=False))
