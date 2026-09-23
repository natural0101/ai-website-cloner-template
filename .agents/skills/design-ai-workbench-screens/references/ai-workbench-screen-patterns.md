# AI Workbench Screen Patterns

Use this reference to design ForgeStudio-like AI design tools with real product surfaces instead of a generic chat UI. Pair it with `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md` for the trusted vertical, source-of-truth objects, false-state bans, and slice QA, `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md` for route maps, pane jobs, responsive IA, and recovery placement, `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md` for action transitions, `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md` for factual labels and messages, `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for proposal/import/export/verification review surfaces, `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` for route/screen/object/state/evidence scope, and `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` so the final workbench screen passes the five-second test instead of stopping at a generic tool layout.

## Table Of Contents

- Product loop map
- Workspace information architecture
- Required screen patterns
- Cross-surface state matrix
- Component contracts
- Layout recipes
- Copy and status language
- Responsive behavior
- QA checklist
- Top-design benchmark

## Product Loop Map

Every serious AI design workbench must expose this loop somewhere in the UI:

```text
open project -> design search -> import -> inspect -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/reopen
```

Minimum end-to-end slice:

```text
open folder -> scan report -> page imported -> agent connection/scopes visible -> object selected -> comment task created -> proposal received -> pending approval bridge -> preview/diff checked -> approve or revise -> ledger row -> export/reopen state
```

Before coding, turn the chosen slice into a contract: route/screen, primary object, entry state, main action, data/fixture source, states included/deferred, responsive behavior, commands, screenshots/browser evidence, and risks.

Before final handoff, run `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: the user should know the current object, state, risk, next action, recovery path, and evidence within five seconds.

## Workspace Information Architecture

Default desktop shell:

| Region | Job | Notes |
| --- | --- | --- |
| Top bar | Project, page, agent connection, verification/export actions | Keep status factual and visible. |
| Left rail | Project map, pages, layers, assets | Selection must mirror canvas and inspector. |
| Center | Canvas, preview, overlays, breakpoint controls | This is the primary work surface. |
| Right panel | Inspector, comments/tasks, proposal/diff, verification | Use tabs or mode switch when space is tight. |
| Bottom/status bar | Zoom, viewport, selection, warning count, ledger summary | Keep low height and stable. |

Do not make the first screen a marketing hero. If no project is open, show a launcher with recent projects, open-folder action, privacy/connection status, and an honest empty state.

## Required Screen Patterns

### Project Launcher

Must show:

- recent projects with path and last opened time;
- open folder action;
- agent connection/scopes status;
- local/privacy status;
- agent/daemon connection status;
- onboarding state when no projects exist.

States:

- no recent projects;
- folder permission denied;
- indexing unavailable;
- daemon disconnected;
- unsupported folder.

Primary actions:

- open folder;
- reconnect local daemon;
- view privacy/settings.

### Design Search Report

Must show:

- discovered pages/routes;
- components;
- assets/images/fonts/3D/code;
- warnings with source path and reason;
- scan duration or freshness;
- import candidates.

States:

- scan running;
- no pages found;
- partial scan;
- skipped assets;
- stale scan;
- permission failure.

Pattern:

- summary row for counts;
- grouped result list or table;
- warning drawer/panel;
- import review action.

### Import Review

Must show:

- import candidates;
- source path;
- confidence or detection reason;
- dependencies;
- unsupported items;
- approval action.

States:

- needs approval;
- skipped item;
- conflict with existing page;
- import failed;
- import completed.

### Studio Workspace

Must show:

- canvas;
- project map/layers/assets;
- inspector;
- comments/tasks;
- agent proposals;
- verification/export access;
- ledger/history summary.

States:

- no project;
- no page selected;
- page loading;
- render error;
- agent disconnected;
- proposal pending;
- verification failed.

Layout:

- center canvas gets the most space;
- left panel uses stable tree/list rows;
- right panel switches between inspector, task, proposal, and verification without hiding current selection context.

### Canvas Viewport

Must show:

- current page/frame;
- selection overlays;
- zoom/pan/fit;
- breakpoint or viewport selector;
- optional grid/rulers;
- anchored comments.

States:

- preview loading;
- missing asset;
- render error;
- stale preview;
- no selectable object;
- locked object.

Rules:

- selection overlay must remain readable at common zoom levels;
- anchors must avoid covering selected object handles when possible;
- missing assets need source path or reason.

### Object Inspector

Must show:

- selected object name/type;
- source file/path when available;
- properties/tokens/constraints;
- responsive values;
- locked/inherited/overridden states;
- reset or revert action.

States:

- no selection;
- multi-selection;
- locked;
- invalid value;
- unsaved change;
- proposal preview mode.

### Comment And Task Thread

Must show:

- anchor/object reference;
- comment text;
- task status;
- owner/agent;
- linked proposal or transaction;
- latest activity;
- resolve/reopen path.

States:

- draft;
- pending agent;
- agent failed;
- needs revision;
- ready for review;
- resolved;
- reopened.

Rule:

- comment is a task, not a passive note.

### Agent Proposal Panel

Must show:

