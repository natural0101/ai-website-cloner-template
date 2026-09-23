"""Soften only the exposed A96 ear contour while preserving its verified skull saddle."""

from __future__ import annotations

import bmesh
import hashlib
import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_soft_backswept_ear_cup_attempt97"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_inboard_feline_ear_saddle_attempt96.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_soft_backswept_ear_cup_attempt97.blend"
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
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
            for polygon in obj.data.polygons:
                digest.update((",".join(str(i) for i in polygon.vertices) + ";").encode("ascii"))
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


def root_state(obj: bpy.types.Object) -> list[list[float]]:
    # OF, OB, IF and IB copies of the hidden saddle indices 10,11,12,13,14,0.
    ob = {0: 15, 10: 24, 11: 25, 12: 26, 13: 27, 14: 28}
    inner_front = {index: 29 + index for index in (0, 10, 11, 12, 13, 14)}
    inner_back = {0: 44, 10: 53, 11: 54, 12: 55, 13: 56, 14: 57}
    state: list[list[float]] = []
    for index in (10, 11, 12, 13, 14, 0):
        for mesh_index in (index, ob[index], inner_front[index], inner_back[index]):
            point = obj.data.vertices[mesh_index].co
            state.append([round(float(value), 9) for value in point])
    return state


OUTER_XZ = {
    1: (0.330, 3.205),
    2: (0.365, 3.285),
    3: (0.405, 3.355),
    4: (0.440, 3.400),
    5: (0.462, 3.420),
    6: (0.505, 3.398),
    7: (0.535, 3.345),
    8: (0.558, 3.250),
    9: (0.565, 3.120),
}
OUTER_FRONT_Y = {
    1: -0.075, 2: -0.080, 3: -0.055, 4: 0.000, 5: 0.055,
    6: 0.000, 7: -0.045, 8: -0.080, 9: -0.070,
}
OUTER_BACK_Y = {
    1: 0.055, 2: 0.055, 3: 0.060, 4: 0.055, 5: 0.055,
    6: 0.055, 7: 0.060, 8: 0.060, 9: 0.055,
}
INNER_XZ = {
    1: (0.370, 3.210),
    2: (0.395, 3.270),
    3: (0.425, 3.330),
    4: (0.448, 3.375),
    5: (0.462, 3.385),
    6: (0.488, 3.373),
    7: (0.515, 3.325),
    8: (0.538, 3.245),
    9: (0.542, 3.180),
}
INNER_FRONT_Y = {
    1: -0.064, 2: -0.060, 3: -0.035, 4: 0.005, 5: 0.020,
    6: 0.005, 7: -0.035, 8: -0.065, 9: -0.068,
}
INNER_RECESS = {
    1: 0.034, 2: 0.038, 3: 0.040, 4: 0.034, 5: 0.000,
    6: 0.034, 7: 0.040, 8: 0.038, 9: 0.034,
}


def set_point(obj: bpy.types.Object, index: int, x: float, y: float, z: float, sign: float) -> None:
    world_point = Vector((sign * x, y, z))
    obj.data.vertices[index].co = obj.matrix_world.inverted() @ world_point


def reshape_outer(obj: bpy.types.Object, sign: float) -> None:
    ob = {1: 16, 2: 17, 3: 18, 4: 19, 5: 5, 6: 20, 7: 21, 8: 22, 9: 23}
    ib = {1: 45, 2: 46, 3: 47, 4: 48, 5: 34, 6: 49, 7: 50, 8: 51, 9: 52}
    for index in range(1, 10):
        x, z = OUTER_XZ[index]
        set_point(obj, index, x, OUTER_FRONT_Y[index], z, sign)
        if index != 5:
            inward = min(0.008, abs(x - 0.462) * 0.08)
            back_x = x + inward if x < 0.462 else x - inward
            set_point(obj, ob[index], back_x, OUTER_BACK_Y[index], z, sign)
        x, z = INNER_XZ[index]
        set_point(obj, 29 + index, x, INNER_FRONT_Y[index], z, sign)
        if index != 5:
            set_point(
                obj,
                ib[index],
                x,
                INNER_FRONT_Y[index] + INNER_RECESS[index],
                z,
                sign,
            )
    set_point(obj, 58, 0.448, 0.038, 3.245, sign)
    set_point(obj, 59, 0.445, 0.061, 3.235, sign)
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def triangular_rows() -> list[tuple[int, int]]:
    return [(row, column) for row in range(6) for column in range(6 - row)]


