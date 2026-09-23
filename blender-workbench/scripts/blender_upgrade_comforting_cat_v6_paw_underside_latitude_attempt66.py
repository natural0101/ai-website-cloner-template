"""Round only the A65 paw underside with one intermediate latitude ring."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_paw_underside_latitude_attempt66"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_paw_loop_remediation_attempt65.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_paw_underside_latitude_attempt66.blend"
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


def selected_vertex_hash(obj: bpy.types.Object, last_exclusive: int) -> str:
    digest = hashlib.sha256()
    for index in range(last_exclusive):
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
    preserve_copy(arm, "Comforting_Cat_V6", "A66", "a65_dark_trumpet_underside")
    for arm in arms.values()
]

segments = 32
locked_vertex_count = 7 * segments
locked_hash_before = {
    side: selected_vertex_hash(arm, locked_vertex_count)
    for side, arm in arms.items()
}
ring7_radius_x = 0.1215
ring7_radius_y = 0.1290
ring8_radius_x = 0.0690
ring8_radius_y = 0.0750
side_metrics: dict[str, dict[str, float]] = {}

for side, arm in arms.items():
    sign = -1.0 if side == "L" else 1.0
    if len(arm.data.vertices) != 257:
        raise RuntimeError(f"Unexpected A65 {arm.name} vertex count: {len(arm.data.vertices)}")
    world_vertices = [arm.matrix_world @ vertex.co for vertex in arm.data.vertices]
    old_materials = list(arm.data.materials)
    ring7_points = world_vertices[7 * segments : 8 * segments]
    ring7_center = sum(ring7_points, Vector()) / segments
    underside_center = ring7_center.copy()
    underside_center.x += sign * 0.0235
    old_radius_x = (max(point.x for point in ring7_points) - min(point.x for point in ring7_points)) * 0.5
    old_radius_y = (max(point.y for point in ring7_points) - min(point.y for point in ring7_points)) * 0.5
    min_z = before[side]["min"][2]
    pole_index = 8 * segments
    pole_world = world_vertices[pole_index]

    for segment in range(segments):
        index = 7 * segments + segment
        world = world_vertices[index]
        normalized_x = (world.x - ring7_center.x) / max(old_radius_x, 1.0e-6)
        normalized_y = (world.y - ring7_center.y) / max(old_radius_y, 1.0e-6)
        world.x = underside_center.x + normalized_x * ring7_radius_x
        world.y = underside_center.y + normalized_y * ring7_radius_y
        world_vertices[index] = world

    ring8_start = len(world_vertices)
    for segment in range(segments):
        source = world_vertices[7 * segments + segment]
        normalized_x = (source.x - underside_center.x) / ring7_radius_x
        normalized_y = (source.y - underside_center.y) / ring7_radius_y
        world_vertices.append(
            Vector(
                (
                    underside_center.x + normalized_x * ring8_radius_x,
                    underside_center.y + normalized_y * ring8_radius_y,
                    min_z + 0.026,
                )
            )
        )
    pole_world.x = underside_center.x
    pole_world.y = underside_center.y
    pole_world.z = min_z
    world_vertices[pole_index] = pole_world

    kept_faces: list[tuple[int, ...]] = []
    kept_material_indices: list[int] = []
    removed_pole_faces = 0
    for polygon in arm.data.polygons:
        indices = tuple(polygon.vertices)
        if pole_index in indices:
            removed_pole_faces += 1
            continue
        kept_faces.append(indices)
        kept_material_indices.append(polygon.material_index)
    if removed_pole_faces != segments:
        raise RuntimeError(f"Expected {segments} pole faces on {arm.name}; got {removed_pole_faces}")

    for segment in range(segments):
        next_segment = (segment + 1) % segments
        ring7_current = 7 * segments + segment
        ring7_next = 7 * segments + next_segment
        ring8_current = ring8_start + segment
        ring8_next = ring8_start + next_segment
        kept_faces.append((ring7_current, ring7_next, ring8_next, ring8_current))
        kept_material_indices.append(1)
        kept_faces.append((pole_index, ring8_next, ring8_current))
        kept_material_indices.append(1)

    inverse = arm.matrix_world.inverted()
    local_vertices = [inverse @ world for world in world_vertices]
    new_mesh = bpy.data.meshes.new(f"V6_ArmUnified_{side}_RoundedUndersideMesh_A66")
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

    side_metrics[side] = {
        "ring6_full_x": 0.268,
        "ring6_full_y": 0.284,
        "ring7_full_x": 2.0 * ring7_radius_x,
        "ring7_full_y": 2.0 * ring7_radius_y,
        "ring8_full_x": 2.0 * ring8_radius_x,
        "ring8_full_y": 2.0 * ring8_radius_y,
        "ring7_to_ring6_x": ring7_radius_x / 0.134,
        "ring8_z_above_pole": 0.026,
    }

bpy.context.view_layer.update()
after = {side: bounds(arm) for side, arm in arms.items()}
robe_bounds = bounds(robe)
non_arm_hash_after = geometry_hash(non_arm_objects)
if non_arm_hash_before != non_arm_hash_after:
    raise RuntimeError("Paw underside pass changed locked geometry or transforms")

locked_hash_after = {
    side: selected_vertex_hash(arm, locked_vertex_count)
    for side, arm in arms.items()
}
if locked_hash_before != locked_hash_after:
    raise RuntimeError("Paw underside pass changed rings 0-6")

metrics = {
    "side_metrics": side_metrics,
    "left_min_z": after["L"]["min"][2],
    "right_min_z": after["R"]["min"][2],
    "bottom_asymmetry": round(after["R"]["min"][2] - after["L"]["min"][2], 5),
    "left_x_bounds_delta": [
        round(after["L"]["min"][0] - before["L"]["min"][0], 5),
        round(after["L"]["max"][0] - before["L"]["max"][0], 5),
    ],
    "right_x_bounds_delta": [
        round(after["R"]["min"][0] - before["R"]["min"][0], 5),
        round(after["R"]["max"][0] - before["R"]["max"][0], 5),
    ],
    "left_y_min_delta": round(after["L"]["min"][1] - before["L"]["min"][1], 5),
    "right_y_min_delta": round(after["R"]["min"][1] - before["R"]["min"][1], 5),
    "left_robe_x_overlap": round(overlap_1d(after["L"], robe_bounds, 0), 5),
    "right_robe_x_overlap": round(overlap_1d(after["R"], robe_bounds, 0), 5),
    "topology": {
        side: {
            "vertices": len(arm.data.vertices),
            "edges": len(arm.data.edges),
            "faces": len(arm.data.polygons),
        }
        for side, arm in arms.items()
    },
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
    "non_arm_hash_before": non_arm_hash_before,
    "non_arm_hash_after": non_arm_hash_after,
}
print("A66_PRE_GATE_METRICS=" + repr(metrics))
for side in ("L", "R"):
    side_metric = side_metrics[side]
    if not 0.240 <= side_metric["ring7_full_x"] <= 0.246:
        raise RuntimeError(f"{side} ring7 width outside target")
    if not 0.254 <= side_metric["ring7_full_y"] <= 0.262:
        raise RuntimeError(f"{side} ring7 depth outside target")
    if not 0.132 <= side_metric["ring8_full_x"] <= 0.144:
        raise RuntimeError(f"{side} ring8 width outside target")
    if not 0.144 <= side_metric["ring8_full_y"] <= 0.156:
        raise RuntimeError(f"{side} ring8 depth outside target")
    if not 0.88 <= side_metric["ring7_to_ring6_x"] <= 0.92:
        raise RuntimeError(f"{side} ring7 still forms an inward notch")
    if metrics["topology"][side] != {"vertices": 289, "edges": 576, "faces": 289}:
        raise RuntimeError(f"{side} topology outside rounded underside target")
if abs(metrics["left_min_z"] - 0.945) > 0.003:
    raise RuntimeError("Left paw minimum Z changed")
if abs(metrics["right_min_z"] - 1.035) > 0.003:
    raise RuntimeError("Right paw minimum Z changed")
if not 0.085 <= metrics["bottom_asymmetry"] <= 0.095:
    raise RuntimeError("Paw bottom asymmetry changed")
if any(abs(delta) > 0.005 for delta in metrics["left_x_bounds_delta"]):
    raise RuntimeError("Left paw changed accepted X envelope")
if any(abs(delta) > 0.005 for delta in metrics["right_x_bounds_delta"]):
    raise RuntimeError("Right paw changed accepted X envelope")
if abs(metrics["left_y_min_delta"]) > 0.005 or abs(metrics["right_y_min_delta"]) > 0.005:
    raise RuntimeError("Paw underside changed locked ring6 depth envelope")
if metrics["left_robe_x_overlap"] < 0.20 or metrics["right_robe_x_overlap"] < 0.18:
    raise RuntimeError("Rounded paws lost robe contact")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_PawUndersideLatitude_A66"
scene["comforting_cat_v6_stage"] = "PAW_UNDERSIDE_LATITUDE"
scene["comforting_cat_v6_attempt"] = 66
scene["comforting_cat_v6_dominant_defect"] = "a65_dark_trumpet_underside"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "PAW_UNDERSIDE_LATITUDE",
    "attempt": 66,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a65_dark_trumpet_underside",
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
