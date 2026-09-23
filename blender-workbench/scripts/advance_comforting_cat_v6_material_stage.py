"""Record A48/A49, approve the restrained material checkpoint, and advance."""

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

StageOrchestrator = runpy.run_path(str(MODULE_PATH))["StageOrchestrator"]
orchestrator = StageOrchestrator.load(STATE_PATH, memory_limit=5)

attempts = [
    (
        "attempt48_soft_painterly_materials",
        "Replace saturated plastic colors with a muted ochre, slate-blue and brown palette.",
        True,
        "Palette moved toward the reference but broad material noise looked cloudy.",
        "Restrain color variation and micro-bump without touching geometry.",
        "comforting_cat_v6_soft_painterly_materials_attempt48",
    ),
    (
        "attempt49_variation_restraint",
        "Narrow the painterly palettes and reduce material variation strength and bump.",
        True,
        "Best material checkpoint; remaining mismatch is structural head, ear, body and tail geometry.",
        "Start a new bounded geometry revision cycle from A49.",
        "comforting_cat_v6_material_variation_restraint_attempt49",
    ),
]

for attempt_id, action, approved, mismatch, next_edit, asset in attempts:
    render_dir = WORKBENCH / "artifacts" / "renders"
    report_dir = WORKBENCH / "artifacts" / "reports"
    orchestrator.record_attempt(
        attempt_id,
        action,
        ["materials", "shader_nodes"],
        render_paths=[
            str(render_dir / f"{asset}_02_material_front.png"),
            str(render_dir / f"{asset}_03_front_3q.png"),
            str(render_dir / f"{asset}_04_side.png"),
            str(render_dir / f"{asset}_05_back.png"),
        ],
        audit_path=str(report_dir / f"{asset}_structural_qa.json"),
    )
    orchestrator.review_attempt(
        attempt_id,
        approved=approved,
        dominant_mismatch=mismatch,
        next_edit=next_edit,
        checklist=[
            "Geometry hash and object bounds must remain unchanged during MATERIAL.",
            "A49 is a material checkpoint, not a final likeness approval.",
            "Structural mismatch must be handled in a new bounded geometry cycle.",
        ],
    )

best_checkpoint = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v6_material_variation_restraint_attempt49.blend"
).resolve()
orchestrator.approve_stage("attempt49_variation_restraint", str(best_checkpoint))
orchestrator.state.unresolved = [
    "Head silhouette is too wide and mask-like; cheek depth has visible horizontal bands.",
    "Ears are too tall, narrow and sharp compared with the reference.",
    "Body and tunic remain too cylindrical and flat; tail is still a heavy tube.",
]
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
