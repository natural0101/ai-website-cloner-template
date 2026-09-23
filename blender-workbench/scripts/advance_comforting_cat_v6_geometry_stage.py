"""Record the five geometry attempts and advance the staged state to MATERIAL."""

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
        "attempt43_face_relief",
        "Integrate eye, pupil, highlight, muzzle, nose, mouth and whiskers into a shallow face relief.",
        ["mesh", "curve"],
        True,
        "Face relief improved; cloth remains primitive-like.",
        "Reblock garment cloth silhouette.",
        "comforting_cat_v6_face_relief_integration_attempt43",
    ),
    (
        "attempt44_garment_reblock",
        "Reprofile robe, tunic, scarf and arms as an asymmetric cloth stack.",
        ["mesh"],
        False,
        "Numeric gates passed but tunic became a board, drape a shield and hem corners too sharp.",
        "Retain arm/topology gains and remediate the cloth contour.",
        "comforting_cat_v6_garment_cloth_reblock_attempt44",
    ),
    (
        "attempt45_cloth_remediation",
        "Reduce the A44 tunic and drape, seat scarf contacts and soften the hem.",
        ["mesh"],
        True,
        "Cloth stack improved; side tail still reads as a third leg.",
        "Lay the tail into a low grounded plume.",
        "comforting_cat_v6_cloth_contour_remediation_attempt45",
    ),
    (
        "attempt46_grounded_plume",
        "Lower the tail while preserving its front X span and embedded tip.",
        ["mesh"],
        False,
        "Front improved but the side camera still exposed a vertical drop.",
        "Increase Y sweep while preserving the low distal Z.",
        "comforting_cat_v6_tail_grounded_plume_attempt46",
    ),
    (
        "attempt47_tail_side_sweep",
        "Sweep the low plume backward in Y so its side projection becomes horizontal.",
        ["mesh"],
        True,
        "Best geometry checkpoint of cycle; material plasticity is now the dominant mismatch.",
        "Move to isolated MATERIAL lookdev without vertex changes.",
        "comforting_cat_v6_tail_side_sweep_remediation_attempt47",
    ),
]

for attempt_id, action, scope, approved, mismatch, next_edit, asset in attempts:
    render_dir = WORKBENCH / "artifacts" / "renders"
    report_dir = WORKBENCH / "artifacts" / "reports"
    orchestrator.record_attempt(
        attempt_id,
        action,
        scope,
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
            "Visual likeness gate is still not final.",
            "Preserve reversible sources and four-view evidence.",
            "Do not use material or light to conceal a silhouette regression.",
        ],
    )

best_checkpoint = (
    WORKBENCH
    / "artifacts"
    / "blend"
    / "comforting_cat_v6_tail_side_sweep_remediation_attempt47.blend"
).resolve()
orchestrator.approve_stage("attempt47_tail_side_sweep", str(best_checkpoint))
orchestrator.state.unresolved = [
    "Fur, eyes and cloth still read as smooth plastic rather than soft painterly surfaces.",
    "Ear wedge and lower hem geometry require a later bounded geometry cycle if material lookdev cannot close the likeness gap.",
]
orchestrator.save(STATE_PATH)
print(orchestrator.memory_window())
