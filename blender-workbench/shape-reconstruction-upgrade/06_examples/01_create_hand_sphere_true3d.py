"""Run from a new Blender file. Creates editable sphere + two stylized hands."""

from pathlib import Path
import json
import sys
import bpy

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
TOOLS = UPGRADE / "04_blender_tools"
OUTPUT = UPGRADE / "demo" / "example_outputs" / "hand_sphere"
OUTPUT.mkdir(parents=True, exist_ok=True)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_tools as st

result = st.create_hand_sphere_icon(
    name="HandSphereHero",
    sphere_radius=1.0,
    sphere_color=(0.12, 0.50, 0.72, 1.0),
    hand_color=(1.0, 0.28, 0.62, 1.0),
    merge_hands=True,
    voxel_size=0.055,
)

st.setup_reference_camera(width=309, height=250, world_height=4.2, distance=10.0)
mask = st.render_silhouette_mask(filepath=OUTPUT / "silhouette.png")
validation = st.validate_shape_asset(max_triangles=80_000, require_closed=True)
export = st.export_glb(filepath=OUTPUT / "hand_sphere.glb")
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "hand_sphere.blend"))

report = {
    "create": result,
    "silhouette": mask,
    "validation": validation,
    "export": export,
    "scene": st.scene_report(),
}
(OUTPUT / "report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False, indent=2))
