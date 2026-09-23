# Agent Report Examples

Use these examples when another agent needs to report product UI work clearly. They are templates, not fake evidence. Replace every route, changed-file path, command, screenshot path, and result with real project evidence. `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` should reference the working brief's route/screen, primary object, product object model, visual system contract, workflow/actions, data/fixture truth, and states. `Visual system checked` should name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. `Browser routes checked` should include the route paths from the working brief. `Information architecture checked` should name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior. `Interaction model checked` should name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control. `Copy/status language checked` should name affected object, state/status, reason or next action, and evidence/source/sample label. `Decision/review cockpit checked` should name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path. `State coverage checked` should cover the brief's included states unless explicitly deferred. `Component state evidence checked` should name changed components/controls, concrete states, and screenshot/browser/manual/keyboard/responsive evidence. `Five-second test` should name object, state, next action, recovery, and evidence; `Mediocrity risks fixed` and `Product-specific details` should reference the working brief instead of generic `passed/checked/improved` wording. For AI design apps, `Operational pattern checked` should name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. `Rubric score` must be numeric on the /30 scale and meet the verdict threshold. `Files changed` should use target-relative paths that exist inside the target project. If using `MANUAL_BROWSER_INSPECTION`, the notes artifact must name route/screen, viewport or pixel size, and visual/layout/focus/overlap checks.

## Dashboard Upgrade Report

```text
Surface classified:
dashboard / admin hybrid

Brief/blueprint used:
UNIVERSAL_PRODUCT_DESIGN_BRIEF: user = ops manager, job = scan stalled jobs and act, core loop = filter -> inspect -> resolve -> export.
PRODUCT_SURFACE_BLUEPRINTS: Dashboard + Admin Panel.

Screen recipe/state specs:
PRODUCT_UI_SCREEN_RECIPES: Dashboard Overview + Master Detail / Admin Records.
COMPONENT_STATE_SPEC: JobTable rows, filter bar, JobDetailDrawer, status badge, export/retry controls.

Implementation slice contract:
Route = `/dashboard`; primary object = job row; workflow = filter -> select row -> inspect detail -> retry/export; data = labeled sample fixture; states = loaded, empty filtered result, loading skeleton, stale source, export pending/failed; evidence = desktop/tablet/mobile screenshots and build commands.

Information architecture checked:
Route map keeps dashboard overview, saved views, selected record detail, and export/history reachable from the app shell. Main work zone is the job table; context/review zone is the detail drawer; mobile moves detail into a drawer.

Interaction model checked:
Filtering shows active/pending/empty states, selected-row actions stay local to the drawer, export has pending/failed/success states, and retry appears near the affected data.

Copy/status language checked:
Status copy names the affected object and recovery path: "Export failed for 2 rows", "Sample data", "Stale sync warning", and "Clear filters" replace generic success/error labels.

Decision/review cockpit checked:
The main table is a triage queue: stalled jobs are sorted by risk, selected row shows evidence/source/freshness, and drawer actions separate retry, export, and destructive resolution with after-state and history.

Rubric score:
Surface fit 2, workflow clarity 2, information architecture 2, interaction model 2, copy/status clarity 2, decision/review support 2, information hierarchy 2, state coverage 2, component craft 1, data/proof honesty 2, accessibility 2, responsive behavior 2, visual system 1, motion/feedback 1, evidence 2. Total: 27. Blocking categories: none.

Top-design benchmark:
Five-second test passes: primary object = job row, state = stalled/stale/export pending, next action = retry/export from detail drawer, recovery = clear filters or retry export, evidence = source/freshness labels. Mediocrity risks fixed: oversized cards removed, table made primary, sample data labeled, status badges stabilized. Product-specific details: saved views, stale sync warning, export failure row, selected-count actions.

Product read:
This screen is for repeated operational scanning, so dense tables, filters, clear status, and recovery states matter more than decorative cards.

Object model checked:
Job row entity shows id, owner, status, source timestamp, error reason, and export history; lifecycle covers queued -> running -> failed/stale -> retrying -> exported/resolved; operator permissions gate retry/export/destructive resolution.

Visual system checked:
Typography uses compact 12-14px table/control text and 20-24px page heading; spacing follows 4/8/12/16 rhythm; 8px radius and subtle dividers define panels; neutral base plus explicit success/warning/error status colors keep scan speed high; target-local Tailwind tokens and existing table/drawer/badge components stay in use.

Workflow improved:
Moved the main job table into the primary column, made saved filters visible, added selected-row detail drawer, added empty/error/loading states, and made export/retry actions local to the affected data.

Files changed:
- src/app/dashboard/page.tsx
- src/components/dashboard/JobTable.tsx
- src/components/dashboard/JobDetailDrawer.tsx
- src/components/ui/status-badge.tsx

Component/source choices:
Used existing table, drawer, button, badge, and tooltip primitives. No external UI library added.

State coverage checked:
loaded, empty result, loading skeleton, selected row, stale sync warning, export pending, export failed.

Component state evidence checked:
JobTable rows checked loading skeleton, empty filtered result, selected/focused row, stale/error badge, and export pending/failed states with `/dashboard` desktop/tablet/mobile screenshots plus keyboard focus notes.

Accessibility checked:
Keyboard tab path reaches filters, table rows, drawer close, retry, and export. Focus-visible is present. Icon-only buttons have labels/tooltips.

Responsive checked:
1440x900, 1024x768, 768x1024, 390x844. Mobile switches to list + detail drawer; table columns do not clip.

Motion/proof/data risks handled:
No fake metrics added. Existing sample metrics are labeled "Sample data". Motion limited to drawer and filter feedback; reduced-motion keeps final state visible.

Commands run:
npm run lint
npm run typecheck
npm run build

Project command evidence:
REAL_PROJECT_COMMANDS: lint, typecheck, and build completed in the target project.

Command evidence artifacts:
qa/commands/lint.log
qa/commands/typecheck.log
qa/commands/build.log

Screenshots/browser checks:
qa/dashboard/overview__loaded__1440x900.png
qa/dashboard/overview__selected-row__1024x768.png
qa/dashboard/overview__empty__768x1024.png
qa/dashboard/overview__export-failed__390x844.png

Visual evidence verdict:
REAL_BROWSER_SCREENSHOTS: four viewport/state screenshots captured from the changed dashboard route.

Blockers fixed:
[P0] 390x844: export button clipped under sticky footer. Fixed by moving export into drawer action row and adding bottom safe padding.
[P1] 1024x768: status badges wrapped inconsistently. Fixed with stable badge width and short labels.

Remaining risks:
Real production export API was not available locally, so export success was verified through the app's mocked success fixture only.

Verdict:
PASS WITH RISKS
```

