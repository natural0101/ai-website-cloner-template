import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT_ROOT = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output")
RENDER_DIR = OUTPUT_ROOT / "renders"
BLEND_DIR = OUTPUT_ROOT / "blend"
RENDER_DIR.mkdir(parents=True, exist_ok=True)
BLEND_DIR.mkdir(parents=True, exist_ok=True)


def set_principled_input(material, names, value):
    if not material or not material.use_nodes:
        return

    bsdf = next(
        (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
        None,
    )
    if not bsdf:
        return

    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            socket.default_value = value
            return


def ensure_material(name, color, metallic=0.0, roughness=0.35, emission=None):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    set_principled_input(material, ["Base Color"], color)
    set_principled_input(material, ["Metallic"], metallic)
    set_principled_input(material, ["Roughness"], roughness)
    set_principled_input(material, ["Alpha"], color[3] if len(color) > 3 else 1.0)

    if emission:
        set_principled_input(material, ["Emission Color", "Emission"], emission[0])
        set_principled_input(material, ["Emission Strength"], emission[1])

    return material


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def get_or_create_area_light(name, location, power, size, color):
    light = bpy.data.lights.get(name)
    if not light:
        light = bpy.data.lights.new(name, "AREA")
    light.energy = power
    light.size = size
    light.color = color

    obj = bpy.data.objects.get(name)
    if not obj:
        obj = bpy.data.objects.new(name, light)
        bpy.context.collection.objects.link(obj)

    obj.location = location
    return obj


def set_card(name, location, rotation, scale, material):
    obj = bpy.data.objects.get(name)
    if not obj:
        bpy.ops.mesh.primitive_plane_add(size=1, location=location, rotation=rotation)
        obj = bpy.context.object
        obj.name = name
    else:
        obj.location = location
        obj.rotation_euler = rotation

    obj.scale = scale
    obj.hide_viewport = False
    obj.hide_render = False
    obj.display_type = "TEXTURED"
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


silver_objects = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH" and obj.name.startswith("bite_site_silver")
]

if not silver_objects:
    silver_objects = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and "silver" in obj.name.lower()
    ]

if not silver_objects:
    raise RuntimeError("Не нашёл bite_site_silver mesh objects в сцене")

for obj in bpy.context.scene.objects:
    if obj.name.startswith("bite_3d_logo"):
        obj.hide_viewport = True
        obj.hide_render = True
    if obj.name.startswith("bite_site_silver"):
        obj.hide_viewport = False
        obj.hide_render = False
        obj.hide_select = False

chrome = ensure_material(
    "Beauty_View_Chrome_Silver",
    (0.82, 0.86, 0.87, 1.0),
    metallic=1.0,
    roughness=0.075,
)

for obj in silver_objects:
    if not obj.data.materials:
        obj.data.materials.append(chrome)
    for index in range(len(obj.data.materials)):
        obj.data.materials[index] = chrome

bounds = []
for obj in silver_objects:
    for corner in obj.bound_box:
        bounds.append(obj.matrix_world @ Vector(corner))

min_corner = Vector(
    (
        min(point.x for point in bounds),
        min(point.y for point in bounds),
        min(point.z for point in bounds),
    )
)
max_corner = Vector(
    (
        max(point.x for point in bounds),
        max(point.y for point in bounds),
        max(point.z for point in bounds),
    )
)
center = (min_corner + max_corner) * 0.5
size = max_corner - min_corner
max_axis = max(size.x, size.y, size.z, 1.0)

white_card = ensure_material(
    "Beauty_View_White_Reflection_Card",
    (1.0, 0.98, 0.92, 1.0),
    roughness=0.18,
    emission=((1.0, 0.96, 0.88, 1.0), 0.6),
)
black_card = ensure_material(
    "Beauty_View_Black_Reflection_Card",
    (0.015, 0.018, 0.022, 1.0),
    roughness=0.28,
)
warm_card = ensure_material(
    "Beauty_View_Warm_Reflection_Card",
    (1.0, 0.46, 0.20, 1.0),
    roughness=0.2,
    emission=((1.0, 0.36, 0.14, 1.0), 0.28),
)

