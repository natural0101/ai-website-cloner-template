"""Reload the clean attempt23 source after an interrupted reversible pass."""

from pathlib import Path

import bpy


source = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template"
    r"\blender-workbench\artifacts\blend"
    r"\comforting_cat_v6_hem_drape_attempt23.blend"
).resolve()
bpy.ops.wm.open_mainfile(filepath=str(source))
