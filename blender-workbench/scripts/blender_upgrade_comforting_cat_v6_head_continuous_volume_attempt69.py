"""Rebalance the head as one continuous volume instead of adding local cheek shelves."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_head_continuous_volume_attempt69"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_root_robe_conceal_attempt63.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_continuous_volume_attempt69.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def gaussian(value: float, center: float, sigma: float) -> float:
    return math.exp(-0.5 * ((value - center) / sigma) ** 2)


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


def band_half_width(obj: bpy.types.Object, z_min: float, z_max: float) -> float:
    values: list[float] = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if z_min <= world.z <= z_max:
            values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
non_head_objects = [obj for obj in descendants(root) if obj.name != head.name]
non_head_hash_before = geometry_hash(non_head_objects)
before = bounds(head)
topology_before = {
    "vertices": len(head.data.vertices),
    "edges": len(head.data.edges),
    "faces": len(head.data.polygons),
}
original_world = [head.matrix_world @ vertex.co for vertex in head.data.vertices]
eye_half_before = band_half_width(head, 2.67, 2.88)
lower_half_before = band_half_width(head, 2.43, 2.57)
preserved_source = preserve_copy(
    head,
    "Comforting_Cat_V6",
    "A69",
    "x_only_cheek_shelves_require_continuous_head_volume",
)

center_y = 0.5 * (before["min"][1] + before["max"][1])
inverse = head.matrix_world.inverted()
affected_vertices = 0
maximum_outward_delta = 0.0
maximum_inward_delta = 0.0
maximum_y_delta = 0.0
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    if world.z < 2.34 or world.z > 3.08:
        continue
    relative_y = world.y - center_y
    horizontal_radius = math.hypot(world.x, relative_y)
    if horizontal_radius < 0.05:
        continue

    radial_delta = (
        0.082 * gaussian(world.z, 2.51, 0.105)
        - 0.032 * gaussian(world.z, 2.78, 0.150)
    )
    if abs(radial_delta) < 0.0001:
        continue

    direction_x = world.x / horizontal_radius
    direction_y = relative_y / horizontal_radius
    x_delta = direction_x * radial_delta
    y_delta = direction_y * radial_delta * 0.35
    world.x += x_delta
    world.y += y_delta
    vertex.co = inverse @ world
    affected_vertices += 1
    maximum_outward_delta = max(maximum_outward_delta, radial_delta)
    maximum_inward_delta = min(maximum_inward_delta, radial_delta)
    maximum_y_delta = max(maximum_y_delta, abs(y_delta))
head.data.update()

bpy.context.view_layer.update()
after = bounds(head)
topology_after = {
    "vertices": len(head.data.vertices),
    "edges": len(head.data.edges),
    "faces": len(head.data.polygons),
}
non_head_hash_after = geometry_hash(non_head_objects)
if non_head_hash_before != non_head_hash_after:
    raise RuntimeError("Continuous head pass changed locked non-head geometry")
if topology_before != topology_after:
    raise RuntimeError("Continuous head pass changed topology")

z_max_delta = 0.0
for vertex, original in zip(head.data.vertices, original_world, strict=True):
    current = head.matrix_world @ vertex.co
    z_max_delta = max(z_max_delta, abs(current.z - original.z))
if z_max_delta > 0.00001:
    raise RuntimeError(f"Continuous head pass changed locked Z: {z_max_delta}")

eye_half_after = band_half_width(head, 2.67, 2.88)
lower_half_after = band_half_width(head, 2.43, 2.57)
metrics = {
    "affected_vertices": affected_vertices,
    "maximum_outward_radial_delta": round(maximum_outward_delta, 6),
    "maximum_inward_radial_delta": round(maximum_inward_delta, 6),
    "maximum_world_y_delta": round(maximum_y_delta, 6),
    "eye_band_half_width_before": round(eye_half_before, 6),
    "eye_band_half_width_after": round(eye_half_after, 6),
    "lower_cheek_half_width_before": round(lower_half_before, 6),
    "lower_cheek_half_width_after": round(lower_half_after, 6),
    "lower_cheek_over_eye_before": round(lower_half_before / eye_half_before, 5),
    "lower_cheek_over_eye_after": round(lower_half_after / eye_half_after, 5),
    "head_width_height_before": round(before["dimensions"][0] / before["dimensions"][2], 5),
    "head_width_height_after": round(after["dimensions"][0] / after["dimensions"][2], 5),
    "head_depth_before": round(before["dimensions"][1], 6),
    "head_depth_after": round(after["dimensions"][1], 6),
    "z_lock_max_delta": round(z_max_delta, 8),
    "non_head_hash_before": non_head_hash_before,
    "non_head_hash_after": non_head_hash_after,
}
print("A69_PRE_GATE_METRICS=" + repr(metrics))
if affected_vertices < 900:
    raise RuntimeError("Continuous head pass did not affect a broad enough volume")
if not 0.075 <= maximum_outward_delta <= 0.083:
    raise RuntimeError("Lower-volume expansion outside target")
if not -0.033 <= maximum_inward_delta <= -0.024:
    raise RuntimeError("Eye-band contraction outside target")
if not 0.82 <= metrics["lower_cheek_over_eye_after"] <= 0.92:
    raise RuntimeError(f"Lower cheek/eye ratio outside target: {metrics['lower_cheek_over_eye_after']}")
if not 1.20 <= metrics["head_width_height_after"] <= 1.29:
    raise RuntimeError(f"Head width/height outside target: {metrics['head_width_height_after']}")
if maximum_y_delta > 0.030:
    raise RuntimeError("Head depth change exceeded the restrained full-volume target")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadContinuousVolume_A69"
scene["comforting_cat_v6_stage"] = "HEAD_CONTINUOUS_VOLUME"
scene["comforting_cat_v6_attempt"] = 69
scene["comforting_cat_v6_dominant_defect"] = "x_only_cheek_shelves_and_wide_eye_band"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_CONTINUOUS_VOLUME",
    "attempt": 69,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "x_only_cheek_shelves_and_wide_eye_band",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head continuous X/Y volume"],
        "preserved": ["head Z", "all non-head geometry", "topology", "materials", "camera", "lights"],
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
