from __future__ import annotations

import json
import math
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

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
CHECKPOINTS = BLENDS / "checkpoints"
PUBLIC_MODELS = REPO / "public" / "models"
V4_BLENDER_TOOLS = WORKBENCH / "research-feedback-upgrade" / "04_blender"

ASSET = "jojo_anime_playing_cards_v1"
SCENE_NAME = "JojoAnimePlayingCardsV1"
END_FRAME = 144
FPS = 24
WIDTH = 1200
HEIGHT = 1000
PREVIEW_FRAMES = (1, 24, 48, 72, 96, 120, 144)

CARD_WIDTH = 0.82
CARD_HEIGHT = 1.18
CARD_DEPTH = 0.056
FRONT_Y = -CARD_DEPTH / 2.0
BACK_Y = CARD_DEPTH / 2.0

for path in (RENDERS, REPORTS, EXPORTS, BLENDS, CHECKPOINTS, PUBLIC_MODELS):
    path.mkdir(parents=True, exist_ok=True)

if str(V4_BLENDER_TOOLS) not in sys.path:
    sys.path.append(str(V4_BLENDER_TOOLS))

try:
    import scene_qa
except Exception:  # pragma: no cover - Blender runtime fallback
    scene_qa = None


SHORTS_NOTES = [
    {
        "title": "Dynamic Cards Animation Tutorial",
        "url": "https://www.youtube.com/shorts/Dhwrw2RtD8I",
        "applied": "Staggered card carousel, not one static stack.",
    },
    {
        "title": "How To Stack Your Cards In Blender",
        "url": "https://www.youtube.com/shorts/994732mCNDA",
        "applied": "Cards sit at different depth offsets so they read as one-behind-another.",
    },
    {
        "title": "Parallax Pokemon card turns 3D",
        "url": "https://www.youtube.com/shorts/8-ET9L_VDkk",
        "applied": "Layered front art with foreground text, aura shapes, and background speed lines.",
    },
    {
        "title": "Editable 3D Pack Opening Animation",
        "url": "https://www.youtube.com/shorts/eIExezP647w",
        "applied": "Reveal timing uses a front showcase moment for each card.",
    },
    {
        "title": "Credit Card Animation for FinTech, part 2",
        "url": "https://www.youtube.com/shorts/NVEuv2WmAyY",
        "applied": "Glossy card material, bevel, and product-style rim lighting.",
    },
    {
        "title": "How to make a card shape",
        "url": "https://www.youtube.com/shorts/zbvn6t9ik9E",
        "applied": "Solid rounded rectangle body with small real thickness.",
    },
    {
        "title": "Trying New NPR Style in Blender Everyday",
        "url": "https://www.youtube.com/shorts/hFuXAjpoe_0",
        "applied": "Crisp anime rim band through colored back/rim lights.",
    },
    {
        "title": "Blender: Easy Anime Hair-Curves",
        "url": "https://www.youtube.com/shorts/ofjmOXSUBVQ",
        "applied": "Thin card-like layered strips for stylized manga accents.",
    },
    {
        "title": "Daily Blender Secrets - Low-poly hair cards",
        "url": "https://www.youtube.com/shorts/E4jKNvaY12s",
        "applied": "Flat low-poly planes are used intentionally as decal layers, not accidental paper.",
    },
    {
        "title": "Secret Shortcuts in Blender - Bevel Flip Trick",
        "url": "https://www.youtube.com/shorts/zn7lmi6KzJU",
        "applied": "Visible bevels and weighted normals make card edges catch light.",
    },
]


CARD_SPECS = [
    {"rank": "A", "label": "STAR", "colors": ("deep_purple", "gold", "hot_pink")},
    {"rank": "K", "label": "POSE", "colors": ("ink", "lime", "violet")},
    {"rank": "Q", "label": "ORA", "colors": ("wine", "sun", "cyan")},
    {"rank": "J", "label": "STAND", "colors": ("teal", "rose", "gold")},
    {"rank": "10", "label": "MENACE", "colors": ("black", "magenta", "acid")},
    {"rank": "9", "label": "SPEED", "colors": ("blue", "gold", "rose")},
    {"rank": "7", "label": "AURA", "colors": ("violet", "green", "cream")},
]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def tag(obj: bpy.types.Object, role: str, export: bool = True) -> bpy.types.Object:
    obj["role"] = role
    obj["abt_export"] = bool(export)
    return obj


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object, location: bool = False, rotation: bool = False, scale: bool = True) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def parent_keep_world(obj: bpy.types.Object, parent: bpy.types.Object) -> None:
    matrix = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = matrix


