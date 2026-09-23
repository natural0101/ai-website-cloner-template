"""Build head-conforming ear saddles with hidden anchors and pointed upper cups."""

from __future__ import annotations

import bmesh
import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ASSET = "comforting_cat_v6_head_conforming_ear_saddle_attempt87"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tunic_balanced_reveal_attempt84.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_conforming_ear_saddle_attempt87.blend"
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


def boundary_edge_count(mesh: bpy.types.Mesh) -> int:
    usage: dict[tuple[int, int], int] = {}
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            end = vertices[(index + 1) % len(vertices)]
            edge = tuple(sorted((start, end)))
            usage[edge] = usage.get(edge, 0) + 1
    return sum(1 for count in usage.values() if count != 2)


def build_world_bvh(obj: bpy.types.Object) -> BVHTree:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
    tree = BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    evaluated.to_mesh_clear()
    return tree


raycast_fallbacks: list[tuple[float, float, str]] = []


def surface_y(tree: BVHTree, x: float, z: float, side: str) -> float:
    if side == "front":
        origin = Vector((x, -2.0, z))
        direction = Vector((0.0, 1.0, 0.0))
    else:
        origin = Vector((x, 2.0, z))
        direction = Vector((0.0, -1.0, 0.0))
    location, _normal, _index, _distance = tree.ray_cast(origin, direction, 4.0)
    if location is not None:
        return location.y
    nearest, _normal, _index, _distance = tree.find_nearest(Vector((x, 0.0, z)))
    if nearest is None:
        raise RuntimeError(f"No head surface near x={x}, z={z}")
    raycast_fallbacks.append((x, z, side))
    return nearest.y


