# Agent Prompts

Use these prompts when another agent works in a different repository but should import this knowledge base.

## Auto Handoff Mode

Prefer the command when you can run it from this knowledge-base repository:

```bash
npm run design:handoff -- "<TARGET_PROJECT_PATH>"
```

Use `--write` to create `DESIGN_AGENT_HANDOFF.md` inside the target project:

```bash
npm run design:handoff -- "<TARGET_PROJECT_PATH>" --write
```

Use `--pack` or `design:pack` to create `DESIGN_AGENT_HANDOFF.md` plus `.design-agent/README.md`, `.design-agent/prompt.txt`, `.design-agent/working-brief.md`, `.design-agent/manifest.json`, `.design-agent/acceptance-checklist.md`, `.design-agent/final-report-template.md`, and `.design-agent/AGENTS_SNIPPET.md` inside the target project:

```bash
npm run design:handoff -- "<TARGET_PROJECT_PATH>" --pack
npm run design:pack -- "<TARGET_PROJECT_PATH>"
```

Install the managed design-agent block into the target `AGENTS.md` when the next agent should auto-discover the packet from the target project itself:

```bash
npm run design:install-agent-rules -- "<TARGET_PROJECT_PATH>"
```

Verify the generated packet before handing it to another agent:

```bash
npm run design:packet-check -- "<TARGET_PROJECT_PATH>"
```

After the receiving agent fills `.design-agent/working-brief.md`, verify it before coding:

```bash
npm run design:brief-check -- "<TARGET_PROJECT_PATH>"
```

Before final handoff, verify `.design-agent/final-report-template.md` has real changed-file, command, and visual evidence:

```bash
npm run design:final-check -- "<TARGET_PROJECT_PATH>"
```

To inspect the target's overall design-agent readiness at any point:

```bash
npm run design:target-audit -- "<TARGET_PROJECT_PATH>"
npm run design:target-audit -- "<TARGET_PROJECT_PATH>" --write
```

Default `auto` mode inspects the target folder and chooses `forgestudio`, `dashboard`, `scratch`, or `universal`. Use explicit `--mode handoff|universal|forgestudio|dashboard|scratch|qa` only when you already know the surface.

`Files changed` in the final report must use target-relative paths that exist inside the target project. `design:target-audit` treats missing paths, directories, and paths outside the target as not ready for final handoff.
`Browser routes checked` must include the route paths named in `.design-agent/working-brief.md`; checking a different route does not prove the changed surface.
`Information architecture checked` must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior; generic `checked`, `done`, or component-only wording does not prove app structure.
`Interaction model checked` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control; generic `checked`, `done`, or static component wording does not prove interaction design.
`Copy/status language checked` must name affected object, state/status, reason or next action, and evidence/source/sample label; generic `checked`, `done`, `success`, or `ready` wording does not prove status clarity.
`Decision/review cockpit checked` must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path; generic `checked`, `done`, or component-only wording does not prove decision support.
`Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components; generic `checked`, `done`, or `looks good` wording does not prove visual-system work.
`State coverage checked` must include the states named in `.design-agent/working-brief.md` `Included states`, except states explicitly listed as deferred.
`Component state evidence checked` must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence; generic `checked`, `done`, or component-only wording does not prove state QA.
`Product read`, `Workflow improved`, and `Implementation slice contract` must reference the working brief's primary object, workflow/actions, and data/fixture truth; generic `done`, `improved`, or component-only wording does not prove a coherent product slice.
Before coding, `.design-agent/working-brief.md` must name the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
`Five-second test` must name object, state, next action, recovery, and evidence. `Mediocrity risks fixed` and `Product-specific details` must reference the working brief; generic `passed`, `checked`, `improved`, or `looks good` text does not pass `design:target-audit`.
For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, `AI Design App Invariants` in the working brief must name the concrete proposal-only path plus bridge proof: preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. `Operational pattern checked` in the final report must name the same path with real evidence or an explicit risk.
`Rubric score` must be numeric on the /30 scale; `PASS` requires 26+/30 and `PASS WITH RISKS` requires 18+/30 or higher.
If the visual verdict is `MANUAL_BROWSER_INSPECTION`, the notes artifact must name the route/screen, viewport or pixel size, and visual/layout/focus/overlap check.

## Handoff Packet Prompt

```text
Use the design knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

The active project is:
<TARGET_PROJECT_PATH>

Read docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md first, then follow its route. Do not modify the knowledge-base repository unless explicitly asked.
Before coding, fill docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md so the change is a coherent route/screen/workflow with object, object model, visual system, data, states, actions, evidence, and risks. Name the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan before editing files.
```

## Universal Product UI Prompt

```text
Use the design knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

