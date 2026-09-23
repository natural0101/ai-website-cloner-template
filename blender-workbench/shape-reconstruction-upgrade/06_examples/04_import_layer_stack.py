"""Imports left hand, right hand and sphere with explicit depth ordering."""

from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
TOOLS = UPGRADE / "04_blender_tools"
OUTPUT = UPGRADE / "demo" / "example_outputs" / "layer_stack"
OUTPUT.mkdir(parents=True, exist_ok=True)
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_tools as st

result = st.import_layer_stack(UPGRADE / "demo" / "layer_stack.example.json")
st.setup_reference_camera(width=309, height=250, world_height=4.0, distance=10)
mask = st.render_silhouette_mask(filepath=OUTPUT / "blender_mask.png")
print(json.dumps({"layers": result, "mask": mask}, indent=2))