def replace_mesh(
    obj: bpy.types.Object,
    world_vertices: list[Vector],
    faces: list[tuple[int, ...]],
    suffix: str,
) -> None:
    material = obj.data.materials[0] if obj.data.materials else None
    inverse = obj.matrix_world.inverted()
    mesh = bpy.data.meshes.new(f"{obj.name}_{suffix}_Mesh")
    mesh.from_pydata([inverse @ vertex for vertex in world_vertices], [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.data = mesh
    if material is not None:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True


outer_center = [(3.000, 0.441), (3.170, 0.448), (3.285, 0.454), (3.370, 0.459), (3.415, 0.462)]
front_half = [(3.000, 0.100), (3.080, 0.135), (3.170, 0.142), (3.285, 0.098), (3.370, 0.045), (3.415, 0.000)]
back_half = [(3.000, 0.090), (3.080, 0.105), (3.170, 0.108), (3.285, 0.085), (3.370, 0.034), (3.415, 0.000)]
front_upper_y = [(3.170, -0.115), (3.285, -0.080), (3.370, -0.015), (3.415, 0.055)]
back_upper_y = [(3.170, 0.070), (3.285, 0.075), (3.370, 0.055), (3.415, 0.055)]

inner_center = [(3.040, 0.442), (3.170, 0.448), (3.285, 0.454), (3.350, 0.458), (3.382, 0.460)]
inner_half = [(3.040, 0.070), (3.100, 0.092), (3.170, 0.102), (3.285, 0.066), (3.350, 0.028), (3.382, 0.000)]
inner_lip_y = [(3.170, -0.082), (3.285, -0.045), (3.350, 0.002), (3.382, 0.032)]
inner_dish_y = [(3.170, -0.020), (3.285, 0.010), (3.350, 0.028), (3.382, 0.032)]


def build_loops(sign: float, tree: BVHTree, samples: int = 13) -> tuple[list[Vector], list[Vector], list[Vector]]:
    front_sides: list[tuple[Vector, Vector]] = []
    back_sides: list[tuple[Vector, Vector]] = []
    for sample in range(samples):
        t = sample / (samples - 1)
        z = 3.000 + (3.415 - 3.000) * t
        center = sign * interpolate(z, outer_center)
        front_radius = interpolate(z, front_half)
        back_radius = interpolate(z, back_half)
        front_points: list[Vector] = []
        back_points: list[Vector] = []
        for lateral_sign in (-1.0, 1.0):
            front_x = center + lateral_sign * front_radius
            back_x = center + lateral_sign * back_radius
            if sample == 0:
                front_surface = surface_y(tree, front_x, z, "front")
                back_surface = surface_y(tree, back_x, z, "back")
                anchor_y = 0.5 * (front_surface + back_surface)
                front_points.append(Vector((front_x, anchor_y, z)))
                back_points.append(Vector((front_x, anchor_y, z)))
            elif z < 3.170:
                front_points.append(Vector((front_x, surface_y(tree, front_x, z, "front") + 0.025, z)))
                back_points.append(Vector((back_x, surface_y(tree, back_x, z, "back") - 0.025, z)))
            else:
                front_points.append(Vector((front_x, interpolate(z, front_upper_y), z)))
                back_points.append(Vector((back_x, interpolate(z, back_upper_y), z)))
        front_sides.append((front_points[0], front_points[1]))
        back_sides.append((back_points[0], back_points[1]))

    front_loop = [pair[0] for pair in front_sides[:-1]] + [front_sides[-1][0]] + [pair[1] for pair in reversed(front_sides[:-1])]
    back_loop = [pair[0] for pair in back_sides[:-1]] + [front_sides[-1][0]] + [pair[1] for pair in reversed(back_sides[:-1])]

    inner_sides: list[tuple[Vector, Vector]] = []
    for sample in range(samples):
        t = sample / (samples - 1)
        z = 3.040 + (3.382 - 3.040) * t
        center = sign * interpolate(z, inner_center)
        radius = interpolate(z, inner_half)
        points: list[Vector] = []
        for lateral_sign in (-1.0, 1.0):
            x = center + lateral_sign * radius
            if z < 3.170:
                y = surface_y(tree, x, z, "front") + 0.035
            else:
                y = interpolate(z, inner_lip_y)
            points.append(Vector((x, y, z)))
        inner_sides.append((points[0], points[1]))
    inner_loop = [pair[0] for pair in inner_sides[:-1]] + [inner_sides[-1][0]] + [pair[1] for pair in reversed(inner_sides[:-1])]
    return front_loop, back_loop, inner_loop


def build_outer(obj: bpy.types.Object, sign: float, tree: BVHTree) -> dict[str, object]:
    front_loop, back_loop_raw, inner_loop = build_loops(sign, tree)
    count = len(front_loop)
    apex = count // 2
    shared = {0, apex, count - 1}
    vertices = list(front_loop)
    back_indices: list[int] = []
    for index, point in enumerate(back_loop_raw):
        if index in shared:
            back_indices.append(index)
        else:
            back_indices.append(len(vertices))
            vertices.append(point)
    inner_indices = list(range(len(vertices), len(vertices) + count))
    vertices.extend(inner_loop)
    cavity_loop: list[Vector] = []
    for point in inner_loop:
        if point.z < 3.170:
            cavity_y = point.y + 0.055
        else:
            cavity_y = interpolate(point.z, back_upper_y) - 0.015
        cavity_loop.append(Vector((point.x, cavity_y, point.z)))
    cavity_indices = list(range(len(vertices), len(vertices) + count))
    vertices.extend(cavity_loop)

    front_indices = list(range(count))
    faces: list[tuple[int, ...]] = []
    for index in range(count):
        following = (index + 1) % count
        faces.append((front_indices[index], front_indices[following], inner_indices[following], inner_indices[index]))
        faces.append((inner_indices[index], inner_indices[following], cavity_indices[following], cavity_indices[index]))
        front_a, front_b = front_indices[index], front_indices[following]
        back_a, back_b = back_indices[index], back_indices[following]
        if front_a == back_a and front_b == back_b:
            continue
        if front_a == back_a:
            faces.append((front_a, front_b, back_b))
        elif front_b == back_b:
            faces.append((front_a, front_b, back_a))
        else:
            faces.append((front_a, front_b, back_b, back_a))
    faces.append(tuple(reversed(cavity_indices)))
    faces.append(tuple(back_indices))
    replace_mesh(obj, vertices, faces, "HeadSaddleA87")
    return {
        "loop_vertices": count,
        "shared_indices": sorted(shared),
        "shared_apex": list(front_loop[apex]),
        "root_front_left": list(front_loop[0]),
        "root_back_left": list(back_loop_raw[0]),
    }


def build_dish(obj: bpy.types.Object, sign: float, tree: BVHTree) -> dict[str, object]:
    rows = 10
    columns = 7
    row_indices: list[list[int]] = []
    vertices: list[Vector] = []
    for row in range(rows - 1):
        t = row / (rows - 1)
        z = 3.080 + (3.382 - 3.080) * t
        center = sign * interpolate(z, inner_center)
        radius = interpolate(z, inner_half)
        indices: list[int] = []
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            x = center + radius * u
            if z < 3.170:
                boundary_y = surface_y(tree, x, z, "front") + 0.041
                dish_center_y = boundary_y + 0.028
            else:
                boundary_y = interpolate(z, inner_lip_y) + 0.006
                dish_center_y = interpolate(z, inner_dish_y)
            y = boundary_y + (dish_center_y - boundary_y) * (1.0 - u * u)
            indices.append(len(vertices))
            vertices.append(Vector((x, y, z)))
        row_indices.append(indices)
    tip_index = len(vertices)
    vertices.append(Vector((sign * 0.460, 0.032, 3.382)))
    faces: list[tuple[int, ...]] = []
    for row in range(len(row_indices) - 1):
        for column in range(columns - 1):
            faces.append((row_indices[row][column], row_indices[row + 1][column], row_indices[row + 1][column + 1], row_indices[row][column + 1]))
    for column in range(columns - 1):
        faces.append((row_indices[-1][column], tip_index, row_indices[-1][column + 1]))
    replace_mesh(obj, vertices, faces, "HeadSaddleDishA87")
    return {"rows": rows, "columns": columns, "tip": list(vertices[tip_index])}


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
tree = build_world_bvh(head)
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
locked_hash_before = geometry_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A87", "separate_closed_root_shell") for obj in ears
]
removed_modifiers: dict[str, list[str]] = {}
for obj in ears:
    removed_modifiers[obj.name] = [modifier.name for modifier in obj.modifiers]
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)

