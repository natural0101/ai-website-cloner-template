import json
from pathlib import Path

TOOLS = Path(
    r"C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\design_upgrade\03_blender_tools\design_tools.py"
)

namespace = {}
exec(TOOLS.read_text(encoding="utf-8"), namespace)

print(
    json.dumps(
        {
            "status": "ok",
            "tools": str(TOOLS),
            "material_presets": sorted(namespace["MATERIAL_PRESETS"].keys()),
            "text_geometry_presets": sorted(namespace["TEXT_GEOMETRY_PRESETS"].keys()),
            "has_reflection_cards": callable(namespace.get("add_reflection_cards")),
            "has_designed_text": callable(namespace.get("create_designed_text")),
            "has_scene_report": callable(namespace.get("scene_design_report")),
        },
        ensure_ascii=False,
        indent=2,
    )
)
