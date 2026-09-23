"""Geometry-only v4 pass for the comforting cat's head and face.

Dominant defect addressed: the v3 face reads as a smooth mascot ball rather
than the soft, cheek-led kitten in the supplied turnaround. This pass keeps all
v3 materials, clothing, lighting and body geometry unchanged.
"""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v4_face_geometry_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
WORKING_BLEND = (BLEND_DIR / "comforting_cat_v4_face_geometry_working.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
REFERENCE_PATH = (WORKBENCH / "references" / "comforting_cat_front_target.png").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()


def assert_under(path: Path, root: Path) -> None:
    path.relative_to(root)


for path in (
    WORKING_BLEND,
    FINAL_BLEND,
    GLB_PATH,
    REFERENCE_PATH,
    SCENE_QA_PATH,
    RENDER_DIR,
    REPORT_DIR,
    CHECKPOINT_DIR,
):
    assert_under(path, WORKBENCH)
for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

if Path(bpy.data.filepath).resolve() != WORKING_BLEND:
    raise RuntimeError(
        f"Open the initialized v4 working file first. Current: {bpy.data.filepath}"
    )
scene = bpy.context.scene
if scene.get("comforting_cat_v4_geometry_applied"):
    raise RuntimeError("The v4 face geometry pass has already been applied.")

required = [
    "Cat_Root",
    "Cat_Head",
    "Cat_Head_Mesh",
    "Cat_Head_FurStrands",
    "Cat_Ear_L",
    "Cat_Ear_R",
    "Cat_InnerEar_L",
    "Cat_InnerEar_R",
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Iris_L",
    "Cat_Iris_R",
    "Cat_Pupil_L",
    "Cat_Pupil_R",
    "Cat_EyeHighlight_L",
    "Cat_EyeHighlight_R",
    "Cat_Muzzle_L",
    "Cat_Muzzle_R",
    "CAT_RenderCamera",
]
missing = [name for name in required if name not in bpy.data.objects]
if missing:
    raise RuntimeError(f"Missing required v3 nodes: {missing}")

pre_geometry_checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v4_pre_face_geometry.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(pre_geometry_checkpoint))


def set_world_location(obj: bpy.types.Object, location: tuple[float, float, float]) -> None:
    matrix = obj.matrix_world.copy()
    matrix.translation = Vector(location)
    obj.matrix_world = matrix


def apply_scale(obj: bpy.types.Object, factors: tuple[float, float, float]) -> None:
    obj.scale = tuple(obj.scale[index] * factors[index] for index in range(3))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def move_world(obj: bpy.types.Object, offset: tuple[float, float, float]) -> None:
    set_world_location(
        obj,
        tuple(obj.matrix_world.translation[index] + offset[index] for index in range(3)),
    )


# GEOMETRY attempt 02: reshape only the skull/face family. Attempt 01 used
# separate cheek wedges and was rejected because they looked attached.
head = bpy.data.objects["Cat_Head_Mesh"]
z_extent = max(abs(vertex.co.z) for vertex in head.data.vertices)
for vertex in head.data.vertices:
    normalized_z = vertex.co.z / max(z_extent, 1e-6)
    lower_cheek = math.exp(-((normalized_z + 0.24) / 0.34) ** 2)
    upper_tuft = math.exp(-((normalized_z + 0.06) / 0.075) ** 2)
    lower_tuft = math.exp(-((normalized_z + 0.31) / 0.085) ** 2)
    crown = max(0.0, (normalized_z - 0.18) / 0.82)
    front_weight = 0.72 + 0.28 * max(0.0, min(1.0, -vertex.co.y / 0.60))
    vertex.co.x *= (
        1.0
        + 0.055 * lower_cheek
        + front_weight * (0.038 * upper_tuft + 0.030 * lower_tuft)
        - 0.085 * crown
    )
    vertex.co.z *= 0.965
    if vertex.co.y < 0.0:
        vertex.co.y *= 0.965
