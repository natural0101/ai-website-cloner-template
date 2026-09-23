"""Reshape only the head shell into a tapered, softly tufted kitten silhouette."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_head_cheek_wedge_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_bushy_tail_attempt3.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_head_cheek_wedge_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    p = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return p * p * (3.0 - 2.0 * p)


head = bpy.data.objects["Cat_Head_Mesh"]
before = bounds(head)
x_radius = 0.805464
z_min = 2.436165
height = 1.073992
inverse = head.matrix_world.inverted()

for vertex in head.data.vertices:
    original = head.matrix_world @ vertex.co
    x = original.x
    y = original.y
    z = original.z
    radius = min(1.0, abs(x) / x_radius)
    height_t = max(0.0, min(1.0, (z - z_min) / height))
    side = -1.0 if x < 0.0 else 1.0

    front = 1.0 - smoothstep(-0.42, 0.08, y)
    rear = smoothstep(0.00, 0.38, y)
    face_lock = (
        front
        * (1.0 - smoothstep(0.50, 0.64, radius))
        * smoothstep(0.12, 0.22, height_t)
        * (1.0 - smoothstep(0.56, 0.64, height_t))
    )
    edit_gate = (1.0 - face_lock) * (
        1.0 - smoothstep(0.58, 0.66, height_t)
    )
    cheek_band = smoothstep(0.20, 0.30, height_t) * (
        1.0 - smoothstep(0.48, 0.58, height_t)
    )
    outer_cheek = smoothstep(0.48, 0.72, radius)
    lower_jaw = 1.0 - smoothstep(0.08, 0.24, height_t)
    lateral_jaw = smoothstep(0.25, 0.62, radius)
    tuft = (
        0.014 * math.exp(-((height_t - 0.30) / 0.040) ** 2)
        + 0.009 * math.exp(-((height_t - 0.40) / 0.035) ** 2)
    )
    depth_weight = 0.65 + 0.35 * front

    reshaped = Vector((x, y, z))
    reshaped.z = z + edit_gate * 0.045 * lower_jaw * lateral_jaw
    reshaped.y = y - edit_gate * (
        0.025 * cheek_band * outer_cheek * front
        + 0.035 * lower_jaw * rear
    )
    reshaped.x = x + side * edit_gate * (
        depth_weight * outer_cheek * (0.038 * cheek_band + tuft)
        - 0.045 * lower_jaw * lateral_jaw
    )
    vertex.co = inverse @ reshaped

head.data.update()
bpy.context.view_layer.update()
after = bounds(head)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_HeadCheekWedge_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "HEAD_CHEEK_WEDGE"
scene["comforting_cat_v5_geometry_attempt"] = "head_cheek_wedge_1"
scene["comforting_cat_v5_dominant_defect"] = "smooth_spherical_head_silhouette"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "eyes, lids, eyebrows",
        "muzzle, nose, mouth and whiskers",
        "ears",
        "scarf and costume",
        "limbs and paws",
        "satchel and tail",
        "materials",
        "lighting and cameras",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render(
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
render(camera, "02_material_front", (0.0, -8.6, 3.20), (0.0, -0.04, 2.05), 4.70)
render(camera, "03_front_3q", (4.0, -7.4, 3.50), (0.0, -0.02, 2.00), 4.80)
render(camera, "04_side", (8.4, -0.35, 3.20), (0.0, 0.0, 1.94), 4.80)
render(camera, "05_back", (0.0, 8.4, 3.20), (0.0, 0.04, 1.94), 4.80)
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
qa = runpy.run_path(str(SCENE_QA_PATH))["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
report = {
    "asset": ASSET,
    "stage": "HEAD_CHEEK_WEDGE",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "smooth_spherical_head_silhouette",
    "protected": [
        "face assemblies",
        "ears",
        "all non-head-shell objects",
    ],
    "before": before,
    "after": after,
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(qa["errors"])),
        "warnings": sorted(set(qa["warnings"])),
    },
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_HEAD_CHEEK_WEDGE_A1=" + json.dumps(report, ensure_ascii=False))
