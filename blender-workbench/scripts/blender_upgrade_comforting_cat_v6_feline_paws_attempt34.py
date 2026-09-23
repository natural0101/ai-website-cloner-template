"""Replace slipper feet and pinched legs with warm three-toe feline paws."""

from __future__ import annotations

import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_feline_paws_attempt34"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v6_head_face_feline_rebuild_attempt33.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_feline_paws_attempt34.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def fit_and_yaw_foot(
    obj: bpy.types.Object,
    center: Vector,
    dimensions: Vector,
    yaw_degrees: float,
) -> None:
    obj_bounds = bounds(obj)
    old_center = Vector(
        (
            (obj_bounds["min"][0] + obj_bounds["max"][0]) * 0.5,
            (obj_bounds["min"][1] + obj_bounds["max"][1]) * 0.5,
            (obj_bounds["min"][2] + obj_bounds["max"][2]) * 0.5,
        )
    )
    old_dimensions = Vector(obj_bounds["dimensions"])
    angle = math.radians(yaw_degrees)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        offset = world - old_center
        offset.x *= dimensions.x / old_dimensions.x
        offset.y *= dimensions.y / old_dimensions.y
        offset.z *= dimensions.z / old_dimensions.z
        rotated_x = offset.x * cosine - offset.y * sine
        rotated_y = offset.x * sine + offset.y * cosine
        vertex.co = inverse @ Vector(
            (
                center.x + rotated_x,
                center.y + rotated_y,
                center.z + offset.z,
            )
        )
    obj.data.update()


def tapered_leg(
    name: str,
    sign: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    profile = [
        (0.230, 0.235, 0.125, 0.115),
        (0.290, 0.232, 0.130, 0.120),
        (0.420, 0.224, 0.138, 0.126),
        (0.590, 0.213, 0.146, 0.133),
        (0.720, 0.205, 0.150, 0.135),
    ]
    segments = 32
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for z_value, center_x, radius_x, radius_y in profile:
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append(
                (
                    sign * center_x + radius_x * math.cos(angle),
                    -0.005 + radius_y * math.sin(angle),
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
    vertices.append((sign * profile[0][1], -0.005, profile[0][0]))
    top_center = len(vertices)
    vertices.append((sign * profile[-1][1], -0.005, profile[-1][0]))
    top_ring = (len(profile) - 1) * segments
    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append((bottom_center, next_index, index))
        faces.append((top_center, top_ring + index, top_ring + next_index))
    mesh = bpy.data.meshes.new(f"{name}_TaperedFelineLegMesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    bevel = obj.modifiers.new(f"{name}_SoftTransition", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 2
    return obj


def toe_curve(
    name: str,
    coordinates: list[tuple[float, float, float]],
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 10
    curve.bevel_depth = 0.007
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(coordinates) - 1)
    for point, coordinate in zip(spline.bezier_points, coordinates):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.data.collections["Comforting_Cat_V6"].objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse = root.matrix_world.inverted()
    obj.data.materials.append(material)
    return obj


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
foot_names = ["V6_Foot_L", "V6_Foot_R"]
leg_names = ["V6_Leg_L", "V6_Leg_R"]
before = {
    name: bounds(bpy.data.objects[name]) for name in foot_names + leg_names
}
preserved_sources = [
    preserve_copy(
        bpy.data.objects[name],
        "Comforting_Cat_V6",
        "A34",
        "white_slipper_or_pinched_ankle",
    )
    for name in foot_names + leg_names
]

# Independent warm paw shader with a restrained procedural fur bump.
paw_material = bpy.data.materials.new("V6_WarmFelinePaw_A34")
paw_material.use_nodes = True
paw_material.diffuse_color = (0.64, 0.44, 0.25, 1.0)
paw_material.roughness = 0.78
nodes = paw_material.node_tree.nodes
links = paw_material.node_tree.links
nodes.clear()
output = nodes.new("ShaderNodeOutputMaterial")
principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.inputs["Base Color"].default_value = (0.64, 0.44, 0.25, 1.0)
principled.inputs["Roughness"].default_value = 0.78
principled.inputs["Specular IOR Level"].default_value = 0.22
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 58.0
noise.inputs["Detail"].default_value = 2.0
noise.inputs["Roughness"].default_value = 0.58
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.14
bump.inputs["Distance"].default_value = 0.022
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

for side, sign in (("L", -1.0), ("R", 1.0)):
    foot = bpy.data.objects[f"V6_Foot_{side}"]
    fit_and_yaw_foot(
        foot,
        Vector((sign * 0.255, -0.080, 0.140)),
        Vector((0.420, 0.360, 0.260)),
        -sign * 3.0,
    )
    foot.data.materials.clear()
    foot.data.materials.append(paw_material)

fur_material = head.data.materials[0]
for side, sign in (("L", -1.0), ("R", 1.0)):
    old_leg = bpy.data.objects[f"V6_Leg_{side}"]
    old_leg.parent = None
    old_leg.hide_render = True
    old_leg.hide_set(True)
    old_leg.name = f"V6_Leg_{side}_REPLACED_A34"
    old_leg["comforting_cat_preserved_source"] = True
    old_leg["comforting_cat_rejection_reason"] = "pinched_ellipsoid_ankle"
    preserved_sources.append(old_leg.name)
    tapered_leg(f"V6_Leg_{side}", sign, fur_material)

toe_material = bpy.data.objects["V6_Mouth"].data.materials[0]
toe_names: list[str] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    center_x = sign * 0.255
    for index, offset in enumerate((-0.065, 0.065)):
        x_value = center_x + offset
        name = f"V6_ToeCrease_{side}_{index}"
        toe_curve(
            name,
            [
                (x_value, -0.258, 0.188),
                (x_value - sign * 0.008, -0.269, 0.151),
                (x_value, -0.258, 0.126),
            ],
            toe_material,
        )
        toe_names.append(name)

bpy.context.view_layer.update()
after = {
    name: bounds(bpy.data.objects[name]) for name in foot_names + leg_names
}
left_foot = after["V6_Foot_L"]
right_foot = after["V6_Foot_R"]
inner_gap = right_foot["min"][0] - left_foot["max"][0]
metrics = {
    "inner_foot_gap": round(inner_gap, 5),
    "foot_width_height": round(
        left_foot["dimensions"][0] / left_foot["dimensions"][2], 5
    ),
    "foot_depth_width": round(
        left_foot["dimensions"][1] / left_foot["dimensions"][0], 5
    ),
    "foot_depth_height": round(
        left_foot["dimensions"][1] / left_foot["dimensions"][2], 5
    ),
    "left_min_z": left_foot["min"][2],
    "toe_curve_count": len(toe_names),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_FelinePaws_A34"
scene["comforting_cat_v6_stage"] = "FELINE_PAWS"
scene["comforting_cat_v6_attempt"] = 34
scene["comforting_cat_v6_dominant_defect"] = "white_slippers_and_pinched_ankles"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "FELINE_PAWS",
    "attempt": 34,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "white_slippers_and_pinched_ankles",
    "preserved_sources": preserved_sources,
    "toe_curves": toe_names,
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
