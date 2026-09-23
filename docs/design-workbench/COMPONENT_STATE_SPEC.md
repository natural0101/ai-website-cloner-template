# Component State Spec

Use this before implementing or sourcing any reusable component for product UI. It keeps agents from shipping a good-looking static component with missing states. Use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md` to place the component in the app shell/work zone/context/review/recovery model, use `PRODUCT_UI_INTERACTION_MODEL.md` to define action transitions, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md` to define labels and messages, use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` to define decision/review behavior when relevant, then use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` to choose the component anatomy and expected behavior before filling the spec.

## Spec Template

```text
Component:
Product job:
Surface/recipe:
Owner screen:
Primary data:
Actions:
Interaction transitions:
Copy/status language:
Decision/review role:
Variants:
States:
Accessibility:
Keyboard behavior:
Responsive behavior:
Motion:
Data/proof honesty:
External source:
QA evidence:
```

## Required Fields

| Field | What to write |
| --- | --- |
| Component | Name and role, such as `ProposalPanel`, `JobTable`, `InspectorField`, `ExportStatus`. |
| Product job | Scan, select, edit, filter, compare, review, approve, recover, export, or navigate. |
| Surface/recipe | Link to the chosen `PRODUCT_UI_SCREEN_RECIPES.md` recipe. |
| Owner screen | Route or screen where the component is primary. |
| Primary data | Real source, sample/demo, local file, API, fixture, or disconnected. |
| Actions | User actions and system actions. |
| Interaction transitions | Pending, success, failure, retry, undo, rollback, permission, and proof behavior from `PRODUCT_UI_INTERACTION_MODEL.md`. |
| Copy/status language | Factual labels, empty/error text, sample/demo labels, and inline-vs-toast behavior from `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`. |
| Decision/review role | Decision question, comparison/options, evidence, risk, action policy, after-state, and audit/recovery from `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` when relevant. |
| Variants | Size, density, status, role, selected, compact/mobile, or read-only variants. |
| States | Default plus all relevant operational states. |
| Accessibility | Label, name, description, role, focus-visible, contrast, hit area. |
| Keyboard behavior | Tab order, arrow navigation, escape/enter/space behavior, focus restore. |
| Responsive behavior | Resize, collapse, truncate, wrap, drawer, mobile fallback. |
| Motion | None, control feedback, continuity, or expressive; reduced-motion behavior. |
| Data/proof honesty | How fake/demo/unavailable data is labeled or avoided. |
| External source | Existing local component first; if external, name source and reason. |
| QA evidence | Screenshots/states/commands needed before done. |

## State Checklist By Primitive

| Primitive | Required states |
| --- | --- |
| Button/icon button | default, hover, active, focus-visible, disabled, loading, destructive when relevant |
| Input/select/combobox | empty, focused, filled, invalid, disabled, pending, no results |
| Table/list row | loading skeleton, empty, hover, selected, focused, disabled, warning/error, stale |
| Tree/layer item | expanded, collapsed, selected, focused, hidden, locked, warning, missing asset |
| Inspector field | no selection, inherited, overridden, invalid, locked, pending, reset available |
| Card/panel | default, selected, loading, empty, warning/error, disabled, stale |
| Drawer/dialog/popover | open, closed, loading, error, keyboard trap/restore, mobile placement |
| Tabs/segmented control | active, hover, focus, disabled, overflow/collapse |
| Toast/alert | info, success, warning, error, action, dismiss, retry |
| Canvas/WebGL/media | loading, render error, missing asset, selected object, unsupported, fallback |

## Product-Specific State Checklist

| Surface | Component states to require |
| --- | --- |
| Dashboard | no data, sample data, stale data, loading, empty filter, selected detail, export failed |
| Admin | permission denied, validation error, unsaved changes, destructive confirm, restore |
| AI workbench | no project, import warning, selected object, comment anchored, agent disconnected, proposal pending, verification failed, ledger row |
| Data tool | query running, partial result, invalid filter, connection missing, export failed |
| Product website | mobile nav, media fallback, proof unavailable, sample preview labeled |
| 3D/WebGL | model loading, model failed, reduced motion, unsupported browser/GPU, mobile fallback |

## Hard Rules

- Do not implement a component with only the happy path.
- Do not source an external component until the product job and missing behavior are named.
- Do not leave catalog demo data, fake users, fake metrics, fake screenshots, fake files, or fake agent activity as real UI.
- Do not use motion on a component until the state transition it explains is named.
- Do not ship vague status labels such as "Done", "Success", or "Ready" as the only feedback for important actions.
- Do not ship review/approval components that hide comparison, evidence, risk, after-state, or audit/recovery.
- Do not call a component done until the final report names the states and evidence checked.

## Mini Example

```text
Component:
ProposalPanel

Product job:
Review, verify, approve/revise, and recover an AI proposal.

Surface/recipe:
PRODUCT_UI_SCREEN_RECIPES.md -> Proposal / Diff Review

States:
no agent, pending, ready, stale, diff unavailable, verification running, verification failed, approved, rejected, needs revision

Accessibility:
Panel has labelled heading, approve/revise buttons have names, focus moves into drawer when opened and returns to trigger on close.

Data/proof honesty:
Mock proposal fixture is labeled "Sample proposal"; no copy says AI changed the project until approval and ledger row exist.

Copy/status language:
"Proposal needs approval"; "Verification failed"; "Ledger row created" only after approved transaction evidence exists.

Decision/review role:
Decision question is "Approve this proposal?"; comparison is before/after diff; evidence is verification result; actions are approve, revise, reject; after-state is transaction plus ledger row.

QA evidence:
proposal-ready 1440x900 screenshot, verification-failed 1024x768 screenshot, mobile drawer screenshot, keyboard focus check.
```
