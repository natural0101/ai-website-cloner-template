"""Rebuild the A73 ears as deep, backward-leaning cups with recessed inner dishes."""

from __future__ import annotations

import bmesh
import hashlib
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_ear_true_cup_attempt78"
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
    CHECKPOINT_DIR / "comforting_cat_v6_before_ear_true_cup_attempt78.blend"
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


def catmull_rom_closed(
    controls: list[tuple[float, float]], samples_per_segment: int = 4
) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    count = len(controls)
    for index in range(count):
        p0 = controls[(index - 1) % count]
        p1 = controls[index]
        p2 = controls[(index + 1) % count]
        p3 = controls[(index + 2) % count]
        for sample in range(samples_per_segment):
            t = sample / samples_per_segment
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * (
                2.0 * p1[0]
                + (-p0[0] + p2[0]) * t
                + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
            )
            z = 0.5 * (
                2.0 * p1[1]
                + (-p0[1] + p2[1]) * t
                + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
            )
            result.append((x, z))
    return result


def replace_mesh(
    obj: bpy.types.Object,
    world_vertices: list[Vector],
    faces: list[tuple[int, ...]],
    mesh_suffix: str,
) -> None:
    material = obj.data.materials[0] if obj.data.materials else None
    inverse = obj.matrix_world.inverted()
    local_vertices = [inverse @ vertex for vertex in world_vertices]
    mesh = bpy.data.meshes.new(f"{obj.name}_{mesh_suffix}_Mesh")
    mesh.from_pydata(local_vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj.data = mesh
    if material is not None:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True


def build_outer_cup(
    obj: bpy.types.Object,
    center_x: float,
    sign: float,
    head_top: float,
    contour: list[tuple[float, float]],
) -> dict[str, float]:
    z_root = head_top - 0.255
    height = 0.420
    half_width = 0.188
    outer_front: list[Vector] = []
    inner_front: list[Vector] = []
    inner_lip: list[Vector] = []
    outer_back: list[Vector] = []
    for u, normalized_z in contour:
        normalized_z = max(-0.04, min(1.0, normalized_z))
        tip_weight = smoothstep((normalized_z - 0.20) / 0.80)
        outward = sign * 0.032 * tip_weight
        x = center_x + half_width * u + outward
        z = z_root + height * normalized_z
        root_embed = 0.155 * (1.0 - smoothstep(normalized_z / 0.24))
        front_y = -0.142 + 0.082 * tip_weight + root_embed
        outer_front.append(Vector((x, front_y, z)))

        inner_x = center_x + (x - center_x) * 0.675
        inner_z = z_root + 0.055 + (height - 0.105) * normalized_z
        inner_y = front_y + 0.034
        inner_front.append(Vector((inner_x, inner_y, inner_z)))
        inner_lip.append(Vector((inner_x, inner_y + 0.042, inner_z)))

        back_x = center_x + (x - center_x) * 0.92
        back_z = z - 0.008 + 0.012 * tip_weight
        back_y = front_y + 0.215 - 0.025 * tip_weight
        outer_back.append(Vector((back_x, back_y, back_z)))

    count = len(contour)
    world_vertices = outer_front + inner_front + inner_lip + outer_back
    back_center_index = len(world_vertices)
    back_center = Vector(
        (
            sum(point.x for point in outer_back) / count,
            sum(point.y for point in outer_back) / count + 0.008,
            sum(point.z for point in outer_back) / count,
        )
    )
    world_vertices.append(back_center)
    faces: list[tuple[int, ...]] = []
    for index in range(count):
        next_index = (index + 1) % count
        outer = index
        outer_next = next_index
        inner = count + index
        inner_next = count + next_index
        lip = 2 * count + index
        lip_next = 2 * count + next_index
        back = 3 * count + index
        back_next = 3 * count + next_index
        faces.append((outer, outer_next, inner_next, inner))
        faces.append((inner, inner_next, lip_next, lip))
        faces.append((outer_next, outer, back, back_next))
        faces.append((back, back_center_index, back_next))
    replace_mesh(obj, world_vertices, faces, "TrueCupA78")
    return {
        "root_z": z_root,
        "tip_z": z_root + height,
        "front_y_min": min(point.y for point in outer_front),
        "back_y_max": max(point.y for point in outer_back),
        "cup_depth": max(point.y for point in outer_back) - min(point.y for point in outer_front),
        "rim_width_ratio": 1.0 - 0.675,
    }


def build_inner_dish(
    obj: bpy.types.Object,
    center_x: float,
    sign: float,
    head_top: float,
    contour: list[tuple[float, float]],
) -> dict[str, float]:
    z_root = head_top - 0.255
    height = 0.420
    half_width = 0.188
    boundary: list[Vector] = []
    for u, normalized_z in contour:
        normalized_z = max(-0.04, min(1.0, normalized_z))
        tip_weight = smoothstep((normalized_z - 0.20) / 0.80)
        outward = sign * 0.032 * tip_weight
        outer_x = center_x + half_width * u + outward
        outer_z = z_root + height * normalized_z
        root_embed = 0.155 * (1.0 - smoothstep(normalized_z / 0.24))
        outer_front_y = -0.142 + 0.082 * tip_weight + root_embed
        boundary.append(
            Vector(
                (
                    center_x + (outer_x - center_x) * 0.675,
                    outer_front_y + 0.084,
                    z_root + 0.055 + (height - 0.105) * normalized_z,
                )
            )
        )
    count = len(boundary)
    dish_center = Vector(
        (
            center_x + sign * 0.006,
            sum(point.y for point in boundary) / count + 0.092,
            z_root + 0.205,
        )
    )
    middle = [dish_center.lerp(point, 0.56) + Vector((0.0, -0.027, 0.0)) for point in boundary]
    world_vertices = boundary + middle + [dish_center]
    center_index = 2 * count
    faces: list[tuple[int, ...]] = []
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
        faces.append((count + index, count + next_index, center_index))
    replace_mesh(obj, world_vertices, faces, "RecessedDishA78")
    return {
        "boundary_y_min": min(point.y for point in boundary),
        "dish_center_y": dish_center.y,
        "dish_recess": dish_center.y - min(point.y for point in boundary),
    }


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
ear_names = ["V6_Ear_L", "V6_InnerEar_L", "V6_Ear_R", "V6_InnerEar_R"]
ears = [bpy.data.objects[name] for name in ear_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in ear_names]
locked_hash_before = geometry_hash(locked_objects)
before = {obj.name: bounds(obj) for obj in ears}
topology_before = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A78", "flat_ear_petal") for obj in ears
]

