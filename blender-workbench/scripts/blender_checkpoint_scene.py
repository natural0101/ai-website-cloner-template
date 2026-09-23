from pathlib import Path

import bpy


checkpoint_dir = Path(r"C:\Users\se-20\Documents\Codex\blender-agent-output\blend\checkpoints")
checkpoint_dir.mkdir(parents=True, exist_ok=True)
checkpoint_path = checkpoint_dir / "before_hands_sphere_icon.blend"

bpy.ops.wm.save_as_mainfile(filepath=str(checkpoint_path))
print({"status": "checkpoint_saved", "path": str(checkpoint_path)})
