"""Initialize bounded staged-production state for the current cat reconstruction."""

from __future__ import annotations

import runpy
from pathlib import Path


WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
MODULE_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
).resolve()
STATE_PATH = (
    WORKBENCH / "artifacts" / "reports" / "comforting_cat_v6_stage_state.json"
).resolve()
SCENE_GRAPH = (
    WORKBENCH / "artifacts" / "reports" / "comforting_cat_v6_attempt42_scene_graph.json"
).resolve()
CHECKPOINT = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v6_integrated_cheek_microtufts_attempt42.blend"
).resolve()

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]

orchestrator = StageOrchestrator.create(
    "comforting_cat_v6",
    "Convincingly match the supplied comforting-cat reference in TRUE_360 while preserving reversible checkpoints, multiview evidence and structural QA.",
    memory_limit=5,
)
orchestrator.record_attempt(
    "attempt42_intake_baseline",
    "Register reference, TRUE_360 mode, acceptance gates and current scene graph.",
    ["spec", "reference", "acceptance"],
    audit_path=str(SCENE_GRAPH),
)
orchestrator.review_attempt(
    "attempt42_intake_baseline",
    approved=True,
    checklist=[
        "Front likeness gate overrides technical validity.",
        "Hidden depth remains an explicit TRUE_360 interpretation.",
    ],
)
orchestrator.approve_stage("attempt42_intake_baseline", str(CHECKPOINT))
orchestrator.record_attempt(
    "attempt42_initialization_baseline",
    "Approve existing units, stable semantic names, collections and orthographic camera scaffold.",
    ["units", "collections", "names", "camera_scaffold"],
    audit_path=str(
        WORKBENCH
        / "artifacts"
        / "reports"
        / "comforting_cat_v6_attempt42_capability_scene_probe.json"
    ),
)
orchestrator.review_attempt(
    "attempt42_initialization_baseline",
    approved=True,
    checklist=["Preserve CAT_RenderCamera and the four fixed review views."],
)
orchestrator.approve_stage("attempt42_initialization_baseline", str(CHECKPOINT))
orchestrator.state.unresolved = [
    "Face still reads as layered plastic rather than soft worried feline anatomy.",
    "Scarf and robe lack cloth asymmetry and folds.",
    "Ear and tail edges remain too smooth for the reference fur character.",
]
orchestrator.save(STATE_PATH)
print(STATE_PATH)
