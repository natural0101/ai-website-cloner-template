from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(
    os.environ.get(
        "TEAMON_PROJECT_ROOT",
        r"C:\Users\se-20\OneDrive\Рабочий стол\2. личные проекты\ai-website-cloner-template",
    )
)
BLEND_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "blend"
    / "teamon_reference_v25_shadow_composed.blend"
)
PREVIEW_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "previews"
    / "teamon-v25-shadow-hero-shell.png"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "reports"
    / "teamon_reference_v25_hero_shell_report.json"
)


def mesh_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


hand_root = bpy.data.objects["TEAMON_ShadowBakedRoot"]
shell_bodies = {"rh_palm", "rh_wrist", "rh_forearm"}
source_shell_objects = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH"
    and obj.name.startswith("TEAMON_V")
    and str(obj.get("mjcf_body", "")) in shell_bodies
    and not obj.hide_render
]
if len(source_shell_objects) != 4:
    raise RuntimeError(
        f"Expected palm, wrist, and two forearm shells; received {len(source_shell_objects)}"
    )

source_collection = bpy.data.collections.new("TEAMON_V25_HeroShell_SOURCE")
bpy.context.scene.collection.children.link(source_collection)
duplicates: list[bpy.types.Object] = []
for source in source_shell_objects:
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    duplicate.name = f"TEAMON_V25_SOURCE_{source.name}"
    source_collection.objects.link(duplicate)
    world = source.matrix_world.copy()
    duplicate.parent = None
    duplicate.matrix_world = world
    duplicate.hide_render = False
    duplicate.hide_set(False)
    duplicates.append(duplicate)

bpy.ops.object.select_all(action="DESELECT")
for duplicate in duplicates:
    duplicate.select_set(True)
bpy.context.view_layer.objects.active = duplicates[0]
bpy.ops.object.join()
hero_shell = bpy.context.active_object
hero_shell.name = "TEAMON_V25_HandHeroShell"

# Imported MJCF meshes carry a small object scale around large raw vertices.
# Voxel remesh uses local coordinates, so applying rotation/scale first avoids
# allocating an enormous grid and keeps the requested world-space voxel size.
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

remesh = hero_shell.modifiers.new(name="TEAMON_V25_VoxelUnion", type="REMESH")
remesh.mode = "VOXEL"
remesh.voxel_size = 0.052
remesh.use_smooth_shade = True
bpy.context.view_layer.objects.active = hero_shell
bpy.ops.object.modifier_apply(modifier=remesh.name)

smooth = hero_shell.modifiers.new(name="TEAMON_V25_SoftSurface", type="SMOOTH")
smooth.factor = 0.28
smooth.iterations = 4
bpy.ops.object.modifier_apply(modifier=smooth.name)
for polygon in hero_shell.data.polygons:
    polygon.use_smooth = True

white_material = next(
    material
    for material in bpy.data.materials
    if "TEAMON_Robot_White" in material.name
)
hero_shell.data.materials.clear()
hero_shell.data.materials.append(white_material)
world = hero_shell.matrix_world.copy()
hero_shell.parent = hand_root
hero_shell.matrix_world = world
hero_shell["export"] = True
hero_shell["hero_shell"] = True

for source in source_shell_objects:
    source.hide_render = True
    source.hide_set(True)
    source["v25_hidden_by_hero_shell"] = True

bpy.context.view_layer.update()
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW_PATH)
bpy.ops.render.render(write_still=True)

low, high = mesh_bounds(hero_shell)
hero_shell.data.calc_loop_triangles()
report = {
    "asset": "TEAMON v25 continuous hand hero shell",
    "mode": "HYBRID_HERO",
    "source_objects_preserved": [obj.name for obj in source_shell_objects],
    "source_objects_hidden": all(obj.hide_render for obj in source_shell_objects),
    "output_object": hero_shell.name,
    "voxel_size": 0.052,
    "smooth_factor": 0.28,
    "smooth_iterations": 4,
    "bounds": {"min": list(low), "max": list(high)},
    "triangles": len(hero_shell.data.loop_triangles),
    "preview": str(PREVIEW_PATH),
    "checkpoint": str(BLEND_PATH),
    "status": "geometry_visual_gate",
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
