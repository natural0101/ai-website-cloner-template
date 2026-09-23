"""Remediate only the lower arm rings into a wrist, paw bulge, and rounded underside."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_paw_loop_remediation_attempt65"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_paw_loop_remediation_attempt65.blend"
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


def selected_vertex_hash(obj: bpy.types.Object, indices: range) -> str:
    digest = hashlib.sha256()
    for index in indices:
        vertex = obj.data.vertices[index]
        digest.update(
            f"{index}:{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
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
    preserve_copy(arm, "Comforting_Cat_V6", "A65", "pinched_ring7_paw_plug")
    for arm in arms.values()
]

segments = 32
ring_count = 8
upper_locked_hash_before = {
    side: selected_vertex_hash(arm, range(0, 4 * segments))
    for side, arm in arms.items()
}
target_radii = {
    5: (0.078, 0.095),
    6: (0.134, 0.142),
    7: (0.098, 0.108),
}
inward_shifts = {5: 0.008, 6: 0.012, 7: 0.022}
ring_metrics: dict[str, dict[str, list[float] | float]] = {}

for side, sign in (("L", -1.0), ("R", 1.0)):
    arm = arms[side]
    if len(arm.data.vertices) != ring_count * segments:
        raise RuntimeError(f"Unexpected {arm.name} vertex count: {len(arm.data.vertices)}")
    old_materials = list(arm.data.materials)
    old_vertices = [vertex.co.copy() for vertex in arm.data.vertices]
    world_vertices = [arm.matrix_world @ coordinate for coordinate in old_vertices]
    old_bounds = bounds(arm)
    old_min_z = old_bounds["min"][2]

    per_ring: dict[int, tuple[Vector, float, float]] = {}
    for ring in range(ring_count):
        points = world_vertices[ring * segments : (ring + 1) * segments]
        center = sum(points, Vector()) / len(points)
        radius_x = (max(point.x for point in points) - min(point.x for point in points)) * 0.5
        radius_y = (max(point.y for point in points) - min(point.y for point in points)) * 0.5
        per_ring[ring] = (center, radius_x, radius_y)

    for ring in (5, 6, 7):
        center, old_radius_x, old_radius_y = per_ring[ring]
        target_radius_x, target_radius_y = target_radii[ring]
        target_center_x = center.x - sign * inward_shifts[ring]
        target_z = center.z + (0.058 if ring == 7 else 0.0)
        for segment in range(segments):
            index = ring * segments + segment
            world = world_vertices[index]
            normalized_x = (world.x - center.x) / max(old_radius_x, 1.0e-6)
            normalized_y = (world.y - center.y) / max(old_radius_y, 1.0e-6)
            world.x = target_center_x + normalized_x * target_radius_x
            world.y = center.y + normalized_y * target_radius_y
            world.z = target_z
            world_vertices[index] = world

    bottom_ring_indices = set(range(7 * segments, 8 * segments))
    kept_faces: list[tuple[int, ...]] = []
    kept_material_indices: list[int] = []
    removed_bottom_cap = 0
    for polygon in arm.data.polygons:
        indices = tuple(polygon.vertices)
        if len(indices) == segments and set(indices) == bottom_ring_indices:
            removed_bottom_cap += 1
            continue
        kept_faces.append(indices)
        kept_material_indices.append(polygon.material_index)
    if removed_bottom_cap != 1:
        raise RuntimeError(f"Expected one bottom cap on {arm.name}; got {removed_bottom_cap}")

    ring7_center = sum(world_vertices[7 * segments : 8 * segments], Vector()) / segments
    pole_index = len(world_vertices)
    world_vertices.append(Vector((ring7_center.x, ring7_center.y, old_min_z)))
    for segment in range(segments):
        next_segment = (segment + 1) % segments
        kept_faces.append((pole_index, 7 * segments + next_segment, 7 * segments + segment))
        kept_material_indices.append(1)

    inverse = arm.matrix_world.inverted()
    local_vertices = [inverse @ world for world in world_vertices]
    new_mesh = bpy.data.meshes.new(f"V6_ArmUnified_{side}_PawLoopMesh_A65")
    new_mesh.from_pydata(local_vertices, [], kept_faces)
    new_mesh.update(calc_edges=True)
    old_mesh = arm.data
    arm.data = new_mesh
    for material in old_materials:
        arm.data.materials.append(material)
    for polygon, material_index in zip(arm.data.polygons, kept_material_indices, strict=True):
        polygon.material_index = material_index
        polygon.use_smooth = True
    arm.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    ring_metrics[side] = {
        "old_min_z": old_min_z,
        "wrist_full_x": 2.0 * target_radii[5][0],
        "paw_full_x": 2.0 * target_radii[6][0],
        "paw_full_y": 2.0 * target_radii[6][1],
        "lower_loop_full_x": 2.0 * target_radii[7][0],
        "lower_loop_full_y": 2.0 * target_radii[7][1],
        "paw_to_wrist": target_radii[6][0] / target_radii[5][0],
        "lower_loop_to_paw": target_radii[7][0] / target_radii[6][0],
    }

bpy.context.view_layer.update()
after = {side: bounds(arm) for side, arm in arms.items()}
robe_bounds = bounds(robe)
non_arm_hash_after = geometry_hash(non_arm_objects)
if non_arm_hash_before != non_arm_hash_after:
    raise RuntimeError("Paw pass changed locked geometry or transforms")

upper_locked_hash_after = {
    side: selected_vertex_hash(arm, range(0, 4 * segments))
    for side, arm in arms.items()
}
if upper_locked_hash_before != upper_locked_hash_after:
    raise RuntimeError("Paw pass changed locked sleeve rings 0-3")

metrics = {
    "ring_metrics": ring_metrics,
    "left_min_z": after["L"]["min"][2],
    "right_min_z": after["R"]["min"][2],
    "bottom_asymmetry": round(after["R"]["min"][2] - after["L"]["min"][2], 5),
    "left_bounds_x_delta": [
        round(after["L"]["min"][0] - before["L"]["min"][0], 5),
        round(after["L"]["max"][0] - before["L"]["max"][0], 5),
    ],
    "right_bounds_x_delta": [
        round(after["R"]["min"][0] - before["R"]["min"][0], 5),
        round(after["R"]["max"][0] - before["R"]["max"][0], 5),
    ],
    "left_y_min_delta": round(after["L"]["min"][1] - before["L"]["min"][1], 5),
    "right_y_min_delta": round(after["R"]["min"][1] - before["R"]["min"][1], 5),
    "left_robe_x_overlap": round(overlap_1d(after["L"], robe_bounds, 0), 5),
    "right_robe_x_overlap": round(overlap_1d(after["R"], robe_bounds, 0), 5),
    "left_robe_y_overlap": round(overlap_1d(after["L"], robe_bounds, 1), 5),
    "right_robe_y_overlap": round(overlap_1d(after["R"], robe_bounds, 1), 5),
    "left_robe_z_overlap": round(overlap_1d(after["L"], robe_bounds, 2), 5),
    "right_robe_z_overlap": round(overlap_1d(after["R"], robe_bounds, 2), 5),
    "topology": {
        side: {
            "vertices": len(arm.data.vertices),
            "edges": len(arm.data.edges),
            "faces": len(arm.data.polygons),
        }
        for side, arm in arms.items()
    },
    "upper_locked_hash_before": upper_locked_hash_before,
    "upper_locked_hash_after": upper_locked_hash_after,
    "non_arm_hash_before": non_arm_hash_before,
    "non_arm_hash_after": non_arm_hash_after,
}
print("A65_PRE_GATE_METRICS=" + repr(metrics))
for side in ("L", "R"):
    ring_side = ring_metrics[side]
    if not 0.145 <= ring_side["wrist_full_x"] <= 0.165:
        raise RuntimeError(f"{side} wrist width outside target")
    if not 0.265 <= ring_side["paw_full_x"] <= 0.290:
        raise RuntimeError(f"{side} paw width outside target")
    if not 0.270 <= ring_side["paw_full_y"] <= 0.300:
        raise RuntimeError(f"{side} paw depth outside target")
    if not 1.65 <= ring_side["paw_to_wrist"] <= 1.90:
        raise RuntimeError(f"{side} paw/wrist ratio outside target")
    if ring_side["lower_loop_to_paw"] < 0.65:
        raise RuntimeError(f"{side} lower loop remains pinched")
    if metrics["topology"][side] != {"vertices": 257, "edges": 512, "faces": 257}:
        raise RuntimeError(f"{side} topology outside closed pole target")
if abs(metrics["left_min_z"] - 0.945) > 0.003:
    raise RuntimeError("Left paw minimum Z changed")
if abs(metrics["right_min_z"] - 1.035) > 0.003:
    raise RuntimeError("Right paw minimum Z changed")
if not 0.085 <= metrics["bottom_asymmetry"] <= 0.095:
    raise RuntimeError("Paw bottom asymmetry changed")
if min(metrics["left_bounds_x_delta"]) < -0.005 or max(metrics["left_bounds_x_delta"]) > 0.005:
    raise RuntimeError("Left upper silhouette envelope changed")
if min(metrics["right_bounds_x_delta"]) < -0.005 or max(metrics["right_bounds_x_delta"]) > 0.005:
    raise RuntimeError("Right upper silhouette envelope changed")
if metrics["left_y_min_delta"] < -0.020 or metrics["right_y_min_delta"] < -0.020:
    raise RuntimeError("Paw depth expanded too far forward")
if metrics["left_robe_x_overlap"] < 0.20 or metrics["right_robe_x_overlap"] < 0.18:
    raise RuntimeError("Paws lost lateral robe contact")
if metrics["left_robe_y_overlap"] < 0.37 or metrics["right_robe_y_overlap"] < 0.37:
    raise RuntimeError("Paws lost depth contact with robe")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_PawLoopRemediation_A65"
scene["comforting_cat_v6_stage"] = "PAW_LOOP_REMEDIATION"
scene["comforting_cat_v6_attempt"] = 65
scene["comforting_cat_v6_dominant_defect"] = "pinched_ring7_paw_plug"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "PAW_LOOP_REMEDIATION",
    "attempt": 65,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "pinched_ring7_paw_plug",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
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
