"""Replace segmented sleeve-arm-paw beads with continuous tapered arm meshes."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_unified_arms_attempt8"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_rounded_satchel_attempt7.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_unified_arms_attempt8.blend"
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
        "min": [round(float(value), 5) for value in mins],
        "max": [round(float(value), 5) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 5) for index in range(3)
        ],
    }


root = bpy.data.objects["CatV6_Root"]
collection = bpy.data.collections["Comforting_Cat_V6"]
blue = bpy.data.objects["V6_Robe"].data.materials[0]
orange = bpy.data.objects["V6_Head"].data.materials[0]
source_names = [
    "V6_Sleeve_L",
    "V6_Sleeve_R",
    "V6_Arm_L",
    "V6_Arm_R",
    "V6_Paw_L",
    "V6_Paw_R",
]
before = {name: bounds(bpy.data.objects[name]) for name in source_names}
for name in source_names:
    source = bpy.data.objects[name]
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = f"{name}_SOURCE_SEGMENTED_A8"
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "segmented_bead_chain"


def build_arm(side: str, sign: float) -> bpy.types.Object:
    ring_specs = [
        (2.02, 0.62, -0.01, 0.060, 0.070),
        (1.92, 0.64, -0.04, 0.155, 0.175),
        (1.73, 0.68, -0.08, 0.180, 0.190),
        (1.60, 0.70, -0.12, 0.150, 0.165),
        (1.39, 0.71, -0.16, 0.135, 0.150),
        (1.10, 0.71, -0.18, 0.120, 0.135),
        (0.91, 0.70, -0.19, 0.155, 0.165),
        (0.80, 0.69, -0.18, 0.070, 0.080),
    ]
    segments = 32
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for z_value, x_abs, center_y, radius_x, radius_y in ring_specs:
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append(
                (
                    sign * x_abs + radius_x * math.cos(angle),
                    center_y + radius_y * math.sin(angle),
                    z_value,
                )
            )
    for ring in range(len(ring_specs) - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            a = ring * segments + index
            b = ring * segments + next_index
            c = (ring + 1) * segments + next_index
            d = (ring + 1) * segments + index
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(f"V6_Arm_{side}_UnifiedMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(f"V6_ArmUnified_{side}", mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(blue)
    obj.data.materials.append(orange)
    for polygon in obj.data.polygons:
        center_z = sum(mesh.vertices[index].co.z for index in polygon.vertices) / len(
            polygon.vertices
        )
        polygon.material_index = 0 if center_z >= 1.64 else 1
        polygon.use_smooth = True
    return obj


arm_l = build_arm("L", -1.0)
arm_r = build_arm("R", 1.0)
bpy.context.view_layer.update()
after = {"left": bounds(arm_l), "right": bounds(arm_r)}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_UnifiedArms_A8"
scene["comforting_cat_v6_stage"] = "UNIFIED_ARMS"
scene["comforting_cat_v6_attempt"] = 8
scene["comforting_cat_v6_dominant_defect"] = "segmented_sleeve_arm_paw_beads"
scene["comforting_cat_v6_preserved_sources"] = json.dumps(
    [f"{name}_SOURCE_SEGMENTED_A8" for name in source_names]
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


camera = bpy.data.objects["CAT_RenderCamera"]
render(camera, "02_material_front", (0.0, -8.6, 3.08), (0.0, 0.0, 1.88), 4.20)
render(camera, "03_front_3q", (4.0, -7.4, 3.35), (0.0, 0.02, 1.84), 4.30)
render(camera, "04_side", (8.4, -0.35, 3.08), (0.0, 0.08, 1.82), 4.30)
render(camera, "05_back", (0.0, 8.4, 3.08), (0.0, 0.12, 1.82), 4.30)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

export_objects = descendants(root)
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
    "stage": "UNIFIED_ARMS",
    "attempt": 8,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "segmented_sleeve_arm_paw_beads",
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
scene["comforting_cat_v6_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V6_UNIFIED_ARMS_A8=" + json.dumps(report, ensure_ascii=False))
