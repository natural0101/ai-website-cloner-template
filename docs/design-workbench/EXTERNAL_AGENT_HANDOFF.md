# External Agent Handoff

Use this file when another agent works in a different repository but must use this design knowledge base.

Knowledge base path:

```text
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template
```

## Best Handoff Command

From the knowledge-base repository, generate a target-local packet:

```bash
npm run design:pack -- "<TARGET_PROJECT_PATH>"
```

This writes `DESIGN_AGENT_HANDOFF.md` and `.design-agent/` into the target project. The packet contains `prompt.txt`, `working-brief.md`, `manifest.json`, `acceptance-checklist.md`, `final-report-template.md`, and `AGENTS_SNIPPET.md` so the receiving agent has the route, source docs, skills, non-negotiables, working brief, final QA checklist, and target-agent rule snippet inside its own repository.

Install a managed `AGENTS.md` block in the target project when future agents should auto-discover the packet:

```bash
npm run design:install-agent-rules -- "<TARGET_PROJECT_PATH>"
```

Then verify the packet:

```bash
npm run design:packet-check -- "<TARGET_PROJECT_PATH>"
```

After the receiving agent fills the working brief and before coding:

```bash
npm run design:brief-check -- "<TARGET_PROJECT_PATH>"
```

`design:brief-check` is a substance gate, not only a placeholder check. The working brief must name the user/job/object, product object model, visual system contract, workflow/action path, data/source truth, verification evidence, route/screen, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, and top-design target. Generic answers like `improve UI`, `make better`, `use app`, `done`, or `N/A` for core product fields are not ready for coding.

Before final handoff:

```bash
npm run design:final-check -- "<TARGET_PROJECT_PATH>"
```

To get a one-page readiness report:

```bash
npm run design:target-audit -- "<TARGET_PROJECT_PATH>" --write
```

## Handoff Prompt

Copy this to the agent working in the target project:

