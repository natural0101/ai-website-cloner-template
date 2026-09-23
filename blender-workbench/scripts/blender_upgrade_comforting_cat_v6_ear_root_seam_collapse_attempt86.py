"""Collapse only the rejected A85 lower ear bridge beneath the head surface."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_ear_root_seam_collapse_attempt86"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_pointed_ear_cup_attempt85.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_ear_root_seam_collapse_attempt86.blend"
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


def interpolate(z: float, rows: list[tuple[float, float]]) -> float:
    if z <= rows[0][0]:
        return rows[0][1]
    if z >= rows[-1][0]:
        return rows[-1][1]
    for (z0, value0), (z1, value1) in zip(rows, rows[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            t = t * t * (3.0 - 2.0 * t)
            return value0 * (1.0 - t) + value1 * t
    return rows[-1][1]


def upper_hash(obj: bpy.types.Object, threshold: float = 3.17001) -> str:
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if world.z >= threshold:
            digest.update(
                f"{vertex.index}:{world.x:.9f},{world.y:.9f},{world.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def boundary_edge_count(mesh: bpy.types.Mesh) -> int:
    usage: dict[tuple[int, int], int] = {}
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            end = vertices[(index + 1) % len(vertices)]
            edge = tuple(sorted((start, end)))
            usage[edge] = usage.get(edge, 0) + 1
    return sum(1 for count in usage.values() if count != 2)


front_center = [(2.935, 0.439), (3.060, 0.443), (3.170, 0.448)]
front_half = [(2.935, 0.160), (3.060, 0.166), (3.170, 0.142)]
front_y = [(2.935, 0.020), (3.060, -0.125), (3.170, -0.115)]
back_center = [(2.935, 0.439), (3.060, 0.443), (3.170, 0.448)]
back_half = [(2.935, 0.110), (3.060, 0.125), (3.170, 0.108)]
back_y = [(2.935, 0.075), (3.060, 0.055), (3.170, 0.070)]


root = bpy.data.objects["CatV6_Root"]
outer_names = ["V6_Ear_L", "V6_Ear_R"]
ear_names = outer_names + ["V6_InnerEar_L", "V6_InnerEar_R"]
locked_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
locked_hash_before = geometry_hash(locked_objects)
before = {name: bounds(bpy.data.objects[name]) for name in ear_names}
topology_before = {
    name: (
        len(bpy.data.objects[name].data.vertices),
        len(bpy.data.objects[name].data.edges),
        len(bpy.data.objects[name].data.polygons),
    )
    for name in ear_names
}
upper_hash_before = {name: upper_hash(bpy.data.objects[name]) for name in outer_names}
preserved_sources = [
    preserve_copy(bpy.data.objects[name], "Comforting_Cat_V6", "A86", "visible_lower_ear_shelf")
    for name in outer_names
]

front_count = 21
apex_index = 10
back_indices = list(range(21, 31)) + [apex_index] + list(range(31, 41))
inner_start = 41
cavity_start = 62

for side, sign in (("L", -1.0), ("R", 1.0)):
    obj = bpy.data.objects[f"V6_Ear_{side}"]
    inverse = obj.matrix_world.inverted()
    front_indices = list(range(front_count))
    for loop_index, vertex_index in enumerate(front_indices):
        if loop_index == apex_index:
            continue
        vertex = obj.data.vertices[vertex_index]
        world = obj.matrix_world @ vertex.co
        if world.z > 3.17001:
            continue
        is_root = loop_index in (0, front_count - 1)
        z = 2.935 if is_root else world.z
        center = sign * interpolate(z, front_center)
        half = interpolate(z, front_half)
        world.x = center - half if loop_index < apex_index else center + half
        world.y = interpolate(z, front_y)
        world.z = z
        vertex.co = inverse @ world

    for loop_index, vertex_index in enumerate(back_indices):
        if loop_index == apex_index:
            continue
        vertex = obj.data.vertices[vertex_index]
        world = obj.matrix_world @ vertex.co
        if world.z > 3.17001:
            continue
        is_root = loop_index in (0, front_count - 1)
        z = 2.935 if is_root else world.z
        center = sign * interpolate(z, back_center)
        half = interpolate(z, back_half)
        world.x = center - half if loop_index < apex_index else center + half
        world.y = interpolate(z, back_y)
        world.z = z
        vertex.co = inverse @ world

    for offset in range(front_count):
        vertex = obj.data.vertices[cavity_start + offset]
        world = obj.matrix_world @ vertex.co
        if world.z <= 3.17001:
            world.y = interpolate(world.z, back_y) - 0.010
            vertex.co = inverse @ world
    obj.data.update()

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in ear_names}
topology_after = {
    name: (
        len(bpy.data.objects[name].data.vertices),
        len(bpy.data.objects[name].data.edges),
        len(bpy.data.objects[name].data.polygons),
    )
    for name in ear_names
}
upper_hash_after = {name: upper_hash(bpy.data.objects[name]) for name in outer_names}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A86 changed locked non-ear A84 geometry")
if topology_before != topology_after:
    raise RuntimeError("A86 changed A85 ear topology")
if upper_hash_before != upper_hash_after:
    raise RuntimeError("A86 changed the accepted A85 cup/wedge above Z=3.17")

per_side: dict[str, dict[str, object]] = {}
for side in ("L", "R"):
    obj = bpy.data.objects[f"V6_Ear_{side}"]
    inverse = obj.matrix_world.inverted()
    front_root = obj.matrix_world @ obj.data.vertices[0].co
    back_root = obj.matrix_world @ obj.data.vertices[back_indices[0]].co
    root_depth = back_root.y - front_root.y
    z306_front = interpolate(3.060, front_y)
    z306_back = interpolate(3.060, back_y)
    z306_ratio = interpolate(3.060, back_half) / interpolate(3.060, front_half)
    per_side[side] = {
        "bounds": after[obj.name],
        "root_front": list(front_root),
        "root_back": list(back_root),
        "root_depth": round(root_depth, 5),
        "z306_depth": round(z306_back - z306_front, 5),
        "z306_back_over_front_halfwidth": round(z306_ratio, 5),
        "outer_boundary_edges": boundary_edge_count(obj.data),
    }
    if not 2.925 <= front_root.z <= 2.945:
        raise RuntimeError(f"{side} hidden root Z outside A86 target")
    if root_depth > 0.060:
        raise RuntimeError(f"{side} hidden root remains too deep")
    if not 0.175 <= z306_back - z306_front <= 0.190:
        raise RuntimeError(f"{side} visible lower depth outside A86 target")
    if not 0.72 <= z306_ratio <= 0.78:
        raise RuntimeError(f"{side} lower back shell still too wide")
    if boundary_edge_count(obj.data) != 0:
        raise RuntimeError(f"{side} outer ear lost manifold closure")

metrics = {
    "per_side": per_side,
    "upper_hash_before": upper_hash_before,
    "upper_hash_after": upper_hash_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A86_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EarRootSeamCollapse_A86"
scene["comforting_cat_v6_stage"] = "EAR_ROOT_SEAM_COLLAPSE"
scene["comforting_cat_v6_attempt"] = 86
scene["comforting_cat_v6_dominant_defect"] = "ear_lower_shelf_hooks_and_back_shell_double_contour"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "EAR_ROOT_SEAM_COLLAPSE",
    "attempt": 86,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "ear_lower_shelf_hooks_and_back_shell_double_contour",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Ear_L/R lower front/back/cavity bridge below Z=3.17"],
        "preserved": [
            "A85 cup/wedge above Z=3.17",
            "A85 inner dishes",
            "A84 tunic",
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
