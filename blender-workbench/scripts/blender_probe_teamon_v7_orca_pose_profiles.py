import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
BODY_XML = PROJECT_ROOT / "blender-workbench" / "vendor" / "orcahand_description" / "v2" / "models" / "mjcf" / "orcahand_right_body.xml"
PREVIEW_ROOT = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)


def parse_vec(value, size=3, default=None):
    if value is None:
        return list(default if default is not None else ([0.0] * size))
    return [float(item) for item in value.split()]


def quat_matrix(value):
    quaternion = Quaternion(parse_vec(value, 4, (1.0, 0.0, 0.0, 0.0)))
    quaternion.normalize()
    return quaternion.to_matrix().to_4x4()


def transform_matrix(pos=None, quat=None):
    return Matrix.Translation(Vector(parse_vec(pos, 3, (0.0, 0.0, 0.0)))) @ quat_matrix(quat)


def body_local_matrix(body_element, pose):
    matrix = transform_matrix(body_element.get("pos"), body_element.get("quat"))
    for joint in body_element.findall("joint"):
        axis = Vector(parse_vec(joint.get("axis"), 3, (1.0, 0.0, 0.0))).normalized()
        pivot = Vector(parse_vec(joint.get("pos"), 3, (0.0, 0.0, 0.0)))
        angle = pose.get(joint.get("name"), float(joint.get("ref", "0")))
        matrix @= Matrix.Translation(pivot) @ Quaternion(axis, angle).to_matrix().to_4x4() @ Matrix.Translation(-pivot)
    return matrix


def apply_pose(body_element, pose):
    body_name = body_element.get("name")
    body_object = bpy.data.objects.get(f"TEAMON_ORCA_{body_name}")
    if body_object is not None:
        body_object.matrix_local = body_local_matrix(body_element, pose)
    for child in body_element.findall("body"):
        apply_pose(child, pose)


profiles = {
    "compact": {
        "right_wrist": 0.06,
        "right_p-abd": 0.0, "right_p-mcp": 1.02, "right_p-pip": 1.20,
        "right_r-abd": 0.0, "right_r-mcp": 0.96, "right_r-pip": 1.16,
        "right_m-abd": 0.0, "right_m-mcp": 0.88, "right_m-pip": 1.10,
        "right_i-abd": 0.0, "right_i-mcp": 0.0, "right_i-pip": 0.03,
        "right_t-cmc": 0.12, "right_t-abd": 0.48, "right_t-mcp": 0.58, "right_t-pip": 0.62,
    },
    "balanced": {
        "right_wrist": 0.06,
        "right_p-abd": -0.01, "right_p-mcp": 0.70, "right_p-pip": 0.80,
        "right_r-abd": 0.0, "right_r-mcp": 0.62, "right_r-pip": 0.72,
        "right_m-abd": 0.01, "right_m-mcp": 0.55, "right_m-pip": 0.64,
        "right_i-abd": 0.0, "right_i-mcp": 0.0, "right_i-pip": 0.03,
        "right_t-cmc": 0.12, "right_t-abd": 0.48, "right_t-mcp": 0.50, "right_t-pip": 0.54,
    },
    "open": {
        "right_wrist": 0.06,
        "right_p-abd": -0.02, "right_p-mcp": 0.56, "right_p-pip": 0.62,
        "right_r-abd": 0.0, "right_r-mcp": 0.50, "right_r-pip": 0.56,
        "right_m-abd": 0.02, "right_m-mcp": 0.44, "right_m-pip": 0.50,
        "right_i-abd": 0.0, "right_i-mcp": 0.0, "right_i-pip": 0.03,
        "right_t-cmc": 0.12, "right_t-abd": 0.48, "right_t-mcp": 0.46, "right_t-pip": 0.50,
    },
}

body_root = ET.parse(BODY_XML).getroot()
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

for profile_name, pose in profiles.items():
    for body_element in body_root.findall("body"):
        apply_pose(body_element, pose)
    bpy.context.view_layer.update()
    scene.render.filepath = str(PREVIEW_ROOT / f"teamon-v7-orca-pose-{profile_name}.png")
    bpy.ops.render.render(write_still=True)
