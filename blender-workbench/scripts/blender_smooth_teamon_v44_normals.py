from __future__ import annotations

import hashlib
import json
from math import acos, degrees, exp, isfinite, radians
import os
from pathlib import Path
from statistics import median
import struct
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
SOURCE_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v39_ada_rigged.blend"
SOURCE_GLB = PROJECT_ROOT / "public" / "models" / "teamon_reference_v39_ada_hand.glb"
OUTPUT_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v44_surface_smoothed.blend"
OUTPUT_GLB = PROJECT_ROOT / "public" / "models" / "teamon_reference_v44_surface_smoothed.glb"
BASELINE_RENDER = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v44-baseline-v39-hero.png"
HERO_RENDER = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v44-surface-smoothed-hero.png"
FRONT_RENDER = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v44-surface-smoothed-front.png"
SIDE_RENDER = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "teamon-v44-surface-smoothed-side.png"
REST_RENDER = PROJECT_ROOT / "public" / "images" / "teamon-reference-v44-surface-smoothed-rest.png"
PRESSED_RENDER = PROJECT_ROOT / "public" / "images" / "teamon-reference-v44-surface-smoothed-pressed.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_export_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_structural_qa.json"
VALIDATION_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_validation.json"

EXPECTED_BLEND_SHA256 = "F8AA93862928DDA6CACED75475D0E1B1B5E1B11CF327E6967D0FD94CE9345C53"
EXPECTED_GLB_SHA256 = "96A01BC3A9CFECE8EC87391EAA469355C399E9574E25EC592F6D0A73FECCCDFE"
WHITE_MATERIAL = "TEAMON_Robot_White_Ada"
MATERIAL_VALUES = {
    "Roughness": 0.36,
    "Coat Weight": 0.26,
    "Coat Roughness": 0.12,
}
HAND_SHELLS = (
    "TEAMON_Ada_Palm",
    "TEAMON_Ada_Thumb",
    "TEAMON_Ada_Index",
    "TEAMON_Ada_Middle",
    "TEAMON_Ada_Ring",
    "TEAMON_Ada_Little",
    "TEAMON_Ada_ForearmShell",
)
FAIR_TARGETS = (
    "TEAMON_Ada_Palm",
    "TEAMON_Ada_Thumb",
    "TEAMON_Ada_Index",
)
FAIR_TOTAL_CAPS = {
    "TEAMON_Ada_Palm": 0.040,
    "TEAMON_Ada_Thumb": 0.040,
    "TEAMON_Ada_Index": 0.025,
}
REQUIRED_NODES = (
    "TEAMON_CompositionRoot",
    "TEAMON_Base",
    "TEAMON_Keycap",
    "TEAMON_RGB_Underplate",
    "TEAMON_PressGroup",
    "TEAMON_HandPressGroup",
    *HAND_SHELLS,
)
REQUIRED_ACTIONS = ("TEAMON_HandPressGroup", "TEAMON_PressGroup")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def source_fingerprint(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "sha256": sha256_file(path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def mesh_hash(obj: bpy.types.Object) -> str:
    mesh = obj.data
    digest = hashlib.sha256()
    digest.update(struct.pack("<III", len(mesh.vertices), len(mesh.edges), len(mesh.polygons)))
    for vertex in mesh.vertices:
        digest.update(struct.pack("<3d", *vertex.co))
    for edge in mesh.edges:
        digest.update(struct.pack("<2I", *edge.vertices))
    for polygon in mesh.polygons:
        digest.update(struct.pack("<I", len(polygon.vertices)))
        digest.update(struct.pack(f"<{len(polygon.vertices)}I", *polygon.vertices))
        digest.update(struct.pack("<?", polygon.use_smooth))
    return digest.hexdigest()


def topology_hash(obj: bpy.types.Object) -> str:
    mesh = obj.data
    digest = hashlib.sha256()
    digest.update(struct.pack("<III", len(mesh.vertices), len(mesh.edges), len(mesh.polygons)))
    for edge in mesh.edges:
        digest.update(struct.pack("<2I", *edge.vertices))
    for polygon in mesh.polygons:
        digest.update(struct.pack("<I", len(polygon.vertices)))
        digest.update(struct.pack(f"<{len(polygon.vertices)}I", *polygon.vertices))
    return digest.hexdigest()


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def build_adjacency(mesh: bpy.types.Mesh) -> tuple[list[set[int]], dict[tuple[int, int], list[int]]]:
    edge_faces: dict[tuple[int, int], list[int]] = {}
    for polygon in mesh.polygons:
        for edge_key in polygon.edge_keys:
            edge_faces.setdefault(tuple(sorted(edge_key)), []).append(polygon.index)
    neighbors = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        if len(edge_faces.get(tuple(sorted((a, b))), [])) == 2:
            neighbors[a].add(b)
            neighbors[b].add(a)
    return neighbors, edge_faces


def expanded(seed: set[int], neighbors: list[set[int]], rings: int) -> set[int]:
    result = set(seed)
    frontier = set(seed)
    for _ in range(rings):
        frontier = {neighbor for index in frontier for neighbor in neighbors[index]} - result
        result.update(frontier)
    return result


def junction_seed_pair(
    first: bpy.types.Object,
    second: bpy.types.Object,
    distance: float,
) -> tuple[set[int], set[int], dict[str, object]]:
    first_points, first_polygons = mesh_world_data(first)
    second_points, second_polygons = mesh_world_data(second)
    first_bvh = BVHTree.FromPolygons(first_points, first_polygons, all_triangles=False)
    second_bvh = BVHTree.FromPolygons(second_points, second_polygons, all_triangles=False)
    overlap_pairs = first_bvh.overlap(second_bvh)
    first_seed = {
        vertex
        for first_polygon, _ in overlap_pairs
        for vertex in first_polygons[first_polygon]
    }
    second_seed = {
        vertex
        for _, second_polygon in overlap_pairs
        for vertex in second_polygons[second_polygon]
    }
    for index, point in enumerate(first_points):
        nearest = second_bvh.find_nearest(point)
        if nearest is not None and nearest[3] <= distance:
            first_seed.add(index)
    for index, point in enumerate(second_points):
        nearest = first_bvh.find_nearest(point)
        if nearest is not None and nearest[3] <= distance:
            second_seed.add(index)
    return first_seed, second_seed, {
        "overlap_pairs": len(overlap_pairs),
        "first_seed": len(first_seed),
        "second_seed": len(second_seed),
        "distance": distance,
    }


def nearest_separation_seed_pair(
    first: bpy.types.Object,
    second: bpy.types.Object,
) -> tuple[set[int], set[int], dict[str, object]]:
    first_points, first_polygons = mesh_world_data(first)
    second_points, second_polygons = mesh_world_data(second)
    first_bvh = BVHTree.FromPolygons(first_points, first_polygons, all_triangles=False)
    second_bvh = BVHTree.FromPolygons(second_points, second_polygons, all_triangles=False)
    first_seed: set[int] = set()
    second_seed: set[int] = set()
    minimum = float("inf")
    for index, point in enumerate(first_points):
        nearest = second_bvh.find_nearest(point)
        if nearest is not None and nearest[3] < minimum:
            minimum = float(nearest[3])
            first_seed = {index}
            second_seed = set(second_polygons[nearest[2]])
    for index, point in enumerate(second_points):
        nearest = first_bvh.find_nearest(point)
        if nearest is not None and nearest[3] < minimum:
            minimum = float(nearest[3])
            first_seed = set(first_polygons[nearest[2]])
            second_seed = {index}
    return first_seed, second_seed, {
        "surface_distance": minimum,
        "first_seed": len(first_seed),
        "second_seed": len(second_seed),
    }


def junction_protection() -> tuple[dict[str, set[int]], dict[str, object]]:
    seeds = {name: set() for name in FAIR_TARGETS}
    stats: dict[str, object] = {}
    for first_name, second_name in (
        ("TEAMON_Ada_Palm", "TEAMON_Ada_Thumb"),
        ("TEAMON_Ada_Palm", "TEAMON_Ada_Index"),
    ):
        first_seed, second_seed, pair_stats = junction_seed_pair(
            bpy.data.objects[first_name],
            bpy.data.objects[second_name],
            0.015,
        )
        seeds[first_name].update(first_seed)
        seeds[second_name].update(second_seed)
        stats[f"{first_name}<->{second_name}"] = pair_stats
    thumb_seed, index_seed, separation_stats = nearest_separation_seed_pair(
        bpy.data.objects["TEAMON_Ada_Thumb"],
        bpy.data.objects["TEAMON_Ada_Index"],
    )
    seeds["TEAMON_Ada_Thumb"].update(thumb_seed)
    seeds["TEAMON_Ada_Index"].update(index_seed)
    stats["TEAMON_Ada_Thumb<->TEAMON_Ada_Index"] = separation_stats
    return seeds, stats


def protected_vertices(
    obj: bpy.types.Object,
    junction_seed: set[int],
) -> tuple[set[int], dict[str, int]]:
    mesh = obj.data
    mesh.update()
    neighbors, edge_faces = build_adjacency(mesh)
    camera_world = bpy.context.scene.camera.matrix_world.translation
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    facing: list[float] = []
    for polygon in mesh.polygons:
        center_world = obj.matrix_world @ polygon.center
        normal_world = (normal_matrix @ polygon.normal).normalized()
        view_world = (camera_world - center_world).normalized()
        facing.append(normal_world.dot(view_world))

    silhouette: set[int] = set()
    features: set[int] = set()
    non_manifold: set[int] = set()
    for edge in mesh.edges:
        a, b = edge.vertices
        faces = edge_faces.get(tuple(sorted((a, b))), [])
        if len(faces) != 2:
            non_manifold.update((a, b))
            continue
        first_face, second_face = faces
        if facing[first_face] * facing[second_face] <= 0.0 or min(
            abs(facing[first_face]), abs(facing[second_face])
        ) <= 0.015:
            silhouette.update((a, b))
        normal_a = (normal_matrix @ mesh.polygons[first_face].normal).normalized()
        normal_b = (normal_matrix @ mesh.polygons[second_face].normal).normalized()
        dot = max(-1.0, min(1.0, normal_a.dot(normal_b)))
        if degrees(acos(dot)) >= 55.0:
            features.update((a, b))

    local_points = [vertex.co.copy() for vertex in mesh.vertices]
    world_points = [obj.matrix_world @ point for point in local_points]
    extrema: set[int] = set()
    for points in (local_points, world_points):
        minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
        maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
        extent = maximum - minimum
        for index, point in enumerate(points):
            if any(
                abs(point[axis] - minimum[axis]) <= max(extent[axis] * 0.004, 1e-5)
                or abs(point[axis] - maximum[axis]) <= max(extent[axis] * 0.004, 1e-5)
                for axis in range(3)
            ):
                extrema.add(index)

    contact: set[int] = set()
    if obj.name == "TEAMON_Ada_Index":
        keycap = bpy.data.objects["TEAMON_Keycap"]
        keycap_points, keycap_polygons = mesh_world_data(keycap)
        keycap_bvh = BVHTree.FromPolygons(keycap_points, keycap_polygons, all_triangles=False)
        contact = {
            vertex.index
            for vertex in mesh.vertices
            if (
                (nearest := keycap_bvh.find_nearest(obj.matrix_world @ vertex.co)) is not None
                and nearest[3] <= 0.010
            )
        }

    protected = expanded(silhouette | features | non_manifold | extrema, neighbors, 1)
    if contact:
        protected.update(expanded(contact, neighbors, 2))
    if junction_seed:
        protected.update(expanded(junction_seed, neighbors, 3))
    return protected, {
        "silhouette": len(silhouette),
        "features": len(features),
        "non_manifold": len(non_manifold),
        "extrema": len(extrema),
        "contact": len(contact),
        "junction_seed": len(junction_seed),
        "protected_total": len(protected),
    }


def fair_mesh(obj: bpy.types.Object, junction_seed: set[int]) -> dict[str, object]:
    obj.data = obj.data.copy()
    mesh = obj.data
    neighbors, _ = build_adjacency(mesh)
    protected, protection_stats = protected_vertices(obj, junction_seed)
    movable = [
        vertex.index
        for vertex in mesh.vertices
        if vertex.index not in protected and neighbors[vertex.index]
    ]
    if len(movable) < len(mesh.vertices) * 0.25:
        raise RuntimeError(f"Protected mask leaves too few fairing vertices on {obj.name}: {len(movable)}")
    original_local = [vertex.co.copy() for vertex in mesh.vertices]
    original_world = [obj.matrix_world @ coordinate for coordinate in original_local]
    inverse_world = obj.matrix_world.inverted()
    edge_lengths = [
        (original_world[first] - original_world[second]).length
        for first, linked in enumerate(neighbors)
        for second in linked
        if first < second
    ]
    median_edge_world = median(edge_lengths)
    per_step_cap = min(0.018, median_edge_world * 0.50)
    total_cap = min(FAIR_TOTAL_CAPS[obj.name], median_edge_world * 1.40)

    for _ in range(8):
        current_world = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
        world_normals = [(normal_matrix @ vertex.normal).normalized() for vertex in mesh.vertices]
        updates: dict[int, Vector] = {}
        for index in movable:
            weighted_delta = Vector()
            total_weight = 0.0
            for neighbor in neighbors[index]:
                edge = current_world[neighbor] - current_world[index]
                length = edge.length
                if length <= 1e-12:
                    continue
                dot = max(-1.0, min(1.0, world_normals[index].dot(world_normals[neighbor])))
                angle = acos(dot)
                weight = (1.0 / length) * exp(-((angle / radians(25.0)) ** 2))
                weighted_delta += edge * weight
                total_weight += weight
            if total_weight <= 0.0:
                continue
            delta = weighted_delta / total_weight * 0.38
            if delta.length > per_step_cap:
                delta = delta.normalized() * per_step_cap
            candidate = current_world[index] + delta
            total_delta = candidate - original_world[index]
            if total_delta.length > total_cap:
                candidate = original_world[index] + total_delta.normalized() * total_cap
            updates[index] = candidate
        for index, coordinate_world in updates.items():
            mesh.vertices[index].co = inverse_world @ coordinate_world
        for index in protected:
            mesh.vertices[index].co = original_local[index]
        mesh.update()

    displacements = [
        (obj.matrix_world.to_3x3() @ (vertex.co - original_local[vertex.index])).length
        for vertex in mesh.vertices
    ]
    changed = sorted(distance for distance in displacements if distance > 1e-8)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mesh.update()
    return {
        **protection_stats,
        "movable": len(movable),
        "changed_vertices": len(changed),
        "maximum_world_displacement": max(changed, default=0.0),
        "mean_changed_world_displacement": sum(changed) / len(changed) if changed else 0.0,
        "p95_world_displacement": changed[min(len(changed) - 1, int(len(changed) * 0.95))] if changed else 0.0,
        "median_edge_world": median_edge_world,
        "per_step_cap_world": per_step_cap,
        "total_cap_world": total_cap,
        "world_bounds": [list(value) for value in world_bounds(obj)],
    }


def matrix_values(matrix: Matrix) -> list[float]:
    return [float(value) for row in matrix for value in row]


def object_signature_at_frames(scene: bpy.types.Scene, frames: tuple[int, ...]) -> dict[str, object]:
    original_frame = scene.frame_current
    signature: dict[str, object] = {}
    for frame in frames:
        scene.frame_set(frame)
        signature[str(frame)] = {
            obj.name: {
                "type": obj.type,
                "parent": obj.parent.name if obj.parent else None,
                "matrix_local": matrix_values(obj.matrix_local),
                "matrix_world": matrix_values(obj.matrix_world),
                "hide_render": bool(obj.hide_render),
                "material_slots": [slot.material.name if slot.material else None for slot in obj.material_slots],
            }
            for obj in sorted(bpy.data.objects, key=lambda item: item.name)
        }
    scene.frame_set(original_frame)
    return signature


def action_signature() -> dict[str, object]:
    result: dict[str, object] = {}
    for action in sorted(bpy.data.actions, key=lambda item: item.name):
        channelbags = []
        for layer_index, layer in enumerate(action.layers):
            for strip_index, strip in enumerate(layer.strips):
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag is None:
                        continue
                    curves = []
                    for curve in sorted(bag.fcurves, key=lambda item: (item.data_path, item.array_index)):
                        curves.append(
                            {
                                "data_path": curve.data_path,
                                "array_index": curve.array_index,
                                "points": [
                                    [float(point.co.x), float(point.co.y), point.interpolation]
                                    for point in curve.keyframe_points
                                ],
                            }
                        )
                    channelbags.append(
                        {
                            "layer_index": layer_index,
                            "layer_name": layer.name,
                            "strip_index": strip_index,
                            "strip_type": strip.type,
                            "slot_identifier": slot.identifier,
                            "slot_target_id_type": slot.target_id_type,
                            "curves": curves,
                        }
                    )
        result[action.name] = {
            "frame_range": [float(action.frame_range[0]), float(action.frame_range[1])],
            "channelbags": channelbags,
        }
    assignments = {
        obj.name: {
            "action": obj.animation_data.action.name,
            "slot": obj.animation_data.action_slot.identifier
            if getattr(obj.animation_data, "action_slot", None)
            else None,
        }
        for obj in bpy.data.objects
        if obj.animation_data and obj.animation_data.action
    }
    return {"actions": result, "assignments": assignments}


def scalar_or_list(value: object) -> object:
    if isinstance(value, (bool, int, float, str)):
        return value
    try:
        return [float(item) for item in value]
    except (TypeError, ValueError):
        return str(value)


def material_signature() -> dict[str, object]:
    result: dict[str, object] = {}
    for material in sorted(bpy.data.materials, key=lambda item: item.name):
        item: dict[str, object] = {"use_nodes": bool(material.use_nodes)}
        if material.use_nodes:
            nodes: dict[str, object] = {}
            for node in sorted(material.node_tree.nodes, key=lambda entry: entry.name):
                nodes[node.name] = {
                    "type": node.bl_idname,
                    "inputs": {
                        socket.name: {
                            "linked": bool(socket.is_linked),
                            "value": scalar_or_list(socket.default_value),
                        }
                        for socket in node.inputs
                        if hasattr(socket, "default_value")
                    },
                }
            item["nodes"] = nodes
        result[material.name] = item
    return result


def world_light_signature(scene: bpy.types.Scene) -> dict[str, object]:
    lights = {
        obj.name: {
            "matrix_world": matrix_values(obj.matrix_world),
            "type": obj.data.type,
            "energy": float(obj.data.energy),
            "color": [float(value) for value in obj.data.color],
        }
        for obj in sorted(bpy.data.objects, key=lambda item: item.name)
        if obj.type == "LIGHT"
    }
    world = scene.world
    world_signature: dict[str, object] | None = None
    if world is not None:
        world_signature = {
            "name": world.name,
            "color": [float(value) for value in world.color],
            "use_nodes": bool(world.use_nodes),
        }
    return {"lights": lights, "world": world_signature}


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


def mesh_world_data(obj: bpy.types.Object) -> tuple[list[Vector], list[tuple[int, ...]]]:
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    polygons = [tuple(polygon.vertices) for polygon in obj.data.polygons]
    return points, polygons


def contact_metrics(index: bpy.types.Object, keycap: bpy.types.Object) -> dict[str, object]:
    index_points, index_polygons = mesh_world_data(index)
    keycap_points, keycap_polygons = mesh_world_data(keycap)
    index_bvh = BVHTree.FromPolygons(index_points, index_polygons, all_triangles=False)
    keycap_bvh = BVHTree.FromPolygons(keycap_points, keycap_polygons, all_triangles=False)
    distances: list[float] = []
    for point in index_points:
        nearest = keycap_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    for point in keycap_points:
        nearest = index_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    if not distances:
        raise RuntimeError("Unable to measure Index-Keycap surface distance")
    vertical_gap = min(point.z for point in index_points) - max(point.z for point in keycap_points)
    return {
        "surface_distance": min(distances),
        "vertical_gap": float(vertical_gap),
        "overlap_pairs": len(index_bvh.overlap(keycap_bvh)),
    }


def pair_metrics(first: bpy.types.Object, second: bpy.types.Object) -> dict[str, object]:
    first_points, first_polygons = mesh_world_data(first)
    second_points, second_polygons = mesh_world_data(second)
    first_bvh = BVHTree.FromPolygons(first_points, first_polygons, all_triangles=False)
    second_bvh = BVHTree.FromPolygons(second_points, second_polygons, all_triangles=False)
    distances: list[float] = []
    for point in first_points:
        nearest = second_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    for point in second_points:
        nearest = first_bvh.find_nearest(point)
        if nearest is not None:
            distances.append(float(nearest[3]))
    return {
        "overlap_pairs": len(first_bvh.overlap(second_bvh)),
        "surface_distance": min(distances) if distances else None,
    }


def hand_junction_metrics() -> dict[str, object]:
    return {
        "palm_thumb": pair_metrics(
            bpy.data.objects["TEAMON_Ada_Palm"],
            bpy.data.objects["TEAMON_Ada_Thumb"],
        ),
        "palm_index": pair_metrics(
            bpy.data.objects["TEAMON_Ada_Palm"],
            bpy.data.objects["TEAMON_Ada_Index"],
        ),
        "thumb_index": pair_metrics(
            bpy.data.objects["TEAMON_Ada_Thumb"],
            bpy.data.objects["TEAMON_Ada_Index"],
        ),
    }


def contact_at_frames(scene: bpy.types.Scene, frames: tuple[int, ...]) -> dict[str, object]:
    original_frame = scene.frame_current
    result: dict[str, object] = {}
    for frame in frames:
        scene.frame_set(frame)
        result[str(frame)] = contact_metrics(
            bpy.data.objects["TEAMON_Ada_Index"],
            bpy.data.objects["TEAMON_Keycap"],
        )
    scene.frame_set(original_frame)
    return result


def render(path: Path, frame: int) -> None:
    scene = bpy.context.scene
    scene.frame_set(frame)
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def render_orbit(path: Path, angle_degrees: float) -> None:
    scene = bpy.context.scene
    original_camera = scene.camera
    if original_camera is None:
        raise RuntimeError("TEAMON scene has no camera")
    target_objects = [bpy.data.objects[name] for name in HAND_SHELLS]
    points = [obj.matrix_world @ Vector(corner) for obj in target_objects for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    target = (minimum + maximum) * 0.5
    camera_data = original_camera.data.copy()
    camera = bpy.data.objects.new(f"TEAMON_V44_QA_Camera_{int(angle_degrees)}", camera_data)
    scene.collection.objects.link(camera)
    offset = original_camera.matrix_world.translation - target
    camera.location = target + Matrix.Rotation(radians(angle_degrees), 4, "Z") @ offset
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    try:
        render(path, 1)
    finally:
        scene.camera = original_camera
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.cameras.remove(camera_data)


def target_shader() -> bpy.types.ShaderNodeBsdfPrincipled:
    material = bpy.data.materials.get(WHITE_MATERIAL)
    if material is None or not material.use_nodes:
        raise RuntimeError(f"Missing white hand material: {WHITE_MATERIAL}")
    node = material.node_tree.nodes.get("Principled BSDF")
    if node is None:
        raise RuntimeError(f"Missing Principled BSDF in: {WHITE_MATERIAL}")
    return node


for path in (
    OUTPUT_BLEND,
    OUTPUT_GLB,
    BASELINE_RENDER,
    HERO_RENDER,
    FRONT_RENDER,
    SIDE_RENDER,
    REST_RENDER,
    PRESSED_RENDER,
    REPORT_PATH,
    QA_PATH,
    VALIDATION_PATH,
):
    path.parent.mkdir(parents=True, exist_ok=True)

source_before = {
    "blend": source_fingerprint(SOURCE_BLEND),
    "glb": source_fingerprint(SOURCE_GLB),
}
if source_before["blend"]["sha256"] != EXPECTED_BLEND_SHA256:
    raise RuntimeError(f"Unexpected v39 blend SHA-256: {source_before['blend']['sha256']}")
if source_before["glb"]["sha256"] != EXPECTED_GLB_SHA256:
    raise RuntimeError(f"Unexpected v39 GLB SHA-256: {source_before['glb']['sha256']}")
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected source scene {SOURCE_BLEND}, got {bpy.data.filepath}")

missing = [name for name in REQUIRED_NODES if bpy.data.objects.get(name) is None]
if missing:
    raise RuntimeError(f"Missing required TEAMON nodes: {missing}")

scene = bpy.context.scene
scene.frame_set(1)
mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
mesh_hashes_before = {obj.name: mesh_hash(obj) for obj in mesh_objects}
topology_hashes_before = {obj.name: topology_hash(obj) for obj in mesh_objects}
mesh_counts_before = {
    obj.name: [len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons)]
    for obj in mesh_objects
}
target_normals_before = {
    name: [polygon.normal.copy() for polygon in bpy.data.objects[name].data.polygons]
    for name in FAIR_TARGETS
}
target_bounds_before = {
    name: [list(value) for value in world_bounds(bpy.data.objects[name])]
    for name in FAIR_TARGETS
}
objects_before = object_signature_at_frames(scene, (1, 24))
actions_before = action_signature()
materials_before = material_signature()
lights_before = world_light_signature(scene)
camera_name_before = scene.camera.name if scene.camera else None
contact_before = contact_at_frames(scene, (1, 24))
junctions_before = hand_junction_metrics()
render_state = {
    "resolution_x": scene.render.resolution_x,
    "resolution_y": scene.render.resolution_y,
    "resolution_percentage": scene.render.resolution_percentage,
    "file_format": scene.render.image_settings.file_format,
    "filepath": scene.render.filepath,
}
render(BASELINE_RENDER, 1)

junction_seeds, junction_seed_stats = junction_protection()
fairing_metrics = {
    name: fair_mesh(bpy.data.objects[name], junction_seeds[name])
    for name in FAIR_TARGETS
}

shader = target_shader()
material_before_values = {
    name: float(shader.inputs[name].default_value)
    for name in MATERIAL_VALUES
}
for name, value in MATERIAL_VALUES.items():
    shader.inputs[name].default_value = value
material_after_values = {
    name: float(shader.inputs[name].default_value)
    for name in MATERIAL_VALUES
}

render(HERO_RENDER, 1)
render(REST_RENDER, 1)
render(PRESSED_RENDER, 24)
render_orbit(FRONT_RENDER, -25.0)
render_orbit(SIDE_RENDER, 55.0)
scene.frame_set(1)

scene.render.resolution_x = render_state["resolution_x"]
scene.render.resolution_y = render_state["resolution_y"]
scene.render.resolution_percentage = render_state["resolution_percentage"]
scene.render.image_settings.file_format = render_state["file_format"]
scene.render.filepath = render_state["filepath"]

mesh_hashes_after = {obj.name: mesh_hash(obj) for obj in mesh_objects}
topology_hashes_after = {obj.name: topology_hash(obj) for obj in mesh_objects}
mesh_counts_after = {
    obj.name: [len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons)]
    for obj in mesh_objects
}
target_bounds_after = {
    name: [list(value) for value in world_bounds(bpy.data.objects[name])]
    for name in FAIR_TARGETS
}
target_normal_dots = {
    name: [
        float(before.dot(after.normal))
        for before, after in zip(target_normals_before[name], bpy.data.objects[name].data.polygons)
    ]
    for name in FAIR_TARGETS
}
objects_after = object_signature_at_frames(scene, (1, 24))
actions_after = action_signature()
materials_after = material_signature()
lights_after = world_light_signature(scene)
camera_name_after = scene.camera.name if scene.camera else None
contact_after = contact_at_frames(scene, (1, 24))
junctions_after = hand_junction_metrics()

composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
export_objects = [composition_root, *composition_root.children_recursive]
export_objects = [
    obj
    for obj in export_objects
    if obj.type not in {"CAMERA", "LIGHT"}
    and obj.name != "TEAMON_Studio_Floor"
    and not obj.hide_render
    and obj.get("abt_export", True) is not False
]
export_meshes = [obj for obj in export_objects if obj.type == "MESH"]
triangles_export = triangle_count(export_meshes)

qa_module_path = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
sys.path.insert(0, str(qa_module_path))
import scene_qa

qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in export_meshes],
    contact_tolerance=0.02,
    floating_tolerance=0.08,
)
qa["expected_contact"] = {
    "before": contact_before,
    "after": contact_after,
    "surface_distance_max": 0.002,
    "unchanged_within_1um": all(
        abs(contact_before[frame][metric] - contact_after[frame][metric]) <= 1e-6
        for frame in ("1", "24")
        for metric in ("surface_distance", "vertical_gap")
    ),
    "rest_pass": contact_after["1"]["surface_distance"] <= 0.002,
    "pressed_pass": contact_after["24"]["surface_distance"] <= 0.002,
    "no_overlap": all(metrics["overlap_pairs"] == 0 for metrics in contact_after.values()),
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

material_other_unchanged = all(
    materials_before[name] == materials_after[name]
    for name in materials_before
    if name != WHITE_MATERIAL
)
target_material_before = materials_before[WHITE_MATERIAL]
target_material_after = materials_after[WHITE_MATERIAL]
allowed_material_change = True
for node_name, node_before in target_material_before.get("nodes", {}).items():
    node_after = target_material_after.get("nodes", {}).get(node_name)
    if node_after is None or node_before.get("type") != node_after.get("type"):
        allowed_material_change = False
        break
    for input_name, input_before in node_before.get("inputs", {}).items():
        input_after = node_after.get("inputs", {}).get(input_name)
        if input_after is None:
            allowed_material_change = False
            break
        if node_name == "Principled BSDF" and input_name in MATERIAL_VALUES:
            expected = material_after_values[input_name]
            if input_after.get("linked") or abs(float(input_after.get("value")) - expected) > 1e-7:
                allowed_material_change = False
                break
        elif input_before != input_after:
            allowed_material_change = False
            break

checks = {
    "non_target_meshes_unchanged": all(
        mesh_hashes_before[name] == mesh_hashes_after[name]
        for name in mesh_hashes_before
        if name not in FAIR_TARGETS
    ),
    "only_fair_targets_changed": all(
        mesh_hashes_before[name] != mesh_hashes_after[name]
        for name in FAIR_TARGETS
    ),
    "all_topology_and_counts_unchanged": (
        topology_hashes_before == topology_hashes_after
        and mesh_counts_before == mesh_counts_after
    ),
    "fair_target_world_bounds_unchanged": all(
        abs(target_bounds_before[name][bound][axis] - target_bounds_after[name][bound][axis]) <= 1e-7
        for name in FAIR_TARGETS
        for bound in range(2)
        for axis in range(3)
    ),
    "fair_target_faces_not_flipped": all(
        dots and min(dots) > 0.0
        for dots in target_normal_dots.values()
    ),
    "fair_target_coordinates_finite": all(
        all(isfinite(float(value)) for value in vertex.co)
        for name in FAIR_TARGETS
        for vertex in bpy.data.objects[name].data.vertices
    ),
    "fair_target_faces_nonzero": all(
        polygon.area > 1e-12
        for name in FAIR_TARGETS
        for polygon in bpy.data.objects[name].data.polygons
    ),
    "object_transforms_parenting_and_slots_unchanged_frames_1_24": objects_before == objects_after,
    "actions_and_assignments_unchanged": actions_before == actions_after,
    "required_actions_present": sorted(action.name for action in bpy.data.actions) == sorted(REQUIRED_ACTIONS),
    "frame_contract_unchanged": scene.frame_start == 1 and scene.frame_end == 24 and scene.render.fps == 30,
    "non_target_materials_unchanged": material_other_unchanged,
    "target_material_only_allowed_values_changed": allowed_material_change,
    "target_material_values_match": all(
        abs(material_after_values[name] - value) <= 1e-6
        for name, value in MATERIAL_VALUES.items()
    ),
    "lights_and_world_unchanged": lights_before == lights_after,
    "camera_unchanged": camera_name_before == camera_name_after,
    "contact_unchanged_within_1um": all(
        abs(contact_before[frame][metric] - contact_after[frame][metric]) <= 1e-6
        for frame in ("1", "24")
        for metric in ("surface_distance", "vertical_gap")
    ) and all(
        contact_before[frame]["overlap_pairs"] == contact_after[frame]["overlap_pairs"]
        for frame in ("1", "24")
    ),
    "palm_thumb_junction_preserved": (
        junctions_before["palm_thumb"]["overlap_pairs"] > 0
        and junctions_before["palm_thumb"]["overlap_pairs"]
        == junctions_after["palm_thumb"]["overlap_pairs"]
    ),
    "palm_index_junction_preserved": (
        junctions_before["palm_index"]["overlap_pairs"] > 0
        and junctions_before["palm_index"]["overlap_pairs"]
        == junctions_after["palm_index"]["overlap_pairs"]
    ),
    "thumb_index_separation_preserved": (
        junctions_before["thumb_index"]["overlap_pairs"] == 0
        and junctions_after["thumb_index"]["overlap_pairs"] == 0
        and abs(
            junctions_before["thumb_index"]["surface_distance"]
            - junctions_after["thumb_index"]["surface_distance"]
        ) <= 1e-6
    ),
    "rest_contact_pass": contact_after["1"]["surface_distance"] <= 0.002,
    "pressed_contact_pass": contact_after["24"]["surface_distance"] <= 0.002,
    "contact_has_no_overlap": all(metrics["overlap_pairs"] == 0 for metrics in contact_after.values()),
    "export_object_count": len(export_objects) == 26,
    "export_mesh_count": len(export_meshes) == 22,
    "triangle_count_exact": triangles_export == 67264,
    "triangle_budget_pass": triangles_export <= 150000,
    "qa_errors_empty": not qa["errors"],
    "export_excludes_camera_light_floor": not any(
        obj.type in {"CAMERA", "LIGHT"} or obj.name == "TEAMON_Studio_Floor"
        for obj in export_objects
    ),
}
validation_errors = [name for name, passed in checks.items() if not passed]
validation = {
    "status": "pass" if not validation_errors else "fail",
    "checks": checks,
    "errors": validation_errors,
    "warnings": qa["warnings"],
    "triangle_count": triangles_export,
    "material_before": material_before_values,
    "material_after": material_after_values,
    "fairing_metrics": fairing_metrics,
    "junction_seed_stats": junction_seed_stats,
    "target_bounds_before": target_bounds_before,
    "target_bounds_after": target_bounds_after,
    "minimum_face_normal_dot": {
        name: min(dots) if dots else None
        for name, dots in target_normal_dots.items()
    },
    "contact_before": contact_before,
    "contact_after": contact_after,
    "junctions_before": junctions_before,
    "junctions_after": junctions_after,
}
VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if validation_errors:
    raise RuntimeError(f"TEAMON v44 validation failed: {validation_errors}")

bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = composition_root
bpy.ops.export_scene.gltf(
    filepath=str(OUTPUT_GLB),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=False,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
    export_extras=True,
    export_animations=True,
    export_animation_mode="ACTIONS",
    export_frame_range=True,
    export_force_sampling=True,
)

source_after = {
    "blend": source_fingerprint(SOURCE_BLEND),
    "glb": source_fingerprint(SOURCE_GLB),
}
if source_after != source_before:
    raise RuntimeError("Immutable v39 source changed during v44 processing")

report = {
    "asset": "TEAMON v44 carefully surface-polished v39 Ada hand",
    "stage": "EXPORT_QA",
    "dominant_defect": "faceted white surfaces on the palm, thumb, and index without changing the restored hand pose",
    "source": {
        "blend": str(SOURCE_BLEND),
        **source_after["blend"],
        "glb": str(SOURCE_GLB),
        "glb_fingerprint": source_after["glb"],
        "license": "CC BY-SA 4.0",
        "revision": "2dbf3cc6c5df112066f12c11af1d001e319a766f",
    },
    "outputs": {
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
        "glb_size_bytes": OUTPUT_GLB.stat().st_size,
        "baseline": str(BASELINE_RENDER),
        "hero": str(HERO_RENDER),
        "front": str(FRONT_RENDER),
        "side": str(SIDE_RENDER),
        "rest": str(REST_RENDER),
        "pressed": str(PRESSED_RENDER),
        "qa": str(QA_PATH),
        "validation": str(VALIDATION_PATH),
    },
    "change_scope": {
        "changed": [
            {
                "geometry": list(FAIR_TARGETS),
                "operation": "camera-silhouette/contact/junction-protected bilateral Laplacian fairing",
                "metrics": fairing_metrics,
            },
            {
                "material": WHITE_MATERIAL,
                "values_before": material_before_values,
                "values_after": material_after_values,
            },
        ],
        "unchanged": [
            "all topology, polygon order, and smooth flags",
            "all non-target mesh coordinates",
            "all object transforms, parenting, pose, world bounds, and contact",
            "animation actions, assignments, timing, and travel",
            "camera, lights, and world",
            "button geometry, material, text, and interaction contract",
        ],
    },
    "animation_clips": sorted(action.name for action in bpy.data.actions),
    "triangle_count": triangles_export,
    "export_object_count": len(export_objects),
    "export_mesh_count": len(export_meshes),
    "contact": contact_after,
    "junctions": junctions_after,
    "structural_qa_errors": qa["errors"],
    "structural_qa_warning_count": len(qa["warnings"]),
    "validation_status": validation["status"],
    "status": "glb_requires_three_and_browser_validation",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("TEAMON_V44_RESULT_BEGIN")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("TEAMON_V44_RESULT_END")
