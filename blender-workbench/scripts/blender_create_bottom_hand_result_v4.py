from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
WORKBENCH = REPO / "blender-workbench"
SHAPE_TOOLS = WORKBENCH / "shape-reconstruction-upgrade" / "04_blender_tools"
RESEARCH_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"
TARGET = ARTIFACTS / "reference_masks" / "bottom_hand_target_v1" / "hand_target.json"

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)

if str(SHAPE_TOOLS) not in sys.path:
    sys.path.insert(0, str(SHAPE_TOOLS))
if str(RESEARCH_TOOLS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_TOOLS))

import capability_probe
import scene_qa
import shape_tools as st


ASSET = "bottom_hand_result_v4"
SCENE_NAME = "BottomHandResultV4Scene"
WIDTH = 1000
HEIGHT = 820
SPHERE_CENTER_N = (0.492, 0.448)
SCALE_X = 3.45
SCALE_Z = 3.25


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def checkpoint_current_scene() -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = CHECKPOINTS / f"{ASSET}_prechange_{timestamp}.blend"
    result = {"path": str(destination), "status": "skipped"}
    if bpy.context.scene.objects:
        bpy.ops.wm.save_as_mainfile(filepath=str(destination))
        result["status"] = "saved"
        result["bytes"] = destination.stat().st_size
    return result


def safe_set_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def create_clean_scene() -> bpy.types.Scene:
    existing = bpy.data.scenes.get(SCENE_NAME)
    if existing is not None:
        if bpy.context.window is not None:
            bpy.context.window.scene = existing
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        if bpy.context.window is not None:
            scene = bpy.data.scenes.new(SCENE_NAME)
            bpy.context.window.scene = scene
        else:
            scene = bpy.context.scene
            scene.name = SCENE_NAME

    scene = bpy.context.scene
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.08
    scene.view_settings.gamma = 1.0

    engine = safe_set_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 80
        scene.cycles.use_denoising = True
    elif hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.2),
            ("gtao_factor", 0.46),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("BottomHandClayWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        background.inputs["Strength"].default_value = 0.70
    return scene


def create_collections() -> dict[str, bpy.types.Collection]:
    root = bpy.data.collections.new("ABT_BOTTOM_HAND_CLAY_V1")
    bpy.context.scene.collection.children.link(root)
    source = bpy.data.collections.new("ABT_BOTTOM_HAND_CLAY_SOURCE")
    output = bpy.data.collections.new("ABT_BOTTOM_HAND_CLAY_OUTPUT")
    guides = bpy.data.collections.new("ABT_BOTTOM_HAND_CLAY_GUIDES")
    root.children.link(source)
    root.children.link(output)
    root.children.link(guides)
    return {"root": root, "source": source, "output": output, "guides": guides}


def material(name: str, color: tuple[float, float, float, float], roughness: float, alpha: float = 1.0) -> bpy.types.Material:
    mat = st.create_principled_material(name, base_color=color, metallic=0.0, roughness=roughness)
    nodes = mat.node_tree.nodes
    principled = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if principled is not None:
        for socket_name, value in (
            ("Specular IOR Level", 0.25),
            ("Coat Weight", 0.0),
        ):
            socket = principled.inputs.get(socket_name)
            if socket is not None:
                socket.default_value = value
        alpha_socket = principled.inputs.get("Alpha")
        if alpha_socket is not None:
            alpha_socket.default_value = alpha
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.show_transparent_back = True
    return mat


def create_light(name: str, location: tuple[float, float, float], power: float, size: float) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    direction = Vector((0.0, 0.0, -0.45)) - Vector(location)
    obj.location = location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    st.tag_object(obj, role="studio_light", export=False)
    return obj


def setup_lighting() -> None:
    create_light("BHCV1_KeyLight_not_exported", (-3.4, -5.0, 4.0), 260.0, 5.0)
    create_light("BHCV1_FillLight_not_exported", (3.4, -3.5, 1.8), 54.0, 6.0)
    create_light("BHCV1_RimLight_not_exported", (2.5, 2.6, 2.8), 42.0, 4.6)


def setup_camera(name: str = "BHCV1_CAM_FRONT") -> dict:
    return st.setup_reference_camera(
        width=WIDTH,
        height=HEIGHT,
        world_height=2.62,
        distance=8.0,
        name=name,
        target=(0.10, 0.0, -0.52),
    )


def setup_orbit_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], ortho: float) -> dict:
    scene = bpy.context.scene
    data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name)
    if camera is None:
        camera = bpy.data.objects.new(name, data)
        scene.collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho
    scene.camera = camera
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    st.tag_object(camera, role="review_camera", export=False)
    return {"status": "ok", "camera": camera.name, "view": name, "ortho_scale": camera.data.ortho_scale}


