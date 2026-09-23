"""Rebuild the A79 front tunic plate as a closed, curved asymmetric cloth panel."""

from __future__ import annotations

import bmesh
import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_front_tunic_curved_cloth_attempt80"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_unified_muzzle_attempt79.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_front_tunic_curved_cloth_attempt80.blend"
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
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def smoothstep(value: float) -> float:
    t = max(0.0, min(1.0, value))
    return t * t * (3.0 - 2.0 * t)


def boundary_edge_count(mesh: bpy.types.Mesh) -> int:
    usage: dict[tuple[int, int], int] = {}
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            end = vertices[(index + 1) % len(vertices)]
            edge = tuple(sorted((start, end)))
            usage[edge] = usage.get(edge, 0) + 1
    return sum(1 for count in usage.values() if count != 2)


root = bpy.data.objects["CatV6_Root"]
tunic = bpy.data.objects["V6_FrontTunic"]
robe = bpy.data.objects["V6_Robe"]
locked_objects = [obj for obj in descendants(root) if obj.name != tunic.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(tunic)
robe_bounds = bounds(robe)
topology_before = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
    boundary_edge_count(tunic.data),
)
preserved_sources = [
    preserve_copy(tunic, "Comforting_Cat_V6", "A80", "flat_open_tunic_plate")
]
removed_modifiers = [modifier.name for modifier in tunic.modifiers]
for modifier in list(tunic.modifiers):
    tunic.modifiers.remove(modifier)

columns = 7
rows = 9
top_z = before["max"][2]
bottom_z = before["min"][2] + 0.018
height = top_z - bottom_z
front_center_y = before["min"][1] - 0.004
thickness = 0.022
world_front: list[Vector] = []

for row in range(rows):
    t = row / (rows - 1)
    z_base = top_z - height * t
    if t <= 0.52:
        width = 0.640 + (0.700 - 0.640) * smoothstep(t / 0.52)
    else:
        width = 0.700 + (0.565 - 0.700) * smoothstep((t - 0.52) / 0.48)
    for column in range(columns):
        u = -1.0 + 2.0 * column / (columns - 1)
        x = 0.5 * width * u - 0.012 * smoothstep((t - 0.45) / 0.55)
        center_bulge = 0.046 * (1.0 - u * u) * (0.35 + 0.65 * smoothstep(t / 0.70))
        edge_embed = 0.012 * abs(u) ** 1.7
        y = front_center_y - center_bulge + edge_embed
        hem_raise = 0.0
        if row == rows - 1:
            hem_raise += 0.036 * abs(u) ** 1.6
            hem_raise += 0.082 * smoothstep((u + 0.10) / 1.10)
        elif row == rows - 2:
            hem_raise += 0.030 * smoothstep((u + 0.10) / 1.10)
        z = z_base + hem_raise
        world_front.append(Vector((x, y, z)))

world_back = [Vector((point.x, point.y + thickness, point.z)) for point in world_front]
world_vertices = world_front + world_back
faces: list[tuple[int, ...]] = []

def front_index(row: int, column: int) -> int:
    return row * columns + column


offset = len(world_front)
for row in range(rows - 1):
    for column in range(columns - 1):
        a = front_index(row, column)
        b = front_index(row, column + 1)
        c = front_index(row + 1, column + 1)
        d = front_index(row + 1, column)
        faces.append((a, d, c, b))
        faces.append((offset + a, offset + b, offset + c, offset + d))

boundary: list[int] = []
boundary.extend(front_index(0, column) for column in range(columns))
boundary.extend(front_index(row, columns - 1) for row in range(1, rows))
boundary.extend(front_index(rows - 1, column) for column in range(columns - 2, -1, -1))
boundary.extend(front_index(row, 0) for row in range(rows - 2, 0, -1))
for index, current in enumerate(boundary):
    following = boundary[(index + 1) % len(boundary)]
    faces.append((current, following, offset + following, offset + current))

material = tunic.data.materials[0] if tunic.data.materials else None
inverse = tunic.matrix_world.inverted()
local_vertices = [inverse @ vertex for vertex in world_vertices]
mesh = bpy.data.meshes.new("V6_FrontTunic_CurvedClosedCloth_A80_Mesh")
mesh.from_pydata(local_vertices, [], faces)
mesh.validate(verbose=True)
mesh.update()
bm = bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
tunic.data = mesh
if material is not None:
    mesh.materials.append(material)
for polygon in mesh.polygons:
    polygon.use_smooth = True

bpy.context.view_layer.update()
after = bounds(tunic)
topology_after = (
    len(tunic.data.vertices),
    len(tunic.data.edges),
    len(tunic.data.polygons),
    boundary_edge_count(tunic.data),
)
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A80 changed locked A79 geometry outside V6_FrontTunic")
if topology_after[3] != 0:
    raise RuntimeError(f"A80 tunic is not closed/manifold: {topology_after[3]} boundary edges")
if not 0.66 <= after["dimensions"][0] <= 0.75:
    raise RuntimeError(f"A80 tunic width outside target: {after['dimensions'][0]}")
if not 0.018 <= after["dimensions"][1] <= 0.095:
    raise RuntimeError(f"A80 tunic depth outside target: {after['dimensions'][1]}")
robe_width_ratio = after["dimensions"][0] / robe_bounds["dimensions"][0]
if not 0.48 <= robe_width_ratio <= 0.53:
    raise RuntimeError(f"A80 tunic/robe width ratio outside target: {robe_width_ratio}")

metrics = {
    "before": before,
    "after": after,
    "robe_bounds": robe_bounds,
    "robe_width_ratio": round(robe_width_ratio, 5),
    "front_center_bulge": 0.046,
    "closed_thickness": thickness,
    "right_hem_raise": 0.082,
    "topology_before_v_e_f_boundary": topology_before,
    "topology_after_v_e_f_boundary": topology_after,
    "removed_legacy_modifiers": removed_modifiers,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A80_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FrontTunicCurvedCloth_A80"
scene["comforting_cat_v6_stage"] = "FRONT_TUNIC_CURVED_CLOTH"
scene["comforting_cat_v6_attempt"] = 80
scene["comforting_cat_v6_dominant_defect"] = "flat_open_front_tunic_shield"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FRONT_TUNIC_CURVED_CLOTH",
    "attempt": 80,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_open_front_tunic_shield",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_FrontTunic"],
        "preserved": [
            "A79 head/face/muzzle",
            "robe/scarf/satchel/arms",
            "legs",
            "tail",
            "camera",
            "lights",
            "materials",
        ],
    },
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