def reshape_pink(obj: bpy.types.Object, sign: float) -> None:
    medial = Vector((sign * 0.345, -0.060, 3.155))
    lateral = Vector((sign * 0.535, -0.060, 3.150))
    tip = Vector((sign * 0.462, 0.030, 3.385))
    front: list[Vector] = []
    for row, column in triangular_rows():
        t = row / 5.0
        row_length = 6 - row
        left = medial.lerp(tip, t)
        right = lateral.lerp(tip, t)
        u = 0.0 if row_length == 1 else column / (row_length - 1)
        point = left.lerp(right, u)
        boundary = row == 0 or column == 0 or column == row_length - 1
        if not boundary:
            point.y += 0.038 * (1.0 - abs(2.0 * u - 1.0)) * (1.0 - t)
        front.append(point)
    inverse = obj.matrix_world.inverted()
    for index, point in enumerate(front):
        obj.data.vertices[index].co = inverse @ point
        obj.data.vertices[index + 21].co = inverse @ (point + Vector((0.0, 0.007, 0.0)))
    obj.data.update()
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
locked_objects = [obj for obj in bpy.data.objects if obj.name not in ear_names]
locked_hash_before = object_state_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {obj.name: topology(obj) for obj in ears}
root_before = {side: root_state(bpy.data.objects[f"V6_Ear_{side}"]) for side in ("L", "R")}

preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A97", "rejected_a96_structural_ear_source")
    for obj in ears
]

reshape_outer(bpy.data.objects["V6_Ear_L"], -1.0)
reshape_pink(bpy.data.objects["V6_InnerEar_L"], -1.0)
reshape_outer(bpy.data.objects["V6_Ear_R"], 1.0)
reshape_pink(bpy.data.objects["V6_InnerEar_R"], 1.0)

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {obj.name: topology(obj) for obj in ears}
root_after = {side: root_state(bpy.data.objects[f"V6_Ear_{side}"]) for side in ("L", "R")}
locked_hash_after = object_state_hash(locked_objects)

if locked_hash_before != locked_hash_after:
    raise RuntimeError("A97 changed scene state outside the four canonical ear objects")
if root_before != root_after:
    raise RuntimeError("A97 changed the verified hidden A96 skull saddle")
if topology_before != topology_after:
    raise RuntimeError("A97 changed the verified A96 ear topology")
for obj in ears:
    topo = topology_after[obj.name]
    if topo["boundary_edges"] or topo["non_manifold_edges"] or topo["loose_vertices"]:
        raise RuntimeError(f"A97 invalid topology on {obj.name}: {topo}")

head_top = bounds(head)["max"][2]
per_side: dict[str, dict[str, object]] = {}
for side in ("L", "R"):
    outer = after[f"V6_Ear_{side}"]
    inner = after[f"V6_InnerEar_{side}"]
    ratio = inner["dimensions"][0] / outer["dimensions"][0]
    per_side[side] = {
        "outer": outer,
        "inner": inner,
        "opening_width_ratio": round(ratio, 6),
        "apex_above_head": round(outer["max"][2] - head_top, 6),
        "topology_outer": topology_after[f"V6_Ear_{side}"],
        "topology_inner": topology_after[f"V6_InnerEar_{side}"],
    }
    print(f"A97_{side}_PRE_GATE=" + json.dumps(per_side[side], ensure_ascii=False))
    if not 0.175 <= per_side[side]["apex_above_head"] <= 0.185:
        raise RuntimeError(
            f"{side} apex height outside strict A97 target: "
            f"{per_side[side]['apex_above_head']}"
        )
    if max(abs(outer["min"][0]), abs(outer["max"][0])) > 0.565001:
        raise RuntimeError(f"{side} outer X exceeds strict A97 target")
    if not 0.68 <= ratio <= 0.72:
        raise RuntimeError(f"{side} opening ratio outside strict A97 target: {ratio}")

metrics = {
    "target_mode": "TRUE_360",
    "reference_resolution": [454, 454],
    "camera_type": "ORTHO",
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "root_saddle_before": root_before,
    "root_saddle_after": root_after,
    "per_side": per_side,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
    "bounded_change": "exposed ear indices 1-9, shell centers, and pink dish only",
}
print("A97_PRE_GATE_METRICS=" + json.dumps(metrics, ensure_ascii=False))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_SoftBacksweptEarCup_A97"
scene["comforting_cat_v6_stage"] = "SOFT_BACKSWEPT_EAR_CUP"
scene["comforting_cat_v6_attempt"] = 97
scene["comforting_cat_v6_dominant_defect"] = "faceted_tall_ear_insert"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)
scene["comforting_cat_v6_target_mode"] = "TRUE_360"

report = {
    "asset": ASSET,
    "stage": "SOFT_BACKSWEPT_EAR_CUP",
    "attempt": 97,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "faceted_tall_ear_insert",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ear_names,
        "preserved": [
            "A96 verified hidden skull saddle",
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
