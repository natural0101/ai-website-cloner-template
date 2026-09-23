from __future__ import annotations

import json
import math
import shutil
import struct
from datetime import datetime
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
WORKBENCH = SCRIPT.parents[1]
REPO = SCRIPT.parents[2]
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"

ASSET = "mint_gold_puffy_heart_v7_section_pillow"
SCENE_NAME = "MintGoldPuffyHeartV7SectionPillow"
FRAME_START = 1
FRAME_END = 144
PREVIEW_FRAMES = (1, 36, 72, 108, 144)
VIEW_RENDERS = (
    ("front", (0.0, -6.2, 0.35), 0.0),
    ("front_3q", (3.8, -6.0, 1.2), math.radians(-9)),
    ("side", (5.8, -0.2, 0.8), math.radians(-4)),
    ("lower_closeup", (1.1, -4.6, -0.68), math.radians(-5)),
)

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def safe_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (color[0], color[1], color[2], alpha)
    mat.use_nodes = True
    mat.blend_method = "BLEND" if alpha < 1.0 else "OPAQUE"
    mat.use_screen_refraction = False
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], alpha)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def setup_scene() -> bpy.types.Scene:
    if bpy.context.scene.objects:
        checkpoint = CHECKPOINTS / f"{ASSET}_prechange_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.fps = 24
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.05
    scene.view_settings.gamma = 1.0
    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.4),
            ("gtao_factor", 0.62),
            ("use_bloom", True),
            ("bloom_intensity", 0.035),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("MintHeartWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.004, 0.020, 0.018, 1.0)
        bg.inputs["Strength"].default_value = 0.18
    return scene


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_camera(name: str, location: tuple[float, float, float], ortho_scale: float) -> bpy.types.Object:
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = location
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    look_at(cam, (0.0, 0.0, 0.05))
    bpy.context.scene.camera = cam
    return tag(cam, "review_camera", False)


def setup_lights() -> None:
    specs = [
        ("MGH_Key_soft_mint_not_exported", (-3.2, -4.4, 4.0), 420.0, 4.8, (0.78, 1.0, 0.90)),
        ("MGH_Fill_cool_not_exported", (3.6, -4.0, 2.0), 90.0, 5.8, (0.55, 0.95, 1.0)),
        ("MGH_Rim_gold_not_exported", (3.0, -2.2, 2.8), 180.0, 2.6, (1.0, 0.78, 0.36)),
        ("MGH_Lower_green_glow_not_exported", (-1.8, -2.6, -1.2), 55.0, 4.2, (0.25, 1.0, 0.62)),
    ]
    for name, loc, power, size, color in specs:
        light = bpy.data.lights.new(name, "AREA")
        light.energy = power
        light.size = size
        light.color = color
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = loc
        look_at(obj, (0.0, 0.0, 0.0))
        tag(obj, "studio_light", False)


def create_preview_background() -> None:
    mat = material("MGH_PreviewDeepGreen_not_exported", (0.005, 0.028, 0.022, 1), 0.82)
    bpy.ops.mesh.primitive_plane_add(size=7.0, location=(0.0, 1.05, 0.0), rotation=(math.radians(90), 0, 0))
    back = bpy.context.object
    back.name = "MGH_BackgroundPanel_not_exported"
    back.data.materials.append(mat)
    tag(back, "preview_background", False)

    shadow_mat = material("MGH_PreviewShadow_not_exported", (0.0, 0.010, 0.008, 1), 0.9, alpha=0.44)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.25, depth=0.012, location=(0.0, 0.62, -1.30), rotation=(math.radians(90), 0, 0))
    shadow = bpy.context.object
    shadow.name = "MGH_SoftContactShadow_not_exported"
    shadow.scale.x = 1.18
    shadow.scale.y = 0.28
    shadow.data.materials.append(shadow_mat)
    tag(shadow, "preview_shadow", False)