- proposal summary;
- changed objects/files;
- risk level;
- checks/verification summary;
- preview/diff action;
- approve/revise/reject actions;
- linked comment task.

States:

- no agent connected;
- waiting for proposal;
- blocked;
- failed;
- ready to preview;
- stale proposal;
- applied;
- rejected.

Rule:

- AI output is proposal-only until preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery are visible.
- Agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, and failure/recovery handling must be visible or honestly marked blocked/deferred.

### Preview And Diff

Must show:

- before/after visual diff;
- code/file diff when relevant;
- viewport variants;
- acceptance checks;
- verification result;
- approve/revise path.

States:

- diff unavailable;
- preview failed;
- verification failed;
- stale base revision;
- conflict;
- accepted.

### Verification

Must show:

- grouped pass/warn/fail checklist;
- worst state first;
- screenshot/viewport evidence when available;
- command/test evidence when available;
- failure reason and retry path.

States:

- not run;
- running;
- passed;
- warnings;
- failed;
- stale result.

### Ledger And History

Must show:

- transactions;
- actor/source;
- linked comment/proposal;
- timestamp;
- result;
- rollback/reopen action.

States:

- empty history;
- rollback unavailable;
- conflict;
- restored revision.

Rule:

- "done" requires a ledger/history row for agent-applied changes.

### Export And Share

Must show:

- export target/path;
- artifact list;
- warnings;
- generated result/open action;
- partial export state.

States:

- pending;
- failed;
- partial;
- completed;
- permission denied.

## Cross-Surface State Matrix

| State | Must appear in |
| --- | --- |
| Agent disconnected | top bar, proposal panel, settings |
| Project not imported | launcher/search report/workspace empty |
| Asset skipped | search report, import review, canvas warning |
| Object selected | canvas, layer tree, inspector, comments |
| Comment pending agent | task thread, proposal panel, status/ledger |
| Proposal ready | proposal panel, preview/diff entry, linked task |
| Verification failed | proposal panel, verification panel, approve disabled/requires override |
| Change applied | task thread, canvas/preview, ledger/history |
| Export failed | export panel, status bar/inline alert |

## Component Contracts

| Component | Required behavior |
| --- | --- |
| Tree row | fixed height, selected/focused/hover/disabled/warning/locked states |
| Toolbar icon button | accessible name, tooltip, focus-visible, disabled/loading |
| Inspector field | label, value, unit, token binding, invalid/locked/reset states |
| Task card | status, anchor, linked tx/proposal, latest message, action |
| Proposal card | summary, risk, changed files/objects, checks, preview action |
| Verification checklist | pass/warn/fail grouping, failure reason, retry |
| Diff viewer | before/after, viewport tabs, code/visual mode, stale state |
| Decision cockpit | question, comparison, evidence, risk, approve/revise/reject, after-state |
| Ledger row | actor, transaction, linked comment, time, result, rollback |
| Inline alert | reason, affected object/path, action; do not hide actionable failures in toast only |

## Layout Recipes

### Full Studio

Use when a project and page are open.

```text
top bar
left project/layers panel | central canvas | right inspector/proposal panel
bottom status bar
```

### Review Mode

Use when proposal/diff is primary.

```text
top bar with proposal status
left changed objects/files
center before/after preview
right verification + approve/revise
bottom ledger/context
```

### Import Mode

Use during scan/import.

```text
top progress/status
left source groups
center candidate table/list
right warnings/dependencies/approval
```

### Mobile/Small Width

Use review/status first, not full editing.

```text
top project/status
main selected preview or task/proposal
bottom tabs: canvas, layers, inspector, tasks
drawers for details
```

## Copy And Status Language

Prefer factual UI copy:

- "Agent disconnected"
- "Project not imported"
- "3 assets skipped"
- "Proposal needs approval"
- "Verification failed"
- "Rollback unavailable"
- "Export completed"
- "Sample proposal"
- "Ledger row created"

Avoid:

- "AI fixed it"
- "Magic applied"
- "Everything ready"
- "Looks good"
- "Fully imported" unless registry evidence exists.
- "Done" before accepted diff, closed task/comment, and ledger/history evidence.

## Responsive Behavior

- Desktop is the primary authoring surface.
- Tablet may collapse left/right panels into drawers, but canvas and current task stay visible.
- Mobile can prioritize review/comment/status flows; deep editing may be limited but must not break.
- Touch targets should remain usable and toolbars should not wrap into unreadable rows.

## QA Checklist

- Product loop is visible.
- Implementation slice contract is explicit and matches the rendered UI.
- Current project, page, object, task, proposal, and verification status are findable.
- Agent connection truth is visible.
- Empty/loading/error/permission/disconnected states exist for the current slice.
- Selection mirrors across canvas, layer tree, inspector, comments, and ledger where relevant.
- Proposal cannot appear applied without approval and ledger evidence.
- Proposal review shows comparison, evidence, risk, decision actions, after-state, and ledger/recovery path.
- Warnings include affected source path/object/reason.
- Mock/sample states are labeled honestly.
- Keyboard focus and tooltips work for icon-heavy surfaces.
- Desktop/tablet/mobile layouts do not overlap or clip.
