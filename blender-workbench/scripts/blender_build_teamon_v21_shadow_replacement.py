from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
VARIANT = os.environ.get("TEAMON_SHADOW_VARIANT", "v21")
SHADOW_BLEND = Path(
    os.environ.get(
        "TEAMON_SHADOW_SOURCE_BLEND",
        str(
            PROJECT_ROOT
            / "blender-workbench"
            / "artifacts"
            / "blend"
            / "teamon_shadow_hand_baked_world.blend"
        ),
    )
)
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / f"teamon_reference_{VARIANT}_shadow_composed.blend"
PREVIEW_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / f"teamon-{VARIANT}-shadow-composed-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / f"teamon_reference_{VARIANT}_shadow_composition_report.json"


def remove_tree(obj: bpy.types.Object) -> None:
    for child in list(obj.children):
        remove_tree(child)
    bpy.data.objects.remove(obj, do_unlink=True)


def mesh_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def triangle_count(objects: list[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


if not SHADOW_BLEND.exists():
    raise FileNotFoundError(SHADOW_BLEND)

composition_root = bpy.data.objects["TEAMON_CompositionRoot"]
keycap = bpy.data.objects["TEAMON_Keycap"]
camera = bpy.data.objects["TEAMON_Camera"]

ability_root = bpy.data.objects.get("TEAMON_Ability_ContactPivot")
if ability_root is not None:
    remove_tree(ability_root)

with bpy.data.libraries.load(str(SHADOW_BLEND), link=False) as (available, requested):
    if "TEAMON_ShadowBaked" not in available.collections:
        raise RuntimeError("Baked Shadow checkpoint has no TEAMON_ShadowBaked collection")
    requested.collections = ["TEAMON_ShadowBaked"]

shadow_collection = requested.collections[0]
shadow_collection.name = "TEAMON_ShadowHand_V21"
bpy.context.scene.collection.children.link(shadow_collection)

hand_root = bpy.data.objects["TEAMON_ShadowBakedRoot"]
source_world = hand_root.matrix_world.copy()
hand_root.parent = composition_root
hand_root.matrix_world = source_world
visible_hand = [
    obj
    for obj in shadow_collection.all_objects
    if obj.type == "MESH" and obj.name.startswith("TEAMON_V") and not obj.hide_render
]
index_mesh = next(obj for obj in visible_hand if obj.get("shadow_index_distal"))

hand_scale = float(os.environ.get("TEAMON_SHADOW_SCALE", "1.0"))
hand_rotation_z_degrees = float(os.environ.get("TEAMON_SHADOW_ROTATION_Z", "0.0"))
bpy.context.view_layer.update()

index_low, index_high = mesh_bounds([index_mesh])
key_low, key_high = mesh_bounds([keycap])
index_contact = Vector(
    (
        (index_low.x + index_high.x) * 0.5,
        (index_low.y + index_high.y) * 0.5,
        index_low.z,
    )
)
contact_target = Vector(
    (
        float(os.environ.get("TEAMON_SHADOW_CONTACT_X", "0.80")),
        float(os.environ.get("TEAMON_SHADOW_CONTACT_Y", "0.90")),
        key_high.z + 0.004,
    )
)
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

# Pose the complete imported hand around the fingertip contact.  Keeping the
# pivot on the key prevents silhouette adjustments from making the finger
# float above, or tunnel through, the cap.
pose_transform = (
    Matrix.Translation(contact_target)
    @ Matrix.Rotation(math.radians(hand_rotation_z_degrees), 4, "Z")
    @ Matrix.Scale(hand_scale, 4)
    @ Matrix.Translation(-contact_target)
)
for obj in visible_hand:
    obj.matrix_world = pose_transform @ obj.matrix_world
bpy.context.view_layer.update()

# Bounding-box contact is only an approximation of the distal surface, so
# re-snap after the pose transform to preserve the measured four-millimetre gap.
index_low, index_high = mesh_bounds([index_mesh])
index_contact = Vector(
    (
        (index_low.x + index_high.x) * 0.5,
        (index_low.y + index_high.y) * 0.5,
        index_low.z,
    )
)
hand_root.location += contact_target - index_contact
bpy.context.view_layer.update()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW_PATH)
bpy.ops.render.render(write_still=True)

hand_low, hand_high = mesh_bounds(visible_hand)
report = {
    "asset": "TEAMON v21 Shadow Hand replacement",
    "source": str(SHADOW_BLEND),
    "source_license": "Apache-2.0",
    "input_button": bpy.data.filepath,
    "checkpoint": str(BLEND_PATH),
    "preview": str(PREVIEW_PATH),
    "hand_scale": hand_scale,
    "hand_rotation_z_degrees": hand_rotation_z_degrees,
    "hand_mesh_count": len(visible_hand),
    "hand_triangle_count": triangle_count(visible_hand),
    "hand_bounds": {"min": list(hand_low), "max": list(hand_high)},
    "contact_target": list(contact_target),
    "contact_gap": mesh_bounds([index_mesh])[0].z - key_high.z,
    "status": "composition_visual_gate",
}
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print(json.dumps(report, ensure_ascii=False, indent=2))
