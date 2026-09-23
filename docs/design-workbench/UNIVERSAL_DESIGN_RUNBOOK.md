# Universal Design Runbook

Use this when an agent must design, redesign, or build any frontend surface from scratch: dashboard, admin panel, SaaS app, AI design studio, canvas editor, data tool, product website, landing page, 3D/WebGL surface, or hybrid product.

This is the operating order. Do not jump directly to visuals.

## Phase 0: Project Read

Inspect the target project before design decisions:

- framework, router, routes, package scripts, build/test commands;
- existing app shell, layout primitives, tokens, components, icons, fonts;
- existing data model, mock/sample data, API/state management, auth/permissions;
- screenshots or live routes when available;
- user request, product constraints, and any brand/reference material.

Output:

```text
Stack:
Existing UI conventions:
Routes/surfaces:
Reusable components:
Data/proof sources:
Risks:
```

## Phase 1: Product Model

Fill `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`.

Decide:

- surface type;
- user and job;
- primary object;
- product object model: entities, fields/attributes, status lifecycle, permissions/events, and source truth;
- visual system contract: typography, spacing/density, radius/surfaces, color/status/contrast, icon/motion policy, and target-local tokens/components;
- core loop;
- primary action;
- density;
- trust/proof level;
- responsive policy;
- verification plan;
- decision/review path when the surface involves approval, comparison, triage, or trust.

Rule: if the product model is unclear, build the smallest honest slice and label assumptions. Do not fill uncertainty with decorative UI.
If using a `.design-agent/` packet, `design:brief-check` must pass before coding. It rejects generic fields and expects user/job/object, product object model, visual system contract, workflow/action path, data/source truth, route/screen, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, verification evidence, and top-design target. For AI design apps, it also requires concrete AI Design App Invariants: proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.

## Phase 2: Surface Blueprint

Choose one primary blueprint from `PRODUCT_SURFACE_BLUEPRINTS.md`:

| Surface | Primary layout bias |
| --- | --- |
| Dashboard | scan, compare, filter, drill down |
| Admin | records, permissions, audit, destructive safety |
| SaaS workflow | current object, progress, validation, next action |
| AI design studio | canvas, object selection, tasks, proposals, verification |
| Canvas/editor | central work area, layers, inspector, history |
| Data tool | table/list as product, source/freshness visible |
| Product website | offer, proof, exploration, conversion |
| Landing | first viewport, offer clarity, proof, conversion |
| 3D/WebGL | rendered object/state, fallback, performance, controls |
| Hybrid | split marketing and app/tool zones explicitly |

Output:

```text
Chosen blueprint:
Why:
Rejected blueprint:
Reason rejected:
Screen recipe/state specs:
```

## Phase 3: Workflow Map

Map the work before layout:

```text
entry -> inspect -> decide -> act -> feedback -> verify -> recover/export
```

For AI design apps, use `AI_DESIGN_APP_TRUSTED_VERTICAL.md` before `AI_WORKBENCH_INTERACTION_FLOWS.md`, then make the proposal-only path and bridge state explicit: preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen.

For each step, name:

- visible object;
- user action;
- system feedback;
- failure state;
- proof/evidence if trust matters.

Hard rule: every primary action needs a visible result, failure state, and recovery path.

For dashboards, admin panels, records UIs, and data tools, use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` before choosing cards, tables, filters, or charts.

## Phase 4: Information Architecture

Use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.

Build the layout around work:

- app shell before hero for tools;
- navigation that matches frequency of use;
- central work surface for editors/workbenches;
- tables/lists for repeated records;
- inspector/detail pane for selected objects;
- inline failures near affected controls;
- history/ledger where trust or recovery matters.

Avoid:

- marketing hero inside operational screens;
- card grids for data that should be compared row by row;
- hidden primary actions;
- equally loud panels;
- decorative motion competing with reading or editing.

Output:

```text
Primary object:
Route map:
Navigation model:
App shell:
Main work zone:
Context/review zones:
State/recovery placement:
Responsive IA:
```

## Phase 5: Screen, Interaction, State, Copy, And Decision Inventory

Choose recipes from `PRODUCT_UI_SCREEN_RECIPES.md`, map actions with `PRODUCT_UI_INTERACTION_MODEL.md`, define factual UI copy and status language with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, shape decision/review screens with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, then choose reusable component contracts from `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before filling `COMPONENT_STATE_SPEC.md`.

Minimum state set for serious product UI:

