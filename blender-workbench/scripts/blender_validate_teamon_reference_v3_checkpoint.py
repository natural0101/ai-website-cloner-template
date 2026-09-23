import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_checkpoint_validation.json"
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[index] for point in corners) for index in range(3)],
        "max": [max(point[index] for point in corners) for index in range(3)],
    }


def triangle_count(obj):
    if obj.type != "MESH":
        return 0
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


required = (
    "TEAMON_CompositionRoot",
    "TEAMON_ButtonRoot",
    "TEAMON_PressGroup",
    "TEAMON_Base",
    "TEAMON_Keycap",
    "TEAMON_Text",
    "TEAMON_HandRoot",
    "TEAMON_HandPressGroup",
    "TEAMON_PalmShell",
    "TEAMON_ThenarShell",
    "TEAMON_WristCuff",
    "TEAMON_Index_ContactPad",
)
missing = [name for name in required if bpy.data.objects.get(name) is None]

visible_meshes = [obj for obj in bpy.data.objects if obj.type == "MESH" and not obj.hide_render]
hidden_rejected = [
    obj.name
    for obj in bpy.data.objects
    if obj.hide_render and obj.get("remediation_status")
]

keycap = bpy.data.objects.get("TEAMON_Keycap")
index_pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
keycap_bounds = world_bounds(keycap) if keycap else None
index_bounds = world_bounds(index_pad) if index_pad else None
contact_delta = None
if keycap_bounds and index_bounds:
    contact_delta = index_bounds["min"][2] - keycap_bounds["max"][2]

finger_names = ("Index", "Middle", "Ring", "Pinky", "Thumb")
finger_parts = {
    finger: sorted(
        obj.name
        for obj in visible_meshes
        if obj.name.startswith(f"TEAMON_{finger}_")
    )
    for finger in finger_names
}

composition_root = bpy.data.objects.get("TEAMON_CompositionRoot")
button_root = bpy.data.objects.get("TEAMON_ButtonRoot")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
hierarchy_ok = bool(
    composition_root
    and button_root
    and hand_root
    and button_root.parent == composition_root
    and hand_root.parent == composition_root
)

camera = bpy.data.objects.get("TEAMON_Camera")
report = {
    "asset": "TEAMON reference v3 checkpoint validation",
    "source_blend": bpy.data.filepath,
    "status": "visual_gate_in_progress",
    "exported_glb": False,
    "missing_required_objects": missing,
    "hierarchy_ok": hierarchy_ok,
    "visible_mesh_count": len(visible_meshes),
    "visible_triangle_count": sum(triangle_count(obj) for obj in visible_meshes),
    "hidden_rejected_checkpoint_part_count": len(hidden_rejected),
    "contact": {
        "keycap_top_z": keycap_bounds["max"][2] if keycap_bounds else None,
        "index_pad_bottom_z": index_bounds["min"][2] if index_bounds else None,
        "signed_gap": contact_delta,
        "passes_tolerance": contact_delta is not None and abs(contact_delta) <= 0.015,
    },
    "finger_parts": finger_parts,
    "camera": {
        "location": list(camera.location) if camera else None,
        "lens_mm": camera.data.lens if camera else None,
    },
    "blocking_visual_findings": [
        "palm and cuff still need more reference-like shell articulation",
        "finger fan occupies less screen area than the reference",
        "hero overlay edge IoU remains only an iteration metric, not an acceptance pass",
    ],
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