```text
Use the design knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

The active project is:
<TARGET_PROJECT_PATH>

Do not modify the knowledge-base repository unless explicitly asked. Work only in the active project.

Read these first:
- docs/design-workbench/AGENT_START_HERE.md
- docs/design-workbench/FORGESTUDIO_CONTEXT.md
- docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md if this is an AI design app, canvas editor, proposal/diff workflow, or ForgeStudio-like workbench.
- docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
- docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
- docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
- docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
- docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md if this is a dashboard, admin panel, records UI, data tool, or operations surface.
- docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
- docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
- docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
- docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
- docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
- docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md if this is an AI design app, canvas editor, proposal/diff workflow, or ForgeStudio-like workbench.
- docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md if this is an AI design app, canvas editor, proposal/diff workflow, or ForgeStudio-like workbench.
- docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
- docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
- docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
- docs/design-workbench/COMPONENT_STATE_SPEC.md
- docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
- docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
- docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
- docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
- docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
- docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
- docs/design-workbench/AGENT_REPORT_EXAMPLES.md
- .codex/skills/product-ui-design-orchestrator/SKILL.md
- .codex/skills/product-design-taste/SKILL.md
- .codex/skills/product-ui-component-sourcing/SKILL.md
- .codex/skills/product-ui-visual-qa/SKILL.md
- .codex/skills/design-ai-workbench-screens/SKILL.md if this is an AI design app, canvas editor, or ForgeStudio-like workbench.

Classify the surface before designing: dashboard, admin, editor, canvas-workbench, SaaS app, AI design studio, website, landing, 3D/WebGL, or hybrid. Follow the Universal Design Runbook, fill the Universal Product Design Brief, name the product object model, define the visual system contract, choose the closest Product Surface Blueprint, map information architecture, choose a Product UI Screen Recipe, define interaction transitions, define copy/status language, shape decision/review cockpits, fill the Implementation Slice Contract, choose component blueprints, name local files to inspect/change, and name key Component State Specs before changing UI.

Do not force landing-page structure onto product UI. Improve workflow clarity, decision/review support, information hierarchy, state/copy coverage, accessibility, responsive behavior, component sourcing, proof/data honesty, and visual QA before decorative polish.

For final handoff, report real changed files, commands, and screenshots/browser checks. If visual verification cannot run, say why and mark the remaining risk. Use target-relative paths in `Files changed`; missing paths, directories, or paths outside the target project block final handoff readiness. `Browser routes checked` must include the route paths named in the working brief. `State coverage checked` must cover the brief's `Included states`, except states explicitly deferred. `Component state evidence checked` must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence; generic `checked`, `done`, or component-only wording is not enough. `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` must reference the working brief's primary object, product object model, visual system contract, workflow/actions, and data/fixture truth; generic `done/improved` or component-only wording is not a coherent slice. `Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic `checked`, `done`, or `looks good` wording is not enough. `Top-design benchmark checked` and `Five-second test` cannot be generic `passed/checked/improved` text: the final report must name object, state, next action, recovery, and evidence, and must tie `Mediocrity risks fixed` plus `Product-specific details` back to the working brief. `Rubric score` must be numeric on the /30 scale: `PASS` requires 26+/30, `PASS WITH RISKS` requires 18+/30 or higher, and 0/blocking categories must be fixed or reported as blockers. Use explicit evidence statuses: `Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK` and `Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK`. Packet-only checks, planned screenshots, and "not applicable" are not final visual evidence. When using `REAL_PROJECT_COMMANDS`, list non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` command-log artifacts in the target project. When using `REAL_BROWSER_SCREENSHOTS` or `USER_SCREENSHOTS`, list non-empty screenshot/artifact files that exist in the target project and are valid PNG/JPEG/WebP/GIF/MP4/WebM files. When using `MANUAL_BROWSER_INSPECTION`, list a non-empty `.md`, `.txt`, `.html`, or valid `.json` notes artifact in the target project that names the route/screen, viewport or pixel size, and visual/layout/focus/overlap check.
`Information architecture checked` must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior; generic `checked`, `done`, or component-only wording is not enough.
`Interaction model checked` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control; generic `checked`, `done`, or static component wording is not enough.
`Copy/status language checked` must name status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label; generic `checked`, `done`, `success`, or `ready` wording is not enough.
`Decision/review cockpit checked` must name decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path; generic `checked`, `done`, or component-only wording is not enough.
`Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic `checked`, `done`, or `looks good` wording is not enough.
```

## Agent Route

1. Inspect the target project before changing anything: stack, existing components, routes, app shell, package scripts, design tokens, and current UI conventions.
2. Follow `UNIVERSAL_DESIGN_RUNBOOK.md` as the operating order from project read to final QA.
3. Classify the surface and state the product read in one sentence: user, job, core loop, density, risk, and tone.
4. Fill `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, name the product object model, define the visual system contract, and choose the closest `PRODUCT_SURFACE_BLUEPRINTS.md` pattern.
5. Map the IA with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, choose a screen recipe from `PRODUCT_UI_SCREEN_RECIPES.md`, define actions/transitions with `PRODUCT_UI_INTERACTION_MODEL.md`, define labels and messages with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, shape decisions with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, choose component blueprints from `PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, name local files to inspect/change, and define key component states with `COMPONENT_STATE_SPEC.md`.
6. Choose the smallest relevant skill route:
   - General product UI: `product-ui-design-orchestrator`.
   - Dashboard/admin/data tool: `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` plus `product-design-taste`.
   - Information architecture/navigation: `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
   - Interaction transitions/actions: `PRODUCT_UI_INTERACTION_MODEL.md`.
   - Copy/status language: `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
   - Decision/review/approval surfaces: `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
   - Product taste/new UI: `product-design-taste`.
   - AI design studio/canvas workbench screens, trusted vertical, state transitions, and buildable slices: `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, `design-ai-workbench-screens`, `AI_WORKBENCH_INTERACTION_FLOWS.md`, and `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`.
   - Component anatomy and state contracts: `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` plus `COMPONENT_STATE_SPEC.md`.
   - Component/library choices: `product-ui-component-sourcing`.
   - Final visual QA: `product-ui-visual-qa` plus `ui-audit`.
   - Landing/marketing-only surfaces: landing workflow skills.
7. Fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, then improve the smallest coherent surface first. If the target is not an AI design app, mark the trusted-vertical fields in `.design-agent/working-brief.md` as `N/A - not an AI design app`; do not leave them blank.
8. Run `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: five-second test, primary object/state/next action, weakest visual category, mediocrity risks fixed, and product-specific details. In the final report, write the actual object, state, next action, recovery, and evidence; do not write only `passed`, `checked`, or `looks good`.
9. Score the changed surface with `PRODUCT_UI_REVIEW_RUBRIC.md`; fix all 0 categories before final handoff.
10. Verify with the target project's real checks and screenshots/browser inspection using `VISUAL_QA_EVIDENCE_PLAYBOOK.md`.
11. Shape the final report with `AGENT_REPORT_EXAMPLES.md`; replace every sample route, changed-file path, command, and screenshot path with real evidence.
12. Use target-relative paths in `Files changed`; `design:target-audit` verifies that they exist inside the target project.
13. Keep `Browser routes checked` aligned with the brief route fields; do not replace the changed route with a different checked route.
14. Keep `Information architecture checked` aligned with the brief's route/screen, navigation, zones, responsive behavior, and recovery path.
15. Keep `Interaction model checked` aligned with the brief's actions and transitions: name action, pending/success/failure state, recovery/permission, and affected object/control.
16. Keep `Copy/status language checked` aligned with the brief's copy/status contract: name affected object, state/status, reason or next action, and evidence/source/sample label.
17. Keep `Decision/review cockpit checked` aligned with the brief's decision/review cockpit: name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path.
18. Keep `Visual system checked` aligned with the brief's visual system contract: name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
19. Keep `State coverage checked` aligned with the brief's `Included states`; only omit explicitly deferred states.
20. Keep `Component state evidence checked` aligned with changed components/controls: name the controls, states, and screenshot/browser/manual/keyboard/responsive evidence used.
21. Keep `Rubric score` numeric and aligned with verdict thresholds from `PRODUCT_UI_REVIEW_RUBRIC.md`.

