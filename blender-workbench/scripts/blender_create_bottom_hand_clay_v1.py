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


ASSET = "bottom_hand_clay_v2"
SCENE_NAME = "BottomHandClayV2Scene"
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
    cuff.name = "BHCV1_Cuff"
    st.move_to_collection(cuff, collection)
    bevel = cuff.modifiers.new("BHCV1_Cuff_SoftBevel", "BEVEL")
    bevel.width = 0.055
    bevel.segments = 8
    bevel.limit_method = "NONE"
    st.apply_modifier(cuff, bevel.name)
    st.shade_smooth(cuff)
    st.assign_material(cuff, mat)
    st.tag_object(cuff, role="source_part", export=True)
    return cuff


def create_bottom_hand_blockout(target: dict, collection: bpy.types.Collection, clay_mat: bpy.types.Material, cuff_mat: bpy.types.Material) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []

    parts.append(
        st.create_ellipsoid(
            name="BHCV1_PalmCup",
            location=(-0.10, -0.55, -0.78),
            scale=(0.58, 0.20, 0.22),
            rotation=(0.0, math.radians(-14), math.radians(-2)),
            segments=56,
            rings=32,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )
    parts.append(
        st.create_ellipsoid(
            name="BHCV1_PalmHeel",
            location=(-0.42, -0.61, -0.92),
            scale=(0.34, 0.15, 0.15),
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
            name="BHCV1_FingerRootPad",
            location=(-0.12, -0.66, -0.96),
            scale=(0.50, 0.105, 0.105),
            rotation=(0.0, math.radians(-12), 0.0),
            segments=48,
            rings=24,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )
    parts.append(
        st.create_ellipsoid(
            name="BHCV1_ThumbWebPad",
            location=(0.38, -0.52, -0.56),
            scale=(0.24, 0.13, 0.15),
            rotation=(0.0, math.radians(-18), 0.0),
            segments=40,
            rings=20,
            collection=collection,
            material=clay_mat,
            export=True,
        )
    )

    # Manual v2 blockout: broad cupped pads, not landmark-to-tip dangling spikes.
    finger_specs = [
        (
            "BHCV1_Index",
            [(0.22, -0.66, -0.78), (-0.10, -0.76, -0.91), (-0.48, -0.71, -0.82), (-0.68, -0.55, -0.62)],
            [0.125, 0.135, 0.116, 0.088],
        ),
        (
            "BHCV1_Middle",
            [(0.12, -0.69, -0.92), (-0.18, -0.81, -1.06), (-0.48, -0.76, -1.00), (-0.64, -0.58, -0.82)],
            [0.128, 0.135, 0.112, 0.084],
        ),
        (
            "BHCV1_Ring",
            [(0.02, -0.71, -1.04), (-0.22, -0.80, -1.16), (-0.45, -0.72, -1.13), (-0.56, -0.56, -0.96)],
            [0.108, 0.114, 0.098, 0.076],
        ),
        (
            "BHCV1_Little",
            [(-0.10, -0.72, -1.11), (-0.27, -0.77, -1.20), (-0.42, -0.68, -1.18), (-0.47, -0.55, -1.06)],
            [0.086, 0.090, 0.078, 0.060],
        ),
    ]
    for name, points, radii in finger_specs:
        parts.append(
            create_meta_capsule(
                name=name,
                points=points,
                radii=radii,
                collection=collection,
                material=clay_mat,
                samples_per_segment=7,
            )
        )

    thumb_points = [(0.38, -0.52, -0.56), (0.55, -0.58, -0.34), (0.76, -0.52, -0.22)]
    thumb_radii = [0.145, 0.132, 0.100]
    parts.append(
        create_meta_capsule(
            name="BHCV1_Thumb",
            points=thumb_points,
            radii=thumb_radii,
            collection=collection,
            material=clay_mat,
            samples_per_segment=7,
        )
    )

    wrist_points = [(1.48, -0.48, -0.52), (1.03, -0.47, -0.52), (0.54, -0.50, -0.60), (0.12, -0.55, -0.76)]
    wrist_radii = [0.215, 0.210, 0.178, 0.142]
    parts.append(
        create_meta_capsule(
            name="BHCV1_Wrist",
            points=wrist_points,
            radii=wrist_radii,
            collection=collection,
            material=clay_mat,
            samples_per_segment=7,
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
        "schema_version": "bottom-hand-clay-v1",
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "stage": "clay blockout from bottom_hand_target_v1",
        "source_target": str(TARGET),
        "triangle_budget": 90000,
        "semantic_objects": [
            {"name": "palm", "sources": ["BHCV1_PalmCup", "BHCV1_PalmHeel", "BHCV1_FingerRootPad", "BHCV1_ThumbWebPad"]},
            {"name": "fingers", "sources": ["BHCV1_Index", "BHCV1_Middle", "BHCV1_Ring", "BHCV1_Little"]},
            {"name": "thumb", "sources": ["BHCV1_Thumb"]},
            {"name": "wrist", "sources": ["BHCV1_Wrist"]},
            {"name": "cuff", "sources": ["BHCV1_Cuff"]},
        ],
        "expected_contacts": [
            {"a": "finger roots", "b": "BHCV1_FingerRootPad/BHCV1_PalmCup", "relation": "OVERLAPS", "minimum": "visible overlap before any union"},
            {"a": "BHCV1_Thumb", "b": "BHCV1_ThumbWebPad/BHCV1_PalmCup", "relation": "OVERLAPS", "minimum": "thumb is separate but rooted"},
            {"a": "BHCV1_Wrist", "b": "BHCV1_Cuff/BHCV1_PalmCup", "relation": "OVERLAPS", "minimum": "wrist reaches cuff and palm"},
        ],
        "do_not_claim": [
            "not final",
            "not accepted",
            "not production render",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    clay_mat = material("BHCV1_MAT_ClayHand", (0.86, 0.78, 0.66, 1.0), 0.72)
    cuff_mat = material("BHCV1_MAT_ClayCuff", (0.90, 0.78, 0.82, 1.0), 0.74)
    guide_mat = material("BHCV1_MAT_GuideSphere", (0.18, 0.58, 0.08, 0.25), 0.64, alpha=0.25)

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
            "F not complete: clay approval required before final material/render",
        ],
        "observations": [
            "New blockout uses target landmarks and separate semantic parts.",
            "Fingers are kept separate for readability before destructive union.",
            "Guide sphere is non-exported in Blender renders; web page still loads approved green sphere separately.",
        ],
        "next_action": "If visual clay pass is acceptable, perform front mask comparison and then controlled OUTPUT union.",
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
            "This is a clay blockout, not final production geometry.",
            "No final material/lookdev was attempted.",
            "Do not call this accepted unless the visual clay pass is approved.",
        ],
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


result = main()
print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
