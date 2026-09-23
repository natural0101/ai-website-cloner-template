from __future__ import annotations

import json
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
SOURCE_BLEND = WORKBENCH / "artifacts" / "blend" / "teamon_reference_v45_thumb_pose_attempt03.blend"
OUTPUT = WORKBENCH / "artifacts" / "previews" / "teamon-v45-segmented-overlay-probe.png"
REPORT = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_segmented_overlay_probe.json"

CAMERA_RIGHT = Vector((0.6248648167, 0.7807329893, 0.0)).normalized()
CAMERA_UP = Vector((-0.4777820706, 0.3823961020, 0.7908840775)).normalized()
CAMERA_FORWARD = Vector((-0.6174692512, 0.4941956103, -0.6119660139)).normalized()
ROOT_TIP = {
    "Middle": (Vector((2.317201, 1.778719, 2.451198)), Vector((1.694164, 0.860260, 2.338133))),
    "Ring": (Vector((2.285797, 2.347095, 2.683837)), Vector((1.737959, 1.539684, 2.584574))),
    "Little": (Vector((2.417904, 2.890847, 2.911310)), Vector((1.929323, 2.169445, 2.821715))),
}
CHAIN_FRACTIONS = (0.0, 0.333, 0.666, 1.0)
CHAIN_FRONT_LIFT = (0.0, 0.08, 0.14, 0.18)
CHAINS = {
    finger: tuple(
        root.lerp(tip, fraction) - CAMERA_FORWARD * lift
        for fraction, lift in zip(CHAIN_FRACTIONS, CHAIN_FRONT_LIFT)
    )
    for finger, (root, tip) in ROOT_TIP.items()
}
WIDTHS = {
    "Middle": (0.64, 0.60, 0.56),
    "Ring": (0.48, 0.45, 0.42),
    "Little": (0.38, 0.36, 0.34),
}
LENGTH_MULTIPLIER = {"Middle": 1.30, "Ring": 1.32, "Little": 1.34}
JOINT_RADII = {"Middle": 0.082, "Ring": 0.078, "Little": 0.074}
PROXIMAL_LENGTHS = {"Middle": 0.80, "Ring": 0.72, "Little": 0.62}
SEGMENT_UP = {"Middle": (0.0, 0.04, 0.06), "Ring": (0.0, 0.02, 0.04), "Little": (0.0, 0.0, 0.0)}


def basis_for(long_axis: Vector) -> Matrix:
    depth_axis = CAMERA_FORWARD.copy()
    vertical_axis = long_axis.cross(depth_axis).normalized()
    if vertical_axis.dot(CAMERA_UP) < 0.0:
        depth_axis.negate()
        vertical_axis = long_axis.cross(depth_axis).normalized()
    return Matrix((long_axis, depth_axis, vertical_axis)).transposed().to_4x4()


def rounded_block(name: str, center: Vector, long_axis: Vector, length: float, depth: float, height: float, material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.matrix_world = Matrix.Translation(center) @ basis_for(long_axis) @ Matrix.Diagonal((length, depth, height, 1.0))
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new("TEAMON_RoundedShell", "BEVEL")
    bevel.width = min(depth, height) * 0.35
    bevel.segments = 5
    bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.materials.append(material)
    return obj


def rose_joint(name: str, center: Vector, radius: float, material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (1.0, 0.82, 1.0)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.materials.append(material)
    return obj


if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
    raise RuntimeError(f"Expected attempt03 source, got {bpy.data.filepath}")

white = bpy.data.materials["TEAMON_Robot_White_Ada"]
rose = bpy.data.materials["TEAMON_Robot_Joint_Rose_Ada"]
hand_root = bpy.data.objects["TEAMON_HandPressGroup"]
for finger in CHAINS:
    for suffix in ("", "_Joint01", "_Joint02", "_Joint03"):
        bpy.data.objects[f"TEAMON_Ada_{finger}{suffix}"].hide_render = True

created = []
for finger, nodes in CHAINS.items():
    radius = JOINT_RADII[finger]
    for joint_index, node in enumerate(nodes[:3]):
        created.append(
            rose_joint(
                f"TEAMON_V45_{finger}_Joint{joint_index:02d}",
                node - CAMERA_FORWARD * 0.028,
                radius,
                rose,
            )
        )
    proximal_axis = (nodes[0] - nodes[1]).normalized()
    if finger == "Little":
        proximal_axis = (CAMERA_RIGHT - CAMERA_UP * 0.40).normalized()
    proximal_length = PROXIMAL_LENGTHS[finger]
    proximal_width = WIDTHS[finger][0] * 1.12
    created.append(
        rounded_block(
            f"TEAMON_V45_{finger}_Shell00",
            nodes[0] + proximal_axis * (proximal_length * 0.45) - CAMERA_FORWARD * 0.08,
            proximal_axis,
            proximal_length,
            proximal_width * 1.08,
            proximal_width,
            white,
        )
    )
    for segment_index in range(3):
        start = nodes[segment_index].copy()
        end = nodes[segment_index + 1].copy()
        long_axis = (end - start).normalized()
        center = (
            (start + end) * 0.5
            - CAMERA_FORWARD * 0.07
            + CAMERA_UP * SEGMENT_UP[finger][segment_index]
        )
        length = (end - start).length * LENGTH_MULTIPLIER[finger]
        width = WIDTHS[finger][segment_index]
        created.append(
            rounded_block(
                f"TEAMON_V45_{finger}_Shell{segment_index + 1:02d}",
                center,
                long_axis,
                length,
                width * 1.05,
                width,
                white,
            )
        )

for obj in created:
    world = obj.matrix_world.copy()
    obj.parent = hand_root
    obj.matrix_world = world
    obj["export"] = True

bpy.context.view_layer.update()
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.frame_set(1)
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUTPUT)
bpy.ops.render.render(write_still=True)
REPORT.write_text(
    json.dumps(
        {
            "source": str(SOURCE_BLEND),
            "render": str(OUTPUT),
            "hidden_existing": [f"TEAMON_Ada_{finger}{suffix}" for finger in CHAINS for suffix in ("", "_Joint01", "_Joint02", "_Joint03")],
            "created": [obj.name for obj in created],
            "chains": {finger: [list(point) for point in points] for finger, points in CHAINS.items()},
            "widths": WIDTHS,
            "joint_radii": JOINT_RADII,
            "saved_blend": False,
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n",
    encoding="utf-8",
)
print(REPORT.read_text(encoding="utf-8"))
