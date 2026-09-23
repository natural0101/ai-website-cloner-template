"""Replace the flat tan satchel with a rounded dark leather volume and details."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_rounded_satchel_attempt7"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_back_sweep_attempt6.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_rounded_satchel_attempt7.blend"
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
source = bpy.data.objects["V6_Satchel"]
strap = bpy.data.objects["V6_SatchelStrap"]
before = {"satchel": bounds(source), "strap": bounds(strap)}
source.parent = None
source.hide_render = True
source.hide_set(True)
source.name = "V6_Satchel_SOURCE_FLAT_A7"
source["comforting_cat_preserved_source"] = True
source["comforting_cat_rejection_reason"] = "flat_tan_panel"

leather = bpy.data.materials.get("V6_DarkWeatheredLeather")
if leather is None:
    leather = bpy.data.materials.new("V6_DarkWeatheredLeather")
leather.use_nodes = True
principled = leather.node_tree.nodes.get("Principled BSDF")
if principled is None:
    raise RuntimeError("Principled BSDF missing from V6_DarkWeatheredLeather")
principled.inputs["Base Color"].default_value = (0.075, 0.026, 0.009, 1.0)
principled.inputs["Roughness"].default_value = 0.72
principled.inputs["Metallic"].default_value = 0.0
cream = bpy.data.objects["V6_Muzzle_L"].data.materials[0]
orange = bpy.data.objects["V6_Head"].data.materials[0]


def rounded_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    bevel_width: float,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(value * 0.5 for value in dimensions)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for linked in list(obj.users_collection):
        linked.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    bevel = obj.modifiers.new(f"{name}_RoundedEdges", "BEVEL")
    bevel.width = bevel_width
    bevel.segments = 5
    return obj


satchel = rounded_cube(
    "V6_Satchel",
    (0.36, -0.545, 1.21),
    (0.71, 0.20, 0.82),
    leather,
    0.075,
)
flap = rounded_cube(
    "V6_SatchelFlap",
    (0.36, -0.665, 1.46),
    (0.68, 0.075, 0.30),
    leather,
    0.055,
)
strap.data.materials.clear()
strap.data.materials.append(leather)


def poly_curve(
    name: str,
    points: list[tuple[float, float, float]],
    bevel_depth: float,
    material: bpy.types.Material,
    cyclic: bool = False,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    return obj


heart_points = [
    (0.36, -0.716, 1.37),
    (0.26, -0.716, 1.49),
    (0.28, -0.716, 1.57),
    (0.36, -0.716, 1.52),
    (0.44, -0.716, 1.57),
    (0.46, -0.716, 1.49),
]
heart = poly_curve("V6_SatchelHeart", heart_points, 0.018, cream, cyclic=True)
for index, x_value in enumerate((0.24, 0.48)):
    poly_curve(
        f"V6_SatchelTasselCord_{index}",
        [(x_value, -0.66, 0.84), (x_value, -0.67, 0.69)],
        0.012,
        leather,
    )
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=16,
        location=(x_value, -0.68, 0.65),
    )
    bead = bpy.context.object
    bead.name = f"V6_SatchelTassel_{index}"
    bead.scale = (0.045, 0.035, 0.075)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for linked in list(bead.users_collection):
        linked.objects.unlink(bead)
    collection.objects.link(bead)
    bead.parent = root
    bead.matrix_parent_inverse = root.matrix_world.inverted()
    bead.data.materials.append(cream)

bpy.context.view_layer.update()
after = {
    "satchel": bounds(satchel),
    "flap": bounds(flap),
    "heart": bounds(heart),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_RoundedSatchel_A7"
scene["comforting_cat_v6_stage"] = "ROUNDED_SATCHEL"
scene["comforting_cat_v6_attempt"] = 7
scene["comforting_cat_v6_dominant_defect"] = "flat_light_satchel_panel"
scene["comforting_cat_v6_preserved_source"] = source.name


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
    "stage": "ROUNDED_SATCHEL",
    "attempt": 7,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "flat_light_satchel_panel",
    "preserved_source": source.name,
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
print("COMFORTING_CAT_V6_ROUNDED_SATCHEL_A7=" + json.dumps(report, ensure_ascii=False))
