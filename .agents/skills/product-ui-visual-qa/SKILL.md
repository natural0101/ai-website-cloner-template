---
name: product-ui-visual-qa
description: "Use when visually auditing, self-reviewing, or deciding whether a product UI change is done for dashboards, admin panels, SaaS apps, AI design studios, canvas editors, data tools, workbenches, app shells, inspectors, tables, proposal/diff flows, verification panels, ledgers, export screens, or any frontend product surface. Requires screenshot/browser checks, responsive/no-overlap review, interaction/state/copy coverage, accessibility basics, component sourcing validation, proof/data honesty, and a clear pass/fail report before final handoff."
---

# Product UI Visual QA

Use this skill after implementation or during final review. It prevents "looks fine" handoffs by forcing evidence from real commands, screenshots, browser checks, or an explicit unverified risk.

## Required Reading

Always read:

```text
docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
docs/design-workbench/AGENT_REPORT_EXAMPLES.md
references/visual-qa-checklist.md
```

For AI design studios or canvas editors, also read:

```text
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
.codex/skills/design-ai-workbench-screens/SKILL.md
```

For component/source risks, also read:

```text
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
.codex/skills/product-ui-component-sourcing/SKILL.md
```

## External Packet Discipline

When working in a target repository that has a `.design-agent/` packet, verify `.design-agent/working-brief.md` with `npm run design:brief-check -- "<target-project>"` before final QA. Use `.design-agent/final-report-template.md` for the report, run `npm run design:final-check -- "<target-project>"`, and refresh `.design-agent/readiness-report.md` with `npm run design:target-audit -- "<target-project>" --write` before calling the target ready.

## Workflow

