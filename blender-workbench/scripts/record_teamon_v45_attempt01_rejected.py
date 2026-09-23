from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
STATE_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_stage_state.json"
MODULE_PATH = WORKBENCH / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt01_report.json"
PREVIEWS = WORKBENCH / "artifacts" / "previews"
ATTEMPT_ID = "v45-attempt01-restore-attached-pose-d"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

if not any(attempt.attempt_id == ATTEMPT_ID for attempt in orchestrator.state.attempts):
    orchestrator.record_attempt(
        ATTEMPT_ID,
        "Restore the connected pose-d middle/ring/little geometry without the erroneous composition offsets while preserving the fixed index contact and runtime contract.",
        ["mesh", "connections"],
        render_paths=[
            str(PREVIEWS / "teamon-v45-attempt01-pose-d-hero.png"),
            str(PREVIEWS / "teamon-v45-attempt01-pose-d-front.png"),
            str(PREVIEWS / "teamon-v45-attempt01-pose-d-side.png"),
        ],
        audit_path=str(REPORT_PATH),
    )

orchestrator.review_attempt(
    ATTEMPT_ID,
    approved=False,
    dominant_mismatch=(
        "Structural reconnection passes, but the visible pose still fails: palm/wrist mass remains "
        "approximately 78 px left and 136 px down with about 24 degrees clockwise bias; the thumb "
        "remains roughly 282 px too far left; the upper finger cluster still reads end-on/upright "
        "instead of layered horizontal shells."
    ),
    next_edit=(
        "Build a versioned screen-space pose candidate around the immutable index/keycap contact: "
        "rotate/reposition palm-wrist mass upward/right, then retract the thumb and lay the connected "
        "middle/ring/little cluster toward the right crop."
    ),
    checklist=[
        "Index contact remains within 8 px of the reference and within 0.002 world units of the keycap.",
        "Palm/wrist centroid and principal direction approach the locked reference without changing the camera or button.",
        "Middle, ring, and little remain attached and form layered horizontal shells rather than upright tips.",
        "Thumb tip returns to the lower-right reference region and does not cross the lower-left button area.",
        "Hero, front, and side views show no disconnected bases, plate-like collapse, or new intersections.",
        "Button, camera, materials, lights, topology, object transforms, action names, timing, and press travel remain unchanged.",
    ],
)
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
