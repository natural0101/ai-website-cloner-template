"""Add two closed, conformal upper-lid crescents to the authoritative A98 face."""

from __future__ import annotations

import bmesh
import hashlib
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ASSET = "comforting_cat_v6_upper_lid_worry_integration_attempt99"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_compact_kitten_body_attempt98.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
for name in ("V6_UpperLid_L", "V6_UpperLid_R"):
    if name in bpy.data.objects:
        raise RuntimeError(f"A99 source unexpectedly already contains {name}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_upper_lid_worry_integration_attempt99.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
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
                digest.update(
                    (f"{polygon.material_index}:" + ",".join(str(i) for i in polygon.vertices) + ";").encode("ascii")
                )
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


def object_bvh(obj: bpy.types.Object) -> tuple[BVHTree, object, Vector]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(obj, depsgraph)
    inverse = obj.matrix_world.inverted()
    direction = inverse.to_3x3() @ Vector((0.0, 1.0, 0.0))
    return tree, inverse, direction


def ray_y(
    obj: bpy.types.Object,
    tree: BVHTree,
    inverse: object,
    direction: Vector,
    x: float,
    z: float,
) -> float | None:
    origin = inverse @ Vector((x, -2.0, z))
    hit, _normal, _index, _distance = tree.ray_cast(origin, direction)
    if hit is None:
        return None
    return float((obj.matrix_world @ hit).y)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
eyes = {side: bpy.data.objects[f"V6_Eye_{side}"] for side in ("L", "R")}
pupils = {side: bpy.data.objects[f"V6_Pupil_{side}"] for side in ("L", "R")}
highlights = {side: bpy.data.objects[f"V6_EyeHighlight_{side}"] for side in ("L", "R")}
head_material = head.data.materials[0]
target_collection = head.users_collection[0]

locked_objects = list(bpy.data.objects)
locked_hash_before = object_state_hash(locked_objects)
locked_bounds_before = {
    obj.name: bounds(obj)
    for obj in [head, *eyes.values(), *pupils.values(), *highlights.values()]
}

head_tree, head_inverse, head_direction = object_bvh(head)
eye_queries = {
    side: object_bvh(eye)
    for side, eye in eyes.items()
}


def combined_surface_y(side: str, x: float, z: float) -> float:
    values: list[float] = []
    head_y = ray_y(head, head_tree, head_inverse, head_direction, x, z)
    if head_y is not None:
        values.append(head_y)
    eye_tree, eye_inverse, eye_direction = eye_queries[side]
    eye_y = ray_y(eyes[side], eye_tree, eye_inverse, eye_direction, x, z)
    if eye_y is not None:
        values.append(eye_y)
    if not values:
        raise RuntimeError(f"A99 combined surface ray miss for {side} at x={x:.6f}, z={z:.6f}")
    return min(values)


profiles: dict[str, object] = {}
created: list[bpy.types.Object] = []
station_count = 13
outer_z = 2.918
inner_z = 2.950
lower_arch = 0.008
front_lower_y = -0.5095

for side, sign in (("L", -1.0), ("R", 1.0)):
    outer_x = sign * 0.333
    inner_x = sign * 0.107
    vertices_world: list[Vector] = []
    stations: list[dict[str, float]] = []
    for index in range(station_count):
        t = index / (station_count - 1)
        x = outer_x + (inner_x - outer_x) * t
        chord_z = outer_z + (inner_z - outer_z) * t
        lower_z = chord_z + math.sin(math.pi * t) * lower_arch
        cap_height = 0.004 + math.sin(math.pi * t) * 0.026
        upper_z = lower_z + cap_height
        lower_surface = combined_surface_y(side, x, lower_z)
        upper_surface = combined_surface_y(side, x, upper_z)
        lower_front = min(lower_surface - 0.0020, front_lower_y)
        upper_front = upper_surface - 0.0020
        lower_back = lower_surface + 0.0010
        upper_back = upper_surface + 0.0010
        vertices_world.extend(
            [
                Vector((x, lower_front, lower_z)),
                Vector((x, upper_front, upper_z)),
                Vector((x, lower_back, lower_z)),
                Vector((x, upper_back, upper_z)),
            ]
        )
        stations.append(
            {
                "t": round(t, 6),
                "x": round(x, 6),
                "lower_z": round(lower_z, 6),
                "upper_z": round(upper_z, 6),
                "cap_height": round(cap_height, 6),
                "lower_front_y": round(lower_front, 6),
                "lower_back_y": round(lower_back, 6),
                "front_proud_over_pupil": round(float(pupils[side].bound_box[0][1]), 6),
            }
        )

    faces: list[tuple[int, ...]] = []
    for index in range(station_count - 1):
        current = index * 4
        following = (index + 1) * 4
        faces.extend(
            [
                (current, following, following + 1, current + 1),
                (current + 2, current + 3, following + 3, following + 2),
                (current, current + 2, following + 2, following),
                (current + 1, following + 1, following + 3, current + 3),
            ]
        )
    faces.append((0, 1, 3, 2))
    last = (station_count - 1) * 4
    faces.append((last, last + 2, last + 3, last + 1))

    mesh = bpy.data.meshes.new(f"V6_UpperLid_{side}_ConformalCrescentMesh_A99")
    inverse_root = root.matrix_world.inverted()
    mesh.from_pydata([inverse_root @ point for point in vertices_world], [], faces)
    mesh.update(calc_edges=True)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    lid = bpy.data.objects.new(f"V6_UpperLid_{side}", mesh)
    target_collection.objects.link(lid)
    lid.parent = root
    mesh.materials.append(head_material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    lid["comforting_cat_role"] = "conformal_upper_lid_worry_crescent"
    lid["comforting_cat_attempt"] = 99
    created.append(lid)

    eye_bounds = locked_bounds_before[eyes[side].name]
    highlight_bounds = locked_bounds_before[highlights[side].name]
    highlight_xs = (highlight_bounds["min"][0], highlight_bounds["max"][0])

    def lower_z_at_x(sample_x: float) -> float:
        denominator = inner_x - outer_x
        t = max(0.0, min(1.0, (sample_x - outer_x) / denominator))
        return outer_z + (inner_z - outer_z) * t + math.sin(math.pi * t) * lower_arch

    highlight_clearance = min(lower_z_at_x(x) for x in highlight_xs) - highlight_bounds["max"][2]
    center_station = stations[station_count // 2]
    profiles[side] = {
        "span": round(abs(inner_x - outer_x), 6),
        "inner_outer_rise": round(inner_z - outer_z, 6),
        "lower_arch": lower_arch,
        "outer_coverage": round(eye_bounds["max"][2] - outer_z, 6),
        "center_visible_eye_height": round(center_station["lower_z"] - eye_bounds["min"][2], 6),
        "lower_front_y": front_lower_y,
        "pupil_front_y": locked_bounds_before[pupils[side].name]["min"][1],
        "front_proud_over_pupil": round(
            locked_bounds_before[pupils[side].name]["min"][1] - front_lower_y,
            6,
        ),
        "highlight_clearance_z": round(highlight_clearance, 6),
        "stations": stations,
        "topology": topology(lid),
    }

bpy.context.view_layer.update()
locked_hash_after = object_state_hash(locked_objects)
locked_bounds_after = {
    obj.name: bounds(obj)
    for obj in [head, *eyes.values(), *pupils.values(), *highlights.values()]
}
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A99 changed an existing A98 object")
if locked_bounds_before != locked_bounds_after:
    raise RuntimeError("A99 changed locked face bounds")

for side, profile in profiles.items():
    if not 0.225 <= profile["span"] <= 0.235:
        raise RuntimeError(f"{side} lid span outside target")
    if not 0.027 <= profile["inner_outer_rise"] <= 0.038:
        raise RuntimeError(f"{side} lid worry rise outside target")
    if not 0.008 <= profile["lower_arch"] <= 0.014:
        raise RuntimeError(f"{side} lid arch outside target")
    if not 0.040 <= profile["outer_coverage"] <= 0.047:
        raise RuntimeError(f"{side} lid outer coverage outside target")
    if profile["center_visible_eye_height"] < 0.245:
        raise RuntimeError(f"{side} lid creates a sleepy center squint")
    if not 0.0015 <= profile["front_proud_over_pupil"] <= 0.0030:
        raise RuntimeError(f"{side} lid proud step outside target")
    if profile["highlight_clearance_z"] < 0.006:
        raise RuntimeError(f"{side} lid threatens the locked highlight")
    if profile["topology"] != {
        "vertices": 52,
        "edges": 100,
        "faces": 50,
        "boundary_edges": 0,
        "non_manifold_edges": 0,
        "loose_vertices": 0,
    }:
        raise RuntimeError(f"{side} lid topology mismatch: {profile['topology']}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "profiles": profiles,
    "created": [obj.name for obj in created],
    "created_bounds": {obj.name: bounds(obj) for obj in created},
    "locked_bounds_before": locked_bounds_before,
    "locked_bounds_after": locked_bounds_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A99_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_UpperLidWorryIntegration_A99"
scene["comforting_cat_v6_stage"] = "UPPER_LID_WORRY_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 99
scene["comforting_cat_v6_dominant_defect"] = "fully_open_button_disc_eyes"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "UPPER_LID_WORRY_INTEGRATION",
    "attempt": 99,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "fully_open_button_disc_eyes",
    "metrics": metrics,
    "scope_lock": {
        "changed": ["created V6_UpperLid_L/R only"],
        "preserved": [
            "A98 head and full eye/pupil/highlight stack",
            "A90 brow ribbons",
            "muzzle, nose, mouth and whiskers",
            "A97 ears",
            "A98 scarf, compact body, arms and satchel",
            "legs, feet and tail",
            "camera, lights and existing materials",
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
