# Universal Product UI Playbook

This reference turns the existing landing-heavy knowledge base into a general product and website design workflow.

Before choosing layout or components, read:

```text
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
```

## Surface Taxonomy

| Surface | Primary job | Design posture |
| --- | --- | --- |
| Dashboard | Scan, compare, decide, act | Dense, predictable, tabular, calm |
| Admin panel | Manage records and settings | Conservative, robust, explicit states |
| AI design studio | Inspect, comment, propose, preview, approve, export | Tool-like, spatial, auditable, fast |
| Canvas editor | Select objects, edit properties, navigate layers | High contrast selection, stable panels, precise controls |
| SaaS app | Complete core workflow | Clear navigation, forms, tables, feedback loops |
| Website | Explain product and route visitors | Brand-forward, content hierarchy, proof integrity |
| Landing page | Convert a visitor | Use the landing pipeline |
| 3D/WebGL surface | Inspect or dramatize 3D content | Performance-first, fallback-ready |

## Routing Matrix

| Need | Skills / sources |
| --- | --- |
| Existing UI feels weak | `redesign-existing-projects`, `ui-audit`, `ui-refactor-principles` |
| AI design app / canvas workbench screens | `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, `design-ai-workbench-screens`, `product-design-taste`, `PRODUCT_UI_QUALITY_GATE.md` |
| Product UI taste from scratch | `product-design-taste`, then `frontend-design-for-distinctive-interfaces` if a distinctive visual direction is needed |
| New distinctive interface | `product-design-taste`, `frontend-design-for-distinctive-interfaces`, `design-taste-frontend` only when its landing/portfolio brief matches |
| App/dashboard density | This skill, `product-design-taste`, `ui-refactor-principles`, `details-that-make-interfaces-feel-better` |
| Product IA/navigation | `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, `UNIVERSAL_DESIGN_RUNBOOK.md` |
| Product interactions/transitions | `PRODUCT_UI_INTERACTION_MODEL.md`, `COMPONENT_STATE_SPEC.md` |
| Product copy/status language | `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, `PRODUCT_UI_REVIEW_RUBRIC.md` |
| Decision/review/approval surfaces | `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, `PRODUCT_UI_REVIEW_RUBRIC.md` |
| Implementation slice planning | `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md` |
| Component primitives and catalog choices | `product-ui-component-sourcing`, `shadcn-ui`, `tailwind-design-system-v4`, existing local components |
| Final product UI visual QA | `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`, `PRODUCT_UI_REVIEW_RUBRIC.md`, `product-ui-visual-qa`, `ui-audit`, `PRODUCT_UI_QUALITY_GATE.md`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md` |
| Animated UI | `animation-systems-for-product-grade-web-motion`, `animate-ui-catalog`, motion safety source map |
| Website/landing conversion | landing workflow and landing skills |
| Claims/proof/demo data | proof integrity source map |
| 3D/WebGL | `three-js-animation`, `webgl-3d-object`, Blender workbench rules |

## ForgeStudio-Inspired Product Principles

ForgeStudio-like products are not chat pages. The UI must expose the actual work loop:

```text
open project -> design search -> import -> inspect -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/reopen
```

Design implications:

- The canvas is the main work surface, not a decorative preview.
- Sidebars should separate project map, layers/assets, comments/tasks, inspector, agent/proposals, and history.
- Agent output is proposal-only until preview/diff, verification, human approval, transaction/ledger evidence, and recovery are visible.
- Agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, and failure/recovery handling are first-class product surfaces, not settings-page trivia.
- Any "done" claim needs accepted diff, closed task/comment, ledger/history row, and visible verification.
- The working brief must fill AI Design App Invariants before coding: proposal-only, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. `N/A` is valid only for non-AI-design-app surfaces.
- Empty states must explain why the project/page/agent/proposal is unavailable and what action fixes it.
- Warnings must include the path/object/reason when import or asset detection fails.

For screen-level planning, read:

```text
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
.codex/skills/design-ai-workbench-screens/SKILL.md
.codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md
```

For design tokens, control states, and layout defaults, read:

```text
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
```

For component source decisions, read:

```text
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
.codex/skills/product-ui-component-sourcing/SKILL.md
.codex/skills/product-ui-component-sourcing/references/component-sourcing-matrix.md
```

## Product UI Quality Gate

Before calling an app/dashboard/editor design done, read:

```text
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
docs/design-workbench/AGENT_REPORT_EXAMPLES.md
.codex/skills/product-ui-visual-qa/SKILL.md
```

At minimum, verify:

- Brief readiness: `design:brief-check` passes before coding; the brief names user/job/object, product object model, visual system contract, workflow/action path, data/source truth, route/screen, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, verification evidence, and top-design target.
- AI design app invariants: for ForgeStudio-like workbenches, `design:brief-check` passes only when proposal-only, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery are concrete; final `Operational pattern checked` must report the same loop with evidence.
- Information hierarchy: primary workflow is visually first; secondary panels do not compete.
- Information architecture: route map, navigation model, app shell, pane jobs, responsive IA, and recovery paths match the product job.
- Navigation: current location, back path, and task status are visible.
- Interaction model: primary actions expose pending, success, failure, retry, undo/rollback, permission, and proof states.
- Copy/status language: primary status labels name object, state, reason, next action, and evidence/sample truth.
- Decision/review support: approval, triage, proposal review, and comparison screens show decision question, options/comparison, evidence, risk, action policy, after-state, and audit/recovery.
- Product object model: entities, fields/attributes, status lifecycle, ownership/permissions, events/history, relationships, and source truth are named before UI layout decisions.
- Visual system contract: typography scale, spacing/density rhythm, radius/borders/surfaces, color/status/contrast rules, icon/motion policy, and target-local tokens/components are named before UI layout decisions.
- Implementation slice: route/screen, primary object, product object model, visual system contract, data/fixture truth, chosen blueprint, screen recipe/state specs, local target files, component state plan, workflow, included/deferred states, responsive behavior, commands, screenshots, and risks form one coherent product slice.
- Visual-system report integrity: final `Visual system checked` names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
- Information architecture report integrity: final `Information architecture checked` names route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior.
- Interaction model report integrity: final `Interaction model checked` names primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control.
- Copy/status report integrity: final `Copy/status language checked` names affected object, state/status, reason or next action, and evidence/source/sample label.
- Decision/review report integrity: final `Decision/review cockpit checked` names decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path.
- Implementation-slice report integrity: final `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` preserve the same route/screen, primary object, product object model, visual system contract, workflow/actions, data/source truth, and states from the working brief; generic `done/improved` or component-only wording is not accepted.
- Component-state report integrity: final `Component state evidence checked` names changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence.
- Data density: tables/lists support scanning, sorting/filtering when needed, and stable row heights.
- Forms/inspectors: labels, units, helper text, validation, disabled/pending states.
- Selection: selected object/row/layer is obvious in canvas and side panels.
- Review loop: proposal, diff, verification, approve/revise, and history states are distinct.
- Empty/loading/error: every major pane has a composed state.
- Component states: reusable components follow `COMPONENT_STATE_SPEC.md`, not just happy-path styling.
- Accessibility: keyboard path, focus-visible, labels, contrast, reduced motion.
- Responsive: desktop is optimized first for tools; tablet/mobile degrade intentionally, not accidentally.
- Performance: no layout-shifting loaders, no frame-by-frame React state for pointer/scroll, no heavy animation in dense panes.
- Evidence: final report lists commands, screenshots/browser checks, evidence artifacts, blockers fixed, remaining risks, `Project command evidence`, `Visual evidence verdict`, and PASS/PASS WITH RISKS/FAIL verdict. `design:target-audit` should not reach `READY FOR FINAL HANDOFF` from packet-only or planned evidence.
- Top-design benchmark: final report passes the five-second test and names mediocrity risks fixed plus product-specific details.
- Rubric: final report scores the surface and fixes all 0 categories before claiming PASS.

## Anti-Patterns

- Marketing hero at the top of a dashboard.
- Oversized cards where a table/list is the real tool.
- Decorative background effects behind dense controls.
- Static "happy path" screenshots with no empty/error/loading states.
- Isolated visual component polish passed off as a product slice.
- Fake agent status, fake metrics, fake customer proof, fake screenshots.
- Hidden failures in console warnings.
- Multiple mutation paths for canonical state in editor-like products.
- Bulk installing UI libraries because the catalog looks good.
