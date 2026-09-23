"""Geometry-only garment silhouette pass on top of the accepted v4 face QA."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v4_garment_geometry_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v4_face_geometry_qa.blend").resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v4_before_garment_geometry_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def reshape_robe(obj: bpy.types.Object) -> None:
    z_values = [vertex.co.z for vertex in obj.data.vertices]
    z_min, z_max = min(z_values), max(z_values)
    span = max(z_max - z_min, 1e-6)
    for vertex in obj.data.vertices:
        t = (vertex.co.z - z_min) / span
        vertex.co.x *= 0.94 + 0.12 * t
        vertex.co.y *= 0.95 + 0.07 * t
        vertex.co.z = z_max - 0.91 * (z_max - vertex.co.z)
    obj.data.update()


def reshape_front_panel(obj: bpy.types.Object) -> None:
    z_values = [vertex.co.z for vertex in obj.data.vertices]
    z_min, z_max = min(z_values), max(z_values)
    span = max(z_max - z_min, 1e-6)
    for vertex in obj.data.vertices:
        t = (vertex.co.z - z_min) / span
        vertex.co.x *= 0.96 + 0.10 * t
        vertex.co.z = z_max - 0.90 * (z_max - vertex.co.z)
    obj.data.update()


def reshape_scarf_panel(obj: bpy.types.Object, x_scale: float, z_scale: float) -> None:
    center_z = sum(vertex.co.z for vertex in obj.data.vertices) / len(obj.data.vertices)
    center_y = sum(vertex.co.y for vertex in obj.data.vertices) / len(obj.data.vertices)
    for vertex in obj.data.vertices:
        vertex.co.x *= x_scale
        vertex.co.y = center_y + (vertex.co.y - center_y) * 0.88 + 0.025
        vertex.co.z = center_z + (vertex.co.z - center_z) * z_scale - 0.025
    obj.data.update()


def apply_scale(obj: bpy.types.Object, factors: tuple[float, float, float]) -> None:
    obj.scale = tuple(obj.scale[index] * factors[index] for index in range(3))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


reshape_robe(bpy.data.objects["Cat_BlueRobe"])
reshape_front_panel(bpy.data.objects["Cat_RobeFrontInset"])
reshape_scarf_panel(bpy.data.objects["Cat_ScarfUpperFold"], 0.97, 0.90)
reshape_scarf_panel(bpy.data.objects["Cat_ScarfLowerDrape"], 0.94, 0.88)
scarf_wrap = bpy.data.objects["Cat_ScarfWrap"]
apply_scale(scarf_wrap, (1.01, 0.92, 0.90))
scarf_wrap.location.z -= 0.025

scene = bpy.context.scene
scene.name = "Comforting_Cat_V4_GarmentGeometry"
scene["comforting_cat_v4_stage"] = "GEOMETRY"
scene["comforting_cat_v4_geometry_attempt"] = "garment_1"
scene["comforting_cat_v4_dominant_defect"] = "rigid_cylindrical_garment_silhouette"
scene["comforting_cat_v4_do_not_change"] = json.dumps(
    ["head and face", "eyes", "arms and paws", "materials", "lighting"]
)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


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
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 2.00), 4.85)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.95), 4.85)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.95), 4.85)

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

triangle_count = 0
for obj in export_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangle_count += sum(max(0, len(face.vertices) - 2) for face in mesh.polygons)
    evaluated.to_mesh_clear()

scene_graph = {
    "schema_version": "1.0",
    "goal": "Make the inherited coat and scarf read as a shorter layered garment instead of a rigid cylinder.",
    "mode": "TRUE_360",
    "units": "METERS",
    "parts": [
        {
            "id": name,
            "name": name,
            "representation": "MESH",
            "dimensions": [
                max(0.0001, round(float(value), 5))
                for value in bpy.data.objects[name].dimensions
            ],
            "material_group": bpy.data.objects[name].data.materials[0].name,
            "source_confidence": 0.76,
            "notes": "Geometry-only v4 garment pass.",
        }
        for name in [
            "Cat_BlueRobe",
            "Cat_RobeFrontInset",
            "Cat_ScarfWrap",
            "Cat_ScarfUpperFold",
            "Cat_ScarfLowerDrape",
        ]
    ],
    "relations": [
        {
            "a": "Cat_BlueRobe",
            "type": "OVERLAPS",
            "b": "Cat_Body",
            "minimum_overlap": 0.01,
            "tolerance": 0.004,
        },
        {
            "a": "Cat_ScarfWrap",
            "type": "OVERLAPS",
            "b": "Cat_Head_Mesh",
            "minimum_overlap": 0.005,
            "tolerance": 0.004,
        },
        {
            "a": "Cat_ScarfWrap",
            "type": "OVERLAPS",
            "b": "Cat_BlueRobe",
            "minimum_overlap": 0.005,
            "tolerance": 0.004,
        },
    ],
    "camera": {
        "type": "ORTHOGRAPHIC",
        "review_views": ["front", "front_3q", "side", "back"],
    },
    "acceptance": {
        "dominant_defect": "rigid_cylindrical_garment_silhouette",
        "requirements": [
            "robe hem is shorter without exposing a gap at the body",
            "upper garment has more shoulder width and less bottom flare",
            "scarf layers remain attached and are less shelf-like",
            "face is unchanged",
        ],
        "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
    },
}
(REPORT_DIR / f"{ASSET}_scene_graph.json").write_text(
    json.dumps(scene_graph, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
report = {
    "asset": ASSET,
    "stage": "GEOMETRY",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_cylindrical_garment_silhouette",
    "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
    "triangles": triangle_count,
    "exportable_objects": len(export_objects),
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
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V4_GARMENT=" + json.dumps(report, ensure_ascii=False))
