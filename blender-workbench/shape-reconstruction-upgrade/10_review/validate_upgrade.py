"""Static package validation: Python syntax, JSON, required files, path hygiene."""

from __future__ import annotations

import json
from pathlib import Path
import py_compile

HERE = Path(__file__).resolve().parent
UPGRADE = HERE.parent
required = [
    "README_RU.md",
    "01_agent_memory/AGENT_MEMORY_CARD_RU.md",
    "03_workflows/TRUE_3D_FROM_PRIMITIVES_RU.md",
    "04_blender_tools/shape_tools.py",
    "04_blender_tools/shape_dispatcher.py",
    "05_external_tools/reference_preprocess.py",
    "07_mcp/tool_manifest_shape.json",
    "skills/blender-shape-reconstruction/SKILL.md",
    "demo/combined.contours.json",
    "demo/layer_stack.example.json",
]
errors = []
checks = []

for rel in required:
    exists = (UPGRADE / rel).is_file()
    checks.append({"check": f"required:{rel}", "pass": exists})
    if not exists:
        errors.append(f"Missing required file: {rel}")

for path in sorted(UPGRADE.rglob("*.py")):
    try:
        py_compile.compile(str(path), doraise=True)
        checks.append({"check": f"py_compile:{path.relative_to(UPGRADE)}", "pass": True})
    except Exception as exc:
        checks.append({"check": f"py_compile:{path.relative_to(UPGRADE)}", "pass": False, "error": str(exc)})
        errors.append(f"Python syntax: {path}: {exc}")

for path in sorted(UPGRADE.rglob("*.json")):
    try:
        json.loads(path.read_text(encoding="utf-8"))
        checks.append({"check": f"json:{path.relative_to(UPGRADE)}", "pass": True})
    except Exception as exc:
        checks.append({"check": f"json:{path.relative_to(UPGRADE)}", "pass": False, "error": str(exc)})
        errors.append(f"JSON: {path}: {exc}")

report = {"status": "pass" if not errors else "fail", "errors": errors, "checks": checks}
(HERE / "STATIC_VALIDATION.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
