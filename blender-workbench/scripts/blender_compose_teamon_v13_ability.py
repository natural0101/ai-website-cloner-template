from __future__ import annotations

import json
from math import radians
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
HAND_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v13_ability_pose_d.blend"
PREVIEW_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
QA_MODULES = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
if str(QA_MODULES) not in sys.path:
    sys.path.insert(0, str(QA_MODULES))

import scene_qa


VARIANT = os.environ.get("TEAMON_VARIANT", "n")
HAND_ROOT_X = float(os.environ.get("TEAMON_HAND_ROOT_X", "83"))
HAND_ROOT_Y = float(os.environ.get("TEAMON_HAND_ROOT_Y", "-90"))
CONTACT_ROLL_Z = float(os.environ.get("TEAMON_CONTACT_ROLL_Z", "-35"))
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / f"teamon_reference_v13_ability_composition_{VARIANT}.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_v13_ability_composition_{VARIANT}_report.json"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_v13_ability_composition_{VARIANT}_structural_qa.json"


def remove_tree(obj: bpy.types.Object) -> None:
    for child in list(obj.children):
        remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(path: Path, camera_location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> str:
    camera = bpy.data.objects["TEAMON_Camera"]
    camera.location = camera_location
    camera.data.lens = lens
    look_at(camera, Vector(target))
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


if not HAND_BLEND.exists():
    raise FileNotFoundError(HAND_BLEND)

composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
button_group = bpy.data.objects["TEAMON_PressGroup"]
keycap = bpy.data.objects["TEAMON_Keycap"]

rebelia_root = bpy.data.objects.get("TEAMON_RebeliaHandRoot")
if rebelia_root is not None:
    remove_tree(rebelia_root)
for obj in (button_group,):
    obj.animation_data_clear()

with bpy.data.libraries.load(str(HAND_BLEND), link=False) as (available, requested):
    if "TEAMON_Ability_Pose_OUTPUT" not in available.collections:
        raise RuntimeError("Ability pose checkpoint lacks TEAMON_Ability_Pose_OUTPUT")
    requested.collections = ["TEAMON_Ability_Pose_OUTPUT"]
hand_collection = requested.collections[0]
bpy.context.scene.collection.children.link(hand_collection)

hand_root = bpy.data.objects["TEAMON_Ability_HandRoot"]
hand_root.parent = composition_root
hand_root.location = (0.0, 0.0, 0.0)
hand_root.rotation_euler = (radians(HAND_ROOT_X), radians(HAND_ROOT_Y), 0.0)
hand_root.scale = (21.0, 21.0, 21.0)
hand_root["stage"] = "COMPOSITION"
hand_root["pose"] = "index extended; middle/ring/pinky curled; thumb below"
hand_root["source_revision"] = "34c9a9324d3739d976e6de441e56ccefafd0000b"
hand_root["source_license"] = "MIT"
bpy.context.view_layer.update()

index_objects = [
    bpy.data.objects["TEAMON_Ability_index_L1_index_mesh_1"],
    bpy.data.objects["TEAMON_Ability_index_L2_index_mesh_2"],
]
index_low, index_high = world_bounds(index_objects)
key_low, key_high = world_bounds([keycap])
index_contact = Vector((index_low.x, (index_low.y + index_high.y) * 0.5, index_low.z))
contact_target = Vector((0.80, 0.90, key_high.z + 0.006))
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

# Rotate the entire hand around the fixed fingertip contact so the wrist falls
# down and right in frame while the index remains on the keycap.
contact_pivot = bpy.data.objects.new("TEAMON_Ability_ContactPivot", None)
bpy.context.scene.collection.objects.link(contact_pivot)
contact_pivot.parent = composition_root
contact_pivot.location = contact_target
bpy.context.view_layer.update()
hand_root.parent = contact_pivot
hand_root.matrix_parent_inverse = contact_pivot.matrix_world.inverted()
contact_pivot.rotation_euler[2] = radians(CONTACT_ROLL_Z)
bpy.context.view_layer.update()

ability_visuals = [
    obj for obj in hand_collection.all_objects
    if obj.type == "MESH" and obj.name.startswith("TEAMON_Ability_")
]
button_meshes = [
    bpy.data.objects[name]
    for name in ("TEAMON_Base", "TEAMON_Recess", "TEAMON_RGB_Underplate", "TEAMON_Keycap", "TEAMON_Text")
]

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"

hero_path = PREVIEW_DIR / f"teamon-v13-ability-composition-{VARIANT}-hero.png"
side_path = PREVIEW_DIR / f"teamon-v13-ability-composition-{VARIANT}-side.png"
top_path = PREVIEW_DIR / f"teamon-v13-ability-composition-{VARIANT}-top.png"
hero = render(hero_path, (11.0, -9.0, 11.8), (-0.22, -0.02, 0.68), 66.0)
side = render(side_path, (10.7, 1.7, 6.3), (0.65, -0.05, 1.15), 62.0)
top = render(top_path, (0.2, -0.45, 15.2), (0.45, 0.0, 0.9), 68.0)
render(hero_path, (11.0, -9.0, 11.8), (-0.22, -0.02, 0.68), 66.0)

all_meshes = button_meshes + ability_visuals
qa = scene_qa.audit_scene(
    object_names=[obj.name for obj in all_meshes],
    contact_tolerance=0.02,
    floating_tolerance=0.08,
)
QA_PATH.parent.mkdir(parents=True, exist_ok=True)
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

index_low, index_high = world_bounds(index_objects)
key_low, key_high = world_bounds([keycap])
report = {
    "stage": "COMPOSITION",
    "target_mode": "HYBRID_HERO",
    "variant": VARIANT,
    "hand_root_rotation_degrees": [HAND_ROOT_X, HAND_ROOT_Y, 0.0],
    "contact_roll_z_degrees": CONTACT_ROLL_Z,
    "input_button_blend": bpy.data.filepath,
    "hand_checkpoint": str(HAND_BLEND),
    "checkpoint": str(BLEND_PATH),
    "previews": [hero, side, top],
    "hand_source": "https://github.com/psyonicinc/ability-hand-api",
    "hand_revision": "34c9a9324d3739d976e6de441e56ccefafd0000b",
    "hand_license": "MIT",
    "hand_visual_mesh_count": len(ability_visuals),
    "contact_target": list(contact_target),
    "index_bounds": {"min": list(index_low), "max": list(index_high)},
    "keycap_bounds": {"min": list(key_low), "max": list(key_high)},
    "aabb_contact_gap_z": index_low.z - key_high.z,
    "qa_report": str(QA_PATH),
    "status": "composition_visual_gate"
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