## ForgeStudio-Like Product Spine

For ForgeStudio-like applications, the UI must expose this loop:

```text
open project -> design search -> import -> inspect -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/reopen
```

Do not collapse this into a chat page. Chat can assist, but the product is the workspace: canvas, project map, layers/assets, inspector, comments/tasks, proposals, preview/diff, verification, ledger/history, export, and connection states.

Start ForgeStudio-like work with `AI_DESIGN_APP_TRUSTED_VERTICAL.md`. It turns the source read into a product-slice contract: source-of-truth objects, false-state bans, transaction-only mutation, proof/evidence surfaces, and slice QA.

Also apply `AI_WORKBENCH_INTERACTION_FLOWS.md`: external AI is proposal-only until preview/diff, verification, human approval, a `DesignTransaction`, and ledger/history evidence exist. For ForgeStudio-like products, also show agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.

Use `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` to choose the smallest coherent slice: launcher/import, workspace selection, comment-to-proposal, proposal review, or ledger/export.

When a `.design-agent/working-brief.md` packet exists, fill `AI Design App Invariants` before coding. For ForgeStudio-like surfaces, `N/A` is not accepted there: name where proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery appear. `design:brief-check` enforces this.

## Non-Negotiables

- No marketing hero inside dashboards, editors, admin panels, or workbenches unless the surface is actually marketing.
- No fake metrics, fake users, fake screenshots, fake imported assets, fake proof, or fake agent status.
- No bulk component/catalog installs.
- No external component without a named product job and local-component check.
- No final "done" without state coverage and visual/browser evidence, or an explicit remaining-risk note.
- No final report with generic information architecture evidence; route/screen map, navigation/app shell, zones, and responsive/recovery behavior must be named.
- No final report with generic interaction evidence; actions, transitions, pending-success-failure, recovery/permission, and affected object/control must be named.
- No final report with generic copy/status evidence; affected object, state/status, reason or next action, and evidence/source/sample label must be named.
- No final report with generic decision/review evidence; decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path must be named.
- No final report with generic visual-system evidence; typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components must be named.
- No isolated decorative fragment passed off as a product slice; route/screen, object, data/fixture truth, states, actions, and evidence must line up.
- No coding from a packet brief that lacks product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
- No final report with generic component-state evidence; changed components/controls must name states and evidence.
- No "AI fixed it" without proposal, preview/diff, approval, closed task/comment, and ledger/history evidence.
- No AI design app final handoff unless `Operational pattern checked` reports proposal-only, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.
- No vague "success", "ready", or "done" as the only feedback for important work; status copy must name object, reason, next action, and evidence/sample label where relevant.
- No approval/review surface without visible decision question, options/comparison, evidence, risk, after-state, and audit/recovery path.

## Final Report Contract

The agent's final report should include:

```text
Surface classified:
Product read:
Object model checked:
Visual system checked:
Runbook phases used:
Brief/blueprint used:
Screen recipe/state specs:
Rubric score:
Top-design benchmark:
Workflow improved:
Information architecture checked:
Interaction model checked:
Copy/status language checked:
Decision/review cockpit checked:
Operational pattern checked:
Files changed:
Component/source choices:
Component blueprints checked:
State coverage checked:
Component state evidence checked:
Interaction flows checked:
Implementation slice checked:
Implementation slice contract:
Accessibility checked:
Responsive checked:
Motion/proof/data risks handled:
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

Use `PASS`, `PASS WITH RISKS`, or `FAIL` for the verdict.
`npm run design:target-audit -- "<TARGET_PROJECT_PATH>" --write` reports `READY FOR FINAL HANDOFF` only when the final report has route checks that match the working brief, visual-system evidence that names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components, information architecture evidence that names route/screen map, navigation/app shell, zones, and responsive/recovery behavior, interaction evidence that names actions/transitions, pending-success-failure, recovery/permission, and affected object/control, state coverage that matches included/deferred states, component-state evidence that names components/controls, states, and evidence, implementation-slice fields that reference the brief primary object/workflow/actions/data truth, substantive top-design fields that name object/state/action/recovery/evidence and reference the brief risks/details, a numeric rubric score that meets the verdict threshold, real changed-file paths, real project command evidence, and real browser/user/manual visual evidence; changed files must exist inside the target project, for command evidence, log artifacts must exist in the target project, for screenshot-based evidence, artifact files must exist in the target project and pass visual-file signature checks, and for manual inspection a notes artifact must exist and name route/screen, viewport/size, and visual check. Otherwise it stays at `READY FOR CODING, NOT READY FOR FINAL HANDOFF`.