controls = [
    (-0.94, 0.02),
    (-1.00, 0.18),
    (-0.74, 0.54),
    (-0.36, 0.83),
    (0.00, 1.00),
    (0.36, 0.83),
    (0.74, 0.54),
    (1.00, 0.18),
    (0.94, 0.02),
    (0.48, -0.035),
    (0.00, -0.045),
    (-0.48, -0.035),
]
contour = catmull_rom_closed(controls, samples_per_segment=4)
head_top = bounds(head)["max"][2]
per_side: dict[str, dict[str, object]] = {}
for side, sign in (("L", -1.0), ("R", 1.0)):
    outer = bpy.data.objects[f"V6_Ear_{side}"]
    inner = bpy.data.objects[f"V6_InnerEar_{side}"]
    outer_before = before[outer.name]
    center_x = 0.5 * (outer_before["min"][0] + outer_before["max"][0])
    cup_metrics = build_outer_cup(outer, center_x, sign, head_top, contour)
    dish_metrics = build_inner_dish(inner, center_x, sign, head_top, contour)
    per_side[side] = {
        "center_x": center_x,
        "cup": cup_metrics,
        "dish": dish_metrics,
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in ears}
topology_after = {
    obj.name: (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
    for obj in ears
}
locked_hash_after = geometry_hash(locked_objects)
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A78 changed locked A73 head, face, costume, legs or tail geometry")
for side in ("L", "R"):
    outer = after[f"V6_Ear_{side}"]
    inner = after[f"V6_InnerEar_{side}"]
    cup = per_side[side]["cup"]
    dish = per_side[side]["dish"]
    if float(cup["cup_depth"]) < 0.25:
        raise RuntimeError(f"{side} cup is not deep enough")
    if float(dish["dish_recess"]) < 0.075:
        raise RuntimeError(f"{side} inner dish is not recessed enough")
    if not 0.34 <= outer["dimensions"][0] <= 0.43:
        raise RuntimeError(f"{side} outer cup width outside structural gate")
    if inner["dimensions"][0] / outer["dimensions"][0] > 0.72:
        raise RuntimeError(f"{side} inner dish still fills too much of outer ear")

metrics = {
    "head_top": head_top,
    "contour_samples": len(contour),
    "per_side": per_side,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
}
print("A78_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_EarTrueCup_A78"
scene["comforting_cat_v6_stage"] = "EAR_TRUE_CUP"
scene["comforting_cat_v6_attempt"] = 78
scene["comforting_cat_v6_dominant_defect"] = "flat_vertical_ear_fins_without_recess"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "EAR_TRUE_CUP",
    "attempt": 78,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_vertical_ear_fins_without_recess",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "topology_before": topology_before,
    "topology_after": topology_after,
    "metrics": metrics,
    "scope_lock": {
        "changed": ear_names,
        "preserved": [
            "A73 head/face/proportions",
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
