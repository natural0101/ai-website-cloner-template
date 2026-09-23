import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT_ROOT = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output")
RENDER_DIR = OUTPUT_ROOT / "renders"
EXPORT_DIR = OUTPUT_ROOT / "exports"
BLEND_DIR = OUTPUT_ROOT / "blend"
REPORT_DIR = OUTPUT_ROOT / "reports"

for directory in (RENDER_DIR, EXPORT_DIR, BLEND_DIR, REPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

SCENE_NAME = "HandsSphereIconScene"
PREFIX = "hands_sphere_icon_"
ASSET_NAME = "hands_sphere_icon"


def set_principled_input(material, names, value):
    if not material.use_nodes:
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


def make_material(name, color, roughness=0.55, metallic=0.0, coat=0.06, specular=0.35):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    set_principled_input(material, ["Base Color"], color)
    set_principled_input(material, ["Metallic"], metallic)
    set_principled_input(material, ["Roughness"], roughness)
    set_principled_input(material, ["Coat Weight", "Clearcoat"], coat)
    set_principled_input(material, ["Specular IOR Level", "Specular"], specular)
    return material


def shade_smooth(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.shade_smooth()
    except RuntimeError:
        pass
    obj.select_set(False)
    return obj


def add_subdivision(obj, levels=1):
    modifier = obj.modifiers.new(f"{obj.name}_soft_subdivision", "SUBSURF")
    modifier.levels = levels
    modifier.render_levels = levels
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except RuntimeError:
        pass
    obj.select_set(False)
    return obj


def apply_rotation_scale(obj):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except RuntimeError:
        pass
    obj.select_set(False)


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def orient_z_to_vector(obj, direction):
    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()


def add_uv_sphere(name, location, scale, material, segments=48, rings=24, subdivision=0):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=1,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    shade_smooth(obj)
    if subdivision:
        add_subdivision(obj, subdivision)
    apply_rotation_scale(obj)
    return obj


def add_cylinder_between(name, start, end, radius, material, vertices=40):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    length = direction.length
    center = (start + end) * 0.5

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=length,
        location=center,
    )
    obj = bpy.context.object
    obj.name = name
    orient_z_to_vector(obj, direction)
    obj.data.materials.append(material)
    shade_smooth(obj)
    apply_rotation_scale(obj)
    return obj


def add_capsule(name, start, end, radius, material, vertices=32, cap_segments=32):
    parts = []
    parts.append(add_cylinder_between(f"{name}_body", start, end, radius, material, vertices))
    parts.append(
        add_uv_sphere(
            f"{name}_cap_a",
            start,
            (radius, radius, radius),
            material,
            segments=cap_segments,
            rings=max(12, cap_segments // 2),
        )
    )
    parts.append(
        add_uv_sphere(
            f"{name}_cap_b",
            end,
            (radius, radius, radius),
            material,
            segments=cap_segments,
            rings=max(12, cap_segments // 2),
        )
    )
    return parts


def add_curve_tube(name, points, radius, material, resolution=24):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = radius
    curve.bevel_resolution = 8
    curve.fill_mode = "FULL"
    curve.twist_smooth = 8

    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = Vector(co)
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"

    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    shade_smooth(obj)
    apply_rotation_scale(obj)
    return obj


def add_cuff(name, start, end, radius, material, rim_material, inner_material):
    start = Vector(start)
    end = Vector(end)
    axis = end - start
    center = (start + end) * 0.5
    depth = axis.length
    objects = []

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=56,
        radius=radius,
        depth=depth,
        location=center,
    )
    body = bpy.context.object
    body.name = f"{name}_body"
    orient_z_to_vector(body, axis)
    body.data.materials.append(material)
    shade_smooth(body)

    bevel = body.modifiers.new(f"{body.name}_soft_edge", "BEVEL")
    bevel.width = radius * 0.13
    bevel.segments = 8
    bevel.affect = "EDGES"
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=bevel.name)
    except RuntimeError:
        pass
    body.select_set(False)
    apply_rotation_scale(body)
    objects.append(body)

    for suffix, loc in (("front", start), ("back", end)):
        bpy.ops.mesh.primitive_torus_add(
            major_segments=64,
            minor_segments=12,
            major_radius=radius * 0.82,
            minor_radius=radius * 0.075,
            location=loc,
        )
        rim = bpy.context.object
        rim.name = f"{name}_{suffix}_rim"
        orient_z_to_vector(rim, axis)
        rim.data.materials.append(rim_material)
        shade_smooth(rim)
        apply_rotation_scale(rim)
        objects.append(rim)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=56,
        radius=radius * 0.72,
        depth=0.018,
        location=start - axis.normalized() * 0.012,
    )
    face = bpy.context.object
    face.name = f"{name}_front_soft_face"
    orient_z_to_vector(face, axis)
    face.data.materials.append(inner_material)
    shade_smooth(face)
    apply_rotation_scale(face)
    objects.append(face)

    return objects


