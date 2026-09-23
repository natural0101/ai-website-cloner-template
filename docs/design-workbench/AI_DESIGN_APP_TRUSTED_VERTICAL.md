# AI Design App Trusted Vertical

Use this for ForgeStudio-like products and any AI-assisted design app where an external agent can propose visual changes. This document turns the product into a verified vertical, not a pile of attractive panels.

## Source Read

ForgeStudio `dev` was inspected on 2026-07-04 at:

```text
https://github.com/natural0101/ForgeStudio/tree/dev
fb23246912b64135b7a17c5765c822672f10c300
```

Important source files used for the product read:

```text
README.md
FORGE_PRODUCT_ROOT_SPEC.md
AGENT_MISSION.md
docs/PRODUCT_VERTICAL.md
docs/USER_JOURNEYS.md
apps/studio/src/App.vue
```

The strongest source lesson: ForgeStudio is a local-first AI design engineering supervisor. It is not a landing page, not a chat page, and not a decorative editor shell. The UI exists to make external-agent design work inspectable, reversible, and exportable.

## Trusted Vertical

The non-negotiable product path is:

```text
open local project folder
-> design search
-> import review
-> studio workspace
-> select visual object
-> anchored comment
-> agent task
-> proposal transaction
-> preview/diff
-> verification
-> human approve/revise/reject
-> DesignTransaction
-> ledger/history
-> export/reopen
```

Every AI-design-app screen should show where the user is in this path or state honestly why the path cannot continue.

## Source-Of-Truth Objects

Design the UI around these objects, not around generic cards:

| Object | UI proof |
| --- | --- |
| Project folder | local path, permission state, scan freshness, privacy/loopback status |
| Design search report | checked files, pages, components, assets, fonts, 3D, code, warnings |
| Import plan | candidates, source paths, confidence, dependencies, approval state |
| Page/canvas | source route/file, render state, viewport, missing asset state |
| Visual object | name, type, source, selection, lock, responsive constraints |
| Anchored comment | object id, page, coordinate, revision, latest message |
| Agent task | queue state, owner/session, retry/cancel, linked comment |
| Agent connection/scope grant | connected/disconnected/unhealthy, provider, MCP/daemon endpoint, granted scopes, missing permissions |
| Proposal | changed objects/files, transaction hash, risk, stale/conflict state |
| Pending approval bridge | proposal source, live-session handoff, approval queue, approve-back/apply result |
| Verification run | command, screenshot/checklist, pass/warn/fail, retry path |
| DesignTransaction | actor, preconditions, accepted diff, applied result |
| Ledger entry | task/proposal/verification links, timestamp, rollback/reopen |
| Export artifact | target path, file list/counts, warnings, open result |

If a UI cannot show the relevant proof object, it must label the state as sample, mock, blocked, disconnected, unavailable, or not imported.

## False-State Ban

Do not show or imply:

- "Agent connected" without a real session or explicit sample label.
- "Project imported" without pages/components/assets/code/3D registry or an honest empty report.
- "AI fixed it" without proposal, preview/diff, verification, human approval, transaction, closed task/comment, and ledger evidence.
- "Done", "ready", or "success" as the only feedback for a trust-heavy action.
- Hidden scene mutation outside the accepted transaction path.
- Toast-only handling for actionable failure, skipped asset, stale proposal, permission denial, or rollback conflict.
- "Agent task sent" when an anchored comment has no task/inbox/thread link.
- "Proposal pending" when the UI has no live-session/pending-approval bridge or approve-back/apply path.
- `console.warn`-only product failures that leave the user with no inline reason or recovery action.

## Product Shell Implications

The default shell for a ForgeStudio-like app is:

```text
top bar: project/page, agent/daemon status, verification/export entry points
left zone: project map, pages, layers, assets, warnings
center zone: canvas, preview/diff, selection, comment anchors
right zone: inspector, proposal, verification, decision cockpit
docked drawers: code/source, projects, overview, agent console, ledger/history
bottom/status: zoom, viewport, selection, warnings, save/reopen/export state
```

Panels are not decorative. Each panel must answer one of these questions:

- What object am I looking at?
- What changed or is about to change?
- What evidence proves it?
- What decision is required?
- What happens after the decision?
- How do I recover, reopen, export, or roll back?

## Implementation Slice Rule

A valid slice is a full path through several objects, not an isolated component. Prefer one of these:

1. Project launcher -> scan report -> import review -> workspace ready.
2. Workspace selection -> layer/object inspector -> anchored comment draft.
3. Comment task -> agent proposal -> preview/diff placeholder -> revise/approve decision.
4. Proposal -> verification -> accepted transaction -> ledger row.
5. Ledger/export -> artifact result -> reopen/rollback state.

Each slice needs:

```text
route/screen:
primary object:
real or sample data source:
included states:
blocked states:
proof/evidence:
decision question:
after-state:
recovery path:
agent connection/scopes:
comment-to-task bridge:
pending proposal/approval bridge:
failure/recovery handling:
commands/screenshots:
remaining risks:
```

## Visual Quality Standard

The product should feel like a serious creative engineering tool:

- dense, calm, and precise;
- readable at repeated-use density;
- canvas-first with quiet chrome;
- strong selection, focus, pending, conflict, and failed states;
- source paths and evidence treated as UI, not backend trivia;
- restrained motion for continuity and feedback;
- no marketing hero, fake AI gradients, fake proof dashboards, or decorative clutter inside the workbench.

Beauty here is trust made visible: hierarchy, alignment, object clarity, state truth, and fast decisions.

## QA Questions

Before calling an AI-design-app slice done, answer:

- Is the trusted vertical visible for the changed slice?
- Does every "applied" state have task, proposal, verification, approval, transaction, and ledger evidence where relevant?
- Are agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen persistence visible or honestly marked blocked/deferred?
- Are disconnected, permission denied, skipped asset, no pages found, stale proposal, verification failed, rollback unavailable, and export failed states represented when relevant?
- Can the user see the current object, next action, risk, evidence, and recovery path without reading docs?
- Are mock/sample states labeled honestly?
- Were screenshots/browser checks run for the actual screen and constrained viewport, or is the missing evidence reported as risk?
