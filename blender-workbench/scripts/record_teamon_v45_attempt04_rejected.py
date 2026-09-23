from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
STATE_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_stage_state.json"
MODULE_PATH = WORKBENCH / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt04_report.json"
PREVIEWS = WORKBENCH / "artifacts" / "previews"
ATTEMPT_ID = "v45-attempt04-mrl-pose"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

if not any(attempt.attempt_id == ATTEMPT_ID for attempt in orchestrator.state.attempts):
    orchestrator.record_attempt(
        ATTEMPT_ID,
        (
            "Rigidly reorient each Middle/Ring/Little shell and its joint fillers around verified palm pivots, "
            "then apply a shared camera-space translation while preserving all numeric contact constraints."
        ),
        ["mesh", "connections"],
        render_paths=[
            str(PREVIEWS / "teamon-v45-attempt04-hand-pose-hero.png"),
            str(PREVIEWS / "teamon-v45-attempt04-hand-pose-front.png"),
            str(PREVIEWS / "teamon-v45-attempt04-hand-pose-side.png"),
        ],
        audit_path=str(REPORT_PATH),
    )

orchestrator.review_attempt(
    ATTEMPT_ID,
    approved=False,
    dominant_mismatch=(
        "Numeric centroid and connectivity checks produced a false visual success: upper MRL visible area fell to "
        "73.8 percent of the reference, the pass lost 9703 net upper pixels versus attempt03, and all independent "
        "curled finger protrusions disappeared behind the palm."
    ),
    next_edit=(
        "Restart from attempt03 and adjust only per-finger screen height and small screen-plane roll while preserving "
        "the attempt03 depth ordering and visible-area floor; do not reuse the attempt04 yaw/pitch collapse or a pure "
        "depth translation."
    ),
    checklist=[
        "Upper MRL visible area is at least the attempt03 baseline 0.04558 canvas fraction.",
        "Three independent horizontal or stepped shell rows remain visibly readable in the hero render.",
        "MRL top-envelope error is no more than 16 px at the locked comparison samples.",
        "Palm-Middle/Ring/Little overlap remains at least 50 pairs each.",
        "All inter-finger, Index-MRL, and MRL-Keycap overlap pairs remain zero.",
        "All non-MRL meshes, transforms, materials, camera, button, and actions remain byte-stable.",
    ],
)
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
