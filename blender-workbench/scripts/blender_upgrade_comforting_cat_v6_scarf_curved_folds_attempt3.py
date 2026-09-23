"""Replace the flat v6 scarf shield with curved, layered quad cloth folds."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_curved_folds_attempt3"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_costume_envelope_attempt2.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_curved_folds_attempt3.blend"
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


root = bpy.data.objects["CatV6_Root"]
source = bpy.data.objects["V6_Scarf_FrontDrape"]
material = source.data.materials[0]
before = {
    "front_drape": bounds(source),
    "upper_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Upper"]),
    "lower_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Lower"]),
}
source.parent = None
source.hide_render = True
source.hide_set(True)
source.name = "V6_Scarf_FrontDrape_SOURCE_FLAT_A3"
source["comforting_cat_preserved_source"] = True
source["comforting_cat_rejection_reason"] = "flat_front_shield"

for name in ("V6_ScarfWrap_Upper", "V6_ScarfWrap_Lower"):
    obj = bpy.data.objects[name]
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        point.x *= 1.13
        vertex.co = inverse @ point
    obj.data.update()


def curved_fold(
    name: str,
    rows: list[list[tuple[float, float]]],
    center_y: float,
    edge_rear_curve: float,
    thickness: float,
) -> bpy.types.Object:
    column_count = len(rows[0])
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    max_abs_x = max(abs(x) for row in rows for x, _ in row)
    for row in rows:
        if len(row) != column_count:
            raise RuntimeError(f"Inconsistent row width for {name}")
        for x, z in row:
            edge = abs(x) / max_abs_x
            y = center_y + edge_rear_curve * edge * edge
            vertices.append((x, y, z))
    for row_index in range(len(rows) - 1):
        for column_index in range(column_count - 1):
            a = row_index * column_count + column_index
            b = a + 1
            c = (row_index + 1) * column_count + column_index + 1
            d = (row_index + 1) * column_count + column_index
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(f"{name}_CurvedQuadMesh")
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
    bevel.width = 0.012
    bevel.segments = 2
    return obj


columns = [-1.0, -0.67, -0.33, 0.0, 0.33, 0.67, 1.0]
top_z = [2.31, 2.34, 2.37, 2.39, 2.36, 2.32, 2.29]
mid_z = [2.16, 2.15, 2.14, 2.12, 2.12, 2.13, 2.15]
bottom_z = [2.04, 1.94, 1.82, 1.70, 1.78, 1.92, 2.04]
lower_rows = [
    [(0.64 * column, z) for column, z in zip(columns, top_z)],
    [(0.62 * column, z) for column, z in zip(columns, mid_z)],
    [(0.58 * column, z) for column, z in zip(columns, bottom_z)],
]
lower_fold = curved_fold(
    "V6_Scarf_FrontDrape",
    lower_rows,
    center_y=-0.515,
    edge_rear_curve=0.105,
    thickness=0.060,
)

upper_top = [2.43, 2.45, 2.46, 2.45, 2.42, 2.39, 2.36]
upper_bottom = [2.27, 2.28, 2.28, 2.27, 2.24, 2.20, 2.17]
upper_rows = [
    [(0.66 * column, z) for column, z in zip(columns, upper_top)],
    [(0.62 * column, z) for column, z in zip(columns, upper_bottom)],
]
upper_fold = curved_fold(
    "V6_Scarf_FrontFold_Upper",
    upper_rows,
    center_y=-0.555,
    edge_rear_curve=0.115,
    thickness=0.055,
)

bpy.context.view_layer.update()
after = {
    "front_drape": bounds(lower_fold),
    "front_upper_fold": bounds(upper_fold),
    "upper_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Upper"]),
    "lower_wrap": bounds(bpy.data.objects["V6_ScarfWrap_Lower"]),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfCurvedFolds_A3"
scene["comforting_cat_v6_stage"] = "SCARF_CURVED_FOLDS"
scene["comforting_cat_v6_attempt"] = 3
scene["comforting_cat_v6_dominant_defect"] = "flat_scarf_front_shield"
scene["comforting_cat_v6_rejected_predecessor"] = "costume_envelope_attempt2_scarf"
scene["comforting_cat_v6_preserved_source"] = source.name


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
    "stage": "SCARF_CURVED_FOLDS",
    "attempt": 3,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_scarf_front_shield",
    "preserved_source": source.name,
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
print("COMFORTING_CAT_V6_SCARF_CURVED_FOLDS_A3=" + json.dumps(report, ensure_ascii=False))
