"""Replace the round tube tail with a low, tapered, anisotropic plume."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v6_tail_tapered_plume_attempt59"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_face_envelope_rebalance_attempt57.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_tapered_plume_attempt59.blend"
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


def object_center(obj: bpy.types.Object) -> Vector:
    obj_bounds = bounds(obj)
    return Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )


def overlap_1d(a: dict, b: dict, axis: int) -> float:
    return max(
        0.0,
        min(a["max"][axis], b["max"][axis])
        - max(a["min"][axis], b["min"][axis]),
    )


def catmull_scalar(a: float, b: float, c: float, d: float, t: float) -> float:
    return 0.5 * (
        2.0 * b
        + (-a + c) * t
        + (2.0 * a - 5.0 * b + 4.0 * c - d) * t * t
        + (-a + 3.0 * b - 3.0 * c + d) * t * t * t
    )


def catmull_vector(a: Vector, b: Vector, c: Vector, d: Vector, t: float) -> Vector:
    return 0.5 * (
        2.0 * b
        + (-a + c) * t
        + (2.0 * a - 5.0 * b + 4.0 * c - d) * t * t
        + (-a + 3.0 * b - 3.0 * c + d) * t * t * t
    )


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
robe = bpy.data.objects["V6_Robe"]
tail_names = [tail.name, tip.name]
non_tail_objects = [obj for obj in descendants(root) if obj.name not in tail_names]
non_tail_hash_before = geometry_hash(non_tail_objects)
before = {"tail": bounds(tail), "tip": bounds(tip), "robe": bounds(robe)}
preserved_sources = [
    preserve_copy(tail, "Comforting_Cat_V6", "A59", "round_horizontal_tube_tail"),
    preserve_copy(tip, "Comforting_Cat_V6", "A59", "detached_axis_aligned_tip"),
]

# World-space guide points. rx controls the visible X/Z plume width and ry its
# much shallower front/back depth. The hidden root descends behind the robe;
# the visible part broadens once, then narrows continuously into the cream tip.
controls = [
    (Vector((0.450, 0.250, 0.840)), 0.115, 0.100),
    (Vector((0.500, 0.270, 0.570)), 0.130, 0.110),
    (Vector((0.590, 0.320, 0.350)), 0.170, 0.140),
    (Vector((0.760, 0.450, 0.270)), 0.210, 0.175),
    (Vector((0.970, 0.570, 0.240)), 0.165, 0.135),
    (Vector((1.080, 0.600, 0.250)), 0.095, 0.080),
]

samples: list[tuple[Vector, float, float]] = []
samples_per_segment = 6
for index in range(len(controls) - 1):
    p0, rx0, ry0 = controls[max(0, index - 1)]
    p1, rx1, ry1 = controls[index]
    p2, rx2, ry2 = controls[index + 1]
    p3, rx3, ry3 = controls[min(len(controls) - 1, index + 2)]
    for step in range(samples_per_segment):
        t = step / samples_per_segment
        samples.append(
            (
                catmull_vector(p0, p1, p2, p3, t),
                catmull_scalar(rx0, rx1, rx2, rx3, t),
                catmull_scalar(ry0, ry1, ry2, ry3, t),
            )
        )
samples.append(controls[-1])

ring_segments = 16
world_vertices: list[Vector] = []
faces: list[tuple[int, ...]] = []
for index, (center, rx, ry) in enumerate(samples):
    previous_center = samples[max(0, index - 1)][0]
    next_center = samples[min(len(samples) - 1, index + 1)][0]
    tangent = next_center - previous_center
    tangent_xz = Vector((tangent.x, 0.0, tangent.z))
    if tangent_xz.length < 1.0e-6:
        tangent_xz = Vector((1.0, 0.0, 0.0))
    tangent_xz.normalize()
    plume_axis = Vector((-tangent_xz.z, 0.0, tangent_xz.x))
    depth_axis = Vector((0.0, 1.0, 0.0))
    for segment in range(ring_segments):
        angle = math.tau * segment / ring_segments
        world_vertices.append(
            center
            + plume_axis * (math.cos(angle) * rx)
            + depth_axis * (math.sin(angle) * ry)
        )

for ring in range(len(samples) - 1):
    first = ring * ring_segments
    second = (ring + 1) * ring_segments
    for segment in range(ring_segments):
        next_segment = (segment + 1) % ring_segments
        faces.append((first + segment, first + next_segment, second + next_segment, second + segment))

start_center_index = len(world_vertices)
world_vertices.append(samples[0][0])
end_center_index = len(world_vertices)
world_vertices.append(samples[-1][0])
last_ring = (len(samples) - 1) * ring_segments
for segment in range(ring_segments):
    next_segment = (segment + 1) % ring_segments
    faces.append((start_center_index, next_segment, segment))
    faces.append((end_center_index, last_ring + segment, last_ring + next_segment))

inverse_tail = tail.matrix_world.inverted()
local_vertices = [inverse_tail @ vertex for vertex in world_vertices]
new_mesh = bpy.data.meshes.new("V6_TailBase_TaperedPlumeMesh_A59")
new_mesh.from_pydata(local_vertices, [], faces)
new_mesh.update()

materials = list(tail.data.materials)
old_mesh = tail.data
tail.data = new_mesh
for material in materials:
    tail.data.materials.append(material)
for polygon in tail.data.polygons:
    polygon.use_smooth = True
tail.data.update()
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)

# Compress and tangent-align the cream tip so it completes the taper instead of
# reading as a separate round plug.
tip_before = bounds(tip)
tip_center = object_center(tip)
old_dimensions = Vector(tip_before["dimensions"])
target_center = Vector((1.105, 0.605, 0.250))
target_dimensions = Vector((0.190, 0.125, 0.135))
tangent = controls[-1][0] - controls[-2][0]
angle = math.atan2(tangent.y, tangent.x)
rotation = Matrix.Rotation(angle, 4, "Z")
inverse_tip = tip.matrix_world.inverted()
for vertex in tip.data.vertices:
    world = tip.matrix_world @ vertex.co
    offset = world - tip_center
    normalized = Vector(
        (
            offset.x / old_dimensions.x,
            offset.y / old_dimensions.y,
            offset.z / old_dimensions.z,
        )
    )
    shaped = Vector(
        (
            normalized.x * target_dimensions.x,
            normalized.y * target_dimensions.y,
            normalized.z * target_dimensions.z,
        )
    )
    vertex.co = inverse_tip @ (target_center + rotation @ shaped)
tip.data.update()

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "tip": bounds(tip), "robe": bounds(robe)}
non_tail_hash_after = geometry_hash(non_tail_objects)
if non_tail_hash_before != non_tail_hash_after:
    raise RuntimeError("Tail pass changed locked body or costume geometry")

combined_min_x = min(after["tail"]["min"][0], after["tip"]["min"][0])
combined_max_x = max(after["tail"]["max"][0], after["tip"]["max"][0])
metrics = {
    "combined_x_span": round(combined_max_x - combined_min_x, 5),
    "tail_min_z": round(after["tail"]["min"][2], 5),
    "tip_min_z": round(after["tip"]["min"][2], 5),
    "max_plume_rx": max(control[1] for control in controls),
    "distal_to_bulge_rx": round(controls[-1][1] / controls[3][1], 5),
    "tail_robe_overlap_x": round(overlap_1d(after["tail"], after["robe"], 0), 5),
    "tail_robe_overlap_y": round(overlap_1d(after["tail"], after["robe"], 1), 5),
    "tail_robe_overlap_z": round(overlap_1d(after["tail"], after["robe"], 2), 5),
    "tip_tail_overlap_x": round(overlap_1d(after["tail"], after["tip"], 0), 5),
    "non_tail_hash_before": non_tail_hash_before,
    "non_tail_hash_after": non_tail_hash_after,
}
print("A59_PRE_GATE_METRICS=" + repr(metrics))
if not 0.78 <= metrics["combined_x_span"] <= 0.94:
    raise RuntimeError(f"Tail X span outside target: {metrics['combined_x_span']}")
if not 0.04 <= metrics["tail_min_z"] <= 0.10:
    raise RuntimeError(f"Tail ground clearance outside target: {metrics['tail_min_z']}")
if metrics["distal_to_bulge_rx"] > 0.50:
    raise RuntimeError("Tail does not taper strongly enough after the plume bulge")
if metrics["tip_tail_overlap_x"] < 0.07:
    raise RuntimeError(f"Cream tip overlap too small: {metrics['tip_tail_overlap_x']}")
if (
    metrics["tail_robe_overlap_x"] < 0.25
    or metrics["tail_robe_overlap_y"] < 0.20
    or metrics["tail_robe_overlap_z"] < 0.15
):
    raise RuntimeError("Tail root is not sufficiently concealed by the robe")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailTaperedPlume_A59"
scene["comforting_cat_v6_stage"] = "TAIL_TAPERED_PLUME"
scene["comforting_cat_v6_attempt"] = 59
scene["comforting_cat_v6_dominant_defect"] = "round_horizontal_tube_tail"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "TAIL_TAPERED_PLUME",
    "attempt": 59,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "round_horizontal_tube_tail",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
    "controls": [
        {"coordinate": list(center), "rx": rx, "ry": ry}
        for center, rx, ry in controls
    ],
    "scope_lock": {"changed": tail_names, "non_tail_geometry_unchanged": True},
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
