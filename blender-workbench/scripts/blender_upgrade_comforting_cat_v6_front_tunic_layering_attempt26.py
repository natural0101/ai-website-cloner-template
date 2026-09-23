"""Narrow, curve, embed, and darken the dominant flat front tunic."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_front_tunic_layering_attempt26"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tail_low_compact_attempt25.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_front_tunic_layering_attempt26.blend"
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


def preserve_copy(obj: bpy.types.Object) -> str:
    copy = obj.copy()
    copy.data = obj.data.copy()
    bpy.data.collections["Comforting_Cat_V6"].objects.link(copy)
    copy.parent = None
    copy.hide_render = True
    copy.hide_set(True)
    copy.name = f"{obj.name}_SOURCE_A26"
    copy["comforting_cat_preserved_source"] = True
    copy["comforting_cat_rejection_reason"] = "wide_bright_flat_apron"
    return copy.name


root = bpy.data.objects["CatV6_Root"]
robe = bpy.data.objects["V6_Robe"]
tunic = bpy.data.objects["V6_FrontTunic"]
if len(tunic.data.vertices) != 20:
    raise RuntimeError(f"Expected 20 tunic vertices; got {len(tunic.data.vertices)}")

before = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "material": tunic.data.materials[0].name,
}
preserved_source = preserve_copy(tunic)

world_vertices = [
    (-0.370, -0.390, 1.980),
    (-0.185, -0.490, 1.980),
    (0.000, -0.520, 1.980),
    (0.185, -0.490, 1.980),
    (0.370, -0.390, 1.980),
    (-0.350, -0.400, 1.580),
    (-0.175, -0.500, 1.580),
    (0.000, -0.530, 1.580),
    (0.175, -0.500, 1.580),
    (0.350, -0.400, 1.580),
    (-0.330, -0.410, 1.150),
    (-0.165, -0.500, 1.150),
    (0.000, -0.525, 1.150),
    (0.165, -0.500, 1.150),
    (0.330, -0.410, 1.150),
    (-0.300, -0.400, 0.780),
    (-0.150, -0.480, 0.730),
    (0.000, -0.510, 0.700),
    (0.150, -0.480, 0.730),
    (0.300, -0.400, 0.780),
]
inverse = tunic.matrix_world.inverted()
for vertex, coordinate in zip(tunic.data.vertices, world_vertices):
    vertex.co = inverse @ Vector(coordinate)
tunic.data.update()

solidify = tunic.modifiers.get("V6_FrontTunicThickness")
if solidify is None:
    solidify = tunic.modifiers.new("V6_FrontTunicThickness", "SOLIDIFY")
solidify.thickness = 0.050
solidify.offset = 1.0

bevel = tunic.modifiers.get("V6_FrontTunicSoftEdge")
if bevel is None:
    bevel = tunic.modifiers.new("V6_FrontTunicSoftEdge", "BEVEL")
bevel.width = 0.014
bevel.segments = 3

old_material = tunic.data.materials[0]
material = old_material.copy()
material.name = "V6_TunicWarmLinen_A26"
material.diffuse_color = (0.27, 0.29, 0.28, 1.0)
material.roughness = 0.84
if material.use_nodes and material.node_tree is not None:
    principled = next(
        (
            node
            for node in material.node_tree.nodes
            if node.type == "BSDF_PRINCIPLED"
        ),
        None,
    )
    if principled is not None:
        principled.inputs["Base Color"].default_value = (0.27, 0.29, 0.28, 1.0)
        principled.inputs["Roughness"].default_value = 0.84
tunic.data.materials.clear()
tunic.data.materials.append(material)

bpy.context.view_layer.update()
after = {
    "robe": bounds(robe),
    "tunic": bounds(tunic),
    "material": material.name,
}
metrics = {
    "tunic_width_over_robe_width": round(
        after["tunic"]["dimensions"][0] / after["robe"]["dimensions"][0], 5
    ),
    "tunic_height": after["tunic"]["dimensions"][2],
    "tunic_depth": after["tunic"]["dimensions"][1],
    "center_hem_drop": round(world_vertices[15][2] - world_vertices[17][2], 5),
    "solidify_thickness": round(float(solidify.thickness), 5),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FrontTunicLayering_A26"
scene["comforting_cat_v6_stage"] = "FRONT_TUNIC_LAYERING"
scene["comforting_cat_v6_attempt"] = 26
scene["comforting_cat_v6_dominant_defect"] = "wide_bright_flat_apron"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)


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
    "stage": "FRONT_TUNIC_LAYERING",
    "attempt": 26,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "wide_bright_flat_apron",
    "preserved_source": preserved_source,
    "before": before,
    "after": after,
    "metrics": metrics,
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
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print(json.dumps(report, ensure_ascii=False))
