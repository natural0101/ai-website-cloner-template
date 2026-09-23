import json
from pathlib import Path

import bpy


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v4_lit.blend"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v4_lighting_report.json"
HERO_PATH = PROJECT_ROOT / "public" / "images" / "teamon-reference-v4-lit-hero.png"

for path in (BLEND_PATH, REPORT_PATH, HERO_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)


scene = bpy.context.scene
floor = bpy.data.objects.get("TEAMON_Studio_Floor")
if floor is None:
    raise RuntimeError("TEAMON studio floor is missing")

# Remove the visible floor edge so the background matches the continuous red
# field of the supplied reference.
floor.dimensions = (32.0, 28.0, 0.18)
bpy.context.view_layer.objects.active = floor
floor.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
floor.select_set(False)

floor_material = floor.data.materials[0] if floor.data.materials else None
if floor_material and floor_material.use_nodes:
    bsdf = floor_material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.78, 0.018, 0.010, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.43
        bsdf.inputs["Coat Weight"].default_value = 0.04

world = scene.world
if world and world.use_nodes:
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.56, 0.008, 0.004, 1.0)
    background.inputs["Strength"].default_value = 0.48

light_settings = {
    "TEAMON_Key_Light": (900.0, (1.0, 0.91, 0.86), 5.8),
    "TEAMON_Fill_Light": (430.0, (0.80, 0.88, 1.0), 5.0),
    "TEAMON_Rim_Light": (520.0, (1.0, 0.24, 0.12), 4.8),
}
for name, (energy, color, size) in light_settings.items():
    light = bpy.data.objects.get(name)
    if light is None or light.type != "LIGHT":
        raise RuntimeError(f"TEAMON studio light missing: {name}")
    light.data.energy = energy
    light.data.color = color
    light.data.size = size

scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.28
scene.render.resolution_x = 1024
scene.render.resolution_y = 576
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
scene.render.filepath = str(HERO_PATH)
bpy.ops.render.render(write_still=True)

report = {
    "asset": "TEAMON reference v4 lighting",
    "stage": "LIGHTING",
    "blend": str(BLEND_PATH),
    "render": str(HERO_PATH),
    "floor_dimensions": list(floor.dimensions),
    "world_strength": 0.48,
    "exposure": scene.view_settings.exposure,
    "lights": {
        name: {"energy": energy, "color": list(color), "size": size}
        for name, (energy, color, size) in light_settings.items()
    },
    "exported_glb": False,
    "status": "lighting_visual_gate",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
