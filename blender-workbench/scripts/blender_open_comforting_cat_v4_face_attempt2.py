"""Open the accepted v4 face attempt for a fresh QA pass."""

from pathlib import Path

import bpy


workbench = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
source = (
    workbench
    / "artifacts"
    / "blend"
    / "comforting_cat_v4_face_geometry_attempt2.blend"
).resolve()
source.relative_to(workbench)
if not source.exists():
    raise FileNotFoundError(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
print(f"OPENED_COMFORTING_CAT_V4_FACE_ATTEMPT2={source}")
