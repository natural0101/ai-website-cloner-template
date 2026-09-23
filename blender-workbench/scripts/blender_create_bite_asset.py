import json
import sys

KIT_PYTHON = r"C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\python"
OUTPUT_ROOT = r"C:\Users\se-20\Documents\Codex\blender-agent-output"

if KIT_PYTHON not in sys.path:
    sys.path.insert(0, KIT_PYTHON)

import ai_blender_toolkit as abt

abt.configure(output_root=OUTPUT_ROOT)

result = abt.dispatch(
    "workflow.create_plastic_text_asset",
    {
        "text": "BITE",
        "asset_name": "bite_3d_logo",
        "reset": False,
        "checkpoint_before": True,
        "mode": "GLYPHS",
        "size": 1.7,
        "depth": 0.34,
        "bevel": 0.16,
        "palette": ["#F04438", "#FFCC33", "#30C48D", "#2D9CDB"],
        "seed": 18,
        "render": True,
        "multiview": False,
        "export": True,
        "save_blend": True,
        "resolution": 1024,
        "view": "FRONT_3Q",
        "transparent": True,
        "add_floor": False,
        "render_engine": "BLENDER_EEVEE",
        "render_samples": 64,
        "max_triangles": 100000,
    },
)

print(json.dumps(result, ensure_ascii=False, indent=2))
