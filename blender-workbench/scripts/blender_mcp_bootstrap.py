import sys

KIT_PYTHON = r"C:\Users\se-20\Documents\Codex\AI_Blender_Agent_Kit\python"
OUTPUT_ROOT = r"C:\Users\se-20\Documents\Codex\blender-agent-output"

if KIT_PYTHON not in sys.path:
    sys.path.insert(0, KIT_PYTHON)

import ai_blender_toolkit as abt

abt.configure(output_root=OUTPUT_ROOT)

print(
    abt.dispatch_json(
        {
            "action": "scene.inspect",
            "arguments": {
                "object_limit": 200,
                "include_mesh_stats": True,
            },
        }
    )
)
