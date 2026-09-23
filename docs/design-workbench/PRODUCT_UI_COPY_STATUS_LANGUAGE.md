# Product UI Copy And Status Language

Use this after `PRODUCT_UI_INTERACTION_MODEL.md` and before visual polish, component sourcing, or final QA. It turns actions and states into factual labels, inline messages, empty states, confirmations, and reportable evidence. For approval, comparison, triage, and proposal-review screens, pair it with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.

Good product UI copy is not marketing flavor. It tells the user what object is affected, what state it is in, why it matters, what can be done next, and what evidence exists.

## Copy Contract

Before implementation, answer for every primary action, major pane, and reusable status component:

```text
Object:
State:
User-facing label:
Reason/details:
Next action:
Evidence/source:
Inline vs toast:
Sample/demo/disconnected label:
Blocked words:
```

## Status Anatomy

Strong status language includes:

- object: project, page, row, proposal, asset, task, export, connection, verification;
- state: empty, loading, running, pending, ready, warning, failed, stale, applied, blocked, disconnected;
- reason: permission, missing source, validation error, skipped asset, stale base, failed command, unavailable backend;
- next action: retry, reconnect, review, approve, revise, reset, open result, request access;
- evidence: source path, timestamp, actor, command, artifact path, diff, ledger row, sample/demo label.

Weak status language hides the object or proof:

- "Done"
- "Success"
- "Ready"
- "Looks good"
- "AI fixed it"
- "Everything synced"
- "Fully imported" without registry/import evidence

## State Language Matrix

| State | Good pattern | Avoid |
| --- | --- | --- |
| Empty | "No proposals yet. Add a comment to request one." | "Nothing here" |
| Loading | "Scanning 12 project files..." | global spinner with no object |
| Pending | "Exporting 3 selected records..." | "Working..." |
| Success | "Export completed: report.csv" | "Success" |
| Error | "Export failed: permission denied. Retry or choose another folder." | "Something went wrong" |
| Warning | "2 assets skipped: unsupported SVG filters" | color-only warning |
| Stale | "Proposal is stale: page changed after preview" | hidden conflict |
| Disabled | "Approve disabled until verification runs" | disabled button with no reason |
| Disconnected | "Agent disconnected. Reconnect local daemon." | fake online status |
| Sample/demo | "Sample proposal" or "Demo metrics" | proof-like fake data |

## Placement Rules

- Use inline alerts for actionable failures, validation, permissions, disconnected systems, stale data, skipped assets, and failed exports.
- Use toasts only for transient confirmations or background completion when the affected object is still visible elsewhere.
- Put status near the object it affects: row, panel, inspector field, proposal, export item, or connection control.
- Keep global status bars factual and compact: current project, connection, selected object, warnings, verification/export summary.
- Do not rely on color alone; pair semantic color with icon, label, or reason.

## AI Design App Language

For ForgeStudio-like apps, preserve the product truth:

```text
comment/task -> agent running -> proposal ready -> preview/diff -> verification -> approve/revise/reject -> transaction -> ledger/export
```

Required labels:

- "Agent disconnected"
- "Task pending agent"
- "Proposal ready"
- "Proposal needs approval"
- "Preview failed"
- "Verification failed"
- "Approve disabled until verification passes"
- "Sample proposal"
- "Applied in transaction"
- "Ledger row created"
- "Rollback unavailable"

Never claim:

- "AI changed the project" before approved transaction and ledger evidence;
- "Done" before accepted diff, closed task/comment, and ledger/history row;
- "Fully imported" before import registry or equivalent source evidence;
- real agent status when the backend is mocked, disconnected, or unavailable.

Use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` to place these labels inside a full review surface with decision question, comparison, evidence, risk, approval/rejection, after-state, and ledger/recovery.

## Dashboard, Admin, And Data Tool Language

Operational UI needs source-aware copy:

- name data source, time range, freshness, filter scope, and units when metrics or tables drive decisions;
- label sample data as sample/demo in the same region as the data;
- use row-local failure language for retries, partial exports, permission failures, and stale records;
- show selected count and object type for bulk actions;
- describe destructive consequences precisely.

Examples:

```text
12 jobs shown from Local fixture, updated 14:32
3 selected invoices will be archived
Filtered result is empty. Clear filters or change date range.
Export failed for 2 rows. Download partial export or retry failed rows.
```

## Forms, Confirmations, And Risk

Forms and risky actions must name the consequence:

- use field-level validation with reason and expected format;
- distinguish unsaved, saving, saved, failed, and conflict;
- show locked/permission reasons and access path;
- for destructive actions, name object count/type and recovery availability;
- for irreversible actions, require stronger confirmation and audit/ledger entry.

Avoid generic confirmation copy like "Are you sure?" when the action has real consequence.

## Visual And Layout Rules

- Keep status labels short enough for fixed-width controls; move detail into helper text, inline alert, tooltip, or detail pane.
- Use stable badge widths or predictable truncation for repeated status badges.
- Prefer concrete nouns over adjectives: "Verification failed" beats "Bad result".
- Use sentence case for messages and compact title case only for short badge labels if the local UI already does.
- Do not put long explanatory text inside dense buttons, chips, tabs, or toolbar controls.

## QA Checks

Before final handoff, verify:

- every primary action has a specific pending, success, failure, and recovery message;
- every major empty/error/disconnected/stale state gives reason and next action;
- every proof-like claim has source/evidence or a sample/demo label;
- AI proposal, verification, approval, transaction, and ledger states use distinct labels;
- no vague "done/success/ready" state is the only feedback for important work;
- screenshot/browser evidence includes at least one critical status or failure state when relevant.

## Output Contract

Use this in planning, implementation notes, or final QA:

```text
Copy/status contract:
Primary status labels:
Empty/loading/error copy:
Pending/success/failure copy:
Recovery copy:
Sample/demo/disconnected labels:
AI/proof/data honesty copy:
Inline vs toast policy:
Blocked vague copy removed:
QA evidence:
```
