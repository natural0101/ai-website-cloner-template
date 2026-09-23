"""General from-scratch pattern: named masses -> overlap -> voxel union -> GLB."""

from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
TOOLS = UPGRADE / "04_blender_tools"
OUTPUT = UPGRADE / "demo" / "example_outputs" / "mascot"
OUTPUT.mkdir(parents=True, exist_ok=True)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_tools as st

source = st.ensure_collection("ABT_Mascot_SOURCE")
output = st.ensure_collection("ABT_Mascot_OUTPUT")
body_mat = st.create_principled_material(
    "MAT_Mascot_Body", base_color=(0.56, 0.42, 0.95, 1), roughness=0.48
)
parts = [
    st.create_ellipsoid(
        name="Mascot_Body", location=(0, 0, 0), scale=(0.75, 0.52, 0.95),
        collection=source, material=body_mat
    ),
    st.create_ellipsoid(
        name="Mascot_Head", location=(0, -0.03, 0.92), scale=(0.62, 0.50, 0.58),
        collection=source, material=body_mat
    ),
]
parts += st.create_bezier_tube(
    name="Mascot_LeftArm",
    points=[(-0.55, 0, 0.45), (-0.95, -0.04, 0.25), (-1.12, -0.08, 0.55)],
    radii=(0.20, 0.17, 0.13), collection=source, material=body_mat
)
parts += st.create_bezier_tube(
    name="Mascot_RightArm",
    points=[(0.55, 0, 0.45), (0.95, -0.04, 0.25), (1.12, -0.08, 0.55)],
    radii=(0.20, 0.17, 0.13), collection=source, material=body_mat
)
for side in (-1, 1):
    parts.append(st.create_ellipsoid(
        name=f"Mascot_Foot_{side}", location=(side * 0.38, -0.05, -0.82),
        scale=(0.38, 0.42, 0.24), collection=source, material=body_mat
    ))

merged = st.voxel_union(
    parts, name="Mascot_Merged", voxel_size=0.045,
    smooth_factor=0.24, smooth_iterations=2,
    output_collection=output, keep_sources=True, material=body_mat, export=True
)

st.setup_reference_camera(width=512, height=512, world_height=3.5, distance=9)
st.render_silhouette_mask(filepath=OUTPUT / "silhouette.png", object_names=[merged.name])
validation = st.validate_shape_asset(object_names=[merged.name], max_triangles=60_000)
export = st.export_glb(filepath=OUTPUT / "mascot.glb", object_names=[merged.name])
print(json.dumps({"validation": validation, "export": export}, indent=2))
