# Product UI Visual QA

Use this before an agent calls any dashboard, editor, AI design studio, canvas workbench, admin panel, SaaS app, or product UI done.

## Rule

Visual UI work is not done until it has evidence.

Evidence can be screenshots, browser checks, Playwright runs, app screenshots from the user, or a clear explanation of why visual verification could not run. Static code review alone is not enough for final sign-off. Use `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` for the five-second top-design bar, `PRODUCT_UI_REVIEW_RUBRIC.md` for scoring, `VISUAL_QA_EVIDENCE_PLAYBOOK.md` for the evidence protocol, and `AGENT_REPORT_EXAMPLES.md` for the report shape.
Use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` to verify factual status labels, empty/error copy, AI/proof language, and sample/demo labels.
Use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` to verify approval, comparison, triage, proposal-review, evidence/risk, after-state, and audit/recovery surfaces.
Use `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` to verify the change is a coherent route/screen/workflow, not isolated decorative polish.

## Required Checks

| Area | Check |
| --- | --- |
| Routes/screens | Changed surfaces are named. |
| Route consistency | `Browser routes checked` includes the route paths from the working brief and implementation slice. |
| Changed files | `Files changed` lists target-relative paths that exist inside the target project. |
| Product object model | Working brief and final report name how entities, fields/attributes, status lifecycle, permissions/events, relationships, and source truth are represented in UI. |
| Visual system contract | Working brief and final report name typography, spacing/density, radius/borders/surfaces, color/status/contrast, icon/motion policy, and target-local tokens/components. |
| Visual system evidence | Final `Visual system checked` names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. |
| Screen/slice selection | Working brief names the closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan before coding. |
| Implementation slice | Route/screen, primary object, data/fixture truth, workflow, included/deferred states, commands, screenshots, and risks are named. |
| Implementation-slice evidence | Final `Product read`, `Workflow improved`, and `Implementation slice contract` fields reference the working brief's primary object, workflow/actions, and data/fixture truth; generic `done/improved` wording blocks handoff readiness. |
| Information architecture evidence | Final `Information architecture checked` names route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior; generic `checked/done` wording blocks handoff readiness. |
| Top-design benchmark | Five-second test passes: primary object, state, next action, recovery, and evidence are clear; mediocrity risks and product-specific details are named. |
| Top-design evidence | Final report `Five-second test` names object, state, next action, recovery, and evidence; `Mediocrity risks fixed` and `Product-specific details` reference the working brief instead of generic `passed/checked/improved` text. |
| AI design app invariants | For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, the working brief names proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. |
| AI operational evidence | Final report `Operational pattern checked` names proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. |
| Viewports | Desktop, desktop-narrow, tablet, mobile when possible. |
| States | Empty, loading, error, disabled, selected, pending, success, retry/rollback where relevant. |
| State consistency | `State coverage checked` covers the brief's `Included states`, except states explicitly deferred. |
| Component state evidence | `Component state evidence checked` names changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence. |
| Layout | No overlap, clipping, accidental wrapping, unstable row/control sizes, hidden controls. |
| Product workflow | Main loop, current object, current task/proposal, verification, history/recovery visible. |
| Information architecture | Route map, app shell, navigation model, work zones, context/review zones, responsive IA, and recovery placement match the product job. |
| Interaction model | Primary actions expose pending, success, failure, retry/undo/rollback, permission, and proof behavior where relevant. |
| Interaction model evidence | Final `Interaction model checked` names primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control. |
| Copy/status language | Empty, loading, error, disabled, stale, disconnected, sample/demo, pending, success, and recovery messages name object, reason, next action, and evidence/source where relevant. |
| Copy/status language evidence | Final `Copy/status language checked` names status/message copy with affected object, state/status, reason or next action, and evidence/source/sample label. |
| Decision/review cockpit | Review/approval/triage surfaces show decision question, options/comparison, evidence, risk, actions, after-state, and audit/recovery path. |
| Decision/review cockpit evidence | Final `Decision/review cockpit checked` names decision question, options/comparison, evidence/risk, primary or secondary action, after-state, and audit/recovery path. |
| Screen recipe/state spec | Changed screens match the chosen screen recipe; changed components expose the required states. |
| Review rubric | Surface fit, workflow clarity, interaction model, copy/status clarity, decision/review support, hierarchy, state coverage, component craft, data honesty, accessibility, responsive behavior, visual system, motion, and evidence are scored. |
| Rubric threshold | `Rubric score` is numeric; `PASS` requires 26+/30, `PASS WITH RISKS` requires 18+/30 or higher, and 0/blocking categories are not hidden. |
| Accessibility | Keyboard, focus-visible, labels, tooltip/accessibility names, contrast, reduced motion. |
| Components | External source justified, no bulk install, demo data cleaned. |
| Data/proof | No fake metrics, agent state, imported assets, screenshots, proof, or "real" data. |