head.data.update()
move_world(head, (0.0, 0.0, -0.012))

for side, suffix in ((-1.0, "L"), (1.0, "R")):
    ear = bpy.data.objects[f"Cat_Ear_{suffix}"]
    inner_ear = bpy.data.objects[f"Cat_InnerEar_{suffix}"]
    apply_scale(ear, (1.14, 1.04, 0.84))
    apply_scale(inner_ear, (0.91, 1.0, 0.74))
    set_world_location(ear, (side * 0.59, -0.01, 3.59))
    set_world_location(inner_ear, (side * 0.59, -0.135, 3.57))
    ear.rotation_euler.z += side * -0.10
    inner_ear.rotation_euler.z += side * -0.10

    eye = bpy.data.objects[f"Cat_Eye_{suffix}"]
    iris = bpy.data.objects[f"Cat_Iris_{suffix}"]
    pupil = bpy.data.objects[f"Cat_Pupil_{suffix}"]
    highlight = bpy.data.objects[f"Cat_EyeHighlight_{suffix}"]
    apply_scale(eye, (1.42, 1.06, 1.30))
    apply_scale(iris, (1.62, 1.04, 1.48))
    apply_scale(pupil, (1.27, 1.03, 1.18))
    apply_scale(highlight, (1.55, 1.05, 1.55))
    set_world_location(eye, (side * 0.275, -0.650, 3.145))
    set_world_location(iris, (side * 0.275, -0.690, 3.145))
    set_world_location(pupil, (side * 0.275, -0.716, 3.145))
    set_world_location(highlight, (side * 0.235, -0.732, 3.235))

    muzzle = bpy.data.objects[f"Cat_Muzzle_{suffix}"]
    apply_scale(muzzle, (1.16, 1.06, 1.10))
    set_world_location(muzzle, (side * 0.145, -0.700, 2.855))

# Brows need a little breathing room above the larger eye geometry.
move_world(bpy.data.objects["Cat_Eyebrow_L"], (0.0, -0.012, 0.045))
move_world(bpy.data.objects["Cat_Eyebrow_R"], (0.0, -0.012, 0.045))

scene.name = "Comforting_Cat_V4_FaceGeometry"
scene["comforting_cat_v4_stage"] = "GEOMETRY"
scene["comforting_cat_v4_geometry_attempt"] = 2
scene["comforting_cat_v4_geometry_applied"] = True
scene["comforting_cat_v4_do_not_change"] = json.dumps(
    [
        "body proportions",
        "robe and scarf topology",
        "satchel placement",
        "materials",
        "lighting",
    ]
)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def set_camera(
    camera: bpy.types.Object,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    ortho_scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    look_at(camera, target)


def render_to(path: Path, camera: bpy.types.Object) -> None:
    assert_under(path.resolve(), WORKBENCH)
    scene.camera = camera
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
ground = bpy.data.objects.get("Cat_RenderGround")
clay = bpy.data.materials.get("CAT_QAClay")
if clay is None:
    clay = bpy.data.materials.new("CAT_QAClay")
    clay.use_nodes = True
    clay.diffuse_color = (0.48, 0.39, 0.30, 1.0)
    principled = clay.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = (0.48, 0.39, 0.30, 1.0)
        principled.inputs["Roughness"].default_value = 0.96

original_materials: dict[str, list[bpy.types.Material]] = {}
for obj in export_objects:
    if obj.type == "MESH":
        original_materials[obj.name] = list(obj.data.materials)
        obj.data.materials.clear()
        obj.data.materials.append(clay)
set_camera(camera, (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_to(RENDER_DIR / f"{ASSET}_01_geometry_front.png", camera)

for obj in export_objects:
    if obj.type == "MESH":
        obj.data.materials.clear()
        for material in original_materials[obj.name]:
            obj.data.materials.append(material)

set_camera(camera, (0.0, -8.6, 3.15), (0.0, -0.04, 2.08), 4.75)
render_to(RENDER_DIR / f"{ASSET}_02_material_front.png", camera)
set_camera(camera, (4.0, -7.4, 3.45), (0.0, -0.02, 2.00), 4.85)
render_to(RENDER_DIR / f"{ASSET}_03_front_3q.png", camera)
set_camera(camera, (8.4, -0.35, 3.15), (0.0, 0.00, 1.95), 4.85)
render_to(RENDER_DIR / f"{ASSET}_04_side.png", camera)
set_camera(camera, (0.0, 8.4, 3.15), (0.0, 0.04, 1.95), 4.85)
render_to(RENDER_DIR / f"{ASSET}_05_back.png", camera)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_render = False
    obj.hide_viewport = False
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


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[index] for point in points) for index in range(3))),
        Vector(tuple(max(point[index] for point in points) for index in range(3))),
    )


