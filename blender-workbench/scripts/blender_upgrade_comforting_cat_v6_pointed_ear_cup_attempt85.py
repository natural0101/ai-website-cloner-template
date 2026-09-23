"""Rebuild A84 ears as manifold pointed wedges with recessed multi-loop dishes."""

from __future__ import annotations

import bmesh
import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_pointed_ear_cup_attempt85"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_pointed_ear_cup_attempt85.blend"
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


outer_z = [2.995, 3.060, 3.170, 3.285, 3.370, 3.415]
outer_center = [(2.995, 0.441), (3.060, 0.443), (3.170, 0.448), (3.285, 0.454), (3.370, 0.459), (3.415, 0.462)]
outer_front_half = [(2.995, 0.172), (3.060, 0.166), (3.170, 0.142), (3.285, 0.098), (3.370, 0.045), (3.415, 0.000)]
outer_front_y = [(2.995, -0.120), (3.060, -0.125), (3.170, -0.115), (3.285, -0.080), (3.370, -0.015), (3.415, 0.055)]
outer_back_half = [(2.995, 0.158), (3.060, 0.152), (3.170, 0.128), (3.285, 0.085), (3.370, 0.034), (3.415, 0.000)]
outer_back_y = [(2.995, 0.105), (3.060, 0.105), (3.170, 0.095), (3.285, 0.075), (3.370, 0.055), (3.415, 0.055)]

inner_center = [(3.070, 0.444), (3.170, 0.448), (3.285, 0.454), (3.350, 0.458), (3.382, 0.460)]
inner_half = [(3.070, 0.118), (3.170, 0.102), (3.285, 0.066), (3.350, 0.028), (3.382, 0.000)]
inner_lip_y = [(3.070, -0.094), (3.170, -0.082), (3.285, -0.045), (3.350, 0.002), (3.382, 0.032)]
inner_dish_y = [(3.070, -0.040), (3.170, -0.020), (3.285, 0.010), (3.350, 0.028), (3.382, 0.032)]


def profile_loop(
    sign: float,
    z_start: float,
    z_end: float,
    samples: int,
    center_rows: list[tuple[float, float]],
    half_rows: list[tuple[float, float]],
    y_rows: list[tuple[float, float]],
) -> list[Vector]:
    side_rows: list[tuple[float, float, float]] = []
    for sample in range(samples):
        t = sample / (samples - 1)
        z = z_start + (z_end - z_start) * t
        side_rows.append((
            sign * interpolate(z, center_rows),
            interpolate(z, half_rows),
            interpolate(z, y_rows),
        ))
    left = [Vector((center - half, y, z_start + (z_end - z_start) * index / (samples - 1))) for index, (center, half, y) in enumerate(side_rows[:-1])]
    apex_center, _apex_half, apex_y = side_rows[-1]
    apex = Vector((apex_center, apex_y, z_end))
    right = [Vector((center + half, y, z_start + (z_end - z_start) * index / (samples - 1))) for index, (center, half, y) in reversed(list(enumerate(side_rows[:-1])))]
    return left + [apex] + right


def build_outer(obj: bpy.types.Object, sign: float) -> dict[str, object]:
    samples = 11
    front_loop = profile_loop(sign, 2.995, 3.415, samples, outer_center, outer_front_half, outer_front_y)
    back_loop_raw = profile_loop(sign, 2.995, 3.415, samples, outer_center, outer_back_half, outer_back_y)
    inner_loop = profile_loop(sign, 3.070, 3.382, samples, inner_center, inner_half, inner_lip_y)
    count = len(front_loop)
    apex_index = samples - 1
    vertices = list(front_loop)
    back_indices: list[int] = []
    for index, point in enumerate(back_loop_raw):
        if index == apex_index:
            back_indices.append(apex_index)
        else:
            back_indices.append(len(vertices))
            vertices.append(point)
    inner_indices = list(range(len(vertices), len(vertices) + count))
    vertices.extend(inner_loop)

    cavity_loop: list[Vector] = []
    for point in inner_loop:
        corresponding_back = interpolate(point.z, outer_back_y)
        cavity_y = corresponding_back - 0.010
        cavity_loop.append(Vector((point.x, cavity_y, point.z)))
    cavity_indices = list(range(len(vertices), len(vertices) + count))
    vertices.extend(cavity_loop)

    front_indices = list(range(count))
    faces: list[tuple[int, ...]] = []
    for index in range(count):
        following = (index + 1) % count
        faces.append((
            front_indices[index],
            front_indices[following],
            inner_indices[following],
            inner_indices[index],
        ))
        faces.append((
            inner_indices[index],
            inner_indices[following],
            cavity_indices[following],
            cavity_indices[index],
        ))
        front_a = front_indices[index]
        front_b = front_indices[following]
        back_a = back_indices[index]
        back_b = back_indices[following]
        if front_a == back_a:
            faces.append((front_a, front_b, back_b))
        elif front_b == back_b:
            faces.append((front_a, front_b, back_a))
        else:
            faces.append((front_a, front_b, back_b, back_a))
    faces.append(tuple(reversed(cavity_indices)))
    faces.append(tuple(back_indices))
    replace_mesh(obj, vertices, faces, "PointedCupA85")
    return {
        "loop_vertices": count,
        "shared_apex": list(front_loop[apex_index]),
        "front_depth_by_station": [
            round(interpolate(z, outer_back_y) - interpolate(z, outer_front_y), 5)
            for z in outer_z
        ],
    }


