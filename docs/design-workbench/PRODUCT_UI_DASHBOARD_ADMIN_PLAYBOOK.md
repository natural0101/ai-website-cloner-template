# Dashboard, Admin, And Data Tool Playbook

Use this after `UNIVERSAL_DESIGN_RUNBOOK.md`, `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, and `PRODUCT_SURFACE_BLUEPRINTS.md` when the target surface is a dashboard, admin panel, records UI, analytics console, data tool, operations screen, settings surface, or any product UI where users scan, filter, compare, edit, approve, export, or recover work. Use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md` for route/pane placement, `PRODUCT_UI_INTERACTION_MODEL.md` for action transitions, `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` for factual status labels, empty/error copy, source/freshness language, and sample/demo labels, and `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for triage, approval, comparison, and evidence/risk surfaces.

The default goal is fast repeated use, not marketing drama.

## Core Layout Contract

| Region | Job | Strong pattern |
| --- | --- | --- |
| App shell | Orientation and navigation | stable sidebar/rail, active route, account/project/status |
| Scope header | What data/work is shown | title, owner/source, time range, freshness, primary action |
| Control bar | Narrow the work | search, filters, saved views, density, sort, export/retry |
| Summary strip | Decision highlights | 3-5 compact facts tied to the table/list below |
| Primary surface | Do the work | table/list/tree/grid with stable rows and clear selection |
| Detail pane | Inspect and act on one object | drawer/split pane with fields, activity, actions, validation |
| Decision/review | Compare and choose | evidence, risk, options, after-state, approval/rejection |
| Status/recovery | Trust and repair | inline error, stale data, sync, undo/redo, rollback, audit |

If a region has no product job, remove it.

## Dashboard Pattern

Use when the user needs to scan, compare, decide, then act.

Must include:

- scope: owner, time range, source, freshness;
- filters before affected data;
- a primary table/list/grid as the main surface;
- summary numbers only when they affect a decision;
- selected-row detail or drilldown;
- export/share/retry near the affected data.
- a decision question or next-action queue when the dashboard is used for triage.

Avoid:

- invented KPI cards;
- charts that do not answer faster than a table;
- equal-weight cards for unrelated metrics;
- dashboard pages with no next action.

## Admin Records Pattern

Use when users manage records, permissions, settings, billing, teams, assets, or configuration.

Must include:

- searchable/filterable records;
- status, role, owner, last changed, and audit metadata;
- bulk actions only after selection;
- detail drawer or split pane;
- validation and unsaved-change state;
- destructive confirmation and recovery/restore path;
- permission denied and locked states.

Avoid:

- destructive actions next to normal save;
- hidden primary management actions;
- custom controls without keyboard/focus support;
- "saved" copy without pending/error/rollback states.
- vague "success" or "done" copy that does not name the record, action, or recovery path.

## Data Tool Pattern

Use when the table/list/query result is the product.

Must include:

- schema/source/freshness;
- column controls;
- sort, filter, search, saved views;
- query/loading state;
- invalid filter/query state;
- partial/stale result state;
- row detail and export.

Avoid:

- decorative charts before table clarity;
- hiding units, time range, source, or data freshness;
- only designing the loaded state.

## Summary Strip Rules

Use a summary strip only when it helps the next decision.

Good cards:

- compact label, value, delta/source, status;
- tied to filters/time range;
- click or drill into the related data;
- honest sample/demo label when not real.

Bad cards:

- giant decorative metrics;
- fake growth numbers;
- no source/freshness;
- unrelated metrics competing equally.

## Table And List Craft

Tables/lists are often the product. Treat them as designed surfaces.

Requirements:

- stable row height;
- aligned columns and tabular numbers;
- visible selected row;
- hover and focus-visible states;
- sort/filter affordances;
- empty, loading skeleton, error, stale, and permission states;
- row actions that do not cause layout shift;
- long text truncates or wraps intentionally;
- mobile fallback chooses priority columns or card rows with labels.

Column order:

1. identity/name;
2. status/risk;
3. owner/source;
4. timing/freshness;
5. amount/count/progress;
6. primary row action or detail trigger.

## Filter And Saved View Craft

Filters must feel operational, not decorative.

Use:

- search box with clear button;
- compact filter chips with remove;
- saved views for repeated work;
- reset all;
- active filter count;
- disabled filter state when data/source is unavailable;
- empty filtered result with next action.

Do not hide essential filters in an unlabeled icon-only menu unless space requires it and the button has a clear accessible name.

## Detail Pane Craft

A detail pane should answer:

- what is selected;
- why it matters;
- what can be changed;
- what happened before;
- what action is next;
- what can fail.

Include:

- selected object title/status/source;
- grouped fields;
- validation;
- activity/audit;
- primary and secondary actions;
- close/back path;
- save pending/success/error;
- unsaved-change confirmation.

## Bulk Actions

Bulk actions appear only when rows are selected.

Must show:

- selected count;
- affected object type;
- reversible vs destructive action distinction;
- confirmation for destructive or permission-sensitive actions;
- partial failure state;
- clear all selection.

## Empty, Error, And Stale States

Every operational surface needs useful failure copy.

| State | Must say |
| --- | --- |
| No data connected | what source is missing and how to connect |
| Empty result | whether data is absent or filters are too narrow |
| Loading | what is loading and where results will appear |
| Stale data | last successful refresh and retry action |
| Error | reason, affected source/object, and next action |
| Permission denied | required role/scope and request path |
| Partial result | what loaded, what failed, and impact |

Toast-only failure is not enough.

## Responsive Strategy

Desktop:

- full app shell;
- table/list primary;
- detail split pane or drawer;
- filters visible.

Tablet:

- collapsible nav;
- filters in toolbar/drawer;
- detail drawer;
- table with priority columns.

Mobile:

- review and focused action first;
- priority list/card rows with labels;
- filters in drawer;
- bulk actions limited or moved to review flow;
- no horizontal table overflow unless explicitly intentional.

## Visual Tone

Operational UI can still feel premium:

- precise alignment;
- quiet surfaces;
- one accent family for action;
- semantic color for status;
- compact typography;
- confident empty/error states;
- restrained shadows;
- clear focus/selection;
- no generic AI glow unless the product brand truly uses it.

## QA Checklist

Before handoff, verify:

- data source/freshness is visible or sample data is labeled;
- loaded, empty, loading, error, stale, selected, and permission states exist;
- filters and saved views affect visible data;
- row/detail selection mirrors correctly;
- bulk actions do not appear with zero selection;
- destructive actions have confirmation and recovery path;
- table/list does not clip at desktop narrow and mobile;
- keyboard can reach filters, rows, detail pane, save/cancel, and confirmation;
- screenshots/browser checks cover loaded, empty/error, selected/detail, and narrow viewport states.

## Output Contract

When planning or reporting, include:

```text
Operational surface:
Primary object:
Core decision/action:
Layout regions:
Table/list strategy:
Filter/saved-view strategy:
Detail pane strategy:
Bulk/destructive action policy:
State coverage:
Copy/status language:
Decision/review cockpit:
Data/source honesty:
Responsive behavior:
Verification evidence:
```
