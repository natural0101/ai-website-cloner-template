import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v3_hand_refined.blend"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v3-hand-refined-hero.png"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v3_hand_refinement_report.json"

for path in (BLEND_PATH, HERO_PATH, REPORT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


def require(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required TEAMON object is missing: {name}")
    return obj


def world_min_z(obj):
    return min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def world_max_z(obj):
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


scales = {
    "TEAMON_Index_ContactPad": (0.90, 0.72, 0.58),
    "TEAMON_Index_Distal_Armor": (1.18, 0.78, 0.72),
    "TEAMON_Index_Middle_Armor": (1.12, 0.82, 0.76),
    "TEAMON_Index_Proximal_Armor": (1.08, 0.84, 0.78),
    "TEAMON_PalmShell": (1.00, 0.86, 0.70),
    "TEAMON_KnuckleRidge_01": (1.20, 0.70, 0.55),
    "TEAMON_KnuckleRidge_02": (1.25, 0.68, 0.55),
    "TEAMON_KnuckleRidge_03": (1.30, 0.66, 0.55),
    "TEAMON_KnuckleRidge_04": (1.35, 0.64, 0.55),
}

for finger in ("Middle", "Ring", "Pinky"):
    for segment in ("Distal", "Middle", "Proximal"):
        scales[f"TEAMON_{finger}_{segment}_Armor"] = (1.12, 0.80, 0.74)
    scales[f"TEAMON_{finger}_ContactPad"] = (0.88, 0.76, 0.62)

for name, scale in scales.items():
    require(name).scale = scale

bpy.context.view_layer.update()

keycap = require("TEAMON_Keycap")
pad = require("TEAMON_Index_ContactPad")
hand_press_group = require("TEAMON_HandPressGroup")
gap_before = world_min_z(pad) - world_max_z(keycap)
target_overlap = 0.008
world_shift = -gap_before - target_overlap
hand_matrix = hand_press_group.matrix_world.copy()
hand_matrix.translation.z += world_shift
hand_press_group.matrix_world = hand_matrix
bpy.context.view_layer.update()
gap_after = world_min_z(pad) - world_max_z(keycap)

material = bpy.data.materials.get("TEAMON_Robot_White_V3")
if material and material.use_nodes:
    principled = next(
        (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
        None,
    )
    if principled:
        values = {
            "Base Color": (0.78, 0.81, 0.86, 1.0),
            "Roughness": 0.36,
            "Coat Weight": 0.08,
            "Coat Roughness": 0.18,
        }
        for socket_name, value in values.items():
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value

scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

report = {
    "asset": "TEAMON reference v3 mechanical hand refinement",
    "blend": str(BLEND_PATH),
    "hero": str(HERO_PATH),
    "scaledObjects": scales,
    "contactGapBefore": gap_before,
    "contactGapAfter": gap_after,
    "contactOverlapTarget": target_overlap,
    "handPressGroupWorldShiftZ": world_shift,
    "triangleCountChanged": False,
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
