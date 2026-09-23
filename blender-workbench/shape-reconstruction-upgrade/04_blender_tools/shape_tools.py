"""High-level Blender 5.1 tools for stylized figures and reference matching.

This module is deliberately separate from the base AI Blender Agent Kit. It does
not monkey-patch existing tools, delete user objects, download assets, or infer
hidden geometry. Use it only for shape/figure reconstruction tasks.

Coordinate convention used by the examples:
    X = image horizontal
    Z = image vertical
    camera sits on negative Y and looks toward +Y
    more-negative Y is visually in front
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import bpy
import bmesh
from mathutils import Matrix, Vector


ADDON_VERSION = "1.0.0"
TARGET_BLENDER = (5, 1, 0)
GENERATED_TAG = "abt_shape_generated"
EXPORT_TAG = "abt_shape_export"
ROLE_TAG = "abt_shape_role"


class ShapeToolError(RuntimeError):
    """Actionable error returned to the MCP boundary."""


@dataclass(frozen=True)
class MaterialSpec:
    name: str
    base_color: tuple[float, float, float, float]
    metallic: float = 0.0
    roughness: float = 0.5


def assert_blender_version() -> None:
    if tuple(bpy.app.version) < TARGET_BLENDER:
        raise ShapeToolError(
            f"Blender {bpy.app.version_string} is too old; expected 5.1.x or newer."
        )


def _safe_name(value: str, fallback: str = "Shape") -> str:
    cleaned = "".join(char if char.isalnum() or char in "_-" else "_" for char in str(value))
    cleaned = cleaned.strip("_")
    return (cleaned or fallback)[:63]


def _vec3(value: Sequence[float], name: str) -> tuple[float, float, float]:
    if len(value) != 3:
        raise ShapeToolError(f"{name} must contain exactly three numbers.")
    return tuple(float(component) for component in value)


def _rgba(value: Sequence[float]) -> tuple[float, float, float, float]:
    if len(value) not in {3, 4}:
        raise ShapeToolError("Color must contain RGB or RGBA values.")
    channels = [float(component) for component in value]
    if max(channels) > 1.0:
        channels = [component / 255.0 for component in channels]
    if len(channels) == 3:
        channels.append(1.0)
    return tuple(max(0.0, min(1.0, component)) for component in channels)  # type: ignore[return-value]


def _set_socket(node: bpy.types.Node, names: Sequence[str], value: Any) -> bool:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return True
    return False


def ensure_object_mode() -> None:
    active = bpy.context.object
    if active is not None and active.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def deselect_all() -> None:
    if bpy.context.view_layer.objects.active is not None:
        bpy.context.view_layer.objects.active = None
    for obj in bpy.context.selected_objects:
        obj.select_set(False)


def set_active(obj: bpy.types.Object, *, selected: bool = True) -> None:
    ensure_object_mode()
    deselect_all()
    obj.hide_set(False)
    obj.select_set(selected)
    bpy.context.view_layer.objects.active = obj


def ensure_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    safe = _safe_name(name, "ABT_Shape")
    collection = bpy.data.collections.get(safe)
    if collection is None:
        collection = bpy.data.collections.new(safe)
        (parent or bpy.context.scene.collection).children.link(collection)
    elif parent is not None and parent.children.get(collection.name) is None:
        parent.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if collection not in obj.users_collection:
        collection.objects.link(obj)
    for existing in list(obj.users_collection):
        if existing != collection:
            existing.objects.unlink(obj)


def tag_object(obj: bpy.types.Object, *, role: str, export: bool) -> None:
    obj[GENERATED_TAG] = True
    obj[ROLE_TAG] = role
    obj[EXPORT_TAG] = bool(export)


def apply_object_transform(
    obj: bpy.types.Object,
    *,
    location: bool = False,
    rotation: bool = False,
    scale: bool = True,
) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def shade_smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.update()


def apply_modifier(obj: bpy.types.Object, modifier_name: str) -> None:
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=modifier_name)


def convert_to_mesh(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        return obj
    set_active(obj)
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def create_principled_material(
    name: str,
    *,
    base_color: Sequence[float] = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5,
) -> bpy.types.Material:
    safe = _safe_name(name, "MAT_Shape")
    material = bpy.data.materials.get(safe) or bpy.data.materials.new(safe)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is None:
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        principled = nodes.new("ShaderNodeBsdfPrincipled")
        material.node_tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    _set_socket(principled, ["Base Color"], _rgba(base_color))
    _set_socket(principled, ["Metallic"], max(0.0, min(1.0, float(metallic))))
    _set_socket(principled, ["Roughness"], max(0.0, min(1.0, float(roughness))))
    material[GENERATED_TAG] = True
    return material


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    data = getattr(obj, "data", None)
    materials = getattr(data, "materials", None)
    if materials is None:
        return
    materials.clear()
    materials.append(material)


def _link_new_object(
    obj: bpy.types.Object, collection: bpy.types.Collection | None
) -> bpy.types.Object:
    (collection or bpy.context.scene.collection).objects.link(obj)
    return obj


def create_root(name: str, collection: bpy.types.Collection | None = None) -> bpy.types.Object:
    root = bpy.data.objects.new(_safe_name(name, "ShapeRoot"), None)
    _link_new_object(root, collection)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.4
    tag_object(root, role="asset_root", export=False)
    return root


def create_ellipsoid(
    *,
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    radius: float = 1.0,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    segments: int = 40,
    rings: int = 24,
    collection: bpy.types.Collection | None = None,
    material: bpy.types.Material | None = None,
    role: str = "source_part",
    export: bool = False,
) -> bpy.types.Object:
    ensure_object_mode()
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=max(12, min(int(segments), 128)),
        ring_count=max(6, min(int(rings), 64)),
        radius=max(0.001, float(radius)),
        location=_vec3(location, "location"),
        rotation=_vec3(rotation, "rotation"),
    )
    obj = bpy.context.object
    obj.name = _safe_name(name)
    obj.scale = _vec3(scale, "scale")
    apply_object_transform(obj, scale=True)
    if collection is not None:
        move_to_collection(obj, collection)
    shade_smooth(obj)
    if material is not None:
        assign_material(obj, material)
    tag_object(obj, role=role, export=export)
    return obj


def create_rounded_box(
    *,
    name: str,
    location: Sequence[float],
    dimensions: Sequence[float],
    radius: float,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
    segments: int = 6,
    collection: bpy.types.Collection | None = None,
    material: bpy.types.Material | None = None,
    role: str = "source_part",
    export: bool = False,
) -> bpy.types.Object:
    dims = _vec3(dimensions, "dimensions")
    if min(dims) <= 0:
        raise ShapeToolError("Rounded-box dimensions must be positive.")
    ensure_object_mode()
    bpy.ops.mesh.primitive_cube_add(
        location=_vec3(location, "location"), rotation=_vec3(rotation, "rotation")
    )
    obj = bpy.context.object
    obj.name = _safe_name(name)
    obj.scale = tuple(component / 2.0 for component in dims)
    apply_object_transform(obj, scale=True)
    bevel = obj.modifiers.new("ABT_Shape_Bevel", "BEVEL")
    bevel.width = max(0.0, min(float(radius), min(dims) * 0.499))
    bevel.segments = max(1, min(int(segments), 12))
    bevel.limit_method = "NONE"
    bevel.use_clamp_overlap = True
    if hasattr(bevel, "harden_normals"):
        bevel.harden_normals = True
    apply_modifier(obj, bevel.name)
    if collection is not None:
        move_to_collection(obj, collection)
    shade_smooth(obj)
    if material is not None:
        assign_material(obj, material)
    tag_object(obj, role=role, export=export)
    return obj


def create_bezier_tube(
    *,
    name: str,
    points: Sequence[Sequence[float]],
    radii: Sequence[float] | float,
    bevel_resolution: int = 5,
    curve_resolution: int = 16,
    collection: bpy.types.Collection | None = None,
    material: bpy.types.Material | None = None,
    add_round_endcaps: bool = True,
    role: str = "source_part",
    export: bool = False,
) -> list[bpy.types.Object]:
    if len(points) < 2:
        raise ShapeToolError("A tube needs at least two points.")
    coords = [Vector(_vec3(point, "point")) for point in points]
    if isinstance(radii, (int, float)):
        radius_values = [float(radii)] * len(coords)
    else:
        radius_values = [float(value) for value in radii]
    if len(radius_values) != len(coords) or min(radius_values) <= 0:
        raise ShapeToolError("Tube radii must be positive and match point count.")

    base_radius = max(radius_values)
    curve = bpy.data.curves.new(f"{_safe_name(name)}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = max(2, min(int(curve_resolution), 64))
    curve.bevel_depth = base_radius
    curve.bevel_resolution = max(0, min(int(bevel_resolution), 12))
    curve.fill_mode = "FULL"
    if hasattr(curve, "use_fill_caps"):
        curve.use_fill_caps = True

    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(coords) - 1)
    for point, coordinate, radius in zip(
        spline.bezier_points, coords, radius_values, strict=True
    ):
        point.co = coordinate
        point.radius = radius / base_radius
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"

    obj = bpy.data.objects.new(_safe_name(name), curve)
    _link_new_object(obj, collection)
    if material is not None:
        assign_material(obj, material)
    tag_object(obj, role=role, export=export)
    created = [obj]

    if add_round_endcaps:
        for suffix, coordinate, radius in (
            ("StartCap", coords[0], radius_values[0]),
            ("EndCap", coords[-1], radius_values[-1]),
        ):
            cap = create_ellipsoid(
                name=f"{name}_{suffix}",
                location=coordinate,
                scale=(radius, radius, radius),
                radius=1.0,
                segments=24,
                rings=16,
                collection=collection,
                material=material,
                role=role,
                export=export,
            )
            created.append(cap)
    return created


def duplicate_objects(
    objects: Sequence[bpy.types.Object],
    *,
    collection: bpy.types.Collection,
    suffix: str = "_WORK",
) -> list[bpy.types.Object]:
    duplicates: list[bpy.types.Object] = []
    for source in objects:
        duplicate = source.copy()
        if source.data is not None:
            duplicate.data = source.data.copy()
        duplicate.name = _safe_name(source.name + suffix)
        collection.objects.link(duplicate)
        duplicates.append(duplicate)
    return duplicates


def join_objects_as_mesh(
    objects: Sequence[bpy.types.Object], *, name: str
) -> bpy.types.Object:
    if not objects:
        raise ShapeToolError("No objects supplied for join.")
    meshes: list[bpy.types.Object] = []
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        converted = convert_to_mesh(obj)
        apply_object_transform(converted, location=False, rotation=False, scale=True)
        meshes.append(converted)
    deselect_all()
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = _safe_name(name)
    return joined


def voxel_union(
    source_objects: Sequence[bpy.types.Object],
    *,
    name: str,
    voxel_size: float = 0.045,
    adaptivity: float = 0.0,
    smooth_factor: float = 0.35,
    smooth_iterations: int = 3,
    output_collection: bpy.types.Collection | None = None,
    keep_sources: bool = True,
    material: bpy.types.Material | None = None,
    export: bool = True,
) -> bpy.types.Object:
    """Fuse overlapping primitives into one soft mesh while preserving sources."""
    assert_blender_version()
    if not source_objects:
        raise ShapeToolError("voxel_union requires at least one source object.")
    target_collection = output_collection or ensure_collection("ABT_SHAPE_OUTPUT")
    work_objects = (
        duplicate_objects(source_objects, collection=target_collection)
        if keep_sources
        else list(source_objects)
    )
    joined = join_objects_as_mesh(work_objects, name=name)
    move_to_collection(joined, target_collection)

    joined.data.remesh_voxel_size = max(0.002, float(voxel_size))
    joined.data.remesh_voxel_adaptivity = max(0.0, min(1.0, float(adaptivity)))
    if hasattr(joined.data, "use_remesh_fix_poles"):
        joined.data.use_remesh_fix_poles = True
    if hasattr(joined.data, "use_remesh_preserve_volume"):
        joined.data.use_remesh_preserve_volume = True
    set_active(joined)
    bpy.ops.object.voxel_remesh()

    if smooth_iterations > 0 and smooth_factor > 0:
        smooth = joined.modifiers.new("ABT_Shape_Smooth", "SMOOTH")
        smooth.factor = max(0.0, min(2.0, float(smooth_factor)))
        smooth.iterations = max(1, min(int(smooth_iterations), 20))
        apply_modifier(joined, smooth.name)
    shade_smooth(joined)
    if material is not None:
        assign_material(joined, material)
    tag_object(joined, role="merged_sculpt", export=export)

    if keep_sources:
        for source in source_objects:
            source.hide_render = True
            source.display_type = "WIRE"
            tag_object(source, role="source_part", export=False)
    return joined


def _parent_objects(objects: Iterable[bpy.types.Object], parent: bpy.types.Object) -> None:
    for obj in objects:
        matrix_world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = matrix_world


def create_cupping_hand(
    *,
    side: str,
    sphere_radius: float = 1.0,
    name: str | None = None,
    hand_material: bpy.types.Material | None = None,
    cuff_material: bpy.types.Material | None = None,
    source_collection: bpy.types.Collection | None = None,
    output_collection: bpy.types.Collection | None = None,
    merge: bool = True,
    voxel_size: float | None = None,
) -> dict:
    """Create a stylized left/right hand that cups a sphere from below/side.

    The hand is intentionally semantic rather than anatomical: palm, four rounded
    fingers, thumb, wrist, cuff. All source parts remain editable when merge=True.
    """
    normalized = side.strip().upper()
    if normalized not in {"LEFT", "RIGHT"}:
        raise ShapeToolError("side must be LEFT or RIGHT")
    sign = -1.0 if normalized == "LEFT" else 1.0
    radius = max(0.2, float(sphere_radius))
    hand_name = _safe_name(name or f"{normalized.title()}Hand")
    source_collection = source_collection or ensure_collection(f"ABT_SOURCE_{hand_name}")
    output_collection = output_collection or ensure_collection("ABT_SHAPE_OUTPUT")
    hand_material = hand_material or create_principled_material(
        "MAT_Hand", base_color=(0.95, 0.45, 0.62, 1.0), roughness=0.52
    )
    cuff_material = cuff_material or hand_material

    parts: list[bpy.types.Object] = []
    palm_center = (sign * radius * 1.05, -radius * 0.04, -radius * 0.22)
    palm = create_ellipsoid(
        name=f"{hand_name}_Palm",
        location=palm_center,
        scale=(radius * 0.42, radius * 0.28, radius * 0.50),
        rotation=(0.0, sign * math.radians(18), sign * math.radians(13)),
        collection=source_collection,
        material=hand_material,
    )
    parts.append(palm)

    # Four fingers form a readable fan. Their tips overlap the ball slightly so
    # voxel union does not leave the characteristic disconnected "tube fingers".
    finger_z = (0.34, 0.13, -0.08, -0.28)
    finger_lengths = (0.76, 0.82, 0.78, 0.68)
    for index, (z, length) in enumerate(zip(finger_z, finger_lengths, strict=True), start=1):
        outside_x = sign * radius * (0.68 + length)
        contact_x = sign * radius * (0.74 + 0.02 * index)
        points = [
            (outside_x, -radius * 0.02, radius * (z - 0.34)),
            (sign * radius * 1.03, -radius * 0.14, radius * (z - 0.05)),
            (contact_x, -radius * 0.30, radius * z),
        ]
        base = radius * (0.145 - 0.008 * index)
        tube_parts = create_bezier_tube(
            name=f"{hand_name}_Finger_{index}",
            points=points,
            radii=(base * 1.08, base, base * 0.88),
            bevel_resolution=5,
            curve_resolution=18,
            collection=source_collection,
            material=hand_material,
        )
        parts.extend(tube_parts)

    thumb_points = [
        (sign * radius * 1.12, -radius * 0.09, -radius * 0.42),
        (sign * radius * 0.91, -radius * 0.22, -radius * 0.16),
        (sign * radius * 0.69, -radius * 0.32, radius * 0.03),
    ]
    parts.extend(
        create_bezier_tube(
            name=f"{hand_name}_Thumb",
            points=thumb_points,
            radii=(radius * 0.18, radius * 0.165, radius * 0.14),
            bevel_resolution=5,
            curve_resolution=18,
            collection=source_collection,
            material=hand_material,
        )
    )

    wrist_points = [
        (sign * radius * 1.22, radius * 0.02, -radius * 0.50),
        (sign * radius * 1.42, radius * 0.08, -radius * 0.82),
        (sign * radius * 1.62, radius * 0.10, -radius * 1.13),
    ]
    parts.extend(
        create_bezier_tube(
            name=f"{hand_name}_Wrist",
            points=wrist_points,
            radii=(radius * 0.29, radius * 0.27, radius * 0.25),
            bevel_resolution=5,
            curve_resolution=14,
            collection=source_collection,
            material=hand_material,
        )
    )
    cuff = create_rounded_box(
        name=f"{hand_name}_Cuff",
        location=(sign * radius * 1.76, radius * 0.10, -radius * 1.28),
        dimensions=(radius * 0.62, radius * 0.60, radius * 0.48),
        radius=radius * 0.16,
        rotation=(0.0, sign * math.radians(20), sign * math.radians(31)),
        segments=6,
        collection=source_collection,
        material=cuff_material,
    )
    parts.append(cuff)

    if merge:
        merged = voxel_union(
            parts,
            name=f"{hand_name}_Merged",
            voxel_size=voxel_size or radius * 0.045,
            adaptivity=0.0,
            smooth_factor=0.28,
            smooth_iterations=2,
            output_collection=output_collection,
            keep_sources=True,
            material=hand_material,
            export=True,
        )
        return {
            "status": "ok",
            "side": normalized,
            "source_collection": source_collection.name,
            "source_parts": [obj.name for obj in parts],
            "merged_object": merged.name,
        }

    return {
        "status": "ok",
        "side": normalized,
        "source_collection": source_collection.name,
        "source_parts": [obj.name for obj in parts],
        "merged_object": None,
    }


def create_hand_sphere_icon(
    *,
    name: str = "HandSphere",
    sphere_radius: float = 1.0,
    sphere_color: Sequence[float] = (0.36, 0.64, 0.95, 1.0),
    hand_color: Sequence[float] = (0.95, 0.45, 0.62, 1.0),
    cuff_color: Sequence[float] | None = None,
    merge_hands: bool = True,
    voxel_size: float | None = None,
) -> dict:
    """Build a complete editable icon from primitives, curves, and voxel unions."""
    assert_blender_version()
    safe = _safe_name(name, "HandSphere")
    root_collection = ensure_collection(f"ABT_{safe}")
    source_parent = ensure_collection(f"ABT_{safe}_SOURCE", root_collection)
    output = ensure_collection(f"ABT_{safe}_OUTPUT", root_collection)
    root = create_root(f"{safe}_ROOT", output)

    sphere_material = create_principled_material(
        f"MAT_{safe}_Sphere", base_color=sphere_color, roughness=0.34
    )
    hand_material = create_principled_material(
        f"MAT_{safe}_Hand", base_color=hand_color, roughness=0.50
    )
    cuff_material = create_principled_material(
        f"MAT_{safe}_Cuff",
        base_color=cuff_color or hand_color,
        roughness=0.58,
    )
    sphere = create_ellipsoid(
        name=f"{safe}_Sphere",
        location=(0.0, 0.0, 0.05 * sphere_radius),
        scale=(sphere_radius, sphere_radius * 0.94, sphere_radius),
        radius=1.0,
        segments=64,
        rings=40,
        collection=output,
        material=sphere_material,
        role="final_part",
        export=True,
    )

    hand_results: list[dict] = []
    final_objects = [sphere]
    for side in ("LEFT", "RIGHT"):
        source = ensure_collection(f"ABT_{safe}_{side}_SOURCE", source_parent)
        result = create_cupping_hand(
            side=side,
            sphere_radius=sphere_radius,
            name=f"{safe}_{side.title()}",
            hand_material=hand_material,
            cuff_material=cuff_material,
            source_collection=source,
            output_collection=output,
            merge=merge_hands,
            voxel_size=voxel_size,
        )
        hand_results.append(result)
        if result["merged_object"]:
            final_objects.append(bpy.data.objects[result["merged_object"]])
        else:
            final_objects.extend(bpy.data.objects[name] for name in result["source_parts"])

    _parent_objects(final_objects, root)
    return {
        "status": "ok",
        "asset": safe,
        "root": root.name,
        "collection": root_collection.name,
        "source_collection": source_parent.name,
        "output_collection": output.name,
        "objects": [obj.name for obj in final_objects],
        "hands": hand_results,
        "note": "SOURCE collections preserve editable primitives; export only OUTPUT objects tagged abt_shape_export=true.",
    }


def _top_level_ancestor(index: int, hierarchy: Sequence[Mapping[str, Any]]) -> int:
    parent = int(hierarchy[index]["parent"])
    current = index
    while parent >= 0:
        current = parent
        parent = int(hierarchy[current]["parent"])
    return current


def import_contour_json(
    *,
    contour_json: str | Path,
    name: str = "ContourRelief",
    thickness: float = 0.18,
    bevel: float = 0.025,
    bevel_resolution: int = 4,
    scale: float = 4.0,
    location: Sequence[float] = (0.0, 0.0, 0.0),
    collection_name: str = "ABT_CONTOURS",
    material: bpy.types.Material | None = None,
    convert_mesh: bool = False,
    export: bool = True,
) -> dict:
    """Import hole-preserving contour JSON produced by reference_preprocess.py."""
    path = Path(contour_json)
    if not path.is_file():
        raise ShapeToolError(f"Contour JSON not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "ai-blender-contours/v1":
        raise ShapeToolError("Unsupported contour JSON schema.")
    loops = payload.get("loops")
    if not isinstance(loops, list) or not loops:
        raise ShapeToolError("Contour JSON contains no loops.")

    location_vec = Vector(_vec3(location, "location"))
    collection = ensure_collection(collection_name)
    groups: dict[int, list[dict]] = {}
    for index, loop in enumerate(loops):
        root = _top_level_ancestor(index, loops)
        groups.setdefault(root, []).append(loop)

    objects: list[bpy.types.Object] = []
    for group_index, group_loops in enumerate(groups.values(), start=1):
        curve = bpy.data.curves.new(f"{_safe_name(name)}_{group_index}_Curve", type="CURVE")
        curve.dimensions = "2D"
        curve.resolution_u = 1
        curve.fill_mode = "BOTH"
        curve.extrude = max(0.0, float(thickness)) * 0.5
        curve.bevel_depth = max(0.0, float(bevel))
        curve.bevel_resolution = max(0, min(int(bevel_resolution), 12))
        if hasattr(curve, "use_fill_caps"):
            curve.use_fill_caps = True

        for loop in group_loops:
            points = loop.get("points_world")
            if not isinstance(points, list) or len(points) < 3:
                continue
            spline = curve.splines.new("POLY")
            spline.points.add(len(points) - 1)
            for point, coordinate in zip(spline.points, points, strict=True):
                point.co = (
                    float(coordinate[0]) * float(scale),
                    float(coordinate[1]) * float(scale),
                    0.0,
                    1.0,
                )
            spline.use_cyclic_u = True

        obj = bpy.data.objects.new(f"{_safe_name(name)}_{group_index}", curve)
        collection.objects.link(obj)
        # Local curve XY becomes world XZ; local +Z thickness points toward -Y.
        obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        obj.location = location_vec
        if material is not None:
            assign_material(obj, material)
        tag_object(obj, role="contour_relief", export=export)
        if convert_mesh:
            obj = convert_to_mesh(obj)
            shade_smooth(obj)
            tag_object(obj, role="contour_relief", export=export)
        objects.append(obj)

    if not objects:
        raise ShapeToolError("No valid contour objects were created.")
    return {
        "status": "ok",
        "source": str(path.resolve()),
        "objects": [obj.name for obj in objects],
        "reconstruction_iou": payload.get("extraction", {}).get("reconstruction_iou"),
        "hole_count": payload.get("extraction", {}).get("hole_count"),
    }


def import_layer_stack(config_json: str | Path) -> dict:
    """Import multiple contour masks with explicit front/back depth ordering."""
    path = Path(config_json)
    if not path.is_file():
        raise ShapeToolError(f"Layer config not found: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema") != "ai-blender-layer-stack/v1":
        raise ShapeToolError("Unsupported layer-stack schema.")
    layers = config.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ShapeToolError("Layer stack contains no layers.")

    created: list[dict] = []
    for layer in layers:
        material_spec = layer.get("material", {})
        material = create_principled_material(
            material_spec.get("name", f"MAT_{layer['name']}"),
            base_color=material_spec.get("base_color", (0.8, 0.8, 0.8, 1.0)),
            metallic=material_spec.get("metallic", 0.0),
            roughness=material_spec.get("roughness", 0.5),
        )
        contour_path = Path(layer["contour_json"])
        if not contour_path.is_absolute():
            contour_path = (path.parent / contour_path).resolve()
        created.append(
            import_contour_json(
                contour_json=contour_path,
                name=layer["name"],
                thickness=layer.get("thickness", 0.18),
                bevel=layer.get("bevel", 0.025),
                bevel_resolution=layer.get("bevel_resolution", 4),
                scale=config.get("world_height", 4.0),
                location=(
                    layer.get("offset_x", 0.0),
                    layer.get("depth_y", 0.0),
                    layer.get("offset_z", 0.0),
                ),
                collection_name=config.get("collection", "ABT_LAYER_STACK"),
                material=material,
                convert_mesh=layer.get("convert_mesh", False),
                export=layer.get("export", True),
            )
        )
    return {"status": "ok", "config": str(path.resolve()), "layers": created}


def setup_reference_camera(
    *,
    width: int,
    height: int,
    world_height: float = 4.0,
    distance: float = 10.0,
    name: str = "CAM_REFERENCE",
    target: Sequence[float] = (0.0, 0.0, 0.0),
) -> dict:
    width = max(16, int(width))
    height = max(16, int(height))
    world_height = max(0.01, float(world_height))
    target_vec = Vector(_vec3(target, "target"))
    location = target_vec + Vector((0.0, -abs(float(distance)), 0.0))
    camera_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None or camera.type != "CAMERA":
        camera = bpy.data.objects.new(name, camera_data)
        bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (target_vec - location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    # Blender's orthographic scale is the horizontal camera width. Convert the
    # requested vertical world height using the render aspect ratio.
    world_width = world_height * width / float(height)
    camera.data.ortho_scale = world_width
    camera.data.lens = 70.0
    bpy.context.scene.camera = camera

    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    tag_object(camera, role="reference_camera", export=False)
    return {
        "status": "ok",
        "camera": camera.name,
        "resolution": [width, height],
        "ortho_scale": world_width,
        "world_height": world_height,
        "world_width": world_width,
    }


def _resolve_objects(names: Sequence[str] | None) -> list[bpy.types.Object]:
    if names is None:
        return [
            obj
            for obj in bpy.context.scene.objects
            if bool(obj.get(EXPORT_TAG, False)) and obj.type not in {"CAMERA", "LIGHT", "EMPTY"}
        ]
    objects: list[bpy.types.Object] = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ShapeToolError(f"Object not found: {name}")
        objects.append(obj)
    return objects


def _create_mask_material() -> bpy.types.Material:
    name = "ABT_MASK_OVERRIDE"
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


@contextmanager
def _temporary_render_isolation(targets: Sequence[bpy.types.Object]):
    scene = bpy.context.scene
    hide_state = {obj.name: bool(obj.hide_render) for obj in scene.objects}
    old_world = scene.world
    old_override = bpy.context.view_layer.material_override
    old_engine = scene.render.engine
    old_transparent = scene.render.film_transparent
    old_filepath = scene.render.filepath
    old_color_mode = scene.render.image_settings.color_mode
    old_file_format = scene.render.image_settings.file_format
    old_cycles_samples = getattr(getattr(scene, "cycles", None), "samples", None)
    old_cycles_denoising = getattr(getattr(scene, "cycles", None), "use_denoising", None)
    target_names = {obj.name for obj in targets}

    temp_world = bpy.data.worlds.new("ABT_MASK_WORLD_TEMP")
    temp_world.use_nodes = True
    background = temp_world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        background.inputs["Strength"].default_value = 0.0
    try:
        for obj in scene.objects:
            if obj.type == "CAMERA":
                obj.hide_render = False
            else:
                obj.hide_render = obj.name not in target_names
        scene.world = temp_world
        bpy.context.view_layer.material_override = _create_mask_material()
        candidates = (
            ("CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH")
            if bpy.app.background
            else ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH")
        )
        engine_error = None
        for candidate in candidates:
            try:
                scene.render.engine = candidate
                break
            except (TypeError, ValueError) as exc:
                engine_error = exc
        else:
            raise ShapeToolError(f"No supported render engine found: {engine_error}")
        if scene.render.engine == "CYCLES" and hasattr(scene, "cycles"):
            scene.cycles.samples = 1
            scene.cycles.use_denoising = False
        scene.render.film_transparent = False
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        yield
    finally:
        for name, hidden in hide_state.items():
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render = hidden
        scene.world = old_world
        bpy.context.view_layer.material_override = old_override
        scene.render.engine = old_engine
        scene.render.film_transparent = old_transparent
        scene.render.filepath = old_filepath
        scene.render.image_settings.color_mode = old_color_mode
        scene.render.image_settings.file_format = old_file_format
        if old_cycles_samples is not None and hasattr(scene, "cycles"):
            scene.cycles.samples = old_cycles_samples
        if old_cycles_denoising is not None and hasattr(scene, "cycles"):
            scene.cycles.use_denoising = old_cycles_denoising
        bpy.data.worlds.remove(temp_world)


def render_silhouette_mask(
    *,
    filepath: str | Path,
    object_names: Sequence[str] | None = None,
    width: int | None = None,
    height: int | None = None,
) -> dict:
    targets = _resolve_objects(object_names)
    if not targets:
        raise ShapeToolError("No target objects for silhouette render.")
    scene = bpy.context.scene
    if scene.camera is None:
        raise ShapeToolError("Reference camera is missing. Run setup_reference_camera first.")
    old_resolution = (
        scene.render.resolution_x,
        scene.render.resolution_y,
        scene.render.resolution_percentage,
    )
    if width is not None:
        scene.render.resolution_x = max(16, int(width))
    if height is not None:
        scene.render.resolution_y = max(16, int(height))
    scene.render.resolution_percentage = 100
    render_resolution = [scene.render.resolution_x, scene.render.resolution_y]
    destination = Path(filepath).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        with _temporary_render_isolation(targets):
            scene.render.filepath = str(destination)
            bpy.ops.render.render(write_still=True)
    finally:
        (
            scene.render.resolution_x,
            scene.render.resolution_y,
            scene.render.resolution_percentage,
        ) = old_resolution
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ShapeToolError(f"Silhouette render was not created: {destination}")
    return {
        "status": "ok",
        "path": str(destination),
        "resolution": render_resolution,
        "objects": [obj.name for obj in targets],
    }


def apply_reference_fit(
    *,
    report_json: str | Path,
    root_object: str,
    mode: str = "UNIFORM",
    confirm: bool = False,
) -> dict:
    """Apply report translation/scale only after explicit confirmation."""
    if not confirm:
        raise ShapeToolError("apply_reference_fit requires confirm=True")
    path = Path(report_json)
    if not path.is_file():
        raise ShapeToolError(f"Silhouette report not found: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    suggestion = report.get("blender_world_suggestion")
    if not isinstance(suggestion, dict):
        raise ShapeToolError("Report has no blender_world_suggestion.")
    root = bpy.data.objects.get(root_object)
    if root is None:
        raise ShapeToolError(f"Root object not found: {root_object}")

    root.location.x += float(suggestion["translate_x"])
    root.location.z += float(suggestion["translate_z"])
    sx = float(suggestion["scale_x"])
    sz = float(suggestion["scale_z"])
    normalized = mode.strip().upper()
    if normalized == "UNIFORM":
        scale = math.sqrt(max(sx * sz, 1e-8))
        root.scale *= scale
    elif normalized == "SCREEN_NONUNIFORM":
        root.scale.x *= sx
        root.scale.z *= sz
        root.scale.y *= math.sqrt(max(sx * sz, 1e-8))
    else:
        raise ShapeToolError("mode must be UNIFORM or SCREEN_NONUNIFORM")
    return {
        "status": "ok",
        "root": root.name,
        "mode": normalized,
        "location": list(root.location),
        "scale": list(root.scale),
    }


def validate_shape_asset(
    *,
    object_names: Sequence[str] | None = None,
    max_triangles: int = 80_000,
    require_closed: bool = True,
) -> dict:
    objects = _resolve_objects(object_names)
    errors: list[str] = []
    warnings: list[str] = []
    reports: list[dict] = []
    total_triangles = 0

    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != "MESH":
            warnings.append(f"{obj.name}: export object is {obj.type}, not MESH")
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            triangles = sum(max(1, len(poly.vertices) - 2) for poly in mesh.polygons)
            total_triangles += triangles
            bm = bmesh.new()
            bm.from_mesh(mesh)
            boundary_edges = sum(1 for edge in bm.edges if len(edge.link_faces) != 2)
            degenerate_faces = sum(1 for face in bm.faces if face.calc_area() <= 1e-12)
            bm.free()
            if require_closed and boundary_edges:
                errors.append(f"{obj.name}: {boundary_edges} non-manifold/boundary edges")
            if degenerate_faces:
                warnings.append(f"{obj.name}: {degenerate_faces} zero-area faces")
            if not obj.data.materials:
                warnings.append(f"{obj.name}: no material")
            reports.append(
                {
                    "object": obj.name,
                    "triangles": triangles,
                    "boundary_edges": boundary_edges,
                    "degenerate_faces": degenerate_faces,
                    "dimensions": [float(value) for value in obj.dimensions],
                }
            )
        finally:
            evaluated.to_mesh_clear()

    if total_triangles > int(max_triangles):
        errors.append(f"Triangle budget exceeded: {total_triangles} > {int(max_triangles)}")
    elif total_triangles > int(max_triangles) * 0.8:
        warnings.append(f"Triangle budget above 80%: {total_triangles}/{int(max_triangles)}")
    return {
        "status": "fail" if errors else ("warn" if warnings else "pass"),
        "summary": {
            "objects": len(objects),
            "triangles": total_triangles,
            "max_triangles": int(max_triangles),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
        "objects": reports,
    }


def export_glb(
    *,
    filepath: str | Path,
    object_names: Sequence[str] | None = None,
) -> dict:
    objects = _resolve_objects(object_names)
    if not objects:
        raise ShapeToolError("No export objects selected.")
    destination = Path(filepath).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    old_selected = list(bpy.context.selected_objects)
    old_active = bpy.context.view_layer.objects.active
    old_hidden = {obj.name: bool(obj.hide_get()) for obj in objects}
    try:
        deselect_all()
        for obj in objects:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.export_scene.gltf(
            filepath=str(destination),
            export_format="GLB",
            use_active_scene=True,
            use_selection=True,
            export_apply=True,
            export_materials="EXPORT",
            export_yup=True,
        )
    finally:
        deselect_all()
        for obj in objects:
            if bpy.data.objects.get(obj.name) is not None:
                obj.hide_set(old_hidden[obj.name])
        for obj in old_selected:
            if bpy.data.objects.get(obj.name) is not None and not obj.hide_get():
                obj.select_set(True)
        if old_active is not None and bpy.data.objects.get(old_active.name) is not None:
            bpy.context.view_layer.objects.active = old_active
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ShapeToolError(f"GLB export failed: {destination}")
    return {
        "status": "ok",
        "path": str(destination),
        "bytes": destination.stat().st_size,
        "objects": [obj.name for obj in objects],
    }


def scene_report() -> dict:
    generated = [obj for obj in bpy.context.scene.objects if obj.get(GENERATED_TAG)]
    export_objects = [obj for obj in generated if obj.get(EXPORT_TAG)]
    return {
        "status": "ok",
        "addon_version": ADDON_VERSION,
        "blender": bpy.app.version_string,
        "generated_objects": [obj.name for obj in generated],
        "export_objects": [obj.name for obj in export_objects],
        "source_objects": [
            obj.name for obj in generated if obj.get(ROLE_TAG) == "source_part"
        ],
        "camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
    }


assert_blender_version()