def cubic_bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    t: float,
) -> tuple[float, float]:
    inv = 1.0 - t
    a = inv * inv * inv
    b = 3.0 * inv * inv * t
    c = 3.0 * inv * t * t
    d = t * t * t
    return (
        a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
        a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
    )


def heart_boundary(samples: int) -> list[tuple[float, float]]:
    # Rounded hand-tuned outline: shallow cleft, full lobes, and a soft lower point.
    curves = [
        ((0.00, 0.70), (0.10, 0.86), (0.34, 0.96), (0.61, 0.87)),
        ((0.61, 0.87), (0.94, 0.77), (1.13, 0.43), (1.05, 0.08)),
        ((1.05, 0.08), (0.98, -0.33), (0.66, -0.66), (0.28, -0.91)),
        ((0.28, -0.91), (0.13, -1.01), (0.03, -1.04), (0.00, -1.00)),
        ((0.00, -1.00), (-0.03, -1.04), (-0.13, -1.01), (-0.28, -0.91)),
        ((-0.28, -0.91), (-0.66, -0.66), (-0.98, -0.33), (-1.05, 0.08)),
        ((-1.05, 0.08), (-1.13, 0.43), (-0.94, 0.77), (-0.61, 0.87)),
        ((-0.61, 0.87), (-0.34, 0.96), (-0.10, 0.86), (0.00, 0.70)),
    ]
    per_curve = max(16, samples // len(curves))
    raw: list[tuple[float, float]] = []
    for curve in curves:
        for i in range(per_curve):
            raw.append(cubic_bezier(*curve, i / per_curve))
    xs = [p[0] for p in raw]
    zs = [p[1] for p in raw]
    width = max(xs) - min(xs)
    height = max(zs) - min(zs)
    scale = min(2.70 / width, 2.50 / height)
    cx = (min(xs) + max(xs)) * 0.5
    cz = (min(zs) + max(zs)) * 0.5
    return [((x - cx) * scale, (z - cz) * scale - 0.02) for x, z in raw]


def face_material_index(center: Vector, front: bool) -> int:
    _ = center, front
    return 0


def cross2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def boundary_radius_for_angle(boundary: list[tuple[float, float]], angle: float) -> float:
    direction = (math.cos(angle), math.sin(angle))
    hits: list[float] = []
    for i, p1 in enumerate(boundary):
        p2 = boundary[(i + 1) % len(boundary)]
        seg = (p2[0] - p1[0], p2[1] - p1[1])
        denom = cross2(direction, seg)
        if abs(denom) < 1e-8:
            continue
        t = cross2(p1, seg) / denom
        u = cross2(p1, direction) / denom
        if t > 1e-5 and -1e-5 <= u <= 1.0 + 1e-5:
            hits.append(t)
    if hits:
        return min(hits)
    projections = [max(0.12, p[0] * direction[0] + p[1] * direction[1]) for p in boundary]
    return max(projections)


def smoothed_boundary_radius(boundary: list[tuple[float, float]], angle: float) -> float:
    samples = (
        (-0.050, 0.05),
        (-0.030, 0.13),
        (-0.014, 0.22),
        (0.000, 0.20),
        (0.014, 0.22),
        (0.030, 0.13),
        (0.050, 0.05),
    )
    return sum(boundary_radius_for_angle(boundary, angle + offset) * weight for offset, weight in samples)


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge0 == edge1:
        return 1.0 if value >= edge1 else 0.0
    t = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def x_intervals_at_z(boundary: list[tuple[float, float]], z: float) -> list[tuple[float, float]]:
    xs: list[float] = []
    for index, p1 in enumerate(boundary):
        p2 = boundary[(index + 1) % len(boundary)]
        z1 = p1[1]
        z2 = p2[1]
        if abs(z2 - z1) < 1e-7:
            continue
        if (z1 <= z < z2) or (z2 <= z < z1):
            t = (z - z1) / (z2 - z1)
            xs.append(p1[0] + (p2[0] - p1[0]) * t)
    xs.sort()
    deduped: list[float] = []
    for x in xs:
        if not deduped or abs(x - deduped[-1]) > 1e-4:
            deduped.append(x)
    intervals: list[tuple[float, float]] = []
    for i in range(0, len(deduped) - 1, 2):
        if deduped[i + 1] - deduped[i] > 0.002:
            intervals.append((deduped[i], deduped[i + 1]))
    return intervals


def interval_for_body(boundary: list[tuple[float, float]], z: float) -> tuple[float, float]:
    intervals = x_intervals_at_z(boundary, z)
    if not intervals:
        raise ValueError(f"No heart interval at z={z:.4f}")
    return (min(interval[0] for interval in intervals), max(interval[1] for interval in intervals))


def intervals_for_lobes(boundary: list[tuple[float, float]], z: float, fallback_left: tuple[float, float], fallback_right: tuple[float, float]) -> tuple[tuple[float, float], tuple[float, float]]:
    intervals = x_intervals_at_z(boundary, z)
    left = [interval for interval in intervals if (interval[0] + interval[1]) * 0.5 < 0.0]
    right = [interval for interval in intervals if (interval[0] + interval[1]) * 0.5 > 0.0]
    return (left[-1] if left else fallback_left, right[0] if right else fallback_right)


def pillow_height(x: float, z: float, interval: tuple[float, float], z_min: float, z_max: float, notch_z: float, depth: float) -> float:
    left, right = interval
    half = max((right - left) * 0.5, 1e-4)
    center = (left + right) * 0.5
    u = max(0.0, min(1.0, abs((x - center) / half)))
    across = 0.12 + 0.88 * ((1.0 - u * u) ** 0.46)
    bottom_taper = smoothstep(z_min + 0.02, z_min + 0.34, z)
    top_taper = 1.0 - 0.18 * smoothstep(notch_z + 0.12, z_max - 0.02, z)
    cleft_groove = math.exp(-((x / 0.20) ** 2.0)) * smoothstep(notch_z - 0.34, notch_z + 0.08, z)
    return depth * across * (0.62 + 0.38 * bottom_taper) * top_taper * (1.0 - 0.18 * cleft_groove)


def build_puffy_heart(collection: bpy.types.Collection, mats: list[bpy.types.Material]) -> tuple[bpy.types.Object, dict]:
    boundary_samples = 960
    body_rows = 76
    lobe_rows = 24
    body_columns = 72
    lobe_columns = 36
    depth = 0.62
    boundary = heart_boundary(boundary_samples)
    z_values = [p[1] for p in boundary]
    z_min = min(z_values)
    z_max = max(z_values)
    notch_z = boundary[0][1]
    z_start = z_min + 0.012
    z_end = z_max - 0.018

    front_positions: list[tuple[float, float, float]] = []
    vertex_cache: dict[tuple[int, int], int] = {}

    def front_vertex(x: float, z: float, interval: tuple[float, float]) -> int:
        key = (round(x, 5), round(z, 5))
        if key in vertex_cache:
            return vertex_cache[key]
        h = pillow_height(x, z, interval, z_min, z_max, notch_z, depth)
        index = len(front_positions)
        front_positions.append((x, -h, z))
        vertex_cache[key] = index
        return index

    def make_row(interval: tuple[float, float], z: float, columns: int) -> list[int]:
        left, right = interval
        return [
            front_vertex(left + (right - left) * (column / columns), z, interval)
            for column in range(columns + 1)
        ]

    def add_strip_faces(faces: list[tuple[int, int, int, int]], rows: list[list[int]]) -> None:
        for row_index in range(len(rows) - 1):
            current = rows[row_index]
            next_row = rows[row_index + 1]
            for column in range(min(len(current), len(next_row)) - 1):
                a = current[column]
                b = current[column + 1]
                c = next_row[column + 1]
                d = next_row[column]
                if len({a, b, c, d}) == 4:
                    faces.append((a, b, c, d))

    front_faces: list[tuple[int, ...]] = []
    body_mesh_rows: list[list[int]] = []
    for row in range(body_rows + 1):
        t = row / body_rows
        z = z_start + (notch_z - z_start) * t
        interval = interval_for_body(boundary, z)
        body_mesh_rows.append(make_row(interval, z, body_columns))
    add_strip_faces(front_faces, body_mesh_rows)

    body_top = body_mesh_rows[-1]
    left_rows = [body_top[: lobe_columns + 1]]
    right_rows = [body_top[lobe_columns:]]
    fallback_left = (front_positions[body_top[0]][0], front_positions[body_top[lobe_columns]][0])
    fallback_right = (front_positions[body_top[lobe_columns]][0], front_positions[body_top[-1]][0])
    last_left = fallback_left
    last_right = fallback_right
    for row in range(1, lobe_rows + 1):
        t = row / lobe_rows
        z = notch_z + (z_end - notch_z) * t
        left_interval, right_interval = intervals_for_lobes(boundary, z, last_left, last_right)
        left_rows.append(make_row(left_interval, z, lobe_columns))
        right_rows.append(make_row(right_interval, z, lobe_columns))
        last_left = left_interval
        last_right = right_interval
    add_strip_faces(front_faces, left_rows)
    add_strip_faces(front_faces, right_rows)

    back_offset = len(front_positions)
    vertices = list(front_positions) + [(x, -y, z) for x, y, z in front_positions]
    faces: list[tuple[int, ...]] = list(front_faces)
    faces.extend(tuple(back_offset + index for index in reversed(face)) for face in front_faces)

    edge_use: dict[tuple[int, int], int] = {}
    directed_edges: dict[tuple[int, int], tuple[int, int]] = {}
    for face in front_faces:
        for index, a in enumerate(face):
            b = face[(index + 1) % len(face)]
            key = (min(a, b), max(a, b))
            edge_use[key] = edge_use.get(key, 0) + 1
            directed_edges[key] = (a, b)
    boundary_edge_count = 0
    for key, count in edge_use.items():
        if count != 1:
            continue
        a, b = directed_edges[key]
        faces.append((a, b, back_offset + b, back_offset + a))
        boundary_edge_count += 1

    mesh = bpy.data.meshes.new("MGH_SectionPillowHeartMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("MGH_PuffyHeart_export", mesh)
    collection.objects.link(obj)
    tag(obj, "single_piece_section_pillow_heart", True)

    for mat in mats:
        obj.data.materials.append(mat)

    for poly in obj.data.polygons:
        center = Vector((0.0, 0.0, 0.0))
        for vertex_index in poly.vertices:
            center += obj.data.vertices[vertex_index].co
        center /= len(poly.vertices)
        poly.material_index = face_material_index(center, center.y < 0)
        poly.use_smooth = True

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    smooth = obj.modifiers.new("MGH_SectionPillowSurfacePolish", "SMOOTH")
    smooth.factor = 0.14
    smooth.iterations = 6
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    bpy.ops.object.shade_smooth()
    weighted = obj.modifiers.new("MGH_WebPreviewWeightedNormals", "WEIGHTED_NORMAL")
    bpy.ops.object.modifier_apply(modifier=weighted.name)
    obj.select_set(False)

    tag(obj, "reference_matched_ico_pillow_heart", True)
    stats = {
        "boundary_samples": boundary_samples,
        "body_rows": body_rows,
        "lobe_rows": lobe_rows,
        "body_columns": body_columns,
        "lobe_columns": lobe_columns,
        "depth": depth,
        "boundary_width": 2.70,
        "boundary_height": 2.50,
        "front_back_depth_ratio": round((depth * 2.0) / 2.70, 4),
        "representation": "row-section pillow mesh from rounded Bezier heart outline, no radial center topology",
        "closed_surface": True,
        "boundary_side_edges": boundary_edge_count,
        "symmetry": symmetry_report(boundary),
    }
    return obj, stats


def symmetry_report(boundary: list[tuple[float, float]]) -> dict:
    samples = len(boundary)
    max_error = 0.0
    mean_error = 0.0
    for i, (x, z) in enumerate(boundary):
        mirror = boundary[(samples - i) % samples]
        error = abs(x + mirror[0]) + abs(z - mirror[1])
        max_error = max(max_error, error)
        mean_error += error
    return {
        "sample_pairs": samples,
        "max_mirror_error": round(max_error, 8),
        "mean_mirror_error": round(mean_error / samples, 8),
    }


def create_materials() -> list[bpy.types.Material]:
    return [
        material("MGH_MintGoldSingleSurface", (0.33, 0.98, 0.67, 1.0), 0.34, metallic=0.025, emission=(0.018, 0.28, 0.13, 1.0), emission_strength=0.018),
    ]


def create_empty(collection: bpy.types.Collection, name: str) -> bpy.types.Object:
    root = bpy.data.objects.new(name, None)
    collection.objects.link(root)
    tag(root, "animated_root", True)
    return root


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def key(obj: bpy.types.Object, frame: int, loc=None, rot=None, scale=None) -> None:
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def smooth_keys(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        if not action:
            continue
        fcurves = getattr(action, "fcurves", None)
        if fcurves is None:
            continue
        for curve in fcurves:
            for point in curve.keyframe_points:
                point.interpolation = "BEZIER"


def animate_root(root: bpy.types.Object) -> None:
    poses = (
        (1, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
        (24, (0.0, -0.02, 0.030), (math.radians(1.0), math.radians(-4.5), math.radians(0.7)), (1.028, 1.028, 1.028)),
        (48, (0.0, 0.0, 0.040), (math.radians(-0.8), math.radians(3.2), math.radians(-0.6)), (0.992, 0.992, 0.992)),
        (72, (0.0, -0.025, 0.065), (math.radians(1.2), math.radians(-5.0), math.radians(0.8)), (1.035, 1.035, 1.035)),
        (108, (0.0, -0.005, 0.025), (math.radians(-0.5), math.radians(2.6), math.radians(-0.4)), (1.006, 1.006, 1.006)),
        (144, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    )
    for frame, loc, rot, scale in poses:
        key(root, frame, loc=loc, rot=rot, scale=scale)
    smooth_keys([root])


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            total += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return total


def mesh_quality(obj: bpy.types.Object) -> dict:
    zero_area = 0
    non_finite = 0
    for vertex in obj.data.vertices:
        co = vertex.co
        if not all(math.isfinite(value) for value in (co.x, co.y, co.z)):
            non_finite += 1
    for poly in obj.data.polygons:
        if poly.area < 1e-8:
            zero_area += 1
    return {
        "vertices": len(obj.data.vertices),
        "faces": len(obj.data.polygons),
        "triangles": triangle_count([obj]),
        "zero_area_faces": zero_area,
        "non_finite_vertices": non_finite,
        "materials": len(obj.data.materials),
    }


def validate(collection: bpy.types.Collection) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    tris = triangle_count(meshes)
    errors: list[str] = []
    warnings: list[str] = []
    if not meshes:
        errors.append("No exportable mesh.")
    if tris > 60000:
        warnings.append(f"Triangle count above soft icon target: {tris}/60000.")
    for obj in meshes:
        q = mesh_quality(obj)
        if q["zero_area_faces"]:
            errors.append(f"{obj.name} has {q['zero_area_faces']} zero-area faces.")
        if q["non_finite_vertices"]:
            errors.append(f"{obj.name} has {q['non_finite_vertices']} non-finite vertices.")
        if q["materials"] < 1:
            errors.append(f"{obj.name} has no material.")
    helper_leaks = [
        obj.name for obj in exportable if any(token in obj.name.lower() for token in ("camera", "light", "preview", "shadow", "background", "guide"))
    ]
    if helper_leaks:
        errors.append(f"Helper objects marked exportable: {helper_leaks}")
    return {
        "asset": ASSET,
        "triangles": tris,
        "mesh_objects": len(meshes),
        "exportable_objects": len(exportable),
        "animated_objects": len([obj for obj in exportable if obj.animation_data]),
        "mesh_quality": {obj.name: mesh_quality(obj) for obj in meshes},
        "errors": errors,
        "warnings": warnings,
    }


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    names = {obj.name for obj in collection.all_objects}
    previous = {}
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_render, obj.hide_get())
        if obj.type in {"CAMERA", "LIGHT"}:
            obj.hide_render = False
            obj.hide_set(False)
        else:
            visible = obj.name in names or not obj.get("abt_export", True)
            obj.hide_render = not visible
            obj.hide_set(not visible)
    return previous


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_render, hidden = previous[obj.name]
            obj.hide_set(hidden)


def render_frame(collection: bpy.types.Collection, frame: int, path: Path) -> dict:
    bpy.context.scene.frame_set(frame)
    previous = hide_except(collection)
    try:
        bpy.context.scene.render.filepath = str(path)
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"frame": frame, "path": str(path), "bytes": path.stat().st_size if path.is_file() else 0}


def set_camera_pose(location: tuple[float, float, float], z_tilt: float) -> None:
    camera = bpy.context.scene.camera
    camera.location = location
    look_at(camera, (0.0, 0.0, 0.03))
    camera.rotation_euler.rotate_axis("Z", z_tilt)


def render_view(collection: bpy.types.Collection, name: str, location: tuple[float, float, float], z_tilt: float) -> dict:
    set_camera_pose(location, z_tilt)
    bpy.context.scene.frame_set(36)
    path = RENDERS / f"{ASSET}_view_{name}.png"
    previous = hide_except(collection)
    try:
        bpy.context.scene.render.filepath = str(path)
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"view": name, "path": str(path), "bytes": path.stat().st_size if path.is_file() else 0}


def export_glb(collection: bpy.types.Collection) -> dict:
    exportable = [obj for obj in collection.all_objects if obj.get("abt_export", True) and obj.type not in {"CAMERA", "LIGHT"}]
    meshes = [obj for obj in exportable if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    path = EXPORTS / f"{ASSET}.glb"
    props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {"filepath": str(path), "export_format": "GLB", "use_selection": True}
    for option, value in (
        ("export_animations", True),
        ("export_frame_range", True),
        ("export_force_sampling", True),
        ("export_nla_strips", True),
        ("export_optimize_animation_size", True),
        ("export_apply", True),
    ):
        if option in props:
            kwargs[option] = value
    bpy.ops.export_scene.gltf(**kwargs)
    public_path = PUBLIC_MODELS / path.name
    shutil.copy2(path, public_path)
    public_alias_v1 = PUBLIC_MODELS / "mint_gold_puffy_heart_v1.glb"
    public_alias_v2 = PUBLIC_MODELS / "mint_gold_puffy_heart_v2_smooth.glb"
    shutil.copy2(path, public_alias_v1)
    shutil.copy2(path, public_alias_v2)
    return {
        "path": str(path),
        "public_path": str(public_path),
        "public_alias_v1": str(public_alias_v1),
        "public_alias_v2": str(public_alias_v2),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def glb_check(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        return {"file": path.name, "error": "not_glb"}
    chunk_len, _ = struct.unpack_from("<II", data, 12)
    gltf = json.loads(data[20 : 20 + chunk_len].decode("utf-8"))
    node_names = [node.get("name", "") for node in gltf.get("nodes", [])]
    helper_names = [name for name in node_names if any(token in name.lower() for token in ("camera", "light", "preview", "shadow", "guide"))]
    return {
        "file": path.name,
        "version": version,
        "declared_length": length,
        "bytes": path.stat().st_size,
        "animations": len(gltf.get("animations", [])),
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
        "helper_names": helper_names,
    }


def write_lesson_notes(report: dict) -> Path:
    path = REPORTS / f"{ASSET}_lesson_notes.md"
    text = f"""# Mint Gold Puffy Heart V1

Goal: smooth animated 3D heart, puffy like a soft ball, in light mint/green shades with warm gold-mint highlights.

Design rules used:

- mathematical symmetric heart profile, not two spheres plus a cone;
- closed biconvex/puffy mesh so it reads as a soft rounded object from front and side;
- single clean PBR material for GLB; mint, emerald and warm-gold nuance comes from lighting and curvature;
- no particles, loose marks, helper geometry, or random decorative fragments in export;
- loop animation where frame 1 and frame {FRAME_END} match exactly.

Result:

- triangles: {report['validation']['triangles']}
- mesh objects: {report['validation']['mesh_objects']}
- validation errors: {len(report['validation']['errors'])}
- validation warnings: {len(report['validation']['warnings'])}
- GLB animations: {report['glb_check'].get('animations')}
- GLB helper leaks: {len(report['glb_check'].get('helper_names', []))}
"""
    path.write_text(text, encoding="utf-8")
    return path


def build_scene() -> dict:
    setup_scene()
    setup_lights()
    create_preview_background()
    create_camera("MGH_Camera_FRONT_not_exported", (0.0, -6.2, 0.35), 3.55)

    collection = create_collection("MGH_MintGoldPuffyHeart")
    mats = create_materials()
    root = create_empty(collection, "MGH_AnimatedRoot_export")
    heart, geometry_stats = build_puffy_heart(collection, mats)
    parent_keep_world(heart, root)
    animate_root(root)

    scene_graph = {
        "asset": ASSET,
        "mode": "organic object + icon/hero object",
        "target": "smooth puffy mint-gold green animated heart for web",
        "objects": [
            {
                "id": "heart",
                "name": heart.name,
                "role": "closed puffy heart mesh",
                "representation": "concentric symmetric heart-profile rings with biconvex depth",
                "materials": [mat.name for mat in mats],
            },
            {
                "id": "root",
                "name": root.name,
                "role": "animated root for heartbeat/hover loop",
            },
        ],
        "palette": {
            "single_surface": "#54faab",
            "shadow_green": "#123f2f",
            "rim_gold_mint": "#94f280",
            "soft_highlight": "#d9ffe5",
        },
        "animation": "root scale/rotation/location loop, no loose decorative parts",
        "acceptance": [
            "heart silhouette is symmetric and instantly readable",
            "surface is rounded like a soft ball, not flat",
            "green shades lean light mint with warm gold-mint highlights",
            "no particles, floating marks, helper objects or guide geometry in GLB",
            "frame 1 and 144 match for loop playback",
        ],
        "geometry_stats": geometry_stats,
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    views = [render_view(collection, name, loc, tilt) for name, loc, tilt in VIEW_RENDERS]
    set_camera_pose((3.8, -6.0, 1.2), math.radians(-9))
    frames = [render_frame(collection, frame, RENDERS / f"{ASSET}_frame_{frame:03d}.png") for frame in PREVIEW_FRAMES]
    validation = validate(collection)
    export = {} if validation["errors"] else export_glb(collection)
    glb_report = glb_check(Path(export["path"])) if export else {}

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "views": views,
        "frames": frames,
        "validation": validation,
        "export": export,
        "glb_check": glb_report,
        "geometry_stats": geometry_stats,
        "warnings": [],
    }
    notes = write_lesson_notes(report)
    report["lesson_notes"] = str(notes)
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    report = build_scene()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
