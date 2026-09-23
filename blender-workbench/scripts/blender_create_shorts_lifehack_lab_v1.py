from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
WORKBENCH = SCRIPT.parents[1]
REPO = SCRIPT.parents[2]
ARTIFACTS = WORKBENCH / "artifacts"
RENDERS = ARTIFACTS / "renders"
REPORTS = ARTIFACTS / "reports"
EXPORTS = ARTIFACTS / "exports"
BLENDS = ARTIFACTS / "blend"
PUBLIC_MODELS = REPO / "public" / "models"

ASSET = "blender_shorts_lifehack_lab_v1"
SCENE_NAME = "BlenderShortsLifehackLabV1"
END_FRAME = 96
FPS = 24
WIDTH = 1200
HEIGHT = 900

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)


APPLIED_LIFEHACKS = [
    {
        "id": "BH-041",
        "name": "Curve Direction Is Data",
        "applied": "Directional curve strokes use arrowheads and flow markers so path direction is visible.",
        "sources": ["https://www.youtube.com/shorts/uGEqAQQxtLM"],
    },
    {
        "id": "BH-042",
        "name": "Stylized Strands From Curves",
        "applied": "Editable bevel-depth curves create fast anime-style energy/hair strokes.",
        "sources": [
            "https://www.youtube.com/shorts/5by_eD6EM44",
            "https://www.youtube.com/shorts/XlXLyZH5f38",
        ],
    },
    {
        "id": "BH-048",
        "name": "Mirror And Array Before Manual Duplication",
        "applied": "Repeated blocks are arranged radially with systematic phase/scale offsets.",
        "sources": [
            "https://www.youtube.com/shorts/B1Vxh2-8cpY",
            "https://www.youtube.com/shorts/jdWcYsBkGsQ",
        ],
    },
    {
        "id": "BH-049",
        "name": "Turntable As QA",
        "applied": "The asset root has a clean 96-frame turntable animation.",
        "sources": ["https://www.youtube.com/shorts/uafPg27H4ms"],
    },
    {
        "id": "BH-050",
        "name": "Origins Are Animation Controls",
        "applied": "A hinge panel rotates around a visible side pivot empty.",
        "sources": ["https://www.youtube.com/shorts/6xq2n7rtpGQ"],
    },
    {
        "id": "BH-052",
        "name": "Normals First When Shadows Look Wrong",
        "applied": "Hard-surface modules use bevels plus weighted normals before lighting polish.",
        "sources": [
            "https://www.youtube.com/shorts/KMM8-bjcRsg",
            "https://www.youtube.com/shorts/OYBC4mN5-_s",
        ],
    },
    {
        "id": "BH-055",
        "name": "Variation For Repeated Assets",
        "applied": "Repeated chips vary color, height, rotation and scale while keeping one visual family.",
        "sources": ["https://www.youtube.com/shorts/nyjp2B3q_6Y"],
    },
]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object, location: bool = False, rotation: bool = False, scale: bool = True) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def make_mat(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.55,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            "Base Color": color,
            "Roughness": roughness,
            "Metallic": metallic,
            "Alpha": color[3],
            "Specular IOR Level": 0.46,
            "Coat Weight": 0.05,
            "Coat Roughness": 0.28,
        }
        for key, value in values.items():
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        if emission is not None:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def make_materials() -> dict[str, bpy.types.Material]:
    return {
        "ink": make_mat("Lab_Ink", (0.025, 0.027, 0.035, 1.0), roughness=0.42),
        "paper": make_mat("Lab_PaperWarm", (0.88, 0.84, 0.74, 1.0), roughness=0.68),
        "cyan": make_mat("Lab_CyanGlow", (0.07, 0.72, 1.0, 1.0), roughness=0.28, emission=(0.02, 0.42, 1.0, 1.0), emission_strength=0.35),
        "pink": make_mat("Lab_PinkGlow", (1.0, 0.15, 0.58, 1.0), roughness=0.32, emission=(1.0, 0.08, 0.35, 1.0), emission_strength=0.28),
        "gold": make_mat("Lab_Gold", (1.0, 0.68, 0.16, 1.0), roughness=0.34, metallic=0.18),
        "violet": make_mat("Lab_Violet", (0.35, 0.12, 0.92, 1.0), roughness=0.38),
        "green": make_mat("Lab_Green", (0.24, 0.95, 0.34, 1.0), roughness=0.44, emission=(0.06, 0.45, 0.12, 1.0), emission_strength=0.12),
        "white": make_mat("Lab_White", (0.96, 0.94, 0.88, 1.0), roughness=0.6),
        "grid_a": make_mat("Lab_UVGridA", (0.93, 0.92, 0.86, 1.0), roughness=0.7),
        "grid_b": make_mat("Lab_UVGridB", (0.12, 0.16, 0.22, 1.0), roughness=0.54),
        "axis_red": make_mat("Lab_AxisRed", (1.0, 0.08, 0.08, 1.0), roughness=0.4, emission=(1.0, 0.02, 0.02, 1.0), emission_strength=0.2),
        "axis_blue": make_mat("Lab_AxisBlue", (0.08, 0.25, 1.0, 1.0), roughness=0.4, emission=(0.02, 0.08, 1.0, 1.0), emission_strength=0.2),
    }


