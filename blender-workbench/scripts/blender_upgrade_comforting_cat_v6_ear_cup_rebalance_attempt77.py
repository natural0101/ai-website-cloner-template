"""Rebalance the four A73 ear objects into broader, rooted, backward-leaning cups."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_ear_cup_rebalance_attempt77"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_upper_stack_settle_attempt73.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_ear_cup_rebalance_attempt77.blend"
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


def fit_world_bounds(
    obj: bpy.types.Object,
    target_min: Vector,
    target_max: Vector,
    tip_sign: float = 0.0,
) -> None:
    current = bounds(obj)
    current_min = Vector(current["min"])
    current_max = Vector(current["max"])
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        normalized = Vector(
            (
                (world.x - current_min.x) / (current_max.x - current_min.x),
                (world.y - current_min.y) / (current_max.y - current_min.y),
                (world.z - current_min.z) / (current_max.z - current_min.z),
            )
        )
        world = Vector(
            (
                target_min.x + normalized.x * (target_max.x - target_min.x),
                target_min.y + normalized.y * (target_max.y - target_min.y),
                target_min.z + normalized.z * (target_max.z - target_min.z),
            )
        )
        if tip_sign:
            tip_weight = smoothstep((normalized.z - 0.25) / 0.75)
            world.x += tip_sign * 0.022 * tip_weight
            world.y += 0.025 * tip_weight
        vertex.co = inverse @ world
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
outer_names = ["V6_Ear_L", "V6_Ear_R"]
inner_names = ["V6_InnerEar_L", "V6_InnerEar_R"]
locked_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
locked_hash_before = geometry_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A77", "plastic_vertical_ear_petal")
    for obj in ears
]

head_top = bounds(head)["max"][2]
for side, sign in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    center_x = 0.5 * (before[outer.name]["min"][0] + before[outer.name]["max"][0])
    fit_world_bounds(
        outer,
        Vector((center_x - 0.1675, -0.116, head_top - 0.245)),
        Vector((center_x + 0.1675, 0.116, head_top + 0.155)),
        tip_sign=sign,
    )

bpy.context.view_layer.update()
outer_after_pre_inner = {name: bounds(bpy.data.objects[name]) for name in outer_names}

for side in ("L", "R"):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer_bounds = bounds(outer)
    outer_center_x = 0.5 * (outer_bounds["min"][0] + outer_bounds["max"][0])
    inner_min_y = outer_bounds["min"][1] + 0.008
    fit_world_bounds(
        inner,
        Vector((outer_center_x - 0.114, inner_min_y, outer_bounds["min"][2] + 0.055)),
        Vector((outer_center_x + 0.114, inner_min_y + 0.070, outer_bounds["min"][2] + 0.323)),
    )

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A77 changed locked A73 head, face, costume, legs or tail geometry")
if topology_before != topology_after:
    raise RuntimeError("A77 changed ear topology")

per_side = {}
for side in ("L", "R"):
    outer = after[f"V6_Ear_{side}"]
    inner = after[f"V6_InnerEar_{side}"]
    root_overlap = min(head_top, outer["max"][2]) - max(bounds(head)["min"][2], outer["min"][2])
    protrusion = outer["max"][2] - head_top
    inner_width_ratio = inner["dimensions"][0] / outer["dimensions"][0]
    inner_height_ratio = inner["dimensions"][2] / outer["dimensions"][2]
    inset_y = inner["min"][1] - outer["min"][1]
    per_side[side] = {
        "outer_dimensions": outer["dimensions"],
        "inner_dimensions": inner["dimensions"],
        "head_root_overlap": round(root_overlap, 6),
        "ear_protrusion_above_crown": round(protrusion, 6),
        "inner_width_ratio": round(inner_width_ratio, 5),
        "inner_height_ratio": round(inner_height_ratio, 5),
        "inner_front_inset_y": round(inset_y, 6),
    }
    if not 0.325 <= outer["dimensions"][0] <= 0.345:
        raise RuntimeError(f"{side} outer ear width outside target")
    if not 0.220 <= outer["dimensions"][1] <= 0.240:
        raise RuntimeError(f"{side} outer ear depth outside target")
    if not 0.390 <= outer["dimensions"][2] <= 0.410:
        raise RuntimeError(f"{side} outer ear height outside target")
    if not 0.150 <= protrusion <= 0.180:
        raise RuntimeError(f"{side} ear crown protrusion outside target")
    if not 0.230 <= root_overlap <= 0.260:
        raise RuntimeError(f"{side} ear root overlap outside target")
    if not 0.66 <= inner_width_ratio <= 0.71:
        raise RuntimeError(f"{side} inner ear width ratio outside target")
    if not 0.64 <= inner_height_ratio <= 0.70:
        raise RuntimeError(f"{side} inner ear height ratio outside target")
    if not 0.006 <= inset_y <= 0.010:
        raise RuntimeError(f"{side} inner ear front inset outside target")

metrics = {
    "head_top": head_top,
    "per_side": per_side,
    "outer_after_before_inner": outer_after_pre_inner,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A77_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EarCupRebalance_A77"
scene["comforting_cat_v6_stage"] = "EAR_CUP_REBALANCE"
scene["comforting_cat_v6_attempt"] = 77
scene["comforting_cat_v6_dominant_defect"] = "plastic_vertical_ear_petals_and_flat_inner_patch"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "EAR_CUP_REBALANCE",
    "attempt": 77,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "plastic_vertical_ear_petals_and_flat_inner_patch",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ear_names,
        "preserved": ["A73 head/face/proportions", "costume", "legs", "tail", "camera", "lights", "materials"],
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
