"""Move A84 head mass from the eye-level sphere into a continuous lower cheek band."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_head_lower_cheek_relax_attempt88"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_lower_cheek_relax_attempt88.blend"
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


def band_half_width(obj: bpy.types.Object, z_min: float, z_max: float) -> float:
    values = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if z_min <= world.z <= z_max:
            values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
scarf = bpy.data.objects["V6_ScarfWrap_Upper"]
locked_objects = [obj for obj in descendants(root) if obj.name != head.name]
locked_hash_before = geometry_hash(locked_objects)
before = bounds(head)
topology_before = (
    len(head.data.vertices),
    len(head.data.edges),
    len(head.data.polygons),
)
bands_before = {
    "lower_cheek": band_half_width(head, 2.43, 2.70),
    "eye_level": band_half_width(head, 2.72, 2.92),
    "temple": band_half_width(head, 2.95, 3.15),
}
preserved_sources = [
    preserve_copy(head, "Comforting_Cat_V6", "A88", "balloon_eye_level_head")
]

inverse = head.matrix_world.inverted()
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    cheek_rise = smoothstep((world.z - 2.30) / 0.15)
    cheek_fall = 1.0 - smoothstep((world.z - 2.70) / 0.22)
    cheek_weight = cheek_rise * cheek_fall
    temple_rise = smoothstep((world.z - 2.92) / 0.08)
    temple_fall = 1.0 - smoothstep((world.z - 3.15) / 0.08)
    temple_weight = temple_rise * temple_fall
    radial_weight = smoothstep((abs(world.x) - 0.12) / 0.40)
    if abs(world.x) > 1e-6:
        direction = 1.0 if world.x > 0.0 else -1.0
        world.x += direction * radial_weight * (
            0.068 * cheek_weight - 0.030 * temple_weight
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
    "lower_cheek": band_half_width(head, 2.43, 2.70),
    "eye_level": band_half_width(head, 2.72, 2.92),
    "temple": band_half_width(head, 2.95, 3.15),
}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A88 changed locked A84 face, ears, scarf, costume, legs or tail")
if topology_before != topology_after:
    raise RuntimeError("A88 changed V6_Head topology")

width_height = after["dimensions"][0] / after["dimensions"][2]
y_ratio = after["dimensions"][1] / before["dimensions"][1]
z_ratio = after["dimensions"][2] / before["dimensions"][2]
scarf_overlap_before = before["max"][2] - bounds(scarf)["min"][2]
scarf_overlap_after = after["max"][2] - bounds(scarf)["min"][2]
if not 1.34 <= after["dimensions"][0] <= 1.41:
    raise RuntimeError(f"A88 head width outside target: {after['dimensions'][0]}")
if not 1.30 <= width_height <= 1.37:
    raise RuntimeError(f"A88 head W/H outside target: {width_height}")
if not 0.98 <= y_ratio <= 1.02:
    raise RuntimeError("A88 changed head Y depth beyond lock")
if abs(z_ratio - 1.0) > 1e-5:
    raise RuntimeError("A88 changed head Z height")
if bands_after["lower_cheek"] <= bands_after["eye_level"]:
    raise RuntimeError("A88 failed to move widest head band below the eyes")

metrics = {
    "before": before,
    "after": after,
    "bands_before_half_width": bands_before,
    "bands_after_half_width": bands_after,
    "head_width_height": round(width_height, 5),
    "y_depth_ratio": round(y_ratio, 5),
    "z_height_ratio": round(z_ratio, 5),
    "scarf_overlap_before": round(scarf_overlap_before, 5),
    "scarf_overlap_after": round(scarf_overlap_after, 5),
    "topology_before": topology_before,
    "topology_after": topology_after,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A88_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadLowerCheekRelax_A88"
scene["comforting_cat_v6_stage"] = "HEAD_LOWER_CHEEK_RELAX"
scene["comforting_cat_v6_attempt"] = 88
scene["comforting_cat_v6_dominant_defect"] = "balloon_sphere_head_missing_lower_cheek_mass"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_LOWER_CHEEK_RELAX",
    "attempt": 88,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "balloon_sphere_head_missing_lower_cheek_mass",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head existing vertex X only"],
        "preserved": [
            "A84 tunic",
            "A79 unified muzzle",
            "eyes/pupils/highlights/brows/nose/mouth/whiskers",
            "ears",
            "scarf/robe/satchel/arms",
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