def rounded_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.04,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj)
    obj.data.materials.append(mat)
    if bevel > 0:
        mod = obj.modifiers.new(name="LAB_BevelWeightedNormal_Bevel", type="BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.affect = "EDGES"
        mod.profile = 0.5
        normal = obj.modifiers.new(name="LAB_BevelWeightedNormal_WeightedNormals", type="WEIGHTED_NORMAL")
        normal.keep_sharp = True
    return tag(obj, "rounded_box")


def add_cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    vertices: int = 24,
    rot: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth_mesh(obj)
    return tag(obj, "cylinder")


def smooth_mesh(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if not any(mod.type == "WEIGHTED_NORMAL" for mod in obj.modifiers):
            obj.modifiers.new(name="LAB_WeightedNormals", type="WEIGHTED_NORMAL")


def make_curve_stroke(
    name: str,
    points: list[tuple[float, float, float]],
    mat: bpy.types.Material,
    bevel_depth: float,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name=name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return tag(obj, "curve_stroke")


def add_cone_arrow(name: str, loc: Vector, direction: Vector, mat: bpy.types.Material, radius: float = 0.07) -> bpy.types.Object:
    direction = direction.normalized()
    quat = direction.to_track_quat("Z", "Y")
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=radius, radius2=0.0, depth=radius * 2.8, location=loc, rotation=quat.to_euler())
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    smooth_mesh(obj)
    return tag(obj, "curve_direction_arrow")


def add_text(
    name: str,
    text: str,
    loc: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    rot: tuple[float, float, float] = (math.radians(70), 0, 0),
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.012
    obj.data.bevel_depth = 0.0
    obj.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smooth_mesh(obj)
    return tag(obj, "preview_label", export=False)


def make_uv_grid(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    origin_x = -0.54
    origin_y = -0.54
    cell = 0.18
    for row in range(6):
        for col in range(6):
            mat = mats["grid_a"] if (row + col) % 2 == 0 else mats["grid_b"]
            obj = rounded_box(
                f"LAB_UVGrid_Cell_{row}_{col}",
                (cell * 0.92, cell * 0.92, 0.018),
                (origin_x + col * cell, 0.05 + origin_y + row * cell, 0.028),
                mat,
                bevel=0.002,
            )
            parts.append(obj)
    return parts


def make_array_ring(mats: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    parts: list[bpy.types.Object] = []
    palette = [mats["cyan"], mats["pink"], mats["gold"], mats["violet"], mats["green"]]
    for i in range(12):
        angle = math.tau * i / 12.0
        radius = 1.52 + 0.08 * math.sin(i * 1.7)
        height = 0.10 + 0.045 * (i % 4)
        sx = 0.20 + 0.025 * (i % 3)
        sy = 0.12 + 0.018 * ((i + 1) % 3)
        obj = rounded_box(
            f"LAB_ArrayVar_Block_{i:02d}",
            (sx, sy, height),
            (math.cos(angle) * radius, math.sin(angle) * radius, 0.13 + height * 0.5),
            palette[i % len(palette)],
            bevel=0.025,
        )
        obj.rotation_euler[2] = angle + math.radians(28 + i * 3)
        obj.rotation_euler[0] = math.radians(4 * math.sin(i))
        tag(obj, "array_variation_block")
        parts.append(obj)
    return parts


def make_hinge_demo(mats: dict[str, bpy.types.Material]) -> tuple[bpy.types.Object, bpy.types.Object, list[bpy.types.Object]]:
    pivot = bpy.data.objects.new("LAB_HingePivot_OriginControl", None)
    pivot.empty_display_type = "SPHERE"
    pivot.empty_display_size = 0.12
    pivot.location = (-1.36, -0.78, 0.28)
    tag(pivot, "pivot_empty", export=True)
    bpy.context.collection.objects.link(pivot)

    panel = rounded_box("LAB_HingePanel_RotatesFromSideOrigin", (0.66, 0.12, 0.36), (-1.03, -0.78, 0.28), mats["paper"], bevel=0.035)
    parent_keep_world(panel, pivot)
    pivot.rotation_euler[2] = math.radians(-22)
    pivot.keyframe_insert(data_path="rotation_euler", frame=1)
    pivot.rotation_euler[2] = math.radians(38)
    pivot.keyframe_insert(data_path="rotation_euler", frame=48)
    pivot.rotation_euler[2] = math.radians(-22)
    pivot.keyframe_insert(data_path="rotation_euler", frame=96)
    linearize_action(pivot)

    axis = add_cylinder(
        "LAB_HingeAxis_VisiblePivot",
        0.035,
        0.46,
        (-1.36, -0.78, 0.28),
        mats["axis_red"],
        vertices=32,
        rot=(math.radians(90), 0, 0),
    )
    tag(axis, "visible_pivot_axis")
    return pivot, panel, [axis]


def linearize_action(obj: bpy.types.Object) -> None:
    action = obj.animation_data.action if obj.animation_data else None
    fcurves = getattr(action, "fcurves", None)
    if fcurves is None:
        return
    for fcurve in fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = "LINEAR"


def configure_animation(obj: bpy.types.Object) -> None:
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = END_FRAME
    bpy.context.scene.render.fps = FPS
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    obj.rotation_euler = (0, 0, math.tau)
    obj.keyframe_insert(data_path="rotation_euler", frame=END_FRAME)
    linearize_action(obj)


def setup_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.eevee.taa_render_samples = 96
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    world = scene.world or bpy.data.worlds.new("LAB_World")
    scene.world = world
    world.color = (0.022, 0.024, 0.03)


def setup_lights() -> None:
    bpy.ops.object.light_add(type="AREA", location=(-3.5, -4.2, 5.0))
    key = bpy.context.object
    key.name = "LAB_KeyArea_Warm"
    key.data.energy = 520
    key.data.size = 4.3
    tag(key, "key_light", export=False)

    bpy.ops.object.light_add(type="AREA", location=(3.4, 2.5, 3.0))
    fill = bpy.context.object
    fill.name = "LAB_FillArea_Cyan"
    fill.data.energy = 80
    fill.data.size = 5.0
    fill.data.color = (0.50, 0.78, 1.0)
    tag(fill, "fill_light", export=False)

    bpy.ops.object.light_add(type="POINT", location=(0, 3.1, 2.1))
    rim = bpy.context.object
    rim.name = "LAB_RimPoint_Pink"
    rim.data.energy = 190
    rim.data.color = (1.0, 0.22, 0.62)
    tag(rim, "rim_light", export=False)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(3.2, -4.5, 3.0), rotation=(math.radians(60), 0, math.radians(39)))
    cam = bpy.context.object
    cam.name = "LAB_Camera_Hero3Q"
    cam.data.lens = 45
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 5.0
    cam.data.dof.aperture_fstop = 7.5
    bpy.context.scene.camera = cam
    tag(cam, "camera", export=False)


def build_scene() -> dict:
    setup_scene()
    mats = make_materials()

    root = bpy.data.objects.new("LAB_Root_TurntableAnimated", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.5
    tag(root, "animated_root", export=True)
    bpy.context.collection.objects.link(root)

    floor = rounded_box("LAB_DisplayBase_NotExportedFloor", (4.2, 3.2, 0.08), (0, 0, -0.05), mats["ink"], bevel=0.05)
    tag(floor, "preview_floor", export=False)

    podium = rounded_box("LAB_CentralRoundedPanel_BevelWeightedNormals", (1.55, 1.1, 0.13), (0, 0, 0.035), mats["paper"], bevel=0.055)
    parent_keep_world(podium, root)

    uv_cells = make_uv_grid(mats)
    for obj in uv_cells:
        parent_keep_world(obj, root)

    flow_a = make_curve_stroke(
        "LAB_CurveFlow_Cyan_DirectionalStroke",
        [(-1.30, 0.55, 0.22), (-0.65, 1.10, 0.48), (0.20, 1.02, 0.38), (0.92, 0.62, 0.58)],
        mats["cyan"],
        0.025,
    )
    flow_b = make_curve_stroke(
        "LAB_CurveFlow_Pink_DirectionalStroke",
        [(1.20, -0.40, 0.27), (0.55, -1.05, 0.55), (-0.40, -0.98, 0.42), (-1.02, -0.50, 0.48)],
        mats["pink"],
        0.018,
    )
    for curve, mat in ((flow_a, mats["cyan"]), (flow_b, mats["pink"])):
        points = [p.co.copy() for p in curve.data.splines[0].bezier_points]
        arrow = add_cone_arrow(f"{curve.name}_ArrowHead", points[-1], points[-1] - points[-2], mat)
        parent_keep_world(curve, root)
        parent_keep_world(arrow, root)

    for obj in make_array_ring(mats):
        parent_keep_world(obj, root)

    pivot, panel, hinge_parts = make_hinge_demo(mats)
    parent_keep_world(pivot, root)
    for obj in hinge_parts:
        parent_keep_world(obj, root)

    axis_x = add_cylinder("LAB_NormalAxis_X_Red", 0.018, 1.35, (0.70, -0.95, 0.11), mats["axis_red"], vertices=24, rot=(0, math.radians(90), 0))
    axis_z = add_cylinder("LAB_NormalAxis_Z_Blue", 0.018, 0.70, (0.70, -0.95, 0.44), mats["axis_blue"], vertices=24)
    parent_keep_world(axis_x, root)
    parent_keep_world(axis_z, root)

    labels = [
        add_text("LAB_Label_CurveFlow", "CURVE FLOW", (0.0, 1.42, 0.30), 0.12, mats["white"]),
        add_text("LAB_Label_ArrayVariation", "ARRAY VARIATION", (0.0, -1.50, 0.30), 0.105, mats["white"]),
        add_text("LAB_Label_Pivot", "SIDE PIVOT", (-1.55, -0.28, 0.34), 0.095, mats["gold"]),
        add_text("LAB_Label_UVGrid", "UV GRID QA", (0.0, 0.03, 0.20), 0.095, mats["ink"], rot=(math.radians(90), 0, 0)),
    ]
    for label in labels:
        parent_keep_world(label, root)

    configure_animation(root)
    setup_lights()
    setup_camera()

    return {
        "root": root,
        "materials": mats,
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "export_object_names": [obj.name for obj in bpy.data.objects if obj.get("abt_export") is True],
    }


def exportable_objects() -> list[bpy.types.Object]:
    return [obj for obj in bpy.data.objects if obj.get("abt_export") is True]


def mesh_triangle_count(obj: bpy.types.Object, depsgraph: bpy.types.Depsgraph) -> int:
    if obj.type != "MESH":
        return 0
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    try:
        return sum(len(poly.vertices) - 2 for poly in mesh.polygons)
    finally:
        eval_obj.to_mesh_clear()


def validate_scene() -> dict:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objects = exportable_objects()
    errors: list[str] = []
    warnings: list[str] = []
    mesh_objects = [obj for obj in objects if obj.type == "MESH"]
    if not mesh_objects:
        errors.append("No exportable mesh objects.")
    triangles = sum(mesh_triangle_count(obj, depsgraph) for obj in mesh_objects)
    if triangles > 25000:
        warnings.append(f"Triangle count {triangles} exceeds lab target 25000.")
    for obj in mesh_objects:
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material.")
        for vertex in obj.data.vertices:
            co = obj.matrix_world @ vertex.co
            if not all(math.isfinite(v) for v in (co.x, co.y, co.z)):
                errors.append(f"{obj.name} has non-finite coordinates.")
                break
        for poly in obj.data.polygons:
            if poly.area <= 1e-10:
                warnings.append(f"{obj.name} has a near-zero-area face.")
                break
    non_exported = [obj.name for obj in bpy.data.objects if obj.get("abt_export") is False]
    return {
        "asset": ASSET,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "triangles": triangles,
        "exportable_objects": len(objects),
        "exportable_meshes": len(mesh_objects),
        "non_exported_helpers": non_exported,
        "animation": {
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": bpy.context.scene.render.fps,
            "animated_roots": [obj.name for obj in objects if obj.animation_data and obj.animation_data.action],
        },
    }


def render_preview(frame: int, suffix: str) -> Path:
    scene = bpy.context.scene
    scene.frame_set(frame)
    path = RENDERS / f"{ASSET}_{suffix}.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path


def export_glb(path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable_objects():
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_lights=False,
        export_cameras=False,
        export_apply=True,
    )


def main() -> None:
    build = build_scene()
    scene_graph = {
        "asset": ASSET,
        "scene": SCENE_NAME,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "icon/hero object",
        "source_goal": "Apply Blender Shorts lifehacks as a compact test asset.",
        "applied_lifehacks": APPLIED_LIFEHACKS,
        "parts": [
            {"name": obj.name, "type": obj.type, "role": obj.get("role"), "export": bool(obj.get("abt_export"))}
            for obj in bpy.data.objects
        ],
        "acceptance": [
            "PNG preview exists.",
            "GLB exists and has non-zero size.",
            "Only objects with abt_export=True are selected for GLB.",
            "Triangle count remains below 25k.",
            "Turntable root and hinge pivot contain animation keyframes.",
        ],
        "export_object_names": build["export_object_names"],
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", scene_graph)

    preview = render_preview(24, "preview_frame_024")
    render_preview(1, "frame_001")
    render_preview(48, "frame_048")
    render_preview(96, "frame_096")

    validation = validate_scene()
    write_json(REPORTS / f"{ASSET}_validation.json", validation)
    if validation["errors"]:
        raise RuntimeError(f"Validation failed: {validation['errors']}")

    glb = EXPORTS / f"{ASSET}.glb"
    export_glb(glb)
    (PUBLIC_MODELS / f"{ASSET}.glb").write_bytes(glb.read_bytes())

    blend = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    scene_report = {
        "asset": ASSET,
        "preview": str(preview),
        "glb": str(glb),
        "public_glb": str(PUBLIC_MODELS / f"{ASSET}.glb"),
        "blend": str(blend),
        "validation": validation,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", scene_report)
    print(json.dumps(scene_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
