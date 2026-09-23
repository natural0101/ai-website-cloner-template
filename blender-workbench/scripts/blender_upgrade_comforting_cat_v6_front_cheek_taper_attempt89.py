"""Build a front-biased lower-cheek silhouette from accepted A84 without widening the skull back."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_front_cheek_taper_attempt89"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_front_cheek_taper_attempt89.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
descendants = utils["descendants"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


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


def band_half_width(
    obj: bpy.types.Object,
    z_min: float,
    z_max: float,
    y_min: float | None = None,
    y_max: float | None = None,
) -> float:
    values: list[float] = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if not z_min <= world.z <= z_max:
            continue
        if y_min is not None and world.y < y_min:
            continue
        if y_max is not None and world.y > y_max:
            continue
        values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
locked_objects = [obj for obj in descendants(root) if obj.name != head.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(head)
topology_before = (
    len(head.data.vertices),
    len(head.data.edges),
    len(head.data.polygons),
)
bands_before = {
    "front_lower_cheek": band_half_width(head, 2.43, 2.70, y_max=0.05),
    "front_eye_level": band_half_width(head, 2.72, 2.92, y_max=0.05),
    "rear_lower_cheek": band_half_width(head, 2.43, 2.70, y_min=0.15),
    "rear_eye_level": band_half_width(head, 2.72, 2.92, y_min=0.15),
}
preserved_sources = [
    preserve_copy(head, "Comforting_Cat_V6", "A89", "uniform_spherical_head")
]

inverse = head.matrix_world.inverted()
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    cheek_rise = smoothstep((world.z - 2.30) / 0.16)
    cheek_fall = 1.0 - smoothstep((world.z - 2.62) / 0.15)
    cheek_weight = cheek_rise * cheek_fall
    temple_rise = smoothstep((world.z - 2.68) / 0.12)
    temple_fall = 1.0 - smoothstep((world.z - 3.02) / 0.10)
    temple_weight = temple_rise * temple_fall
    radial_weight = smoothstep((abs(world.x) - 0.12) / 0.40)
    front_weight = 1.0 - smoothstep((world.y + 0.05) / 0.20)
    if abs(world.x) > 1e-6:
        direction = 1.0 if world.x > 0.0 else -1.0
        world.x += direction * radial_weight * front_weight * (
            0.052 * cheek_weight - 0.015 * temple_weight
        )
    vertex.co = inverse @ world
head.data.update()
bpy.context.view_layer.update()

after = bounds(head)
topology_after = (
    len(head.data.vertices),
    len(head.data.edges),
    len(head.data.polygons),
)
bands_after = {
    "front_lower_cheek": band_half_width(head, 2.43, 2.70, y_max=0.05),
    "front_eye_level": band_half_width(head, 2.72, 2.92, y_max=0.05),
    "rear_lower_cheek": band_half_width(head, 2.43, 2.70, y_min=0.15),
    "rear_eye_level": band_half_width(head, 2.72, 2.92, y_min=0.15),
}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A89 changed locked A84 face, ears, scarf, costume, legs or tail")
if topology_before != topology_after:
    raise RuntimeError("A89 changed V6_Head topology")

width_height = after["dimensions"][0] / after["dimensions"][2]
y_ratio = after["dimensions"][1] / before["dimensions"][1]
z_ratio = after["dimensions"][2] / before["dimensions"][2]
rear_delta = max(
    abs(bands_after["rear_lower_cheek"] - bands_before["rear_lower_cheek"]),
    abs(bands_after["rear_eye_level"] - bands_before["rear_eye_level"]),
)
if not 1.34 <= after["dimensions"][0] <= 1.37:
    raise RuntimeError(f"A89 head width outside target: {after['dimensions'][0]}")
if not 1.30 <= width_height <= 1.34:
    raise RuntimeError(f"A89 head W/H outside target: {width_height}")
if not 0.98 <= y_ratio <= 1.02 or abs(z_ratio - 1.0) > 1e-5:
    raise RuntimeError("A89 changed locked head depth or height")
if rear_delta > 0.003:
    raise RuntimeError(f"A89 widened the rear skull: {rear_delta}")
if bands_after["front_lower_cheek"] <= bands_after["front_eye_level"]:
    raise RuntimeError("A89 failed to move widest front band below the eyes")
if not 0.665 <= bands_after["front_lower_cheek"] <= 0.685:
    raise RuntimeError("A89 front lower-cheek band outside localized target")
if not 0.620 <= bands_after["front_eye_level"] <= 0.650:
    raise RuntimeError("A89 front eye band outside tapered target")
if not 0.025 <= (
    bands_after["front_lower_cheek"] - bands_after["front_eye_level"]
) <= 0.050:
    raise RuntimeError("A89 front cheek-to-eye taper outside target")

metrics = {
    "before": before,
    "after": after,
    "bands_before_half_width": bands_before,
    "bands_after_half_width": bands_after,
    "head_width_height": round(width_height, 5),
    "y_depth_ratio": round(y_ratio, 5),
    "z_height_ratio": round(z_ratio, 5),
    "rear_half_width_delta": round(rear_delta, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A89_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FrontCheekTaper_A89"
scene["comforting_cat_v6_stage"] = "FRONT_CHEEK_TAPER"
scene["comforting_cat_v6_attempt"] = 89
scene["comforting_cat_v6_dominant_defect"] = "front_cheek_mass_without_rear_skull_bulge"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FRONT_CHEEK_TAPER",
    "attempt": 89,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "front_cheek_mass_without_rear_skull_bulge",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head existing vertex X only, front-weighted"],
        "preserved": [
            "A84 tunic",
            "A79 unified muzzle",
            "eyes/pupils/highlights/brows/nose/mouth/whiskers",
            "ears",
            "scarf/robe/satchel/arms",
            "legs",
            "tail",
            "camera/lights/materials",
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
