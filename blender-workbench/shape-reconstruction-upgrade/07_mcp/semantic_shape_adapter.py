"""Build a minimal allow-listed Blender code call for shape_dispatcher."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def build_blender_code(
    *,
    shape_tools_dir: str | Path,
    action: str,
    arguments: Mapping[str, Any] | None = None,
) -> str:
    tools_path = str(Path(shape_tools_dir).expanduser().resolve())
    payload = json.dumps(
        {"action": action, "arguments": dict(arguments or {})}, ensure_ascii=False
    )
    return (
        "import sys\n"
        f"_shape_path = {tools_path!r}\n"
        "if _shape_path not in sys.path: sys.path.insert(0, _shape_path)\n"
        "import shape_dispatcher\n"
        f"print(shape_dispatcher.dispatch_json({payload!r}))\n"
    )


if __name__ == "__main__":
    print(build_blender_code(
        shape_tools_dir="/path/to/shape_reconstruction_upgrade/04_blender_tools",
        action="shape.scene_report",
    ))
