"""TRUE_360 lower silhouette pass: pear-shaped cloak over compact planted legs."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_cloak_leg_blockout_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_head_fur_mass_attempt1.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_cloak_leg_blockout_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


robe = bpy.data.objects["Cat_BlueRobe"]
body = bpy.data.objects["Cat_Body"]
legs = [bpy.data.objects["Cat_Leg_L"], bpy.data.objects["Cat_Leg_R"]]
feet = [bpy.data.objects["Cat_Foot_L"], bpy.data.objects["Cat_Foot_R"]]
tracked = [robe, body, *legs, *feet]
before = {obj.name: bounds(obj) for obj in tracked}

# Keep the collar fixed while extending the hem over the upper 40–50% of the
# legs. Profile scales create a lower-third belly and a softly tucked hem.
robe_points = [robe.matrix_world @ vertex.co for vertex in robe.data.vertices]
z_min = min(point.z for point in robe_points)
z_max = max(point.z for point in robe_points)
height = z_max - z_min
target_bottom = 0.49
robe_inverse = robe.matrix_world.inverted()
for vertex in robe.data.vertices:
    point = robe.matrix_world @ vertex.co
    t = max(0.0, min(1.0, (point.z - z_min) / height))
    point.z = target_bottom + t * (z_max - target_bottom)

    lower_belly = math.exp(-((t - 0.24) / 0.19) ** 2)
    hem_tuck = math.exp(-((t - 0.00) / 0.10) ** 2)
    shoulder_narrow = max(0.0, min(1.0, (t - 0.68) / 0.32))
    radial_scale = (
        1.0
        + 0.070 * lower_belly
        - 0.045 * hem_tuck
        - 0.060 * shoulder_narrow * shoulder_narrow
    )
    point.x *= radial_scale
    point.y *= 1.0 + 0.035 * lower_belly - 0.025 * hem_tuck
    # A subtle front chest and rounded back break the straight cylinder profile.
    point.y += -0.018 * math.exp(-((t - 0.62) / 0.20) ** 2)
    point.y += 0.014 * math.exp(-((t - 0.38) / 0.22) ** 2)
    vertex.co = robe_inverse @ point
robe.data.update()

# The body remains an editable internal volume but no longer reads as a third
# orange leg under the cloak.
body_points = [body.matrix_world @ vertex.co for vertex in body.data.vertices]
body_inverse = body.matrix_world.inverted()
for vertex in body.data.vertices:
    point = body.matrix_world @ vertex.co
    if point.z < 0.72:
        weight = max(0.0, min(1.0, (0.72 - point.z) / 0.24))
        point.x *= 1.0 - 0.24 * weight
        point.y *= 1.0 - 0.18 * weight
        point.z += 0.015 * weight
    vertex.co = body_inverse @ point
body.data.update()

# Extend the leg bottoms into the feet while the lowered cloak shortens the
# visible leg segment. Upper body contact stays fixed.
for leg in legs:
    points = [leg.matrix_world @ vertex.co for vertex in leg.data.vertices]
    leg_min = min(point.z for point in points)
    leg_max = max(point.z for point in points)
    inverse = leg.matrix_world.inverted()
    for vertex in leg.data.vertices:
        point = leg.matrix_world @ vertex.co
        t = max(0.0, min(1.0, (point.z - leg_min) / (leg_max - leg_min)))
        point.z -= 0.047 * (1.0 - t) ** 2
        vertex.co = inverse @ point
    leg.data.update()

# Bring the feet close together and flatten them without losing floor contact.
for foot in feet:
    points = [foot.matrix_world @ vertex.co for vertex in foot.data.vertices]
    foot_min = min(point.z for point in points)
    inverse = foot.matrix_world.inverted()
    direction = 1.0 if foot.name.endswith("_L") else -1.0
    for vertex in foot.data.vertices:
        point = foot.matrix_world @ vertex.co
        point.x += 0.035 * direction
        point.z = foot_min + (point.z - foot_min) * 0.90
        vertex.co = inverse @ point
    foot.data.update()

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in tracked}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_CloakLegBlockout_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "CLOAK_LEG_SILHOUETTE"
scene["comforting_cat_v5_geometry_attempt"] = "cloak_leg_blockout_1"
scene["comforting_cat_v5_dominant_defect"] = "cone_cloak_and_beaded_lower_body"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "head, ears and face",
        "scarf and collar",
        "arms and paws",
        "satchel and strap",
        "tail",
        "materials",
        "lighting and cameras",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "CLOAK_LEG_SILHOUETTE",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "cone_cloak_and_beaded_lower_body",
    "target_robe_bottom_world_z": target_bottom,
    "foot_inward_offset_each": 0.035,
    "before": before,
    "after": after,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_CLOAK_LEG_BLOCKOUT=" + json.dumps(report, ensure_ascii=False))
