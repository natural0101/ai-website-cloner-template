"""Remediate A44's shield, board and sharp hem while retaining useful cloth gains."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_cloth_contour_remediation_attempt45"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_garment_cloth_reblock_attempt44.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_cloth_contour_remediation_attempt45.blend"
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


def object_center(obj: bpy.types.Object) -> Vector:
    obj_bounds = bounds(obj)
    return Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )


def fit_mesh_world(obj: bpy.types.Object, center: Vector, dimensions: Vector) -> None:
    old_center = object_center(obj)
    old_dimensions = Vector(bounds(obj)["dimensions"])
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        offset = world - old_center
        offset.x *= dimensions.x / old_dimensions.x
        offset.y *= dimensions.y / old_dimensions.y
        offset.z *= dimensions.z / old_dimensions.z
        vertex.co = inverse @ (center + offset)
    obj.data.update()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
upper = bpy.data.objects["V6_ScarfWrap_Upper"]
drape = bpy.data.objects["V6_Scarf_FrontDrape"]
affected = [robe, tunic, drape]
before = {obj.name: bounds(obj) for obj in affected}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A45", "a44_cloth_visual_gate_failure")
    for obj in affected
]

# Round the A44 pointed robe corners by lifting and tucking only the extreme
# lower side vertices. The approved narrower torso envelope stays unchanged.
inverse = robe.matrix_world.inverted()
for vertex in robe.data.vertices:
    world = robe.matrix_world @ vertex.co
    if world.z < 0.84:
        side = clamp(abs(world.x) / 0.72, 0.0, 1.0)
        lower = 1.0 - smoothstep(0.66, 0.84, world.z)
        world.x *= 1.0 - 0.055 * side * lower
        world.z += 0.060 * side * side * lower
    vertex.co = inverse @ world
robe.data.update()

# Return the pale panel to reference-like visual dominance: wider than A43 but
# no longer a chest-sized board. Taper it toward a soft asymmetric hem.
fit_mesh_world(tunic, Vector((0.0, -0.4025, 1.400)), Vector((0.780, 0.075, 1.140)))
solidify = next((modifier for modifier in tunic.modifiers if modifier.type == "SOLIDIFY"), None)
if solidify is not None:
    solidify.thickness = 0.026
inverse = tunic.matrix_world.inverted()
tunic_bounds = bounds(tunic)
for vertex in tunic.data.vertices:
    world = tunic.matrix_world @ vertex.co
    u = clamp((world.z - tunic_bounds["min"][2]) / tunic_bounds["dimensions"][2], 0.0, 1.0)
    normalized_x = clamp(world.x / 0.39, -1.0, 1.0)
    taper = 0.84 + 0.16 * smoothstep(0.0, 0.72, u)
    world.x *= taper
    lower = 1.0 - smoothstep(0.84, 1.18, world.z)
    world.z -= lower * (
        0.032 * (1.0 - abs(normalized_x))
        + 0.014 * normalized_x
    )
    world.y += 0.008 * (1.0 - normalized_x * normalized_x)
    vertex.co = inverse @ world
tunic.data.update()

# Convert the A44 front shield into one compact diagonal cloth overlap and seat
# it through both upper scarf and robe in Y/Z.
fit_mesh_world(drape, Vector((-0.030, -0.350, 2.180)), Vector((0.780, 0.110, 0.270)))
inverse = drape.matrix_world.inverted()
for vertex in drape.data.vertices:
    world = drape.matrix_world @ vertex.co
    side = clamp((world.x + 0.420) / 0.780, 0.0, 1.0)
    world.z += 0.028 * (side - 0.5) + 0.012 * math.sin(side * math.pi)
    world.y += 0.006 * math.sin(side * math.pi)
    vertex.co = inverse @ world
drape.data.update()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in affected}
upper_bounds = bounds(upper)
metrics = {
    "robe_width_over_height": round(
        after[robe.name]["dimensions"][0] / after[robe.name]["dimensions"][2], 5
    ),
    "tunic_width_over_robe": round(
        after[tunic.name]["dimensions"][0] / after[robe.name]["dimensions"][0], 5
    ),
    "tunic_depth": after[tunic.name]["dimensions"][1],
    "drape_width": after[drape.name]["dimensions"][0],
    "drape_height": after[drape.name]["dimensions"][2],
    "drape_upper_y_overlap": round(overlap_1d(after[drape.name], upper_bounds, 1), 5),
    "drape_upper_z_overlap": round(overlap_1d(after[drape.name], upper_bounds, 2), 5),
    "drape_robe_y_overlap": round(overlap_1d(after[drape.name], after[robe.name], 1), 5),
    "drape_robe_z_overlap": round(overlap_1d(after[drape.name], after[robe.name], 2), 5),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ClothContourRemediation_A45"
scene["comforting_cat_v6_stage"] = "CLOTH_CONTOUR_REMEDIATION"
scene["comforting_cat_v6_attempt"] = 45
scene["comforting_cat_v6_dominant_defect"] = "a44_shield_board_and_pointed_hem"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "CLOTH_CONTOUR_REMEDIATION",
    "attempt": 45,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a44_shield_board_and_pointed_hem",
    "preserved_sources": preserved_sources,
    "retained_from_a44": [
        "narrower robe torso profile",
        "asymmetric reprofiled arms",
        "closed arm boundary loops",
        "front-heavy scarf wrap",
    ],
    "before": before,
    "after": after,
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
