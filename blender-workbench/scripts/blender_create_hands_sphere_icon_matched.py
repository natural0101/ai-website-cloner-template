import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT_ROOT = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output")
REFERENCE_PATH = Path(r"C:\Users\se-20\AppData\Local\Temp\codex-clipboard-22475c29-ff69-43c5-b7e8-5578bbedfa52.png")
RENDER_DIR = OUTPUT_ROOT / "renders"
EXPORT_DIR = OUTPUT_ROOT / "exports"
BLEND_DIR = OUTPUT_ROOT / "blend"
REPORT_DIR = OUTPUT_ROOT / "reports"

for directory in (RENDER_DIR, EXPORT_DIR, BLEND_DIR, REPORT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

SCENE_NAME = "HandsSphereIconMatchedScene"
PREFIX = "hands_sphere_matched_"
ASSET_NAME = "hands_sphere_icon_matched"
IMG_W = 309
IMG_H = 250
PX_PER_UNIT = 100.0


def p(px, py, y=-0.35):
    """Map reference pixels to Blender x/y/z with camera looking along +Y."""
    return ((px - IMG_W / 2) / PX_PER_UNIT, y, (IMG_H / 2 - py) / PX_PER_UNIT)


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


def make_material(name, color, roughness=0.55, metallic=0.0, coat=0.08, specular=0.34):
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


def apply_transform(obj, location=False):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=True, scale=True)
    obj.select_set(False)


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def orient_z_to_vector(obj, direction):
    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()


def add_uv_sphere(name, location, scale, material, segments=64, rings=32):
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
    apply_transform(obj)
    return obj


