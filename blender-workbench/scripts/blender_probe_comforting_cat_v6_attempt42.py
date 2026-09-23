"""Read-only capability and active-scene probe for comforting cat attempt42."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v6_integrated_cheek_microtufts_attempt42.blend"
).resolve()
CAPABILITY_PROBE = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "capability_probe.py"
).resolve()
REPORT_PATH = (
    WORKBENCH
    / "artifacts"
    / "reports"
    / "comforting_cat_v6_attempt42_capability_scene_probe.json"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

capabilities = runpy.run_path(str(CAPABILITY_PROBE))["probe"]()
root = bpy.data.objects.get("CatV6_Root")
descendants = []
if root is not None:
    stack = [root]
    while stack:
        current = stack.pop()
        descendants.append(current)
        stack.extend(list(current.children))

payload = {
    "source_blend": str(SOURCE_BLEND),
    "scene": bpy.context.scene.name,
    "mode": "TRUE_360",
    "capability_probe": capabilities,
    "root_present": root is not None,
    "root_descendant_count": len(descendants),
    "mesh_count": sum(obj.type == "MESH" for obj in descendants),
    "curve_count": sum(obj.type == "CURVE" for obj in descendants),
    "camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
    "render_engine": bpy.context.scene.render.engine,
    "frame": bpy.context.scene.frame_current,
}
REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False))
