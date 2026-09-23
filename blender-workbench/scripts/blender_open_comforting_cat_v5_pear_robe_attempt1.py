"""Open the clean pre-cheek checkpoint for the next reversible head pass."""

from pathlib import Path

import bpy


SOURCE_BLEND = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend\comforting_cat_v5_pear_robe_attempt1.blend"
).resolve()

if not SOURCE_BLEND.exists():
    raise FileNotFoundError(SOURCE_BLEND)

bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
print(f"OPENED_BLEND={Path(bpy.data.filepath).resolve()}")