def add_area_light(name, location, target, power, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = power
    light.size = size
    light.color = color
    obj = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def triangle_count(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    per_object = {}
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        count = len(mesh.loop_triangles)
        total += count
        per_object[obj.name] = count
        evaluated.to_mesh_clear()
    return total, per_object


def validate_objects(objects):
    errors = []
    warnings = []
    total, per_object = triangle_count(objects)

    if total <= 0:
        errors.append("No exportable mesh triangles")
    if total > 60000:
        warnings.append(f"Triangle count {total} is above the 60k icon target")

    for obj in objects:
        if obj.type != "MESH":
            continue
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material")
        if any(abs(scale - 1.0) > 0.001 for scale in obj.scale):
            warnings.append(f"{obj.name} has unapplied scale {tuple(round(v, 3) for v in obj.scale)}")
        for vertex in obj.data.vertices:
            co = obj.matrix_world @ vertex.co
            if not all(math.isfinite(value) for value in (co.x, co.y, co.z)):
                errors.append(f"{obj.name} has non-finite coordinates")
                break

    return {"errors": errors, "warnings": warnings, "triangles": total, "per_object": per_object}


scene = bpy.data.scenes.get(SCENE_NAME)
if scene is None:
    scene = bpy.data.scenes.new(SCENE_NAME)

if bpy.context.window:
    bpy.context.window.scene = scene

for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE"

scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.film_transparent = False
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0.15
scene.view_settings.gamma = 1.0

world = scene.world or bpy.data.worlds.new("HandsSphereIconWorld")
scene.world = world
world.use_nodes = False
world.color = (1.0, 1.0, 1.0)

green = make_material(f"{PREFIX}soft_green_ball", (0.43, 0.82, 0.27, 1), roughness=0.58, coat=0.08, specular=0.34)
orange = make_material(f"{PREFIX}warm_orange_hand", (1.0, 0.34, 0.015, 1), roughness=0.5, coat=0.1, specular=0.36)
orange_light = make_material(f"{PREFIX}hand_highlight_orange", (1.0, 0.62, 0.14, 1), roughness=0.54, coat=0.08, specular=0.32)
pink = make_material(f"{PREFIX}soft_pink_cuff", (1.0, 0.67, 0.78, 1), roughness=0.5, coat=0.12, specular=0.38)
pink_rim = make_material(f"{PREFIX}soft_pink_rim", (1.0, 0.78, 0.86, 1), roughness=0.52, coat=0.1, specular=0.34)
pink_inner = make_material(f"{PREFIX}pink_inner_face", (1.0, 0.86, 0.91, 1), roughness=0.6, coat=0.04, specular=0.22)
floor_mat = make_material(f"{PREFIX}matte_shadow_floor", (1.0, 1.0, 1.0, 1), roughness=0.7, coat=0.0, specular=0.2)

asset_objects = []

root = bpy.data.objects.new(f"{PREFIX}Root", None)
bpy.context.collection.objects.link(root)

ball = add_uv_sphere(f"{PREFIX}green_ball", (0, 0, 0), (0.92, 0.92, 0.92), green, segments=72, rings=36)
asset_objects.append(ball)

# Upper hand enters from the left and wraps over the front of the ball.
asset_objects.extend(
    add_capsule(
        f"{PREFIX}upper_forearm",
        (-2.05, -0.18, 0.52),
        (-0.78, -0.58, 0.54),
        0.22,
        orange,
        vertices=40,
        cap_segments=36,
    )
)
upper_palm = add_uv_sphere(
    f"{PREFIX}upper_palm",
    (-0.55, -0.73, 0.52),
    (0.58, 0.25, 0.27),
    orange,
    segments=56,
    rings=28,
)
upper_palm.rotation_euler[2] = math.radians(-8)
apply_rotation_scale(upper_palm)
asset_objects.append(upper_palm)

upper_finger_specs = [
    ("upper_index", [(-0.82, -0.91, 0.93), (-0.32, -1.03, 1.14), (0.42, -0.97, 1.08), (0.66, -0.84, 0.98)], 0.105),
    ("upper_middle", [(-0.82, -0.93, 0.78), (-0.28, -1.04, 0.94), (0.39, -1.01, 0.90), (0.57, -0.88, 0.80)], 0.11),
    ("upper_ring", [(-0.76, -0.93, 0.62), (-0.22, -1.01, 0.72), (0.32, -0.95, 0.66)], 0.10),
    ("upper_thumb", [(-0.70, -0.94, 0.37), (-0.18, -1.04, 0.27), (0.27, -0.92, 0.32)], 0.125),
]

for name, points, radius in upper_finger_specs:
    tube = add_curve_tube(f"{PREFIX}{name}", points, radius, orange, resolution=28)
    asset_objects.append(tube)
    fingertip = add_uv_sphere(
        f"{PREFIX}{name}_tip",
        points[-1],
        (radius * 1.18, radius * 1.18, radius * 1.18),
        orange,
        segments=28,
        rings=14,
    )
    asset_objects.append(fingertip)

highlight = add_curve_tube(
    f"{PREFIX}upper_hand_soft_highlight",
    [(-0.63, -1.055, 0.87), (-0.05, -1.09, 0.99), (0.43, -1.01, 0.96)],
    0.027,
    orange_light,
    resolution=20,
)
asset_objects.append(highlight)

# Lower hand comes from the right and cups the ball from below.
asset_objects.extend(
    add_capsule(
        f"{PREFIX}lower_forearm",
        (2.05, -0.15, -0.07),
        (0.82, -0.58, -0.50),
        0.22,
        orange,
        vertices=40,
        cap_segments=36,
    )
)
lower_palm = add_uv_sphere(
    f"{PREFIX}lower_palm",
    (0.12, -0.78, -0.79),
    (0.78, 0.24, 0.24),
    orange,
    segments=56,
    rings=28,
)
lower_palm.rotation_euler[2] = math.radians(5)
apply_rotation_scale(lower_palm)
asset_objects.append(lower_palm)

lower_finger_specs = [
    ("lower_thumb", [(-0.72, -0.97, -0.72), (-0.42, -1.08, -0.94), (-0.06, -1.00, -0.87)], 0.105),
    ("lower_index", [(-0.42, -1.02, -0.86), (-0.20, -1.13, -1.07), (0.05, -1.05, -0.98)], 0.092),
    ("lower_middle", [(-0.10, -1.02, -0.91), (0.13, -1.13, -1.10), (0.36, -1.05, -0.99)], 0.092),
    ("lower_ring", [(0.22, -0.99, -0.90), (0.43, -1.08, -1.04), (0.61, -1.00, -0.92)], 0.086),
]

for name, points, radius in lower_finger_specs:
    tube = add_curve_tube(f"{PREFIX}{name}", points, radius, orange, resolution=24)
    asset_objects.append(tube)
    fingertip = add_uv_sphere(
        f"{PREFIX}{name}_tip",
        points[-1],
        (radius * 1.15, radius * 1.15, radius * 1.15),
        orange,
        segments=24,
        rings=12,
    )
    asset_objects.append(fingertip)

asset_objects.extend(
    add_cuff(
        f"{PREFIX}left_pink_cuff",
        (-2.64, -0.33, 0.53),
        (-2.03, -0.18, 0.52),
        0.36,
        pink,
        pink_rim,
        pink_inner,
    )
)
asset_objects.extend(
    add_cuff(
        f"{PREFIX}right_pink_cuff",
        (2.55, -0.24, -0.01),
        (1.96, -0.14, -0.08),
        0.34,
        pink,
        pink_rim,
        pink_inner,
    )
)

for obj in asset_objects:
    obj.parent = root

# A simple white floor is only for preview shadows, not for GLB export.
bpy.ops.mesh.primitive_plane_add(size=6.2, location=(0, 0.25, -1.22))
floor = bpy.context.object
floor.name = f"{PREFIX}preview_floor_not_exported"
floor.data.materials.append(floor_mat)
floor.hide_select = True

bpy.ops.mesh.primitive_plane_add(
    size=7.2,
    location=(0, 1.55, 0.3),
    rotation=(math.radians(90), 0, 0),
)
backdrop = bpy.context.object
backdrop.name = f"{PREFIX}preview_backdrop_not_exported"
backdrop.data.materials.append(floor_mat)
backdrop.hide_select = True

add_area_light(f"{PREFIX}key_softbox", (-2.4, -4.2, 4.3), (0, -0.4, 0), 520, 4.0, (1.0, 0.94, 0.88))
add_area_light(f"{PREFIX}fill_softbox", (3.2, -3.2, 1.4), (0, -0.4, -0.1), 90, 4.5, (0.78, 0.88, 1.0))
add_area_light(f"{PREFIX}rim_softbox", (1.9, 2.0, 2.7), (0, -0.3, 0), 210, 2.2, (1.0, 0.78, 0.58))

camera_data = bpy.data.cameras.new(f"{PREFIX}Camera")
camera = bpy.data.objects.new(f"{PREFIX}Camera", camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (0.12, -7.2, 0.36)
look_at(camera, (0, -0.65, 0.02))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 4.55
camera.data.lens = 74
camera.data.dof.use_dof = True
camera.data.dof.focus_object = ball
camera.data.dof.aperture_fstop = 8.0
scene.camera = camera

for window in bpy.context.window_manager.windows:
    window.scene = scene
    for area in window.screen.areas:
        if area.type != "VIEW_3D":
            continue
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.shading.type = "RENDERED"
                space.shading.use_scene_lights_render = True
                space.shading.use_scene_world_render = True
                space.overlay.show_overlays = False
                if space.region_3d:
                    space.region_3d.view_perspective = "CAMERA"
        area.tag_redraw()

validation = validate_objects(asset_objects)

for existing_object in bpy.data.objects:
    existing_object.select_set(False)
root.select_set(True)
for obj in asset_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = root

glb_path = EXPORT_DIR / f"{ASSET_NAME}.glb"
if validation["errors"]:
    exported = False
else:
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

render_path = RENDER_DIR / f"{ASSET_NAME}_preview.png"
scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

blend_path = BLEND_DIR / f"{ASSET_NAME}.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

report = {
    "asset": ASSET_NAME,
    "style": "clay_puffy_icon",
    "reference_summary": {
        "main_shapes": ["green sphere", "orange hands", "pink cuffs"],
        "camera": "front 3/4 studio product icon",
        "materials": "soft matte plasticine / puffy toy material",
    },
    "scene": SCENE_NAME,
    "render": str(render_path),
    "glb": str(glb_path),
    "blend": str(blend_path),
    "exported": exported,
    "validation": validation,
    "exported_objects": [obj.name for obj in asset_objects],
}

report_path = REPORT_DIR / f"{ASSET_NAME}_scene_report.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(report, ensure_ascii=False, indent=2))
