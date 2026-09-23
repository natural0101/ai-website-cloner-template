"""Open the last accepted pre-compact checkpoint."""

from pathlib import Path

import bpy


SOURCE_BLEND = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend"
    r"\comforting_cat_v5_leg_paw_grounding_attempt1.blend"
).resolve()

if not SOURCE_BLEND.exists():
    raise FileNotFoundError(SOURCE_BLEND)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
print(f"OPENED_BLEND={Path(bpy.data.filepath).resolve()}")
