"""Broaden the lower front cheek envelope with two restrained connected fur lobes."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_lower_cheek_envelope_attempt68"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_lower_cheek_envelope_attempt68.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


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


def band_half_width(
    obj: bpy.types.Object,
    z_min: float,
    z_max: float,
    maximum_y: float | None = None,
) -> float:
    values: list[float] = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if not z_min <= world.z <= z_max:
            continue
        if maximum_y is not None and world.y > maximum_y:
            continue
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
front_lower_half_before = band_half_width(head, 2.43, 2.54, maximum_y=0.02)
preserved_source = preserve_copy(
    head,
    "Comforting_Cat_V6",
    "A68",
    "lower_cheek_fur_envelope_missing",
)

inverse = head.matrix_world.inverted()
affected_vertices = 0
maximum_delta = 0.0
maximum_rear_delta = 0.0
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    absolute_x = abs(world.x)
    if world.z < 2.43 or world.z > 2.67 or absolute_x < 0.30 or world.y > 0.16:
        continue

    side_weight = smoothstep(0.30, 0.44, absolute_x)
    # The projected front silhouette is formed by vertices close to world Y=0,
    # not by the deepest frontal vertices. Keep full influence through that rim,
    # then fade quickly before reaching the rear half of the head.
    front_weight = 1.0 - smoothstep(0.02, 0.12, world.y)
    profile = (
        0.080 * gaussian(world.z, 2.62, 0.052)
        + 0.100 * gaussian(world.z, 2.49, 0.052)
        - 0.026 * gaussian(world.z, 2.555, 0.026)
    )
    delta = clamp(profile, 0.0, 0.085) * side_weight * front_weight
    target_absolute_x = min(absolute_x + delta, eye_half_before - 0.001)
    actual_delta = target_absolute_x - absolute_x
    if actual_delta <= 0.0001:
        continue
    world.x = math.copysign(target_absolute_x, world.x)
    vertex.co = inverse @ world
    affected_vertices += 1
    maximum_delta = max(maximum_delta, actual_delta)
    if world.y >= 0.10:
        maximum_rear_delta = max(maximum_rear_delta, actual_delta)
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
    raise RuntimeError("Lower-cheek pass changed locked non-head geometry")
if topology_before != topology_after:
    raise RuntimeError("Lower-cheek pass changed head topology")

yz_max_delta = 0.0
for vertex, original in zip(head.data.vertices, original_world, strict=True):
    current = head.matrix_world @ vertex.co
    yz_max_delta = max(yz_max_delta, abs(current.y - original.y), abs(current.z - original.z))
if yz_max_delta > 0.00001:
    raise RuntimeError(f"Lower-cheek pass changed locked Y/Z coordinates: {yz_max_delta}")

eye_half_after = band_half_width(head, 2.67, 2.88)
lower_half_after = band_half_width(head, 2.43, 2.57)
front_lower_half_after = band_half_width(head, 2.43, 2.54, maximum_y=0.02)
metrics = {
    "affected_vertices": affected_vertices,
    "maximum_world_x_delta": round(maximum_delta, 6),
    "maximum_rear_world_x_delta": round(maximum_rear_delta, 6),
    "eye_band_half_width_before": round(eye_half_before, 6),
    "eye_band_half_width_after": round(eye_half_after, 6),
    "lower_cheek_half_width_before": round(lower_half_before, 6),
    "lower_cheek_half_width_after": round(lower_half_after, 6),
    "lower_cheek_over_eye_before": round(lower_half_before / eye_half_before, 5),
    "lower_cheek_over_eye_after": round(lower_half_after / eye_half_after, 5),
    "front_lower_half_width_before": round(front_lower_half_before, 6),
    "front_lower_half_width_after": round(front_lower_half_after, 6),
    "head_width_before": round(before["dimensions"][0], 6),
    "head_width_after": round(after["dimensions"][0], 6),
    "yz_lock_max_delta": round(yz_max_delta, 8),
    "non_head_hash_before": non_head_hash_before,
    "non_head_hash_after": non_head_hash_after,
}
print("A68_PRE_GATE_METRICS=" + repr(metrics))
if affected_vertices < 20:
    raise RuntimeError("Too few vertices affected for a broad cheek envelope")
if not 0.060 <= maximum_delta <= 0.085:
    raise RuntimeError("Cheek expansion amplitude outside restrained target")
if maximum_rear_delta > 0.012:
    raise RuntimeError("Cheek deformation leaked too far into the rear profile")
if abs(metrics["eye_band_half_width_after"] - metrics["eye_band_half_width_before"]) > 0.002:
    raise RuntimeError("Eye-band head width changed")
if not 0.82 <= metrics["lower_cheek_over_eye_after"] <= 0.89:
    raise RuntimeError(f"Lower cheek/eye ratio outside target: {metrics['lower_cheek_over_eye_after']}")
if abs(metrics["head_width_after"] - metrics["head_width_before"]) > 0.005:
    raise RuntimeError("Overall head width changed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_LowerCheekEnvelope_A68"
scene["comforting_cat_v6_stage"] = "LOWER_CHEEK_ENVELOPE"
scene["comforting_cat_v6_attempt"] = 68
scene["comforting_cat_v6_dominant_defect"] = "lower_cheek_fur_envelope_missing"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "LOWER_CHEEK_ENVELOPE",
    "attempt": 68,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "lower_cheek_fur_envelope_missing",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head X coordinates at front lower cheek only"],
        "preserved": ["all head Y/Z", "all non-head geometry", "topology", "materials", "camera", "lights"],
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
