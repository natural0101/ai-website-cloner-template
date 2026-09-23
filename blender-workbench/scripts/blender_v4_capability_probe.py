from __future__ import annotations

import json
from pathlib import Path
import sys


REPO = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
TOOLS = REPO / "blender-workbench" / "research-feedback-upgrade" / "04_blender"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import capability_probe


report = capability_probe.probe()
out = REPO / "blender-workbench" / "artifacts" / "reports" / "blender_v4_capability_probe.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
