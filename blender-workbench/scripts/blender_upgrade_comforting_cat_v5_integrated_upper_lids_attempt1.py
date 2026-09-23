"""Face pass: build integrated upper-lid caps from the eye curvature."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_integrated_upper_lids_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_chest_inset_attempt2.blend").resolve()
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
    CHECKPOINT_DIR / "comforting_cat_v5_before_integrated_upper_lids_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


created = []
lid_metrics = {}
fur_material = bpy.data.materials["CAT_GoldenOrangeFur"]

for suffix in ("L", "R"):
    eye = bpy.data.objects[f"Cat_Eye_{suffix}"]
    eye_corners = [eye.matrix_world @ Vector(corner) for corner in eye.bound_box]
    eye_top = max(point.z for point in eye_corners)
    eye_bottom = min(point.z for point in eye_corners)
    eye_center = eye.matrix_world.translation.copy()
    eye_half_width = (max(point.x for point in eye_corners) - min(point.x for point in eye_corners)) / 2

    lid = eye.copy()
    lid.data = eye.data.copy()
    lid.name = f"Cat_UpperLidIntegrated_{suffix}"
    for collection in eye.users_collection[:1]:
        collection.objects.link(lid)
    lid.parent = eye.parent
    lid.matrix_world = eye.matrix_world.copy()
    lid.data.materials.clear()
    lid.data.materials.append(fur_material)

    bm = bmesh.new()
    bm.from_mesh(lid.data)
    delete_faces = []
    for face in bm.faces:
        center = lid.matrix_world @ face.calc_center_median()
        if suffix == "L":
            inner_weight = max(
                0.0,
                min(1.0, (center.x - (eye_center.x - eye_half_width)) / (2 * eye_half_width)),
            )
        else:
            inner_weight = max(
                0.0,
                min(1.0, ((eye_center.x + eye_half_width) - center.x) / (2 * eye_half_width)),
            )
        coverage = 0.044 + 0.018 * inner_weight
        cutoff = eye_top - coverage
        if center.z < cutoff or center.y > eye_center.y + 0.004:
            delete_faces.append(face)
    bmesh.ops.delete(bm, geom=delete_faces, context="FACES")
    loose_vertices = [vertex for vertex in bm.verts if not vertex.link_faces]
    if loose_vertices:
        bmesh.ops.delete(bm, geom=loose_vertices, context="VERTS")
    bm.to_mesh(lid.data)
    bm.free()
    lid.data.update()

    matrix = lid.matrix_world.copy()
    matrix.translation += Vector((0.0, -0.007, 0.0))
    lid.matrix_world = matrix
    for polygon in lid.data.polygons:
        polygon.use_smooth = True
    lid["comforting_cat_role"] = "integrated_upper_lid"
    created.append(lid.name)
    lid_metrics[lid.name] = {
        "eye_height": round(float(eye_top - eye_bottom), 6),
        "outer_coverage": 0.044,
        "inner_coverage": 0.062,
        "face_count": len(lid.data.polygons),
    }

# Bring brows into the 0.055–0.085 eye-gap band without changing their slope.
for suffix in ("L", "R"):
    brow = bpy.data.objects[f"Cat_Eyebrow_{suffix}"]
    matrix = brow.matrix_world.copy()
    matrix.translation += Vector((0.0, -0.002, -0.050))
    brow.matrix_world = matrix

bpy.context.view_layer.update()

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_IntegratedUpperLids_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "FACE_ORBIT_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "integrated_upper_lids_1"
scene["comforting_cat_v5_dominant_defect"] = "fully_open_disc_eyes_without_lids"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "eye separation and centers",
        "pupils and highlights",
        "muzzle, nose and mouth",
        "head and ears",
        "costume",
        "limbs",
        "satchel and tail",
        "materials except new lid material assignment",
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
    "stage": "FACE_ORBIT_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "fully_open_disc_eyes_without_lids",
    "created_parts": created,
    "lid_metrics": lid_metrics,
    "brow_world_offset": [0.0, -0.002, -0.050],
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
print("COMFORTING_CAT_V5_INTEGRATED_UPPER_LIDS_A1=" + json.dumps(report, ensure_ascii=False))
