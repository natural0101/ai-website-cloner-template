---
name: product-design-taste
description: "Use when designing from scratch or improving product UI taste for dashboards, admin panels, SaaS apps, AI design studios, canvas editors, data tools, workbenches, command surfaces, inspectors, tables/lists/forms, proposal/review flows, or any frontend product surface where the design must balance workflow clarity, density, states, accessibility, and visual craft without landing-page bias."
---

# Product Design Taste

Use this skill when the task is about making a real product interface feel excellent, not merely decorative. Pair it with `product-ui-design-orchestrator` for routing, then use this skill to make taste decisions.

## Required Reading

Always read:

```text
docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
references/product-design-taste-playbook.md
```

Also read `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md`, `docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md`, `docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md`, and `.codex/skills/design-ai-workbench-screens/SKILL.md` for AI design studios, canvas editors, proposal/diff flows, or ForgeStudio-like apps. Read `docs/design-workbench/FORGESTUDIO_CONTEXT.md` when the target resembles ForgeStudio or external-agent design tooling.

## External Packet Discipline

When working in a target repository that has a `.design-agent/` packet, read `.design-agent/working-brief.md` before making taste decisions, then verify it from the knowledge-base repository with `npm run design:brief-check -- "<target-project>"`. Before final handoff, use `.design-agent/final-report-template.md`, run `npm run design:final-check -- "<target-project>"`, and refresh the readiness report with `npm run design:target-audit -- "<target-project>" --write`.

## Workflow

1. Classify the product surface: `dashboard`, `admin`, `SaaS-app`, `AI-design-studio`, `canvas-editor`, `data-tool`, `settings`, `workflow-app`, `website-hybrid`, or `landing`.
2. Follow `UNIVERSAL_DESIGN_RUNBOOK.md` so taste decisions come after project read, product model, workflow, IA, screen/interaction/state/copy/decision inventory, and design-system baseline.
3. Fill the Universal Product Design Brief and pick the closest Product Surface Blueprint.
4. Map information architecture, choose the screen recipe, define interaction transitions, define copy/status language, shape decision/review surfaces, choose component blueprints, and define key component state specs.
5. For dashboard, admin, records, operations, or data-tool surfaces, apply `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` before visual styling.
6. For AI design studios or canvas workbenches, use `AI_DESIGN_APP_TRUSTED_VERTICAL.md` to name the trusted vertical segment, source-of-truth objects, false-state risks, proof/evidence surfaces, decision question, after-state, and recovery path before visual styling.
7. State the product read in one sentence: user, job, core loop, density, risk, and tone.
8. Set taste dials before styling:
   - Workflow density: `low`, `medium`, or `high`.
   - Visual character: `neutral`, `editorial`, `technical`, `premium`, `playful`, or `brand-led`.
   - Motion intensity: `none`, `control feedback`, `workflow continuity`, or `expressive`.
   - Auditability: `light`, `visible`, or `strict`.
9. Design the work loop first: route map, navigation, current object, primary action, review/recovery path, and next step.
10. Design the interaction/state/copy model before color: enabled, pending, success, error, disabled, selected, warning, conflict, retry, undo, rollback, reopen, with factual labels from `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
11. Design the decision/review cockpit with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for approvals, proposal review, triage, comparison, evidence/risk, and audit/recovery.
12. Fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` so the taste work maps to a coherent route/screen/workflow with object, data/fixture truth, states, actions, responsive behavior, and evidence.
13. Choose component primitives that match the surface. Prefer tables/lists/trees/inspectors/toolbars for repeated work; use cards only for discrete objects or grouped decisions.
14. Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` to define anatomy, states, and behavior before visual styling.
15. Use `product-ui-component-sourcing` before adding external component sources or dependencies.
16. Apply visual craft after the workflow is legible: spacing rhythm, typography scale, contrast, icon system, status color, motion, and responsive behavior.
17. Run `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: five-second test, primary object/state/next action, weakest visual category, mediocrity risks, and product-specific details.
18. Verify against `PRODUCT_UI_QUALITY_GATE.md` before calling the work done.

## Product Taste Rules

- Do not turn dashboards, editors, or workbenches into landing pages. No hero-first composition unless the surface is actually marketing.
- Treat density as design. Dense UI is good when grouped, aligned, scannable, and stateful.
- Make selection, focus, pending work, and recovery more visible than decoration.
- Use restrained accent color for action and status. Do not use generic AI-purple glow by default.
- Keep panels stable. Avoid floating-card sprawl in operational screens.
- Make data honest. Label sample/demo data and never fake metrics, screenshots, imported assets, agent status, proof, or completed work.
- Replace vague "done/success/ready" copy with specific object, reason, next action, and evidence/sample labels.
- Make decision surfaces help the user choose: question, options/comparison, evidence, risk, action, after-state, and recovery.
- Motion must explain continuity, hierarchy, or feedback. Remove motion that competes with reading, selection, editing, or review.
- Desktop is primary for serious tools. Tablet/mobile should degrade intentionally into review, navigation, or focused edit flows.

## Output Contract

When planning or auditing, produce:

- Product read:
- Runbook phase coverage:
- Brief/blueprint:
- Rubric target:
- Top-design benchmark:
- Surface and workflow:
- Operational pattern:
- Trusted vertical segment:
- AI workbench implementation slice:
- Taste dials:
- Information architecture:
- Interaction model:
- Copy/status language:
- Decision/review cockpit:
- Screen recipe/state specs:
- Implementation slice contract:
- State model:
- Component choices:
- Component blueprints:
- Visual system:
- Motion policy:
- Accessibility and responsive checks:
- Risks and verification/evidence plan:

When implementing, improve the smallest coherent surface first, run the target project's checks/screenshots where possible, and report what was verified.
