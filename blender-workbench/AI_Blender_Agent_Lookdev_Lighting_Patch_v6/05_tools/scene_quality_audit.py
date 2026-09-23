"""Read-only scene QA for Blender 5.x production lookdev.

Execute in Blender, then call:
    report = run_audit("/path/scene_quality_report.json")
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import pstdev
from typing import Any

import bpy


def _socket_value(node: bpy.types.Node, names: tuple[str, ...], default=None):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            value = socket.default_value
            if hasattr(value, "__len__") and not isinstance(value, str):
                return [float(v) for v in value]
            try:
                return float(value)
            except Exception:
                return value
    return default


def _socket_linked(node: bpy.types.Node, names: tuple[str, ...]) -> bool:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return bool(socket.is_linked)
    return False


def _principled(material: bpy.types.Material):
    if not material.use_nodes or material.node_tree is None:
        return None
    return next((n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)


def _material_record(mat: bpy.types.Material) -> dict[str, Any]:
    node = _principled(mat)
    record: dict[str, Any] = {
        "name": mat.name,
        "use_nodes": bool(mat.use_nodes),
        "principled": node is not None,
        "warnings": [],
    }
    if node is None:
        record["warnings"].append("No Principled BSDF: verify GLB compatibility or bake material.")
        return record

    base = _socket_value(node, ("Base Color",), [0.8, 0.8, 0.8, 1.0])
    metallic = _socket_value(node, ("Metallic",), 0.0)
    roughness = _socket_value(node, ("Roughness",), 0.5)
    emission_strength = _socket_value(node, ("Emission Strength",), 0.0)
    transmission = _socket_value(node, ("Transmission Weight", "Transmission"), 0.0)
    record.update(
        {
            "base_color": base,
            "metallic": metallic,
            "roughness": roughness,
            "roughness_linked": _socket_linked(node, ("Roughness",)),
            "base_color_linked": _socket_linked(node, ("Base Color",)),
            "emission_strength": emission_strength,
            "emission_linked": _socket_linked(node, ("Emission Color", "Emission")),
            "transmission": transmission,
        }
    )

    rgb = base[:3] if isinstance(base, list) else [0.8, 0.8, 0.8]
    if max(rgb) > 0.98 and min(rgb) > 0.98:
        record["warnings"].append("Near-pure white base color leaves little highlight headroom.")
    if max(rgb) < 0.01:
        record["warnings"].append("Near-absolute black base color may crush surface detail.")
    if isinstance(metallic, (int, float)) and 0.05 < metallic < 0.95:
        record["warnings"].append("Intermediate metallic value: verify mixed/weathered material intent.")
    if isinstance(roughness, (int, float)) and roughness < 0.03:
        record["warnings"].append("Extremely low roughness: requires strong environment/reflection control.")
    if isinstance(emission_strength, (int, float)) and emission_strength > 10.0:
        record["warnings"].append("High emission: separate visible emitter from illumination and check clipping.")
    if isinstance(transmission, (int, float)) and transmission > 0.0:
        record["warnings"].append("Transmission material: verify target GLB viewer extension support.")
    return record


def _mesh_record(obj: bpy.types.Object) -> dict[str, Any]:
    data = obj.data
    polygons = len(data.polygons)
    triangles = sum(max(1, len(poly.vertices) - 2) for poly in data.polygons)
    bevel_mods = [m.name for m in obj.modifiers if m.type == "BEVEL"]
    smooth_ratio = (
        sum(1 for p in data.polygons if p.use_smooth) / polygons if polygons else 0.0
    )
    scale = [float(v) for v in obj.scale]
    max_dim = max((float(v) for v in obj.dimensions), default=0.0)
    warnings: list[str] = []
    if any(abs(v - 1.0) > 0.01 for v in scale):
        warnings.append("Object scale is not applied; bevel/normal/export behavior may differ.")
    is_hard_surface = bool(obj.get("lookdev_hard_surface", False))
    if is_hard_surface and polygons > 12 and max_dim > 0.05 and not bevel_mods:
        warnings.append("Tagged hard-surface object has no Bevel modifier.")
    if smooth_ratio == 0.0 and polygons > 24:
        warnings.append("All faces flat-shaded; check for unwanted low-poly faceting.")
    if triangles > 100000:
        warnings.append("High triangle count for one web asset; review LOD/decimation after approval.")
    return {
        "name": obj.name,
        "polygons": polygons,
        "triangle_estimate": triangles,
        "dimensions": [float(v) for v in obj.dimensions],
        "scale": scale,
        "bevel_modifiers": bevel_mods,
        "lookdev_hard_surface": is_hard_surface,
        "smooth_face_ratio": smooth_ratio,
        "material_slots": [slot.material.name if slot.material else None for slot in obj.material_slots],
        "warnings": warnings,
    }


def run_audit(filepath: str | Path | None = None) -> dict[str, Any]:
    scene = bpy.context.scene
    meshes = [_mesh_record(o) for o in scene.objects if o.type == "MESH" and not o.hide_render]
    materials = [_material_record(m) for m in bpy.data.materials]
    lights = []
    for obj in scene.objects:
        if obj.type != "LIGHT":
            continue
        data = obj.data
        lights.append(
            {
                "name": obj.name,
                "type": data.type,
                "energy": float(getattr(data, "energy", 0.0)),
                "color": [float(v) for v in data.color],
                "size": float(getattr(data, "size", 0.0)) if hasattr(data, "size") else None,
                "shadow_soft_size": float(getattr(data, "shadow_soft_size", 0.0)) if hasattr(data, "shadow_soft_size") else None,
            }
        )

    warnings: list[dict[str, str]] = []
    if scene.camera is None:
        warnings.append({"severity": "critical", "message": "No active camera."})
    world_has_nodes = bool(scene.world and scene.world.use_nodes and scene.world.node_tree)
    if not lights and not world_has_nodes:
        warnings.append({"severity": "critical", "message": "No light objects and no node-based World lighting."})
    elif not lights:
        warnings.append({"severity": "warning", "message": "No light objects; environment-only lighting may be intentional but requires reflection/exposure review."})
    if scene.view_settings.view_transform not in {"AgX", "Khronos PBR Neutral"}:
        warnings.append({"severity": "warning", "message": f"View transform is {scene.view_settings.view_transform!r}; verify highlight handling."})

    roughness_values = [
        m.get("roughness")
        for m in materials
        if isinstance(m.get("roughness"), (int, float)) and not m.get("roughness_linked", False)
    ]
    if len(roughness_values) >= 4 and pstdev(roughness_values) < 0.06:
        warnings.append({"severity": "warning", "message": "Material roughness values are nearly uniform; scene may look rubbery."})

    emission_materials = [m for m in materials if isinstance(m.get("emission_strength"), (int, float)) and m["emission_strength"] > 0.0]
    if emission_materials and not lights:
        warnings.append({"severity": "warning", "message": "Emission exists without separate light objects; verify that environment/baking intentionally provides illumination."})

    for mesh in meshes:
        for message in mesh["warnings"]:
            warnings.append({"severity": "warning", "object": mesh["name"], "message": message})
    for mat in materials:
        for message in mat["warnings"]:
            warnings.append({"severity": "warning", "material": mat["name"], "message": message})

    triangle_total = sum(m["triangle_estimate"] for m in meshes)
    critical_count = sum(1 for w in warnings if w["severity"] == "critical")
    warning_count = sum(1 for w in warnings if w["severity"] == "warning")
    score = max(0, 100 - critical_count * 25 - min(warning_count, 20) * 3)

    report: dict[str, Any] = {
        "blender_version": bpy.app.version_string,
        "render": {
            "engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "view_transform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": float(scene.view_settings.exposure),
            "film_transparent": bool(scene.render.film_transparent),
        },
        "counts": {
            "objects": len(scene.objects),
            "meshes": len(meshes),
            "materials": len(materials),
            "lights": len(lights),
            "triangle_estimate": triangle_total,
        },
        "lights": lights,
        "materials": materials,
        "meshes": meshes,
        "warnings": warnings,
        "score": score,
        "status": "PASS" if critical_count == 0 and warning_count <= 4 else "REVIEW_REQUIRED",
        "note": "Score is a triage aid, not an artistic quality metric.",
    }

    if filepath is not None:
        path = Path(filepath).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_audit(), ensure_ascii=False, indent=2))