def overlap(a_name: str, b_name: str) -> tuple[list[float], bool]:
    a_min, a_max = world_bounds(bpy.data.objects[a_name])
    b_min, b_max = world_bounds(bpy.data.objects[b_name])
    extent = [
        max(0.0, min(a_max[index], b_max[index]) - max(a_min[index], b_min[index]))
        for index in range(3)
    ]
    return extent, all(value > 0.0 for value in extent)


contact_pairs = [
    ("Cat_Head_Mesh", "Cat_Body"),
    ("Cat_Ear_L", "Cat_Head_Mesh"),
    ("Cat_Ear_R", "Cat_Head_Mesh"),
    ("Cat_Eye_L", "Cat_Head_Mesh"),
    ("Cat_Eye_R", "Cat_Head_Mesh"),
    ("Cat_BlueRobe", "Cat_Body"),
    ("Cat_ScarfWrap", "Cat_Head_Mesh"),
    ("Cat_Arm_L", "Cat_Sleeve_L"),
    ("Cat_Arm_R", "Cat_Sleeve_R"),
    ("Cat_Foot_L", "Cat_Leg_L"),
    ("Cat_Foot_R", "Cat_Leg_R"),
    ("Cat_Tail_Base", "Cat_Body"),
    ("Cat_SatchelBag", "Cat_SatchelStrap"),
]
contacts = []
for a_name, b_name in contact_pairs:
    extent, passes = overlap(a_name, b_name)
    contacts.append(
        {
            "a": a_name,
            "b": b_name,
            "type": "OVERLAPS",
            "overlap_extent": [round(value, 5) for value in extent],
            "passes": passes,
        }
    )

triangle_count = 0
mesh_objects = []
for obj in export_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangles = sum(max(0, len(polygon.vertices) - 2) for polygon in mesh.polygons)
    triangle_count += triangles
    minimum, maximum = world_bounds(obj)
    mesh_objects.append(
        {
            "name": obj.name,
            "triangles": triangles,
            "bounds_min": [round(value, 5) for value in minimum],
            "bounds_max": [round(value, 5) for value in maximum],
        }
    )
    evaluated.to_mesh_clear()

external_images = [
    {"name": image.name, "filepath": image.filepath}
    for image in bpy.data.images
    if image.source == "FILE"
]
image_texture_nodes = [
    f"{material.name}/{node.name}"
    for material in bpy.data.materials
    if material.use_nodes
    for node in material.node_tree.nodes
    if node.bl_idname == "ShaderNodeTexImage"
]
forbidden_tokens = ("reference", "relief", "billboard", "imageplane", "projection")
forbidden_scene_objects = [
    obj.name
    for obj in bpy.data.objects
    if any(token in obj.name.lower() for token in forbidden_tokens)
]
errors = []
warnings = []
if forbidden_scene_objects:
    errors.append(f"Forbidden reference-like objects: {forbidden_scene_objects}")
if external_images:
    errors.append(f"External file images loaded: {external_images}")