1. Identify changed surfaces, routes, critical states, runbook phase coverage, brief fields, the chosen surface blueprint, information architecture, interaction model, copy/status language, decision/review cockpit, implementation slice contract, screen recipes, operational dashboard/admin/data-tool pattern when relevant, component blueprints, component state specs, and rubric categories.
2. Run available project checks: typecheck, lint, tests, build, or the project's equivalent.
3. Build an evidence matrix from `VISUAL_QA_EVIDENCE_PLAYBOOK.md`: routes, viewports, states, commands, and screenshots/browser checks.
4. Inspect real rendered UI at desktop, tablet, and mobile widths when possible.
5. Capture or review screenshots for changed surfaces. If screenshots are impossible, state why and mark visual verification incomplete.
6. Check P0 visual failures: overlap, clipping, unreadable text, broken spacing, hidden controls, blank canvases, missing assets, stuck loading, broken focus, fake data/proof.
7. Check product states and copy: empty, loading, error, disabled, selected, pending, success, retry/rollback, permission, disconnected, stale, sample/demo, with object/reason/next-action/evidence labels where relevant.
8. Check decision/review cockpit surfaces: decision question, options/comparison, evidence, risk, actions, after-state, and audit/recovery.
9. Check `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`: route/screen, primary object, data/fixture source, workflow, included/deferred states, responsive behavior, commands, screenshots/browser evidence, and risks line up with the shipped UI.
10. For AI workbench surfaces, check `AI_DESIGN_APP_TRUSTED_VERTICAL.md`: trusted vertical segment, source-of-truth objects, false-state bans, proof/evidence surfaces, decision question, after-state, recovery path, proposal-only AI, preview/diff, verification, approval, transaction, ledger, stale proposal, rollback/reopen, and honest mock labels. If a `.design-agent/` packet exists, verify that AI Design App Invariants are not `N/A` and name those same surfaces.
11. Check `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: five-second test, primary object/state/next action, weakest visual category, mediocrity risks fixed, and product-specific details.
12. Check accessibility basics: keyboard path, visible focus, labels, tooltip/accessibility names for icon buttons, contrast, reduced motion.
13. Check the final report's `Files changed` field: it must list target-relative paths that exist inside the target project.
14. Check the final report's `Browser routes checked` field: it must include the route paths named in `.design-agent/working-brief.md` when a packet exists.
15. Check the final report's `Visual system checked` field: it must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
16. Check the final report's `Information architecture checked` field: it must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior.
17. Check the final report's `Interaction model checked` field: it must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control.
18. Check the final report's `Copy/status language checked` field: it must name affected object, state/status, reason or next action, and evidence/source/sample label.
19. Check the final report's `Decision/review cockpit checked` field: it must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path.
20. Check the final report's `State coverage checked` field: it must cover the brief's `Included states`, except states explicitly listed in `Deferred states`.
21. Check the final report's `Component state evidence checked` field: it must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence.
22. Check the final report's `Rubric score` field: it must be numeric on the /30 scale, with `PASS` at 26+/30 and `PASS WITH RISKS` at 18+/30 or higher.
23. Check final report implementation-slice substance: `Product read`, `Workflow improved`, and `Implementation slice contract` must reference the working brief's route/screen, primary object, workflow/actions, data/source truth, and states.
24. Check final report top-design substance: `Five-second test` must name object, state, next action, recovery, and evidence; `Mediocrity risks fixed` and `Product-specific details` must reference the working brief, not generic `passed/checked/improved` wording.
25. For AI design apps, check final report operational substance: `Operational pattern checked` must name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.
26. Fix blockers when possible. Re-run the relevant checks after fixes.
27. Produce the done statement using `AGENT_REPORT_EXAMPLES.md` as the shape. Do not call the UI done if P0 visual checks, top-design benchmark, or screenshots/browser checks are missing without explanation.

## Hard Rules

- Do not trust static code review alone for visual UI work.
- Do not call a dashboard/editor/workbench done without checking responsive/no-overlap behavior.
- Do not ignore tiny floating fragments, cropped labels, misaligned icons, or broken hover/focus states.
- Do not leave fake metrics, fake screenshots, fake agent state, fake imported assets, or fake proof unlabelled.
- Do not call an AI workbench done if proposal, verification, approval, transaction, or ledger states are collapsed into one vague success state.
- Do not call an AI workbench done if `Operational pattern checked` is generic or omits proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, or export/reopen.
- Do not call a product UI done if the route/screen, object, workflow, data/source truth, states, and evidence do not form one coherent implementation slice.
- Do not call review/approval UI done if the decision question, comparison/options, evidence, risk, after-state, or audit/recovery path is missing.
- Do not hide failures behind "not tested" without a remaining-risk note.
- When reporting `Files changed`, list target-relative paths that exist inside the target project; missing files, directories, and paths outside the project block `design:target-audit` final handoff readiness.
- When reporting `Browser routes checked`, include the route paths from the working brief; checking a different route does not prove the changed route.
- When reporting `Visual system checked`, name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic `checked`, `done`, or `looks good` wording is not evidence.
- When reporting `Information architecture checked`, name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior; generic `checked`, `done`, or component-only wording is not evidence.
- When reporting `Interaction model checked`, name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control; generic `checked`, `done`, or static component wording is not evidence.
- When reporting `Copy/status language checked`, name affected object, state/status, reason or next action, and evidence/source/sample label; generic `checked`, `done`, `success`, or `ready` wording is not evidence.
- When reporting `Decision/review cockpit checked`, name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path; generic `checked`, `done`, or component-only wording is not evidence.
- When reporting `State coverage checked`, include the brief's included states and name any deferred states honestly.
- When reporting `Component state evidence checked`, name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence; generic `checked`, `done`, or component-only wording is not evidence.
- When reporting `Product read`, `Workflow improved`, and `Implementation slice contract`, reference the working brief's route/screen, primary object, workflow/actions, data/source truth, and states; generic `done/improved` or component-only wording is not evidence.
- When reporting `Rubric score`, use a numeric /30 score; `PASS` requires 26+/30, `PASS WITH RISKS` requires 18+/30 or higher, and 0/blocking categories must be fixed or reported as blockers.
- When reporting `Five-second test`, name object, state, next action, recovery, and evidence; `passed`, `checked`, `looks good`, or `improved` is not evidence.
- When reporting `Mediocrity risks fixed` and `Product-specific details`, reference the working brief's risk/detail fields so `design:target-audit` can prove the result is product-specific.
- When reporting `REAL_PROJECT_COMMANDS`, list non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` command-log artifacts in the target project so `design:target-audit` can verify them.
- When reporting `REAL_BROWSER_SCREENSHOTS` or `USER_SCREENSHOTS`, list non-empty screenshot/artifact files that exist in the target project and are valid PNG/JPEG/WebP/GIF/MP4/WebM files so `design:target-audit` can verify them.
- When reporting `MANUAL_BROWSER_INSPECTION`, list a non-empty `.md`, `.txt`, `.html`, or valid `.json` notes artifact in the target project so `design:target-audit` can verify the manual check.
- Manual inspection notes must name the checked route/screen, viewport or pixel size, and visual/layout/focus/overlap check.

## Output Contract

Finish with:

```text
Surface classified:
Runbook phase coverage checked:
Brief/blueprint checked:
Rubric score:
Top-design benchmark checked:
Five-second test:
Mediocrity risks fixed:
Product-specific details:
Files changed:
Visual system checked:
Trusted vertical checked:
Information architecture checked:
Interaction model checked:
Copy/status language checked:
Decision/review cockpit checked:
Screen recipe/state specs checked:
Operational pattern checked:
Interaction flows checked:
Implementation slice checked:
Implementation slice contract checked:
Component blueprints checked:
Routes/screens checked:
Viewports checked:
State coverage checked:
Component state evidence checked:
States checked:
Accessibility checked:
Component/data/proof risks checked:
Commands run:
Project command evidence:
Command evidence artifacts:
Screenshots/browser checks:
Visual evidence verdict:
Evidence artifacts:
Blockers fixed:
Remaining risks:
Verdict:
```
