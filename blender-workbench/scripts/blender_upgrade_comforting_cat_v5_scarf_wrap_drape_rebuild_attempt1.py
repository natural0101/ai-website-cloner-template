"""Rebuild the rigid ring scarf as layered wraps with front and back drapes."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v5_scarf_wrap_drape_rebuild_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_front_inset_length_attempt2.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_scarf_wrap_drape_rebuild_attempt1.blend"
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
old_wrap = bpy.data.objects["Cat_ScarfWrap"]
old_drape = bpy.data.objects["Cat_ScarfLowerDrape"]
before = {
    "Cat_ScarfWrap": bounds(old_wrap),
    "Cat_ScarfLowerDrape": bounds(old_drape),
}
collection = old_wrap.users_collection[0]
wrap_material = old_wrap.data.materials[0]
drape_material = old_drape.data.materials[0] if old_drape.data.materials else wrap_material

for source, source_name in (
    (old_wrap, "Cat_ScarfWrap_SOURCE_V5_REBUILD_A1"),
    (old_drape, "Cat_ScarfLowerDrape_SOURCE_V5_REBUILD_A1"),
):
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = source_name
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "rigid_ring_and_shallow_shelf"


def add_torus_band(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
    center_z: float,
    scale_x: float,
    scale_y: float,
    tilt: float,
    phase: float,
) -> None:
    major_segments = 64
    minor_segments = 20
    major_radius = 0.33
    minor_radius = 0.20
    start = len(vertices)
    for major_index in range(major_segments):
        u = math.tau * major_index / major_segments
        fold_offset = tilt * math.sin(u + phase)
        for minor_index in range(minor_segments):
            v = math.tau * minor_index / minor_segments
            radial = major_radius + minor_radius * math.cos(v)
            vertices.append(
                (
                    scale_x * radial * math.cos(u),
                    scale_y * radial * math.sin(u),
                    center_z + minor_radius * math.sin(v) + fold_offset,
                )
            )
    for major_index in range(major_segments):
        next_major = (major_index + 1) % major_segments
        for minor_index in range(minor_segments):
            next_minor = (minor_index + 1) % minor_segments
            a = start + major_index * minor_segments + minor_index
            b = start + next_major * minor_segments + minor_index
            c = start + next_major * minor_segments + next_minor
            d = start + major_index * minor_segments + next_minor
            faces.append((a, b, c, d))


wrap_vertices: list[tuple[float, float, float]] = []
wrap_faces: list[tuple[int, int, int, int]] = []
add_torus_band(wrap_vertices, wrap_faces, 2.245, 1.22, 0.90, 0.032, 0.2)
add_torus_band(wrap_vertices, wrap_faces, 2.055, 1.17, 0.94, -0.027, 1.3)
wrap_mesh = bpy.data.meshes.new("Cat_ScarfWrap_LayeredMesh_A1")
wrap_mesh.from_pydata(wrap_vertices, [], wrap_faces)
wrap_mesh.update(calc_edges=True)
wrap = bpy.data.objects.new("Cat_ScarfWrap", wrap_mesh)
collection.objects.link(wrap)
wrap.parent = root
wrap.matrix_parent_inverse = root.matrix_world.inverted()
wrap.matrix_world = Matrix.Identity(4)
wrap.data.materials.append(wrap_material)
for polygon in wrap.data.polygons:
    polygon.use_smooth = True
wrap["comforting_cat_role"] = "layered_soft_scarf_wrap"


def add_closed_drape(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    points_xz: list[tuple[float, float]],
    y_outer: float,
    y_inner: float,
) -> None:
    start = len(vertices)
    count = len(points_xz)
    vertices.extend((x, y_outer, z) for x, z in points_xz)
    vertices.extend((x, y_inner, z) for x, z in points_xz)
    faces.append(tuple(reversed(range(start, start + count))))
    faces.append(tuple(range(start + count, start + 2 * count)))
    for index in range(count):
        next_index = (index + 1) % count
        faces.append(
            (
                start + index,
                start + count + index,
                start + count + next_index,
                start + next_index,
            )
        )


drape_vertices: list[tuple[float, float, float]] = []
drape_faces: list[tuple[int, ...]] = []
front_points = [
    (-0.55, 2.30),
    (-0.16, 2.38),
    (0.55, 2.27),
    (0.45, 2.06),
    (0.12, 1.84),
    (-0.28, 1.93),
    (-0.50, 2.08),
]
back_points = [
    (-0.58, 2.28),
    (0.58, 2.28),
    (0.47, 2.08),
    (0.08, 1.86),
    (-0.42, 2.02),
]
add_closed_drape(drape_vertices, drape_faces, front_points, -0.565, -0.485)
add_closed_drape(drape_vertices, drape_faces, back_points, 0.515, 0.435)
drape_mesh = bpy.data.meshes.new("Cat_ScarfDrapes_ClosedMesh_A1")
drape_mesh.from_pydata(drape_vertices, [], drape_faces)
drape_mesh.update(calc_edges=True)
drape = bpy.data.objects.new("Cat_ScarfLowerDrape", drape_mesh)
collection.objects.link(drape)
drape.parent = root
drape.matrix_parent_inverse = root.matrix_world.inverted()
drape.matrix_world = Matrix.Identity(4)
drape.data.materials.append(drape_material)
for polygon in drape.data.polygons:
    polygon.use_smooth = False
drape["comforting_cat_role"] = "front_and_back_pointed_scarf_drapes"
bevel = drape.modifiers.new("ScarfDrapeSoftEdge", "BEVEL")
bevel.width = 0.018
bevel.segments = 3
bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = {
    "Cat_ScarfWrap": bounds(wrap),
    "Cat_ScarfLowerDrape": bounds(drape),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_ScarfWrapDrapeRebuild_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "SCARF_WRAP_DRAPE_REBUILD"
scene["comforting_cat_v5_geometry_attempt"] = "scarf_wrap_drape_rebuild_1"
scene["comforting_cat_v5_dominant_defect"] = "rigid_ring_scarf_with_oversized_hole"
scene["comforting_cat_v5_preserved_sources"] = json.dumps(
    [old_wrap.name, old_drape.name]
)
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head and face",
        "robe shell, hem and front inset",
        "body, legs and paws",
        "arms",
        "satchel and tail",
        "materials",
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
    "stage": "SCARF_WRAP_DRAPE_REBUILD",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_ring_scarf_with_oversized_hole",
    "preserved_sources": [old_wrap.name, old_drape.name],
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
print("COMFORTING_CAT_V5_SCARF_REBUILD_A1=" + json.dumps(report, ensure_ascii=False))
