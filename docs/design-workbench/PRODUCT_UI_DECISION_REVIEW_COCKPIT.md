# Product UI Decision And Review Cockpit

Use this after workflow, information architecture, interaction model, and copy/status language are defined, and before component sourcing or visual polish. It turns dashboards, admin screens, proposal reviews, approvals, and AI workbench panels into decision surfaces instead of decorative collections of cards.

A decision/review cockpit helps a user answer:

```text
What am I deciding?
What changed?
What are my options?
What evidence supports each option?
What is risky or blocked?
What happens after I choose?
How can I recover or audit the choice?
```

## Cockpit Contract

Before implementation, answer:

```text
Decision question:
Primary object:
Options:
Recommended/default option:
Comparison axes:
Evidence:
Risk/impact:
Confidence/source limits:
Primary decision action:
Secondary actions:
Blocked/disabled decision states:
After-decision state:
Audit/ledger/recovery path:
```

## Anatomy

A strong decision cockpit includes:

- decision header: object, current status, owner/source, time/freshness;
- comparison surface: table, diff, side-by-side preview, checklist, or ranked option list;
- evidence panel: source, command, screenshot, test, metric, timestamp, actor, artifact, or linked task;
- risk panel: failed checks, conflicts, stale data, permission limits, irreversible consequences;
- action zone: approve, revise, reject, retry, rollback, export, assign, or request access;
- after-state preview: what changes after approval or completion;
- history/audit link when trust, recovery, or compliance matters.

## Decision Surface Patterns

| Surface | Strong pattern | Avoid |
| --- | --- | --- |
| Dashboard triage | prioritized list/table, filters, risk/status, next action | metric cards with no decision |
| Admin approval | selected record, change summary, permissions, audit, confirm/revert | save/destructive actions with equal weight |
| AI proposal review | linked task, changed objects/files, preview/diff, verification, approve/revise/reject, ledger | chat-only answer or "AI fixed it" |
| Data investigation | query/filter scope, source freshness, compared records, anomalies, export/retry | charts without source or action |
| Import review | candidates, source paths, dependencies, conflicts, approve/skip | silent import or vague "ready" |
| Export/share | target, artifact list, warnings, partial/failure, open result | "exported" without artifact evidence |

## Comparison Rules

Use comparison whenever the user must choose, approve, or trust a change.

Good comparison axes:

- before/after;
- option A/B/C;
- expected vs actual;
- current vs proposed;
- passed/warn/failed checks;
- affected objects/files/records;
- cost, risk, impact, time, freshness, owner, permission, reversibility.

Rules:

- Put the compared objects in the same visual rhythm so differences are scannable.
- Keep the current object and proposed change visible at the same time when possible.
- Show the worst risk first in review/approval flows.
- Do not hide critical differences behind hover-only UI.
- Use tables/lists for repeated comparisons; use cards only for discrete choices.

## Approval And Rejection Rules

Every approval surface must define:

- what is being approved;
- who or what proposed it;
- what evidence was checked;
- what blocks approval;
- what happens after approval;
- how rejection/revision works;
- where the decision appears in history/ledger.

For AI design apps:

```text
proposal -> preview/diff -> verification -> approve/revise/reject -> transaction -> ledger/export
```

Approval cannot be the first visible decision. Preview/diff and verification must be visible first, or the UI must show why they are unavailable.

## Evidence And Confidence

Evidence must be concrete:

- source path or data source;
- timestamp/freshness;
- actor/agent/session;
- command or verifier result;
- screenshot/artifact path;
- before/after diff;
- linked task/comment/proposal;
- transaction/ledger row.

If evidence is missing, label the state:

- sample/demo;
- disconnected;
- not run;
- unverified;
- unavailable;
- stale;
- partial.

Never invent confidence percentages, scores, screenshots, metrics, agent status, or proof-like labels.

## Layout Guidance

Desktop:

- keep decision header, comparison, evidence/risk, and actions visible together;
- use sticky local action row only when it does not cover evidence;
- keep destructive or irreversible actions visually separate.

Tablet:

- comparison stays primary;
- evidence/risk moves to drawer or stacked panel;
- action zone remains reachable without losing context.

Mobile:

- review/status first;
- one comparison at a time;
- evidence and action in clear steps;
- deep editing can move to desktop, but approval/rejection state must not break.

## Component Implications

Common cockpit components:

- decision header;
- option list or ranked queue;
- comparison table;
- before/after diff viewer;
- evidence row;
- risk checklist;
- approval action bar;
- revise/reject reason form;
- history/ledger row;
- rollback/reopen control.

Each reusable component still needs `COMPONENT_STATE_SPEC.md`, `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, and the nearest `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` pattern.

## QA Checks

Before final handoff, verify:

- the decision question is visible or obvious from the screen;
- the primary object and current status are visible;
- options or before/after states can be compared;
- evidence and source limits are visible;
- risks, failed checks, stale data, and blockers are not hidden;
- approve/revise/reject or equivalent actions are distinct;
- after-decision state and ledger/history/recovery path are visible when trust matters;
- screenshots/browser checks include the decision/review state, not only the loaded happy path.

## Output Contract

Use this in planning, implementation notes, or final QA:

```text
Decision/review cockpit:
Decision question:
Primary object:
Options/comparison:
Evidence:
Risk/impact:
Approval/rejection policy:
After-decision state:
Audit/ledger/recovery:
Responsive review behavior:
QA evidence:
```
