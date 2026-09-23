"""Replace the two A73 muzzle capsules with one compact, shallow continuous pad."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_unified_muzzle_attempt79"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_unified_muzzle_attempt79.blend"
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


def fit_world_bounds(obj: bpy.types.Object, target_min: Vector, target_max: Vector) -> None:
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
        vertex.co = inverse @ world
    obj.data.update()


root = bpy.data.objects["CatV6_Root"]
left = bpy.data.objects["V6_Muzzle_L"]
right = bpy.data.objects["V6_Muzzle_R"]
affected_names = {left.name, right.name}
locked_objects = [obj for obj in descendants(root) if obj.name not in affected_names]
locked_hash_before = geometry_hash(locked_objects)
before = {left.name: bounds(left), right.name: bounds(right)}
preserved_sources = [
    preserve_copy(left, "Comforting_Cat_V6", "A79", "disconnected_muzzle_capsules"),
    preserve_copy(right, "Comforting_Cat_V6", "A79", "disconnected_muzzle_capsules"),
]

combined_min = Vector(
    (
        min(before[left.name]["min"][0], before[right.name]["min"][0]),
        min(before[left.name]["min"][1], before[right.name]["min"][1]),
        min(before[left.name]["min"][2], before[right.name]["min"][2]),
    )
)
combined_max = Vector(
    (
        max(before[left.name]["max"][0], before[right.name]["max"][0]),
        max(before[left.name]["max"][1], before[right.name]["max"][1]),
        max(before[left.name]["max"][2], before[right.name]["max"][2]),
    )
)
combined_dimensions = combined_max - combined_min
combined_center = (combined_min + combined_max) * 0.5

for source, side in ((left, "L"), (right, "R")):
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = f"V6_Muzzle_{side}_SOURCE_A79"
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "disconnected_plastic_capsule"

meta_data = bpy.data.metaballs.new("V6_MuzzleUnified_A79_Meta")
meta_data.resolution = 0.018
meta_data.render_resolution = 0.012
meta_data.threshold = 0.68
meta_obj = bpy.data.objects.new("V6_MuzzleUnified_A79_Meta", meta_data)
bpy.data.collections["Comforting_Cat_V6"].objects.link(meta_obj)
for x in (-0.082, 0.082):
    element = meta_data.elements.new()
    element.co = (x, 0.0, 0.0)
    element.radius = 0.185
    element.stiffness = 2.0

bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = meta_obj
meta_obj.select_set(True)
bpy.ops.object.convert(target="MESH")
unified = bpy.context.object
unified.name = "V6_MuzzleUnified_A79"
unified.data.name = "V6_MuzzleUnified_A79_ContinuousPadMesh"
unified.parent = root
unified.matrix_parent_inverse = root.matrix_world.inverted()
unified.data.materials.append(left.data.materials[0])
for polygon in unified.data.polygons:
    polygon.use_smooth = True

target_dimensions = Vector(
    (
        combined_dimensions.x * 0.80,
        combined_dimensions.y * 0.70,
        combined_dimensions.z * 0.84,
    )
)
target_center = Vector((combined_center.x, combined_center.y - 0.015, combined_center.z - 0.006))
target_min = target_center - target_dimensions * 0.5
target_max = target_center + target_dimensions * 0.5
fit_world_bounds(unified, target_min, target_max)

# A very shallow central philtrum suggestion: recede only the front-facing center band.
unified_inverse = unified.matrix_world.inverted()
for vertex in unified.data.vertices:
    world = unified.matrix_world @ vertex.co
    x_weight = max(0.0, 1.0 - abs(world.x - target_center.x) / 0.070)
    z_weight = max(0.0, 1.0 - abs(world.z - (target_center.z - 0.015)) / 0.105)
    front_weight = max(
        0.0,
        min(1.0, (target_center.y - world.y) / max(target_dimensions.y * 0.5, 1e-6)),
    )
    world.y += 0.010 * x_weight * z_weight * front_weight
    vertex.co = unified_inverse @ world
unified.data.update()

bpy.context.view_layer.update()
after = bounds(unified)
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A79 changed locked A73 head, eyes, costume, ears, legs or tail geometry")

width_ratio = after["dimensions"][0] / combined_dimensions.x
depth_ratio = after["dimensions"][1] / combined_dimensions.y
height_ratio = after["dimensions"][2] / combined_dimensions.z
if not 0.78 <= width_ratio <= 0.82:
    raise RuntimeError(f"Unified muzzle width ratio outside target: {width_ratio}")
if not 0.68 <= depth_ratio <= 0.72:
    raise RuntimeError(f"Unified muzzle depth ratio outside target: {depth_ratio}")
if not 0.82 <= height_ratio <= 0.86:
    raise RuntimeError(f"Unified muzzle height ratio outside target: {height_ratio}")
if len(unified.data.vertices) < 200:
    raise RuntimeError("Unified muzzle topology is too coarse")

metrics = {
    "before_combined_bounds": {
        "min": list(combined_min),
        "max": list(combined_max),
        "dimensions": list(combined_dimensions),
    },
    "after_unified_bounds": after,
    "width_ratio": round(width_ratio, 5),
    "depth_ratio": round(depth_ratio, 5),
    "height_ratio": round(height_ratio, 5),
    "vertex_count": len(unified.data.vertices),
    "face_count": len(unified.data.polygons),
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A79_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_UnifiedMuzzle_A79"
scene["comforting_cat_v6_stage"] = "UNIFIED_MUZZLE"
scene["comforting_cat_v6_attempt"] = 79
scene["comforting_cat_v6_dominant_defect"] = "two_disconnected_oversized_muzzle_capsules"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "UNIFIED_MUZZLE",
    "attempt": 79,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "two_disconnected_oversized_muzzle_capsules",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Muzzle_L", "V6_Muzzle_R", "V6_MuzzleUnified_A79"],
        "preserved": [
            "A73 head",
            "eyes/pupils/highlights",
            "nose/mouth/philtrum/whiskers",
            "ears",
            "costume",
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
