import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_cohesive_hand.blend"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-cohesive-hand-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_finger_spines_report.json"

for path in (BLEND_PATH, HERO_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def require(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required TEAMON object is missing: {name}")
    return obj


def parent_keep_world(obj, parent):
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def world_min_z(obj):
    return min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def world_max_z(obj):
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def make_tube(name, points, radius_w, radius_h, material, collection, parent, sides=8):
    vertices = []
    faces = []
    points = [Vector(point) for point in points]
    world_up = Vector((0.0, 0.0, 1.0))
    for index, point in enumerate(points):
        if index == 0:
            tangent = points[1] - point
        elif index == len(points) - 1:
            tangent = point - points[index - 1]
        else:
            tangent = points[index + 1] - points[index - 1]
        tangent.normalize()
        across = tangent.cross(world_up)
        if across.length < 1e-5:
            across = Vector((0.0, 1.0, 0.0))
        across.normalize()
        vertical = across.cross(tangent).normalized()
        for side in range(sides):
            angle = math.tau * side / sides
            vertices.append(
                point
                + across * (math.cos(angle) * radius_w)
                + vertical * (math.sin(angle) * radius_h)
            )
    for ring in range(len(points) - 1):
        for side in range(sides):
            nxt = (side + 1) % sides
            a = ring * sides + side
            b = ring * sides + nxt
            c = (ring + 1) * sides + nxt
            d = (ring + 1) * sides + side
            faces.append((a, b, c, d))
    faces.append(tuple(range(sides - 1, -1, -1)))
    last = (len(points) - 1) * sides
    faces.append(tuple(last + side for side in range(sides)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj["export"] = True
    obj["role"] = "continuous_low_poly_finger_spine"
    parent_keep_world(obj, parent)
    return obj


output = bpy.data.collections.get("TEAMON_OUTPUT")
hand_root = require("TEAMON_HandRoot")
press_group = require("TEAMON_HandPressGroup")
keycap = require("TEAMON_Keycap")
index_pad = require("TEAMON_Index_ContactPad")
if output is None:
    raise RuntimeError("TEAMON_OUTPUT collection is missing")

for obj in list(bpy.data.objects):
    if obj.name.startswith("TEAMON_") and obj.name.endswith("_MechanicalSpine"):
        bpy.data.objects.remove(obj, do_unlink=True)

hidden_tendons = []
for obj in bpy.data.objects:
    if obj.name.startswith("TEAMON_") and obj.name.endswith("_InnerTendon"):
        obj.hide_render = True
        obj.hide_viewport = True
        obj["remediation_status"] = "replaced_by_low_poly_continuous_spine"
        hidden_tendons.append(obj.name)

core_material = bpy.data.materials.get("TEAMON_Robot_InnerCore_V3")
if core_material is None:
    core_material = bpy.data.materials.new("TEAMON_Robot_InnerCore_V3")
    core_material.use_nodes = True
principled = next(
    (node for node in core_material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
    None,
)
if principled:
    principled.inputs["Base Color"].default_value = (0.16, 0.07, 0.085, 1.0)
    principled.inputs["Metallic"].default_value = 0.38
    principled.inputs["Roughness"].default_value = 0.36


def center(name):
    return require(name).matrix_world.translation.copy()


finger_points = {}
for finger in ("Middle", "Ring", "Pinky", "Thumb"):
    finger_points[finger] = [
        center(f"TEAMON_{finger}_Proximal_Armor"),
        center(f"TEAMON_{finger}_Middle_Armor"),
        center(f"TEAMON_{finger}_Distal_Armor"),
        center(f"TEAMON_{finger}_ContactPad"),
    ]
finger_points["Index"] = [
    center("TEAMON_Index_Proximal_Armor"),
    center("TEAMON_Index_Middle_Armor"),
    center("TEAMON_Index_RecessedPin_02"),
    center("TEAMON_Index_Distal_Armor"),
    center("TEAMON_Index_ContactPad"),
]
radii = {
    "Index": (0.105, 0.078),
    "Middle": (0.115, 0.084),
    "Ring": (0.11, 0.08),
    "Pinky": (0.095, 0.072),
    "Thumb": (0.12, 0.088),
}

new_spines = []
for finger, points in finger_points.items():
    radius_w, radius_h = radii[finger]
    if finger == "Index":
        static_spine = make_tube(
            "TEAMON_Index_Static_MechanicalSpine",
            points[:3],
            radius_w,
            radius_h,
            core_material,
            output,
            hand_root,
        )
        distal_spine = make_tube(
            "TEAMON_Index_Distal_MechanicalSpine",
            points[2:],
            radius_w * 0.88,
            radius_h * 0.88,
            core_material,
            output,
            press_group,
        )
        new_spines.extend((static_spine.name, distal_spine.name))
    else:
        spine = make_tube(
            f"TEAMON_{finger}_MechanicalSpine",
            points,
            radius_w,
            radius_h,
            core_material,
            output,
            hand_root,
        )
        new_spines.append(spine.name)

# Recover manufactured thickness after the previous anti-blob pass while
# keeping every shell visibly flatter than the rejected capsule version.
scales = {
    "TEAMON_Index_ContactPad": (0.92, 0.78, 0.68),
    "TEAMON_Index_Distal_Armor": (1.16, 0.84, 0.82),
    "TEAMON_Index_Middle_Armor": (1.10, 0.86, 0.84),
    "TEAMON_Index_Proximal_Armor": (1.06, 0.88, 0.86),
    "TEAMON_PalmShell": (1.00, 0.90, 0.78),
}
for finger in ("Middle", "Ring", "Pinky"):
    for segment in ("Distal", "Middle", "Proximal"):
        scales[f"TEAMON_{finger}_{segment}_Armor"] = (1.10, 0.86, 0.82)
    scales[f"TEAMON_{finger}_ContactPad"] = (0.90, 0.82, 0.72)
for index, values in enumerate(
    ((1.18, 0.74, 0.65), (1.22, 0.72, 0.65), (1.26, 0.70, 0.65), (1.30, 0.68, 0.65)),
    start=1,
):
    scales[f"TEAMON_KnuckleRidge_{index:02d}"] = values
for name, scale in scales.items():
    require(name).scale = scale

bpy.context.view_layer.update()
gap_before = world_min_z(index_pad) - world_max_z(keycap)
target_overlap = 0.006
hand_matrix = press_group.matrix_world.copy()
hand_matrix.translation.z += -gap_before - target_overlap
press_group.matrix_world = hand_matrix
bpy.context.view_layer.update()
gap_after = world_min_z(index_pad) - world_max_z(keycap)

scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

triangle_count = 0
for obj in bpy.data.objects:
    if obj.type == "MESH" and not obj.hide_render and obj.name.startswith("TEAMON_"):
        obj.data.calc_loop_triangles()
        triangle_count += len(obj.data.loop_triangles)

report = {
    "asset": "TEAMON reference v3 cohesive mechanical hand",
    "blend": str(BLEND_PATH),
    "hero": str(HERO_PATH),
    "hiddenHighPolyTendons": hidden_tendons,
    "newLowPolySpines": new_spines,
    "contactGapBefore": gap_before,
    "contactGapAfter": gap_after,
    "visibleAssetTriangles": triangle_count,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
