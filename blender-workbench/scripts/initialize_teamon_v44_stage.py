from __future__ import annotations

import os
from pathlib import Path
import runpy


PROJECT_ROOT = Path(os.environ["TEAMON_PROJECT_ROOT"]).resolve()
MODULE_PATH = PROJECT_ROOT / "blender-workbench" / "research-feedback-upgrade" / "04_python" / "stage_orchestrator.py"
STATE_PATH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_stage_state.json"
SOURCE_BLEND = PROJECT_ROOT / "blender-workbench" / "artifacts" / "blend" / "teamon_reference_v39_ada_rigged.blend"
SCENE_GRAPH = PROJECT_ROOT / "blender-workbench" / "artifacts" / "reports" / "teamon_reference_v44_scene_graph.json"

module = runpy.run_path(str(MODULE_PATH))
StageOrchestrator = module["StageOrchestrator"]

orchestrator = StageOrchestrator.create(
    "teamon-reference-v44-surface-polish",
    "Carefully fair the internal surfaces of the restored v39 palm, thumb, and index and soften white-plastic highlights while preserving pose, protected silhouette, contact, animation, camera, lighting, and button.",
    memory_limit=5,
)
orchestrator.record_attempt(
    "v44-intake",
    "Lock v39 as the immutable source and define the protected three-mesh fairing plus three-socket material scope.",
    ["spec", "reference", "acceptance"],
)
orchestrator.review_attempt(
    "v44-intake",
    approved=True,
    checklist=[
        "Do not replace, reposition, rescale, or re-pose any hand object.",
        "Fair only internal vertices of Palm, Thumb, and Index while locking camera silhouette, world extrema, contact, and palm junctions.",
        "Do not alter topology, object transforms, actions, camera, lighting, button, or interaction contract.",
        "Change only Roughness, Coat Weight, and Coat Roughness on TEAMON_Robot_White_Ada.",
        "Keep the immutable v39 blend and GLB as rollback assets.",
    ],
)
orchestrator.approve_stage("v44-intake", str(SOURCE_BLEND))
orchestrator.record_attempt(
    "v44-initialization",
    "Verify the v39 hierarchy, names, units, action contract, locked camera, and material scope.",
    ["units", "collections", "names", "camera_scaffold", "reference_plane"],
    audit_path=str(SCENE_GRAPH),
)
orchestrator.review_attempt("v44-initialization", approved=True, checklist=[])
orchestrator.approve_stage("v44-initialization", str(SOURCE_BLEND))
orchestrator.save(STATE_PATH)
print(STATE_PATH)