## P0 Blockers

- Text or controls overlap/clip.
- Canvas/WebGL/media area is blank without fallback.
- Major pane lacks empty/loading/error state.
- Selected/current object is not visible in product UI.
- Proposal/diff/approval/ledger states are collapsed into vague "done".
- Important actions use vague "done/success/ready" feedback without object, reason, next action, or evidence.
- Review/approval surface lacks visible evidence, risk, comparison, or after-decision state.
- Fake proof or fake agent state is presented as real.
- `Files changed` names missing files, directories, or paths outside the target project.
- `Browser routes checked` omits the changed route path named in the working brief.
- `Information architecture checked` is generic or omits route/screen map, navigation/app shell, main/context zones, or responsive/recovery behavior.
- `Interaction model checked` is generic or omits primary actions/transitions, pending-success-failure states, recovery/permission behavior, or the affected object/control.
- `Copy/status language checked` is generic or omits affected object, state/status, reason or next action, or evidence/source/sample label.
- `Decision/review cockpit checked` is generic or omits decision question, options/comparison, evidence/risk, action, after-state, or audit/recovery path.
- `State coverage checked` omits states promised in the working brief's `Included states`.
- `Component state evidence checked` is generic or omits changed components/controls, concrete states, or screenshot/browser/manual/keyboard/responsive evidence.
- Component library was bulk-installed or demo block shipped as product UI.
- The implementation is only an isolated component/style fragment while the route, object, workflow, data, states, and evidence do not line up.
- Working brief or final report lacks product object model evidence: entities, fields/attributes, status lifecycle, permissions/events, relationships, and source truth.
- Working brief or final report lacks visual system evidence: typography, spacing/density, radius/borders/surfaces, color/status/contrast, icon/motion policy, and target-local token/component conventions.
- `Visual system checked` is generic or omits typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, or target-local tokens/components.
- Working brief lacks the closest product surface blueprint, screen recipe/state specs, local files to inspect/change, or component state plan.
- Final `Implementation slice contract` is generic, omits route/screen, primary object, workflow/action, data/source truth, or does not match the working brief.
- Five-second test fails: primary object, state, next action, recovery, or evidence are unclear.
- Final top-design fields are generic, such as `passed`, `checked`, `improved`, or `looks good`, or do not reference the working brief's mediocrity risks and product-specific details.
- AI design app `Operational pattern checked` is generic or omits proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, or export/reopen.
- `Rubric score` is non-numeric, below verdict threshold, or reports 0/blocking categories.
- No visual/browser evidence was captured for a visual change and no reason was reported.

## Done Statement

Final reports must include:

```text
Surface classified:
Rubric score:
Top-design benchmark checked:
Five-second test:
Mediocrity risks fixed:
Product-specific details:
Object model checked:
Visual system checked:
Files changed:
Information architecture checked:
Interaction model checked:
Copy/status language checked:
Decision/review cockpit checked:
Operational pattern checked:
Implementation slice checked:
Screen recipe/state specs checked:
Routes/screens checked:
Viewports checked:
States checked:
Component state evidence checked:
Accessibility checked:
Component/data/proof risks checked:
Commands run:
Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK:
Command evidence artifacts:
Screenshots/browser checks:
Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK:
Evidence artifacts:
Blockers fixed:
Remaining risks:
Verdict:
```

If `Project command evidence` is `REAL_PROJECT_COMMANDS`, list non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` command-log artifacts in the target project before `design:target-audit` can report `READY FOR FINAL HANDOFF`.

`Files changed` must list target-relative paths that exist inside the target project. Missing files, directories, or paths outside the target project keep `design:target-audit` below `READY FOR FINAL HANDOFF`.

If `Visual evidence verdict` is `REAL_BROWSER_SCREENSHOTS` or `USER_SCREENSHOTS`, the listed screenshot/artifact paths must exist in the target project, be non-empty, and be valid PNG/JPEG/WebP/GIF/MP4/WebM files before `design:target-audit` can report `READY FOR FINAL HANDOFF`.

If `Visual evidence verdict` is `MANUAL_BROWSER_INSPECTION`, list a non-empty `.md`, `.txt`, `.html`, or valid `.json` notes artifact in the target project before `design:target-audit` can report `READY FOR FINAL HANDOFF`. The notes must mention the checked route/screen, viewport name or pixel size, and a visual/layout/focus/overlap check.
