"""Read-only Blender 5.1 capability probe for high-priority SHVYREV techniques."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
REPORT = (
    WORKBENCH
    / "artifacts"
    / "reports"
    / "shvyrev_blender_5_1_runtime_capability_probe.json"
).resolve()
REPORT.relative_to(WORKBENCH)


def node_type_exists(identifier: str) -> bool:
    return hasattr(bpy.types, identifier)


def modifier_type_exists(identifier: str) -> bool:
    return hasattr(bpy.types, identifier)


def has_operator(module: object, name: str) -> bool:
    return hasattr(module, name)


def enum_identifiers(rna_type: object, property_name: str) -> list[str]:
    prop = rna_type.bl_rna.properties.get(property_name)
    if prop is None or not hasattr(prop, "enum_items"):
        return []
    return [item.identifier for item in prop.enum_items]


nodes = {
    identifier: node_type_exists(identifier)
    for identifier in (
        "GeometryNodeRaycast",
        "ShaderNodeBsdfMetallic",
        "ShaderNodeTexGabor",
        "ShaderNodeAmbientOcclusion",
        "ShaderNodeTexSky",
        "CompositorNodeKuwahara",
        "CompositorNodeWhiteBalance",
    )
}
modifiers = {
    identifier: modifier_type_exists(identifier)
    for identifier in (
        "ShrinkwrapModifier",
        "LatticeModifier",
        "SurfaceDeformModifier",
        "SolidifyModifier",
        "BevelModifier",
        "WeightedNormalModifier",
        "ClothModifier",
    )
}
operators = {
    "object.material_slot_remove_all": has_operator(
        bpy.ops.object, "material_slot_remove_all"
    ),
    "object.modifier_add": has_operator(bpy.ops.object, "modifier_add"),
    "object.shape_key_add": has_operator(bpy.ops.object, "shape_key_add"),
    "uv.unwrap": has_operator(bpy.ops.uv, "unwrap"),
    "mesh.knife_project": has_operator(bpy.ops.mesh, "knife_project"),
    "outliner.orphans_purge": has_operator(bpy.ops.outliner, "orphans_purge"),
    "export_scene.gltf": has_operator(bpy.ops.export_scene, "gltf"),
}
api = {
    "asset_libraries": hasattr(
        bpy.context.preferences.filepaths, "asset_libraries"
    ),
    "file_datablocks": all(
        hasattr(bpy.data, name)
        for name in ("objects", "meshes", "materials", "images", "libraries")
    ),
    "library_load": hasattr(bpy.data.libraries, "load"),
    "library_write": hasattr(bpy.data.libraries, "write"),
}

report = {
    "schema_version": "1.0",
    "probe_kind": "RNA_API_READ_ONLY",
    "blender_version": bpy.app.version_string,
    "blender_version_tuple": list(bpy.app.version),
    "python_version": sys.version,
    "current_file": str(Path(bpy.data.filepath).resolve()),
    "current_scene": bpy.context.scene.name,
    "nodes": nodes,
    "modifiers": modifiers,
    "operators": operators,
    "api": api,
    "render_engines": enum_identifiers(bpy.types.RenderSettings, "engine"),
    "image_file_formats": enum_identifiers(
        bpy.types.ImageFormatSettings, "file_format"
    ),
    "technique_checks": {
        "raycast_geometry_workflow": nodes["GeometryNodeRaycast"],
        "metallic_bsdf_workflow": nodes["ShaderNodeBsdfMetallic"],
        "gabor_noise_workflow": nodes["ShaderNodeTexGabor"],
        "kuwahara_compositor_workflow": nodes["CompositorNodeKuwahara"],
        "white_balance_compositor_workflow": nodes[
            "CompositorNodeWhiteBalance"
        ],
        "shrinkwrap_decal_workflow": modifiers["ShrinkwrapModifier"],
        "lattice_soft_deformation": modifiers["LatticeModifier"],
        "surface_deform_flat_rest_shape": modifiers[
            "SurfaceDeformModifier"
        ],
        "solidify_shell_quality": modifiers["SolidifyModifier"],
        "edge_weight_bevel_control": modifiers["BevelModifier"],
        "shape_key_morph_workflow": operators["object.shape_key_add"],
        "asset_browser_library_intake": api["asset_libraries"],
        "export_reimport_validation_contract": operators[
            "export_scene.gltf"
        ],
    },
    "interpretation": {
        "true": "API/RNA capability exists in this Blender runtime; visual correctness still needs a fixture.",
        "false": "Capability is absent under this identifier and must remain version-gated or use an alternative.",
    },
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("SHVYREV_5_1_CAPABILITY_PROBE=" + json.dumps(report, ensure_ascii=False))
