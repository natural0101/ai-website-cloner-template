"""TRUE_360 costume pass: replace the rigid frustum with a soft pear robe."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ASSET = "comforting_cat_v5_pear_robe_attempt1"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_DIR = (WORKBENCH / "artifacts" / "blend").resolve()
RENDER_DIR = (WORKBENCH / "artifacts" / "renders").resolve()
EXPORT_DIR = (WORKBENCH / "artifacts" / "exports").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
CHECKPOINT_DIR = (BLEND_DIR / "checkpoints").resolve()
SOURCE_BLEND = (
    BLEND_DIR / "comforting_cat_v5_integrated_upper_lids_attempt1.blend"
).resolve()
FINAL_BLEND = (BLEND_DIR / f"{ASSET}.blend").resolve()
GLB_PATH = (EXPORT_DIR / f"{ASSET}.glb").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

for directory in (BLEND_DIR, RENDER_DIR, EXPORT_DIR, REPORT_DIR, CHECKPOINT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
if Path(bpy.data.filepath).resolve() != SOURCE_BLEND:
    raise RuntimeError(f"Expected already-open {SOURCE_BLEND}; got {bpy.data.filepath}")

checkpoint = (
    CHECKPOINT_DIR / "comforting_cat_v5_before_pear_robe_attempt1.blend"
).resolve()
bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint))


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def bounds(obj: bpy.types.Object) -> dict[str, list[float]]:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(corner[index] for corner in corners) for index in range(3)]
    maxs = [max(corner[index] for corner in corners) for index in range(3)]
    return {
        "min": [round(float(value), 6) for value in mins],
        "max": [round(float(value), 6) for value in maxs],
        "dimensions": [
            round(float(maxs[index] - mins[index]), 6) for index in range(3)
        ],
    }


root = bpy.data.objects["Cat_Root"]
source = bpy.data.objects["Cat_BlueRobe"]
before = bounds(source)
robe_material = source.material_slots[0].material

source.parent = None
source.hide_render = True
source.hide_viewport = True
source.name = "Cat_BlueRobe_SOURCE_V5_PEAR_A1"
source["comforting_cat_preserved_source"] = True
source["comforting_cat_rejection_reason"] = "rigid_two_ring_frustum"

# World-space profile: narrow shoulder, gentle lower-third fullness, tucked hem.
profile = [
    (0.720, 0.670, 0.455),
    (0.790, 0.688, 0.468),
    (0.930, 0.718, 0.492),
    (1.120, 0.730, 0.505),
    (1.350, 0.714, 0.500),
    (1.580, 0.682, 0.480),
    (1.820, 0.642, 0.452),
    (2.050, 0.596, 0.420),
    (2.240, 0.560, 0.398),
    (2.330, 0.548, 0.392),
]
segments = 48
center_y = 0.040
vertices: list[tuple[float, float, float]] = []
for z_value, radius_x, radius_y in profile:
    for index in range(segments):
        angle = math.tau * index / segments
        # Front is negative Y. A small chest bias makes the front slightly
        # fuller than the back without changing the contact envelope.
        front_weight = max(0.0, -math.sin(angle))
        y_radius = radius_y * (1.0 + 0.018 * front_weight)
        vertices.append(
            (
                radius_x * math.cos(angle),
                center_y + y_radius * math.sin(angle),
                z_value,
            )
        )

faces: list[tuple[int, ...]] = []
for ring in range(len(profile) - 1):
    start = ring * segments
    next_start = (ring + 1) * segments
    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append(
            (
                start + index,
                start + next_index,
                next_start + next_index,
                next_start + index,
            )
        )

bottom_center = len(vertices)
vertices.append((0.0, center_y, profile[0][0]))
top_center = len(vertices)
vertices.append((0.0, center_y, profile[-1][0]))
for index in range(segments):
    next_index = (index + 1) % segments
    faces.append((bottom_center, next_index, index))
    top_start = (len(profile) - 1) * segments
    faces.append((top_center, top_start + index, top_start + next_index))

mesh = bpy.data.meshes.new("Cat_BlueRobe_PearMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()
robe = bpy.data.objects.new("Cat_BlueRobe", mesh)
source_collection = source.users_collection[0] if source.users_collection else bpy.context.scene.collection
source_collection.objects.link(robe)
robe.parent = root
robe.matrix_parent_inverse = root.matrix_world.inverted()
robe.matrix_world = Matrix.Identity(4)
robe.data.materials.append(robe_material)
for polygon in robe.data.polygons:
    polygon.use_smooth = polygon.center.z not in {profile[0][0], profile[-1][0]}
robe["comforting_cat_role"] = "soft_pear_robe"
robe["comforting_cat_profile"] = json.dumps(profile)

# Weighted normals preserve the soft side shading while keeping hem/top readable.
bevel = robe.modifiers.new("PearRobeSoftHem", "BEVEL")
bevel.width = 0.020
bevel.segments = 2
bevel.limit_method = "ANGLE"
bpy.context.view_layer.update()
after = bounds(robe)

scene = bpy.context.scene
scene.name = "Comforting_Cat_V5_PearRobe_A1"
scene["comforting_cat_target_mode"] = "TRUE_360"
scene["comforting_cat_v5_stage"] = "ROBE_VOLUME_RECONSTRUCTION"
scene["comforting_cat_v5_geometry_attempt"] = "pear_robe_1"
scene["comforting_cat_v5_dominant_defect"] = "rigid_straight_sided_frustum_robe"
scene["comforting_cat_v5_do_not_change"] = json.dumps(
    [
        "collar and scarf",
        "head and face",
        "chest inset",
        "arms and sleeves",
        "legs and feet",
        "satchel and strap",
        "tail",
        "materials",
        "lighting and cameras",
    ]
)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def render_view(
    camera: bpy.types.Object,
    suffix: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    scale: float,
) -> None:
    camera.location = location
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = scale
    look_at(camera, target)
    scene.camera = camera
    scene.render.filepath = str(RENDER_DIR / f"{ASSET}_{suffix}.png")
    bpy.ops.render.render(write_still=True)


export_objects = descendants(root)
camera = bpy.data.objects["CAT_RenderCamera"]
render_view(camera, "02_material_front", (0.0, -8.6, 3.15), (0.0, -0.04, 2.03), 4.65)
render_view(camera, "03_front_3q", (4.0, -7.4, 3.45), (0.0, -0.02, 1.98), 4.75)
render_view(camera, "04_side", (8.4, -0.35, 3.15), (0.0, 0.0, 1.92), 4.75)
render_view(camera, "05_back", (0.0, 8.4, 3.15), (0.0, 0.04, 1.92), 4.75)
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
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
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "ROBE_VOLUME_RECONSTRUCTION",
    "attempt": 1,
    "target_mode": "TRUE_360",
    "source_blend": str(SOURCE_BLEND),
    "checkpoint": str(checkpoint),
    "dominant_defect": "rigid_straight_sided_frustum_robe",
    "preserved_hidden_source": source.name,
    "profile": profile,
    "before": before,
    "after": after,
    "do_not_change": json.loads(scene["comforting_cat_v5_do_not_change"]),
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
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
print("COMFORTING_CAT_V5_PEAR_ROBE_A1=" + json.dumps(report, ensure_ascii=False))
