# AI Workbench Interaction Flows

Use this with `AI_DESIGN_APP_TRUSTED_VERTICAL.md` and `AI_DESIGN_APP_SCREEN_BLUEPRINT.md` for ForgeStudio-like products and any AI design app where a human supervises an external agent. The trusted vertical defines the source-of-truth objects and false-state bans; the screen blueprint names the surfaces; this file defines the object model, allowed state transitions, copy/status requirements, decision/review requirements, and proof requirements. Use `PRODUCT_UI_INTERACTION_MODEL.md` for the generic action contract, `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` for factual state language, `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for proposal/import/export/verification review surfaces, and `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` when choosing the next vertical slice to build.

## Core Objects

| Object | Meaning | UI must reveal |
| --- | --- | --- |
| Project | Local folder or workspace being edited | path, permission, scan freshness, privacy/connection state |
| Page | Imported visual surface, route, frame, or canvas | source path, viewport, render status, import state |
| VisualObject | Selectable layer/component/asset/text/3D object | name/type, source, selection, lock, responsive constraints |
| Asset | Image, font, video, GLB, code asset, token file | source path, loaded/skipped/missing state, dependency links |
| CommentTask | Anchored feedback that becomes work | anchor, status, owner/agent, linked proposal/transaction |
| AgentSession | External AI/client connection | connected/disconnected/unhealthy, provider, permissions |
| ScopeGrant | What the external agent can actually do | granted scopes, missing scopes, request/grant state, denial reason |
| Proposal | Agent-suggested change set | changed objects/files, risk, checks, preview/diff status |
| PendingApprovalBridge | Cross-process/live-session handoff | pending proposal source, poll/merge/apply path, stale/conflict state |
| VerificationRun | Evidence that the proposal was checked | command/screenshot/result, failures, stale status |
| DesignTransaction | Accepted mutation to canonical design state | actor, before/after, linked task/proposal, timestamp |
| LedgerEntry | Human-readable audit history | transaction result, rollback/reopen path, conflict state |
| ExportArtifact | Generated handoff/output | target path, file list, warnings, completion/partial/failure |

## Canonical Product Loop

```text
open project -> design search -> import review -> studio workspace -> select object -> anchored comment/task -> agent proposal -> preview/diff -> verification -> approve/revise/reject -> design transaction -> ledger/history -> export/reopen
```

Do not create a second hidden mutation path. The only normal path from agent output to real design state is:

```text
proposal -> preview/diff -> verification -> human approval -> DesignTransaction -> LedgerEntry
```

## Required Flows

### 1. Open Project To Import

Start state:

- no project, recent project, permission denied, or project reopened;
- agent connection may be disconnected and must be visible.

Flow:

1. User opens or reopens a folder.
2. App scans pages, components, assets, fonts, code, and 3D.
3. App shows a design search report with source paths and warnings.
4. User approves import candidates or skips them.
5. Workspace opens with imported pages and a visible import summary.

UI proof:

- real path or clearly labeled sample path;
- scan freshness/time;
- skipped asset reason;
- import candidate source;
- empty, loading, partial, permission, and unsupported-folder states.

### 2. Select Object To Comment Task

Start state:

- page rendered, no object selected, object selected, locked object, missing asset, or stale preview.

Flow:

1. User selects a visual object on canvas or in layers.
2. Selection mirrors in canvas, layer tree, inspector, comments, and status bar.
3. User creates an anchored comment.
4. Comment becomes a `CommentTask` with status `draft`, then `pending agent` or `ready for review`.

UI proof:

- selected object name/type/source;
- anchor position and object reference;
- task status and owner/agent;
- blocked path for locked or missing objects;
- no passive notes that cannot become trackable work.

### 3. Agent Proposal Lifecycle

Start state:

- no agent, agent disconnected, pending task, agent running, blocked, failed, or ready proposal.

Flow:

1. Agent receives a task.
2. Proposal is created with changed objects/files and risk notes.
3. Proposal remains proposal-only until reviewed.
4. User opens preview/diff.

UI proof:

- agent connection truth;
- proposal changed files/objects;
- linked comment task;
- blocked/failure reason;
- stale proposal state when base project changed.

### 4. Preview, Verification, Approval

Start state:

- proposal ready, preview loading, diff unavailable, verification not run, verification failed, stale base, conflict.

Flow:

1. User compares before/after visual diff and code/file diff when relevant.
2. Verification runs with screenshot, viewport, command, or checklist evidence.
3. Failure disables approval or requires an explicit override pattern.
4. User approves, requests revision, or rejects.
5. Approval creates a `DesignTransaction`.

UI proof:

- before/after preview;
- verification result grouped by pass/warn/fail;
- failure reason and retry path;
- decision question, evidence, risk, and after-approval state;
- approval state distinct from preview state;
- revision/reject path remains visible.

### 5. Ledger, Rollback, Reopen

Start state:

- empty history, transaction applied, rollback unavailable, conflict, restored revision.

Flow:

1. Applied transaction creates a ledger row.
2. Ledger links task, proposal, verification, actor, timestamp, and result.
3. User can reopen a task, inspect history, or rollback when supported.
4. Conflicts are explicit and never hidden in toast-only feedback.

UI proof:

- linked task/proposal/verification;
- accepted/rejected/revised result;
- rollback/reopen availability;
- conflict reason.

### 6. Export And Share

Start state:

- no export target, pending export, partial export, failed export, permission denied, completed.

Flow:

1. User chooses export/share target.
2. App shows artifact list and warnings.
3. Export result links back to project/page/transaction.
4. User can open result or inspect failure.

UI proof:

- target path;
- file/artifact list;
- partial/failure warnings;
- completed state only after actual result or honest mock label.

## Interaction Invariants

- A comment is a task, not decorative annotation.
- External AI is proposal-only until preview, verification, human approval, transaction, and ledger evidence exist.
- Agent connection/scopes are product state, not settings trivia: show disconnected, connecting, connected, unhealthy, missing-scope, and permission-denied states when relevant.
- Anchored comments must become trackable tasks or be labeled draft/comment-only; do not imply agent work without a comment-to-task bridge.
- Pending approvals must have a visible handoff path: proposal source, live-session/poll/merge state, approve/revise/reject action, and approve-back/apply result or blocker.
- Product failures must be inline near the affected pane/object; `console.warn`, optimistic toast-only success, or silent no-op is not acceptable for scan/import/agent/verification/export paths.
- "Done" means accepted diff, resolved/closed task, and ledger row.
- "Agent connected" must reflect a real connection or be labeled sample/mock.
- "Project imported" requires registry evidence: pages, components, assets, fonts, code, or explicit empty state.
- Verification results become stale when the base project or proposal changes.
- Approval must be reversible or at least auditable through history.
- Toasts are not enough for actionable failures; use inline failure states near the affected object or pane.
- Vague "success", "ready", or "AI fixed it" copy is not enough; labels must distinguish proposal, preview, verification, approval, transaction, ledger, and export states.
- Source paths, object names, timestamps, and failure reasons are proof surfaces, not optional decoration.
- Do not hide disconnected, permission, skipped asset, stale proposal, or rollback-unavailable states.

## Per-Screen Flow Requirements

| Screen | Must expose |
| --- | --- |
| Launcher | project path, recent/reopen, local privacy, agent/daemon state, permission errors |
| Design search | discovered surfaces, source paths, warnings, skipped assets, scan freshness |
| Import review | candidate approval, dependencies, unsupported/conflict states |
| Studio workspace | current project/page/object/task/proposal/verification/export state |
| Canvas | selection, anchors, render/missing asset/stale preview states |
| Inspector | source, token/constraint state, locked/invalid/pending values |
| Comment/task | anchor, status, linked proposal/transaction, resolve/reopen |
| Proposal | changed objects/files, risk, pending approval bridge, preview/diff, failure/stale/block states |
| Verification | pass/warn/fail, evidence, failure reason, retry/override policy |
| Ledger/history | transaction, actor, linked task/proposal, rollback/reopen/conflict |
| Export/share | target, artifacts, warnings, partial/failure/completed state |

## QA Gate

Before calling an AI workbench UI done, verify:

- the canonical loop is visible for the changed slice;
- every shown "applied" change has task/proposal/verification/ledger evidence;
- review surfaces expose decision question, comparison, evidence, risk, approve/revise/reject, after-state, and ledger/recovery;
- disconnected, failed, stale, permission, skipped, empty, and rollback-unavailable states are represented where relevant;
- selection mirrors across canvas, layers, inspector, comments, and ledger;
- screenshots/browser checks cover desktop and at least one constrained viewport;
- mock/sample state is explicitly labeled and never presented as real work.
- important status labels name the affected object, reason, next action, and evidence/sample truth where relevant.

## Output Contract

When planning or reporting, include:

```text
Flow slice:
Core objects affected:
Allowed transitions:
Blocked transitions:
Visible proof/evidence:
State coverage:
Copy/status language:
Decision/review cockpit:
Agent connection/scopes:
Comment-to-task bridge:
Pending proposal/approval bridge:
Failure/recovery handling:
Rollback/reopen path:
Mock/sample labels:
Verification artifacts:
Remaining interaction risks:
```
