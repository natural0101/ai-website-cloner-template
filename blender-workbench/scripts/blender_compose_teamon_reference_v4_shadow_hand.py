import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_shadow_composed.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_shadow_composition_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-composed-hero.png"
SIDE_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-composed-side.png"
TOP_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-shadow-composed-top.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH, SIDE_PATH, TOP_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def mesh_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    return {
        "min": [min(point[index] for point in points) for index in range(3)],
        "max": [max(point[index] for point in points) for index in range(3)],
    }


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


hand_root = bpy.data.objects.get("TEAMON_HandRoot")
keycap = bpy.data.objects.get("TEAMON_Keycap")
camera = bpy.data.objects.get("TEAMON_Camera")
if None in (hand_root, keycap, camera):
    raise RuntimeError("TEAMON v4 geometry checkpoint is incomplete")

body = {
    name: bpy.data.objects.get(f"TEAMON_SH_{name}")
    for name in ("rh_wrist", "rh_palm", "rh_ffknuckle", "rh_ffdistal", "rh_lfknuckle")
}
if any(value is None for value in body.values()):
    raise RuntimeError("Shadow Hand hierarchy is incomplete")

visible_hand = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH" and obj.name.startswith("TEAMON_SH_") and not obj.hide_render
]
index_mesh = next(obj for obj in visible_hand if obj.get("mjcf_body") == "rh_ffdistal")

# Recover the original posed MJCF basis independently of the previous global
# transform, then flip the palm roll so the dorsal shells face the hero camera
# and the thumb sits in the foreground like the primary reference.
inverse_root = hand_root.matrix_world.inverted()
local_wrist = inverse_root @ body["rh_wrist"].matrix_world.translation
local_tip = inverse_root @ (body["rh_ffdistal"].matrix_world @ Vector((0.0, 0.0, 0.030)))
local_ff = inverse_root @ body["rh_ffknuckle"].matrix_world.translation
local_lf = inverse_root @ body["rh_lfknuckle"].matrix_world.translation

source_long = (local_tip - local_wrist).normalized()
source_width = (local_ff - local_lf).normalized()
source_normal = source_long.cross(source_width).normalized()
source_width = source_normal.cross(source_long).normalized()

target_long = Vector((-1.0, -0.08, -0.18)).normalized()
target_width = Vector((-0.08, -1.0, 0.02))
target_width = (target_width - target_long * target_width.dot(target_long)).normalized()
target_normal = target_long.cross(target_width).normalized()
target_width = target_normal.cross(target_long).normalized()

source_basis = Matrix((source_long, source_width, source_normal)).transposed()
target_basis = Matrix((target_long, target_width, target_normal)).transposed()
rotation = target_basis @ source_basis.transposed()
hand_scale = 13.2
hand_root.matrix_world = rotation.to_4x4() @ Matrix.Diagonal((hand_scale, hand_scale, hand_scale, 1.0))
bpy.context.view_layer.update()

index_before = mesh_bounds([index_mesh])
index_contact = Vector(
    (
        (index_before["min"][0] + index_before["max"][0]) * 0.5,
        (index_before["min"][1] + index_before["max"][1]) * 0.5,
        index_before["min"][2],
    )
)
keycap_top = mesh_bounds([keycap])["max"][2]
contact_target = Vector((1.05, -0.48, keycap_top + 0.004))
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

# Match the supplied image crop: dominant base, hand entering from the right,
# and enough elevation to read the acrylic thickness.
camera.location = (11.65, -13.55, 10.45)
camera.data.lens = 68
look_at(camera, (0.70, 0.12, 1.04))

scene = bpy.context.scene
scene.render.resolution_x = 768
scene.render.resolution_y = 432
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

hero_location = camera.location.copy()
hero_rotation = camera.rotation_euler.copy()
hero_lens = camera.data.lens
camera.location = (10.6, -2.0, 6.3)
camera.data.lens = 66
look_at(camera, (0.7, 0.0, 1.0))
scene.render.filepath = str(SIDE_PATH)
bpy.ops.render.render(write_still=True)
camera.location = (0.0, -0.6, 15.6)
camera.data.lens = 68
look_at(camera, (0.35, 0.0, 0.9))
scene.render.filepath = str(TOP_PATH)
bpy.ops.render.render(write_still=True)
camera.location = hero_location
camera.rotation_euler = hero_rotation
camera.data.lens = hero_lens

index_after = mesh_bounds([index_mesh])
report = {
    "asset": "TEAMON reference v4 Shadow Hand composition",
    "stage": "COMPOSITION",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "renders": [str(HERO_PATH), str(SIDE_PATH), str(TOP_PATH)],
    "hand_scale": hand_scale,
    "hand_bounds": mesh_bounds(visible_hand),
    "keycap_top_z": keycap_top,
    "index_tip_bounds": index_after,
    "rest_contact_gap": index_after["min"][2] - keycap_top,
    "contact_target": list(contact_target),
    "camera_location": list(camera.location),
    "camera_lens_mm": camera.data.lens,
    "exported_glb": False,
    "status": "composition_visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
