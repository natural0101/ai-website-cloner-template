---
name: blender-staged-production
description: Use for complex Blender assets, reference reconstruction, multi-part figures, unusual lookdev, or after one failed attempt. Do not load for trivial text/color/export tasks.
license: MIT
---

# Blender staged production

1. Run read-only scene inspection and `capability_probe.probe()`.
2. Write a scene graph using `03_schemas/scene_graph.schema.json`.
3. Choose target mode: `FRONT_2_5D`, `TRUE_360`, `HYBRID_HERO`, or `FREEFORM`.
4. Retrieve 3–5 relevant verified examples; ignore examples with incompatible representation/version.
5. Initialize `StageOrchestrator` with memory limit 5.
6. Execute stages in order. Enforce `STAGE_PERMISSIONS_RU.md`.
7. One attempt changes one dominant defect.
8. After each attempt render front, 3/4 and side; add back/top when true 360 matters.
9. Critic returns an explicit checklist and `do_not_change` list.
10. Approve stage only with a checkpoint path and stage-specific evidence.
11. Run `scene_qa.audit_scene()` before leaving geometry and before export.
12. On API mismatch or transport timeout, classify the error; do not blindly rerun non-idempotent code.
13. On budget exhaustion choose the best checkpoint or ask for a single A/B verdict.
14. Export only after visual, structural and budget validation.
