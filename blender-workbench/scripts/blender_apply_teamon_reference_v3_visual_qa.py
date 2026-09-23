import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_visual_qa.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_visual_qa_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-visual-qa-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min_z": min(point.z for point in corners),
        "max_z": max(point.z for point in corners),
    }


scene = bpy.context.scene
camera = bpy.data.objects.get("TEAMON_Camera")
keycap = bpy.data.objects.get("TEAMON_Keycap")
underplate = bpy.data.objects.get("TEAMON_RGB_Underplate")
text = bpy.data.objects.get("TEAMON_Text")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
index_pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
palm = bpy.data.objects.get("TEAMON_PalmShell")
palm_plate = bpy.data.objects.get("TEAMON_PalmDorsalPlate_V3")
knuckle_bridge = bpy.data.objects.get("TEAMON_KnuckleBridge_V3")
wrist = bpy.data.objects.get("TEAMON_WristHousing_V3")
required = (camera, keycap, underplate, text, press_group, index_pad, palm, palm_plate, knuckle_bridge, wrist)
if any(item is None for item in required):
    raise RuntimeError("TEAMON palm/cuff checkpoint is incomplete")

# Reference-locked projection: footprint diagonal aligns vertically and the
# ensemble is lifted in the 16:9 hero frame.
camera_target = (0.30, 0.20, 0.55)
camera.location = (13.84, -9.80, 14.00)
camera.data.lens = 63
look_at(camera, camera_target)
scene.camera = camera

# Restore a visible black shoulder around the acrylic without adding a third
# stacked slab. The hidden diffuser follows the cap footprint.
keycap.scale.x *= 5.12 / 5.46
keycap.scale.y *= 3.46 / 3.72
underplate.scale.x *= 4.98 / 5.30
underplate.scale.y *= 3.32 / 3.56

# Reference lettering runs along the other local axis; keep it left of the
# index contact zone.
text.rotation_euler.z += math.radians(90.0)
text.location.x = -0.42
text.location.y = -0.08

# Flatten the organic palm body and let the mechanical dorsal plate dominate.
palm.scale.y *= 1.12
palm.scale.z *= 0.72
palm_plate.scale.x *= 1.20
palm_plate.scale.y *= 1.25
palm_plate.scale.z *= 1.08
knuckle_bridge.scale.x *= 1.18
knuckle_bridge.scale.y *= 1.12
wrist.scale.y *= 0.74
wrist.scale.z *= 0.86
wrist_top = bpy.data.objects.get("TEAMON_WristDorsalPlate_V3")
if wrist_top is not None:
    wrist_top.scale.y *= 0.86

# Lengthen armor locally so the internal links become recessed joint gaps
# instead of long black rods.
for obj in bpy.data.objects:
    if not obj.hide_render and obj.name.startswith("TEAMON_") and obj.name.endswith("_Armor"):
        obj.scale.x *= 1.15

# Raise and spread the non-index fingers as a stepped fan. The enlarged palm
# plate overlaps the shifted roots, keeping the hero silhouette continuous.
fan_offsets = {
    "Middle": Vector((0.0, 0.05, 0.24)),
    "Ring": Vector((0.0, 0.14, 0.38)),
    "Pinky": Vector((0.0, 0.24, 0.50)),
}
for finger, offset in fan_offsets.items():
    for obj in bpy.data.objects:
        if obj.hide_render or not obj.name.startswith(f"TEAMON_{finger}_"):
            continue
        obj.location += offset

# Move the whole index chain farther across the key so its contact anchor rises
# from ~55% to ~42% of frame height after the camera correction.
index_offset = Vector((0.0, 0.36, 0.0))
for obj in bpy.data.objects:
    if obj.hide_render or not obj.name.startswith("TEAMON_Index_"):
        continue
    if obj.parent == press_group:
        continue
    obj.location += index_offset
press_group.location += index_offset

# Wide, flat pad with overlap into distal armor. Keep thickness low and seat
# the entire distal group by evaluated world bounds.
index_pad.scale.x *= 1.78
index_pad.scale.y *= 1.42
index_pad.scale.z *= 0.88
bpy.context.view_layer.update()
keycap_top = world_bounds(keycap)["max_z"]
pad_bottom_before = world_bounds(index_pad)["min_z"]
press_group.location.z += keycap_top - pad_bottom_before
bpy.context.view_layer.update()
pad_bottom_after = world_bounds(index_pad)["min_z"]

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v3 visual QA application",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "camera": {
        "location": list(camera.location),
        "target": list(camera_target),
        "lens_mm": camera.data.lens,
    },
    "contact": {
        "keycap_top_z": keycap_top,
        "pad_bottom_before": pad_bottom_before,
        "pad_bottom_after": pad_bottom_after,
        "signed_gap": pad_bottom_after - keycap_top,
    },
    "fan_offsets": {name: list(offset) for name, offset in fan_offsets.items()},
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