## AI Design Workbench Report

```text
Surface classified:
AI design studio / canvas workbench

Brief/blueprint used:
UNIVERSAL_PRODUCT_DESIGN_BRIEF: user = designer supervising an external AI agent, job = inspect imported page, comment on object, review proposal, verify, approve/export.
PRODUCT_SURFACE_BLUEPRINTS: AI Design Studio Or Canvas Editor.

Screen recipe/state specs:
PRODUCT_UI_SCREEN_RECIPES: AI Design Studio Workspace + Proposal / Diff Review + Verification / Ledger / History + Export / Share.
COMPONENT_STATE_SPEC: layer rows, CanvasViewport, ProposalPanel, VerificationPanel, CommentTaskList, ledger row, export artifact row.

Implementation slice contract:
Route = `/studio`; primary object = selected canvas node; workflow = select object -> anchored comment -> proposal -> preview/diff -> verification -> approve/revise -> ledger/export; data = disconnected agent plus sample proposal fixture; states = no project, asset skipped, selected object, agent disconnected, proposal pending, verification failed, ledger row; evidence = route screenshots, constrained viewport checks, and app commands.

Information architecture checked:
Route map keeps launcher/import, workspace, proposal review, ledger/history, and export reachable. Workspace IA uses project/layers left, canvas center, inspector/proposals right, with ledger/history available without losing the current selection.

Interaction model checked:
Comment/task transitions remain draft -> pending agent -> proposal ready/failed -> preview/diff -> verification -> approve/revise -> ledger/export. Approval is blocked until preview and verification states are visible.

Copy/status language checked:
AI states stay factual: "Agent disconnected", "Proposal ready", "Verification failed", "Sample proposal", "Ledger row created", and "Rollback unavailable" are distinct from applied/done states.

Decision/review cockpit checked:
Proposal review shows the decision question, changed objects/files, before/after diff, verification evidence, failed checks, approve/revise/reject actions, after-approval transaction, and ledger/reopen path.

Operational pattern checked:
External AI remains proposal-only in this slice: sample proposal is separate from applied state, preview/diff is visible before approval, verification failed blocks approval copy, human approve/revise/reject actions are explicit, accepted state points to transaction/ledger evidence, agent connection/scopes are shown in the top bar, anchored comment becomes a visible task, pending proposal/approval bridge is represented in the review rail, inline failure/recovery copy replaces silent no-op states, and export/reopen recovery stays visible in the ledger/export rail.

Rubric score:
Surface fit 2, workflow clarity 2, information architecture 2, interaction model 2, copy/status clarity 2, decision/review support 2, information hierarchy 2, state coverage 2, component craft 2, data/proof honesty 2, accessibility 1, responsive behavior 2, visual system 2, motion/feedback 1, evidence 2. Total: 28. Blocking categories: none. Accessibility remains a noted risk for full screen-reader flow.

Top-design benchmark:
Five-second test passes: primary object = selected canvas node/proposal, state = sample proposal with verification failed, next action = revise/retry verification or approve when checks pass, recovery = ledger/reopen path, evidence = changed objects/files, checklist, ledger row. Mediocrity risks fixed: chat does not replace canvas, proposal/verification/applied states are separate, disconnected agent is factual, mobile review mode is explicit. Product-specific details: anchored comment pins, layer selection mirror, transaction evidence, rollback unavailable copy.

Product read:
The UI is a supervisor/review surface, not a chat page. The canvas, selection, comments/tasks, proposal state, verification, ledger, and export path must stay visible.

Object model checked:
Selected canvas node, anchored comment/task, proposal, verification check, DesignTransaction, ledger row, and export artifact each have visible fields, ownership/source labels, lifecycle states, and proposal-only/applied boundaries.

Visual system checked:
Studio shell uses compact tool typography, 8/12/16 spacing, 6-8px control radius, dark neutral canvas chrome, high-contrast selection/status accents, explicit warning/error colors, local panel/tabs/button/tokens, and motion only for panel continuity and verification feedback.

Workflow improved:
Added a stable studio shell with project map/layers on the left, canvas center, inspector/proposals on the right, anchored comments, agent disconnected state, proposal diff panel, verification checklist, and ledger row after approval.

Files changed:
- src/app/studio/page.tsx
- src/components/studio/StudioShell.tsx
- src/components/studio/CanvasViewport.tsx
- src/components/studio/ProposalPanel.tsx
- src/components/studio/VerificationPanel.tsx
- src/components/studio/CommentTaskList.tsx

Component/source choices:
Used local panel, tabs, button, tooltip, and drawer primitives. Added no new dependencies. Canvas overlay remains custom because selection anchors and comment pins are product-specific.

State coverage checked:
no project open, scan/import running, asset skipped with path and reason, object selected, comment anchored, agent disconnected, proposal pending, preview/diff ready, verification failed, approved/applied with ledger row, rollback unavailable.

Component state evidence checked:
CanvasViewport, ProposalPanel, VerificationPanel, CommentTaskList, and ledger/export rail checked selected, disconnected, pending, failed, approved, rollback unavailable, and reopened states with `/studio` browser screenshots, constrained viewport checks, and keyboard/focus notes.

Accessibility checked:
Keyboard reaches project tree, canvas toolbar, inspector tabs, comment composer, approve/revise actions, and export. Icon-only canvas tools have accessible names and tooltips. Focus is restored after proposal drawer close.

Responsive checked:
1440x900, 1024x768, 768x1024, 390x844. Desktop keeps three-pane layout. Tablet collapses inspector into drawer. Mobile shows review mode with canvas preview, task/proposal tabs, and clear "open on desktop for editing" state.

Motion/proof/data risks handled:
Agent state is never faked. Disconnected and mocked proposal states are labeled. Approval requires preview/diff, verification state, and ledger entry. Reduced motion disables panel slide choreography.

Commands run:
npm run lint
npm run typecheck
npm run build

Project command evidence:
REAL_PROJECT_COMMANDS: lint, typecheck, and build completed in the target project.

Command evidence artifacts:
qa/commands/lint.log
qa/commands/typecheck.log
qa/commands/build.log

Screenshots/browser checks:
qa/workbench/studio__no-project__1440x900.png
qa/workbench/studio__object-selected__1440x900.png
qa/workbench/studio__proposal-diff__1024x768.png
qa/workbench/studio__verification-failed__768x1024.png
qa/workbench/studio__mobile-review__390x844.png

Visual evidence verdict:
REAL_BROWSER_SCREENSHOTS: five viewport/state screenshots captured from the changed studio route.

Blockers fixed:
[P0] 1024x768: proposal drawer covered approve/revise buttons. Fixed drawer max-height and sticky action row.
[P0] 390x844: canvas toolbar overlapped comment pin. Fixed mobile review layout and moved toolbar into compact bottom sheet.
[P1] 1440x900: selected object was visible on canvas but not mirrored in layers. Added selected layer state.

Remaining risks:
The real external MCP agent was not connected in this environment. Agent connected state was not marked PASS; only disconnected and sample proposal fixtures were verified.

Verdict:
PASS WITH RISKS
```

## Bad Report Patterns

Do not report:

```text
Done, improved the dashboard, looks much better.
```

Problems:

- no surface classification;
- no product read;
- no visual-system evidence;
- no route/screen map or information architecture evidence;
- no action transition or interaction evidence;
- no copy/status language evidence;
- no decision/review cockpit evidence;
- no files;
- no commands;
- no screenshots;
- no states;
- no component-state evidence;
- no risks;
- no verdict.

Do not report:

```text
All good. I checked responsive.
```

Problems:

- no viewport names;
- no route names;
- no evidence;
- no statement about overlap/clipping;
- no accessibility or data/proof check.
