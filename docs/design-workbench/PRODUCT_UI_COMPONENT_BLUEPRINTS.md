# Product UI Component Blueprints

Use this after `PRODUCT_UI_SCREEN_RECIPES.md`, `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, `PRODUCT_UI_INTERACTION_MODEL.md`, `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, and `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, and before `COMPONENT_STATE_SPEC.md` or `PRODUCT_UI_COMPONENT_SOURCING.md`. It defines the product-grade components agents should design before reaching for external catalogs or decorative blocks.

Each blueprint is a contract: job, anatomy, states, copy/status language, accessibility, responsive behavior, and evidence.

## App Shell

Use for dashboards, admin panels, SaaS apps, data tools, and workbenches.

Anatomy:

- top bar with product/project, current section, status, primary action;
- sidebar/rail with active route, collapsed state, unavailable items;
- main workspace with one primary job;
- optional detail/inspector/proposal panel;
- status strip only when it carries real sync, warnings, selection, export, or ledger state.

States:

- first run/no project;
- active route;
- loading/syncing;
- disconnected;
- permission denied;
- unsaved changes;
- collapsed/narrow;
- mobile fallback.

Evidence:

- desktop wide and desktop narrow screenshots;
- active route and collapsed state;
- keyboard reaches nav, primary action, and first content action.

## Data Table Or List

Use when users scan, compare, filter, select, export, or act on records.

Anatomy:

- source/freshness label when trust matters;
- header row with sort/filter affordances;
- stable rows with identity, status/risk, owner/source, timing, numeric/progress values, row action;
- selection state and detail trigger;
- empty/loading/error/stale states near the data.

States:

- loading skeleton;
- no data connected;
- empty filtered result;
- hover/focus-visible;
- selected;
- disabled/unavailable;
- warning/error/stale;
- export pending/failed.

Evidence:

- loaded, empty, selected, error/stale screenshots;
- no row-height shift on hover/selection;
- desktop narrow and mobile fallback checked.

## Filter Bar And Saved Views

Use when users narrow repeated work.

Anatomy:

- search with clear;
- filter controls or chips;
- active filter count;
- saved views;
- reset all;
- export/retry when tied to filtered data.

States:

- no filters;
- active filters;
- disabled source unavailable;
- empty filtered result;
- invalid filter;
- loading results.

Evidence:

- active filter screenshot;
- empty filtered screenshot;
- keyboard path through search, filters, reset, saved view.

## Detail Drawer Or Split Pane

Use when one selected object needs inspection, editing, or decision.

Anatomy:

- selected object title, status, source;
- grouped fields;
- activity/audit trail;
- primary action, secondary action, close/back;
- inline validation/failure;
- recovery path.

States:

- no selection;
- loading detail;
- selected;
- validation error;
- save pending;
- save failed/success;
- unsaved changes;
- permission denied;
- record not found.

Evidence:

- selected/detail screenshot;
- validation/error screenshot;
- focus enters and returns after close.

## Inspector Field Group

Use for canvas editors, settings, configuration, and object properties.

Anatomy:

- field label, value, unit, token/source binding;
- reset/revert;
- helper/error text;
- locked/inherited/overridden marker;
- responsive value indicator when relevant.

States:

- no selection;
- multi-selection;
- inherited;
- overridden;
- locked;
- invalid;
- pending;
- reset available.

Evidence:

- selected object with inspector;
- locked/invalid field screenshot;
- keyboard and screen-reader labels checked.

## Command Menu

Use as acceleration, not as the only way to access primary work.

Anatomy:

- trigger with accessible name;
- search input;
- grouped commands;
- disabled/unavailable commands with reason;
- keyboard hints only when useful;
- no-results state.

States:

- closed/open;
- searching;
- no results;
- command disabled;
- command running/success/error.

Evidence:

- keyboard-only flow;
- focus restore;
- no primary actions hidden only inside command menu.

## Task Or Comment Card

Use when feedback becomes work.

Anatomy:

- anchor/object reference;
- status;
- owner/agent;
- latest activity;
- linked proposal/transaction;
- resolve/reopen/retry actions.

States:

- draft;
- pending agent;
- failed;
- needs revision;
- ready for review;
- resolved;
- reopened.

Evidence:

- anchor and selected object mirrored;
- failed/retry state visible inline;
- no passive comment that cannot be tracked as work.

## Proposal Panel

Use when AI or another actor proposes changes before approval.

Anatomy:

- linked task;
- actor/source;
- changed objects/files;
- risk;
- verification summary;
- preview/diff action;
- approve/revise/reject.

States:

- no agent;
- pending;
- blocked;
- failed;
- ready;
- stale;
- verification failed;
- approved;
- rejected.

Evidence:

- changed objects/files visible;
- stale/failure reason;
- no "applied" state before approval and ledger evidence.

## Diff Viewer

Use when users compare before/after.

Anatomy:

- before/after visual mode;
- code/object diff when relevant;
- viewport tabs;
- changed object list;
- stale/conflict indicator;
- approve/revise path nearby.

States:

- loading;
- diff unavailable;
- preview failed;
- stale base;
- conflict;
- accepted/rejected.

Evidence:

- before/after screenshot;
- failed/stale screenshot;
- keyboard can move across tabs and actions.

## Verification Checklist

Use when trust, AI output, import, export, or risky actions require proof.

Anatomy:

- grouped failed/warning/passed items, worst first;
- command/screenshot/source evidence;
- failure reason;
- retry path;
- stale result indicator.

States:

- not run;
- running;
- passed;
- warning;
- failed;
- stale;
- retrying.

Evidence:

- failed verification screenshot;
- command/test output reported;
- approval policy visible when verification fails.

## Ledger Or History Row

Use for audit, recovery, and trust.

Anatomy:

- actor/source;
- transaction/action;
- linked task/proposal;
- timestamp;
- result;
- rollback/reopen availability.

States:

- empty history;
- applied;
- rollback unavailable;
- conflict;
- restored.

Evidence:

- accepted proposal creates ledger row;
- rollback unavailable reason;
- linked task/proposal visible.

## Export Or Share Panel

Use when users expect an artifact.

Anatomy:

- target path/destination;
- artifact list;
- warnings/missing assets;
- progress;
- retry/open/download/share action;
- history/metadata link.

States:

- not configured;
- pending;
- partial;
- failed;
- completed;
- permission denied.

Evidence:

- failed and completed states;
- target/artifact names;
- no completed/exported claim without artifact evidence.

## Inline Alert And Toast Policy

Use inline alerts for actionable failures. Use toast only for transient confirmation.

Inline alert must include:

- affected object/source;
- reason;
- next action;
- retry/recover when available.

Toast can include:

- short success confirmation;
- undo when safe;
- non-blocking status.

Hard rule: permission, import, verification, save, export, and agent failures cannot live only in a toast.

For detailed status wording, sample/demo labels, AI/proof language, and inline-vs-toast placement, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
For approval/review components, also use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` so the component exposes the decision question, options/comparison, evidence, risk, action policy, after-state, and audit/recovery path.

## Component Output Contract

When planning or reporting a reusable/product component, include:

```text
Component:
Product job:
Owner screen/recipe:
Anatomy:
Interaction transitions:
Copy/status language:
Decision/review role:
States:
Accessibility:
Keyboard:
Responsive:
Data/proof honesty:
Source/local reuse:
QA evidence:
```
