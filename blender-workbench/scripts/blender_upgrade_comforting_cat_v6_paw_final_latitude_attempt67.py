"""Round only the A66 ring8-to-pole segment with one final latitude ring."""

from __future__ import annotations

import hashlib
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_paw_final_latitude_attempt67"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_paw_underside_latitude_attempt66.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_paw_final_latitude_attempt67.blend"
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


root = bpy.data.objects["CatV6_Root"]
arms = {
    "L": bpy.data.objects["V6_ArmUnified_L"],
    "R": bpy.data.objects["V6_ArmUnified_R"],
}
arm_names = [arm.name for arm in arms.values()]
non_arm_objects = [obj for obj in descendants(root) if obj.name not in arm_names]
non_arm_hash_before = geometry_hash(non_arm_objects)
before = {side: bounds(arm) for side, arm in arms.items()}
preserved_sources = [
    preserve_copy(arm, "Comforting_Cat_V6", "A67", "a66_residual_dark_underside_rim")
    for arm in arms.values()
]

segments = 32
pole_index = 8 * segments
ring8_start = pole_index + 1
locked_vertex_count = ring8_start
locked_hash_before = {
    side: selected_vertex_hash(arm, locked_vertex_count)
    for side, arm in arms.items()
}
ring8_radius_x = 0.090
ring8_radius_y = 0.097
ring9_radius_x = 0.055
ring9_radius_y = 0.059
side_metrics: dict[str, dict[str, float]] = {}

for side, arm in arms.items():
    if len(arm.data.vertices) != 289:
        raise RuntimeError(f"Unexpected A66 {arm.name} vertex count: {len(arm.data.vertices)}")
    world_vertices = [arm.matrix_world @ vertex.co for vertex in arm.data.vertices]
    old_materials = list(arm.data.materials)
    ring8_points = world_vertices[ring8_start : ring8_start + segments]
    ring8_center = sum(ring8_points, Vector()) / segments
    old_radius_x = (max(point.x for point in ring8_points) - min(point.x for point in ring8_points)) * 0.5
    old_radius_y = (max(point.y for point in ring8_points) - min(point.y for point in ring8_points)) * 0.5
    min_z = before[side]["min"][2]

    for segment in range(segments):
        index = ring8_start + segment
        world = world_vertices[index]
        normalized_x = (world.x - ring8_center.x) / max(old_radius_x, 1.0e-6)
        normalized_y = (world.y - ring8_center.y) / max(old_radius_y, 1.0e-6)
        world.x = ring8_center.x + normalized_x * ring8_radius_x
        world.y = ring8_center.y + normalized_y * ring8_radius_y
        world_vertices[index] = world

    ring9_start = len(world_vertices)
    for segment in range(segments):
        source = world_vertices[ring8_start + segment]
        normalized_x = (source.x - ring8_center.x) / ring8_radius_x
        normalized_y = (source.y - ring8_center.y) / ring8_radius_y
        world_vertices.append(
            Vector(
                (
                    ring8_center.x + normalized_x * ring9_radius_x,
                    ring8_center.y + normalized_y * ring9_radius_y,
                    min_z + 0.010,
                )
            )
        )

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
        raise RuntimeError(f"Expected {segments} A66 pole faces on {arm.name}; got {removed_pole_faces}")

    for segment in range(segments):
        next_segment = (segment + 1) % segments
        ring8_current = ring8_start + segment
        ring8_next = ring8_start + next_segment
        ring9_current = ring9_start + segment
        ring9_next = ring9_start + next_segment
        kept_faces.append((ring8_current, ring8_next, ring9_next, ring9_current))
        kept_material_indices.append(1)
        kept_faces.append((pole_index, ring9_next, ring9_current))
        kept_material_indices.append(1)

    inverse = arm.matrix_world.inverted()
    local_vertices = [inverse @ world for world in world_vertices]
    new_mesh = bpy.data.meshes.new(f"V6_ArmUnified_{side}_FinalLatitudeMesh_A67")
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
        "ring8_full_x": 2.0 * ring8_radius_x,
        "ring8_full_y": 2.0 * ring8_radius_y,
        "ring9_full_x": 2.0 * ring9_radius_x,
        "ring9_full_y": 2.0 * ring9_radius_y,
        "ring9_z_above_pole": 0.010,
    }

bpy.context.view_layer.update()
after = {side: bounds(arm) for side, arm in arms.items()}
non_arm_hash_after = geometry_hash(non_arm_objects)
if non_arm_hash_before != non_arm_hash_after:
    raise RuntimeError("Final paw latitude pass changed locked geometry or transforms")

locked_hash_after = {
    side: selected_vertex_hash(arm, locked_vertex_count)
    for side, arm in arms.items()
}
if locked_hash_before != locked_hash_after:
    raise RuntimeError("Final paw latitude pass changed rings0-7 or pole")

metrics = {
    "side_metrics": side_metrics,
    "left_min_z": after["L"]["min"][2],
    "right_min_z": after["R"]["min"][2],
    "bottom_asymmetry": round(after["R"]["min"][2] - after["L"]["min"][2], 5),
    "left_bounds_delta": [
        round(after["L"][axis][index] - before["L"][axis][index], 5)
        for axis in ("min", "max")
        for index in range(3)
    ],
    "right_bounds_delta": [
        round(after["R"][axis][index] - before["R"][axis][index], 5)
        for axis in ("min", "max")
        for index in range(3)
    ],
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
print("A67_PRE_GATE_METRICS=" + repr(metrics))
for side in ("L", "R"):
    side_metric = side_metrics[side]
    if not 0.176 <= side_metric["ring8_full_x"] <= 0.184:
        raise RuntimeError(f"{side} ring8 width outside target")
    if not 0.188 <= side_metric["ring8_full_y"] <= 0.200:
        raise RuntimeError(f"{side} ring8 depth outside target")
    if not 0.104 <= side_metric["ring9_full_x"] <= 0.116:
        raise RuntimeError(f"{side} ring9 width outside target")
    if not 0.112 <= side_metric["ring9_full_y"] <= 0.124:
        raise RuntimeError(f"{side} ring9 depth outside target")
    if metrics["topology"][side] != {"vertices": 321, "edges": 640, "faces": 321}:
        raise RuntimeError(f"{side} topology outside final latitude target")
if abs(metrics["left_min_z"] - 0.945) > 0.003:
    raise RuntimeError("Left paw minimum Z changed")
if abs(metrics["right_min_z"] - 1.035) > 0.003:
    raise RuntimeError("Right paw minimum Z changed")
if not 0.085 <= metrics["bottom_asymmetry"] <= 0.095:
    raise RuntimeError("Paw bottom asymmetry changed")
if any(abs(delta) > 0.005 for delta in metrics["left_bounds_delta"]):
    raise RuntimeError("Left paw bounds changed")
if any(abs(delta) > 0.005 for delta in metrics["right_bounds_delta"]):
    raise RuntimeError("Right paw bounds changed")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_PawFinalLatitude_A67"
scene["comforting_cat_v6_stage"] = "PAW_FINAL_LATITUDE"
scene["comforting_cat_v6_attempt"] = 67
scene["comforting_cat_v6_dominant_defect"] = "a66_residual_dark_underside_rim"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "PAW_FINAL_LATITUDE",
    "attempt": 67,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "a66_residual_dark_underside_rim",
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
