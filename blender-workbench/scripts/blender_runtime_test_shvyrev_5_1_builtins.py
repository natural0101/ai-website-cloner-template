"""Transient runtime fixtures for high-priority SHVYREV Blender built-ins."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
REPORT = (
    WORKBENCH
    / "artifacts"
    / "reports"
    / "shvyrev_blender_5_1_builtin_runtime_test.json"
).resolve()
REPORT.relative_to(WORKBENCH)
PREFIX = "__SHVYREV_RUNTIME_FIXTURE__"

results: dict[str, dict[str, object]] = {}
created_node_groups: list[bpy.types.NodeTree] = []
created_objects: list[bpy.types.Object] = []
created_meshes: list[bpy.types.Mesh] = []


def record(name: str, ok: bool, detail: str) -> None:
    results[name] = {"ok": ok, "detail": detail}


def test_node(tree_type: str, node_type: str) -> None:
    key = f"node:{node_type}"
    group = None
    try:
        group = bpy.data.node_groups.new(
            name=f"{PREFIX}{node_type}",
            type=tree_type,
        )
        created_node_groups.append(group)
        node = group.nodes.new(node_type)
        record(key, node.bl_idname == node_type, node.bl_idname)
    except Exception as exc:
        record(key, False, f"{type(exc).__name__}: {exc}")


def make_fixture_object() -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{PREFIX}Mesh")
    mesh.from_pydata(
        [
            (-0.5, -0.5, 0.0),
            (0.5, -0.5, 0.0),
            (0.5, 0.5, 0.0),
            (-0.5, 0.5, 0.0),
        ],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    obj = bpy.data.objects.new(f"{PREFIX}Object", mesh)
    created_meshes.append(mesh)
    created_objects.append(obj)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def test_modifier(obj: bpy.types.Object, modifier_type: str) -> None:
    key = f"modifier:{modifier_type}"
    try:
        modifier = obj.modifiers.new(
            name=f"{PREFIX}{modifier_type}",
            type=modifier_type,
        )
        record(key, modifier.type == modifier_type, modifier.type)
        obj.modifiers.remove(modifier)
    except Exception as exc:
        record(key, False, f"{type(exc).__name__}: {exc}")


try:
    for node_type in (
        "ShaderNodeBsdfMetallic",
        "ShaderNodeTexGabor",
        "ShaderNodeAmbientOcclusion",
        "ShaderNodeTexSky",
    ):
        test_node("ShaderNodeTree", node_type)
    test_node("GeometryNodeTree", "GeometryNodeRaycast")
    test_node("CompositorNodeTree", "CompositorNodeKuwahara")
    test_node("CompositorNodeTree", "CompositorNodeWhiteBalance")

    fixture = make_fixture_object()
    for modifier_type in (
        "SHRINKWRAP",
        "LATTICE",
        "SURFACE_DEFORM",
        "SOLIDIFY",
        "BEVEL",
        "WEIGHTED_NORMAL",
        "CLOTH",
    ):
        test_modifier(fixture, modifier_type)
    try:
        basis = fixture.shape_key_add(name="Basis")
        test = fixture.shape_key_add(name="Test")
        record(
            "shape_keys:add",
            basis.name == "Basis" and test.name == "Test",
            f"{basis.name},{test.name}",
        )
    except Exception as exc:
        record("shape_keys:add", False, f"{type(exc).__name__}: {exc}")
finally:
    for obj in created_objects:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in created_meshes:
        if mesh.name in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
    for group in created_node_groups:
        if group.name in bpy.data.node_groups:
            bpy.data.node_groups.remove(group)

leftovers = sorted(
    datablock.name
    for collection in (
        bpy.data.objects,
        bpy.data.meshes,
        bpy.data.node_groups,
    )
    for datablock in collection
    if datablock.name.startswith(PREFIX)
)
report = {
    "schema_version": "1.0",
    "probe_kind": "TRANSIENT_RUNTIME_FIXTURE",
    "blender_version": bpy.app.version_string,
    "source_file": str(Path(bpy.data.filepath).resolve()),
    "source_scene": bpy.context.scene.name,
    "results": results,
    "counts": {
        "passed": sum(result["ok"] is True for result in results.values()),
        "failed": sum(result["ok"] is False for result in results.values()),
        "total": len(results),
    },
    "cleanup": {
        "leftovers": leftovers,
        "passed": not leftovers,
    },
    "status_policy": (
        "A passed fixture proves node/modifier instantiation in Blender 5.1.1, "
        "not visual quality or production adoption."
    ),
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("SHVYREV_5_1_BUILTIN_RUNTIME_TEST=" + json.dumps(report, ensure_ascii=False))
