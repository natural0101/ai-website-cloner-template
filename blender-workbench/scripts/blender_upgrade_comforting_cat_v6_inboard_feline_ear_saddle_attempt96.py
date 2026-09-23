"""Build restrained feline ear cups with a narrow in-skull saddle from authoritative A90."""

from __future__ import annotations

import bmesh
import hashlib
import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ASSET = "comforting_cat_v6_inboard_feline_ear_saddle_attempt96"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_brow_surface_ribbon_attempt90.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_inboard_feline_ear_saddle_attempt96.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
descendants = utils["descendants"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def object_state_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        digest.update(obj.type.encode("ascii"))
        digest.update((obj.parent.name if obj.parent else "").encode("utf-8"))
        digest.update(f"{int(obj.hide_render)},{int(obj.hide_viewport)}".encode("ascii"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for modifier in obj.modifiers:
            digest.update(f"{modifier.name}:{modifier.type};".encode("utf-8"))
        if obj.type == "MESH":
            digest.update(
                ",".join(material.name if material else "" for material in obj.data.materials).encode("utf-8")
            )
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
            for polygon in obj.data.polygons:
                digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode("ascii"))
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                for point in spline.bezier_points:
                    digest.update(
                        f"{point.co.x:.9f},{point.co.y:.9f},{point.co.z:.9f},{point.radius:.9f};".encode("ascii")
                    )
    return digest.hexdigest()


def topology(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(1 for edge in bm.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
        "loose_vertices": sum(1 for vertex in bm.verts if not vertex.link_edges),
    }
    bm.free()
    return result


def replace_mesh(
    obj: bpy.types.Object,
    world_vertices: list[Vector],
    faces: list[tuple[int, ...]],
    suffix: str,
) -> None:
    materials = list(obj.data.materials)
    old_mesh = obj.data
    inverse = obj.matrix_world.inverted()
    mesh = bpy.data.meshes.new(f"{obj.name}_{suffix}_Mesh")
    mesh.from_pydata([inverse @ point for point in world_vertices], [], faces)
    mesh.validate(verbose=True)
    mesh.update(calc_edges=True)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.data = mesh
    for material in materials:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def world_bvh(obj: bpy.types.Object) -> BVHTree:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
    tree = BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    evaluated.to_mesh_clear()
    return tree


def head_surfaces(tree: BVHTree, x: float, z: float) -> tuple[float, float]:
    front, _normal, _index, _distance = tree.ray_cast(
        Vector((x, -2.0, z)), Vector((0.0, 1.0, 0.0)), 4.0
    )
    back, _normal, _index, _distance = tree.ray_cast(
        Vector((x, 2.0, z)), Vector((0.0, -1.0, 0.0)), 4.0
    )
    if front is None or back is None:
        raise RuntimeError(f"A96 head ray miss at x={x:.6f}, z={z:.6f}; fallback forbidden")
    return float(front.y), float(back.y)


ROOT_INDICES = (10, 11, 12, 13, 14, 0)
OUTER_XZ = [
    (0.290, 3.150),
    (0.318, 3.235),
    (0.355, 3.320),
    (0.400, 3.390),
    (0.448, 3.438),
    (0.480, 3.460),
    (0.515, 3.438),
    (0.555, 3.365),
    (0.585, 3.270),
    (0.595, 3.140),
    (0.430, 3.000),
    (0.405, 3.030),
    (0.375, 3.060),
    (0.345, 3.090),
    (0.315, 3.120),
]
OUTER_FRONT_Y = [
    -0.0230, -0.0900, -0.0900, -0.0600, -0.0150,
    0.0300, -0.0150, -0.0600, -0.0900, -0.0800,
    -0.0184, -0.0275, -0.0325, -0.0334, -0.0294,
]
OUTER_BACK_Y = [
    0.0165, 0.0450, 0.0350, 0.0200, 0.0200,
    0.0300, 0.0200, 0.0350, 0.0450, 0.0700,
    0.0316, 0.0375, 0.0325, 0.0266, 0.0206,
]
INNER_XZ = [
    (0.350, 3.175),
    (0.375, 3.235),
    (0.405, 3.300),
    (0.438, 3.355),
    (0.465, 3.395),
    (0.480, 3.405),
    (0.507, 3.392),
    (0.535, 3.340),
    (0.555, 3.270),
    (0.558, 3.205),
    (0.540, 3.170),
    (0.500, 3.145),
    (0.455, 3.135),
    (0.410, 3.145),
    (0.375, 3.160),
]
INNER_FRONT_Y = [
    -0.055, -0.060, -0.050, -0.025, 0.005,
    0.018, 0.005, -0.030, -0.060, -0.072,
    -0.070, -0.065, -0.060, -0.058, -0.056,
]
INNER_RECESS = [
    0.025, 0.027, 0.030, 0.030, 0.020,
    0.000, 0.020, 0.030, 0.032, 0.032,
    0.030, 0.028, 0.027, 0.026, 0.025,
]


def mirrored_x(sign: float, x: float) -> float:
    return sign * x


def back_x(x: float, index: int) -> float:
    if index in ROOT_INDICES or index == 5:
        return x
    offset = min(0.012, abs(x - 0.480) * 0.10)
    return x + offset if x < 0.480 else x - offset


def build_outer_ear(
    obj: bpy.types.Object,
    sign: float,
    tree: BVHTree,
) -> dict[str, object]:
    of = [
        Vector((mirrored_x(sign, x), OUTER_FRONT_Y[index], z))
        for index, (x, z) in enumerate(OUTER_XZ)
    ]
    ob_raw = [
        Vector((mirrored_x(sign, back_x(x, index)), OUTER_BACK_Y[index], z))
        for index, (x, z) in enumerate(OUTER_XZ)
    ]
    inner_front = [
        Vector((mirrored_x(sign, x), INNER_FRONT_Y[index], z))
        for index, (x, z) in enumerate(INNER_XZ)
    ]
    inner_back_raw = [
        Vector((point.x, point.y + INNER_RECESS[index], point.z))
        for index, point in enumerate(inner_front)
    ]

    vertices = list(of)
    ob_indices: list[int] = []
    for index, point in enumerate(ob_raw):
        if index == 5:
            ob_indices.append(5)
        else:
            ob_indices.append(len(vertices))
            vertices.append(point)
    if_indices = list(range(len(vertices), len(vertices) + 15))
    vertices.extend(inner_front)
    ib_indices: list[int] = []
    for index, point in enumerate(inner_back_raw):
        if index == 5:
            ib_indices.append(if_indices[5])
        else:
            ib_indices.append(len(vertices))
            vertices.append(point)
    cavity_center_index = len(vertices)
    vertices.append(Vector((mirrored_x(sign, 0.460), 0.025, 3.255)))
    back_center_index = len(vertices)
    vertices.append(Vector((mirrored_x(sign, 0.455), 0.060, 3.245)))

    faces: list[tuple[int, ...]] = []
    for index in range(15):
        following = (index + 1) % 15
        faces.append((index, following, if_indices[following], if_indices[index]))
        if index == 4:
            faces.append((index, following, ob_indices[index]))
        elif index == 5:
            faces.append((index, following, ob_indices[following]))
        else:
            faces.append((index, following, ob_indices[following], ob_indices[index]))
        if index == 4:
            faces.append((if_indices[index], if_indices[following], ib_indices[index]))
        elif index == 5:
            faces.append((if_indices[index], if_indices[following], ib_indices[following]))
        else:
            faces.append(
                (if_indices[index], if_indices[following], ib_indices[following], ib_indices[index])
            )
        faces.append((cavity_center_index, ib_indices[following], ib_indices[index]))
        faces.append((back_center_index, ob_indices[index], ob_indices[following]))

    root_probes: list[dict[str, float]] = []
    root_order = [10, 11, 12, 13, 14, 0]
    for index, following in zip(root_order, root_order[1:]):
        sample_points = [
            of[index],
            ob_raw[index],
            (of[index] + of[following]) * 0.5,
            (ob_raw[index] + ob_raw[following]) * 0.5,
            (of[index] + ob_raw[index] + of[following] + ob_raw[following]) * 0.25,
        ]
        for point in sample_points:
            front_surface, back_surface = head_surfaces(tree, float(point.x), float(point.z))
            if not front_surface + 0.012 <= point.y <= back_surface - 0.012:
                raise RuntimeError(
                    f"A96 root point outside hidden skull band: {tuple(point)}, "
                    f"surfaces=({front_surface}, {back_surface})"
                )
            root_probes.append(
                {
                    "x": round(float(point.x), 6),
                    "z": round(float(point.z), 6),
                    "front_clearance": round(float(point.y - front_surface), 6),
                    "back_clearance": round(float(back_surface - point.y), 6),
                }
            )

    replace_mesh(obj, vertices, faces, "InboardFelineSaddleA96")
    return {
        "root_probe_count": len(root_probes),
        "root_probes": root_probes,
        "apex": [round(float(value), 6) for value in of[5]],
        "depth_profile": {
            str(index): round(float(ob_raw[index].y - of[index].y), 6)
            for index in (9, 8, 7, 6, 5)
        },
        "back_shell_x_exit": round(
            max(abs(float(ob_raw[index].x - of[index].x)) for index in range(15)),
            6,
        ),
    }


def triangular_rows() -> list[tuple[int, int]]:
    return [(row, column) for row in range(6) for column in range(6 - row)]


def build_inner_ear(obj: bpy.types.Object, sign: float) -> dict[str, object]:
    medial = Vector((mirrored_x(sign, 0.360), -0.050, 3.160))
    lateral = Vector((mirrored_x(sign, 0.550), -0.064, 3.165))
    tip = Vector((mirrored_x(sign, 0.480), 0.013, 3.405))
    rows = triangular_rows()
    front: list[Vector] = []
    for row, column in rows:
        t = row / 5.0
        row_length = 6 - row
        left = medial.lerp(tip, t)
        right = lateral.lerp(tip, t)
        u = 0.0 if row_length == 1 else column / (row_length - 1)
        point = left.lerp(right, u)
        boundary = (
            row == 0
            or column == 0
            or column == row_length - 1
        )
        if not boundary:
            barycentric_recess = 1.0 - abs(2.0 * u - 1.0)
            point.y += 0.024 * barycentric_recess * (1.0 - t)
        front.append(point)
    back = [Vector((point.x, point.y + 0.007, point.z)) for point in front]
    vertices = front + back

    def start(row: int) -> int:
        return row * 6 - row * (row - 1) // 2

    def front_index(row: int, column: int) -> int:
        return start(row) + column

    front_faces: list[tuple[int, int, int]] = []
    for row in range(5):
        for column in range(5 - row):
            front_faces.append(
                (
                    front_index(row, column),
                    front_index(row, column + 1),
                    front_index(row + 1, column),
                )
            )
            if column < 4 - row:
                front_faces.append(
                    (
                        front_index(row, column + 1),
                        front_index(row + 1, column + 1),
                        front_index(row + 1, column),
                    )
                )
    faces: list[tuple[int, ...]] = list(front_faces)
    faces.extend(tuple(index + 21 for index in reversed(face)) for face in front_faces)
    boundary = [front_index(0, column) for column in range(6)]
    boundary.extend(front_index(row, 5 - row) for row in range(1, 6))
    boundary.extend(front_index(row, 0) for row in range(4, 0, -1))
    for index, current in enumerate(boundary):
        following = boundary[(index + 1) % len(boundary)]
        faces.append((current, following, following + 21, current + 21))

    replace_mesh(obj, vertices, faces, "RecessedPinkDishA96")
    return {
        "front_vertices": len(front),
        "boundary_vertices": len(boundary),
        "maximum_front_recess": 0.024,
        "solid_depth": 0.007,
    }


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
tree = world_bvh(head)
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
locked_objects = [obj for obj in bpy.data.objects if obj.name not in ear_names]
locked_hash_before = object_state_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {obj.name: topology(obj) for obj in ears}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A96", "authoritative_a90_ear_source")
    for obj in ears
]

construction: dict[str, dict[str, object]] = {}
for side, sign in (("L", -1.0), ("R", 1.0)):
    construction[side] = {
        "outer": build_outer_ear(bpy.data.objects[f"V6_Ear_{side}"], sign, tree),
        "inner": build_inner_ear(bpy.data.objects[f"V6_InnerEar_{side}"], sign),
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {obj.name: topology(obj) for obj in ears}
locked_hash_after = object_state_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A96 changed A90 scene state outside the four canonical ear objects")

per_side: dict[str, dict[str, object]] = {}
for side in ("L", "R"):
    outer_obj = bpy.data.objects[f"V6_Ear_{side}"]
    inner_obj = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer = after[outer_obj.name]
    inner = after[inner_obj.name]
    outer_topology = topology_after[outer_obj.name]
    inner_topology = topology_after[inner_obj.name]
    opening_ratio = inner["dimensions"][0] / outer["dimensions"][0]
    per_side[side] = {
        "outer": outer,
        "inner": inner,
        "outer_topology": outer_topology,
        "inner_topology": inner_topology,
        "opening_width_ratio": round(opening_ratio, 6),
        "apex_above_head": round(outer["max"][2] - bounds(head)["max"][2], 6),
        "modifiers": [modifier.type for modifier in outer_obj.modifiers]
        + [modifier.type for modifier in inner_obj.modifiers],
    }
    if outer_topology != {
        "vertices": 60,
        "edges": 133,
        "faces": 75,
        "boundary_edges": 0,
        "non_manifold_edges": 0,
        "loose_vertices": 0,
    }:
        raise RuntimeError(f"{side} outer topology mismatch: {outer_topology}")
    if inner_topology != {
        "vertices": 42,
        "edges": 105,
        "faces": 65,
        "boundary_edges": 0,
        "non_manifold_edges": 0,
        "loose_vertices": 0,
    }:
        raise RuntimeError(f"{side} inner topology mismatch: {inner_topology}")
    if not 0.295 <= outer["dimensions"][0] <= 0.312:
        raise RuntimeError(f"{side} outer width outside feline target")
    if not 0.135 <= outer["dimensions"][1] <= 0.160:
        raise RuntimeError(f"{side} outer depth outside tapered-cup target")
    if not 0.450 <= outer["dimensions"][2] <= 0.470:
        raise RuntimeError(f"{side} outer total height outside target")
    if not 0.185 <= inner["dimensions"][0] <= 0.205:
        raise RuntimeError(f"{side} pink opening width outside target")
    if not 0.240 <= inner["dimensions"][2] <= 0.255:
        raise RuntimeError(f"{side} pink opening height outside target")
    if not 0.60 <= opening_ratio <= 0.68:
        raise RuntimeError(f"{side} pink opening ratio outside target")
    if per_side[side]["modifiers"]:
        raise RuntimeError(f"{side} A96 ears must not use bevel/subdivision modifiers")

left_outer = Vector(after["V6_Ear_L"]["dimensions"])
right_outer = Vector(after["V6_Ear_R"]["dimensions"])
if max(abs(left_outer[index] - right_outer[index]) for index in range(3)) > 0.00001:
    raise RuntimeError("A96 L/R outer bounds are not mirrored")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "hidden_surface_assumption": (
        "Rear ear shell is a shallow tapered cup; the entire saddle is hidden inside the A90 skull."
    ),
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "construction": construction,
    "per_side": per_side,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A96_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_InboardFelineEarSaddle_A96"
scene["comforting_cat_v6_stage"] = "INBOARD_FELINE_EAR_SADDLE"
scene["comforting_cat_v6_attempt"] = 96
scene["comforting_cat_v6_dominant_defect"] = "flat_triangular_horn_ears_with_oversized_pink_insert"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "INBOARD_FELINE_EAR_SADDLE",
    "attempt": 96,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_triangular_horn_ears_with_oversized_pink_insert",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ear_names,
        "preserved": [
            "A90 head/face/brow ribbons",
            "A84/A79 costume and muzzle",
            "scarf/satchel/arms",
            "legs/feet/tail",
            "camera/lights/materials",
            "all non-ear object state",
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
