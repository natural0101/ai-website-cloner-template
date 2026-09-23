# Product UI Quality Gate

Use this before an agent calls any dashboard, editor, SaaS app, AI design tool, or website UI work complete.

For the full design order from project read to verification, also use `UNIVERSAL_DESIGN_RUNBOOK.md`.
For route maps, navigation, app shell, zones, and recovery placement, also use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
For actions, transitions, pending states, failures, recovery, and proof behavior, also use `PRODUCT_UI_INTERACTION_MODEL.md`.
For factual labels, empty/error copy, AI/proof status language, sample/demo labels, and inline-vs-toast policy, also use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
For comparison, approval, proposal review, triage, decision queues, evidence/risk panels, and audit/recovery paths, also use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
For AI design studio or canvas-editor work, also use `AI_DESIGN_APP_SCREEN_BLUEPRINT.md`.
For tokens, layout, components, and state standards, also use `PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md`.
For product component anatomy and behavior, also use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md`.
For external component/library choices, also use `PRODUCT_UI_COMPONENT_SOURCING.md`.
For screen anatomy and component states, also use `PRODUCT_UI_SCREEN_RECIPES.md` and `COMPONENT_STATE_SPEC.md`.
For dashboards, admin panels, records UIs, operations screens, and data tools, also use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`.
For AI design studio or canvas-editor implementation order, also use `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`.
For every implementation, also use `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` so the work is a coherent route/screen/workflow with object, data, states, actions, evidence, and risks.
For top-design threshold and protection against "works but still generic", also use `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`.
For quality scoring and top-design self-review, also use `PRODUCT_UI_REVIEW_RUBRIC.md`.
For screenshot/browser evidence and final visual self-review, also use `PRODUCT_UI_VISUAL_QA.md`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md`, and `AGENT_REPORT_EXAMPLES.md`.

## P0 Gates

These block completion.

| Gate | Pass condition |
| --- | --- |
| Surface classified | Agent states whether this is dashboard, admin, editor, canvas, SaaS app, website, landing, 3D/WebGL, or hybrid. |
| Runbook phase coverage | Agent can report project read, brief, blueprint, workflow map, information architecture, screen/interaction/state/copy/decision inventory, design-system decisions, component sourcing, implementation slice, and verification. |
| Product object model | Working brief names entities, visible fields/attributes, status lifecycle, ownership/permissions, events/history, relationships, and source truth before coding. |
| Visual system contract | Working brief names typography, spacing/density, radius/borders/surfaces, color/status/contrast, icon/motion policy, and target-local token/component conventions before coding. |
| Visual system evidence | Final report `Visual system checked` names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. |
| Screen/slice selection before coding | Working brief names the closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan before implementation starts. |
| Implementation slice contract | Agent names the route/screen, primary object, product object model, user job, data/fixture source, included/deferred states, actions, responsive behavior, verification commands, screenshots/browser evidence, and remaining risks. Final `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` must reference the working brief's primary object, product object model, visual system contract, workflow/actions, and data/source truth rather than generic `done/improved` wording. |
| Workflow visible | Main user loop is visible in the UI, not hidden in chat or docs. |
| Information architecture | Agent names route map, navigation model, app shell, main work zone, context/review zones, responsive IA, and recovery placement for the changed surface. |
| Information architecture evidence | Final report `Information architecture checked` names route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior. |
| Interaction model | Primary actions have enabled, pending, success, failure, retry/undo/rollback, permission, and proof states where relevant. |
| Interaction model evidence | Final report `Interaction model checked` names primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control. |
| Copy/status language | Primary status labels name the affected object, state, reason, next action, and evidence/sample label where relevant; no vague "done/success/ready" as sole feedback. |
| Copy/status language evidence | Final report `Copy/status language checked` names status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label. |
| Decision/review cockpit | Approval, triage, comparison, proposal-review, and trust-heavy screens show decision question, options/comparison, evidence, risk, action policy, after-state, and audit/recovery. |
| Decision/review cockpit evidence | Final report `Decision/review cockpit checked` names decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path. |
| No landing bias | Product tools do not start with marketing hero layouts unless the surface is actually marketing. |
| State coverage | Major panes have empty, loading, error, disabled, selected, pending, success, and retry/rollback states where relevant. |
| State consistency | Final report `State coverage checked` covers the working brief's `Included states`, except states explicitly listed in `Deferred states`. |
| Component state evidence | Final report `Component state evidence checked` names changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence. |
| Screen recipe/state spec | Agent names the screen recipe and key component state specs used for changed surfaces. |
| Component blueprint | Reusable product components match `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` or report why a custom pattern is needed. |
| Operational pattern | Dashboard/admin/data-tool surfaces use a source-aware operational pattern: scope, filters, primary table/list, detail pane, bulk/destructive policy, and recovery states. |
| AI workbench slice | AI design workbench surfaces name the chosen implementation slice and preserve its required panes, states, proof, and mock/sample labels. |
| AI design app invariants | AI design workbench surfaces expose proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery before they are treated as real product slices. |
| Review rubric | Agent scores the changed surface with `PRODUCT_UI_REVIEW_RUBRIC.md`; all 0/blocking categories are fixed or the verdict is FAIL. |
| Rubric threshold | `Rubric score` is numeric on a /30 scale; `PASS` is 26+/30 and `PASS WITH RISKS` is 18+/30 or higher. |
| Top-design benchmark | Agent runs `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: five-second test, primary object/state/next action, weakest visual category, mediocrity risks fixed, and product-specific details. Final top-design fields are substantive, not `passed/checked/improved`; `Five-second test` names object, state, next action, recovery, and evidence, and risk/detail fields tie back to the working brief. |
| Navigation clarity | Current location, back path, active item, and task/proposal status are visible. |
| Real data integrity | No fake metrics, proof, logos, customer names, screenshots, agent status, or "real" dashboard states. Mock data is labeled sample/demo. |
| Component sourcing | External components solve a named product job, local options were checked first, no bulk catalog install, and demo data is removed/labeled. |
| Accessibility | Keyboard path, focus-visible, labels, contrast, hit areas, and reduced motion are checked. |
| No overlap/clipping | Text, controls, panels, canvas overlays, dropdowns, and tooltips do not collide on desktop/tablet/mobile. |
| Visual evidence | Screenshots/browser checks cover changed visual surfaces, or missing visual verification is explicitly reported as a risk. |
| Verification run | Agent reports actual commands, screenshots, or browser checks used. If not possible, states why. |
| Changed-file evidence | Final report lists target-relative `Files changed` paths that exist inside the target project. Missing paths, directories, or paths outside the project block final handoff readiness. |
| Route consistency | Final report `Browser routes checked` includes the route paths named in the working brief's route fields. |
| Evidence status | Final report chooses `Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK` and `Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK`; final handoff readiness requires real project commands and real visual evidence. Real project commands must list non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` command-log artifacts. Screenshot-based evidence must list non-empty, valid PNG/JPEG/WebP/GIF/MP4/WebM artifact files in the target project. Manual browser inspection must list a non-empty `.md`, `.txt`, `.html`, or valid `.json` notes artifact that names the route/screen, viewport or pixel size, and visual/layout/focus/overlap check. |

## Product-App Checks

| Area | Check |
| --- | --- |
| Information architecture | Sidebars, top bars, inspector panels, content panes, drawers, route maps, and responsive pane changes have distinct jobs. |
| Density | Dense areas use tables/lists/grids intentionally; decorative cards are not used where scan speed matters. |
| Tables and lists | Stable row heights, clear alignment, sortable/filterable affordances when needed, skeleton rows while loading. |
| Filters and saved views | Search, filters, active filter count, reset, saved views, and empty filtered state are visible when relevant. |
| Bulk actions | Bulk actions appear only after selection and show selected count, affected object type, partial failure, and clear-selection path. |
| Forms and inspectors | Labels, units, helper text, validation, disabled/pending states, and unsaved-change handling. |
| Selection | Selected object/row/layer is clear in the main view and mirrored in side panels. |
| Review loop | Proposal, diff, verification, approve, revise, applied, rejected, and history states are visually distinct. |
| Decision support | Decision-driving surfaces expose comparison axes, evidence/source limits, risk/impact, and next actions without forcing the user to infer the choice from raw panels. |
| Command surfaces | Menus, command palettes, context menus, and shortcuts do not hide primary actions. |
| Assets | Images, fonts, icons, GLB/WebGL, screenshots, and generated assets have source/usage notes. |
| Recovery | Back, undo/redo, reset, retry, rollback, history, or reopen paths exist for destructive or agent-driven work. |
| Interaction transitions | No action jumps from idle to vague done; pending/failure/recovery/proof are visible near the affected object. |
| Copy/status language | Empty, loading, error, disabled, stale, disconnected, sample/demo, pending, success, and recovery copy are factual and placed near the affected object. |

## Visual Quality Checks

- Establish a clear attention path: primary work surface first, support panels second, metadata third.
- Use one coherent spacing rhythm and one radius system.
- Use restrained color: neutral UI base, deliberate status colors, and one accent family unless the brand requires more.
- Use icon buttons for toolbars and dense controls, with labels/tooltips when ambiguity is possible.
- Use tabular numbers for changing counts, metrics, coordinates, prices, durations, and progress.
- Keep tool surfaces compact. Do not use landing-page display type inside inspectors, tables, sidebars, or dashboards.
- Prefer stable panels over floating cards for repeated operational UI.
- Choose tables/lists/trees/inspectors/toolbars when they match the work better than imported visual blocks.

## Motion Gate

- Motion must support hierarchy, continuity, feedback, or state transition.
- Do not animate dense data for decoration.
- Prefer transform and opacity.
- Respect `prefers-reduced-motion`.
- Avoid scroll hijack, autoplay loops, custom cursors, or heavy WebGL in product panes unless central to the job.

## Done Statement

A product UI change is done only when the final report can say:

```text
Surface classified:
Runbook phase coverage:
Rubric score:
Top-design benchmark checked:
Five-second test:
Mediocrity risks fixed:
Product-specific details:
Object model checked:
Visual system checked:
Workflow improved:
Files changed:
Information architecture checked:
Interaction model checked:
Copy/status language checked:
Decision/review cockpit checked:
Operational pattern checked:
AI workbench implementation slice checked:
Implementation slice contract checked:
Component blueprints checked:
Screen recipe/state specs checked:
State coverage checked:
Component state evidence checked:
Accessibility checked:
Responsive checked:
Motion/proof/data risks handled:
Commands/screenshots used:
Project command evidence:
Command evidence artifacts:
Visual evidence verdict:
Evidence artifacts:
Remaining risks:
Verdict:
```
