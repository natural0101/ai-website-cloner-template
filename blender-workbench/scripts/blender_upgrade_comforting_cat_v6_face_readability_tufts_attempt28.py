"""Restore reference-like eye/muzzle readability and connected cheek tufts."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_face_readability_tufts_attempt28"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_tunic_material_embed_attempt27.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_face_readability_tufts_attempt28.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def scale_mesh_world(
    obj: bpy.types.Object,
    scale_x: float,
    scale_z: float,
    translate_x: float = 0.0,
) -> None:
    obj_bounds = bounds(obj)
    center = Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        world.x = center.x + (world.x - center.x) * scale_x + translate_x
        world.z = center.z + (world.z - center.z) * scale_z
        vertex.co = inverse @ world
    obj.data.update()


def cheek_wedge(
    name: str,
    outline: list[tuple[float, float]],
    material: bpy.types.Material,
) -> bpy.types.Object:
    front_y = -0.30
    back_y = 0.10
    vertices = [(x, front_y, z) for x, z in outline]
    vertices.extend((x, back_y, z) for x, z in outline)
    faces = [
        (0, 1, 2),
        (5, 4, 3),
        (0, 3, 4, 1),
        (1, 4, 5, 2),
        (2, 5, 3, 0),
    ]
    mesh = bpy.data.meshes.new(f"{name}_ConnectedWedgeMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    bevel = obj.modifiers.new(f"{name}_SoftJoin", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 3
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
eye_names = [
    "V6_Eye_L",
    "V6_Eye_R",
    "V6_Pupil_L",
    "V6_Pupil_R",
    "V6_EyeHighlight_L",
    "V6_EyeHighlight_R",
]
face_names = eye_names + ["V6_MuzzleUnified", "V6_Nose"]
before = {name: bounds(bpy.data.objects[name]) for name in face_names}
preserved_sources = [
    preserve_copy(
        bpy.data.objects[name],
        "Comforting_Cat_V6",
        "A28",
        "undersized_sparse_face_after_head_narrowing",
    )
    for name in face_names
]

for side, sign in (("L", -1.0), ("R", 1.0)):
    for stem in ("V6_Eye", "V6_Pupil", "V6_EyeHighlight"):
        scale_mesh_world(
            bpy.data.objects[f"{stem}_{side}"],
            1.12,
            1.10,
            sign * 0.020,
        )
scale_mesh_world(bpy.data.objects["V6_MuzzleUnified"], 1.24, 1.13)
scale_mesh_world(bpy.data.objects["V6_Nose"], 1.05, 1.05)

old_tuft_names = [
    "V6_CheekTuft_L_0",
    "V6_CheekTuft_L_1",
    "V6_CheekTuft_R_0",
    "V6_CheekTuft_R_1",
]
for name in old_tuft_names:
    old = bpy.data.objects.get(name)
    if old is not None:
        old.parent = None
        old.hide_render = True
        old.hide_set(True)
        old.name = f"{name}_SOURCE_A28"
        old["comforting_cat_preserved_source"] = True
        old["comforting_cat_rejection_reason"] = "detached_side_plate_tuft"
        preserved_sources.append(old.name)

fur_material = head.data.materials[0]
created_tufts: list[bpy.types.Object] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    created_tufts.append(
        cheek_wedge(
            f"V6_CheekTuft_{side}_0",
            [
                (sign * 0.600, 2.835),
                (sign * 0.795, 2.730),
                (sign * 0.600, 2.655),
            ],
            fur_material,
        )
    )
    created_tufts.append(
        cheek_wedge(
            f"V6_CheekTuft_{side}_1",
            [
                (sign * 0.600, 2.690),
                (sign * 0.845, 2.570),
                (sign * 0.585, 2.505),
            ],
            fur_material,
        )
    )

bpy.context.view_layer.update()
after = {name: bounds(bpy.data.objects[name]) for name in face_names}
after["tufts"] = {obj.name: bounds(obj) for obj in created_tufts}
head_width = bounds(head)["dimensions"][0]
metrics = {
    "single_eye_width_over_head_width": round(
        after["V6_Eye_L"]["dimensions"][0] / head_width, 5
    ),
    "muzzle_width_over_head_width": round(
        after["V6_MuzzleUnified"]["dimensions"][0] / head_width, 5
    ),
    "tuft_tip_over_head_half_width": round(0.845 / (head_width * 0.5), 5),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FaceReadabilityTufts_A28"
scene["comforting_cat_v6_stage"] = "FACE_READABILITY_TUFTS"
scene["comforting_cat_v6_attempt"] = 28
scene["comforting_cat_v6_dominant_defect"] = "undersized_sparse_toy_face"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FACE_READABILITY_TUFTS",
    "attempt": 28,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "undersized_sparse_toy_face",
    "preserved_sources": preserved_sources,
    "before": before,
    "after": after,
    "metrics": metrics,
}
finalize_pass(
    asset=ASSET,
    root=root,
    scene=scene,
    final_blend=FINAL_BLEND,
    glb_path=GLB_PATH,
    render_dir=RENDER_DIR,
    report_dir=REPORT_DIR,
    scene_qa_path=SCENE_QA_PATH,
    report=report,
)