def world_xy(point: dict, depth: float = -0.54) -> tuple[float, float, float]:
    x = (float(point["x"]) - SPHERE_CENTER_N[0]) * SCALE_X
    z = -(float(point["y"]) - SPHERE_CENTER_N[1]) * SCALE_Z
    return (x, depth, z)


def world_radius(point: dict, scale: float = 0.92) -> float:
    return max(0.035, float(point["radius"]) * SCALE_X * scale)


def load_target() -> dict:
    return json.loads(TARGET.read_text(encoding="utf-8"))


def line_points(target: dict, line_id: str, depth: float) -> list[tuple[float, float, float]]:
    line = next(item for item in target["hand"]["centerlines"] if item["id"] == line_id)
    return [world_xy(point, depth) for point in line["points"]]


def line_radii(target: dict, line_id: str, scale: float = 0.92) -> list[float]:
    line = next(item for item in target["hand"]["centerlines"] if item["id"] == line_id)
    return [world_radius(point, scale) for point in line["points"]]


def landmark(target: dict, landmark_id: str) -> dict:
    return next(item for item in target["hand"]["landmarks"] if item["id"] == landmark_id)


def target_point(target: dict, landmark_id: str, depth: float) -> tuple[float, float, float]:
    return world_xy(landmark(target, landmark_id), depth)


