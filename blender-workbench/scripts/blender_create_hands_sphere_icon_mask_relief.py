import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


OUTPUT_ROOT = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output")
MASK_JSON = OUTPUT_ROOT / "reference_masks" / "hands_sphere_reference_masks.json"
SCENE_NAME = "HandsSphereIconMaskReliefScene"
PREFIX = "hands_sphere_relief_"
ASSET_NAME = "hands_sphere_icon_mask_relief"

RENDER_DIR = OUTPUT_ROOT / "renders"
EXPORT_DIR = OUTPUT_ROOT / "exports"
BLEND_DIR = OUTPUT_ROOT / "blend"
REPORT_DIR = OUTPUT_ROOT / "reports"
for directory in (RENDER_DIR, EXPORT_DIR, BLEND_DIR, REPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def map_point(x, y, width, height, px_per_unit, depth_y):
    return Vector(((x - width / 2) / px_per_unit, depth_y, (height / 2 - y) / px_per_unit))


def set_principled_input(material, names, value):
    if not material.use_nodes:
        return
    bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            socket.default_value = value
            return


def make_material(name, color, roughness=0.5, coat=0.12, specular=0.35):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = tuple(color)
    set_principled_input(material, ["Base Color"], tuple(color))
    set_principled_input(material, ["Metallic"], 0.0)
    set_principled_input(material, ["Roughness"], roughness)
    set_principled_input(material, ["Coat Weight", "Clearcoat"], coat)
    set_principled_input(material, ["Specular IOR Level", "Specular"], specular)
    return material


def apply_modifiers(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for modifier in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except RuntimeError:
            pass
    try:
        bpy.ops.object.shade_smooth()
    except RuntimeError:
        pass
    obj.select_set(False)


def create_polygon_mesh(name, polygon, layer, data, material):
    loops = []
    outer = [map_point(x, y, data["width"], data["height"], data["px_per_unit"], layer["y"]) for x, y in polygon["points"]]
    loops.append(outer)
    for hole in polygon.get("holes", []):
        loops.append([map_point(x, y, data["width"], data["height"], data["px_per_unit"], layer["y"]) for x, y in hole])

    vertices = [vertex for loop in loops for vertex in loop]
    if len(vertices) < 3:
        return None

    triangles = tessellate_polygon(loops)
    if not triangles:
        return None

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata([tuple(vertex) for vertex in vertices], [], [tuple(triangle) for triangle in triangles])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)

    solidify = obj.modifiers.new(f"{name}_soft_depth", "SOLIDIFY")
    solidify.thickness = layer["thickness"]
    solidify.offset = 0
    bevel = obj.modifiers.new(f"{name}_rounded_edge", "BEVEL")
    bevel.width = layer["bevel"]
    bevel.segments = 8
    bevel.affect = "EDGES"
    obj.modifiers.new(f"{name}_weighted_normals", "WEIGHTED_NORMAL")
    apply_modifiers(obj)
    return obj


def add_area_light(name, location, target, power, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = power
    light.size = size
    light.color = color
    obj = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return obj


def triangle_report(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    per_object = {}
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        tris = len(mesh.loop_triangles)
        total += tris
        per_object[obj.name] = tris
        evaluated.to_mesh_clear()
    return total, per_object


data = json.loads(MASK_JSON.read_text(encoding="utf-8"))

scene = bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME)
if bpy.context.window:
    bpy.context.window.scene = scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = data["width"] * 4
scene.render.resolution_y = data["height"] * 4
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = -0.04
scene.view_settings.gamma = 1.0

world = scene.world or bpy.data.worlds.new("HandsSphereReliefWorld")
scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (1, 1, 1, 1)
    background.inputs["Strength"].default_value = 1.0

root = bpy.data.objects.new(f"{PREFIX}Root", None)
bpy.context.collection.objects.link(root)
asset_objects = []

materials = {
    name: make_material(f"{PREFIX}{name}", layer["color"], roughness=0.48 if name != "green" else 0.55)
    for name, layer in data["layers"].items()
}

# Render preview backdrop, deliberately excluded from GLB.
white = make_material(f"{PREFIX}preview_white", [1, 1, 1, 1], roughness=0.7, coat=0.0, specular=0.1)
bpy.ops.mesh.primitive_plane_add(size=4.6, location=(0, 0.38, 0), rotation=(math.radians(90), 0, 0))
backdrop = bpy.context.object
backdrop.name = f"{PREFIX}preview_white_backdrop_not_exported"
backdrop.data.materials.append(white)

for layer_name in ("green", "orange", "pink"):
    layer = data["layers"][layer_name]
    for index, polygon in enumerate(layer["polygons"]):
        obj = create_polygon_mesh(f"{PREFIX}{layer_name}_{index:02d}", polygon, layer, data, materials[layer_name])
        if obj:
            obj.parent = root
            asset_objects.append(obj)

add_area_light(f"{PREFIX}key_light", (-2.3, -4.5, 3.3), (0, -0.35, 0), 330, 4.0, (1.0, 0.94, 0.86))
add_area_light(f"{PREFIX}fill_light", (2.2, -3.6, 1.0), (0, -0.35, 0), 80, 4.5, (0.80, 0.88, 1.0))
add_area_light(f"{PREFIX}rim_light", (1.5, -1.7, 2.2), (0, -0.35, 0), 70, 2.0, (1.0, 0.82, 0.62))

camera_data = bpy.data.cameras.new(f"{PREFIX}Camera")
camera = bpy.data.objects.new(f"{PREFIX}Camera", camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (0, -4.8, 0)
direction = Vector((0, 0, 0)) - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = data["height"] / data["px_per_unit"]
camera.data.show_background_images = True
source_path = Path(data["source"])
if source_path.exists():
    image = bpy.data.images.load(str(source_path), check_existing=True)
    bg = camera.data.background_images.new()
    bg.image = image
    bg.alpha = 0.25
    bg.display_depth = "BACK"
scene.camera = camera

for window in bpy.context.window_manager.windows:
    window.scene = scene
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type = "RENDERED"
                    space.shading.use_scene_lights_render = True
                    space.shading.use_scene_world_render = True
                    space.overlay.show_overlays = False
                    if space.region_3d:
                        space.region_3d.view_perspective = "CAMERA"
            area.tag_redraw()

render_path = RENDER_DIR / f"{ASSET_NAME}_preview.png"
scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

total_triangles, per_object = triangle_report(asset_objects)
warnings = []
if total_triangles > 60000:
    warnings.append(f"Triangle count {total_triangles} exceeds 60k icon target")
errors = []

glb_path = EXPORT_DIR / f"{ASSET_NAME}.glb"
exported = False
if not errors:
    for existing in bpy.data.objects:
        existing.select_set(False)
    root.select_set(True)
    for obj in asset_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        use_active_scene=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )
    exported = glb_path.exists() and glb_path.stat().st_size > 0

blend_path = BLEND_DIR / f"{ASSET_NAME}.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

report = {
    "asset": ASSET_NAME,
    "scene": SCENE_NAME,
    "primary_reference": data["source"],
    "mask_json": str(MASK_JSON),
    "render": str(render_path),
    "glb": str(glb_path),
    "blend": str(blend_path),
    "exported": exported,
    "validation": {
        "errors": errors,
        "warnings": warnings,
        "triangles": total_triangles,
        "per_object": per_object,
    },
    "not_exported": [backdrop.name],
}
report_path = REPORT_DIR / f"{ASSET_NAME}_scene_report.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
