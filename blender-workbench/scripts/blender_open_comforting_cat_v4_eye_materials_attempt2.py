"""Open the selected v4 eye-material checkpoint in a dedicated socket call."""

from pathlib import Path

import bpy


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
SOURCE_BLEND = (
    WORKBENCH / "artifacts" / "blend" / "comforting_cat_v4_eye_materials_attempt2.blend"
).resolve()
SOURCE_BLEND.relative_to(WORKBENCH)
if not SOURCE_BLEND.exists():
    raise FileNotFoundError(SOURCE_BLEND)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
print(f"OPENED_COMFORTING_CAT_V4={SOURCE_BLEND}")