The active project is:
<TARGET_PROJECT_PATH>

Do not edit the knowledge-base repository unless explicitly asked. Read:
- docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md
- docs/design-workbench/AGENT_START_HERE.md
- docs/design-workbench/FORGESTUDIO_CONTEXT.md
- docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md for AI design apps, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches.
- docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
- docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
- docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
- docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
- docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md
- docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
- docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
- docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
- docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
- docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
- docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
- docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
- docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
- docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
- docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
- docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
- docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
- docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
- docs/design-workbench/COMPONENT_STATE_SPEC.md
- docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
- docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
- docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
- docs/design-workbench/AGENT_REPORT_EXAMPLES.md
- .codex/skills/product-ui-design-orchestrator/SKILL.md
- .codex/skills/product-ui-design-orchestrator/references/universal-product-ui-playbook.md
- .codex/skills/product-design-taste/SKILL.md
- .codex/skills/product-design-taste/references/product-design-taste-playbook.md
- .codex/skills/product-ui-component-sourcing/SKILL.md
- .codex/skills/product-ui-component-sourcing/references/component-sourcing-matrix.md
- .codex/skills/product-ui-visual-qa/SKILL.md
- .codex/skills/product-ui-visual-qa/references/visual-qa-checklist.md
- .codex/skills/design-ai-workbench-screens/SKILL.md
- .codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md

Task: improve the active project's product UI/dashboard/editor/site. Classify the surface first, follow the Universal Design Runbook, fill the Universal Product Design Brief, name the product object model, define the visual system contract, choose the closest Product Surface Blueprint, map information architecture with PRODUCT_UI_INFORMATION_ARCHITECTURE.md, choose a Product UI Screen Recipe, name local files to inspect/change, define interaction transitions with PRODUCT_UI_INTERACTION_MODEL.md, define copy/status language with PRODUCT_UI_COPY_STATUS_LANGUAGE.md, shape decision/review cockpits with PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, fill PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md, choose component blueprints, and define key Component State Specs. Do not edit code until the brief names the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan. For reusable product components, use PRODUCT_UI_COMPONENT_BLUEPRINTS before implementation or sourcing. For dashboards, admin panels, records UIs, operations screens, or data tools, use PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK before layout work. Use product-design-taste for workflow-first taste decisions. Use product-ui-component-sourcing before adding or copying UI libraries/components. For AI design apps, canvas editors, proposal/diff review, verification, ledger/history, or ForgeStudio-like workbenches, use AI_DESIGN_APP_TRUSTED_VERTICAL, design-ai-workbench-screens, AI_WORKBENCH_INTERACTION_FLOWS, AI_WORKBENCH_IMPLEMENTATION_SLICES, and PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT before layout work; the working brief must fill AI Design App Invariants with proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen visibility. Do not force landing-page structure onto product UI. Improve workflow clarity, decision/review support, information hierarchy, interaction/state/copy coverage, accessibility, responsive behavior, and verification before decorative polish. In the final report, `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` must preserve the working brief's route/screen, primary object, product object model, visual system contract, workflow/actions, data/fixture truth, and states. `Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. `Information architecture checked` must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior. `Interaction model checked` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control. `Copy/status language checked` must name affected object, state/status, reason or next action, and evidence/source/sample label. `Decision/review cockpit checked` must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path. `Component state evidence checked` must name changed components/controls, states checked, and screenshot/browser/manual/keyboard/responsive evidence. For AI design apps, `Operational pattern checked` must name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. Run PRODUCT_UI_TOP_DESIGN_BENCHMARK, score with PRODUCT_UI_REVIEW_RUBRIC, and fix all 0 categories before final handoff. In the final report, `Five-second test` must name object, state, next action, recovery, and evidence, while `Mediocrity risks fixed` and `Product-specific details` must tie back to the working brief. Use product-ui-visual-qa and VISUAL_QA_EVIDENCE_PLAYBOOK before final handoff, with screenshots/browser checks or explicit remaining risk if unavailable. Use AGENT_REPORT_EXAMPLES for the final report shape. Use component, IA/navigation, interactions, copy/status, decision/review, implementation-slice, motion, proof/data, 3D, and QA source maps from the knowledge base when relevant.
```

## ForgeStudio-Specific Prompt

