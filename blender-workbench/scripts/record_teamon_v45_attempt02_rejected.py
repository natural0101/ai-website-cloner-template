from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
STATE_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_stage_state.json"
MODULE_PATH = WORKBENCH / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt02_report.json"
PREVIEWS = WORKBENCH / "artifacts" / "previews"
ATTEMPT_ID = "v45-attempt02-palm-pose"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

if not any(attempt.attempt_id == ATTEMPT_ID for attempt in orchestrator.state.attempts):
    orchestrator.record_attempt(
        ATTEMPT_ID,
        "Rotate the connected palm/forearm/non-index cluster by -7.5 degrees around the fixed index contact and bridge Index_Joint01 at half angle.",
        ["mesh", "connections"],
        render_paths=[
            str(PREVIEWS / "teamon-v45-attempt02-palm-pose-hero.png"),
            str(PREVIEWS / "teamon-v45-attempt02-palm-pose-front.png"),
            str(PREVIEWS / "teamon-v45-attempt02-palm-pose-side.png"),
        ],
        audit_path=str(REPORT_PATH),
    )

orchestrator.review_attempt(
    ATTEMPT_ID,
    approved=False,
    dominant_mismatch=(
        "The palm/wrist angular error improved by 44.9 percent and all intended junctions remain connected, "
        "but the thumb still intersects the keycap and remains about 164 px left and 40 px above its target; "
        "the three upper fingers still form an uneven end-on staircase with a 34-44 px outer overshoot."
    ),
    next_edit=(
        "Keep attempt02 palm/index pose fixed and change only TEAMON_Ada_Thumb around its Palm-Thumb attachment: "
        "shorten the longitudinal reach, rotate the distal shell into the lower-right target, and require zero "
        "Thumb-Keycap overlap while preserving Palm-Thumb overlap."
    ),
    checklist=[
        "Thumb-Keycap overlap is exactly zero at rest and pressed frames.",
        "Palm-Thumb overlap remains at least 50 triangle pairs with no visible base gap.",
        "Thumb tip lies within 16 px of the perspective-registered lower-right target.",
        "Thumb thickness remains mechanical and does not collapse into a thin spike or plate.",
        "Index contact, palm pose, MRL geometry, topology, object matrices, camera, button, materials, and actions remain unchanged.",
    ],
)
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