construction: dict[str, dict[str, object]] = {}
for side, sign in (("L", -1.0), ("R", 1.0)):
    construction[side] = {
        "outer": build_outer(bpy.data.objects[f"V6_Ear_{side}"], sign, tree),
        "dish": build_dish(bpy.data.objects[f"V6_InnerEar_{side}"], sign, tree),
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A87 changed locked A84 geometry outside the four ears")

per_side: dict[str, dict[str, object]] = {}
for side in ("L", "R"):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer_bounds = after[outer.name]
    inner_bounds = after[inner.name]
    boundary_edges = boundary_edge_count(outer.data)
    per_side[side] = {
        "outer": outer_bounds,
        "inner": inner_bounds,
        "outer_boundary_edges": boundary_edges,
        "opening_width_ratio": round(inner_bounds["dimensions"][0] / outer_bounds["dimensions"][0], 5),
        "protrusion_above_crown": round(outer_bounds["max"][2] - bounds(head)["max"][2], 5),
    }
    if boundary_edges != 0:
        raise RuntimeError(f"{side} A87 outer saddle is not manifold")
    if not 0.165 <= outer_bounds["max"][2] - bounds(head)["max"][2] <= 0.185:
        raise RuntimeError(f"{side} A87 apex height outside target")
    if not 0.66 <= inner_bounds["dimensions"][0] / outer_bounds["dimensions"][0] <= 0.73:
        raise RuntimeError(f"{side} A87 opening width ratio outside target")

metrics = {
    "per_side": per_side,
    "construction": construction,
    "raycast_fallbacks": raycast_fallbacks,
    "removed_modifiers": removed_modifiers,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A87_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadConformingEarSaddle_A87"
scene["comforting_cat_v6_stage"] = "HEAD_CONFORMING_EAR_SADDLE"
scene["comforting_cat_v6_attempt"] = 87
scene["comforting_cat_v6_dominant_defect"] = "separate_ear_shell_intersection_gash"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_CONFORMING_EAR_SADDLE",
    "attempt": 87,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "separate_ear_shell_intersection_gash",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ear_names,
        "preserved": [
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
