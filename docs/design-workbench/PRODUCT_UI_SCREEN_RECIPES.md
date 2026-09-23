# Product UI Screen Recipes

Use this after `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, `PRODUCT_SURFACE_BLUEPRINTS.md`, and `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`. These recipes translate the product read into concrete screens, panels, actions, states, copy, decisions, and evidence. Use `PRODUCT_UI_INTERACTION_MODEL.md` for action transitions, `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` for factual labels/messages, and `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for comparison/approval/review surfaces before component styling or sourcing.

Do not copy these as rigid templates. Use them as a checklist for what a serious product screen must contain.

For dashboard, admin, records, and data-tool surfaces, also use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` for operational layout, table/list, filter, bulk action, detail pane, and state guidance.

## App Shell

Use for dashboards, admin panels, SaaS apps, data tools, and workbenches.

Anatomy:

- top bar: product/project, current section, primary status, global action;
- side navigation or rail: stable destinations, active route, collapsed state;
- main workspace: one primary job, not equal-weight card sprawl;
- right drawer/panel when detail, inspector, or proposal review is contextual;
- status/footer strip only when it carries real state such as sync, selection, warnings, or export.

Required states:

- first run/no project;
- loading/syncing;
- disconnected/unavailable;
- active route;
- permission denied;
- unsaved changes;
- narrow desktop/sidebar collapsed;
- mobile fallback.

Evidence:

- screenshot at 1440x900 and 1024x768;
- active route and collapsed state checked;
- keyboard reaches nav, primary action, and first content action.

## Dashboard Overview

Use when the user scans, compares, decides, and acts.

Anatomy:

- compact header with scope, time range, data source, freshness;
- filters/saved views before the data they affect;
- summary strip only for decision-driving numbers;
- table/list/grid as the main surface;
- detail drawer or drilldown for selected object;
- export/share/retry near the affected data.

Required states:

- no data connected;
- sample/demo data;
- loading skeleton;
- empty filtered result;
- stale data;
- selected row/detail;
- export pending/success/failure.

Evidence:

- loaded, empty, selected, and error/stale screenshots;
- table/list no-overlap check at desktop-narrow and mobile;
- fake metrics removed or labeled.

## Master Detail / Admin Records

Use for CRUD, permissions, settings, and record management.

Anatomy:

- searchable/filterable record list or table;
- bulk actions that are visible only when selection exists;
- detail panel/drawer with grouped fields;
- audit/ownership/last changed metadata;
- destructive actions separated from normal save;
- recovery path after destructive or agent-driven changes.

Required states:

- no records;
- loading rows;
- row selected;
- validation error;
- save pending;
- unsaved changes;
- destructive confirmation;
- permission denied;
- record not found;
- restore/rollback.

Evidence:

- selected and validation screenshots;
- keyboard path through table, drawer, save, cancel, destructive confirmation;
- focus returns after drawer/modal close.

## AI Design Studio Workspace

Use for ForgeStudio-like products, AI design apps, canvas editors, external-agent review tools.

Anatomy:

- left: project map, pages, layers, assets, warnings;
- center: canvas/preview with selection overlays, zoom, breakpoints, comment anchors;
- right: inspector, comments/tasks, proposals, verification tabs;
- top/status: project, page, agent status, proposal status, export;
- bottom/status: zoom, viewport, selected object, warnings, ledger summary.

Required states:

- no project open;
- scan/import running;
- asset skipped with path and reason;
- no page selected;
- object selected;
- comment draft/anchored;
- agent disconnected;
- proposal pending/ready/stale/failed;
- verification passed/warning/failed;
- approval applied with ledger row;
- rollback/reopen unavailable/conflict.

Evidence:

- object selected screenshot mirrors canvas, layers, inspector;
- agent disconnected screenshot;
- proposal/diff screenshot;
- verification failed screenshot;
- mobile review-mode screenshot.

## Proposal / Diff Review

Use when AI or another actor proposes changes before approval.

Anatomy:

- proposal summary: actor, linked task, changed objects/files, risk;
- before/after visual diff or preview;
- code/object diff when relevant;
- verification checklist;
- approve, revise, reject, and rollback/reopen path;
- ledger/history preview after apply.
- decision question and after-decision state.

Required states:

- no agent connected;
- proposal pending;
- diff unavailable;
- stale proposal;
- verification running;
- verification failed;
- approved/applied;
- rejected;
- needs revision.

Evidence:

- screenshot with approve/revise visible;
- failed verification state checked;
- evidence/risk/action zones visible together at desktop width;
- no "AI fixed it" copy before approval and ledger evidence.

## Verification / Ledger / History

Use when trust, auditability, or recovery matters.

Anatomy:

- worst state first: failed, warning, pending, passed;
- commands/checks with timestamps or source labels;
- linked screenshots/artifacts;
- ledger rows with actor, transaction, linked task/comment, result, time;
- rollback/reopen availability and conflict reason.

Required states:

- not run;
- running;
- passed;
- warning;
- failed;
- retry;
- empty history;
- rollback unavailable;
- restored/conflict.

Evidence:

- command output reported;
- screenshot/artifact paths listed;
- rollback unavailable/conflict copy is explicit.

## Export / Share

Use when the user expects an artifact.

Anatomy:

- export target/path or destination;
- file/artifact list;
- warnings and missing assets;
- progress and retry;
- open/download/share action after completion;
- history entry or reproducible artifact metadata.

Required states:

- not configured;
- pending;
- partial;
- failed;
- completed;
- permission denied;
- missing asset warning.

Evidence:

- export failure and success/complete states;
- target path or artifact source shown;
- no "exported" claim without artifact/check.

## Product Website / Hybrid App Website

Use for product websites that are not pure landing pages or include app-like surfaces.

Anatomy:

- first viewport names the product/category and shows real product signal;
- sections explain what it is, who it is for, how it works, proof/source, and next action;
- screenshots/assets should show the real product, not div-based fake UI;
- app-like widgets must be labeled demo/sample if not connected;
- mobile navigation and media fallback are designed.

Required states:

- media unavailable fallback;
- mobile menu;
- pricing/contact ambiguity resolved;
- no proof/source available;
- sample app preview labeled.

Evidence:

- first viewport desktop/mobile screenshot;
- proof/data source check;
- no fake testimonials/logos/metrics/screenshots.

## Recipe Output

When planning a screen, produce:

```text
Recipe:
Primary object:
Main workflow:
Interaction model:
Copy/status language:
Decision/review cockpit:
Layout anatomy:
Primary action:
Secondary actions:
Required states:
Component/state specs:
Data/proof risks:
Responsive behavior:
Evidence plan:
```
