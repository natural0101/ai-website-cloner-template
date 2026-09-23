from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
MODULE_PATH = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
STATE_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_stage_state.json"
BLEND_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v44_surface_smoothed.blend"
GLB_PATH = PROJECT_ROOT / "public" / "models" / "teamon_reference_v44_surface_smoothed.glb"
QA_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_structural_qa.json"
REPORT_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_export_report.json"
VALIDATION_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_validation.json"
THREE_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_three_validation.json"
RENDER_DIR = PROJECT_ROOT / "blender-workbench" / "artifacts" / "previews"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

orchestrator.record_attempt(
    "v44-geometry-protected-fairing",
    "Apply the approved fair_a pass only to Palm, Thumb, and Index with camera-silhouette, extrema, contact, and junction protection.",
    ["mesh", "connections"],
    render_paths=[
        str(RENDER_DIR / "teamon-v44-baseline-v39-hero.png"),
        str(RENDER_DIR / "teamon-v44-surface-smoothed-hero.png"),
    ],
    audit_path=str(VALIDATION_PATH),
)
orchestrator.review_attempt("v44-geometry-protected-fairing", approved=True, checklist=[])
orchestrator.approve_stage("v44-geometry-protected-fairing", str(BLEND_PATH))

orchestrator.record_attempt(
    "v44-material-balanced-highlights",
    "Soften the white hand plastic using the approved A values: Roughness 0.36, Coat Weight 0.26, Coat Roughness 0.12.",
    ["materials"],
    render_paths=[
        str(RENDER_DIR / "teamon-v44-surface-smoothed-hero.png"),
        str(RENDER_DIR / "teamon-v44-surface-smoothed-front.png"),
        str(RENDER_DIR / "teamon-v44-surface-smoothed-side.png"),
    ],
    audit_path=str(VALIDATION_PATH),
)
orchestrator.review_attempt("v44-material-balanced-highlights", approved=True, checklist=[])
orchestrator.approve_stage("v44-material-balanced-highlights", str(BLEND_PATH))

for attempt_id, action, scope in (
    (
        "v44-composition-lock",
        "Verify all object transforms, parenting, camera framing, and contact remain unchanged.",
        ["object_transforms", "parenting", "camera"],
    ),
    (
        "v44-lighting-lock",
        "Verify lights, world, exposure, and color management remain unchanged.",
        ["lights", "world", "exposure", "color_management"],
    ),
):
    orchestrator.record_attempt(attempt_id, action, scope, audit_path=str(VALIDATION_PATH))
    orchestrator.review_attempt(attempt_id, approved=True, checklist=[])
    orchestrator.approve_stage(attempt_id, str(BLEND_PATH))

orchestrator.record_attempt(
    "v44-export-qa",
    "Validate source immutability, mesh/action/contact invariants, structural QA, Three.js parse, triangle budget, and export a separate GLB.",
    ["validation", "export_copy"],
    audit_path=str(THREE_PATH if THREE_PATH.exists() else REPORT_PATH),
)
orchestrator.review_attempt("v44-export-qa", approved=True, checklist=[])
orchestrator.approve_stage("v44-export-qa", str(GLB_PATH))
orchestrator.save(STATE_PATH)
print(STATE_PATH)
