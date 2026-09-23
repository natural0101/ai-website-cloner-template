"""Lighten and re-arc the v6 tail while pinning its root and ground clearance."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tail_pinned_sweep_attempt13"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_eye_round_inset_attempt12.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tail_pinned_sweep_attempt13.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


def preserve_copy(obj: bpy.types.Object) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A13"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "heavy_descending_tail_mass"
    return copy.name


def closest_polyline_u(point: Vector, knots: list[Vector]) -> float:
    best_distance = float("inf")
    best_u = 0.0
    segment_count = len(knots) - 1
    for index in range(segment_count):
        start = knots[index]
        delta = knots[index + 1] - start
        length_squared = delta.length_squared
        local = 0.0
        if length_squared > 1e-12:
            local = max(0.0, min(1.0, (point - start).dot(delta) / length_squared))
        closest = start + delta * local
        distance = (point - closest).length_squared
        if distance < best_distance:
            best_distance = distance
            best_u = (index + local) / segment_count
    return best_u


def interpolate_knots(knots: list[Vector], u: float) -> Vector:
    segment_count = len(knots) - 1
    position = max(0.0, min(1.0, u)) * segment_count
    index = min(segment_count - 1, int(position))
    local = position - index
    return knots[index].lerp(knots[index + 1], local)


def interpolate_values(values: list[float], u: float) -> float:
    segment_count = len(values) - 1
    position = max(0.0, min(1.0, u)) * segment_count
    index = min(segment_count - 1, int(position))
    local = position - index
    return values[index] * (1.0 - local) + values[index + 1] * local


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


root = bpy.data.objects["CatV6_Root"]
tail = bpy.data.objects["V6_TailBase"]
tip = bpy.data.objects["V6_TailTip"]
if tail.type != "MESH":
    raise RuntimeError(f"Expected mesh tail, got {tail.type}")
before = {"tail": bounds(tail), "tip": bounds(tip)}
preserved_sources = [preserve_copy(tail), preserve_copy(tip)]

current_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.67, 0.50, 0.48)),
    Vector((0.92, 0.70, 0.27)),
    Vector((1.14, 0.86, 0.29)),
]
target_path = [
    Vector((0.43, 0.24, 0.74)),
    Vector((0.66, 0.58, 0.56)),
    Vector((0.88, 0.80, 0.34)),
    Vector((1.10, 0.98, 0.37)),
]
radial_scales = [1.000, 0.893, 0.823, 0.911]
inverse = tail.matrix_world.inverted()
locked_vertices = 0
max_displacement = 0.0

for vertex in tail.data.vertices:
    world = tail.matrix_world @ vertex.co
    u = closest_polyline_u(world, current_path)
    if u <= 0.10:
        locked_vertices += 1
        continue
    current_center = interpolate_knots(current_path, u)
    target_center = interpolate_knots(target_path, u)
    weight = smoothstep(0.10, 0.28, u)
    new_center = current_center + weight * (target_center - current_center)
    target_radial_scale = interpolate_values(radial_scales, u)
    radial_scale = 1.0 + weight * (target_radial_scale - 1.0)
    new_world = new_center + radial_scale * (world - current_center)
    max_displacement = max(max_displacement, (new_world - world).length)
    vertex.co = inverse @ new_world
tail.data.update()

tip_dimensions_before = bounds(tip)["dimensions"]
for vertex in tip.data.vertices:
    vertex.co.x *= 0.400 / tip_dimensions_before[0]
    vertex.co.y *= 0.360 / tip_dimensions_before[1]
    vertex.co.z *= 0.340 / tip_dimensions_before[2]
tip.data.update()
tip.location = (1.12, 1.02, 0.40)

bpy.context.view_layer.update()
after = {"tail": bounds(tail), "tip": bounds(tip)}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TailPinnedSweep_A13"
scene["comforting_cat_v6_stage"] = "TAIL_PINNED_SWEEP"
scene["comforting_cat_v6_attempt"] = 13
scene["comforting_cat_v6_dominant_defect"] = "heavy_descending_tail_mass"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 3.08), (0.0, 0.0, 1.88), 4.20)
render(camera, "03_front_3q", (4.0, -7.4, 3.35), (0.0, 0.02, 1.84), 4.30)
render(camera, "04_side", (8.4, -0.35, 3.08), (0.0, 0.08, 1.82), 4.30)
render(camera, "05_back", (0.0, 8.4, 3.08), (0.0, 0.12, 1.82), 4.30)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

export_objects = descendants(root)
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)
qa = runpy.run_path(str(SCENE_QA_PATH))["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "TAIL_PINNED_SWEEP",
    "attempt": 13,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "heavy_descending_tail_mass",
    "preserved_sources": preserved_sources,
    "current_path": [list(point) for point in current_path],
    "target_path": [list(point) for point in target_path],
    "radial_scales": radial_scales,
    "locked_root_vertices": locked_vertices,
    "max_vertex_displacement": round(max_displacement, 6),
    "before": before,
    "after": after,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(qa["errors"])),
        "warnings": sorted(set(qa["warnings"])),
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
scene["comforting_cat_v6_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V6_TAIL_PINNED_SWEEP_A13=" + json.dumps(report, ensure_ascii=False))
