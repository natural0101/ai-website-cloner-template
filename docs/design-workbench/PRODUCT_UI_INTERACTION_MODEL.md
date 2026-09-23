# Product UI Interaction Model

Use this after `PRODUCT_UI_INFORMATION_ARCHITECTURE.md` and before component styling, component sourcing, or visual polish. It turns routes and panes into actions, transitions, pending states, failures, recovery, and proof. After defining transitions, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` to turn those states into factual labels and messages, and `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for approval, comparison, and review surfaces.

Good product UI is not a static screen. Every important action needs a visible before, during, after, failure, and recovery path.

## Interaction Contract

Before implementation, answer:

```text
Primary action:
Secondary actions:
Trigger:
Actor:
Preconditions:
Pending state:
Success result:
Failure state:
Recovery path:
Undo/rollback/reopen:
Proof/evidence:
Disabled/permission state:
Keyboard path:
Copy/status language:
Decision/review cockpit:
```

## Action Model

For every action, define the transition:

```text
idle -> ready -> pending -> success | warning | error | conflict -> retry | undo | rollback | reopen
```

Not every action needs every state, but every important action must define:

- what enables it;
- where progress appears;
- what changes after success;
- what happens on failure;
- how the user recovers;
- what proof/evidence is shown when trust matters.

## Common Product Actions

| Action | Must show | Avoid |
| --- | --- | --- |
| Navigate | active destination, return path, unsaved warning when relevant | route change with lost selection and no recovery |
| Select | selected object mirrored in related panes | selection visible only in one panel |
| Search/filter | active filters, empty filtered result, reset | stale results that look current |
| Create/edit/save | validation, pending, success, unsaved changes, failed save | vague "saved" copy without state |
| Bulk action | selected count, affected type, confirmation, partial failure | applying to hidden or ambiguous items |
| Destructive action | consequence, confirmation, permission, recovery/restore | destructive button next to normal save |
| Import/connect | source, permission, progress, skipped items, retry | silent skipped files or fake connection |
| Export/share | target, artifacts, progress, partial/failure, open result | "exported" without artifact evidence |
| Review/approve | proposal, diff, verification, approve/revise/reject, ledger | approval before preview and verification |
| Retry/rollback | last failed action, reason, safe target, result | toast-only failure with no local retry |

## Async And Pending States

Async actions need a local pending state near the affected object, not only a global spinner.

Use:

- button loading for direct control feedback;
- row/panel pending state when a specific object is changing;
- skeleton for first load;
- progress list for multi-file import/export;
- inline alert for actionable failure;
- toast only for transient confirmation or background completion.

Never disable a whole surface without explaining why and how to recover.

## Validation And Forms

For forms, inspectors, settings, and edit panels:

- validate close to the field;
- show units, constraints, inherited/overridden values, and locked states;
- keep save/cancel/revert visible;
- distinguish unsaved, saving, saved, failed, and conflict;
- restore focus after dialogs/drawers close;
- warn before navigation when unsaved changes would be lost.

## Destructive And Risky Actions

Risky actions need an explicit policy:

| Risk | Required pattern |
| --- | --- |
| reversible low risk | inline undo or history entry |
| bulk change | selected count, object type, partial failure path |
| destructive | confirmation dialog or typed confirmation for high impact |
| permission-sensitive | disabled state with reason and request/access path |
| irreversible | strongest confirmation, clear consequence, audit entry |
| AI/agent-driven | proposal-only until preview, verification, human approval, transaction, and ledger |

Do not hide risky outcomes behind generic "Are you sure?" copy.

## Proof And Ledger

Use proof/evidence when an action changes trust:

- source path or data source;
- actor;
- timestamp;
- command or verifier result;
- before/after diff;
- artifact path;
- linked task/comment/proposal;
- ledger/history entry;
- rollback or rollback-unavailable reason.

If proof is unavailable, label the state as sample, demo, disconnected, unverified, or not run.

For exact UI labels, empty/error copy, AI/proof language, sample/demo labels, and toast-vs-inline placement, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
For the surrounding comparison, evidence, risk, approval, after-state, and audit/recovery surface, use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.

## AI Design App Actions

For ForgeStudio-like apps, preserve this transition:

```text
comment/task -> agent running -> proposal -> preview/diff -> verification -> approve/revise/reject -> DesignTransaction -> ledger/export
```

Rules:

- agent output is proposal-only;
- preview is not approval;
- verification failure disables approval or requires an explicit override policy;
- "applied" needs transaction and ledger evidence;
- comment status changes only through the approved workflow;
- stale proposal is visible when the base project changes;
- disconnected agent, missing scope, skipped asset, and rollback-unavailable states are first-class UI.

## Motion For Interactions

Motion is allowed when it explains:

- selection continuity;
- panel/drawer origin;
- pending to success/error;
- diff reveal;
- object movement;
- undo/rollback restoration.

Avoid motion that delays repeated work, hides the final state, or competes with reading dense data.

## Output Contract

Use this before implementation:

```text
Interaction slice:
Primary action:
Secondary actions:
Allowed transitions:
Blocked transitions:
Pending states:
Success states:
Failure states:
Recovery/undo/rollback:
Proof/evidence:
Copy/status language:
Decision/review cockpit:
Permission/disabled states:
Keyboard/focus behavior:
Motion policy:
QA evidence:
```
