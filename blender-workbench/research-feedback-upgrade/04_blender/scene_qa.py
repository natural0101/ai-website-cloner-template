"""Read-only structural QA for Blender 5.x scenes.

Run inside Blender. It does not apply modifiers, change transforms or save the
blend file. The report is JSON-serializable and may optionally be written to an
allowlisted path by the caller.
"""
from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Iterable

import bpy
import bmesh
from mathutils import Vector


def _world_bbox(obj: bpy.types.Object) -> tuple[Vector, Vector] | None:
    if not hasattr(obj, 'bound_box') or obj.bound_box is None:
        return None
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    if not points:
        return None
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def _axis_gap(a_min: float, a_max: float, b_min: float, b_max: float) -> float:
    if a_max < b_min:
        return b_min - a_max
    if b_max < a_min:
        return a_min - b_max
    return 0.0


def aabb_gap(a: tuple[Vector, Vector], b: tuple[Vector, Vector]) -> float:
    gaps = [_axis_gap(a[0][i], a[1][i], b[0][i], b[1][i]) for i in range(3)]
    return sqrt(sum(g * g for g in gaps))


def aabb_overlap_extent(a: tuple[Vector, Vector], b: tuple[Vector, Vector]) -> list[float]:
    return [max(0.0, min(a[1][i], b[1][i]) - max(a[0][i], b[0][i])) for i in range(3)]


def mesh_topology(obj: bpy.types.Object) -> dict:
    if obj.type != 'MESH' or obj.data is None:
        return {}
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        bm.normal_update()
        return {
            'vertices': len(bm.verts),
            'edges': len(bm.edges),
            'faces': len(bm.faces),
            'non_manifold_edges': sum(1 for e in bm.edges if not e.is_manifold),
            'boundary_edges': sum(1 for e in bm.edges if e.is_boundary),
            'wire_edges': sum(1 for e in bm.edges if e.is_wire),
            'loose_vertices': sum(1 for v in bm.verts if not v.link_edges),
            'degenerate_faces': sum(1 for f in bm.faces if f.calc_area() <= 1e-12),
        }
    finally:
        bm.free()


def object_report(obj: bpy.types.Object) -> dict:
    bounds = _world_bbox(obj)
    report = {
        'name': obj.name,
        'type': obj.type,
        'hidden_render': bool(obj.hide_render),
        'location': list(map(float, obj.location)),
        'rotation_euler': list(map(float, obj.rotation_euler)),
        'scale': list(map(float, obj.scale)),
        'negative_scale': any(v < 0 for v in obj.scale),
        'unapplied_scale': any(abs(abs(v) - 1.0) > 1e-4 for v in obj.scale),
        'parent': obj.parent.name if obj.parent else None,
        'collections': sorted(c.name for c in obj.users_collection),
        'modifiers': [{'name': m.name, 'type': m.type, 'show_render': bool(m.show_render)} for m in obj.modifiers],
    }
    if bounds:
        report['bounds_min'] = list(map(float, bounds[0]))
        report['bounds_max'] = list(map(float, bounds[1]))
        report['dimensions_world'] = list(map(float, bounds[1] - bounds[0]))
    if obj.type == 'MESH':
        report['topology'] = mesh_topology(obj)
    return report


def audit_scene(
    object_names: Iterable[str] | None = None,
    contact_tolerance: float = 0.002,
    floating_tolerance: float = 0.02,
) -> dict:
    selected_names = set(object_names or [])
    objects = [
        obj for obj in bpy.context.scene.objects
        if obj.type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}
        and (not selected_names or obj.name in selected_names)
        and not obj.hide_render
    ]
    reports = [object_report(obj) for obj in objects]
    bounds = {obj.name: _world_bbox(obj) for obj in objects}
    edges: list[dict] = []
    adjacency = {obj.name: set() for obj in objects}
    for i, a in enumerate(objects):
        ba = bounds.get(a.name)
        if not ba:
            continue
        for b in objects[i + 1:]:
            bb = bounds.get(b.name)
            if not bb:
                continue
            gap = aabb_gap(ba, bb)
            overlap = aabb_overlap_extent(ba, bb)
            relation = 'OVERLAP' if all(x > 0 for x in overlap) else ('NEAR' if gap <= contact_tolerance else 'SEPARATE')
            if gap <= floating_tolerance:
                adjacency[a.name].add(b.name)
                adjacency[b.name].add(a.name)
            edges.append({
                'a': a.name, 'b': b.name, 'gap': float(gap),
                'overlap_extent': list(map(float, overlap)), 'relation': relation,
            })
    floating = sorted(name for name, neighbours in adjacency.items() if not neighbours and len(objects) > 1)
    duplicate_base_names: dict[str, list[str]] = {}
    for obj in objects:
        base = obj.name.rsplit('.', 1)[0] if obj.name.rsplit('.', 1)[-1].isdigit() else obj.name
        duplicate_base_names.setdefault(base, []).append(obj.name)
    duplicates = {k: v for k, v in duplicate_base_names.items() if len(v) > 1}
    errors: list[str] = []
    warnings: list[str] = []
    for report in reports:
        if report.get('negative_scale'):
            warnings.append(f"{report['name']}: negative scale")
        topology = report.get('topology', {})
        if topology.get('degenerate_faces', 0):
            errors.append(f"{report['name']}: degenerate faces={topology['degenerate_faces']}")
        if topology.get('loose_vertices', 0):
            warnings.append(f"{report['name']}: loose vertices={topology['loose_vertices']}")
    if floating:
        warnings.append('Potential floating components: ' + ', '.join(floating))
    if duplicates:
        warnings.append('Ambiguous duplicate-style names detected')
    return {
        'schema_version': '1.0',
        'blender_version': '.'.join(map(str, bpy.app.version)),
        'scene': bpy.context.scene.name,
        'object_count': len(objects),
        'objects': reports,
        'contact_graph': edges,
        'potential_floating_components': floating,
        'duplicate_style_names': duplicates,
        'errors': errors,
        'warnings': warnings,
        'limits': [
            'AABB proximity is a heuristic, not exact mesh collision.',
            'Non-manifold edges can be intentional for open surfaces.',
            'Visual quality still requires renders from multiple views.',
        ],
    }


def write_report(path: str | Path, **kwargs) -> str:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(audit_scene(**kwargs), ensure_ascii=False, indent=2), encoding='utf-8')
    return str(target)
