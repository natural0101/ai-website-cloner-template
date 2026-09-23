# Product UI Information Architecture

Use this after the product brief, surface blueprint, and workflow map, and before `PRODUCT_UI_INTERACTION_MODEL.md`, design-system styling, or component sourcing. It turns a product idea into routes, navigation, panes, object hierarchy, decision/review zones, and recovery paths.

Good IA lets an agent build a coherent app instead of a set of attractive screens.

## IA Contract

Before layout work, answer:

```text
Primary object:
Secondary objects:
Core loop:
Entry points:
Persistent navigation:
Main work zone:
Context zones:
Detail/review zones:
Decision/review cockpit:
Global actions:
Local actions:
Recovery/history:
Responsive model:
```

## Object Model

Name the things the UI is about before naming screens.

Examples:

| Surface | Primary object | Secondary objects |
| --- | --- | --- |
| Dashboard | record, alert, account, metric group | filter, saved view, export, owner |
| Admin | user, role, permission, setting | audit row, validation error, destructive action |
| SaaS workflow | project, document, request, order | step, checklist item, reviewer, output |
| AI design studio | project, page, canvas object, proposal | comment, task, diff, verification row, ledger transaction |
| Canvas editor | frame, layer, asset, selection | tool, property group, history entry |
| Data tool | table, row, query, dataset | schema, column, transform, export |
| Product website | offer, product, proof, plan | section, CTA, media, FAQ |

Hard rule: the primary object must stay visible or recoverable while the user acts.

## Route And App Shell Map

Create a route map before arranging sections:

```text
/entry or /projects
/workspace/:id
/workspace/:id/review
/workspace/:id/history
/settings or /connections
```

For product tools, app shell normally includes:

- top bar: current product/project, status, primary action;
- left rail/sidebar: stable destinations and active route;
- main workspace: one dominant job;
- right/detail zone: selection, inspector, review, proposal, or help;
- bottom/status strip only for real sync, selection, warning, export, or ledger state.

Avoid route maps where every screen is a standalone landing section. Operational UI needs persistence, memory, and return paths.

## Navigation Patterns

Choose one primary navigation model:

| Model | Use for | Watch for |
| --- | --- | --- |
| Sidebar/rail | dashboards, admin, workbenches, SaaS apps | too many equal destinations |
| Master-detail | records, inboxes, assets, tasks | detail pane losing selection on refresh |
| Tabs | sibling views of one object | hidden destructive or primary actions |
| Breadcrumbs | deep hierarchy or folders | replacing main navigation with breadcrumbs |
| Stepper | linear workflow | no skip/recover path |
| Command menu | expert navigation/actions | hiding the only visible path |
| Canvas panels | editors and AI design tools | panels disconnected from current selection |
| Content sections | websites/landings | using section nav inside dashboards |

Navigation should reflect frequency of use, not the database schema.

## Pane And Zone Rules

Design zones by job:

- scan zone: table/list/grid/tree;
- work zone: canvas, editor, form, or current object;
- context zone: metadata, source, owner, freshness, status;
- action zone: primary action, secondary actions, bulk actions;
- review zone: diff, proposal, validation, approval;
- decision zone: decision question, options/comparison, evidence, risk, approval/rejection, after-state;
- recovery zone: history, undo, rollback, retry, reopen.

Keep one dominant zone. If three panels compete at the same visual weight, the IA is not done.

## AI Design App IA

For ForgeStudio-like products, keep this spine visible across the workspace:

```text
project -> page/canvas object -> comment/task -> proposal -> preview/diff -> verification -> approval -> transaction -> ledger/export
```

Recommended workspace IA:

- left: project map, pages, layers, assets, comments/tasks;
- center: preview/canvas/diff;
- right: inspector, proposal, verification, export;
- top: project status, agent connection, primary action;
- history/ledger reachable without losing current selection.

Do not collapse this into chat-only IA. Chat can assist, but the product state must live in objects, selections, proposals, proofs, and ledger rows.

## Responsive IA

Define how the IA changes by viewport:

- desktop wide: full shell, primary pane, context/review pane;
- desktop narrow: collapsible sidebar or narrower detail pane;
- tablet: one primary pane plus drawer for context/review;
- mobile: review-only, focused edit, or route-by-route flow; do not pretend dense desktop tools are fully equivalent on mobile unless built that way.

Every hidden pane needs an obvious way back.

## State And Recovery IA

Place failure states where the user can fix them:

- empty project near open/import action;
- disconnected agent near agent-dependent controls;
- invalid filter near filters, not only in a toast;
- failed export near export action and history;
- stale proposal near preview/diff and approval;
- evidence/risk near decision actions, not hidden behind separate navigation;
- permission denied near the blocked pane;
- rollback unavailable near ledger/history.

Do not hide primary failures in a global toast only.

## Anti-Patterns

- Hero-first app screens.
- Navigation built from decorative cards instead of real destinations.
- A command palette as the only path to core actions.
- Detail drawers that hide status, history, or validation.
- Tabs that mix routes, filters, modes, and actions.
- Mobile layout that simply stacks every desktop panel.
- AI workbench IA where "done" appears without proposal, preview/diff, verification, approval, and ledger evidence.

## Output Contract

Use this format before implementation:

```text
Primary object:
Route map:
Navigation model:
App shell:
Main work zone:
Context/review zones:
Decision/review cockpit:
Global actions:
Local actions:
State/recovery placement:
Responsive IA:
Rejected IA pattern:
Reason rejected:
```
