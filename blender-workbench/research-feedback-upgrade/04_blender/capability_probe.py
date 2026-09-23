"""Read-only Blender version and capability probe."""
from __future__ import annotations

import sys

import bpy


def _has(path: str) -> bool:
    current = bpy
    for part in path.split('.'):
        if not hasattr(current, part):
            return False
        current = getattr(current, part)
    return True


def probe() -> dict:
    checks = [
        'ops.object.text_add',
        'ops.object.convert',
        'ops.object.modifier_apply',
        'ops.export_scene.gltf',
        'ops.wm.save_as_mainfile',
        'data.materials.new',
        'types.GeometryNodeTree',
    ]
    return {
        'blender_version': '.'.join(map(str, bpy.app.version)),
        'version_tuple': list(bpy.app.version),
        'background': bool(bpy.app.background),
        'capabilities': {name: _has(name) for name in checks},
        'python_version': sys.version.split()[0],
    }
