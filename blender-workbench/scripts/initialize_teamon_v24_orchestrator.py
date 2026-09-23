from __future__ import annotations

import runpy
from pathlib import Path


PROJECT_ROOT = Path(r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template")
MODULE_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "research-feedback-upgrade"
    / "04_python"
    / "stage_orchestrator.py"
)
STATE_PATH = (
    PROJECT_ROOT
    / "blender-workbench"
    / "artifacts"
    / "reports"
    / "teamon_reference_v24_stage_state.json"
)

StageOrchestrator = runpy.run_path(str(MODULE_PATH))["StageOrchestrator"]
orchestrator = StageOrchestrator.create(
    "teamon-reference-v24",
    "Improve curled-finger, thumb, and palm silhouette while preserving index contact",
    memory_limit=5,
)
orchestrator.save(STATE_PATH)
print(STATE_PATH)
