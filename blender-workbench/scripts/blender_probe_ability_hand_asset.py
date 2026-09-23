import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
MODEL_PATH = PROJECT_ROOT / "blender-workbench" / "vendor" / "ability-hand-api" / "URDF" / "models" / "full_model_fused_with__wrist.stl"
OUTPUT_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews" / "ability_hand_probe"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "ability_hand_probe.json"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "ability_hand_probe.blend"

for path in (OUTPUT_DIR, REPORT_PATH.parent, BLEND_PATH.parent):
    path.mkdir(parents=True, exist_ok=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    low = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    high = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return low, high


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(MODEL_PATH))
hand = bpy.context.object
hand.name = "ABILITY_HAND_Probe"
hand.scale = (10.0, 10.0, 10.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

for polygon in hand.data.polygons:
    polygon.use_smooth = True

material = bpy.data.materials.new("AbilityHand_White")
material.use_nodes = True
bsdf = material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.92, 0.94, 0.98, 1.0)
bsdf.inputs["Roughness"].default_value = 0.31
bsdf.inputs["Coat Weight"].default_value = 0.18
hand.data.materials.append(material)

low, high = bounds(hand)
center = (low + high) * 0.5
span = max(high.x - low.x, high.y - low.y, high.z - low.z)
hand.location -= center
bpy.context.view_layer.update()

world = bpy.context.scene.world or bpy.data.worlds.new("AbilityHandWorld")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025, 0.025, 0.035, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

for name, energy, size, location in (
    ("Key", 900.0, 5.0, (4.0, -5.0, 6.0)),
    ("Fill", 500.0, 4.0, (-4.0, -2.0, 3.0)),
    ("Rim", 700.0, 3.0, (2.0, 4.0, 5.0)),
):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, (0.0, 0.0, 0.0))

camera_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", camera_data)
bpy.context.scene.collection.objects.link(camera)
bpy.context.scene.camera = camera
camera.data.type = "ORTHO"
camera.data.ortho_scale = span * 1.25

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.view_settings.look = "AgX - Medium High Contrast"

views = {
    "front": (0.0, -span * 2.5, 0.0),
    "three_quarter": (span * 1.7, -span * 1.7, span * 0.8),
    "side": (span * 2.5, 0.0, 0.0),
}
renders = []
for name, location in views.items():
    camera.location = location
    look_at(camera, (0.0, 0.0, 0.0))
    target = OUTPUT_DIR / f"ability-hand-{name}.png"
    scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    renders.append(str(target))

hand.data.calc_loop_triangles()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
report = {
    "asset": "PSYONIC Ability Hand fused model with wrist",
    "source": "https://github.com/psyonicinc/ability-hand-api",
    "license": "MIT",
    "input": str(MODEL_PATH),
    "blend": str(BLEND_PATH),
    "renders": renders,
    "triangles": len(hand.data.loop_triangles),
    "bounds": {"min": list(low), "max": list(high)},
    "status": "visual_probe_only",
}
REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
