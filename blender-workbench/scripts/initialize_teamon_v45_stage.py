from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
MODULE_PATH = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
STATE_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v45_stage_state.json"
SOURCE_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v44_surface_smoothed.blend"
SCENE_GRAPH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v45_scene_graph.json"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]

orchestrator = StageOrchestrator.create(
    "teamon-reference-v45-pose-repair",
    "Repair the visibly crooked TEAMON robot-hand pose against the durable reference while preserving the fixed index contact, button, camera, materials, and synchronized click animation.",
    memory_limit=5,
)
orchestrator.record_attempt(
    "v45-intake",
    "Reject v44 as a visual pose match, preserve it as rollback, and lock measurable reference landmarks plus the unchanged web interaction contract.",
    ["spec", "reference", "acceptance"],
    render_paths=[str(PROJECT_ROOT / "output" / "playwright" / "teamon-v44" / "teamon-v44-browser-rest.png")],
    audit_path=str(SCENE_GRAPH),
)
orchestrator.review_attempt(
    "v45-intake",
    approved=True,
    checklist=[
        "Index contact remains within 8 px of the reference and within 0.002 world units of the keycap.",
        "Middle, ring, and little reconnect to the palm and form an inward-curled upper cluster.",
        "Palm/wrist mass rotates upward around the fixed contact instead of entering from bottom-right.",
        "Thumb retracts to the lower-right reference region.",
        "Button, camera, materials, lighting, text, action names, timing, and press travel remain unchanged.",
        "v44 blend, GLB, component backup, and evidence remain immutable rollback assets."
    ],
)
orchestrator.approve_stage("v45-intake", str(SOURCE_BLEND))
orchestrator.record_attempt(
    "v45-initialization",
    "Verify Blender 5.1.1 capabilities, source hierarchy, flat hand parenting, durable reference, scene graph, action contract, and current structural gaps.",
    ["units", "collections", "names", "camera_scaffold", "reference_plane"],
    audit_path=str(SCENE_GRAPH),
)
orchestrator.review_attempt("v45-initialization", approved=True, checklist=[])
orchestrator.approve_stage("v45-initialization", str(SOURCE_BLEND))
orchestrator.save(STATE_PATH)
print(STATE_PATH)
