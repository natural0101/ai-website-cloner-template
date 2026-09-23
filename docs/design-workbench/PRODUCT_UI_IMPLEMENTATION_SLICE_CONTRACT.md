# Product UI Implementation Slice Contract

Use this in Phase 9 of `UNIVERSAL_DESIGN_RUNBOOK.md`, before coding or while turning a plan into a buildable product UI change. It prevents agents from shipping isolated decorative fragments by requiring a coherent slice with route, object, data, states, actions, responsive behavior, and evidence.

A slice is not a component. A slice is a small product workflow that can be opened, inspected, acted on, and verified.

Final handoff must preserve the slice. `Product read`, `Workflow improved`, and `Implementation slice contract` should reference the same route/screen, primary object, workflow/actions, data/fixture truth, and states from the working brief. Generic `done`, `improved`, `implemented`, or component-only wording is not a valid slice report.

## Slice Contract

Before implementation, answer:

```text
Slice name:
Route/screen:
User job:
Primary object:
Entry state:
Main action:
Secondary actions:
Data/fixture source:
States included:
States deferred:
Components touched:
Interaction model:
Copy/status contract:
Decision/review cockpit:
Responsive behavior:
Accessibility checks:
Verification commands:
Screenshots/browser evidence:
Remaining risks:
```

## Minimum Coherent Slice

Every serious product UI slice needs:

- one reachable route or screen;
- one primary object visible in the UI;
- one main workflow from entry to result;
- at least one non-happy-path state;
- local action feedback for pending/failure/success;
- source/sample/demo/disconnected truth;
- responsive behavior for desktop and one constrained viewport;
- final report evidence.

Do not call it a slice if it is only:

- a static card grid;
- a new visual component with no route or state;
- a mock screen with no data/source label;
- a table with no empty/loading/error state;
- a proposal panel with no preview/diff/verification/action path;
- styling changes with no browser evidence.

## Slice Types

| Surface | Useful first slice | Must include |
| --- | --- | --- |
| Dashboard | filter -> select row -> inspect detail -> retry/export | source/freshness, empty/loading/error, selected detail, recovery |
| Admin | records -> edit/approve/destructive action -> audit | validation, permission, confirmation, after-state, restore/history |
| SaaS workflow | create/review -> validate -> submit -> result | progress, validation, saved/failed state, next action |
| AI design studio | select object -> task -> proposal -> review | canvas/object, task, proposal, status, proof/sample label |
| Canvas/editor | select object -> edit property -> preview -> undo | selection mirror, inspector state, pending/error, history |
| Data tool | query/filter -> compare rows -> export/retry | query state, stale/partial result, units/source, export evidence |
| Product website | first viewport -> proof/product section -> action | real product signal, media fallback, mobile nav, proof honesty |
| 3D/WebGL | load model -> inspect/control -> fallback | loading/error, reduced motion, mobile/GPU fallback, asset path |

For ForgeStudio-like work, choose the matching `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` slice and then fill this universal contract.

## Data And Fixtures

A slice must be honest about its data:

- real API/local file/source when available;
- fixture/sample/demo label when backend is incomplete;
- disconnected/unavailable state when integration is absent;
- no fake metrics, screenshots, users, imported assets, agent activity, or proof.

Fixtures are acceptable when they exercise the same UI states the real backend will use.

## State Budget

If time is limited, do not attempt every state. Pick the states that prove the slice is real:

```text
loaded + one action pending + one failure/recovery + one constrained viewport
```

For review/approval surfaces, minimum state budget is:

```text
proposal/record ready + evidence visible + risk/blocker visible + approve/revise/reject or equivalent + after-state/ledger preview
```

For dashboards/data tools, minimum state budget is:

```text
loaded + empty filtered result + selected detail + export/retry failed or stale source
```

## Implementation Order

Build in this order:

1. Route/screen entry.
2. App shell and layout zones.
3. Primary object and data source/fixture label.
4. Core workflow action.
5. State coverage and recovery.
6. Copy/status language.
7. Decision/review cockpit when relevant.
8. Component polish and responsive behavior.
9. Verification and evidence capture.

Do not start with decorative polish before the slice can be used.

## Stop Conditions

Stop expanding the scope when:

- the route is reachable;
- the primary object is visible;
- the main action works or has an honest unavailable state;
- the required non-happy state is represented;
- desktop and constrained viewport do not break;
- commands/screenshots are captured or the limitation is reported.

Then report remaining risks instead of inventing more UI.

## QA Checks

Before final handoff, verify:

- slice route/screen can be reached;
- primary object and current status are visible;
- data/source/sample truth is visible;
- main action has pending/success/failure/recovery behavior;
- key components have state specs or a named reason for custom behavior;
- decision/review surfaces include comparison, evidence, risk, action, after-state, and audit/recovery;
- at least desktop wide and one constrained viewport were checked when possible;
- final report names commands, screenshots/browser checks, and remaining risks.
- final report `Product read`, `Workflow improved`, and `Implementation slice contract` still match the working brief's primary object, workflow/actions, and data/fixture truth.

## Output Contract

Use this in planning and final reports:

```text
Implementation slice:
Route/screen:
Primary object:
User job:
Data/fixture source:
Workflow covered:
States covered:
States deferred:
Interaction/copy/decision contracts:
Components touched:
Responsive behavior:
Commands:
Screenshots/browser evidence:
Remaining risks:
Verdict:
```