def link_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for user_collection in list(obj.users_collection):
        if user_collection != collection:
            user_collection.objects.unlink(obj)
    if obj.name not in collection.objects.keys():
        try:
            collection.objects.link(obj)
        except RuntimeError:
            pass


def safe_engine(scene: bpy.types.Scene) -> str:
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            return candidate
        except Exception:
            continue
    return scene.render.engine


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.48,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
    coat_weight: float = 0.12,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        values = {
            "Base Color": color,
            "Roughness": roughness,
            "Metallic": metallic,
            "Alpha": color[3],
            "Coat Weight": coat_weight,
            "Coat Roughness": 0.24,
            "Specular IOR Level": 0.56,
        }
        for key, value in values.items():
            if key in bsdf.inputs:
                bsdf.inputs[key].default_value = value
        if emission is not None:
            for key in ("Emission Color", "Emission"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission
                    break
            for key in ("Emission Strength", "Emission Weight"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = emission_strength
                    break
    return mat


def make_materials() -> dict[str, bpy.types.Material]:
    colors = {
        "cream": (0.98, 0.93, 0.80, 1.0),
        "paper": (0.96, 0.92, 0.82, 1.0),
        "edge": (0.035, 0.031, 0.043, 1.0),
        "ink": (0.015, 0.012, 0.020, 1.0),
        "black": (0.006, 0.006, 0.012, 1.0),
        "deep_purple": (0.18, 0.055, 0.46, 1.0),
        "violet": (0.42, 0.12, 0.86, 1.0),
        "hot_pink": (1.0, 0.12, 0.55, 1.0),
        "magenta": (0.86, 0.03, 0.72, 1.0),
        "gold": (1.0, 0.72, 0.19, 1.0),
        "sun": (1.0, 0.85, 0.12, 1.0),
        "lime": (0.42, 1.0, 0.20, 1.0),
        "acid": (0.72, 1.0, 0.02, 1.0),
        "green": (0.02, 0.78, 0.35, 1.0),
        "teal": (0.02, 0.68, 0.76, 1.0),
        "cyan": (0.08, 0.95, 1.0, 1.0),
        "blue": (0.08, 0.24, 0.90, 1.0),
        "rose": (1.0, 0.34, 0.44, 1.0),
        "wine": (0.35, 0.02, 0.12, 1.0),
    }
    mats: dict[str, bpy.types.Material] = {}
    for name, color in colors.items():
        emissive = name in {"hot_pink", "magenta", "lime", "acid", "cyan", "gold"}
        mats[name] = material(
            f"JJC_{name}_PBR",
            color,
            roughness=0.38 if name not in {"paper", "cream"} else 0.46,
            emission=color if emissive else None,
            emission_strength=0.06 if emissive else 0.0,
            coat_weight=0.20 if name in {"paper", "cream"} else 0.08,
        )
    mats["neon_purple"] = material(
        "JJC_neon_purple_PBR",
        (0.58, 0.16, 1.0, 1.0),
        roughness=0.30,
        emission=(0.58, 0.16, 1.0, 1.0),
        emission_strength=0.18,
        coat_weight=0.08,
    )
    return mats


def setup_scene() -> bpy.types.Scene:
    if bpy.context.scene.objects:
        checkpoint = CHECKPOINTS / f"{ASSET}_prechange_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    scene = bpy.context.scene
    scene.name = SCENE_NAME
    scene.frame_start = 1
    scene.frame_end = END_FRAME
    scene.frame_set(1)
    scene.render.fps = FPS
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -0.08
    scene.view_settings.gamma = 1.0

    engine = safe_engine(scene)
    if engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
    if hasattr(scene, "eevee"):
        for attr, value in (
            ("taa_render_samples", 128),
            ("use_gtao", True),
            ("gtao_distance", 2.5),
            ("gtao_factor", 0.65),
            ("use_bloom", True),
            ("bloom_intensity", 0.028),
        ):
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    world = scene.world or bpy.data.worlds.new("JJC_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.010, 0.008, 0.016, 1.0)
        bg.inputs["Strength"].default_value = 0.18
    return scene


def create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def create_empty(collection: bpy.types.Collection, name: str, location=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.16
    obj.location = location
    collection.objects.link(obj)
    return tag(obj, "animation_root", True)


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def shade_smooth(obj: bpy.types.Object) -> bpy.types.Object:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True
        set_active(obj)
        modifier = obj.modifiers.new("weighted_anime_card_normals", "WEIGHTED_NORMAL")
        modifier.keep_sharp = True
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except Exception:
            pass
    return obj


def rounded_box(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    segments: int = 8,
    role: str = "semantic_mesh",
    export: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    assign_material(obj, mat)
    link_to_collection(obj, collection)
    apply_transform(obj, location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("rounded_card_bevel", "BEVEL")
    bevel.width = radius
    bevel.segments = segments
    try:
        bevel.affect = "EDGES"
    except Exception:
        pass
    normal = obj.modifiers.new("weighted_normals", "WEIGHTED_NORMAL")
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    if normal.name in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=normal.name)
    tag(obj, role, export)
    return shade_smooth(obj)


def flat_polygon(
    collection: bpy.types.Collection,
    name: str,
    points_xz: list[tuple[float, float]],
    y: float,
    mat: bpy.types.Material,
    role: str = "card_decal",
    export: bool = True,
    reverse: bool = False,
) -> bpy.types.Object:
    pts = list(reversed(points_xz)) if reverse else points_xz
    verts = [(x, y, z) for x, z in pts]
    faces = []
    for i in range(1, len(verts) - 1):
        faces.append((0, i, i + 1))
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, mat)
    tag(obj, role, export)
    return obj


def rounded_rect_points(width: float, height: float, radius: float, segments: int = 6) -> list[tuple[float, float]]:
    w = width / 2.0
    h = height / 2.0
    r = min(radius, w * 0.95, h * 0.95)
    corners = [
        ((w - r, -h + r), -90.0, 0.0),
        ((w - r, h - r), 0.0, 90.0),
        ((-w + r, h - r), 90.0, 180.0),
        ((-w + r, -h + r), 180.0, 270.0),
    ]
    points: list[tuple[float, float]] = []
    for (cx, cz), start, end in corners:
        for step in range(segments + 1):
            angle = math.radians(start + (end - start) * step / segments)
            points.append((cx + math.cos(angle) * r, cz + math.sin(angle) * r))
    return points


def rounded_rect_plane(
    collection: bpy.types.Collection,
    name: str,
    width: float,
    height: float,
    y: float,
    radius: float,
    mat: bpy.types.Material,
    role: str = "card_panel_decal",
    reverse: bool = False,
) -> bpy.types.Object:
    return flat_polygon(collection, name, rounded_rect_points(width, height, radius), y, mat, role=role, reverse=reverse)


def disc(
    collection: bpy.types.Collection,
    name: str,
    center: tuple[float, float],
    radius: float,
    y: float,
    mat: bpy.types.Material,
    segments: int = 32,
    scale_x: float = 1.0,
    scale_z: float = 1.0,
    reverse: bool = False,
) -> bpy.types.Object:
    points = []
    for i in range(segments):
        angle = math.tau * i / segments
        points.append((center[0] + math.cos(angle) * radius * scale_x, center[1] + math.sin(angle) * radius * scale_z))
    return flat_polygon(collection, name, points, y, mat, reverse=reverse)


def star(
    collection: bpy.types.Collection,
    name: str,
    center: tuple[float, float],
    outer: float,
    inner: float,
    y: float,
    mat: bpy.types.Material,
    points_count: int = 8,
    rotation: float = 0.0,
    reverse: bool = False,
) -> bpy.types.Object:
    points = []
    for i in range(points_count * 2):
        radius = outer if i % 2 == 0 else inner
        angle = rotation + math.tau * i / (points_count * 2)
        points.append((center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius))
    return flat_polygon(collection, name, points, y, mat, reverse=reverse)


def text_mesh(
    collection: bpy.types.Collection,
    name: str,
    text: str,
    location: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    rotation_x: float,
    align: str = "CENTER",
    role: str = "card_text",
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=location, rotation=(rotation_x, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.0
    obj.data.bevel_depth = 0.0
    obj.data.resolution_u = 1
    obj.data.materials.append(mat)
    link_to_collection(obj, collection)
    set_active(obj)
    bpy.ops.object.convert(target="MESH")
    converted = bpy.context.object
    converted.name = name
    link_to_collection(converted, collection)
    assign_material(converted, mat)
    decimate = converted.modifiers.new("text_glb_decimate", "DECIMATE")
    decimate.ratio = 0.58
    set_active(converted)
    try:
        bpy.ops.object.modifier_apply(modifier=decimate.name)
    except Exception:
        pass
    tag(converted, role, True)
    return shade_smooth(converted)


def local_parent_parts(root: bpy.types.Object, parts: Iterable[bpy.types.Object]) -> None:
    for obj in parts:
        parent_keep_world(obj, root)


def add_front_art(
    collection: bpy.types.Collection,
    prefix: str,
    spec: dict,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    rank = spec["rank"]
    label = spec["label"]
    primary, secondary, accent = spec["colors"]
    parts: list[bpy.types.Object] = []
    y = FRONT_Y - 0.020

    parts.append(rounded_rect_plane(collection, f"{prefix}_Front_ivory_panel", 0.70, 1.04, FRONT_Y - 0.010, 0.040, mats["paper"], role="card_front_panel"))
    parts.append(rounded_rect_plane(collection, f"{prefix}_Front_inner_frame", 0.62, 0.94, FRONT_Y - 0.013, 0.030, mats[primary], role="card_front_frame"))
    parts.append(rounded_rect_plane(collection, f"{prefix}_Front_art_field", 0.54, 0.78, FRONT_Y - 0.016, 0.022, mats["cream"], role="card_front_art_field"))

    for i, offset in enumerate((-0.25, -0.13, 0.00, 0.13, 0.25), start=1):
        height = 0.74 - abs(offset) * 0.65
        z0 = -0.36
        z1 = z0 + height
        width = 0.030 + 0.006 * (i % 2)
        parts.append(flat_polygon(
            collection,
            f"{prefix}_Speedline_{i}",
            [(offset - width, z0), (offset + width, z0), (offset + 0.13, z1), (offset + 0.10, z1)],
            y - 0.002 * i,
            mats[secondary if i % 2 else accent],
        ))

    parts.append(star(collection, f"{prefix}_Aura_star_large", (0.0, 0.08), 0.28, 0.11, y - 0.018, mats[accent], points_count=9, rotation=math.radians(10)))
    parts.append(star(collection, f"{prefix}_Aura_star_dark", (0.0, 0.08), 0.20, 0.08, y - 0.020, mats[primary], points_count=9, rotation=math.radians(29)))
    parts.append(disc(collection, f"{prefix}_Stand_head_disc", (0.0, 0.21), 0.075, y - 0.025, mats["ink"], segments=28, scale_x=0.88, scale_z=1.05))
    parts.append(flat_polygon(collection, f"{prefix}_Stand_torso_shape", [(-0.12, 0.13), (0.12, 0.13), (0.18, -0.13), (0.06, -0.26), (-0.06, -0.26), (-0.18, -0.13)], y - 0.026, mats["ink"]))
    parts.append(flat_polygon(collection, f"{prefix}_Pose_shoulder_left", [(-0.11, 0.07), (-0.32, -0.04), (-0.26, -0.13), (-0.08, 0.00)], y - 0.027, mats[secondary]))
    parts.append(flat_polygon(collection, f"{prefix}_Pose_shoulder_right", [(0.11, 0.07), (0.32, -0.04), (0.26, -0.13), (0.08, 0.00)], y - 0.027, mats[accent]))

    parts.append(text_mesh(collection, f"{prefix}_Rank_top", rank, (-0.275, y - 0.034, 0.435), 0.150, mats["ink"], math.radians(90)))
    parts.append(text_mesh(collection, f"{prefix}_Rank_bottom", rank, (0.275, y - 0.034, -0.435), 0.150, mats["ink"], math.radians(90)))
    parts.append(text_mesh(collection, f"{prefix}_Label_neon", label, (0.0, y - 0.040, -0.360), 0.072, mats[accent], math.radians(90)))
    parts.append(text_mesh(collection, f"{prefix}_Small_JOJO", "JOJO", (0.0, y - 0.041, 0.365), 0.055, mats[secondary], math.radians(90)))
    return parts


def add_back_art(
    collection: bpy.types.Collection,
    prefix: str,
    spec: dict,
    mats: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    primary, secondary, accent = spec["colors"]
    parts: list[bpy.types.Object] = []
    y = BACK_Y + 0.020
    reverse = True

    parts.append(rounded_rect_plane(collection, f"{prefix}_Back_dark_panel", 0.70, 1.04, BACK_Y + 0.010, 0.040, mats["ink"], role="card_back_panel", reverse=reverse))
    parts.append(rounded_rect_plane(collection, f"{prefix}_Back_inner_color", 0.60, 0.90, BACK_Y + 0.013, 0.030, mats[primary], role="card_back_frame", reverse=reverse))

    for i in range(8):
        z = -0.42 + i * 0.12
        x_shift = -0.25 if i % 2 == 0 else 0.08
        parts.append(flat_polygon(
            collection,
            f"{prefix}_Back_slash_{i + 1}",
            [(x_shift - 0.34, z - 0.035), (x_shift - 0.24, z - 0.035), (x_shift + 0.35, z + 0.085), (x_shift + 0.25, z + 0.085)],
            y + 0.002 * i,
            mats[secondary if i % 2 == 0 else accent],
            reverse=reverse,
        ))
    parts.append(star(collection, f"{prefix}_Back_star_outer", (0.0, 0.0), 0.285, 0.120, y + 0.028, mats["gold"], points_count=8, rotation=math.radians(22), reverse=reverse))
    parts.append(star(collection, f"{prefix}_Back_star_inner", (0.0, 0.0), 0.180, 0.075, y + 0.030, mats["ink"], points_count=8, rotation=math.radians(44), reverse=reverse))
    parts.append(text_mesh(collection, f"{prefix}_Back_text", "JXJX", (0.0, y + 0.040, 0.0), 0.118, mats["cream"], math.radians(-90)))
    return parts


def build_card(collection: bpy.types.Collection, index: int, spec: dict, mats: dict[str, bpy.types.Material]) -> bpy.types.Object:
    prefix = f"JJC_Card_{index + 1:02d}"
    root = create_empty(collection, f"{prefix}_AnimatedRoot")
    root["card_rank"] = spec["rank"]
    root["card_label"] = spec["label"]

    body = rounded_box(
        collection,
        f"{prefix}_Solid_rounded_body",
        (0.0, 0.0, 0.0),
        (CARD_WIDTH, CARD_DEPTH, CARD_HEIGHT),
        0.026,
        mats["edge"],
        segments=6,
        role="card_body",
    )
    front_parts = add_front_art(collection, prefix, spec, mats)
    back_parts = add_back_art(collection, prefix, spec, mats)
    local_parent_parts(root, [body, *front_parts, *back_parts])
    return root


def key(obj: bpy.types.Object, frame: int, loc=None, rot=None, scale=None) -> None:
    bpy.context.scene.frame_set(frame)
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


def smooth_keys(objects: Iterable[bpy.types.Object]) -> None:
    for obj in objects:
        if not obj.animation_data or not obj.animation_data.action:
            continue
        obj.animation_data.action.name = f"{ASSET}_{obj.name}_Loop"
        for curve in getattr(obj.animation_data.action, "fcurves", []):
            for item in curve.keyframe_points:
                item.interpolation = "SINE"


def animate_cards(card_roots: list[bpy.types.Object]) -> None:
    samples = (1, 18, 36, 54, 72, 90, 108, 126, 144)
    radius_x = 1.02
    radius_y = 0.68
    count = len(card_roots)
    for index, root in enumerate(card_roots):
        phase = -math.tau * index / count
        for frame in samples:
            progress = (frame - 1) / (END_FRAME - 1)
            theta = progress * math.tau + phase
            frontness = (math.cos(theta) + 1.0) / 2.0
            loc = (
                math.sin(theta) * radius_x,
                -math.cos(theta) * radius_y,
                0.98 + 0.10 * math.cos(theta + index * 0.37),
            )
            rot = (
                math.radians(4.0 * math.sin(theta * 1.5 + index)),
                math.radians(6.0 * math.sin(theta + index * 0.6)),
                theta + math.radians(5.0 * math.sin(theta * 2.0)),
            )
            scale_value = 0.84 + 0.18 * frontness
            key(root, frame, loc=loc, rot=rot, scale=(scale_value, scale_value, scale_value))
    smooth_keys(card_roots)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera_and_lights(collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> dict[str, bpy.types.Object]:
    camera_data = bpy.data.cameras.new("JJC_Camera_data")
    camera = bpy.data.objects.new("JJC_Camera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.12
    camera.location = (2.65, -5.55, 2.20)
    look_at(camera, (0.0, -0.04, 0.88))
    bpy.context.scene.camera = camera
    tag(camera, "preview_camera", False)

    floor = rounded_box(collection, "JJC_preview_floor_not_exported", (0.0, 0.18, -0.035), (3.2, 2.35, 0.04), 0.020, mats["ink"], segments=3, role="preview_floor", export=False)
    floor["abt_export"] = False

    back_panel = rounded_box(collection, "JJC_manga_back_panel_not_exported", (0.0, 1.08, 1.08), (3.0, 0.035, 2.25), 0.018, mats["deep_purple"], segments=4, role="preview_backdrop", export=False)
    back_panel["abt_export"] = False
    for i, x in enumerate((-1.20, -0.72, -0.25, 0.25, 0.72, 1.20), start=1):
        strip = flat_polygon(
            collection,
            f"JJC_background_speedline_{i}_not_exported",
            [(x - 0.055, -0.02), (x + 0.055, -0.02), (x + 0.36, 2.02), (x + 0.22, 2.02)],
            1.045 - i * 0.001,
            mats["gold" if i % 2 else "hot_pink"],
            role="preview_backdrop_line",
            export=False,
            reverse=True,
        )
        strip["abt_export"] = False

    def add_light(name: str, loc: tuple[float, float, float], energy: float, size: float, color: tuple[float, float, float]) -> bpy.types.Object:
        data = bpy.data.lights.new(name=f"{name}_data", type="AREA")
        data.energy = energy
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = loc
        look_at(obj, (0.0, -0.05, 0.78))
        tag(obj, "preview_light", False)
        return obj

    key_light = add_light("JJC_Key_warm_softbox", (-3.4, -4.9, 4.1), 560.0, 4.6, (1.0, 0.82, 0.62))
    fill_light = add_light("JJC_Fill_violet_softbox", (3.8, -3.0, 2.6), 170.0, 4.0, (0.58, 0.30, 1.0))
    rim_light = add_light("JJC_Rim_cyan_backlight", (2.4, 2.2, 2.8), 260.0, 3.0, (0.24, 1.0, 0.96))
    gold_rim = add_light("JJC_Rim_gold_side", (-2.9, 1.7, 1.8), 145.0, 2.8, (1.0, 0.62, 0.16))
    return {"camera": camera, "floor": floor, "back_panel": back_panel, "key": key_light, "fill": fill_light, "rim": rim_light, "gold_rim": gold_rim}


def set_camera_view(camera: bpy.types.Object, view: str) -> None:
    if view == "front":
        camera.location = (0.0, -5.95, 1.02)
        camera.data.ortho_scale = 2.70
        look_at(camera, (0.0, -0.06, 0.92))
    elif view == "side":
        camera.location = (4.95, -0.10, 1.10)
        camera.data.ortho_scale = 2.85
        look_at(camera, (0.0, -0.04, 0.92))
    else:
        camera.location = (2.65, -5.55, 2.20)
        camera.data.ortho_scale = 3.12
        look_at(camera, (0.0, -0.04, 0.88))


def hide_except(collection: bpy.types.Collection) -> dict[str, tuple[bool, bool]]:
    previous: dict[str, tuple[bool, bool]] = {}
    keep = set(collection.objects)
    for obj in bpy.context.scene.objects:
        previous[obj.name] = (obj.hide_viewport, obj.hide_render)
        if obj not in keep and obj.type not in {"CAMERA", "LIGHT"}:
            obj.hide_viewport = True
            obj.hide_render = True
        else:
            obj.hide_viewport = False
            obj.hide_render = False
    return previous


def restore_visibility(previous: dict[str, tuple[bool, bool]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.name in previous:
            obj.hide_viewport, obj.hide_render = previous[obj.name]


def render_frame(collection: bpy.types.Collection, camera: bpy.types.Object, frame: int, path: Path, view: str = "front_3q") -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    set_camera_view(camera, view)
    previous = hide_except(collection)
    try:
        scene.render.filepath = str(path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        bpy.ops.render.render(write_still=True)
    finally:
        restore_visibility(previous)
    return {"frame": frame, "view": view, "path": str(path), "bytes": path.stat().st_size if path.exists() else 0}


def exportable_objects(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    return [obj for obj in collection.objects if bool(obj.get("abt_export", True))]


def triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    count = 0
    for obj in objects:
        if obj.type == "MESH" and obj.data is not None:
            count += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return count


def validate(collection: bpy.types.Collection) -> dict:
    objects = exportable_objects(collection)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    errors: list[str] = []
    warnings: list[str] = []
    triangles = triangle_count(meshes)
    if not meshes:
        errors.append("No exportable mesh objects")
    if triangles > 100000:
        warnings.append(f"Triangle budget above animated hero target: {triangles}/100000")
    animated = [obj for obj in objects if obj.animation_data and obj.animation_data.action]
    if not animated:
        errors.append("No animated exportable roots")
    for obj in meshes:
        if not obj.data.materials:
            errors.append(f"{obj.name} has no material")
        if any(value < 0 for value in obj.scale):
            errors.append(f"{obj.name} has negative scale")
        if any(abs(value - 1.0) > 0.001 for value in obj.scale):
            warnings.append(f"{obj.name} has unapplied scale {tuple(round(v, 3) for v in obj.scale)}")
        for vertex in obj.data.vertices:
            if not all(math.isfinite(value) for value in vertex.co):
                errors.append(f"{obj.name} has non-finite coordinates")
                break
    return {
        "asset": ASSET,
        "target_mode": "HYBRID_HERO",
        "frame_start": 1,
        "frame_end": END_FRAME,
        "fps": FPS,
        "triangles": triangles,
        "mesh_objects": len(meshes),
        "exportable_objects": len(objects),
        "animated_objects": len(animated),
        "errors": errors,
        "warnings": warnings,
    }


def export_glb(collection: bpy.types.Collection) -> dict:
    objects = exportable_objects(collection)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]
    path = EXPORTS / f"{ASSET}.glb"
    props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    kwargs = {
        "filepath": str(path),
        "export_format": "GLB",
        "use_selection": True,
        "export_animations": True,
        "export_nla_strips": False,
        "export_force_sampling": True,
        "export_frame_range": True,
        "export_frame_step": 1,
        "export_optimize_animation_size": False,
    }
    filtered = {key: value for key, value in kwargs.items() if key in props}
    bpy.ops.export_scene.gltf(**filtered)
    public_path = PUBLIC_MODELS / path.name
    shutil.copy2(path, public_path)
    return {
        "path": str(path),
        "public_path": str(public_path),
        "bytes": path.stat().st_size,
        "public_bytes": public_path.stat().st_size,
    }


def glb_check(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        return {"file": path.name, "bytes": len(data), "errors": ["not a GLB file"]}
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        return {"file": path.name, "bytes": len(data), "errors": ["first chunk is not JSON"]}
    payload = data[20 : 20 + chunk_length].decode("utf-8")
    gltf = json.loads(payload)
    return {
        "file": path.name,
        "bytes": len(data),
        "animations": len(gltf.get("animations", [])),
        "animation_names": [item.get("name", "") for item in gltf.get("animations", [])],
        "nodes": len(gltf.get("nodes", [])),
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
    }


def write_scene_graph(card_roots: list[bpy.types.Object]) -> dict:
    graph = {
        "asset": ASSET,
        "purpose": "Original anime/JoJo-inspired rotating 3D playing-card hero asset",
        "target_mode": "HYBRID_HERO",
        "original_design": True,
        "copyright_note": "No existing JoJo character, manga panel, logo, or card artwork is copied; this is an original anime-drama visual language.",
        "cards": [{"root": root.name, "rank": root.get("card_rank"), "label": root.get("card_label")} for root in card_roots],
        "expected_contacts": [
            "front panel sits flush on each solid card body",
            "back panel sits flush on each solid card body",
            "decal planes are intentionally layered just above card faces",
            "all card components are parented to animated card roots",
            "preview floor, background, camera and lights are not exported",
        ],
        "animation": {
            "name": "seven_card_showcase_loop_144f",
            "frames": END_FRAME,
            "fps": FPS,
            "motion": "cards rotate on a carousel so one card shows its face while the others pass behind it",
            "loop": "frame 1 and frame 144 return to the same pose",
        },
        "acceptance": [
            "seven readable playing cards with real thickness and bevels",
            "front and back faces are both designed",
            "animation has exportable GLB tracks",
            "lighting has warm key, violet fill, cyan rim and gold side accent",
            "PNG previews exist for frame sequence, front, 3/4 and side views",
            "GLB excludes preview-only floor, manga backdrop, lights and camera",
        ],
        "shorts_research": SHORTS_NOTES,
    }
    write_json(REPORTS / f"{ASSET}_scene_graph.json", graph)
    return graph


def write_research_notes() -> Path:
    path = REPORTS / f"{ASSET}_shorts_research.md"
    lines = [
        f"# {ASSET} Shorts Research",
        "",
        "Goal: use ten short Blender references as compact production cues, then build an original rotating anime playing-card scene.",
        "",
    ]
    for index, item in enumerate(SHORTS_NOTES, start=1):
        lines.append(f"{index}. [{item['title']}]({item['url']})")
        lines.append(f"   Applied: {item['applied']}")
    lines.extend(
        [
            "",
            "Style rule: inspired by high-energy anime/manga motion, not a copy of a specific character or licensed card artwork.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_scene() -> dict:
    scene = setup_scene()
    collection = create_collection("JJC_Output")
    mats = make_materials()
    setup = setup_camera_and_lights(collection, mats)
    card_roots = [build_card(collection, index, spec, mats) for index, spec in enumerate(CARD_SPECS)]
    animate_cards(card_roots)

    scene_graph = write_scene_graph(card_roots)
    research_path = write_research_notes()

    renders = [
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_front.png", "front"),
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_front_3q.png", "front_3q"),
        render_frame(collection, setup["camera"], 48, RENDERS / f"{ASSET}_view_side.png", "side"),
    ]
    for frame in PREVIEW_FRAMES:
        renders.append(render_frame(collection, setup["camera"], frame, RENDERS / f"{ASSET}_frame_{frame:03d}.png", "front_3q"))

    validation = validate(collection)
    object_names = [obj.name for obj in exportable_objects(collection)]
    qa = scene_qa.audit_scene(object_names=object_names, floating_tolerance=0.08) if scene_qa else {"warnings": ["scene_qa unavailable"], "errors": []}
    write_json(REPORTS / f"{ASSET}_structural_qa.json", qa)

    export = export_glb(collection) if not validation["errors"] else {"skipped": True, "reason": validation["errors"]}
    animation_check = None
    if "path" in export:
        animation_check = glb_check(Path(export["path"]))
        write_json(REPORTS / f"{ASSET}_glb_animation_check.json", animation_check)

    blend_path = BLENDS / f"{ASSET}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    report = {
        "asset": ASSET,
        "scene": scene.name,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size if blend_path.exists() else 0},
        "scene_graph": scene_graph,
        "shorts_research": str(research_path),
        "renders": renders,
        "validation": validation,
        "structural_qa": {
            "path": str(REPORTS / f"{ASSET}_structural_qa.json"),
            "errors": qa.get("errors", []),
            "warnings": qa.get("warnings", []),
            "potential_floating_components": qa.get("potential_floating_components", []),
        },
        "export": export,
        "glb_animation_check": animation_check,
    }
    write_json(REPORTS / f"{ASSET}_scene_report.json", report)
    return report


def main() -> None:
    print(json.dumps(build_scene(), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
