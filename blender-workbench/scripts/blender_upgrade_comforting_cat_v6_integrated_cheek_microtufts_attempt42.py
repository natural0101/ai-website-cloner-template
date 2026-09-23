"""Probe two tiny connected cheek-fur lobes without changing topology."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_integrated_cheek_microtufts_attempt42"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_satchel_tassel_attach_attempt41.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_integrated_cheek_microtufts_attempt42.blend"
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


def band_half_width(obj: bpy.types.Object, z_min: float, z_max: float) -> float:
    values = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if z_min <= world.z <= z_max:
            values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
before = bounds(head)
topology_before = {
    "vertices": len(head.data.vertices),
    "faces": len(head.data.polygons),
}
preserved_source = preserve_copy(
    head,
    "Comforting_Cat_V6",
    "A42",
    "smooth_cheek_without_reference_fur_breakup",
)

inverse = head.matrix_world.inverted()
affected_vertices = 0
maximum_delta = 0.0
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    if abs(world.x) < 0.50 or world.z < 2.50 or world.z > 2.76:
        continue
    side_weight = smoothstep(0.50, 0.64, abs(world.x))
    front_weight = 1.0 - smoothstep(0.02, 0.24, world.y)
    profile = (
        0.016 * gaussian(world.z, 2.57, 0.028)
        + 0.020 * gaussian(world.z, 2.70, 0.030)
        - 0.007 * gaussian(world.z, 2.635, 0.018)
    )
    delta = clamp(profile, 0.0, 0.018) * side_weight * front_weight
    if delta <= 0.0:
        continue
    world.x += math.copysign(delta, world.x)
    vertex.co = inverse @ world
    affected_vertices += 1
    maximum_delta = max(maximum_delta, delta)
head.data.update()

bpy.context.view_layer.update()
after = bounds(head)
cheek_half = band_half_width(head, 2.55, 2.75)
crown_half = band_half_width(head, 3.03, 3.18)
topology_after = {
    "vertices": len(head.data.vertices),
    "faces": len(head.data.polygons),
}
metrics = {
    "affected_vertices": affected_vertices,
    "maximum_world_x_delta": round(maximum_delta, 6),
    "mesh_cheek_over_crown_width": round(cheek_half / crown_half, 5),
    "head_width": after["dimensions"][0],
    "topology_unchanged": topology_before == topology_after,
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_IntegratedCheekMicrotufts_A42"
scene["comforting_cat_v6_stage"] = "INTEGRATED_CHEEK_MICROTUFTS"
scene["comforting_cat_v6_attempt"] = 42
scene["comforting_cat_v6_dominant_defect"] = "smooth_fox_like_cheek_contour"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "INTEGRATED_CHEEK_MICROTUFTS",
    "attempt": 42,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "smooth_fox_like_cheek_contour",
    "preserved_sources": [preserved_source],
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
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
