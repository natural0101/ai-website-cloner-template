"""FRONT_2_5D example using the bundled copyright-free synthetic mask."""

from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
TOOLS = UPGRADE / "04_blender_tools"
OUTPUT = UPGRADE / "demo" / "example_outputs" / "contour_relief"
OUTPUT.mkdir(parents=True, exist_ok=True)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_tools as st

material = st.create_principled_material(
    "MAT_Contour_Demo", base_color=(0.25, 0.65, 0.95, 1), roughness=0.42
)
created = st.import_contour_json(
    contour_json=UPGRADE / "demo" / "combined.contours.json",
    name="DemoRelief", thickness=0.16, bevel=0.0, scale=4.0,
    material=material, convert_mesh=False, export=True
)
camera = st.setup_reference_camera(width=309, height=250, world_height=4.0, distance=10)
mask = st.render_silhouette_mask(filepath=OUTPUT / "blender_mask.png")
print(json.dumps({"created": created, "camera": camera, "mask": mask}, indent=2))

# Next, outside Blender, run reference_preprocess.py compare as shown in
# 05_external_tools/USAGE_RU.md.
