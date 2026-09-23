# AI Workbench Implementation Slices

Use this after `AI_DESIGN_APP_SCREEN_BLUEPRINT.md` and `AI_WORKBENCH_INTERACTION_FLOWS.md` when building or improving a ForgeStudio-like AI design app. This file turns the abstract product loop into concrete vertical slices an agent can implement, inspect, and QA. Use `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` to turn the chosen slice into a route/screen/object/state/evidence contract, and use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` for each slice's microcopy and status labels.

Do not build every panel at once. Build the smallest slice that preserves the real state machine.

## Slice 1: Project Launcher And Import

Goal:

```text
no project -> open folder -> scan report -> import review -> workspace ready
```

Required UI:

- launcher with recent projects, open folder, local/privacy status, agent/daemon status;
- agent connection/scopes strip with disconnected, connecting, connected, missing-scope, and permission-denied states when the app supports external agents;
- scan report with pages, components, assets, fonts, code, 3D, warnings;
- import review with candidate list, source paths, dependencies, skipped/unsupported items;
- clear transition into workspace after import.

Required states:

- no recent projects;
- folder permission denied;
- scan running;
- no pages found;
- partial scan;
- skipped asset with source path and reason;
- import conflict;
- import completed.

Microcopy:

- "Open local project"
- "Scanning project"
- "3 assets skipped"
- "Import needs review"
- "Project imported"

Evidence:

- project path or clearly labeled sample path;
- scan freshness or duration;
- skipped item reason;
- import candidate source.

QA:

- launcher screenshot;
- scan running/partial screenshot;
- import review screenshot with warnings;
- no "fully imported" copy unless registry evidence exists.

## Slice 2: Workspace Selection And Inspector

Goal:

```text
workspace ready -> select page -> select object -> inspect source/properties -> handle locked/missing state
```

Required UI:

- top bar with current project, page, agent status, verification/export entry;
- left panel with project map, pages, layers, assets, warning badges;
- center canvas/preview with zoom, breakpoint, selection overlay;
- right inspector with selected object name, type, source, tokens/constraints, responsive values;
- bottom/status strip with zoom, viewport, selected object, warning count, ledger summary.

Required states:

- no page selected;
- page loading;
- render error;
- missing asset;
- object selected;
- locked object;
- multi-selection;
- inspector invalid value;
- unsaved/pending value.

Microcopy:

- "No page selected"
- "Render failed"
- "Asset missing"
- "Locked object"
- "Selection: Hero CTA"

Evidence:

- selection mirrors canvas, layer row, inspector, and status strip;
- source path is visible for selected object when available;
- missing asset names the affected object/path.

QA:

- selected-object screenshot;
- render/missing asset screenshot;
- keyboard focus through layers, canvas tools, inspector controls;
- desktop narrow check for panel clipping.

## Slice 3: Comment Task To Agent Proposal

Goal:

```text
selected object -> anchored comment -> task created -> agent pending/failed/ready proposal
```

Required UI:

- visible comment anchor linked to selected object;
- comment composer with draft and submit state;
- task card with status, owner/agent, anchor, latest activity;
- explicit comment-to-task bridge showing task id/thread/inbox status or an honest blocked/sample label;
- proposal panel with no-agent, pending, failed, blocked, ready states.

Required states:

- comment draft;
- task pending agent;
- agent disconnected;
- agent failed;
- proposal blocked;
- proposal ready;
- task needs revision;
- task resolved/reopened.

Microcopy:

- "Comment anchored to Button / primary CTA"
- "Waiting for agent"
- "Agent disconnected"
- "Proposal ready"
- "Needs revision"

Evidence:

- task links selected object and source;
- proposal links task id/comment;
- agent connection/scopes state is visible before the task is sent;
- failure reason visible inline, not only in toast;
- mock proposal labeled sample when backend is incomplete.

QA:

- anchored comment screenshot;
- agent disconnected screenshot;
- proposal ready screenshot;
- no "AI fixed it" before preview/diff and ledger.

## Slice 4: Proposal Preview And Diff

Goal:

```text
proposal ready -> preview/diff -> verification -> approve/revise/reject
```

Required UI:

- proposal summary with actor, linked task, changed objects/files, risk;
- pending proposal/approval bridge with live-session/poll/merge/apply status when the proposal comes from a daemon or external process;
- before/after visual preview;
- code/object diff when relevant;
- viewport selector;
- verification summary;
- approve, revise, reject actions.

Required states:

- diff unavailable;
- preview loading;
- preview failed;
- verification not run;
- verification running;
- verification failed;
- stale proposal;
- conflict;
- approved/rejected/needs revision.

Microcopy:

- "Proposal needs approval"
- "Diff unavailable"
- "Verification failed"
- "Base changed since proposal"
- "Request revision"

Evidence:

- changed objects/files list;
- before/after comparison;
- verification result and failure reason;
- approve/revise/reject path shows whether approve-back/apply succeeded, is pending, or is blocked;
- approve disabled or override policy visible when verification fails.

QA:

- proposal/diff screenshot;
- verification failed screenshot;
- stale proposal/conflict screenshot when applicable;
- approval cannot apply without visible diff/verification policy.

## Slice 5: Ledger, Recovery, Export

Goal:

```text
approved proposal -> DesignTransaction -> ledger row -> export/share -> reopen/rollback
```

Required UI:

- ledger/history list with actor/source, linked task/proposal, timestamp, result;
- rollback/reopen action when supported;
- export panel with target path, artifact list, warnings, progress, result;
- inline failure/recovery state for export/share/reopen instead of silent no-op or toast-only failure;
- status strip showing applied transaction and export state.

Required states:

- empty history;
- transaction applied;
- rollback unavailable;
- conflict;
- restored revision;
- export not configured;
- export pending;
- export partial;
- export failed;
- export completed;
- permission denied.

Microcopy:

- "Transaction applied"
- "Rollback unavailable"
- "Export failed"
- "Partial export"
- "Export completed"

Evidence:

- accepted proposal creates a ledger row;
- ledger links task, proposal, verification, actor, timestamp;
- export result names target path and artifacts;
- failure states explain cause and next action.

QA:

- ledger screenshot with linked task/proposal;
- export failed and completed screenshots;
- reopen/rollback state screenshot;
- no "done" without ledger evidence.

## Slice Selection Guide

| Situation | Build first |
| --- | --- |
| No product shell exists | Slice 1, then Slice 2 |
| Workspace exists but feels fake | Slice 2 and Slice 3 |
| Agent workflow is vague | Slice 3 and Slice 4 |
| Review/approval is unsafe | Slice 4 |
| Product lacks trust/recovery | Slice 5 |
| Time is very limited | Minimal end-to-end: import summary -> selected object -> task -> proposal -> diff placeholder -> verification state -> ledger row |

## Minimum Coherent Prototype

If backend integration is incomplete, build an honest mock prototype:

```text
sample project -> sample scan report -> selected sample object -> sample anchored task -> sample proposal -> preview/diff placeholder -> verification sample result -> ledger sample row -> export sample state
```

Rules:

- every sample/mock label must be visible;
- sample data must never imply real import, real agent connection, real verification, or real export;
- the same UI states should be reusable when real backend data arrives.

## Output Contract

When planning or reporting, include:

```text
Chosen slice:
Implementation slice contract:
Reason:
Core objects:
Required panes:
States implemented:
States deferred:
Evidence/proof shown:
Agent connection/scopes:
Comment-to-task bridge:
Pending proposal/approval bridge:
Failure/recovery handling:
Mock/sample labels:
Verification screenshots:
Remaining risk:
```
