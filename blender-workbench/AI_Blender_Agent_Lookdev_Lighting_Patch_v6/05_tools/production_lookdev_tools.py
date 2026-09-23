"""Non-destructive Blender 5.x helpers for production lookdev and lighting.

Usage from Blender Text Editor or MCP:
    exec(open(r".../production_lookdev_tools.py", encoding="utf-8").read())

The module does not delete user objects. Generated lights are tagged and can be
removed with remove_generated_lookdev_objects(). Runtime API differences are
handled with feature checks where practical.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Vector

TAG = "lookdev_v6_generated"

MATERIAL_PRESETS = {
    "painted_metal": {
        "base_color": (0.32, 0.34, 0.38, 1.0),
        "metallic": 0.0,
        "roughness": 0.36,
        "coat_weight": 0.22,
        "coat_roughness": 0.18,
    },
    "bare_aluminium": {
        "base_color": (0.91, 0.91, 0.89, 1.0),
        "metallic": 1.0,
        "roughness": 0.32,
        "coat_weight": 0.0,
    },
    "rubber": {
        "base_color": (0.035, 0.035, 0.035, 1.0),
        "metallic": 0.0,
        "roughness": 0.78,
        "coat_weight": 0.0,
        "specular_ior_level": 0.28,
    },
    "plastic": {
        "base_color": (0.18, 0.22, 0.28, 1.0),
        "metallic": 0.0,
        "roughness": 0.48,
        "coat_weight": 0.06,
    },
    "concrete": {
        "base_color": (0.42, 0.41, 0.39, 1.0),
        "metallic": 0.0,
        "roughness": 0.88,
        "coat_weight": 0.0,
        "specular_ior_level": 0.26,
    },
    "glass": {
        "base_color": (0.20, 0.34, 0.42, 1.0),
        "metallic": 0.0,
        "roughness": 0.08,
        "transmission_weight": 1.0,
        "ior": 1.46,
    },
    "neutral_clay": {
        "base_color": (0.42, 0.42, 0.42, 1.0),
        "metallic": 0.0,
        "roughness": 0.62,
        "coat_weight": 0.0,
    },
}


def _enum_ids(owner, prop_name: str) -> set[str]:
    try:
        return {item.identifier for item in owner.bl_rna.properties[prop_name].enum_items}
    except Exception:
        return set()


def _set_enum_if_available(owner, prop_name: str, preferred: Sequence[str]) -> str | None:
    available = _enum_ids(owner, prop_name)
    for value in preferred:
        if not available or value in available:
            try:
                setattr(owner, prop_name, value)
                return value
            except Exception:
                continue
    return None


def _set_socket(node: bpy.types.Node, names: Iterable[str], value) -> bool:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return True
    return False


def _principled(material: bpy.types.Material) -> bpy.types.Node:
    material.use_nodes = True
    nodes = material.node_tree.nodes
    node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if node is None:
        node = nodes.new("ShaderNodeBsdfPrincipled")
    output = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    if output is None:
        output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = node.outputs.get("BSDF")
    surface = output.inputs.get("Surface")
    if bsdf is None or surface is None:
        raise RuntimeError("Principled BSDF or Material Output socket is unavailable")
    if not surface.is_linked:
        material.node_tree.links.new(bsdf, surface)
    return node


def _look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    if direction.length > 1e-8:
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _resolve_objects(names: Sequence[str] | None = None) -> list[bpy.types.Object]:
    if names:
        return [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    return [
        obj
        for obj in bpy.context.scene.objects
        if obj.type not in {"CAMERA", "LIGHT", "EMPTY"}
        and not bool(obj.get(TAG, False))
    ]


def _world_bounds(objects: Sequence[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in objects:
        try:
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        except Exception:
            points.append(obj.location.copy())
    if not points:
        return Vector((-1, -1, -1)), Vector((1, 1, 1))
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def save_checkpoint(filepath: str | Path) -> str:
    path = Path(filepath).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
    return str(path)


def set_production_color_management(
    *,
    exposure: float = 0.0,
    look_preference: Sequence[str] = (
        "Medium High Contrast",
        "AgX - Medium High Contrast",
        "Medium High Contrast - AgX",
        "None",
    ),
) -> dict:
    scene = bpy.context.scene
    view = _set_enum_if_available(scene.view_settings, "view_transform", ("AgX", "Khronos PBR Neutral", "Standard"))
    look = _set_enum_if_available(scene.view_settings, "look", look_preference)
    scene.view_settings.exposure = float(exposure)
    scene.view_settings.gamma = 1.0
    return {"view_transform": view, "look": look, "exposure": scene.view_settings.exposure}


def set_render_engine(preference: str = "CYCLES") -> str:
    scene = bpy.context.scene
    preference = preference.upper()
    if preference == "CYCLES":
        candidates = ("CYCLES",)
    else:
        candidates = ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_EEVEE_LEGACY")
    selected = _set_enum_if_available(scene.render, "engine", candidates)
    if selected is None:
        raise RuntimeError(f"No supported render engine found for {preference}")
    return selected


def configure_cycles_production(
    *,
    samples: int = 256,
    adaptive_threshold: float = 0.01,
    resolution: Sequence[int] = (1600, 900),
    transparent: bool = False,
    exposure: float = 0.0,
) -> dict:
    scene = bpy.context.scene
    engine = set_render_engine("CYCLES")
    cycles = scene.cycles
    cycles.samples = max(16, int(samples))
    for prop, value in (
        ("use_adaptive_sampling", True),
        ("adaptive_threshold", max(0.001, float(adaptive_threshold))),
        ("use_denoising", True),
        ("max_bounces", 8),
        ("diffuse_bounces", 4),
        ("glossy_bounces", 4),
        ("transmission_bounces", 6),
        ("transparent_max_bounces", 8),
    ):
        if hasattr(cycles, prop):
            setattr(cycles, prop, value)
    scene.render.resolution_x = int(resolution[0])
    scene.render.resolution_y = int(resolution[1])
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = bool(transparent)
    scene.render.image_settings.file_format = "PNG"
    color = set_production_color_management(exposure=exposure)
    return {"engine": engine, "samples": cycles.samples, "resolution": list(resolution), **color}


def configure_eevee_web_preview(
    *, resolution: Sequence[int] = (1280, 720), exposure: float = 0.0
) -> dict:
    scene = bpy.context.scene
    engine = set_render_engine("EEVEE")
    scene.render.resolution_x = int(resolution[0])
    scene.render.resolution_y = int(resolution[1])
    scene.render.resolution_percentage = 100
    color = set_production_color_management(exposure=exposure)
    return {"engine": engine, "resolution": list(resolution), **color}


def ensure_world(color=(0.006, 0.009, 0.018, 1.0), strength: float = 0.05) -> bpy.types.World:
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("LOOKDEV_World")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    background = next((n for n in nodes if n.type == "BACKGROUND"), None) or nodes.new("ShaderNodeBackground")
    output = next((n for n in nodes if n.type == "OUTPUT_WORLD"), None) or nodes.new("ShaderNodeOutputWorld")
    bg_output = background.outputs.get("Background")
    world_surface = output.inputs.get("Surface")
    if bg_output is None or world_surface is None:
        raise RuntimeError("World Background or Output socket is unavailable")
    if not world_surface.is_linked:
        links.new(bg_output, world_surface)
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = max(0.0, float(strength))
    world[TAG] = True
    return world


def create_area_light(
    *,
    name: str,
    location: Sequence[float],
    target: Sequence[float],
    energy: float,
    size: float,
    color: Sequence[float] = (1.0, 1.0, 1.0),
    shape: str = "DISK",
) -> bpy.types.Object:
    data = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
    data.energy = max(0.0, float(energy))
    data.color = tuple(float(c) for c in color[:3])
    data.shape = shape if shape in {"SQUARE", "RECTANGLE", "DISK", "ELLIPSE"} else "DISK"
    data.size = max(0.01, float(size))
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    _look_at(obj, Vector(target))
    obj[TAG] = True
    obj["lookdev_role"] = "light"
    obj.hide_render = False
    return obj


def remove_generated_lookdev_objects() -> int:
    removed = 0
    for obj in list(bpy.data.objects):
        if bool(obj.get(TAG, False)):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
    return removed


def create_architecture_night_rig(
    *,
    object_names: Sequence[str] | None = None,
    clear_previous: bool = True,
    base_energy: float | None = None,
    world_strength: float = 0.045,
) -> dict:
    objects = _resolve_objects(object_names)
    minimum, maximum = _world_bounds(objects)
    center = (minimum + maximum) * 0.5
    extent = maximum - minimum
    scene_size = max(extent.length, 1.0)
    if clear_previous:
        remove_generated_lookdev_objects()
    ensure_world(strength=world_strength)

    key_power = float(base_energy) if base_energy is not None else max(350.0, scene_size * scene_size * 12.0)
    key = create_area_light(
        name="LOOKDEV_Key_Moon",
        location=center + Vector((-0.75, -0.95, 1.25)) * scene_size,
        target=center,
        energy=key_power,
        size=scene_size * 0.7,
        color=(0.72, 0.82, 1.0),
    )
    fill = create_area_light(
        name="LOOKDEV_Fill",
        location=center + Vector((0.95, -0.45, 0.45)) * scene_size,
        target=center,
        energy=key_power * 0.22,
        size=scene_size * 1.0,
        color=(0.78, 0.86, 1.0),
    )
    rim = create_area_light(
        name="LOOKDEV_Rim",
        location=center + Vector((0.65, 0.85, 0.95)) * scene_size,
        target=center,
        energy=key_power * 0.42,
        size=scene_size * 0.45,
        color=(1.0, 0.72, 0.50),
    )
    return {
        "center": list(center),
        "scene_size": scene_size,
        "lights": [key.name, fill.name, rim.name],
        "key_energy": key_power,
        "note": "Add practical lights explicitly at fixtures; do not increase emission blindly.",
    }


def create_pbr_material(
    name: str,
    preset: str = "plastic",
    *,
    base_color: Sequence[float] | None = None,
    metallic: float | None = None,
    roughness: float | None = None,
    coat_weight: float | None = None,
) -> bpy.types.Material:
    params = dict(MATERIAL_PRESETS.get(preset, MATERIAL_PRESETS["plastic"]))
    overrides = {
        "base_color": base_color,
        "metallic": metallic,
        "roughness": roughness,
        "coat_weight": coat_weight,
    }
    params.update({k: v for k, v in overrides.items() if v is not None})
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    node = _principled(mat)
    rgba = tuple(params.get("base_color", (0.5, 0.5, 0.5, 1.0)))
    if len(rgba) == 3:
        rgba = rgba + (1.0,)
    mat.diffuse_color = rgba
    _set_socket(node, ("Base Color",), rgba)
    _set_socket(node, ("Metallic",), float(params.get("metallic", 0.0)))
    _set_socket(node, ("Roughness",), float(params.get("roughness", 0.5)))
    _set_socket(node, ("Coat Weight", "Clearcoat", "Coat"), float(params.get("coat_weight", 0.0)))
    _set_socket(node, ("Coat Roughness", "Clearcoat Roughness"), float(params.get("coat_roughness", 0.2)))
    _set_socket(node, ("Specular IOR Level", "Specular"), float(params.get("specular_ior_level", 0.5)))
    _set_socket(node, ("Transmission Weight", "Transmission"), float(params.get("transmission_weight", 0.0)))
    _set_socket(node, ("IOR",), float(params.get("ior", 1.5)))
    mat["lookdev_v6_preset"] = preset
    mat["glb_policy"] = "simple_principled"
    return mat


def set_material_emission(
    material_name: str,
    *,
    color: Sequence[float] = (1.0, 0.55, 0.22, 1.0),
    strength: float = 2.0,
) -> dict:
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        raise ValueError(f"Material not found: {material_name}")
    node = _principled(mat)
    rgba = tuple(color) if len(color) == 4 else tuple(color) + (1.0,)
    color_set = _set_socket(node, ("Emission Color", "Emission"), rgba)
    strength_set = _set_socket(node, ("Emission Strength",), max(0.0, float(strength)))
    mat["lookdev_v6_emission_calibrate_by_clipping"] = True
    return {"material": mat.name, "color_set": color_set, "strength_set": strength_set, "strength": strength}


def assign_material(object_name: str, material_name: str, slot: int = 0) -> None:
    obj = bpy.data.objects.get(object_name)
    mat = bpy.data.materials.get(material_name)
    if obj is None or mat is None:
        raise ValueError("Object or material not found")
    data = getattr(obj, "data", None)
    if data is None or not hasattr(data, "materials"):
        raise TypeError(f"Object {object_name} does not support materials")
    while len(data.materials) <= slot:
        data.materials.append(mat)
    data.materials[slot] = mat


def apply_bevel_detail_pass(
    object_names: Sequence[str],
    *,
    width_ratio: float = 0.004,
    segments: int = 3,
    angle_limit_degrees: float = 30.0,
) -> list[dict]:
    results: list[dict] = []
    for name in object_names:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH":
            results.append({"object": name, "status": "skipped"})
            continue
        max_dim = max(float(v) for v in obj.dimensions)
        if max_dim <= 0:
            results.append({"object": name, "status": "zero_size"})
            continue
        width = max(max_dim * 0.0005, min(max_dim * float(width_ratio), max_dim * 0.03))
        mod = next((m for m in obj.modifiers if m.type == "BEVEL" and m.name.startswith("LOOKDEV")), None)
        if mod is None:
            mod = obj.modifiers.new("LOOKDEV_Bevel", "BEVEL")
        mod.width = width
        mod.segments = max(1, int(segments))
        if hasattr(mod, "limit_method"):
            mod.limit_method = "ANGLE"
        if hasattr(mod, "angle_limit"):
            mod.angle_limit = math.radians(float(angle_limit_degrees))
        if hasattr(mod, "harden_normals"):
            mod.harden_normals = True
        for poly in obj.data.polygons:
            poly.use_smooth = True
        obj["lookdev_hard_surface"] = True
        obj["lookdev_v6_bevel_width"] = width
        results.append({"object": name, "status": "ok", "width": width, "modifier": mod.name})
    return results


def set_neutral_clay_override(enabled: bool = True) -> str | None:
    view_layer = bpy.context.view_layer
    if enabled:
        mat = create_pbr_material("LOOKDEV_Neutral_Clay", "neutral_clay")
        view_layer.material_override = mat
        return mat.name
    view_layer.material_override = None
    return None


def render_png(
    filepath: str | Path,
    *,
    resolution: Sequence[int] = (1600, 900),
    samples: int = 256,
    exposure: float = 0.0,
) -> str:
    if bpy.context.scene.camera is None:
        raise RuntimeError("Scene has no active camera")
    configure_cycles_production(samples=samples, resolution=resolution, exposure=exposure)
    path = Path(filepath).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if not path.exists():
        raise RuntimeError(f"Render output missing: {path}")
    return str(path)


def write_scene_summary(filepath: str | Path) -> str:
    scene = bpy.context.scene
    payload = {
        "render_engine": scene.render.engine,
        "view_transform": scene.view_settings.view_transform,
        "look": scene.view_settings.look,
        "exposure": scene.view_settings.exposure,
        "objects": len(scene.objects),
        "lights": [
            {
                "name": obj.name,
                "type": obj.data.type,
                "energy": getattr(obj.data, "energy", None),
                "size": getattr(obj.data, "size", None),
            }
            for obj in scene.objects
            if obj.type == "LIGHT"
        ],
        "materials": [mat.name for mat in bpy.data.materials],
    }
    path = Path(filepath).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


__all__ = [
    "save_checkpoint",
    "set_production_color_management",
    "configure_cycles_production",
    "configure_eevee_web_preview",
    "ensure_world",
    "create_area_light",
    "remove_generated_lookdev_objects",
    "create_architecture_night_rig",
    "create_pbr_material",
    "set_material_emission",
    "assign_material",
    "apply_bevel_detail_pass",
    "set_neutral_clay_override",
    "render_png",
    "write_scene_summary",
]
