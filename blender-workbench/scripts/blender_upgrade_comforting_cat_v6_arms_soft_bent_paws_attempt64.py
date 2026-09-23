"""Rebuild both long straight arms as shorter inward-bent forearms with soft paws."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_arms_soft_bent_paws_attempt64"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_arms_soft_bent_paws_attempt64.blend"
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
        for value in obj.matrix_world:
            for component in value:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        for vertex in obj.data.vertices:
            digest.update(
                f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
            )
    return digest.hexdigest()


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
arms = {
    "L": bpy.data.objects["V6_ArmUnified_L"],
    "R": bpy.data.objects["V6_ArmUnified_R"],
}
arm_names = [arm.name for arm in arms.values()]
non_arm_objects = [obj for obj in descendants(root) if obj.name not in arm_names]
non_arm_hash_before = geometry_hash(non_arm_objects)
before = {side: bounds(arm) for side, arm in arms.items()}
preserved_sources = [
    preserve_copy(arm, "Comforting_Cat_V6", "A64", "long_straight_forearm_and_pinched_paw")
    for arm in arms.values()
]

# z, center |x|, center y, X radius, Y radius. The sleeve stays broad at the
# shoulder; the exposed forearm bends inward and narrows before one soft paw
# bulge. Left/right bottom heights differ slightly, as in the reference pose.
common_specs = [
    (2.020, 0.610, -0.010, 0.055, 0.065),
    (1.930, 0.640, -0.050, 0.155, 0.170),
    (1.780, 0.660, -0.090, 0.165, 0.175),
    (1.660, 0.655, -0.120, 0.145, 0.155),
    (1.550, 0.648, -0.150, 0.118, 0.132),
    (1.380, 0.632, -0.180, 0.105, 0.118),
    (1.210, 0.615, -0.198, 0.118, 0.132),
    (1.110, 0.603, -0.202, 0.143, 0.158),
]
bottom_specs = {
    "L": (1.040, 0.596, -0.194, 0.076, 0.086),
    "R": (1.080, 0.601, -0.186, 0.076, 0.086),
}

segments = 32
after_specs: dict[str, list[tuple[float, float, float, float, float]]] = {}
for side, sign in (("L", -1.0), ("R", 1.0)):
    arm = arms[side]
    specs = common_specs + [bottom_specs[side]]
    after_specs[side] = specs
    world_vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for z_value, center_abs_x, center_y, radius_x, radius_y in specs:
        for segment in range(segments):
            angle = math.tau * segment / segments
            world_vertices.append(
                (
                    sign * center_abs_x + radius_x * math.cos(angle),
                    center_y + radius_y * math.sin(angle),
                    z_value,
                )
            )
    for ring in range(len(specs) - 1):
        for segment in range(segments):
            next_segment = (segment + 1) % segments
            a = ring * segments + segment
            b = ring * segments + next_segment
            c = (ring + 1) * segments + next_segment
            d = (ring + 1) * segments + segment
            faces.append((a, b, c, d))
    bottom_center = len(world_vertices)
    world_vertices.append((sign * specs[-1][1], specs[-1][2], specs[-1][0]))
    top_center = len(world_vertices)
    world_vertices.append((sign * specs[0][1], specs[0][2], specs[0][0]))
    last_ring = (len(specs) - 1) * segments
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        faces.append((bottom_center, last_ring + next_segment, last_ring + segment))
        faces.append((top_center, segment, next_segment))

    inverse = arm.matrix_world.inverted()
    local_vertices = [inverse @ Vector(vertex) for vertex in world_vertices]
    materials = list(arm.data.materials)
    mesh = bpy.data.meshes.new(f"V6_ArmUnified_{side}_SoftBentPawMesh_A64")
    mesh.from_pydata(local_vertices, [], faces)
    mesh.update(calc_edges=True)
    old_mesh = arm.data
    arm.data = mesh
    for material in materials:
        arm.data.materials.append(material)
    for polygon in arm.data.polygons:
        center_z = sum(
            (arm.matrix_world @ arm.data.vertices[index].co).z
            for index in polygon.vertices
        ) / len(polygon.vertices)
        polygon.material_index = 0 if center_z >= 1.640 else 1
        polygon.use_smooth = True
    arm.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

bpy.context.view_layer.update()
after = {side: bounds(arm) for side, arm in arms.items()}
robe_bounds = bounds(robe)
non_arm_hash_after = geometry_hash(non_arm_objects)
if non_arm_hash_before != non_arm_hash_after:
    raise RuntimeError("Arm pass changed locked body, costume, face, or tail geometry")

metrics = {
    "left_height": after["L"]["dimensions"][2],
    "right_height": after["R"]["dimensions"][2],
    "bottom_height_asymmetry": round(after["R"]["min"][2] - after["L"]["min"][2], 5),
    "forearm_inward_bend": round(common_specs[3][1] - common_specs[-1][1], 5),
    "paw_to_shaft_width": round((2.0 * common_specs[-1][3]) / (2.0 * common_specs[5][3]), 5),
    "left_robe_x_overlap": round(overlap_1d(after["L"], robe_bounds, 0), 5),
    "right_robe_x_overlap": round(overlap_1d(after["R"], robe_bounds, 0), 5),
    "left_robe_z_overlap": round(overlap_1d(after["L"], robe_bounds, 2), 5),
    "right_robe_z_overlap": round(overlap_1d(after["R"], robe_bounds, 2), 5),
    "non_arm_hash_before": non_arm_hash_before,
    "non_arm_hash_after": non_arm_hash_after,
}
print("A64_PRE_GATE_METRICS=" + repr(metrics))
if not 0.94 <= metrics["left_height"] <= 1.00:
    raise RuntimeError("Left arm height outside target")
if not 0.90 <= metrics["right_height"] <= 0.96:
    raise RuntimeError("Right arm height outside target")
if not 0.025 <= metrics["bottom_height_asymmetry"] <= 0.055:
    raise RuntimeError("Arm pose asymmetry outside target")
if not 0.040 <= metrics["forearm_inward_bend"] <= 0.060:
    raise RuntimeError("Forearms remain too straight or bend too much")
if not 1.25 <= metrics["paw_to_shaft_width"] <= 1.45:
    raise RuntimeError("Paw transition is not softly broadened")
if metrics["left_robe_x_overlap"] < 0.12 or metrics["right_robe_x_overlap"] < 0.12:
    raise RuntimeError("Arms lost lateral contact with robe")
if metrics["left_robe_z_overlap"] < 0.90 or metrics["right_robe_z_overlap"] < 0.90:
    raise RuntimeError("Arms lost vertical contact with robe")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_ArmsSoftBentPaws_A64"
scene["comforting_cat_v6_stage"] = "ARMS_SOFT_BENT_PAWS"
scene["comforting_cat_v6_attempt"] = 64
scene["comforting_cat_v6_dominant_defect"] = "long_straight_forearms_and_pinched_paws"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "ARMS_SOFT_BENT_PAWS",
    "attempt": 64,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "long_straight_forearms_and_pinched_paws",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "ring_specs": after_specs,
    "scope_lock": {"changed": arm_names, "non_arm_geometry_unchanged": True},
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