if image_texture_nodes:
    errors.append(f"Image texture nodes found: {image_texture_nodes}")
failed_contacts = [f"{item['a']} / {item['b']}" for item in contacts if not item["passes"]]
if failed_contacts:
    errors.append(f"Required contacts failed: {failed_contacts}")
if triangle_count > 100_000:
    warnings.append(f"Triangle count {triangle_count} exceeds 100000 hero target")
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
errors.extend(structural_qa["errors"])
warnings.extend(structural_qa["warnings"])

part_ids = [
    "Cat_Head_Mesh",
    "Cat_Ear_L",
    "Cat_Ear_R",
    "Cat_Eye_L",
    "Cat_Eye_R",
    "Cat_Muzzle_L",
    "Cat_Muzzle_R",
    "Cat_Body",
    "Cat_BlueRobe",
    "Cat_ScarfWrap",
    "Cat_SatchelBag",
]
scene_graph = {
    "schema_version": "1.0",
    "goal": "Improve the v3 kitten face silhouette without changing body, clothing, materials or lighting.",
    "mode": "TRUE_360",
    "units": "METERS",
    "parts": [
        {
            "id": name,
            "name": name,
            "representation": "MESH",
            "dimensions": [
                max(0.0001, round(float(value), 5))
                for value in bpy.data.objects[name].dimensions
            ],
            "material_group": (
                bpy.data.objects[name].data.materials[0].name
                if bpy.data.objects[name].data.materials
                else "none"
            ),
            "source_confidence": 0.82 if name.startswith("Cat_Head") else 0.72,
            "notes": "Inherited from v3 unless named as a v4 cheek tuft.",
        }
        for name in part_ids
    ],
    "relations": [
        {
            "a": item["a"],
            "type": "OVERLAPS",
            "b": item["b"],
            "minimum_overlap": 0.0001,
            "tolerance": 0.004,
        }
        for item in contacts
    ],
    "camera": {
        "type": "ORTHOGRAPHIC",
        "review_views": ["front", "front_3q", "side", "back"],
        "front_ortho_scale": 4.75,
    },
    "acceptance": {
        "dominant_defect": "head_and_face_proportions",
        "requirements": [
            "eyes carry substantially more visual weight than v3",
            "ears are shorter and wider",
            "cheek silhouette reads as a single soft feline volume from front and three-quarter",
            "all expected face/head contacts pass",
            "no image plane or texture projection exists",
        ],
        "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
    },
}
(REPORT_DIR / f"{ASSET}_scene_graph.json").write_text(
    json.dumps(scene_graph, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

report = {
    "asset": ASSET,
    "blender_version": ".".join(map(str, bpy.app.version)),
    "stage": "GEOMETRY",
    "attempt": 2,
    "target_representation": "TRUE_360",
    "source_blend": str(WORKING_BLEND),
    "checkpoint": str(pre_geometry_checkpoint),
    "dominant_defect": "head_and_face_proportions",
    "do_not_change": json.loads(scene["comforting_cat_v4_do_not_change"]),
    "triangles": triangle_count,
    "mesh_objects": mesh_objects,
    "exportable_objects": len(export_objects),
    "contacts": contacts,
    "reference_integrity": {
        "forbidden_scene_objects": forbidden_scene_objects,
        "external_images": external_images,
        "image_texture_nodes": image_texture_nodes,
        "passed": not forbidden_scene_objects and not external_images and not image_texture_nodes,
    },
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "geometry_front": str(RENDER_DIR / f"{ASSET}_01_geometry_front.png"),
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    },
    "assumptions": [
        "front and three-quarter views are the primary likeness tests",
        "v3 remains the immutable source and rollback checkpoint",
        "hidden-side fur and cloth construction remain inferred from the turnaround",
    ],
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V4_FACE_GEOMETRY=" + json.dumps(report, ensure_ascii=False))
