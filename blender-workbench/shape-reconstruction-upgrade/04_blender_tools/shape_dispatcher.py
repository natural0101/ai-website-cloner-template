"""Allow-listed JSON dispatcher for shape_tools.py.

Designed for MCP bridges that only expose "execute Python in Blender". The MCP
server should call ``dispatch_json`` with a small JSON payload instead of asking
the model to generate a large monolithic bpy script.
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any, Callable, Mapping

import bpy

import shape_tools as st


DISPATCHER_VERSION = "1.0.0"


class ShapeDispatchError(RuntimeError):
    pass


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ShapeDispatchError(f"{name} must be a JSON object")
    return dict(value)


def _material(spec: Any, fallback_name: str):
    if spec is None:
        return None
    data = _mapping(spec, "material")
    return st.create_principled_material(
        data.get("name", fallback_name),
        base_color=data.get("base_color", (0.8, 0.8, 0.8, 1.0)),
        metallic=data.get("metallic", 0.0),
        roughness=data.get("roughness", 0.5),
    )


def _collection(name: str | None):
    return st.ensure_collection(name) if name else None


def _create_part(arguments: dict[str, Any]) -> dict[str, Any]:
    kind = str(arguments.pop("kind", "")).strip().upper()
    name = str(arguments.pop("name", "ShapePart"))
    collection = _collection(arguments.pop("collection_name", None))
    material = _material(arguments.pop("material", None), f"MAT_{name}")
    export = bool(arguments.pop("export", False))

    if kind == "ELLIPSOID":
        obj = st.create_ellipsoid(
            name=name,
            location=arguments.pop("location", (0.0, 0.0, 0.0)),
            scale=arguments.pop("scale", (1.0, 1.0, 1.0)),
            radius=arguments.pop("radius", 1.0),
            rotation=arguments.pop("rotation", (0.0, 0.0, 0.0)),
            segments=arguments.pop("segments", 40),
            rings=arguments.pop("rings", 24),
            collection=collection,
            material=material,
            export=export,
        )
        created = [obj.name]
    elif kind == "ROUNDED_BOX":
        obj = st.create_rounded_box(
            name=name,
            location=arguments.pop("location", (0.0, 0.0, 0.0)),
            dimensions=arguments.pop("dimensions", (1.0, 1.0, 1.0)),
            radius=arguments.pop("radius", 0.15),
            rotation=arguments.pop("rotation", (0.0, 0.0, 0.0)),
            segments=arguments.pop("segments", 6),
            collection=collection,
            material=material,
            export=export,
        )
        created = [obj.name]
    elif kind == "TUBE":
        objects = st.create_bezier_tube(
            name=name,
            points=arguments.pop("points"),
            radii=arguments.pop("radii", 0.1),
            bevel_resolution=arguments.pop("bevel_resolution", 5),
            curve_resolution=arguments.pop("curve_resolution", 16),
            collection=collection,
            material=material,
            add_round_endcaps=arguments.pop("add_round_endcaps", True),
            export=export,
        )
        created = [obj.name for obj in objects]
    else:
        raise ShapeDispatchError("kind must be ELLIPSOID, ROUNDED_BOX, or TUBE")

    if arguments:
        raise ShapeDispatchError(f"Unsupported create_part arguments: {sorted(arguments)}")
    return {"status": "ok", "kind": kind, "objects": created}


def _voxel_union(arguments: dict[str, Any]) -> dict[str, Any]:
    names = arguments.pop("source_names", None)
    if not isinstance(names, list) or not names:
        raise ShapeDispatchError("source_names must be a non-empty array")
    objects = []
    for name in names:
        obj = bpy.data.objects.get(str(name))
        if obj is None:
            raise ShapeDispatchError(f"Object not found: {name}")
        objects.append(obj)
    material = _material(arguments.pop("material", None), "MAT_VoxelUnion")
    output_collection = _collection(arguments.pop("output_collection", None))
    obj = st.voxel_union(
        objects,
        name=arguments.pop("name", "MergedShape"),
        voxel_size=arguments.pop("voxel_size", 0.045),
        adaptivity=arguments.pop("adaptivity", 0.0),
        smooth_factor=arguments.pop("smooth_factor", 0.35),
        smooth_iterations=arguments.pop("smooth_iterations", 3),
        output_collection=output_collection,
        keep_sources=True,
        material=material,
        export=arguments.pop("export", True),
    )
    if arguments:
        raise ShapeDispatchError(f"Unsupported voxel_union arguments: {sorted(arguments)}")
    return {"status": "ok", "object": obj.name, "sources_preserved": True}


def _create_hand(arguments: dict[str, Any]) -> dict[str, Any]:
    return st.create_cupping_hand(
        side=arguments.pop("side"),
        sphere_radius=arguments.pop("sphere_radius", 1.0),
        name=arguments.pop("name", None),
        merge=arguments.pop("merge", True),
        voxel_size=arguments.pop("voxel_size", None),
    )


def _call(function: Callable[..., dict[str, Any]], arguments: dict[str, Any]) -> dict[str, Any]:
    kwargs = dict(arguments)
    arguments.clear()
    return function(**kwargs)


_ACTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "shape.scene_report": lambda a: st.scene_report(),
    "shape.create_part": _create_part,
    "shape.voxel_union": _voxel_union,
    "shape.create_cupping_hand": _create_hand,
    "shape.create_hand_sphere": lambda a: _call(st.create_hand_sphere_icon, a),
    "shape.import_contours": lambda a: _call(st.import_contour_json, a),
    "shape.import_layer_stack": lambda a: _call(st.import_layer_stack, a),
    "shape.setup_reference_camera": lambda a: _call(st.setup_reference_camera, a),
    "shape.render_silhouette": lambda a: _call(st.render_silhouette_mask, a),
    "shape.apply_reference_fit": lambda a: _call(st.apply_reference_fit, a),
    "shape.validate": lambda a: _call(st.validate_shape_asset, a),
    "shape.export_glb": lambda a: _call(st.export_glb, a),
}


def dispatch(payload: str | Mapping[str, Any]) -> dict[str, Any]:
    try:
        request = json.loads(payload) if isinstance(payload, str) else dict(payload)
        action = str(request.get("action", ""))
        arguments = _mapping(request.get("arguments", {}), "arguments")
        handler = _ACTIONS.get(action)
        if handler is None:
            raise ShapeDispatchError(
                f"Unknown action: {action!r}. Allowed: {sorted(_ACTIONS)}"
            )
        result = handler(arguments)
        if arguments:
            raise ShapeDispatchError(f"Unused arguments for {action}: {sorted(arguments)}")
        return {
            "ok": True,
            "action": action,
            "dispatcher_version": DISPATCHER_VERSION,
            "result": result,
        }
    except Exception as exc:
        return {
            "ok": False,
            "action": request.get("action") if "request" in locals() else None,
            "dispatcher_version": DISPATCHER_VERSION,
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback_tail": traceback.format_exc().splitlines()[-8:],
        }


def dispatch_json(payload: str | Mapping[str, Any]) -> str:
    return json.dumps(dispatch(payload), ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    print(dispatch_json({"action": "shape.scene_report", "arguments": {}}))
