# Universal Product Design Brief

Use this before designing, redesigning, or auditing any product surface. The goal is to make the agent understand the product before choosing layout, components, motion, or visual style.

This brief is required for dashboards, admin panels, SaaS apps, AI design studios, canvas editors, data tools, product websites, hybrid sites, and landing pages. For exact website cloning, complete the clone/research workflow first, then use this brief only for adaptation or improvement.

For the full order of design work, use `UNIVERSAL_DESIGN_RUNBOOK.md`; this brief is Phase 1 of that runbook. For the navigation and layout model behind the `Navigation model` field, use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`. For the action/state behavior behind the `State model` field, use `PRODUCT_UI_INTERACTION_MODEL.md`. For factual labels, empty/error copy, AI/proof status language, and sample/demo labels, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`. For approval, comparison, triage, and proposal-review surfaces, use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
For implementation scope, use `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` before coding so the work is a coherent route/screen/workflow rather than isolated component polish.

## Brief Template

```text
Surface:
User:
Job:
Core loop:
Primary object:
Product object model:
Visual system contract:
Primary action:
Secondary actions:
Density:
Trust/proof level:
Data source:
State model:
Copy/status policy:
Decision/review path:
AI operational invariants:
Implementation slice:
Navigation model:
Component strategy:
Motion policy:
Responsive policy:
Accessibility risks:
Verification plan:
```

## How To Fill It

| Field | Good answer |
| --- | --- |
| Surface | `dashboard`, `admin`, `SaaS workflow`, `AI design studio`, `canvas editor`, `data tool`, `website`, `landing`, `3D/WebGL`, or `hybrid`. |
| User | The real operator, not a vague persona. Example: founder reviewing agent proposals, analyst triaging alerts, designer editing a canvas. |
| Job | The decision or task the UI must make easier. |
| Core loop | The repeated path: inspect -> decide -> act -> verify, or the domain-specific equivalent. |
| Primary object | The thing the UI is about: project, page, proposal, record, row, asset, task, metric, document, scene, file. |
| Product object model | Entities, visible fields/attributes, status lifecycle, ownership/permissions, events/history, relationships, and source truth the UI must respect. |
| Visual system contract | Typography scale, spacing/density rhythm, radius/borders/surfaces, color/status/contrast rules, icon/motion policy, and target-local token/component conventions. |
| Primary action | The action that moves work forward. |
| Secondary actions | Review, filter, compare, edit, approve, export, rollback, share, connect, retry. |
| Density | `low`, `medium`, or `high`, based on repeated use and scan speed. |
| Trust/proof level | `light`, `visible`, or `strict`. Use strict for AI claims, imports, metrics, payments, security, or irreversible actions. |
| Data source | Real source, local file, API, sample/demo, or disconnected. Never imply sample data is real. |
| State model | Empty, loading, error, disabled, selected, pending, success, warning, conflict, retry, rollback. |
| Copy/status policy | Factual labels for action states, empty/error/disconnected messages, sample/demo labels, and inline-vs-toast policy. |
| Decision/review path | Decision question, comparison/options, evidence, risk, approval/rejection policy, after-state, and audit/recovery. |
| AI operational invariants | For AI design apps: proposal-only boundary, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen path. Use `N/A - not an AI design app` only outside AI workbenches. |
| Implementation slice | Route/screen, primary object, entry state, main action, data/fixture truth, included/deferred states, verification commands, screenshot/browser evidence, and risks. |
| Navigation model | App shell, master-detail, tabs, command palette, breadcrumbs, stepper, canvas panels, or content sections. |
| Component strategy | Existing local primitives first; add external components only for named product jobs. |
| Motion policy | None, control feedback, workflow continuity, or expressive. Must respect reduced motion. |
| Responsive policy | Desktop-first, mobile review-only, mobile focused edit, or fully responsive. |
| Accessibility risks | Keyboard path, focus, labels, contrast, hit areas, tooltips, reduced motion. |
| Verification plan | Commands, screenshots, browser checks, states, and viewports to verify. |

## Decision Order

1. Classify the surface.
2. Name the primary object and core loop.
3. Choose the information architecture with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
4. Define the interaction and state model with `PRODUCT_UI_INTERACTION_MODEL.md`.
5. Define factual copy/status language with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
6. Shape decision/review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
7. Fill the implementation slice contract with `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`.
8. Choose components that fit the work.
9. Apply visual system and taste.
10. Add motion only if it clarifies feedback or continuity.
11. Verify with screenshots, states, and real commands.

## Top Design Standard

Top product design is:

- useful before it is decorative;
- readable under repeated use;
- honest about data, proof, AI, and import state;
- stable across desktop, tablet, and mobile;
- polished in spacing, typography, alignment, contrast, and states;
- distinctive only where distinctiveness helps the product, brand, or memorability.

## Brief Readiness

For `.design-agent/` packet work, `design:brief-check` must pass before coding. Core product fields cannot be generic. The brief must make these concrete:

- user/job/object;
- product object model: entities, fields, status lifecycle, permissions/events, source truth;
- visual system contract: typography, spacing/density, radius/surfaces, color/status/contrast, icon/motion policy;
- workflow/action path;
- data/source truth;
- route/screen;
- closest product surface blueprint;
- screen recipe/state specs;
- local files to inspect/change;
- component state plan;
- verification evidence;
- top-design target and product-specific details.

Weak answers such as `improve UI`, `make better`, `use app`, `done`, or `N/A` for core product fields are not ready for coding. A brief that does not name the product object model, visual system contract, product surface blueprint, screen recipe/state specs, local target files, and component states is still planning, not implementation-ready.

For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, the brief must also fill AI Design App Invariants: external AI is proposal-only until what evidence exists, where preview/diff is visible, where verification is visible, where human approval happens, where transaction/ledger evidence appears, where agent connection/scopes are visible, how comments become agent tasks, how pending proposals/approvals cross into the live UI, how failures/recovery are shown inline, and how export/reopen recovery works. `N/A` is allowed only when the surface is not an AI design app.

## Hard Stops

- Do not start with a landing hero for dashboards, editors, workbenches, admin panels, or data tools.
- Do not use cards where a table, list, tree, inspector, or command surface is the real primitive.
- Do not show fake metrics, fake customers, fake screenshots, fake files, fake agent activity, or fake proof.
- Do not install a UI catalog in bulk.
- Do not call a visual change done without browser or screenshot evidence, unless the final report clearly marks the missing evidence as a risk.
