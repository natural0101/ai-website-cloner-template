"""Structural cleanup for the accepted v4 face-geometry attempt."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ASSET = "comforting_cat_v4_face_geometry_qa"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v4_face_geometry_attempt2.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
for directory in (BLEND_DIR, EXPORT_DIR, RENDER_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected open source blend {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (CHECKPOINT_DIR / "comforting_cat_v4_face_before_qa_cleanup.blend").resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

cleanup_targets = ["Cat_InnerEar_L", "Cat_InnerEar_R"]
cleanup_results = []
qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
mesh_topology = qa_namespace["mesh_topology"]
for name in cleanup_targets:
    obj = bpy.data.objects[name]
    before = mesh_topology(obj)
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=list(bm.edges))
        degenerate_faces = [face for face in bm.faces if face.calc_area() <= 1e-12]
        if degenerate_faces:
            bmesh.ops.delete(bm, geom=degenerate_faces, context="FACES")
            boundary_edges = [edge for edge in bm.edges if edge.is_boundary]
            if boundary_edges:
                bmesh.ops.holes_fill(bm, edges=boundary_edges)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.normal_update()
        bm.to_mesh(mesh)
        mesh.update()
    finally:
        bm.free()
    after = mesh_topology(obj)
    cleanup_results.append({"name": name, "before": before, "after": after})

# The inherited beveled inset contains collapsed bevel faces. Rebuild this
# simple closed garment panel instead of trying to repair a malformed bevel.
robe_inset = bpy.data.objects["Cat_RobeFrontInset"]
robe_before = mesh_topology(robe_inset)
robe_materials = list(robe_inset.data.materials)
points_xz = [
    (-0.35, 1.98),
    (0.35, 1.98),
    (0.33, 0.82),
    (0.12, 0.72),
    (-0.12, 0.72),
    (-0.33, 0.82),
]
y_front = -0.57
y_back = -0.48
vertices = [(x, y_front, z) for x, z in points_xz] + [
    (x, y_back, z) for x, z in points_xz
]
count = len(points_xz)
faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
for index in range(count):
    next_index = (index + 1) % count
    faces.append((index, count + index, count + next_index, next_index))
new_mesh = bpy.data.meshes.new("Cat_RobeFrontInset_CleanMesh")
new_mesh.from_pydata(vertices, [], faces)
new_mesh.update(calc_edges=True)
for material in robe_materials:
    new_mesh.materials.append(material)
old_mesh = robe_inset.data
robe_inset.data = new_mesh
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
for polygon in new_mesh.polygons:
    polygon.use_smooth = False
robe_after = mesh_topology(robe_inset)
cleanup_results.append(
    {"name": "Cat_RobeFrontInset", "before": robe_before, "after": robe_after}
)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V4_FaceGeometry_QA"
scene["comforting_cat_v4_stage"] = "EXPORT_QA"
scene["comforting_cat_v4_qa_cleanup"] = True


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    path: Path,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(
    camera,
    RENDER_DIR / f"{ASSET}_02_material_front.png",
    (0.0, -8.6, 3.15),
    (0.0, -0.04, 2.08),
    4.75,
)
render_view(
    camera,
    RENDER_DIR / f"{ASSET}_03_front_3q.png",
    (4.0, -7.4, 3.45),
    (0.0, -0.02, 2.00),
    4.85,
)

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

structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if any(item["after"]["degenerate_faces"] for item in cleanup_results):
    errors.append("Degenerate-face cleanup did not clear all target meshes")
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

report = {
    "asset": ASSET,
    "stage": "EXPORT_QA",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "cleanup_results": cleanup_results,
    "triangles": triangle_count,
    "exportable_objects": len(export_objects),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
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
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V4_FACE_QA=" + json.dumps(report, ensure_ascii=False))
