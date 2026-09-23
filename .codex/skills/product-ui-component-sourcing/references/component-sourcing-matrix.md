# Component Sourcing Matrix

Use this reference to choose product UI primitives deliberately. The default path is local component -> accessible primitive -> focused library -> verified catalog item. Before choosing a source, use `docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, `docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md`, `docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md`, `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md`, `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, `docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, `docs/design-workbench/COMPONENT_STATE_SPEC.md`, and `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` to identify the surface, primary object, core loop, density, route/pane placement, interaction transitions, copy/status language, decision/review role, implementation slice, state model, screen recipe, component blueprint, top-design role, and component job. For AI design studios, canvas editors, proposal/diff flows, or ForgeStudio-like products, also use `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md` so each component maps to a source-of-truth object, proof/evidence surface, decision, after-state, or recovery path.

## Source Trust Ladder

| Level | Use first when | Risk |
| --- | --- | --- |
| Existing local component | The project already has a semantic component or wrapper | Must match current API and states |
| Native HTML/CSS/Tailwind | The need is layout, spacing, simple hover, static status, or basic form | Easy to underbuild accessibility |
| shadcn/Radix/headless primitive | The need is dialog, popover, tabs, menu, tooltip, command, select, accordion, drawer | Requires project-local styling and states |
| Focused domain library | The need is real data grid, code editor, rich editor, charting, drag/drop, form validation | Dependency and bundle cost |
| Verified catalog item | The component saves implementation time and can be adapted | Demo-data, template look, license/dependency drift |
| Custom implementation | The behavior is product-specific and no primitive fits | Must implement keyboard/a11y/state behavior |

## Product Primitive Routing

| Need | Preferred source | Notes |
| --- | --- | --- |
| App shell / sidebar | Existing layout, shadcn sidebar, local CSS grid | Keep navigation/current location visible. |
| Layer tree / project tree | Local tree component, Radix collapsible, virtualized list if huge | Fixed row height, selected/focused/locked/warning states. |
| Data table | Existing table, TanStack Table, AG Grid only for heavy enterprise needs | Sort/filter/selection/skeleton/empty states matter more than visual cards. |
| Inspector fields | Local field group, shadcn input/select/slider/switch, React Hook Form when validation grows | Labels, units, token binding, locked/reset/invalid states. |
| Command palette | cmdk or shadcn command | Keep primary actions visible; palette is acceleration, not main navigation. |
| Dialog/modal | shadcn/Radix dialog | Use for blocking confirmation or focused short form only. |
| Drawer/sheet | shadcn/Radix drawer/sheet or local panel | Good for proposal, detail, settings, mobile inspector. |
| Tabs/segmented control | shadcn/Radix tabs or local segmented control | Stable dimensions, keyboard, active/focus states. |
| Tooltip/popover | shadcn/Radix tooltip/popover | Tooltips for icon buttons; popover for extra controls. |
| Toast/inline alert | Local alert + toast primitive | Use inline alerts for actionable failures; toast for transient confirmation. |
| Chart | Recharts, Visx, existing chart lib | Only use when chart answers faster than table; show source/time range. |
| Code diff | Existing diff viewer, Monaco diff, CodeMirror, lightweight custom if small | Avoid heavy editor if static diff is enough. |
| Canvas overlay | Custom, because it is product-specific | Selection, anchors, zoom, hit testing, and z-index must be designed. |
| Proposal card | Local component | Needs status, risk, changed files/objects, checks, preview action. |
| Verification checklist | Local component | Passed/warning/failed grouping, worst state first, retry path. |
| Ledger/history row | Local component/table | Actor, transaction, linked task, timestamp, result, rollback. |
| File upload | Existing upload, native input, verified upload block only for complex flows | Must show file type, progress, failure, retry, source. |
| Rich text/comment composer | Textarea first, rich editor only when formatting is required | Comment is a task; avoid overbuilt chat UI. |

## Catalog Routing

| Source | Use for product UI when | Avoid when |
| --- | --- | --- |
| shadcn/ui | Editable React primitives in Tailwind projects | You would ship default styling or duplicate existing components |
| Animate UI | Animated/headless/radix details that improve state continuity | Dense panes, decorative motion, or unsupported endpoint |
| Blocks.so | Reference or import for app-like blocks: sidebars, command menus, upload, forms, tables | Fake dashboards, fake AI chats, full template identity |
| Kibo UI / Coss / Origin | Focused widgets such as command, calendar, upload, editor-like details | Endpoint/dependency cannot be verified |
| ReUI / HextaUI / SmoothUI / Kokonut / Skiper / Eldora | Reference or small adapted components after source-map check | Bulk install, landing-style cards in work surfaces |
| Motion Primitives | Lightweight motion primitives | Motion that distracts from scan/edit/review |
| Magic UI / Aceternity / React Bits | Website/marketing effects or inspiration | Operational dashboards/editors unless isolated and justified |

Always read the matching local catalog skill/source map before using a catalog item.

## Dependency Gates

Before adding a dependency, answer:

- Does the project already have an equivalent?
- Is this behavior hard enough to justify the library?
- Is it compatible with the current framework, React version, Tailwind version, and component style?
- Does it force a new animation system or client boundary?
- Can the component be keyboard accessible and responsive?
- Is the license/source acceptable?
- Is there demo content that must be removed?

Reject by default:

- second design system for the same screen;
- chart library for static metrics;
- editor library for plain comments;
- drag/drop library for a non-reorderable list;
- full block template for one primitive;
- component with unverifiable registry endpoint;
- component that ships fake proof as UI.

## ForgeStudio-Like Component Needs

| Surface | Components to design/source |
| --- | --- |
| Project launcher | recent project list, open-folder button, connection status, privacy/settings link |
| Design search | count summary, grouped result table/list, warning panel, import action |
| Import review | candidate table, dependency list, approval controls, conflict rows |
| Studio workspace | app shell, project tree, layer tree, canvas, inspector, task/proposal tabs |
| Canvas | custom overlays, zoom controls, breakpoint selector, anchors, missing asset warnings |
| Inspector | field groups, token binding, reset controls, lock/inherited states |
| Comments/tasks | anchored task card, status tabs, composer, linked transaction |
| Proposal/diff | proposal card, changed object list, before/after diff, approve/revise controls |
| Verification | checklist, command/screenshot evidence, retry path |
| Ledger/history | transaction table/list, rollback/reopen action |
| Export/share | artifact list, target path, warning list, completed/open action |

Trusted-vertical component rule: do not add an AI-workbench component unless it clarifies one trusted object or state in `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, such as project folder, design search report, import plan, visual object, anchored comment, agent task, proposal, verification run, transaction, ledger entry, or export artifact.

## Acceptance Checklist

- The chosen component solves a named product job.
- The chosen component improves the top-design benchmark instead of adding generic visual novelty.
- The component belongs to a coherent implementation slice, not isolated decoration.
- The chosen component has a matching blueprint or a documented custom reason.
- Existing local primitives were checked first.
- Only one source/system owns the primitive family.
- All required states are named before implementation.
- Copy/status labels are factual and avoid vague "done/success/ready" feedback.
- Review/approval components expose comparison, evidence, risk, after-state, and audit/recovery path.
- A `COMPONENT_STATE_SPEC.md` spec exists for reusable or sourced components.
- Keyboard/focus behavior is covered.
- Demo/sample data is removed or labeled.
- Dependency and license/source are recorded.
- Mobile and reduced-motion behavior are planned.
- Verification includes screenshots or commands when available.
