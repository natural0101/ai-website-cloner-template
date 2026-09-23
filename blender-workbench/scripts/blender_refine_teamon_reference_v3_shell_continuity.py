import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_shell_continuity.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_shell_continuity_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-shell-continuity-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-shell-continuity-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-shell-continuity-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min_z": min(point.z for point in corners),
        "max_z": max(point.z for point in corners),
    }


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
press_group = bpy.data.objects.get("TEAMON_HandPressGroup")
keycap = bpy.data.objects.get("TEAMON_Keycap")
index_pad = bpy.data.objects.get("TEAMON_Index_ContactPad")
camera = bpy.data.objects.get("TEAMON_Camera")
if None in (hand_root, press_group, keycap, index_pad, camera):
    raise RuntimeError("TEAMON visual-QA checkpoint is incomplete")

# Replace black stick-like inner links with the recessed rose mechanism visible
# in the reference. Geometry remains narrow; only the joint read changes.
seam_material = bpy.data.materials.get("TEAMON_Robot_Seam_V3")
if seam_material is not None and seam_material.use_nodes:
    bsdf = seam_material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.22, 0.065, 0.078, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.38

# Make the three rear fingers read as overlapping mechanical shells instead of
# rows of beads. Scaling occurs along each object's local capsule axis.
scaled = {}
for finger in ("Middle", "Ring", "Pinky"):
    for obj in bpy.data.objects:
        if obj.hide_render or not obj.name.startswith(f"TEAMON_{finger}_"):
            continue
        if obj.name.endswith("_Armor"):
            obj.scale.x *= 1.22
            obj.scale.y *= 1.10
            obj.scale.z *= 1.06
            scaled[obj.name] = list(obj.scale)
        elif obj.name.endswith("_ContactPad"):
            obj.scale.x *= 1.25
            obj.scale.y *= 1.16
            scaled[obj.name] = list(obj.scale)

# The index receives a broad, nearly planar contact assembly. Its distal armor
# and pad grow together so the overlap remains visible from the hero camera.
index_distal = bpy.data.objects.get("TEAMON_Index_Distal_Armor")
if index_distal is not None:
    index_distal.scale.x *= 1.16
    index_distal.scale.y *= 1.10
    scaled[index_distal.name] = list(index_distal.scale)
index_pad.scale.x *= 1.14
index_pad.scale.y *= 1.10
index_pad.scale.z *= 0.92
scaled[index_pad.name] = list(index_pad.scale)

# Extend the manufactured palm housing toward the knuckle row.
for name, delta_x, scale_x in (
    ("TEAMON_PalmShell", -0.10, 1.08),
    ("TEAMON_PalmDorsalPlate_V3", -0.24, 1.08),
    ("TEAMON_KnuckleBridge_V3", -0.22, 1.12),
):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.location.x += delta_x
        obj.scale.x *= scale_x

# Raise the index contact farther back on the key. Shift both static chain
# pieces and the distal pivot group, then re-seat the pad in world space.
index_shift = Vector((0.0, 0.30, 0.0))
for obj in bpy.data.objects:
    if obj.hide_render or not obj.name.startswith("TEAMON_Index_"):
        continue
    if obj.parent == press_group:
        continue
    obj.location += index_shift
press_group.location += index_shift

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

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens
camera.location = (9.1, -5.6, 5.0)
camera.data.lens = 70
look_at(camera, (2.0, 1.0, 1.65))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)
camera.location = (3.4, 0.7, 13.8)
camera.data.lens = 70
look_at(camera, (1.5, 0.9, 1.2))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v3 shell continuity",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "scaled_shells": scaled,
    "contact": {
        "keycap_top_z": keycap_top,
        "pad_bottom_before": pad_bottom_before,
        "pad_bottom_after": pad_bottom_after,
        "signed_gap": pad_bottom_after - keycap_top,
    },
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