def build_dish(obj: bpy.types.Object, sign: float) -> dict[str, object]:
    rows = 9
    columns = 5
    vertices: list[Vector] = []
    row_indices: list[list[int]] = []
    recess_values: list[float] = []
    for row in range(rows - 1):
        t = row / (rows - 1)
        z = 3.070 + (3.382 - 3.070) * t
        center = sign * interpolate(z, inner_center)
        half = interpolate(z, inner_half)
        lip_y = interpolate(z, inner_lip_y)
        boundary_y = lip_y + 0.006
        dish_y = interpolate(z, inner_dish_y)
        recess_values.append(dish_y - boundary_y)
        indices: list[int] = []
        for column in range(columns):
            u = -1.0 + 2.0 * column / (columns - 1)
            curvature = 1.0 - u * u
            y = boundary_y + (dish_y - boundary_y) * curvature
            indices.append(len(vertices))
            vertices.append(Vector((center + half * u, y, z)))
        row_indices.append(indices)
    tip_index = len(vertices)
    vertices.append(Vector((sign * 0.460, 0.032, 3.382)))
    faces: list[tuple[int, ...]] = []
    for row in range(len(row_indices) - 1):
        for column in range(columns - 1):
            faces.append((
                row_indices[row][column],
                row_indices[row + 1][column],
                row_indices[row + 1][column + 1],
                row_indices[row][column + 1],
            ))
    for column in range(columns - 1):
        faces.append((
            row_indices[-1][column],
            tip_index,
            row_indices[-1][column + 1],
        ))
    replace_mesh(obj, vertices, faces, "RecessedDishA85")
    return {
        "rows": rows,
        "columns": columns,
        "recess_min": round(min(recess_values), 5),
        "recess_max": round(max(recess_values), 5),
        "tip": list(vertices[tip_index]),
    }


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
locked_hash_before = geometry_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A85", "flat_nonconvergent_ear") for obj in ears
]
removed_modifiers: dict[str, list[str]] = {}
for obj in ears:
    removed_modifiers[obj.name] = [modifier.name for modifier in obj.modifiers]
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)

construction: dict[str, dict[str, object]] = {}
for side, sign in (("L", -1.0), ("R", 1.0)):
    construction[side] = {
        "outer": build_outer(bpy.data.objects[f"V6_Ear_{side}"], sign),
        "dish": build_dish(bpy.data.objects[f"V6_InnerEar_{side}"], sign),
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A85 changed locked A84 geometry outside four ear objects")

head_top = bounds(head)["max"][2]
per_side: dict[str, dict[str, object]] = {}
for side in ("L", "R"):
    outer_obj = bpy.data.objects[f"V6_Ear_{side}"]
    inner_obj = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer = after[outer_obj.name]
    inner = after[inner_obj.name]
    overlap = head_top - outer["min"][2]
    protrusion = outer["max"][2] - head_top
    aspect = outer["dimensions"][2] / outer["dimensions"][0]
    opening_ratio = inner["dimensions"][0] / outer["dimensions"][0]
    boundary_edges = boundary_edge_count(outer_obj.data)
    per_side[side] = {
        "outer": outer,
        "inner": inner,
        "head_overlap_z": round(overlap, 5),
        "protrusion_above_crown": round(protrusion, 5),
        "outer_h_over_w": round(aspect, 5),
        "opening_width_ratio": round(opening_ratio, 5),
        "outer_boundary_edges": boundary_edges,
    }
    if not 0.340 <= outer["dimensions"][0] <= 0.350:
        raise RuntimeError(f"{side} outer width outside A85 gate")
    if not 0.225 <= outer["dimensions"][1] <= 0.235:
        raise RuntimeError(f"{side} outer depth outside A85 gate")
    if not 0.410 <= outer["dimensions"][2] <= 0.425:
        raise RuntimeError(f"{side} outer height outside A85 gate")
    if not 0.235 <= overlap <= 0.250:
        raise RuntimeError(f"{side} root/head overlap outside A85 gate")
    if not 0.165 <= protrusion <= 0.185:
        raise RuntimeError(f"{side} crown protrusion outside A85 gate")
    if not 1.19 <= aspect <= 1.24:
        raise RuntimeError(f"{side} outer H/W outside A85 gate")
    if not 0.68 <= opening_ratio <= 0.72:
        raise RuntimeError(f"{side} opening/outer width outside A85 gate")
    if boundary_edges != 0:
        raise RuntimeError(f"{side} outer mesh is not closed manifold")

left_dims = Vector(after["V6_Ear_L"]["dimensions"])
right_dims = Vector(after["V6_Ear_R"]["dimensions"])
if max(abs(left_dims[index] - right_dims[index]) for index in range(3)) > 0.003:
    raise RuntimeError("A85 L/R evaluated ear bounds are asymmetric")

metrics = {
    "head_top": head_top,
    "per_side": per_side,
    "construction": construction,
    "removed_modifiers": removed_modifiers,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A85_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_PointedEarCup_A85"
scene["comforting_cat_v6_stage"] = "POINTED_EAR_CUP"
scene["comforting_cat_v6_attempt"] = 85
scene["comforting_cat_v6_dominant_defect"] = "flat_vertical_ear_without_shared_pointed_apex"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "POINTED_EAR_CUP",
    "attempt": 85,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_vertical_ear_without_shared_pointed_apex",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
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