```text
Use the knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

Work in:
<FORGESTUDIO_PROJECT_PATH>

Read docs/design-workbench/FORGESTUDIO_CONTEXT.md, AI_DESIGN_APP_TRUSTED_VERTICAL.md, UNIVERSAL_DESIGN_RUNBOOK.md, UNIVERSAL_PRODUCT_DESIGN_BRIEF.md, PRODUCT_SURFACE_BLUEPRINTS.md, PRODUCT_UI_SCREEN_RECIPES.md, PRODUCT_UI_INFORMATION_ARCHITECTURE.md, PRODUCT_UI_INTERACTION_MODEL.md, PRODUCT_UI_COPY_STATUS_LANGUAGE.md, PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md, PRODUCT_UI_COMPONENT_BLUEPRINTS.md, COMPONENT_STATE_SPEC.md, AI_DESIGN_APP_SCREEN_BLUEPRINT.md, AI_WORKBENCH_INTERACTION_FLOWS.md, AI_WORKBENCH_IMPLEMENTATION_SLICES.md, PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md, PRODUCT_UI_QUALITY_GATE.md, PRODUCT_UI_TOP_DESIGN_BENCHMARK.md, PRODUCT_UI_REVIEW_RUBRIC.md, PRODUCT_UI_VISUAL_QA.md, VISUAL_QA_EVIDENCE_PLAYBOOK.md, AGENT_REPORT_EXAMPLES.md, .codex/skills/product-design-taste/SKILL.md, .codex/skills/product-ui-visual-qa/SKILL.md, and .codex/skills/design-ai-workbench-screens/SKILL.md from the knowledge base before editing. Treat ForgeStudio as a local-first AI design engineering studio, not a landing page and not a chat UI. The UI must support:
open project -> design search -> import -> canvas -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/history.

Improve the smallest coherent product surface first. Use AI_DESIGN_APP_TRUSTED_VERTICAL.md to name the source-of-truth objects, false-state bans, proof/evidence surfaces, decision question, after-state, and recovery path. Pick an implementation slice from AI_WORKBENCH_IMPLEMENTATION_SLICES.md: launcher/import, workspace selection, comment-to-proposal, proposal review, or ledger/export. Fill PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md before coding: route/screen, primary object, product object model, visual system contract, data/fixture source, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, states included/deferred, actions, responsive behavior, commands, screenshots, and risks. Fill AI Design App Invariants before coding: external AI is proposal-only until what evidence exists, where preview/diff is visible, where verification is visible, where human approval happens, where transaction/ledger evidence is visible, where agent connection/scopes are visible, how comments become agent tasks, how pending proposals/approvals reach the live UI, how failures/recovery are shown inline, and how export/reopen recovery works. Show real project state, agent connection/scopes, comment tasks, pending proposals, pending approval bridge, verification, ledger/history, empty/error/loading states, rollback/retry paths, and a real decision cockpit for proposal review: decision question, before/after comparison, evidence, risk, approve/revise/reject, after-state, and ledger/recovery. External AI is proposal-only until preview/diff, verification, approval, transaction, and ledger evidence exist. Do not fake agent status, imported assets, proof, metrics, screenshots, completed work, or vague "AI fixed it" copy. Before final handoff, run PRODUCT_UI_TOP_DESIGN_BENCHMARK and screenshot/browser QA across the changed workspace surface. Report `Visual system checked` with tool typography/type scale, spacing/density rhythm, panel/canvas surfaces, radius/borders, status/selection contrast, and local tokens/components. Report `Operational pattern checked` with proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen evidence. Report a five-second test with object, state, next action, recovery, and evidence, not a generic pass/fail sentence.
```

## Dashboard Upgrade Prompt

```text
Use the knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

Work in:
<TARGET_PROJECT_PATH>

Use product-ui-design-orchestrator, product-design-taste, PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md, PRODUCT_UI_INFORMATION_ARCHITECTURE.md, PRODUCT_UI_INTERACTION_MODEL.md, PRODUCT_UI_COPY_STATUS_LANGUAGE.md, PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md, PRODUCT_UI_TOP_DESIGN_BENCHMARK.md, product-ui-component-sourcing, product-ui-visual-qa, ui-audit, ui-refactor-principles, details-that-make-interfaces-feel-better, tailwind-design-system-v4/shadcn-ui if applicable. Fill the Universal Product Design Brief, name the dashboard product object model, define the visual system contract, use the Dashboard blueprint, choose the Dashboard Overview or Master Detail recipe, name local files to inspect/change, map dashboard IA/navigation, define action transitions, define copy/status language, shape the dashboard decision/review cockpit, fill an implementation slice contract, choose component blueprints, and define Component State Specs for table/list rows, filters, detail drawer, status badges, and export/retry controls. Do not code until the brief names the dashboard object model, visual system contract, dashboard blueprint, screen recipe/state specs, local files to inspect/change, and component state plan. Improve the dashboard for scan speed and repeated work: navigation, tables/lists, filters, saved views, empty/loading/error/stale states, source/freshness copy, decision queues, risk/evidence panels, forms, command actions, detail panes, bulk actions, spacing, typography, contrast, focus/hover/active states, and responsive behavior. No marketing hero, no decorative card bloat, no fake metrics, no vague "success" statuses, no bulk component installs. Run PRODUCT_UI_TOP_DESIGN_BENCHMARK and score with PRODUCT_UI_REVIEW_RUBRIC before final handoff. Use VISUAL_QA_EVIDENCE_PLAYBOOK and AGENT_REPORT_EXAMPLES for screenshot/browser evidence and final report, including `Visual system checked` for typography, density, surfaces, status colors, contrast, and local tokens/components plus `Component state evidence checked` for table/list rows, filters, drawer, badges, and export/retry controls.
```

