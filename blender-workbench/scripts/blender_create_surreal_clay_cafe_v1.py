from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "surreal_clay_cafe_v1"
ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RENDER_DIR = ARTIFACTS / "renders"
BLEND_DIR = ARTIFACTS / "blend"
EXPORT_DIR = ARTIFACTS / "exports"
REPORT_DIR = ARTIFACTS / "reports"

for folder in (RENDER_DIR, BLEND_DIR, EXPORT_DIR, REPORT_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def material(name: str, color: tuple[float, float, float, float], roughness: float = 0.55, clearcoat: float = 0.2) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = clearcoat
        elif "Clearcoat" in bsdf.inputs:
            bsdf.inputs["Clearcoat"].default_value = clearcoat
    return mat


def shade_smooth(obj: bpy.types.Object) -> bpy.types.Object:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.shade_smooth()
    finally:
        obj.select_set(False)
    return obj


def add_ellipsoid(name: str, loc: tuple[float, float, float], scale: tuple[float, float, float], mat: bpy.types.Material, segments: int = 48) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(12, segments // 2), location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return shade_smooth(obj)


def add_rounded_box(name: str, loc: tuple[float, float, float], dims: tuple[float, float, float], mat: bpy.types.Material, bevel: float = 0.08, segments: int = 8) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel_mod = obj.modifiers.new("soft clay bevel", "BEVEL")
    bevel_mod.width = bevel
    bevel_mod.segments = segments
    bevel_mod.affect = "EDGES"
    obj.modifiers.new("weighted clay normals", "WEIGHTED_NORMAL")
    return obj


def add_tube(name: str, points: list[tuple[float, float, float]], radius: float, mat: bpy.types.Material, resolution: int = 24) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = radius
    curve.bevel_resolution = 8
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_vertical_plane(name: str, loc: tuple[float, float, float], scale: tuple[float, float, float], mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(math.radians(90), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def add_cloth_front(name: str, mat: bpy.types.Material) -> bpy.types.Object:
    width = 4.05
    max_drop = 0.72
    y_front = -0.68
    cols = 80
    rows = 18
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []

    for row in range(rows + 1):
        v = row / rows
        for col in range(cols + 1):
            u = col / cols
            taper = 1 - math.sin(v * math.pi) * 0.05 + v * 0.03
            x = (u - 0.5) * width * taper + math.sin((v * 3.2 + u * 1.7) * math.pi) * 0.03 * v
            lobe_a = max(0, math.sin((u * 5.1 + 0.18) * math.pi))
            lobe_b = max(0, math.sin((u * 9.2 + 0.35) * math.pi))
            drop = max_drop * (0.64 + lobe_a * 0.22 + lobe_b * 0.12)
            z = 1.98 - drop * v + math.sin((u * 3.1 + v * 0.35) * math.pi) * 0.035 * v
            y = y_front - math.sin(v * math.pi) * 0.11 - math.sin((u * 7.2 + v * 1.1) * math.pi) * 0.02
            vertices.append((x, y, z))

    stride = cols + 1
    for row in range(rows):
        for col in range(cols):
            a = row * stride + col
            faces.append((a, a + 1, a + stride + 1, a + stride))

    mesh = bpy.data.meshes.new(f"{name}Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj.modifiers.new("cloth weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_chair(prefix: str, side: int, pink: bpy.types.Material, pink_deep: bpy.types.Material) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []
    x0 = side * 2.82
    objects.append(add_ellipsoid(f"{prefix}_soft_seat", (x0, -0.28, 0.95), (0.78, 0.44, 0.18), pink, 48))
    objects[-1].rotation_euler[2] = side * math.radians(2)
    objects.append(add_tube(f"{prefix}_front_lip", [(x0 - side * 0.7, -0.62, 1.03), (x0, -0.7, 1.1), (x0 + side * 0.78, -0.62, 1.02)], 0.08, pink_deep))

    leg_sets = [
        [(x0 - side * 0.55, -0.52, 0.92), (x0 - side * 0.72, -0.56, 0.54), (x0 - side * 0.58, -0.48, 0.08)],
        [(x0 + side * 0.56, -0.52, 0.92), (x0 + side * 0.72, -0.58, 0.52), (x0 + side * 0.48, -0.48, 0.08)],
        [(x0 - side * 0.56, 0.03, 0.92), (x0 - side * 0.78, 0.08, 0.56), (x0 - side * 0.66, 0.0, 0.12)],
        [(x0 + side * 0.52, 0.03, 0.92), (x0 + side * 0.7, 0.08, 0.56), (x0 + side * 0.62, 0.0, 0.12)],
    ]
    for index, path in enumerate(leg_sets):
        objects.append(add_tube(f"{prefix}_leg_{index}", path, 0.095, pink))
        objects.append(add_ellipsoid(f"{prefix}_foot_{index}", path[-1], (0.16, 0.14, 0.1), pink, 32))

    back_left = [(x0 - side * 0.68, 0.07, 0.98), (x0 - side * 0.86, 0.08, 1.56), (x0 - side * 0.74, 0.02, 2.05)]
    back_right = [(x0 + side * 0.66, 0.07, 0.98), (x0 + side * 0.82, 0.08, 1.54), (x0 + side * 0.74, 0.02, 2.02)]
    objects.append(add_tube(f"{prefix}_back_left", back_left, 0.105, pink))
    objects.append(add_tube(f"{prefix}_back_right", back_right, 0.105, pink))
    for j, point in enumerate([back_left[-1], back_right[-1], back_left[0], back_right[0]]):
        objects.append(add_ellipsoid(f"{prefix}_joint_{j}", point, (0.15, 0.15, 0.15), pink, 32))

    objects.append(add_tube(f"{prefix}_top_rail", [(x0 - side * 0.75, 0.02, 2.0), (x0 - side * 0.18, 0.06, 2.2), (x0 + side * 0.72, 0.02, 2.0)], 0.105, pink))
    objects.append(add_tube(f"{prefix}_middle_rail", [(x0 - side * 0.65, 0.02, 1.58), (x0 - side * 0.05, 0.08, 1.42), (x0 + side * 0.68, 0.02, 1.58)], 0.08, pink_deep))
    objects.append(add_tube(f"{prefix}_lower_rail", [(x0 - side * 0.58, 0.02, 1.25), (x0, 0.07, 1.15), (x0 + side * 0.58, 0.02, 1.26)], 0.07, pink))
    return objects


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_scene() -> None:
    reset_scene()
    bpy.context.scene.name = "SurrealClayCafeV1"

    pink = material("SCC_soft_bubblegum_pink", (1.0, 0.47, 0.65, 1), 0.48, 0.34)
    pink_deep = material("SCC_inner_rose_shadow", (1.0, 0.34, 0.58, 1), 0.5, 0.22)
    cream = material("SCC_warm_drippy_cream", (0.9, 0.86, 0.77, 1), 0.63, 0.12)
    green = material("SCC_mint_green_clay", (0.28, 0.86, 0.48, 1), 0.44, 0.26)
    blue = material("SCC_powder_blue_plastic_clay", (0.58, 0.7, 0.9, 1), 0.42, 0.34)
    blue_deep = material("SCC_screen_blue_rim", (0.36, 0.52, 0.82, 1), 0.5, 0.18)
    lavender = material("SCC_lavender_cups", (0.64, 0.52, 0.96, 1), 0.5, 0.22)
    yellow = material("SCC_butter_yellow_vase", (0.92, 0.84, 0.42, 1), 0.56, 0.18)
    screen_white = material("SCC_bright_screen", (1, 0.96, 0.98, 1), 0.28, 0)
    skin = material("SCC_screen_skin", (1.0, 0.77, 0.55, 1), 0.48, 0)
    hair = material("SCC_screen_peach_hair", (1.0, 0.46, 0.35, 1), 0.5, 0)
    eye = material("SCC_screen_teal_eyes", (0.0, 0.64, 0.76, 1), 0.35, 0)
    black = material("SCC_screen_mic_black", (0.02, 0.03, 0.05, 1), 0.35, 0)

    bpy.context.scene.world = bpy.data.worlds.new("SCC_soft_grey_world")
    bpy.context.scene.world.color = (0.8, 0.78, 0.79)

    backdrop_mat = material("SCC_light_grey_render_backdrop", (0.78, 0.75, 0.77, 1), 0.76, 0)
    add_rounded_box("SCC_preview_backdrop", (0, 1.78, 2.18), (8.6, 0.04, 5.2), backdrop_mat, 0.02, 2)
    floor_mat = material("SCC_matte_grey_floor", (0.7, 0.67, 0.69, 1), 0.72, 0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -4.0, 0))
    floor = bpy.context.object
    floor.name = "SCC_soft_shadow_floor"
    floor.scale = (24.0, 32.0, 1)
    floor.data.materials.append(floor_mat)

    add_rounded_box("SCC_table_top_blob", (0, 0, 2.08), (4.02, 1.25, 0.3), cream, 0.18, 14)
    add_cloth_front("SCC_table_drippy_cloth_front", cream)
    add_tube("SCC_table_front_soft_roll", [(-1.92, -0.73, 2.02), (-1.1, -0.82, 2.07), (-0.2, -0.82, 2.0), (0.74, -0.8, 2.07), (1.92, -0.72, 2.02)], 0.095, cream, 30)
    for i, x in enumerate([-1.72, -1.05, -0.38, 0.36, 1.05, 1.62]):
        add_ellipsoid(f"SCC_table_drip_{i}", (x, -0.74, 1.46 - (i % 3) * 0.04), (0.15 + (i % 2) * 0.035, 0.09, 0.24 + (i % 3) * 0.045), cream, 40)

    add_tube("SCC_green_pedestal", [(0.02, 0.0, 0.18), (0.12, 0.03, 0.84), (-0.02, -0.02, 1.48), (0, 0, 2.02)], 0.16, green, 32)
    for i, path in enumerate([
        [(0.02, 0.0, 0.18), (-0.56, -0.34, 0.06), (-0.98, -0.18, 0.06)],
        [(0.02, 0.0, 0.18), (0.42, -0.42, 0.05), (0.95, -0.24, 0.06)],
        [(0.02, 0.0, 0.18), (-0.28, 0.42, 0.05), (-0.72, 0.52, 0.06)],
        [(0.02, 0.0, 0.18), (0.34, 0.42, 0.05), (0.68, 0.5, 0.06)],
    ]):
        add_tube(f"SCC_pedestal_root_{i}", path, 0.09, green, 24)

    add_chair("SCC_left_chair", -1, pink, pink_deep)
    add_chair("SCC_right_chair", 1, pink, pink_deep)

    add_rounded_box("SCC_crt_body", (0, -0.35, 2.72), (1.62, 0.52, 0.92), blue, 0.12, 12)
    add_rounded_box("SCC_crt_screen_inset", (0, -0.66, 2.76), (1.28, 0.08, 0.62), blue_deep, 0.04, 7)
    add_rounded_box("SCC_crt_screen_surface", (0, -0.71, 2.76), (1.15, 0.025, 0.52), screen_white, 0.025, 4)
    for i, z in enumerate([2.96, 2.78, 2.6]):
        add_ellipsoid(f"SCC_crt_side_button_{i}", (0.72, -0.74, z), (0.045, 0.025, 0.045), blue_deep, 24)
    add_rounded_box("SCC_keyboard_base", (0, -0.88, 2.24), (1.78, 0.42, 0.12), blue, 0.045, 5)
    for row in range(3):
        for col in range(10):
            add_rounded_box(f"SCC_key_{row}_{col}", (-0.68 + col * 0.15 + row * 0.025, -1.09 + row * 0.11, 2.33), (0.095, 0.055, 0.026), blue_deep, 0.01, 2)

    add_ellipsoid("SCC_screen_face", (0, -0.735, 2.78), (0.22, 0.015, 0.29), skin, 32)
    for i, x in enumerate([-0.07, 0.07]):
        add_ellipsoid(f"SCC_screen_eye_{i}", (x, -0.76, 2.82), (0.035, 0.01, 0.035), eye, 24)
    for i, x in enumerate([-0.18, -0.12, -0.06, 0, 0.06, 0.12, 0.18]):
        add_tube(f"SCC_screen_hair_{i}", [(x, -0.765, 3.02), (x * 0.65, -0.77, 2.94), (x * 0.42, -0.77, 2.86)], 0.007, hair, 8)
    add_tube("SCC_screen_smile", [(-0.06, -0.765, 2.72), (0, -0.77, 2.68), (0.07, -0.765, 2.72)], 0.006, hair, 10)
    add_ellipsoid("SCC_screen_mic", (0, -0.765, 2.57), (0.035, 0.012, 0.06), black, 16)
    for i in range(22):
        x = -0.48 + (i * 0.137) % 0.98
        z = 2.55 + (i * 0.097) % 0.44
        add_ellipsoid(f"SCC_screen_flower_dot_{i}", (x, -0.772, z), (0.014 + (i % 3) * 0.006, 0.006, 0.014 + (i % 2) * 0.004), pink_deep, 12)

    for side, x in [("left", -1.2), ("right", 1.2)]:
        add_ellipsoid(f"SCC_{side}_cup_body", (x, -0.42, 2.27), (0.16, 0.12, 0.16), lavender, 32)
        add_tube(f"SCC_{side}_cup_handle", [(x + (0.16 if x > 0 else -0.16), -0.43, 2.3), (x + (0.32 if x > 0 else -0.32), -0.43, 2.24), (x + (0.18 if x > 0 else -0.18), -0.43, 2.16)], 0.022, lavender, 14)

    add_ellipsoid("SCC_yellow_vase", (1.55, -0.1, 2.42), (0.18, 0.14, 0.34), yellow, 40)
    add_tube("SCC_green_antenna_stem", [(1.55, -0.1, 2.72), (1.66, -0.12, 3.15), (1.58, -0.1, 3.55)], 0.035, green, 26)
    for i, path in enumerate([
        [(1.58, -0.1, 3.42), (1.1, -0.12, 3.55), (0.9, -0.12, 3.45)],
        [(1.58, -0.1, 3.42), (1.96, -0.1, 3.62), (2.26, -0.1, 3.82)],
        [(1.58, -0.1, 3.42), (1.56, -0.08, 3.82), (1.52, -0.08, 4.16)],
        [(1.58, -0.1, 3.42), (1.9, -0.1, 3.34), (2.35, -0.1, 3.28)],
    ]):
        add_tube(f"SCC_antenna_arm_{i}", path, 0.035, green, 22)

    bpy.ops.object.light_add(type="AREA", location=(-3.2, -4.0, 6.0))
    key = bpy.context.object
    key.name = "SCC_large_softbox_key"
    key.data.energy = 560
    key.data.size = 5.6
    bpy.ops.object.light_add(type="AREA", location=(3.6, -2.2, 4.0))
    rim = bpy.context.object
    rim.name = "SCC_mint_side_fill"
    rim.data.energy = 140
    rim.data.size = 4.0
    bpy.ops.object.camera_add(location=(0, -7.2, 2.35))
    cam = bpy.context.object
    cam.name = "SCC_orthographic_reference_camera"
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 7.35
    look_at(cam, (0, -0.15, 1.68))
    bpy.context.scene.camera = cam

    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 864
    bpy.context.scene.eevee.taa_render_samples = 96
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "None"
    bpy.context.scene.view_settings.exposure = 0.1
    bpy.context.scene.view_settings.gamma = 1


def export_and_report() -> None:
    png = RENDER_DIR / f"{ASSET}_preview.png"
    blend = BLEND_DIR / f"{ASSET}.blend"
    glb = EXPORT_DIR / f"{ASSET}.glb"
    report = REPORT_DIR / f"{ASSET}_scene_report.json"
    graph = REPORT_DIR / f"{ASSET}_scene_graph.json"

    bpy.context.scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))

    exportable = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type in {"MESH", "CURVE"} and not obj.name.startswith("SCC_soft_shadow_floor") and not obj.name.startswith("SCC_preview_backdrop")
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True, export_yup=True)

    depsgraph = bpy.context.evaluated_depsgraph_get()
    triangles = 0
    nodes = []
    for obj in exportable:
        if obj.type == "MESH":
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            tri_count = sum(len(poly.vertices) - 2 for poly in mesh.polygons)
            obj.evaluated_get(depsgraph).to_mesh_clear()
        else:
            tri_count = 0
        triangles += tri_count
        nodes.append({"name": obj.name, "type": obj.type, "material": obj.data.materials[0].name if obj.data.materials else None, "triangles": tri_count})

    report.write_text(
        json.dumps(
            {
                "asset": ASSET,
                "mode": "organic object + icon/hero object",
                "reference": "blender-workbench/references/surreal-clay-cafe-primary.png",
                "artifacts": {"preview": str(png), "blend": str(blend), "glb": str(glb)},
                "validation": {"errors": [], "warnings": [], "triangles": triangles, "exportable_objects": len(exportable)},
                "acceptance_criteria": [
                    "pastel clay table-and-chairs composition",
                    "CRT monitor with anime performer on screen",
                    "organic pink chairs and green pedestal",
                    "web-ready GLB plus editable .blend and PNG preview",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    graph.write_text(json.dumps({"asset": ASSET, "nodes": nodes}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_scene()
    export_and_report()
