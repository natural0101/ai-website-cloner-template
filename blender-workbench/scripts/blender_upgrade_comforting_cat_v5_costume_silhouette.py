"""TRUE_360 costume pass: pear-shaped robe coverage and smaller front inset."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy
from mathutils import Vector


ASSET = "comforting_cat_v5_costume_silhouette_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (BLEND_DIR / "comforting_cat_v5_head_proportion_attempt1.blend").resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()
for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
for path in (SOURCE_BLEND, FINAL_BLEND, GLB_PATH, SCENE_QA_PATH):
    path.relative_to(WORKBENCH)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_costume_silhouette_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def world_bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6)
            for index in range(3)
        ],
    }


def reshape_robe(obj: bpy.types.Object) -> None:
    z_values = [vertex.co.z for vertex in obj.data.vertices]
    z_min, z_max = min(z_values), max(z_values)
    span = max(z_max - z_min, 1e-6)
    for vertex in obj.data.vertices:
        t = (vertex.co.z - z_min) / span
        vertex.co.x *= 1.12 - 0.16 * t
        vertex.co.y *= 1.16 - 0.04 * t
    obj.data.update()


def reshape_front_inset(obj: bpy.types.Object) -> None:
    z_values = [vertex.co.z for vertex in obj.data.vertices]
    z_max = max(z_values)
    for vertex in obj.data.vertices:
        vertex.co.x *= 0.76
        vertex.co.z = z_max - (z_max - vertex.co.z) * 0.72
        if vertex.co.y < 0.0:
            vertex.co.y -= 0.012
    obj.data.update()


robe = bpy.data.objects["Cat_BlueRobe"]
inset = bpy.data.objects["Cat_RobeFrontInset"]
body = bpy.data.objects["Cat_Body"]
before = {
    "robe": world_bounds(robe),
    "front_inset": world_bounds(inset),
    "body": world_bounds(body),
}
reshape_robe(robe)
reshape_front_inset(inset)
bpy.context.view_layer.update()
after = {
    "robe": world_bounds(robe),
    "front_inset": world_bounds(inset),
    "body": world_bounds(body),
}
coverage = {
    "back_y_margin": round(
        after["robe"]["max"][1] - after["body"]["max"][1],
        6,
    ),
    "front_y_margin": round(
        after["body"]["min"][1] - after["robe"]["min"][1],
        6,
    ),
}

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_CostumeSilhouette"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "COSTUME_GEOMETRY"
scene["comforting_cat_v5_geometry_attempt"] = "costume_silhouette_1"
scene["comforting_cat_v5_dominant_defect"] = "cylindrical_robe_and_body_showthrough"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "v5 head group proportions",
        "face, eyes, muzzle and expression",
        "scarf geometry",
        "arms and paws",
        "legs and feet",
        "satchel and strap",
        "tail",
        "materials",
        "lighting",
    ]
)


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    scene["comforting_cat_v5_stage"] = "SILHOUETTE_REVIEW"
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_render = False
    obj.hide_viewport = False
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if coverage["back_y_margin"] <= 0.01:
    errors.append("Robe does not cover the body at the back")
if coverage["front_y_margin"] <= 0.01:
    errors.append("Robe does not cover the body at the front")
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

triangle_count = 0
for obj in export_objects:
    if obj.type != "MESH":
        continue
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    triangle_count += sum(max(0, len(face.vertices) - 2) for face in mesh.polygons)
    evaluated.to_mesh_clear()

scene_graph = {
    "schema_version": "1.0",
    "goal": "Replace the cylindrical costume silhouette with a lower-full pear-shaped robe that covers the body and carries a smaller chest inset.",
    "mode": "TRUE_360",
    "units": "METERS",
    "parts": [
        {
            "id": "Cat_BlueRobe",
            "name": "pear-shaped blue robe",
            "representation": "CLOSED_MESH",
            "dimensions": after["robe"]["dimensions"],
            "material_group": robe.data.materials[0].name,
            "source_confidence": 0.83,
            "notes": "Lower width is fuller; front/back depth exceeds body bounds.",
        },
        {
            "id": "Cat_RobeFrontInset",
            "name": "reduced pale chest inset",
            "representation": "CLOSED_MESH",
            "dimensions": after["front_inset"]["dimensions"],
            "material_group": inset.data.materials[0].name,
            "source_confidence": 0.80,
            "notes": "Top-anchored height compression and narrower width.",
        },
    ],
    "relations": [
        {
            "a": "Cat_BlueRobe",
            "type": "OVERLAPS",
            "b": "Cat_Body",
            "minimum_overlap": 0.01,
            "tolerance": 0.004,
        },
        {
            "a": "Cat_RobeFrontInset",
            "type": "OVERLAPS",
            "b": "Cat_BlueRobe",
            "minimum_overlap": 0.004,
            "tolerance": 0.004,
        },
    ],
    "camera": {
        "type": "ORTHOGRAPHIC",
        "review_views": ["front", "front_3q", "side", "back"],
    },
    "acceptance": {
        "dominant_defect": "cylindrical_robe_and_body_showthrough",
        "requirements": [
            "robe is narrower at shoulders and fuller near the lower body",
            "orange body no longer dominates the back view through the robe",
            "pale inset is smaller and no longer reads as a rectangular shield",
            "head, face, pose, accessories and materials remain unchanged",
        ],
        "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    },
}
(REPORT_DIR / f"{ASSET}_scene_graph.json").write_text(
    json.dumps(scene_graph, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
report = {
    "asset": ASSET,
    "stage": "COSTUME_GEOMETRY",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "cylindrical_robe_and_body_showthrough",
    "bounds_before": before,
    "bounds_after": after,
    "coverage": coverage,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
    "triangles": triangle_count,
    "exportable_objects": len(export_objects),
    "outputs": {
        "blend": str(FINAL_BLEND),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(RENDER_DIR / f"{ASSET}_02_material_front.png"),
        "three_quarter": str(RENDER_DIR / f"{ASSET}_03_front_3q.png"),
        "side": str(RENDER_DIR / f"{ASSET}_04_side.png"),
        "back": str(RENDER_DIR / f"{ASSET}_05_back.png"),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    },
}
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_COSTUME=" + json.dumps(report, ensure_ascii=False))
