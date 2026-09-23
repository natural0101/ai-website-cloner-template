from pathlib import Path

import bpy


render_path = Path(
    r"C:\Users\se-20\Documents\Codex\blender-agent-output\renders\bite_site_silver_logo_beauty_view.png"
)
render_path.parent.mkdir(parents=True, exist_ok=True)

bpy.context.scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

print({"status": "rendered", "path": str(render_path)})
