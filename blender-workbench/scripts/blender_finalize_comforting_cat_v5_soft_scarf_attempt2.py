"""Finalize export and structural QA after the soft scarf render pass."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import bpy


ASSET = "comforting_cat_v5_soft_scarf_attempt2"
WORKBENCH = Path(
    r"C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template\blender-workbench"
).resolve()
BLEND_PATH = (WORKBENCH / "artifacts" / "blend" / f"{ASSET}.blend").resolve()
GLB_PATH = (WORKBENCH / "artifacts" / "exports" / f"{ASSET}.glb").resolve()
REPORT_DIR = (WORKBENCH / "artifacts" / "reports").resolve()
SCENE_QA_PATH = (
    WORKBENCH / "research-feedback-upgrade" / "04_blender" / "scene_qa.py"
).resolve()

if Path(bpy.data.filepath).resolve() != BLEND_PATH:
    raise RuntimeError(f"Expected already-open {BLEND_PATH}; got {bpy.data.filepath}")


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


root = bpy.data.objects["Cat_Root"]
export_objects = descendants(root)
bpy.ops.object.select_all(action="DESELECT")
for obj in export_objects:
    obj.hide_set(False)
    obj.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=False,
    export_yup=True,
    export_animations=False,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
)

qa_namespace = runpy.run_path(str(SCENE_QA_PATH))
structural_qa = qa_namespace["audit_scene"](
    object_names=[obj.name for obj in export_objects if obj.type == "MESH"],
    contact_tolerance=0.004,
    floating_tolerance=0.03,
)
errors = list(structural_qa["errors"])
warnings = list(structural_qa["warnings"])
if not GLB_PATH.exists() or GLB_PATH.stat().st_size == 0:
    errors.append("GLB export missing or empty")

report = {
    "asset": ASSET,
    "stage": "EXPORT_QA",
    "attempt": 2,
    "target_mode": "TRUE_360",
    "source_blend": str(BLEND_PATH),
    "checkpoint": str(
        WORKBENCH
        / "artifacts"
        / "blend"
        / "checkpoints"
        / "comforting_cat_v5_before_soft_scarf_attempt2.blend"
    ),
    "dominant_defect": "mechanical_stacked_scarf_plates",
    "accepted_intermediate_predecessor": "comforting_cat_v5_head_silhouette_attempt1",
    "preserved_hidden_source": "Cat_ScarfUpperFold",
    "outputs": {
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "glb_bytes": GLB_PATH.stat().st_size if GLB_PATH.exists() else 0,
        "front": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_02_material_front.png"
        ),
        "three_quarter": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_03_front_3q.png"
        ),
        "side": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_04_side.png"
        ),
        "back": str(
            WORKBENCH / "artifacts" / "renders" / f"{ASSET}_05_back.png"
        ),
    },
    "validation": {
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    },
    "visual_verdict": "accepted_intermediate_only",
}
(REPORT_DIR / f"{ASSET}_structural_qa.json").write_text(
    json.dumps(structural_qa, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
(REPORT_DIR / f"{ASSET}_scene_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
bpy.context.scene["comforting_cat_v5_stage"] = "EXPORT_QA"
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
print("COMFORTING_CAT_V5_SOFT_SCARF_FINALIZE=" + json.dumps(report, ensure_ascii=False))
