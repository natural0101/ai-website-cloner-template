from pathlib import Path
from datetime import datetime

import bpy


workbench = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench")
checkpoint_dir = workbench / "artifacts" / "blend" / "checkpoints"
checkpoint_dir.mkdir(parents=True, exist_ok=True)
path = checkpoint_dir / f"teamon_live_prechange_{datetime.now().strftime('%Y%m%d_%H%M%S')}.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(path))
print({"checkpoint": str(path), "bytes": path.stat().st_size})
