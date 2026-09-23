import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_palm_cuff.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_palm_cuff_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-palm-cuff-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def apply_material(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def smooth_mesh(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def rounded_box(name, dimensions, location, radius, material, collection, parent, rotation=None, segments=7):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new(name=f"{name}_Bevel", type="BEVEL")
    bevel.width = min(radius, min(dimensions) * 0.44)
    bevel.segments = segments
    bevel.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    if rotation is not None:
        obj.rotation_euler = rotation
    smooth_mesh(obj)
    apply_material(obj, material)
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)
    parent_keep_world(obj, parent)
    return obj


def rounded_box_between(name, start, end, width, height, radius, material, collection, parent):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    center = (a + b) * 0.5
    return rounded_box(
        name,
        (direction.length, width, height),
        center,
        radius,
        material,
        collection,
        parent,
        rotation=direction.normalized().to_track_quat("X", "Z").to_euler(),
        segments=8,
    )


scene = bpy.context.scene
output = bpy.data.collections.get("TEAMON_OUTPUT")
hand_root = bpy.data.objects.get("TEAMON_HandRoot")
white = bpy.data.materials.get("TEAMON_Robot_White_V3")
seam = bpy.data.materials.get("TEAMON_Robot_Seam_V3")
if None in (output, hand_root, white, seam):
    raise RuntimeError("TEAMON finger-mass checkpoint is incomplete")

hidden = []
for name in ("TEAMON_PalmDorsalShell", "TEAMON_WristCuff", "TEAMON_WristInsetBand"):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.hide_render = True
        obj.hide_viewport = True
        obj["remediation_status"] = "rejected_soft_blob_preserved_hidden"
        hidden.append(name)

# A broad, flattened dorsal shield overlaps the finger roots and reads as a
# manufactured palm housing rather than a second organic blob.
palm_plate = rounded_box(
    "TEAMON_PalmDorsalPlate_V3",
    (2.30, 1.58, 0.34),
    (4.58, 2.18, 2.69),
    0.15,
    white,
    output,
    hand_root,
    rotation=(math.radians(-7.0), math.radians(8.0), math.radians(-17.0)),
    segments=8,
)

# A smaller bridge keeps the knuckle row visually attached to the palm plate.
knuckle_bridge = rounded_box(
    "TEAMON_KnuckleBridge_V3",
    (1.82, 0.62, 0.28),
    (4.22, 1.78, 2.62),
    0.12,
    white,
    output,
    hand_root,
    rotation=(math.radians(-9.0), math.radians(8.0), math.radians(-17.0)),
    segments=7,
)

# One continuous wrist housing, cropped by the hero frame. A thin dark collar
# remains recessed between it and the palm instead of a visible ball joint.
wrist_inner = rounded_box_between(
    "TEAMON_WristInnerLink_V3",
    (5.08, 2.52, 2.40),
    (5.68, 2.86, 2.37),
    1.28,
    0.82,
    0.18,
    seam,
    output,
    hand_root,
)
wrist_cuff = rounded_box_between(
    "TEAMON_WristHousing_V3",
    (5.48, 2.74, 2.39),
    (7.42, 3.82, 2.28),
    1.68,
    1.12,
    0.22,
    white,
    output,
    hand_root,
)
cuff_top = rounded_box_between(
    "TEAMON_WristDorsalPlate_V3",
    (5.65, 2.84, 2.78),
    (7.25, 3.72, 2.68),
    1.36,
    0.24,
    0.10,
    white,
    output,
    hand_root,
)

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v3 palm and cuff refinement",
    "mode": "HYBRID_HERO",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "hidden_soft_parts": hidden,
    "new_parts": [palm_plate.name, knuckle_bridge.name, wrist_inner.name, wrist_cuff.name, cuff_top.name],
    "exported_glb": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
