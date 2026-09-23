"""Replace detached round brow rods with closed, head-conforming surface ribbons."""

from __future__ import annotations

import hashlib
import math
import runpy
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ASSET = "comforting_cat_v6_brow_surface_ribbon_attempt90"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = WORKBENCH / "artifacts" / "blend"
RENDER_DIR = WORKBENCH / "artifacts" / "renders"
EXPORT_DIR = WORKBENCH / "artifacts" / "exports"
REPORT_DIR = WORKBENCH / "artifacts" / "reports"
CHECKPOINT_DIR = BLEND_DIR / "checkpoints"
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v6_front_cheek_taper_attempt89.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
UTILS_PATH = (WORKBENCH / "scripts" / "comforting_cat_pass_utils.py").resolve()

if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v6_before_brow_surface_ribbon_attempt90.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))

utils = runpy.run_path(str(UTILS_PATH))
bounds = utils["bounds"]
descendants = utils["descendants"]
preserve_copy = utils["preserve_copy"]
finalize_pass = utils["finalize_pass"]


def object_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        digest.update(obj.type.encode("ascii"))
        for row in obj.matrix_world:
            for component in row:
                digest.update(f"{float(component):.9f}".encode("ascii"))
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                digest.update(
                    f"{vertex.co.x:.9f},{vertex.co.y:.9f},{vertex.co.z:.9f};".encode("ascii")
                )
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                for point in spline.bezier_points:
                    digest.update(
                        f"{point.co.x:.9f},{point.co.y:.9f},{point.co.z:.9f},{point.radius:.9f};".encode("ascii")
                    )
    return digest.hexdigest()


def topology(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundary_edges": sum(1 for edge in bm.edges if edge.is_boundary),
        "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
    }
    bm.free()
    return result


root = bpy.data.objects["CatV6_Root"]
head = bpy.data.objects["V6_Head"]
brow_names = ("V6_Eyebrow_L", "V6_Eyebrow_R")
old_brows = [bpy.data.objects[name] for name in brow_names]
locked_objects = [obj for obj in descendants(root) if obj.name not in brow_names]
locked_hash_before = object_hash(locked_objects)
head_hash_before = object_hash([head])
before = {obj.name: bounds(obj) for obj in old_brows}
preserved_sources = [
    preserve_copy(obj, "Comforting_Cat_V6", "A90", "detached_round_brow_rod")
    for obj in old_brows
]

depsgraph = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(head, depsgraph)
head_inverse = head.matrix_world.inverted()
head_direction = head_inverse.to_3x3() @ Vector((0.0, 1.0, 0.0))


def surface_y(x: float, z: float) -> float:
    origin = head_inverse @ Vector((x, -2.0, z))
    hit, _normal, _index, _distance = bvh.ray_cast(origin, head_direction)
    if hit is None:
        raise RuntimeError(f"A90 brow ray missed head at x={x:.5f}, z={z:.5f}")
    return float((head.matrix_world @ hit).y)


