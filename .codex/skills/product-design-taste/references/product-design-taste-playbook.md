# Product Design Taste Playbook

Use this reference to make product UI decisions that feel intentional, mature, and useful under repeated work.

For the full design order from project read to QA, use `docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md`. This playbook is for the taste/craft decisions inside that larger runbook.

For dashboard, admin, records, operations, and data-tool surfaces, use `docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` before choosing KPI cards, table/list layout, filters, detail panes, charts, or bulk actions.

For product information architecture, use `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md` before visual styling so routes, navigation, panes, responsive behavior, and recovery paths match the job.
For product interactions, use `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md` before visual styling so primary actions have pending, success, failure, retry, undo/rollback, permission, and proof states.
For product copy/status language, use `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md` before visual styling so empty, error, disconnected, AI/proof, and sample/demo states are factual.
For product decision/review surfaces, use `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` before visual styling so approvals, comparisons, triage, proposal review, evidence, risk, and audit paths are clear.
For AI design studios, canvas editors, proposal/diff flows, or ForgeStudio-like products, use `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md` before visual styling so source-of-truth objects, false-state bans, proof/evidence surfaces, decision question, after-state, recovery path, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, and failure/recovery handling are explicit.
For implementation scope, use `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` before visual styling so polish attaches to a reachable route/screen/workflow with a primary object, data truth, states, actions, responsive behavior, and evidence.
For reusable product components, use `docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before styling so the component has anatomy, states, accessibility, and QA evidence.
For the final top-tier bar, use `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` so the screen passes the five-second test and names mediocrity risks before final handoff.

## Taste Heuristics

| Product question | Strong answer | Weak answer |
| --- | --- | --- |
| What is the user doing? | The main loop is visible and one action is clearly next. | The page looks nice but the work is hidden. |
| What needs attention? | Priority, risk, pending work, and selected objects are obvious. | Every card competes equally. |
| What changed? | Diff, status, history, or inline feedback explains it. | A toast says "Done" with no evidence. |
| What does the status mean? | Object, reason, next action, and evidence/source are named. | A badge says "Ready" or "Success" with no context. |
| What decision is being made? | Question, options, evidence, risk, action, after-state, and audit path are visible. | User must infer the choice from scattered panels. |
| What slice is being shipped? | Route, object, data, action, state coverage, and evidence line up. | A pretty component has no workflow around it. |
| What can fail? | Empty, loading, error, conflict, retry, and rollback states exist. | Only the happy path is designed. |
| How dense should it be? | Density follows scan frequency and task urgency. | Big decorative spacing slows routine work. |
| Is the data honest? | Sample/demo states are labeled and real data is sourced. | Fake metrics or agent states imply proof. |

## Surface Guidance

### Dashboard

- Lead with the user's recurring decisions, not a hero headline.
- Prefer tables, lists, small multiples, filters, and compact summaries over oversized cards.
- Use tabular numbers, consistent alignment, stable row heights, and explicit empty/loading/error states.
- Put drill-down, filters, export, and saved views near the data they affect.

### Admin Panel

- Favor conservative hierarchy, clear permissions, explicit destructive actions, and reversible paths.
- Make record status, validation, ownership, audit trail, and last changed metadata visible.
- Do not hide bulk actions behind decorative menus when they are primary work.

### SaaS Workflow App

- Structure around the core job: create, review, approve, schedule, reconcile, configure, or export.
- Keep navigation, current object, progress, and next action visible.
- Multi-step flows need saved progress, validation, back paths, and final review.

### AI Design Studio Or Canvas Editor

- Start from the trusted vertical, not the panel layout: project, design search, import, agent connection/scopes, object comment/task, pending proposal/approval bridge, proposal, preview/diff, verification, approval, transaction, ledger, failure/recovery, export/reopen.
- Keep the canvas central and quiet; side panels carry object detail, layers/assets, comments, proposals, and history.
- Mirror selection across canvas, layers, inspector, comments, and ledger.
- Treat comments as tasks and agent output as proposals until approval.
- Show proposal, preview/diff, verification, approve/revise, applied/rejected, agent connection/scopes, comment-to-task, pending approval bridge, failure/recovery, rollback, and export/reopen states as separate visual states.
- Do not turn the product into a chat page. Chat can assist; the work surface is the product.

### Data Tool

- Table/list design is the product. Invest in column alignment, sorting/filtering, saved views, row actions, density control, and skeleton rows.
- Use charts only when they answer a question faster than a table.
- Keep units, time ranges, filters, source, and freshness visible.

### Website Hybrid

- Separate marketing/story sections from logged-in/tool sections.
- A public product page can use stronger brand composition; the app shell should return to operational clarity.
- Never carry marketing proof or decorative gradients into dense tool panes by default.

## Visual System

- Typography: use `12-14px` for dense UI, `14-16px` for body, `20-28px` for product page headings, and larger type only for true marketing surfaces.
- Spacing: start from `4, 8, 12, 16, 24, 32`. Dense panels usually use `8/12/16`.
- Radius: choose one system and keep it consistent. Product UI usually works best at `4-8px`.
- Color: neutral surface, one accent family, clear semantic colors. Status color must mean something.
- Borders: use dividers and hairlines to organize scan paths; do not nest bordered cards inside bordered cards.
- Icons: use one icon family, tooltips for icon-only controls, and stable button dimensions.

## Motion Taste

- Use motion for: panel open/close, selection continuity, diff reveal, pending-to-success feedback, and spatial context.
- Default timings: `120-200ms` for controls, `180-260ms` for state changes, `220-320ms` for drawers/popovers.
- Avoid decorative looping motion in dense panes.
- Respect reduced motion and keep final content visible without animation.

## ForgeStudio-Like Taste

ForgeStudio should feel like a serious creative engineering tool:

- local-first, audit-aware, and precise;
- not a Figma clone, not a landing generator, not a chat app;
- strong canvas, layer, inspector, comment/task, proposal, verification, ledger, and export surfaces;
- visible agent connection truth and proposal status;
- calm enough for long sessions, but polished enough to feel like a creative tool.

Use this loop as the product spine:

```text
open project -> design search -> import -> inspect -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/reopen
```

## Common Fixes

| Symptom | Fix |
| --- | --- |
| Looks like a landing page | Replace hero/cards with app shell, navigation, primary workspace, and task states. |
| Looks bland | Add stronger hierarchy, better selection states, precise spacing, one accent, and real status language. |
| Looks cluttered | Group by workflow, align columns, remove duplicate labels, reduce competing borders/shadows. |
| Feels fake | Remove fake proof and label demo/sample data. Add source paths, timestamps, or empty connection states. |
| Feels static | Add hover/focus/selected/pending/error/success states and restrained transition continuity. |
| Hard to trust | Add verification, history, rollback, actor/source labels, and failure reasons. |

## Pre-Handoff Taste Check

- The surface classification is explicit.
- The top-design benchmark is checked: primary object, state, next action, recovery, and evidence are clear within five seconds.
- The core workflow is visible without reading documentation.
- The UI has a stable app shell or content structure suited to the task.
- The implementation slice contract is named and proves route/screen, object, data/source, states, actions, responsive behavior, and evidence.
- Selection and current location are visually clear.
- Empty/loading/error/pending/success/retry states are represented for major panes.
- Status copy is factual and avoids vague "done/success/ready" as sole feedback.
- Decision/review screens make the choice and evidence obvious.
- Sample or mock content is labeled.
- Typography, spacing, radius, icons, and status color are coherent.
- Responsive behavior is intentional, especially for desktop-first tools.
- The product UI review rubric has no 0 categories before final handoff.
- The final report names commands, screenshots, or checks that were actually run.
- The final report includes evidence artifacts, blockers fixed, remaining risks, and PASS/PASS WITH RISKS/FAIL verdict.
