# Product UI Component Sourcing

Use this when an agent needs to choose components for dashboards, editors, AI design studios, canvas workbenches, SaaS apps, or product workflows. Before sourcing a component, identify the screen recipe in `PRODUCT_UI_SCREEN_RECIPES.md`, confirm IA placement in `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, define action transitions with `PRODUCT_UI_INTERACTION_MODEL.md`, define status labels and messages with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, define decision/review behavior with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, choose the closest blueprint from `PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, and fill the relevant fields from `COMPONENT_STATE_SPEC.md`.

## Rule

Pick components for the product job, not for catalog beauty.

Default order:

```text
existing local component -> native/Tailwind -> shadcn/Radix/headless primitive -> focused domain library -> verified catalog item -> custom implementation
```

## Product Jobs

| Job | Typical primitive |
| --- | --- |
| Scan and compare | table, list, small chart, saved view |
| Select and inspect | tree/list row, canvas overlay, inspector panel |
| Edit and validate | form field, slider/switch/select, validation group |
| Navigate fast | sidebar, tabs, command palette, breadcrumbs |
| Review AI work | proposal card, changed object list, before/after diff |
| Verify | checklist, evidence row, failure inline alert |
| Recover | history row, rollback action, conflict state |
| Export | artifact list, target path, warning/result panel |

## Use Existing First

Before adding anything:

- inspect `package.json`;
- inspect `src/components`, `src/components/ui`, app-shell/layout files, and local token files;
- check whether shadcn/Radix/TanStack/cmdk/Recharts/Motion/etc. are already present;
- preserve project conventions and wrappers.
- compare the needed component against `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before browsing catalogs.
- confirm whether the component belongs to app shell, main work zone, context/review zone, global action, local action, recovery path, or responsive fallback in `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
- define pending, success, failure, retry, undo/rollback, permission, and proof behavior in `PRODUCT_UI_INTERACTION_MODEL.md`.
- define factual labels, empty/error copy, sample/demo labels, and toast-vs-inline behavior in `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
- define comparison, evidence, risk, approval, after-state, and audit/recovery behavior in `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` for review/decision components.

## Catalog Rules

- Use exact registry item names and endpoints.
- Install one component at a time.
- Never bulk-install a catalog.
- Read the matching local catalog/source-map skill before using a catalog item.
- Treat catalog demos as reference, not final product content.
- Remove or label fake metrics, fake users, fake AI chats, fake files, fake tables, fake screenshots, and fake proof.

## Hard Rejects

- landing sections used as dashboards;
- decorative cards where a table/list/tree is needed;
- animated effects inside dense edit/review panes without a state reason;
- multiple component systems on one screen;
- unverifiable registry endpoint;
- library that exists only to avoid implementing a simple primitive;
- component that breaks keyboard/focus/reduced-motion requirements.

## Required Record

For each accepted external component/source, record:

- product job;
- IA placement;
- interaction transitions;
- copy/status language;
- decision/review role;
- chosen component blueprint;
- source and exact item;
- source URL/registry endpoint/install command where applicable;
- dependency and license impact;
- adaptation plan;
- removed demo content;
- state coverage;
- accessibility/mobile/reduced-motion checks;
- verification command or screenshot plan.