def add_capsule(name, start, end, radius, material, vertices=36):
    start = Vector(start)
    end = Vector(end)
    direction = end - start
    center = (start + end) * 0.5
    length = direction.length
    objects = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=center)
    body = bpy.context.object
    body.name = f"{name}_body"
    orient_z_to_vector(body, direction)
    body.data.materials.append(material)
    shade_smooth(body)
    apply_transform(body)
    objects.append(body)
    for suffix, loc in (("a", start), ("b", end)):
        cap = add_uv_sphere(
            f"{name}_cap_{suffix}",
            loc,
            (radius, radius, radius),
            material,
            segments=vertices,
            rings=max(12, vertices // 2),
        )
        objects.append(cap)
    return objects


def add_curve_tube(name, points, radius, material, resolution=28):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = radius
    curve.bevel_resolution = 9
    curve.use_fill_caps = True
    curve.twist_smooth = 8
    curve.fill_mode = "FULL"
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
    apply_transform(obj)
    return obj


def catmull_rom(points, samples_per_segment=10):
    pts = [Vector(point) for point in points]
    if len(pts) < 2:
        return pts
    result = []
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for sample in range(samples_per_segment):
            t = sample / samples_per_segment
            t2 = t * t
            t3 = t2 * t
            co = 0.5 * (
                (2 * p1)
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
            )
            result.append(co)
    result.append(pts[-1])
    return result


def add_ribbon(name, pixel_points, width_px, material, y=-0.72, thickness=0.075, bevel=0.025):
    centers = [Vector(p(x, py, y=y)) for x, py in pixel_points]
    centers = catmull_rom(centers, samples_per_segment=10)
    half_width = width_px / PX_PER_UNIT / 2

    normals = []
    for index, center in enumerate(centers):
        if index == 0:
            tangent = centers[1] - center
        elif index == len(centers) - 1:
            tangent = center - centers[index - 1]
        else:
            tangent = centers[index + 1] - centers[index - 1]
        tangent.y = 0
        if tangent.length < 1e-6:
            normal = Vector((0, 0, 1))
        else:
            tangent.normalize()
            normal = Vector((-tangent.z, 0, tangent.x))
        normals.append(normal)

    left = [center + normal * half_width for center, normal in zip(centers, normals)]
    right = [center - normal * half_width for center, normal in zip(centers, normals)]

    def arc_points(center, from_vec, to_vec, steps=10):
        a0 = math.atan2(from_vec.z, from_vec.x)
        a1 = math.atan2(to_vec.z, to_vec.x)
        while a1 < a0:
            a1 += math.tau
        if a1 - a0 > math.pi * 1.25:
            a1 -= math.tau
        return [
            center
            + Vector((math.cos(a0 + (a1 - a0) * i / steps), 0, math.sin(a0 + (a1 - a0) * i / steps)))
            * half_width
            for i in range(1, steps)
        ]

    polygon = []
    polygon.extend(left)
    polygon.extend(arc_points(centers[-1], normals[-1], -normals[-1], steps=12))
    polygon.extend(reversed(right))
    polygon.extend(arc_points(centers[0], -normals[0], normals[0], steps=12))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata([tuple(vertex) for vertex in polygon], [], [list(range(len(polygon)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)

    solidify = obj.modifiers.new(f"{name}_soft_depth", "SOLIDIFY")
    solidify.thickness = thickness
    solidify.offset = 0
    bevel_mod = obj.modifiers.new(f"{name}_rounded_edge", "BEVEL")
    bevel_mod.width = bevel
    bevel_mod.segments = 6
    bevel_mod.affect = "EDGES"
    obj.modifiers.new(f"{name}_weighted_normals", "WEIGHTED_NORMAL")

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for modifier in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except RuntimeError:
            pass
    shade_smooth(obj)
    obj.select_set(False)
    return obj


def add_cuff(name, px_start, px_end, radius_z, material, rim_material, face_material, y=-0.28):
    start = Vector(p(*px_start, y=y))
    end = Vector(p(*px_end, y=y))
    axis = end - start
    center = (start + end) * 0.5
    depth = axis.length
    objects = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius_z, depth=depth, location=center)
    body = bpy.context.object
    body.name = f"{name}_body"
    orient_z_to_vector(body, axis)
    body.scale.y = 0.93
    body.data.materials.append(material)
    shade_smooth(body)
    bevel = body.modifiers.new(f"{body.name}_soft_bevel", "BEVEL")
    bevel.width = radius_z * 0.11
    bevel.segments = 8
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    body.select_set(False)
    apply_transform(body)
    objects.append(body)

    for suffix, loc in (("front", start), ("back", end)):
        bpy.ops.mesh.primitive_torus_add(
            major_segments=72,
            minor_segments=12,
            major_radius=radius_z * 0.82,
            minor_radius=radius_z * 0.065,
            location=loc,
        )
        rim = bpy.context.object
        rim.name = f"{name}_{suffix}_rim"
        orient_z_to_vector(rim, axis)
        rim.data.materials.append(rim_material)
        shade_smooth(rim)
        apply_transform(rim)
        objects.append(rim)
    front_face = add_uv_sphere(
        f"{name}_front_soft_face",
        start - axis.normalized() * 0.01,
        (radius_z * 0.72, radius_z * 0.035, radius_z * 0.72),
        face_material,
        segments=48,
        rings=16,
    )
    objects.append(front_face)
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
        per_object[obj.name] = tris
        total += tris
        evaluated.to_mesh_clear()
    return total, per_object


scene = bpy.data.scenes.get(SCENE_NAME) or bpy.data.scenes.new(SCENE_NAME)
if bpy.context.window:
    bpy.context.window.scene = scene
for obj in list(scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = IMG_W * 4
scene.render.resolution_y = IMG_H * 4
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = -0.05
scene.view_settings.gamma = 1
world = scene.world or bpy.data.worlds.new("HandsSphereMatchedWorld")
scene.world = world
world.use_nodes = True
background_node = world.node_tree.nodes.get("Background")
if background_node:
    background_node.inputs["Color"].default_value = (1, 1, 1, 1)
    background_node.inputs["Strength"].default_value = 0.95
world.color = (1, 1, 1)

green = make_material(f"{PREFIX}green_ball", (0.43, 0.78, 0.23, 1), roughness=0.50, coat=0.08, specular=0.34)
orange = make_material(f"{PREFIX}orange_hand", (0.95, 0.33, 0.015, 1), roughness=0.48, coat=0.10, specular=0.34)
orange_light = make_material(f"{PREFIX}orange_highlight", (1.0, 0.60, 0.12, 1), roughness=0.52, coat=0.08, specular=0.28)
pink = make_material(f"{PREFIX}pink_cuff", (1.0, 0.68, 0.79, 1), roughness=0.46, coat=0.14, specular=0.40)
pink_rim = make_material(f"{PREFIX}pink_rim", (1.0, 0.83, 0.90, 1), roughness=0.52, coat=0.08, specular=0.30)
pink_inner = make_material(f"{PREFIX}pink_inner", (1.0, 0.91, 0.94, 1), roughness=0.58, coat=0.05, specular=0.22)
white = make_material(f"{PREFIX}preview_white", (1, 1, 1, 1), roughness=0.68, coat=0, specular=0.12)

asset_objects = []
root = bpy.data.objects.new(f"{PREFIX}Root", None)
bpy.context.collection.objects.link(root)

bpy.ops.mesh.primitive_plane_add(size=4.6, location=(0, 0.78, 0), rotation=(math.radians(90), 0, 0))
backdrop = bpy.context.object
backdrop.name = f"{PREFIX}preview_white_backdrop_not_exported"
backdrop.data.materials.append(white)

# Main ball, matched to green bbox around x=104..211, y=81..190.
ball_center = p(158, 136, y=0.02)
ball = add_uv_sphere(f"{PREFIX}green_sphere", ball_center, (0.53, 0.53, 0.53), green, segments=64, rings=32)
asset_objects.append(ball)

# Cuffs and arms.
asset_objects.extend(add_cuff(f"{PREFIX}left_cuff", (6, 112), (70, 112), 0.31, pink, pink_rim, pink_inner, y=-0.42))
asset_objects.extend(add_cuff(f"{PREFIX}right_cuff", (292, 145), (230, 145), 0.29, pink, pink_rim, pink_inner, y=-0.42))

asset_objects.extend(add_capsule(f"{PREFIX}upper_wrist", p(70, 113, -0.38), p(112, 91, -0.42), 0.155, orange, vertices=36))
asset_objects.extend(add_capsule(f"{PREFIX}right_wrist", p(229, 145, -0.08), p(186, 164, -0.08), 0.16, orange, vertices=36))

# Upper hand: one flattened palm mass plus four deliberately varied fingers.
upper_palm = add_uv_sphere(f"{PREFIX}upper_flat_palm", p(119, 104, -0.60), (0.50, 0.15, 0.20), orange, segments=56, rings=20)
upper_palm.rotation_euler[1] = math.radians(-7)
apply_transform(upper_palm)
asset_objects.append(upper_palm)

for name, pts, width in [
    ("top_finger", [(99, 73), (130, 63), (176, 65), (202, 75)], 24),
    ("middle_finger", [(91, 92), (126, 84), (171, 89), (196, 99)], 27),
    ("lower_finger", [(86, 112), (116, 111), (147, 123), (162, 139)], 30),
    ("upper_thumb", [(91, 127), (115, 132), (138, 141), (150, 150)], 23),
]:
    obj = add_ribbon(f"{PREFIX}{name}", pts, width, orange, y=-0.72, thickness=0.075, bevel=0.026)
    asset_objects.append(obj)

asset_objects.append(
    add_ribbon(
        f"{PREFIX}upper_bright_ridge",
        [(107, 74), (139, 67), (184, 69), (199, 76)],
        4,
        orange_light,
        y=-0.785,
        thickness=0.028,
        bevel=0.008,
    )
)

# Lower hand: flattened cup shape under the sphere, with small merged fingertips.
lower_palm = add_uv_sphere(f"{PREFIX}lower_cupped_palm", p(150, 185, -0.68), (0.49, 0.13, 0.105), orange, segments=56, rings=20)
lower_palm.rotation_euler[1] = math.radians(4)
apply_transform(lower_palm)
asset_objects.append(lower_palm)
lower_thumb = add_curve_tube(
    f"{PREFIX}lower_left_thumb",
    [p(112, 187, -0.76), p(98, 194, -0.76), p(91, 202, -0.76), p(103, 208, -0.76)],
    0.055,
    orange,
    resolution=24,
)
asset_objects.append(lower_thumb)
for i, pts in enumerate([
    [(106, 199), (120, 206), (132, 201)],
    [(124, 202), (139, 210), (151, 203)],
    [(145, 202), (160, 210), (171, 203)],
    [(164, 199), (178, 206), (189, 198)],
]):
    asset_objects.append(add_ribbon(f"{PREFIX}lower_finger_{i+1}", pts, 13, orange, y=-0.79, thickness=0.055, bevel=0.018))

for obj in asset_objects:
    obj.parent = root

# Studio lighting mimics clean web icon lighting.
add_area_light(f"{PREFIX}key_light", (-2.5, -4.0, 3.2), (0, -0.35, 0), 280, 3.6, (1.0, 0.93, 0.84))
add_area_light(f"{PREFIX}fill_light", (2.3, -3.1, 1.1), (0, -0.35, 0), 75, 4.0, (0.78, 0.86, 1.0))
add_area_light(f"{PREFIX}rim_warm_light", (1.7, -1.4, 2.5), (0.1, -0.45, 0.1), 90, 1.9, (1.0, 0.76, 0.54))

camera_data = bpy.data.cameras.new(f"{PREFIX}Camera")
camera = bpy.data.objects.new(f"{PREFIX}Camera", camera_data)
bpy.context.collection.objects.link(camera)
camera.location = (0, -5.2, 0)
look_at(camera, (0, 0, 0))
camera.data.type = "ORTHO"
camera.data.ortho_scale = IMG_H / PX_PER_UNIT * 1.08
camera.data.show_background_images = True
if REFERENCE_PATH.exists():
    image = bpy.data.images.load(str(REFERENCE_PATH), check_existing=True)
    bg = camera.data.background_images.new()
    bg.image = image
    bg.alpha = 0.32
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

total_triangles, per_object = triangle_report(asset_objects)
errors = []
warnings = []
if total_triangles > 60000:
    warnings.append(f"Triangle count {total_triangles} exceeds 60k icon target")
for obj in asset_objects:
    if obj.type == "MESH" and not obj.data.materials:
        errors.append(f"{obj.name} has no material")

render_path = RENDER_DIR / f"{ASSET_NAME}_preview.png"
scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

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
    "primary_reference": str(REFERENCE_PATH),
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
    "reference_matching_notes": {
        "camera": "orthographic, same aspect as reference",
        "construction": "pixel-mapped sphere/cuffs/finger curves",
        "not_exported": [backdrop.name],
    },
}

report_path = REPORT_DIR / f"{ASSET_NAME}_scene_report.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