set_card(
    "Beauty_View_Left_White_Card",
    center + Vector((-max_axis * 1.05, -max_axis * 0.45, max_axis * 0.16)),
    (math.radians(76), 0, math.radians(-20)),
    (max_axis * 0.18, max_axis * 1.15, 1),
    white_card,
)
set_card(
    "Beauty_View_Right_Black_Card",
    center + Vector((max_axis * 1.05, -max_axis * 0.36, max_axis * 0.12)),
    (math.radians(76), 0, math.radians(20)),
    (max_axis * 0.22, max_axis * 1.25, 1),
    black_card,
)
set_card(
    "Beauty_View_Top_Warm_Card",
    center + Vector((max_axis * 0.18, -max_axis * 0.52, max_axis * 0.88)),
    (math.radians(68), 0, math.radians(2)),
    (max_axis * 0.82, max_axis * 0.16, 1),
    warm_card,
)

key = get_or_create_area_light(
    "Beauty_View_Key_Softbox",
    center + Vector((-max_axis * 1.7, -max_axis * 2.25, max_axis * 1.5)),
    620,
    max_axis * 1.35,
    (1.0, 0.94, 0.86),
)
rim = get_or_create_area_light(
    "Beauty_View_Rim_Strip",
    center + Vector((max_axis * 1.35, max_axis * 1.6, max_axis * 0.95)),
    460,
    max_axis * 0.55,
    (0.82, 0.92, 1.0),
)
fill = get_or_create_area_light(
    "Beauty_View_Fill",
    center + Vector((max_axis * 1.15, -max_axis * 1.8, max_axis * 0.38)),
    95,
    max_axis * 2.0,
    (0.75, 0.82, 1.0),
)
for light_obj in (key, rim, fill):
    look_at(light_obj, center)

camera_data = bpy.data.cameras.get("Beauty_View_Camera")
if not camera_data:
    camera_data = bpy.data.cameras.new("Beauty_View_Camera")
camera = bpy.data.objects.get("Beauty_View_Camera")
if not camera:
    camera = bpy.data.objects.new("Beauty_View_Camera", camera_data)
    bpy.context.collection.objects.link(camera)

camera.location = center + Vector((0.05 * max_axis, -max_axis * 2.65, max_axis * 0.42))
look_at(camera, center + Vector((0, 0, size.z * 0.04)))
camera.data.lens = 78
camera.data.dof.use_dof = True
camera.data.dof.focus_object = silver_objects[0]
camera.data.dof.aperture_fstop = 8.0
bpy.context.scene.camera = camera

world = bpy.context.scene.world or bpy.data.worlds.new("Beauty_View_World")
bpy.context.scene.world = world
world.color = (0.008, 0.009, 0.011)

engine_candidates = ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"]
for engine in engine_candidates:
    try:
        bpy.context.scene.render.engine = engine
        break
    except TypeError:
        continue

if bpy.context.scene.render.engine == "CYCLES":
    bpy.context.scene.cycles.samples = 96
    bpy.context.scene.cycles.preview_samples = 32
elif hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 64
    bpy.context.scene.eevee.taa_samples = 32

bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.view_settings.view_transform = "Filmic"
bpy.context.scene.view_settings.look = "Medium High Contrast"
bpy.context.scene.view_settings.exposure = 0.15
bpy.context.scene.view_settings.gamma = 1.0

for window in bpy.context.window_manager.windows:
    screen = window.screen
    for area in screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                space.shading.type = "RENDERED"
                space.shading.use_scene_world_render = True
                space.shading.use_scene_lights_render = True
                space.overlay.show_overlays = False
                if space.region_3d:
                    space.region_3d.view_perspective = "CAMERA"
            area.tag_redraw()

bpy.ops.object.select_all(action="DESELECT")
for obj in silver_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = silver_objects[0]

blend_path = BLEND_DIR / "bite_site_silver_logo_beauty_view.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

print(
    {
        "status": "beauty_view_ready",
        "camera": camera.name,
        "engine": bpy.context.scene.render.engine,
        "visible_silver_meshes": [obj.name for obj in silver_objects],
        "blend": str(blend_path),
        "hint": "Viewport switched to Rendered camera view with overlays hidden.",
    }
)