## New UI From Scratch Prompt

```text
Use the knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

Work in:
<TARGET_PROJECT_PATH>

Build a product-grade UI from scratch. Use UNIVERSAL_DESIGN_RUNBOOK.md, product-design-taste, product-ui-component-sourcing, PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md, and PRODUCT_UI_TOP_DESIGN_BENCHMARK.md. First inspect the project, classify the surface, fill the Universal Product Design Brief, name the product object model, define the visual system contract, choose the closest Product Surface Blueprint, map information architecture with PRODUCT_UI_INFORMATION_ARCHITECTURE.md, choose Product UI Screen Recipes, name local files to inspect/change, define action transitions with PRODUCT_UI_INTERACTION_MODEL.md, define copy/status language with PRODUCT_UI_COPY_STATUS_LANGUAGE.md, shape decision/review cockpits with PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, fill the implementation slice contract, choose component blueprints, define Component State Specs, and state the design read. Do not create files until the brief names the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan. Then design the workflow map, route map, screen inventory, interaction model, copy/status model, decision/review model, component system, state model, visual system contract, motion policy, top-design target, rubric target, and verification plan. Use PRODUCT_UI_COMPONENT_BLUEPRINTS.md before implementing app shell, tables/lists, filters, drawers, inspectors, command menus, diff/review panels, verification, ledger, export, alerts, or toasts. Use AI_DESIGN_APP_TRUSTED_VERTICAL.md, AI_DESIGN_APP_SCREEN_BLUEPRINT.md, AI_WORKBENCH_IMPLEMENTATION_SLICES.md, and design-ai-workbench-screens for AI design tools, PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md for product UI tokens/components, and PRODUCT_UI_COMPONENT_SOURCING.md before adding libraries. Use existing project stack and avoid bulk installing UI libraries. For app/editor/dashboard surfaces, prioritize task flow, decision support, density, IA/navigation, interactions, states, factual status copy, accessibility, and responsive layout before visual drama. Use PRODUCT_UI_TOP_DESIGN_BENCHMARK, PRODUCT_UI_REVIEW_RUBRIC, and product-ui-visual-qa plus VISUAL_QA_EVIDENCE_PLAYBOOK before final handoff; final reports must include visual-system evidence, information-architecture evidence, interaction evidence, copy/status language evidence, decision/review cockpit evidence, and component/control state evidence, not generic route/action/state claims.
```

## Final QA Prompt

```text
Use docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md, docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md, docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md, docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md, docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md, docs/design-workbench/PRODUCT_UI_VISUAL_QA.md, docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md, and docs/design-workbench/AGENT_REPORT_EXAMPLES.md from:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

The active project is:
<TARGET_PROJECT_PATH>

Use .codex/skills/product-ui-visual-qa/SKILL.md. Audit the active product UI. Report blockers first. Verify surface classification, implementation slice contract, workflow clarity, decision/review support, state/copy coverage, accessibility, responsive behavior, motion safety, proof/data integrity, component sourcing, and screenshots/commands used. Verify that `Visual system checked` names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. Verify that `Copy/status language checked` names affected object, state/status, reason or next action, and evidence/source/sample label. Verify that `Decision/review cockpit checked` names decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path. Verify that `Component state evidence checked` names changed components/controls, concrete states, and screenshot/browser/manual/keyboard/responsive evidence. Verify that `Five-second test` names object, state, next action, recovery, and evidence, and that mediocrity/product-specific fields reference the working brief. Fix issues when possible; otherwise produce a prioritized punch list with file references, evidence artifacts, remaining risks, and a PASS / PASS WITH RISKS / FAIL verdict.
```