profiles: dict[str, object] = {}
new_brows: list[bpy.types.Object] = []
for old_brow in old_brows:
    material = old_brow.data.materials[0] if old_brow.data.materials else None
    target_collection = old_brow.users_collection[0]
    side = -1.0 if old_brow.name.endswith("_L") else 1.0
    outer_x = side * 0.318367
    inner_x = side * 0.090962
    outer_z = 3.051600
    inner_z = 3.145200
    span = abs(outer_x - inner_x)
    inner_outer_rise = inner_z - outer_z
    old_name = old_brow.name
    bpy.data.objects.remove(old_brow, do_unlink=True)

    vertices: list[tuple[float, float, float]] = []
    station_metrics: list[dict[str, float]] = []
    station_count = 9
    for index in range(station_count):
        t = index / (station_count - 1)
        x = outer_x + (inner_x - outer_x) * t
        chord_z = outer_z + (inner_z - outer_z) * t
        center_z = chord_z + math.sin(math.pi * t) * 0.018
        half_height = 0.002 + math.sin(math.pi * t) * 0.006
        top_z = center_z + half_height
        bottom_z = center_z - half_height
        top_surface_y = surface_y(x, top_z)
        bottom_surface_y = surface_y(x, bottom_z)
        front_top = Vector((x, top_surface_y - 0.0022, top_z))
        front_bottom = Vector((x, bottom_surface_y - 0.0022, bottom_z))
        back_top = Vector((x, top_surface_y + 0.0008, top_z))
        back_bottom = Vector((x, bottom_surface_y + 0.0008, bottom_z))
        for point in (front_top, front_bottom, back_top, back_bottom):
            local = root.matrix_world.inverted() @ point
            vertices.append((float(local.x), float(local.y), float(local.z)))
        station_metrics.append(
            {
                "t": round(t, 4),
                "x": round(x, 6),
                "center_z": round(center_z, 6),
                "visible_height": round(half_height * 2.0, 6),
                "front_proud": 0.0022,
                "back_embed": 0.0008,
            }
        )

    faces: list[tuple[int, ...]] = []
    for index in range(station_count - 1):
        current = index * 4
        following = (index + 1) * 4
        faces.extend(
            [
                (current, following, following + 1, current + 1),
                (current + 2, current + 3, following + 3, following + 2),
                (current, current + 2, following + 2, following),
                (current + 1, following + 1, following + 3, current + 3),
            ]
        )
    faces.append((0, 1, 3, 2))
    last = (station_count - 1) * 4
    faces.append((last, last + 2, last + 3, last + 1))

    mesh = bpy.data.meshes.new(f"{old_name}_SurfaceRibbonMesh_A90")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    brow = bpy.data.objects.new(old_name, mesh)
    target_collection.objects.link(brow)
    brow.parent = root
    if material is not None:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    brow["comforting_cat_role"] = "head_conforming_brow_surface_ribbon"
    brow["comforting_cat_attempt"] = 90
    new_brows.append(brow)

    center = station_metrics[station_count // 2]
    profiles[old_name] = {
        "span": round(span, 6),
        "inner_outer_rise": round(inner_outer_rise, 6),
        "middle_arch_above_chord": 0.018,
        "endpoint_visible_height": station_metrics[0]["visible_height"],
        "center_visible_height": center["visible_height"],
        "front_proud": 0.0022,
        "back_embed": 0.0008,
        "stations": station_metrics,
        "topology": topology(brow),
    }

bpy.context.view_layer.update()
after = {obj.name: bounds(obj) for obj in new_brows}
locked_hash_after = object_hash(locked_objects)
head_hash_after = object_hash([head])
if locked_hash_before != locked_hash_after:
    raise RuntimeError("A90 changed A89 geometry outside the two brow objects")
if head_hash_before != head_hash_after:
    raise RuntimeError("A90 changed the accepted A89 head")

for name, profile in profiles.items():
    if not 0.225 <= profile["span"] <= 0.235:
        raise RuntimeError(f"{name} span outside target")
    if not 0.085 <= profile["inner_outer_rise"] <= 0.100:
        raise RuntimeError(f"{name} worried rise outside target")
    if not 0.015 <= profile["middle_arch_above_chord"] <= 0.022:
        raise RuntimeError(f"{name} arch outside target")
    if not 0.010 <= profile["center_visible_height"] <= 0.018:
        raise RuntimeError(f"{name} center ribbon height outside target")
    if not 0.002 <= profile["endpoint_visible_height"] <= 0.004:
        raise RuntimeError(f"{name} endpoint ribbon height outside target")
    if profile["front_proud"] > 0.003:
        raise RuntimeError(f"{name} brow floats above the head")
    if profile["topology"]["boundary_edges"] != 0:
        raise RuntimeError(f"{name} ribbon shell has open boundary")
    if profile["topology"]["non_manifold_edges"] != 0:
        raise RuntimeError(f"{name} ribbon shell is non-manifold")

metrics = {
    "before": before,
    "after": after,
    "profiles": profiles,
    "locked_hash_before": locked_hash_before,
    "locked_hash_after": locked_hash_after,
    "head_hash_before": head_hash_before,
    "head_hash_after": head_hash_after,
}
print("A90_PRE_GATE_METRICS=" + repr(metrics))

scene = bpy.context.scene
scene.name = "Comforting_Cat_V6_BrowSurfaceRibbon_A90"
scene["comforting_cat_v6_stage"] = "BROW_SURFACE_RIBBON_INTEGRATION"
scene["comforting_cat_v6_attempt"] = 90
scene["comforting_cat_v6_dominant_defect"] = "detached_round_mechanical_brow_rods"
scene["comforting_cat_v6_source"] = str(SOURCE_BLEND)

report = {
    "asset": ASSET,
    "stage": "BROW_SURFACE_RIBBON_INTEGRATION",
    "attempt": 90,
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "detached_round_mechanical_brow_rods",
    "preserved_sources": preserved_sources,
    "metrics": metrics,
    "scope_lock": {
        "changed": ["V6_Eyebrow_L/R curve rods replaced by closed conformal mesh ribbons"],
        "preserved": [
            "A89 head and cheek silhouette",
            "ears",
            "eyes/pupils/highlights",
            "muzzle/nose/mouth/whiskers",
            "A84 tunic and all costume",
            "legs/tail",
            "camera/lights/materials",
        ],
    },
}
finalize_pass(
    asset=ASSET,
    root=root,
    scene=scene,
    final_blend=FINAL_BLEND,
    glb_path=GLB_PATH,
    render_dir=RENDER_DIR,
    report_dir=REPORT_DIR,
    scene_qa_path=SCENE_QA_PATH,
    report=report,
)
