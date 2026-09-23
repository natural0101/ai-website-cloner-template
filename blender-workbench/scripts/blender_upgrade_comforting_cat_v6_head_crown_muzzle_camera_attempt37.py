"""Camera-gated crown, muzzle integration, and whisker rebuild."""

from __future__ import annotations

import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v6_head_crown_muzzle_camera_attempt37"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_toe_crease_seated_attempt36.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")
checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_head_crown_muzzle_camera_attempt37.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def interpolate_knots(value: float, knots: list[tuple[float, float]]) -> float:
    if value <= knots[0][0]:
        return knots[0][1]
    if value >= knots[-1][0]:
        return knots[-1][1]
    for (x0, y0), (x1, y1) in zip(knots, knots[1:]):
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            t = t * t * (3.0 - 2.0 * t)
            return y0 * (1.0 - t) + y1 * t
    return 1.0


def fit_mesh_world(
    obj: bpy.types.Object,
    center: Vector,
    dimensions: Vector,
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
    inverse = obj.matrix_world.inverted()
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        offset = world - old_center
        offset.x *= dimensions.x / old_dimensions.x
        offset.y *= dimensions.y / old_dimensions.y
        offset.z *= dimensions.z / old_dimensions.z
        vertex.co = inverse @ (center + offset)
    obj.data.update()


def shift_curve_world(obj: bpy.types.Object, delta: Vector) -> None:
    inverse = obj.matrix_world.inverted()
    for spline in obj.data.splines:
        for point in spline.bezier_points:
            point.co = inverse @ (obj.matrix_world @ point.co + delta)
            point.handle_left = inverse @ (
                obj.matrix_world @ point.handle_left + delta
            )
            point.handle_right = inverse @ (
                obj.matrix_world @ point.handle_right + delta
            )
    bpy.context.view_layer.update()


def whisker_curve(
    name: str,
    coordinates: list[tuple[float, float, float]],
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = 0.003
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


def band_half_width(
    obj: bpy.types.Object,
    z_min: float,
    z_max: float,
) -> float:
    values = []
    for vertex in obj.data.vertices:
        world = obj.matrix_world @ vertex.co
        if z_min <= world.z <= z_max:
            values.append(abs(world.x))
    return max(values, default=0.0)


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
muzzles = [bpy.data.objects["V6_Muzzle_L"], bpy.data.objects["V6_Muzzle_R"]]
nose = bpy.data.objects["V6_Nose"]
mouth = bpy.data.objects["V6_Mouth"]
philtrum = bpy.data.objects["V6_Philtrum"]
ear_names = ["V6_Ear_L", "V6_Ear_R", "V6_InnerEar_L", "V6_InnerEar_R"]
affected = [head, nose, mouth, philtrum] + muzzles + [
    bpy.data.objects[name] for name in ear_names
]
before = {obj.name: bounds(obj) for obj in affected}
preserved_sources = [
    preserve_copy(
        obj,
        "Comforting_Cat_V6",
        "A37",
        "camera_space_narrow_crown_and_stuck_on_muzzle",
    )
    for obj in affected
]

# Carry the maximum width upward into crown/temples while freezing eyes.
crown_profile = [
    (2.26, 1.00),
    (2.50, 0.99),
    (2.62, 1.00),
    (2.75, 1.02),
    (2.90, 1.10),
    (3.05, 1.18),
    (3.20, 1.21),
    (3.38, 1.09),
]
head_inverse = head.matrix_world.inverted()
for vertex in head.data.vertices:
    world = head.matrix_world @ vertex.co
    world.x *= interpolate_knots(world.z, crown_profile)
    vertex.co = head_inverse @ world
head.data.update()

# Keep ear volumes seated on the widened crown by moving them outward together.
for side, sign in (("L", -1.0), ("R", 1.0)):
    for stem in ("V6_Ear", "V6_InnerEar"):
        obj = bpy.data.objects[f"{stem}_{side}"]
        inverse = obj.matrix_world.inverted()
        for vertex in obj.data.vertices:
            world = obj.matrix_world @ vertex.co
            world.x += sign * 0.030
            vertex.co = inverse @ world
        obj.data.update()

# Wider, shallower cheek puffs sit mostly inside the orange face volume.
for side, sign in (("L", -1.0), ("R", 1.0)):
    fit_mesh_world(
        bpy.data.objects[f"V6_Muzzle_{side}"],
        Vector((sign * 0.140, -0.490, 2.550)),
        Vector((0.390, 0.180, 0.240)),
    )
fit_mesh_world(nose, Vector((0.0, -0.595, 2.596)), Vector((0.080, 0.052, 0.078)))
shift_curve_world(mouth, Vector((0.0, 0.040, 0.0)))
shift_curve_world(philtrum, Vector((0.0, 0.040, 0.0)))

whisker_material = bpy.data.objects["V6_Muzzle_L"].data.materials[0]
whisker_names: list[str] = []
for side, sign in (("L", -1.0), ("R", 1.0)):
    specs = [
        [
            (sign * 0.225, -0.588, 2.585),
            (sign * 0.390, -0.585, 2.615),
            (sign * 0.570, -0.548, 2.650),
        ],
        [
            (sign * 0.240, -0.592, 2.545),
            (sign * 0.410, -0.588, 2.548),
            (sign * 0.595, -0.552, 2.555),
        ],
        [
            (sign * 0.225, -0.588, 2.505),
            (sign * 0.390, -0.582, 2.480),
            (sign * 0.565, -0.545, 2.455),
        ],
    ]
    for index, coordinates in enumerate(specs):
        name = f"V6_Whisker_{side}_{index}"
        whisker_curve(name, coordinates, whisker_material)
        whisker_names.append(name)

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in affected}
head_width = bounds(head)["dimensions"][0]
cheek_half = band_half_width(head, 2.55, 2.75)
crown_half = band_half_width(head, 3.03, 3.18)
eye_width = bounds(bpy.data.objects["V6_Eye_L"])["dimensions"][0]
muzzle_min = min(bounds(obj)["min"][0] for obj in muzzles)
muzzle_max = max(bounds(obj)["max"][0] for obj in muzzles)
metrics = {
    "mesh_cheek_over_crown_width": round(cheek_half / crown_half, 5),
    "head_width": head_width,
    "single_eye_width_over_head_width": round(eye_width / head_width, 5),
    "combined_muzzle_width_over_head_width": round(
        (muzzle_max - muzzle_min) / head_width, 5
    ),
    "whisker_count": len(whisker_names),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_HeadCrownMuzzleCamera_A37"
scene["comforting_cat_v6_stage"] = "HEAD_CROWN_MUZZLE_CAMERA"
scene["comforting_cat_v6_attempt"] = 37
scene["comforting_cat_v6_dominant_defect"] = "camera_space_narrow_crown_and_stuck_on_muzzle"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "HEAD_CROWN_MUZZLE_CAMERA",
    "attempt": 37,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "camera_space_narrow_crown_and_stuck_on_muzzle",
    "crown_profile": crown_profile,
    "preserved_sources": preserved_sources,
    "whiskers": whisker_names,
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