def lerp_point(a: tuple[float, float, float], b: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    av = Vector(a)
    bv = Vector(b)
    value = av.lerp(bv, t)
    return (value.x, value.y, value.z)


def target_line_depths(
    target: dict,
    line_id: str,
    *,
    root_depth: float,
    tip_depth: float,
    radius_scale: float,
    root_pull: tuple[float, float, float] | None = None,
) -> tuple[list[tuple[float, float, float]], list[float]]:
    line = next(item for item in target["hand"]["centerlines"] if item["id"] == line_id)
    points: list[tuple[float, float, float]] = []
    count = max(1, len(line["points"]) - 1)
    for index, point in enumerate(line["points"]):
        t = index / count
        depth = root_depth + (tip_depth - root_depth) * t
        points.append(world_xy(point, depth))
    if root_pull is not None:
        points.insert(0, lerp_point(root_pull, points[0], 0.62))

    radii = [world_radius(point, radius_scale) for point in line["points"]]
    if root_pull is not None:
        radii.insert(0, max(radii[0] * 1.10, radii[0] + 0.018))
    return points, radii


def create_guide_sphere(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    guide = st.create_ellipsoid(
        name="BHCV1_GuideSphere_not_exported",
        location=(0.0, 0.07, 0.0),
        scale=(0.92, 0.92, 0.92),
        segments=72,
        rings=36,
        collection=collection,
        material=mat,
        role="guide",
        export=False,
    )
    st.shade_smooth(guide)
    return guide


def select_only(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def convert_to_mesh(obj: bpy.types.Object, name: str, mat: bpy.types.Material, collection: bpy.types.Collection) -> bpy.types.Object:
    select_only(obj)
    bpy.ops.object.convert(target="MESH")
    mesh = bpy.context.object
    mesh.name = name
    mesh.data.name = f"{name}_Mesh"
    st.move_to_collection(mesh, collection)
    st.assign_material(mesh, mat)
    st.shade_smooth(mesh)
    weighted = mesh.modifiers.new(f"{name}_WeightedNormals", "WEIGHTED_NORMAL")
    st.apply_modifier(mesh, weighted.name)
    st.tag_object(mesh, role="source_part", export=True)
    return mesh


def interpolate(points: list[tuple[float, float, float]], radii: list[float], samples_per_segment: int = 5) -> list[tuple[tuple[float, float, float], float]]:
    samples: list[tuple[tuple[float, float, float], float]] = []
    for index in range(len(points) - 1):
        a = Vector(points[index])
        b = Vector(points[index + 1])
        ra = radii[index]
        rb = radii[index + 1]
        for step in range(samples_per_segment):
            t = step / float(samples_per_segment)
            p = a.lerp(b, t)
            r = ra + (rb - ra) * t
            samples.append(((p.x, p.y, p.z), r))
    samples.append((points[-1], radii[-1]))
    return samples


def catmull_rom(a: Vector, b: Vector, c: Vector, d: Vector, t: float) -> Vector:
    t2 = t * t
    t3 = t2 * t
    return (b * 2.0 + (c - a) * t + (a * 2.0 - b * 5.0 + c * 4.0 - d) * t2 + (-a + b * 3.0 - c * 3.0 + d) * t3) * 0.5


def sample_smooth_path(
    points: list[tuple[float, float, float]],
    radii: list[float],
    samples_per_segment: int = 10,
) -> list[tuple[Vector, float]]:
    coords = [Vector(point) for point in points]
    if len(coords) < 2 or len(coords) != len(radii):
        raise ValueError("smooth tube path needs matching points/radii")

    samples: list[tuple[Vector, float]] = []
    for index in range(len(coords) - 1):
        p0 = coords[max(index - 1, 0)]
        p1 = coords[index]
        p2 = coords[index + 1]
        p3 = coords[min(index + 2, len(coords) - 1)]
        for step in range(samples_per_segment):
            t = step / float(samples_per_segment)
            p = catmull_rom(p0, p1, p2, p3, t)
            r = radii[index] + (radii[index + 1] - radii[index]) * t
            samples.append((p, r))
    samples.append((coords[-1], radii[-1]))
    return samples


def create_tapered_tube_mesh(
    *,
    name: str,
    points: list[tuple[float, float, float]],
    radii: list[float],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    samples_per_segment: int = 12,
    ring_segments: int = 28,
    depth_scale: float = 0.82,
    screen_scale: float = 1.0,
) -> bpy.types.Object:
    samples = sample_smooth_path(points, radii, samples_per_segment=samples_per_segment)
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    up_hint = Vector((0.0, 1.0, 0.0))

    for index, (point, radius) in enumerate(samples):
        previous_point = samples[max(index - 1, 0)][0]
        next_point = samples[min(index + 1, len(samples) - 1)][0]
        tangent = next_point - previous_point
        if tangent.length < 0.0001:
            tangent = Vector((1.0, 0.0, 0.0))
        tangent.normalize()

        depth_axis = up_hint.copy()
        if abs(tangent.dot(depth_axis)) > 0.92:
            depth_axis = Vector((0.0, 0.0, 1.0))
        screen_axis = tangent.cross(depth_axis)
        if screen_axis.length < 0.0001:
            screen_axis = Vector((0.0, 0.0, 1.0))
        screen_axis.normalize()
        depth_axis = screen_axis.cross(tangent)
        depth_axis.normalize()

        for segment in range(ring_segments):
            angle = math.tau * segment / ring_segments
            offset = (
                depth_axis * math.cos(angle) * radius * depth_scale
                + screen_axis * math.sin(angle) * radius * screen_scale
            )
            co = point + offset
            verts.append((co.x, co.y, co.z))

    for ring in range(len(samples) - 1):
        base = ring * ring_segments
        next_base = (ring + 1) * ring_segments
        for segment in range(ring_segments):
            a = base + segment
            b = base + (segment + 1) % ring_segments
            c = next_base + (segment + 1) % ring_segments
            d = next_base + segment
            faces.append((a, b, c, d))

    start_center = len(verts)
    verts.append(tuple(samples[0][0]))
    end_center = len(verts)
    verts.append(tuple(samples[-1][0]))
    last_ring = (len(samples) - 1) * ring_segments
    for segment in range(ring_segments):
        faces.append((start_center, (segment + 1) % ring_segments, segment))
        faces.append((end_center, last_ring + segment, last_ring + (segment + 1) % ring_segments))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    st.assign_material(obj, material)
    st.shade_smooth(obj)
    weighted = obj.modifiers.new(f"{name}_WeightedNormals", "WEIGHTED_NORMAL")
    st.apply_modifier(obj, weighted.name)
    st.tag_object(obj, role="source_part", export=True)
    return obj


def create_meta_capsule(
    *,
    name: str,
    points: list[tuple[float, float, float]],
    radii: list[float],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    samples_per_segment: int = 5,
) -> bpy.types.Object:
    meta = bpy.data.metaballs.new(f"{name}_Meta")
    meta.resolution = 0.035
    meta.render_resolution = 0.020
    meta.threshold = 0.62
    obj = bpy.data.objects.new(f"{name}_MetaObject", meta)
    collection.objects.link(obj)
    samples = interpolate(points, radii, samples_per_segment=samples_per_segment)
    first = meta.elements.new(type="BALL")
    first.co = samples[0][0]
    first.radius = samples[0][1]
    first.stiffness = 2.0
    for co, radius in samples[1:]:
        elem = meta.elements.new(type="BALL")
        elem.co = co
        elem.radius = radius
        elem.stiffness = 2.0
    return convert_to_mesh(obj, name, material, collection)


def create_cylinder_cuff(collection: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=0.34,
        depth=0.46,
        location=(1.46, -0.45, -0.49),
        rotation=(0.0, math.radians(90), 0.0),
    )
    cuff = bpy.context.object
    cuff.name = "BHCV4_Cuff"
    st.move_to_collection(cuff, collection)
    st.shade_smooth(cuff)
    st.assign_material(cuff, mat)
    st.tag_object(cuff, role="source_part", export=True)
    return cuff


def create_bottom_hand_blockout(target: dict, collection: bpy.types.Collection, clay_mat: bpy.types.Material, cuff_mat: bpy.types.Material) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    palm_center = target_point(target, "palm_center", -0.62)
    palm_heel = target_point(target, "palm_heel", -0.70)
    thumb_web = target_point(target, "web_thumb_index", -0.60)
    thumb_base = target_point(target, "thumb_base", -0.61)
    finger_roots = [
        line_points(target, "index", -0.70)[0],
        line_points(target, "middle", -0.72)[0],
        line_points(target, "ring", -0.74)[0],
        line_points(target, "little", -0.76)[0],
    ]
    avg_root = (
        sum(point[0] for point in finger_roots) / len(finger_roots),
        -0.73,
        sum(point[2] for point in finger_roots) / len(finger_roots),
    )

    parts.append(
        st.create_ellipsoid(
            name="BHCV4_PalmCup",
            location=lerp_point(palm_center, palm_heel, 0.38),
            scale=(0.50, 0.20, 0.20),
            rotation=(0.0, math.radians(-11), math.radians(-2)),
            segments=56,
            rings=32,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )
    parts.append(
        st.create_ellipsoid(
            name="BHCV4_PalmHeel",
            location=palm_heel,
            scale=(0.30, 0.13, 0.12),
            rotation=(0.0, math.radians(-8), 0.0),
            segments=48,
            rings=24,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )
    parts.append(
        st.create_ellipsoid(
            name="BHCV4_FingerRootPad",
            location=avg_root,
            scale=(0.46, 0.105, 0.105),
            rotation=(0.0, math.radians(-13), 0.0),
            segments=48,
            rings=24,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )
    parts.append(
        st.create_ellipsoid(
            name="BHCV4_ThumbWebPad",
            location=lerp_point(thumb_web, thumb_base, 0.35),
            scale=(0.23, 0.12, 0.13),
            rotation=(0.0, math.radians(-18), 0.0),
            segments=40,
            rings=20,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )

    def add_tip(name: str, point: tuple[float, float, float], radius: float) -> None:
        parts.append(
            st.create_ellipsoid(
                name=f"{name}Tip",
                location=point,
                scale=(radius * 1.18, radius * 0.88, radius * 1.04),
                segments=36,
                rings=18,
                collection=collection,
                material=clay_mat,
                export=True,
            )
        )

    # v4: target-driven finger fan. Landmarks decide the front silhouette;
    # depth values only create a cupped 3D volume around that silhouette.
    finger_specs = []
    finger_depths = {
        "index": (-0.70, -0.90, 0.66),
        "middle": (-0.73, -0.93, 0.66),
        "ring": (-0.75, -0.92, 0.64),
        "little": (-0.77, -0.88, 0.62),
    }
    for line_id, (root_depth, tip_depth, radius_scale) in finger_depths.items():
        points, radii = target_line_depths(
            target,
            line_id,
            root_depth=root_depth,
            tip_depth=tip_depth,
            radius_scale=radius_scale,
            root_pull=avg_root,
        )
        # Push root inside palm for overlap, keep target tip exact for front match.
        points[0] = lerp_point(avg_root, points[1], 0.35)
        finger_specs.append((f"BHCV4_{line_id.title()}", points, radii))

    for name, points, radii in finger_specs:
        parts.append(
            create_tapered_tube_mesh(
                name=name,
                points=points,
                radii=radii,
                collection=collection,
                material=clay_mat,
                samples_per_segment=14,
                ring_segments=32,
            )
        )
        add_tip(name, points[-1], radii[-1])

    thumb_points, thumb_radii = target_line_depths(
        target,
        "thumb",
        root_depth=-0.61,
        tip_depth=-0.86,
        radius_scale=0.78,
        root_pull=thumb_web,
    )
    thumb_points[0] = lerp_point(thumb_web, thumb_points[1], 0.42)
    parts.append(
        create_tapered_tube_mesh(
            name="BHCV4_Thumb",
            points=thumb_points,
            radii=thumb_radii,
            collection=collection,
            material=clay_mat,
            samples_per_segment=14,
            ring_segments=32,
        )
    )
    add_tip("BHCV4_Thumb", thumb_points[-1], thumb_radii[-1])

    wrist_points, wrist_radii = target_line_depths(
        target,
        "wrist",
        root_depth=-0.48,
        tip_depth=-0.62,
        radius_scale=0.84,
        root_pull=(1.46, -0.46, -0.49),
    )
    parts.append(
        create_tapered_tube_mesh(
            name="BHCV4_Wrist",
            points=wrist_points,
            radii=wrist_radii,
            collection=collection,
            material=clay_mat,
            samples_per_segment=12,
            ring_segments=32,
        )
    )
    parts.append(create_cylinder_cuff(collection, cuff_mat))
    return parts


def render(path: Path, visible: list[bpy.types.Object], camera: str = "FRONT") -> dict:
    if camera == "FRONT":
        setup_camera("BHCV1_CAM_FRONT")
    elif camera == "FRONT_3Q":
        setup_orbit_camera("BHCV1_CAM_FRONT_3Q", (2.1, -7.3, 0.30), (0.10, 0.0, -0.52), 2.55)
    elif camera == "SIDE":
        setup_orbit_camera("BHCV1_CAM_SIDE", (7.1, -0.25, -0.28), (0.10, 0.0, -0.52), 2.55)

    scene = bpy.context.scene
    target_names = {obj.name for obj in visible}
    previous = {obj.name: obj.hide_render for obj in scene.objects}
    previous_view = {obj.name: obj.hide_get() for obj in scene.objects}
    try:
        for obj in scene.objects:
            if obj.type in {"CAMERA", "LIGHT"}:
                obj.hide_render = False
                obj.hide_set(False)
            else:
                shown = obj.name in target_names
                obj.hide_render = not shown
                obj.hide_set(not shown)
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        for obj in scene.objects:
            if obj.name in previous:
                obj.hide_render = previous[obj.name]
            if obj.name in previous_view:
                obj.hide_set(previous_view[obj.name])
    return {"path": str(path), "bytes": path.stat().st_size if path.is_file() else 0, "camera": camera, "objects": sorted(target_names)}


def main() -> dict:
    checkpoint = checkpoint_current_scene()
    probe = capability_probe.probe()
    target = load_target()
    create_clean_scene()
    collections = create_collections()
    setup_lighting()
    camera_info = setup_camera()

    scene_graph = {
        "schema_version": "bottom-hand-result-v4",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "stage": "target-driven smooth-tube bottom hand from bottom_hand_target_v1",
        "source_target": str(TARGET),
        "triangle_budget": 90000,
        "semantic_objects": [
            {"name": "palm", "sources": ["BHCV4_PalmCup", "BHCV4_PalmHeel", "BHCV4_FingerRootPad", "BHCV4_ThumbWebPad"]},
            {"name": "fingers", "sources": ["BHCV4_Index", "BHCV4_Middle", "BHCV4_Ring", "BHCV4_Little"]},
            {"name": "thumb", "sources": ["BHCV4_Thumb"]},
            {"name": "wrist", "sources": ["BHCV4_Wrist"]},
            {"name": "cuff", "sources": ["BHCV4_Cuff"]},
        ],
        "expected_contacts": [
            {"a": "finger roots", "b": "BHCV4_FingerRootPad/BHCV4_PalmCup", "relation": "OVERLAPS", "minimum": "visible overlap before any union"},
            {"a": "BHCV4_Thumb", "b": "BHCV4_ThumbWebPad/BHCV4_PalmCup", "relation": "OVERLAPS", "minimum": "thumb is separate but rooted"},
            {"a": "BHCV4_Wrist", "b": "BHCV4_Cuff/BHCV4_PalmCup", "relation": "OVERLAPS", "minimum": "wrist reaches cuff and palm"},
        ],
        "do_not_claim": [
            "not final",
            "not accepted",
            "not production render",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    clay_mat = material("BHCV4_MAT_WarmHand", (1.0, 0.61, 0.12, 1.0), 0.58)
    cuff_mat = material("BHCV4_MAT_SoftPinkCuff", (1.0, 0.78, 0.88, 1.0), 0.66)
    guide_mat = material("BHCV4_MAT_GuideSphere", (0.22, 0.66, 0.11, 0.48), 0.64, alpha=0.48)

    guide = create_guide_sphere(collections["guides"], guide_mat)
    parts = create_bottom_hand_blockout(target, collections["source"], clay_mat, cuff_mat)

    stage_renders = {
        "01_clay_front_with_guide": render(RENDERS / f"{ASSET}_01_clay_front_with_guide.png", [guide] + parts),
        "02_clay_front_hand_only": render(RENDERS / f"{ASSET}_02_clay_front_hand_only.png", parts),
        "03_clay_front_3q": render(RENDERS / f"{ASSET}_03_clay_front_3q.png", [guide] + parts, camera="FRONT_3Q"),
        "04_clay_side": render(RENDERS / f"{ASSET}_04_clay_side.png", [guide] + parts, camera="SIDE"),
    }

    object_names = [obj.name for obj in parts]
    validation = st.validate_shape_asset(
        object_names=object_names,
        max_triangles=90000,
        require_closed=True,
    )
    structural = scene_qa.audit_scene(object_names=object_names, contact_tolerance=0.08, floating_tolerance=0.16)

    export = {"status": "skipped"}
    if validation["status"] != "fail":
        export = st.export_glb(
            filepath=EXPORTS / f"{ASSET}.glb",
            object_names=object_names,
        )
        public_path = PUBLIC_MODELS / f"{ASSET}.glb"
        public_path.write_bytes((EXPORTS / f"{ASSET}.glb").read_bytes())
        export["public_copy"] = str(public_path)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    qa = {
        "status": "review_required",
        "stage": "clay_blockout",
        "active_gates": ["A", "D", "E"],
        "metrics": {
            "objects": len(object_names),
            "triangles": validation.get("summary", {}).get("triangles"),
            "errors": validation.get("summary", {}).get("errors"),
            "warnings": validation.get("summary", {}).get("warnings"),
        },
        "failed_gates": [
            "B/C not measured yet: no filled-mask overlay from clay render",
            "F not complete: visual acceptance required before treating as final production geometry",
        ],
        "observations": [
            "V4 uses hand_target centerlines/radii for fingers, thumb and wrist instead of hardcoded v3 fan coordinates.",
            "Fingers are kept separate and readable; sphere occludes root mass in the final web composition.",
            "Guide sphere is non-exported in Blender renders; web page still loads approved green sphere separately.",
        ],
        "next_action": "If visual pass is acceptable, perform front mask comparison and then controlled OUTPUT union.",
    }
    write_json(REPORTS / f"{ASSET}_qa.json", qa)

    report = {
        "status": "ok",
        "checkpoint": checkpoint,
        "probe": probe,
        "scene": SCENE_NAME,
        "camera": camera_info,
        "target": str(TARGET),
        "stage_renders": stage_renders,
        "validation": validation,
        "structural_qa": structural,
        "export": export,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.is_file() else 0},
        "qa": qa,
        "notes": [
            "This is a result-preview pass, not final production geometry.",
            "No destructive union was attempted; semantic sources remain readable.",
            "Do not call this accepted unless the visual pass is approved.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


result = main()
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
