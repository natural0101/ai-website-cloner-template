"""Remediate A50 crown spike and pasted-on ears with embedded lofted ear volumes."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v6_crown_ear_root_continuity_attempt52"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_head_ear_silhouette_rebuild_attempt50.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_crown_ear_root_continuity_attempt52.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def interpolate_knots(value: float, knots: list[tuple[float, float]]) -> float:
    if value <= knots[0][0]:
        return knots[0][1]
    if value >= knots[-1][0]:
        return knots[-1][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:], strict=True):
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            t = t * t * (3.0 - 2.0 * t)
            return y0 * (1.0 - t) + y1 * t
    raise RuntimeError("Knot interpolation failed")


def replace_mesh(
    obj: bpy.types.Object,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mesh_name: str,
) -> None:
    materials = list(obj.data.materials)
    mesh = bpy.data.meshes.new(mesh_name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    old_mesh = obj.data
    obj.data = mesh
    for material in materials:
        obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.update()
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def loft_ear(obj: bpy.types.Object, sign: float) -> None:
    # Closed elliptical stations converge to one apex, so the side profile has
    # no constant-depth wall or rear duplicate flap.
    stations = [
        (3.100, sign * 0.440, 0.165, 0.000, 0.110),
        (3.180, sign * 0.445, 0.155, 0.005, 0.100),
        (3.300, sign * 0.450, 0.120, 0.015, 0.075),
        (3.420, sign * 0.455, 0.065, 0.025, 0.040),
    ]
    ring_segments = 8
    vertices: list[tuple[float, float, float]] = []
    for z, center_x, radius_x, center_y, radius_y in stations:
        for index in range(ring_segments):
            angle = 2.0 * math.pi * index / ring_segments
            vertices.append(
                (
                    center_x + sign * radius_x * math.cos(angle),
                    center_y + radius_y * math.sin(angle),
                    z,
                )
            )
    apex_index = len(vertices)
    vertices.append((sign * 0.460, 0.035, 3.530))
    faces: list[tuple[int, ...]] = [tuple(reversed(range(ring_segments)))]
    for station_index in range(len(stations) - 1):
        current = station_index * ring_segments
        following = (station_index + 1) * ring_segments
        for index in range(ring_segments):
            next_index = (index + 1) % ring_segments
            faces.append(
                (
                    current + index,
                    current + next_index,
                    following + next_index,
                    following + index,
                )
            )
    top_ring = (len(stations) - 1) * ring_segments
    for index in range(ring_segments):
        next_index = (index + 1) % ring_segments
        faces.append((top_ring + index, top_ring + next_index, apex_index))
    replace_mesh(obj, vertices, faces, f"{obj.name}_VolumetricLoftMesh_A52")


def inner_patch(obj: bpy.types.Object, sign: float) -> None:
    outline = [
        (sign * 0.325, -0.112, 3.170),
        (sign * 0.560, -0.112, 3.170),
        (sign * 0.535, -0.077, 3.300),
        (sign * 0.460, -0.030, 3.460),
        (sign * 0.385, -0.077, 3.300),
    ]
    thickness = 0.006
    vertices = outline + [(x, y + thickness, z) for x, y, z in outline]
    count = len(outline)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, count + index, count + next_index, next_index))
    replace_mesh(obj, vertices, faces, f"{obj.name}_SlopePatchMesh_A52")


def band_half_width(obj: bpy.types.Object, z_center: float, tolerance: float = 0.012) -> float:
    values = [
        abs((obj.matrix_world @ vertex.co).x)
        for vertex in obj.data.vertices
        if abs((obj.matrix_world @ vertex.co).z - z_center) <= tolerance
    ]
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
face_names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
    "V6_Muzzle_L",
    "V6_Muzzle_R",
    "V6_Nose",
    "V6_Eyebrow_L",
    "V6_Eyebrow_R",
    "V6_Mouth",
    "V6_Philtrum",
    *[f"V6_Whisker_{side}_{index}" for side in ("L", "R") for index in range(3)],
]
face_objects = [bpy.data.objects[name] for name in face_names]
face_before = {obj.name: bounds(obj) for obj in face_objects}
before = {obj.name: bounds(obj) for obj in [head, *ears]}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A52", "crown_spike_and_pasted_ear_baseline")
    for obj in [head, *ears]
]

# Preserve every point below the upper-crown gate. Above it, widen the crown
# smoothly and compress the upper rings into a soft cap instead of one pole.
inverse = head.matrix_world.inverted()
width_scale_knots = [
    (3.080, 1.000),
    (3.140, 1.080),
    (3.200, 1.280),
    (3.240, 1.245),
    (3.280, 1.320),
    (3.310, 1.360),
    (3.360, 1.000),
]
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    if world.z <= 3.080:
        continue
    old_z = world.z
    scale = interpolate_knots(old_z, width_scale_knots)
    world.x *= scale
    world.y *= 1.0 + (scale - 1.0) * 0.42
    if old_z > 3.300:
        world.z = 3.310
    vertex.co = inverse @ world
head.data.update()

for side, sign in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    loft_ear(outer, sign)
    inner_patch(inner, sign)
    for modifier in list(outer.modifiers):
        if modifier.type == "BEVEL":
            outer.modifiers.remove(modifier)
    bevel = outer.modifiers.new(f"{outer.name}_LoftSoftEdge_A52", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    for modifier in list(inner.modifiers):
        if modifier.type == "BEVEL":
            inner.modifiers.remove(modifier)
    inner_bevel = inner.modifiers.new(f"{inner.name}_PatchSoftEdge_A52", "BEVEL")
    inner_bevel.width = 0.004
    inner_bevel.segments = 2
    inner_bevel.limit_method = "ANGLE"

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in [head, *ears]}
face_after = {obj.name: bounds(obj) for obj in face_objects}

face_max_delta = 0.0
for name in face_names:
    for key in ("min", "max", "dimensions"):
        for before_value, after_value in zip(face_before[name][key], face_after[name][key], strict=True):
            face_max_delta = max(face_max_delta, abs(before_value - after_value))
if face_max_delta > 0.002:
    raise RuntimeError(f"Face lock exceeded: {face_max_delta}")

outer_dims = after["V6_Ear_R"]["dimensions"]
metrics = {
    "head_top_before": before["V6_Head"]["max"][2],
    "head_top_after": after["V6_Head"]["max"][2],
    "crown_half_width_z3_14": round(band_half_width(head, 3.14), 5),
    "crown_half_width_z3_20": round(band_half_width(head, 3.20), 5),
    "crown_half_width_z3_24": round(band_half_width(head, 3.24), 5),
    "crown_half_width_z3_28": round(band_half_width(head, 3.28), 5),
    "outer_ear_dimensions": outer_dims,
    "outer_ear_height_width": round(outer_dims[2] / outer_dims[0], 5),
    "outer_ear_depth": outer_dims[1],
    "head_ear_z_overlap": round(
        min(after["V6_Head"]["max"][2], after["V6_Ear_R"]["max"][2])
        - max(after["V6_Head"]["min"][2], after["V6_Ear_R"]["min"][2]),
        5,
    ),
    "face_lock_max_delta": round(face_max_delta, 6),
}

if not 3.30 <= metrics["head_top_after"] <= 3.32:
    raise RuntimeError(f"Head cap outside target: {metrics['head_top_after']}")
if not 1.20 <= metrics["outer_ear_height_width"] <= 1.48:
    raise RuntimeError(f"Ear H/W outside target: {metrics['outer_ear_height_width']}")
if not 0.18 <= metrics["head_ear_z_overlap"] <= 0.22:
    raise RuntimeError(f"Ear root overlap outside target: {metrics['head_ear_z_overlap']}")

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_CrownEarRootContinuity_A52"
scene["comforting_cat_v6_stage"] = "CROWN_EAR_ROOT_CONTINUITY"
scene["comforting_cat_v6_attempt"] = 52
scene["comforting_cat_v6_dominant_defect"] = "crown_spike_and_pasted_slab_ears"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "CROWN_EAR_ROOT_CONTINUITY",
    "attempt": 52,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "crown_spike_and_pasted_slab_ears",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "face_before": face_before,
    "face_after": face_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Head vertices above world Z 3.08", *ear_names],
        "face_bounds_locked_to": 0.002,
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
