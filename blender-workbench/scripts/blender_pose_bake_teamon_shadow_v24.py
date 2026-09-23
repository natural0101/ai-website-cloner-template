from __future__ import annotations

import json
import os
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
VARIANT = os.environ.get("TEAMON_SHADOW_POSE_VARIANT", "v24")
OUTPUT_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "blend"
    / f"teamon_shadow_hand_{VARIANT}_baked_world.blend"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "reports"
    / f"teamon_shadow_hand_{VARIANT}_pose_report.json"
)


def env_float(name: str, default: float) -> float:
    return float(os.environ.get(name, str(default)))


def set_finger_pose(prefix: str, proximal: float, middle: float, distal: float) -> None:
    bpy.data.objects[f"TEAMON_SH_rh_{prefix}proximal"].rotation_euler.x = proximal
    bpy.data.objects[f"TEAMON_SH_rh_{prefix}middle"].rotation_euler.x = middle
    bpy.data.objects[f"TEAMON_SH_rh_{prefix}distal"].rotation_euler.x = distal


poses = {
    # A graded curl creates the stepped silhouette seen in the reference:
    # middle reaches furthest, ring sits behind it, little stays closest to palm.
    "mf": (
        env_float("TEAMON_MF_PROXIMAL", 0.76),
        env_float("TEAMON_MF_MIDDLE", 1.10),
        env_float("TEAMON_MF_DISTAL", 0.88),
    ),
    "rf": (
        env_float("TEAMON_RF_PROXIMAL", 0.94),
        env_float("TEAMON_RF_MIDDLE", 1.22),
        env_float("TEAMON_RF_DISTAL", 0.96),
    ),
    "lf": (
        env_float("TEAMON_LF_PROXIMAL", 1.10),
        env_float("TEAMON_LF_MIDDLE", 1.34),
        env_float("TEAMON_LF_DISTAL", 1.04),
    ),
}
for finger_prefix, finger_pose in poses.items():
    set_finger_pose(finger_prefix, *finger_pose)

# Open the thumb away from the palm and rotate its fan toward the lower-right
# screen quadrant.  These remain editable environment parameters for the next
# visual iteration.
thumb_base = bpy.data.objects["TEAMON_SH_rh_thbase"]
thumb_base.rotation_euler.z += env_float("TEAMON_THUMB_BASE_Z_DELTA", -0.58)
bpy.data.objects["TEAMON_SH_rh_thproximal"].rotation_euler.x = env_float(
    "TEAMON_THUMB_PROXIMAL", 0.82
)
bpy.data.objects["TEAMON_SH_rh_thmiddle"].rotation_euler.y = env_float(
    "TEAMON_THUMB_MIDDLE_Y", -0.36
)
bpy.data.objects["TEAMON_SH_rh_thdistal"].rotation_euler.x = env_float(
    "TEAMON_THUMB_DISTAL", 0.34
)

finger_thickness = env_float("TEAMON_FINGER_THICKNESS", 1.34)
thumb_thickness = env_float("TEAMON_THUMB_THICKNESS", 1.28)
for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.startswith("TEAMON_SH_rh_"):
        continue
    body = str(obj.get("mjcf_body", ""))
    if body.startswith(("rh_mf", "rh_rf", "rh_lf")):
        obj.scale.x *= finger_thickness
        obj.scale.y *= finger_thickness
    elif body.startswith("rh_th"):
        obj.scale.x *= thumb_thickness
        obj.scale.y *= thumb_thickness
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

# Increase the solid central mass without scaling the kinematic hierarchy or
# moving the already-approved index contact.
palm_mesh = bpy.data.objects["TEAMON_SH_rh_palm_palm_00"]
palm_mesh.scale.x *= env_float("TEAMON_PALM_WIDTH", 1.20)
palm_mesh.scale.y *= env_float("TEAMON_PALM_THICKNESS", 1.28)
palm_mesh.scale.z *= env_float("TEAMON_PALM_LENGTH", 1.10)
wrist_mesh = bpy.data.objects["TEAMON_SH_rh_wrist_wrist_00"]
wrist_mesh.scale.x *= env_float("TEAMON_WRIST_WIDTH", 1.10)
wrist_mesh.scale.y *= env_float("TEAMON_WRIST_THICKNESS", 1.10)

bpy.context.view_layer.update()
source_meshes = [
    obj
    for obj in bpy.data.objects
    if obj.type == "MESH"
    and obj.name.startswith("TEAMON_SH_")
    and not obj.hide_render
]
if len(source_meshes) != 24:
    raise RuntimeError(f"Expected 24 visible Shadow Hand meshes, received {len(source_meshes)}")

baked_collection = bpy.data.collections.new("TEAMON_ShadowBaked")
bpy.context.scene.collection.children.link(baked_collection)
baked_root = bpy.data.objects.new("TEAMON_ShadowBakedRoot", None)
baked_collection.objects.link(baked_root)

baked_objects: list[bpy.types.Object] = []
for source in source_meshes:
    baked = source.copy()
    baked.data = source.data.copy()
    baked.animation_data_clear()
    baked.name = f"TEAMON_V24_{source.name.removeprefix('TEAMON_SH_')}"
    baked_collection.objects.link(baked)
    baked.parent = baked_root
    baked.matrix_world = source.matrix_world.copy()
    baked["mjcf_body"] = source.get("mjcf_body", "")
    baked["shadow_index_distal"] = source.get("mjcf_body") == "rh_ffdistal"
    baked_objects.append(baked)

for obj in list(bpy.data.objects):
    if obj not in baked_objects and obj != baked_root:
        bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection != baked_collection:
        bpy.data.collections.remove(collection)

report = {
    "asset": f"TEAMON Shadow Hand pose {VARIANT}",
    "mode": "HYBRID_HERO",
    "source_license": "Apache-2.0",
    "index_pose_changed": False,
    "finger_pose_radians": poses,
    "finger_thickness": finger_thickness,
    "thumb_thickness": thumb_thickness,
    "mesh_count": len(baked_objects),
    "output": str(OUTPUT_PATH),
}
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
