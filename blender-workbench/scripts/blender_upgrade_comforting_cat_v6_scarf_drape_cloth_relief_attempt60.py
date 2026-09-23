"""Give the front scarf drape a thin, curved cloth relief without changing its envelope."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_scarf_drape_cloth_relief_attempt60"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_tapered_plume_attempt59.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_scarf_drape_cloth_relief_attempt60.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def geometry_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted((item for item in objects if item.type == "MESH"), key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for value in obj.matrix_world:
            for component in value:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
lower = bpy.data.objects["V6_ScarfWrap_Lower"]
non_drape_objects = [obj for obj in descendants(root) if obj.name != drape.name]
non_drape_hash_before = geometry_hash(non_drape_objects)
before = bounds(drape)
preserved_source = preserve_copy(
    drape,
    "Comforting_Cat_V6",
    "A60",
    "rigid_thick_polygon_board",
)

column_count = 6
row_count = 3
front_world: list[Vector] = []
back_world: list[Vector] = []
for row in range(row_count):
    v = row / (row_count - 1)
    for column in range(column_count):
        u = column / (column_count - 1)
        top_x = -0.430 + 0.740 * u
        bottom_x = -0.340 + 0.540 * u
        x = (1.0 - v) * top_x + v * bottom_x
        x += 0.010 * math.sin(math.pi * v) * math.sin(math.tau * u)
        top_z = 2.310 + 0.040 * math.sin(math.pi * u) - 0.060 * u
        bottom_z = 2.100 - 0.030 * math.sin(math.pi * u) + 0.008 * u
        z = (1.0 - v) * top_z + v * bottom_z
        front_y = -0.387 - 0.023 * math.sin(math.pi * u) * (0.55 + 0.45 * v)
        front_world.append(Vector((x, front_y, z)))
        back_world.append(Vector((x, -0.365, z)))

world_vertices = front_world + back_world
faces: list[tuple[int, ...]] = []
layer_size = column_count * row_count
for row in range(row_count - 1):
    for column in range(column_count - 1):
        a = row * column_count + column
        b = a + 1
        c = a + column_count
        d = c + 1
        faces.append((a, c, d, b))
        faces.append((layer_size + a, layer_size + b, layer_size + d, layer_size + c))

perimeter: list[int] = []
perimeter.extend(range(column_count))
perimeter.extend(row * column_count + column_count - 1 for row in range(1, row_count))
perimeter.extend(
    (row_count - 1) * column_count + column
    for column in range(column_count - 2, -1, -1)
)
perimeter.extend(row * column_count for row in range(row_count - 2, 0, -1))
for index, front_index in enumerate(perimeter):
    next_front = perimeter[(index + 1) % len(perimeter)]
    faces.append(
        (
            front_index,
            next_front,
            layer_size + next_front,
            layer_size + front_index,
        )
    )

inverse = drape.matrix_world.inverted()
vertices = [inverse @ vertex for vertex in world_vertices]
materials = list(drape.data.materials)
mesh = bpy.data.meshes.new("V6_Scarf_FrontDrape_ClothReliefMesh_A60")
mesh.from_pydata(vertices, [], faces)
mesh.update(calc_edges=True)
old_mesh = drape.data
drape.data = mesh
for material in materials:
    drape.data.materials.append(material)
for polygon in drape.data.polygons:
    polygon.use_smooth = True
drape.data.update()
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)

for modifier in list(drape.modifiers):
    if modifier.type in {"SOLIDIFY", "BEVEL", "SUBSURF"}:
        drape.modifiers.remove(modifier)
bevel = drape.modifiers.new("V6_Scarf_FrontDrape_SoftEdge_A60", "BEVEL")
bevel.width = 0.003
bevel.segments = 2
bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = bounds(drape)
upper_bounds = bounds(upper)
lower_bounds = bounds(lower)
non_drape_hash_after = geometry_hash(non_drape_objects)
if non_drape_hash_before != non_drape_hash_after:
    raise RuntimeError("Scarf relief pass changed locked geometry or transforms")

front_y_values = [vertex.y for vertex in front_world]
outline_edges: list[float] = []
for index, vertex_index in enumerate(perimeter):
    next_index = perimeter[(index + 1) % len(perimeter)]
    outline_edges.append((front_world[vertex_index] - front_world[next_index]).length)
metrics = {
    "drape_dimensions": after["dimensions"],
    "depth_over_height": round(after["dimensions"][1] / after["dimensions"][2], 5),
    "front_surface_y_range": round(max(front_y_values) - min(front_y_values), 5),
    "front_vertex_count": len(front_world),
    "max_outline_edge": round(max(outline_edges), 5),
    "upper_z_overlap": round(overlap_1d(after, upper_bounds, 2), 5),
    "lower_z_overlap": round(overlap_1d(after, lower_bounds, 2), 5),
    "bounds_delta": [
        round(after["dimensions"][axis] - before["dimensions"][axis], 5)
        for axis in range(3)
    ],
    "non_drape_hash_before": non_drape_hash_before,
    "non_drape_hash_after": non_drape_hash_after,
}
print("A60_PRE_GATE_METRICS=" + repr(metrics))
if not 0.035 <= metrics["drape_dimensions"][1] <= 0.050:
    raise RuntimeError(f"Drape depth outside cloth target: {metrics['drape_dimensions'][1]}")
if not 0.13 <= metrics["depth_over_height"] <= 0.19:
    raise RuntimeError(f"Drape depth/height outside target: {metrics['depth_over_height']}")
if not 0.020 <= metrics["front_surface_y_range"] <= 0.035:
    raise RuntimeError("Front cloth curvature outside target")
if metrics["front_vertex_count"] < 15:
    raise RuntimeError("Front cloth grid is too sparse")
if metrics["max_outline_edge"] > 0.16:
    raise RuntimeError(f"Visible scarf edge remains too straight: {metrics['max_outline_edge']}")
if metrics["upper_z_overlap"] < 0.12 or metrics["lower_z_overlap"] < 0.12:
    raise RuntimeError("Scarf drape lost vertical contact with wrap layers")
if abs(after["dimensions"][0] - before["dimensions"][0]) > 0.03:
    raise RuntimeError("Scarf drape width envelope changed too much")
if abs(after["dimensions"][2] - before["dimensions"][2]) > 0.03:
    raise RuntimeError("Scarf drape height envelope changed too much")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ScarfDrapeClothRelief_A60"
scene["comforting_cat_v6_stage"] = "SCARF_DRAPE_CLOTH_RELIEF"
scene["comforting_cat_v6_attempt"] = 60
scene["comforting_cat_v6_dominant_defect"] = "rigid_thick_polygon_board"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "SCARF_DRAPE_CLOTH_RELIEF",
    "attempt": 60,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_thick_polygon_board",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {"changed": [drape.name], "non_drape_geometry_unchanged": True},
}
finalize_pass(
    asset=ASSET,
    root=root,
    scene=scene,
    final_blend=FINAL_BLEND,
    glb_path=GLB_PATH,
    render_dir=RENDER_DIR,
    report_dir=REPORT_DIR,
    scene_qa_path=SCENE_QA_PATH,
    report=report,
)
