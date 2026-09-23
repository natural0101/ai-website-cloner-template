"""The small code block an execute-code MCP can run inside Blender."""

from pathlib import Path
import sys

UPGRADE = Path(__file__).resolve().parents[1]
TOOLS = UPGRADE / "04_blender_tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import shape_dispatcher

print(shape_dispatcher.dispatch_json({
    "action": "shape.create_part",
    "arguments": {
        "kind": "ELLIPSOID",
        "name": "SemanticPalm",
        "location": [0, 0, 0],
        "scale": [0.8, 0.35, 1.0],
        "collection_name": "ABT_EXAMPLE_SOURCE",
        "material": {
            "name": "MAT_Example",
            "base_color": [0.95, 0.45, 0.62, 1],
            "roughness": 0.5
        }
    }
}))
