"""Open the stable v5 source selected for the separate v6 rebuild."""

from pathlib import Path

import bpy


SOURCE = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend\comforting_cat_v5_lower_robe_hem_attempt1.blend"
).resolve()
if not SOURCE.exists():
    raise RuntimeError(f"Missing stable source: {SOURCE}")
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
print(f"COMFORTING_CAT_V6_STABLE_SOURCE={SOURCE}")
