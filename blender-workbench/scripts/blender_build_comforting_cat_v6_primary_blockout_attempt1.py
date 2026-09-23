"""Build a separate v6 cat from the target's primary silhouette and proportions."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v6_primary_blockout_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_lower_robe_hem_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected stable source {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_primary_blockout_attempt1.blend"
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


def material_from_object(
    object_name: str,
    fallback_name: str,
    color: tuple[float, float, float, float],
) -> bpy.types.Material:
    obj = bpy.data.objects.get(object_name)
    if obj is not None and obj.type == "MESH" and obj.data.materials:
        return obj.data.materials[0]
    material = bpy.data.materials.get(fallback_name)
    if material is None:
        material = bpy.data.materials.new(fallback_name)
    material.diffuse_color = color
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = 0.82
    return material


orange = material_from_object("Cat_Head_Mesh", "V6_OrangeFur", (0.62, 0.30, 0.11, 1.0))
cream = material_from_object("Cat_Muzzle_L", "V6_CreamFur", (0.82, 0.70, 0.50, 1.0))
blue = material_from_object("Cat_BlueRobe", "V6_WeatheredBlue", (0.12, 0.24, 0.28, 1.0))
gray = material_from_object("Cat_RobeFrontInset", "V6_GrayLinen", (0.34, 0.37, 0.35, 1.0))
brown = material_from_object("Cat_Satchel", "V6_LeatherBrown", (0.20, 0.09, 0.035, 1.0))
eye_mat = material_from_object("Cat_Eye_L", "V6_EyeBrown", (0.08, 0.035, 0.015, 1.0))
pink = material_from_object("Cat_Nose", "V6_NosePink", (0.72, 0.35, 0.37, 1.0))

old_root = bpy.data.objects["Cat_Root"]
for obj in descendants(old_root):
    obj.hide_render = True
    obj.hide_set(True)
old_root["comforting_cat_preserved_source"] = True
old_root["comforting_cat_rejection_reason"] = "incremental_v5_failed_primary_likeness"

collection = bpy.data.collections.new("Comforting_Cat_V6")
bpy.context.scene.collection.children.link(collection)
root = bpy.data.objects.new("CatV6_Root", None)
collection.objects.link(root)
root["comforting_cat_target_mode"] = "TRUE_360"
root["comforting_cat_reference"] = str(
    WORKBENCH / "references" / "comforting_cat_front_target.png"
)


def link_to_v6(obj: bpy.types.Object) -> None:
    for linked in list(obj.users_collection):
        linked.objects.unlink(obj)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()


def ellipsoid(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    segments: int = 48,
    rings: int = 32,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(value * 0.5 for value in dimensions)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_to_v6(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


head = ellipsoid(
    "V6_Head",
    (0.0, 0.0, 2.82),
    (1.48, 1.02, 1.06),
    orange,
    segments=64,
    rings=48,
)
head_inverse = head.matrix_world.inverted()
head_center_z = 2.82
for vertex in head.data.vertices:
    point = head.matrix_world @ vertex.co
    zn = (point.z - head_center_z) / 0.52
    cheek = math.exp(-((zn + 0.20) / 0.32) ** 2)
    crown = max(0.0, (zn - 0.20) / 0.80)
    chin = max(0.0, (-zn - 0.28) / 0.72)
    point.x *= 1.0 + 0.095 * cheek - 0.12 * crown - 0.14 * chin
    point.y *= 1.0 - 0.05 * crown - 0.08 * chin
    vertex.co = head_inverse @ point
head.data.update()


def prism(
    name: str,
    front_points: list[tuple[float, float]],
    y_front: float,
    y_back: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    vertices = [(x, y_front, z) for x, z in front_points] + [
        (x, y_back, z) for x, z in front_points
    ]
    count = len(front_points)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, count + index, count + next_index, next_index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.matrix_world = Matrix.Identity(4)
    obj.data.materials.append(material)
    return obj


for side, sign in (("L", -1.0), ("R", 1.0)):
    ear_points = [
        (sign * 0.66, 3.16),
        (sign * 0.25, 3.18),
        (sign * 0.47, 3.60),
    ]
    ear = prism(f"V6_Ear_{side}", ear_points, -0.20, 0.18, orange)
    inner_points = [
        (sign * 0.57, 3.21),
        (sign * 0.33, 3.22),
        (sign * 0.47, 3.51),
    ]
    prism(f"V6_InnerEar_{side}", inner_points, -0.215, -0.225, pink)

for side, sign in (("L", -1.0), ("R", 1.0)):
    tuft_specs = [
        (2.76, 0.11, 0.10),
        (2.64, 0.15, 0.09),
    ]
    for index, (z_value, reach, half_height) in enumerate(tuft_specs):
        base_x = sign * 0.68
        tip_x = sign * (0.67 + reach)
        points = [
            (base_x, z_value + half_height),
            (tip_x, z_value),
            (base_x, z_value - half_height),
        ]
        prism(f"V6_CheekTuft_{side}_{index}", points, -0.10, 0.16, orange)


def robe_mesh() -> bpy.types.Object:
    profile = [
        (0.56, 0.56, 0.37),
        (0.74, 0.59, 0.39),
        (1.05, 0.62, 0.41),
        (1.30, 0.62, 0.42),
        (1.70, 0.59, 0.40),
        (2.08, 0.53, 0.36),
        (2.25, 0.49, 0.34),
    ]
    segments = 64
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for z_value, radius_x, radius_y in profile:
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append(
                (
                    radius_x * math.cos(angle),
                    0.04 + radius_y * math.sin(angle),
                    z_value,
                )
            )
    for ring in range(len(profile) - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            a = ring * segments + index
            b = ring * segments + next_index
            c = (ring + 1) * segments + next_index
            d = (ring + 1) * segments + index
            faces.append((a, b, c, d))
    bottom_center = len(vertices)
    vertices.append((0.0, 0.04, profile[0][0]))
    top_center = len(vertices)
    vertices.append((0.0, 0.04, profile[-1][0]))
    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append((bottom_center, next_index, index))
        top = (len(profile) - 1) * segments
        faces.append((top_center, top + index, top + next_index))
    mesh = bpy.data.meshes.new("V6_Robe_PearMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("V6_Robe", mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(blue)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    bevel = obj.modifiers.new("V6_RobeSoftHem", "BEVEL")
    bevel.width = 0.015
    bevel.segments = 2
    return obj


robe = robe_mesh()


def curved_front_panel() -> bpy.types.Object:
    levels = [
        (2.05, 0.38),
        (1.58, 0.37),
        (1.05, 0.34),
        (0.60, 0.31),
    ]
    columns = [-1.0, -0.5, 0.0, 0.5, 1.0]
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for z_value, half_width in levels:
        for column in columns:
            x = half_width * column
            edge = abs(column)
            y = -0.405 - 0.075 * (1.0 - edge * edge)
            vertices.append((x, y, z_value))
    width = len(columns)
    for row in range(len(levels) - 1):
        for column in range(width - 1):
            a = row * width + column
            b = a + 1
            c = (row + 1) * width + column + 1
            d = (row + 1) * width + column
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new("V6_FrontTunic_CurvedMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new("V6_FrontTunic", mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(gray)
    solidify = obj.modifiers.new("V6_FrontTunicThickness", "SOLIDIFY")
    solidify.thickness = 0.025
    solidify.offset = 0.0
    bevel = obj.modifiers.new("V6_FrontTunicSoftEdge", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 2
    return obj


front_tunic = curved_front_panel()


def torus_band(
    name: str,
    center_z: float,
    scale_x: float,
    scale_y: float,
    tilt: float,
) -> bpy.types.Object:
    major_segments = 64
    minor_segments = 20
    major_radius = 0.32
    minor_radius = 0.18
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for major_index in range(major_segments):
        u = math.tau * major_index / major_segments
        for minor_index in range(minor_segments):
            v = math.tau * minor_index / minor_segments
            radial = major_radius + minor_radius * math.cos(v)
            vertices.append(
                (
                    scale_x * radial * math.cos(u),
                    scale_y * radial * math.sin(u),
                    center_z
                    + minor_radius * math.sin(v)
                    + tilt * math.sin(u + 0.4),
                )
            )
    for major_index in range(major_segments):
        next_major = (major_index + 1) % major_segments
        for minor_index in range(minor_segments):
            next_minor = (minor_index + 1) % minor_segments
            a = major_index * minor_segments + minor_index
            b = next_major * minor_segments + minor_index
            c = next_major * minor_segments + next_minor
            d = major_index * minor_segments + next_minor
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(blue)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


scarf_upper = torus_band("V6_ScarfWrap_Upper", 2.36, 1.20, 0.88, 0.025)
scarf_lower = torus_band("V6_ScarfWrap_Lower", 2.18, 1.16, 0.92, -0.022)
front_scarf = prism(
    "V6_Scarf_FrontDrape",
    [
        (-0.54, 2.36),
        (-0.14, 2.43),
        (0.54, 2.31),
        (0.43, 2.08),
        (0.10, 1.72),
        (-0.28, 1.86),
        (-0.49, 2.08),
    ],
    -0.49,
    -0.41,
    blue,
)
back_scarf = prism(
    "V6_Scarf_BackDrape",
    [(-0.55, 2.31), (0.55, 2.31), (0.43, 2.08), (0.05, 1.78), (-0.42, 2.02)],
    0.46,
    0.38,
    blue,
)
for obj in (front_scarf, back_scarf):
    bevel = obj.modifiers.new("V6_ScarfDrapeSoftEdge", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 3

for side, sign in (("L", -1.0), ("R", 1.0)):
    ellipsoid(
        f"V6_Sleeve_{side}",
        (sign * 0.58, -0.03, 1.72),
        (0.30, 0.34, 0.44),
        blue,
        rotation=(0.0, sign * 0.20, 0.0),
    )
    ellipsoid(
        f"V6_Arm_{side}",
        (sign * 0.61, -0.18, 1.36),
        (0.22, 0.24, 0.55),
        orange,
        rotation=(0.0, sign * 0.10, 0.0),
    )
    ellipsoid(
        f"V6_Paw_{side}",
        (sign * 0.61, -0.20, 1.07),
        (0.22, 0.24, 0.25),
        orange,
    )
    ellipsoid(
        f"V6_Leg_{side}",
        (sign * 0.21, 0.0, 0.34),
        (0.26, 0.30, 0.48),
        orange,
    )
    ellipsoid(
        f"V6_Foot_{side}",
        (sign * 0.22, -0.10, 0.10),
        (0.36, 0.42, 0.18),
        cream,
    )

for side, sign in (("L", -1.0), ("R", 1.0)):
    ellipsoid(
        f"V6_Eye_{side}",
        (sign * 0.27, -0.515, 2.90),
        (0.31, 0.14, 0.36),
        eye_mat,
    )
    ellipsoid(
        f"V6_EyeHighlight_{side}",
        (sign * 0.22, -0.588, 2.99),
        (0.065, 0.035, 0.085),
        cream,
        segments=24,
        rings=16,
    )
    ellipsoid(
        f"V6_Muzzle_{side}",
        (sign * 0.15, -0.535, 2.58),
        (0.34, 0.18, 0.23),
        cream,
    )
ellipsoid("V6_Nose", (0.0, -0.635, 2.64), (0.13, 0.08, 0.10), pink, segments=24, rings=16)


def curve_object(
    name: str,
    points: list[tuple[float, float, float]],
    bevel_depth: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    return obj


curve_object("V6_Eyebrow_L", [(-0.42, -0.585, 3.12), (-0.28, -0.605, 3.20), (-0.12, -0.585, 3.15)], 0.018, brown)
curve_object("V6_Eyebrow_R", [(0.12, -0.585, 3.15), (0.28, -0.605, 3.20), (0.42, -0.585, 3.12)], 0.018, brown)
curve_object("V6_Mouth", [(-0.10, -0.635, 2.50), (0.0, -0.65, 2.46), (0.10, -0.635, 2.50)], 0.010, brown)

satchel = prism(
    "V6_Satchel",
    [(-0.02, 1.43), (0.47, 1.43), (0.47, 0.80), (-0.02, 0.80)],
    -0.58,
    -0.45,
    brown,
)
bevel = satchel.modifiers.new("V6_SatchelSoftEdge", "BEVEL")
bevel.width = 0.035
bevel.segments = 3
curve_object("V6_SatchelStrap", [(-0.46, -0.48, 2.08), (-0.12, -0.55, 1.70), (0.28, -0.58, 1.25)], 0.025, brown)

ellipsoid("V6_TailRoot", (0.48, 0.30, 0.62), (0.42, 0.42, 0.45), orange, rotation=(0.40, 0.30, -0.20))
ellipsoid("V6_TailMid", (0.72, 0.44, 0.47), (0.55, 0.44, 0.42), orange, rotation=(0.20, 0.45, -0.30))
ellipsoid("V6_TailEnd", (0.91, 0.56, 0.43), (0.48, 0.40, 0.38), orange, rotation=(0.10, 0.35, -0.30))
ellipsoid("V6_TailTip", (1.08, 0.62, 0.43), (0.31, 0.34, 0.34), cream, rotation=(0.0, 0.20, -0.25))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_PrimaryBlockout_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v6_stage"] = "PRIMARY_BLOCKOUT"
scene["comforting_cat_v6_attempt"] = 1
scene["comforting_cat_v6_strategy"] = "new_root_from_reference_not_incremental_v5_patch"
scene["comforting_cat_v6_preserved_source"] = old_root.name


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
    "stage": "PRIMARY_BLOCKOUT",
    "attempt": 1,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "strategy": "new_root_from_reference_not_incremental_v5_patch",
    "preserved_source": old_root.name,
    "v6_root": root.name,
    "key_bounds": {
        "head": bounds(head),
        "robe": bounds(robe),
        "front_tunic": bounds(front_tunic),
        "scarf_upper": bounds(scarf_upper),
        "scarf_lower": bounds(scarf_lower),
    },
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
print("COMFORTING_CAT_V6_PRIMARY_BLOCKOUT_A1=" + json.dumps(report, ensure_ascii=False))
