"""Replace constant-depth head plates with tapered ear and cheek wedges."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_tapered_ears_tufts_attempt4"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_scarf_curved_folds_attempt3.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_tapered_ears_tufts_attempt4.blend"
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
orange = bpy.data.objects["V6_Head"].data.materials[0]
pink = bpy.data.objects["V6_Nose"].data.materials[0]
source_names = [
    "V6_Ear_L",
    "V6_Ear_R",
    "V6_InnerEar_L",
    "V6_InnerEar_R",
    "V6_CheekTuft_L_0",
    "V6_CheekTuft_L_1",
    "V6_CheekTuft_R_0",
    "V6_CheekTuft_R_1",
]
before = {name: bounds(bpy.data.objects[name]) for name in source_names}
for name in source_names:
    source = bpy.data.objects[name]
    source.parent = None
    source.hide_render = True
    source.hide_set(True)
    source.name = f"{name}_SOURCE_FLAT_A4"
    source["comforting_cat_preserved_source"] = True
    source["comforting_cat_rejection_reason"] = "constant_depth_plate"


def tapered_wedge(
    name: str,
    base_a: tuple[float, float],
    base_b: tuple[float, float],
    tip: tuple[float, float],
    center_y: float,
    base_depth: float,
    tip_depth: float,
    material: bpy.types.Material,
    bevel_width: float,
) -> bpy.types.Object:
    vertices = [
        (base_a[0], center_y - base_depth * 0.5, base_a[1]),
        (base_b[0], center_y - base_depth * 0.5, base_b[1]),
        (tip[0], center_y - tip_depth * 0.5, tip[1]),
        (base_a[0], center_y + base_depth * 0.5, base_a[1]),
        (base_b[0], center_y + base_depth * 0.5, base_b[1]),
        (tip[0], center_y + tip_depth * 0.5, tip[1]),
    ]
    faces = [
        (2, 1, 0),
        (3, 4, 5),
        (0, 1, 4, 3),
        (1, 2, 5, 4),
        (2, 0, 3, 5),
    ]
    mesh = bpy.data.meshes.new(f"{name}_TaperedWedgeMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    bevel = obj.modifiers.new(f"{name}_SoftEdge", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 3
    return obj


for side, sign in (("L", -1.0), ("R", 1.0)):
    ear = tapered_wedge(
        f"V6_Ear_{side}",
        (sign * 0.66, 3.16),
        (sign * 0.25, 3.18),
        (sign * 0.47, 3.60),
        center_y=0.0,
        base_depth=0.38,
        tip_depth=0.055,
        material=orange,
        bevel_width=0.022,
    )
    tapered_wedge(
        f"V6_InnerEar_{side}",
        (sign * 0.57, 3.21),
        (sign * 0.33, 3.22),
        (sign * 0.47, 3.51),
        center_y=-0.194,
        base_depth=0.020,
        tip_depth=0.010,
        material=pink,
        bevel_width=0.006,
    )
    for index, (z_value, reach, half_height) in enumerate(
        [(2.76, 0.11, 0.10), (2.64, 0.15, 0.09)]
    ):
        base_x = sign * 0.68
        tip_x = sign * (0.67 + reach)
        tapered_wedge(
            f"V6_CheekTuft_{side}_{index}",
            (base_x, z_value + half_height),
            (base_x, z_value - half_height),
            (tip_x, z_value),
            center_y=0.02,
            base_depth=0.22,
            tip_depth=0.025,
            material=orange,
            bevel_width=0.012,
        )

bpy.context.view_layer.update()
after = {
    name: bounds(bpy.data.objects[name])
    for name in (
        "V6_Ear_L",
        "V6_Ear_R",
        "V6_CheekTuft_L_0",
        "V6_CheekTuft_R_0",
    )
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_TaperedEarsTufts_A4"
scene["comforting_cat_v6_stage"] = "TAPERED_EARS_TUFTS"
scene["comforting_cat_v6_attempt"] = 4
scene["comforting_cat_v6_dominant_defect"] = "ear_and_cheek_plates_in_side_view"
scene["comforting_cat_v6_preserved_sources"] = json.dumps(
    [f"{name}_SOURCE_FLAT_A4" for name in source_names]
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
    "stage": "TAPERED_EARS_TUFTS",
    "attempt": 4,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "ear_and_cheek_plates_in_side_view",
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
print("COMFORTING_CAT_V6_TAPERED_EARS_TUFTS_A4=" + json.dumps(report, ensure_ascii=False))
