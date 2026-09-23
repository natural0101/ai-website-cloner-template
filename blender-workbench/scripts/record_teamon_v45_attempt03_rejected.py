from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
WORKBENCH = PROJECT_ROOT / "blender-workbench"
STATE_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_stage_state.json"
MODULE_PATH = WORKBENCH / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
REPORT_PATH = WORKBENCH / "artifacts" / "reports" / "teamon_reference_v45_attempt03_report.json"
PREVIEWS = WORKBENCH / "artifacts" / "previews"
ATTEMPT_ID = "v45-attempt03-thumb-pose"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

if not any(attempt.attempt_id == ATTEMPT_ID for attempt in orchestrator.state.attempts):
    orchestrator.record_attempt(
        ATTEMPT_ID,
        "Apply a proximal-preserving nonlinear cage to TEAMON_Ada_Thumb, shortening its axial reach to 60 percent and bending the distal shell 15 degrees into the lower-right target.",
        ["mesh", "connections"],
        render_paths=[
            str(PREVIEWS / "teamon-v45-attempt03-thumb-pose-hero.png"),
            str(PREVIEWS / "teamon-v45-attempt03-thumb-pose-front.png"),
            str(PREVIEWS / "teamon-v45-attempt03-thumb-pose-side.png"),
        ],
        audit_path=str(REPORT_PATH),
    )

orchestrator.review_attempt(
    ATTEMPT_ID,
    approved=False,
    dominant_mismatch=(
        "Thumb placement and collision are repaired with zero Thumb-Keycap overlap and unchanged Palm-Thumb attachment, "
        "but the middle/ring/little shells still present upright end caps and an uneven staircase unlike the layered "
        "horizontal curl in the reference."
    ),
    next_edit=(
        "Keep Palm, Forearm, Index, Thumb, button, camera and actions byte-stable; rigidly reorient only each connected "
        "Middle/Ring/Little shell plus its three joint meshes around its verified palm pivot, then apply one shared "
        "camera-space translation and require palm connectivity with zero inter-finger intersections."
    ),
    checklist=[
        "Middle, ring, and little hero silhouettes read as thick horizontal stepped shells rather than vertical tips.",
        "Combined MRL centroid is within 16 px of the locked reference target and maintains right-edge crop.",
        "Palm-Middle/Ring/Little overlap remains at least 50 pairs each.",
        "Middle-Ring, Ring-Little, Middle-Little, and Index-MRL overlap pairs remain zero.",
        "Palm, Forearm, Index, Thumb, contact, topology, matrices, materials, camera, button, and actions remain unchanged.",
    ],
)
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