- empty;
- loading/skeleton;
- error with reason;
- disabled/unavailable;
- hover/focus-visible;
- selected/current;
- pending;
- success/applied;
- warning/conflict;
- retry/rollback/reopen when relevant.

Every primary action needs:

- trigger and preconditions;
- pending state;
- success result;
- failure state;
- recovery path;
- proof/evidence if trust matters.

Every major status message needs:

- affected object;
- specific state label;
- reason/details when the state blocks action;
- next action;
- source/evidence or sample/demo/disconnected label;
- inline-vs-toast placement.

Every decision/review surface needs:

- decision question;
- primary object;
- options or before/after comparison;
- evidence and source limits;
- risk/impact;
- approve/revise/reject or equivalent action policy;
- after-decision state;
- audit/ledger/recovery path when trust matters.

Output:

```text
Screens:
Interaction model:
Copy/status contract:
Decision/review cockpit:
Primary components:
State specs:
Missing states:
```

## Phase 6: Design System Baseline

Use `PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md`.

Define before implementation:

- typography scale;
- spacing scale;
- radius;
- surface/background layers;
- border/divider policy;
- accent and semantic colors;
- icon family;
- focus ring and keyboard policy;
- motion policy;
- responsive breakpoints.

Rule: distinctive design comes from hierarchy, rhythm, object clarity, states, and brand-specific details, not random gradients.

## Phase 7: Component Sourcing

Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before implementing reusable components, then use `PRODUCT_UI_COMPONENT_SOURCING.md` before adding libraries.

Decision order:

1. Existing local component.
2. Existing design-system primitive.
3. Small copied component with clear job.
4. External package only when it solves a real interaction/state problem.

Never bulk-install a catalog. Every imported component needs:

```text
Product job:
IA placement:
Interaction transitions:
Chosen component blueprint:
Why local primitives are insufficient:
Source:
States covered:
Accessibility notes:
```

## Phase 8: Visual Craft

Apply taste after the workflow, IA, interaction, and state model are sound:

- align to a grid;
- create strong scan hierarchy;
- make the decision question, current object, evidence, risk, and next action visually obvious;
- reserve accent for action/status;
- use stable row/control dimensions;
- keep text inside containers;
- make selected/focus/pending states obvious;
- remove fake proof and vague "looks good", "done", or "success" status language;
- use motion only for continuity, feedback, or spatial context.

For websites/landings, visual assets are required. For product tools, visual polish should clarify work before it decorates.

## Phase 9: Implementation Slice

Use `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`.

Implement the smallest coherent slice first:

```text
route/screen -> app shell/layout -> primary objects -> states -> actions -> responsive -> QA
```

Before coding, name:

- route/screen;
- user job;
- primary object;
- product object model;
- visual system contract;
- data/fixture source;
- closest product surface blueprint;
- screen recipe/state specs;
- local files to inspect/change;
- component state plan;
- states included and deferred;
- interaction/copy/decision contracts;
- components touched;
- verification commands and screenshot/browser evidence.

Prefer existing project patterns. Keep edits scoped. Do not refactor unrelated architecture to make a visual point.

## Phase 10: Verification

Use `PRODUCT_UI_REVIEW_RUBRIC.md`, `PRODUCT_UI_VISUAL_QA.md`, and `VISUAL_QA_EVIDENCE_PLAYBOOK.md`.

Verify:

- build/typecheck/lint/test commands available in the project;
- real browser or screenshot checks for changed visual routes;
- desktop wide, desktop narrow, tablet, and mobile when possible;
- no overlap, clipping, blank media/canvas, missing assets, or broken focus;
- empty/loading/error/pending/success/retry states;
- visual-system evidence names typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components;
- component-state evidence names changed components/controls, checked states, and screenshot/browser/manual/keyboard/responsive proof;
- proof/data honesty;
- reduced motion and keyboard basics.

If visual verification cannot run, final report must say why and mark the risk.

## Universal Done Contract

Before final handoff, report:

```text
Project read:
Brief:
Blueprint:
Workflow map:
Information architecture:
Information architecture evidence:
Interaction evidence:
Screen/interaction/state/copy/decision inventory:
Copy/status contract:
Copy/status evidence:
Decision/review cockpit:
Decision/review evidence:
Design-system decisions:
Visual system evidence:
Component sourcing:
Component state evidence:
Implementation slice:
Rubric score:
Commands:
Screenshots/browser checks:
Remaining risks:
Verdict:
```

Use `PASS`, `PASS WITH RISKS`, or `FAIL`. Do not use `PASS` when P0 visual blockers remain or visual evidence is missing without explanation.
