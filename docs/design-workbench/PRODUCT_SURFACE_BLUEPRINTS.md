# Product Surface Blueprints

Use these blueprints after `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md` and before implementation. Pick the closest surface, then adapt to the target project's existing stack and conventions. After choosing a surface, map the information architecture with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, choose concrete screen recipes from `PRODUCT_UI_SCREEN_RECIPES.md`, define interaction behavior with `PRODUCT_UI_INTERACTION_MODEL.md`, define copy/status language with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, shape decision/review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, and choose component blueprints/state requirements from `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` and `COMPONENT_STATE_SPEC.md`.

For dashboard, admin, records, and data-tool surfaces, also use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` before implementation.

## Dashboard

Purpose: scan, compare, decide, and act.

Start with:

- app shell with current area, time range, filters, and owner/source;
- compact summary strip only when it answers recurring decisions;
- table/list/grid as the main work surface;
- drill-down, saved views, export, and alert/action states near the data.

Required states:

- no data connected;
- sample/demo data;
- loading skeleton rows;
- filter returns zero results;
- stale data or sync failed;
- selected row/detail;
- export pending/success/failure.

Avoid:

- marketing hero;
- decorative metric cards with invented numbers;
- charts that do not answer a faster question than a table.

## Admin Panel

Purpose: manage records, permissions, settings, and risky changes.

Start with:

- clear navigation, records table, filters, bulk actions, and detail drawer;
- explicit status, role, ownership, last changed, audit trail, and validation;
- confirmation for destructive actions and visible recovery paths.

Required states:

- permission denied;
- validation error;
- unsaved changes;
- pending save;
- destructive confirmation;
- rollback or restore;
- record not found.

Avoid:

- hiding primary management actions in decorative menus;
- custom controls that break keyboard or screen-reader behavior.

## SaaS Workflow App

Purpose: complete a job from intake to review, approval, and output.

Start with:

- stable app shell;
- visible current object and next action;
- progress/status model;
- forms, checklists, review screens, and completion evidence.

Required states:

- draft;
- blocked;
- waiting for review;
- rejected/rework;
- approved;
- export/share complete;
- saved progress and return path.

Avoid:

- single happy-path wizard with no recovery;
- final "done" state without review or output evidence.

## AI Design Studio Or Canvas Editor

Purpose: inspect a project, edit or comment on visual objects, review agent proposals, verify, approve, export, and recover.

Start with:

- canvas or preview as the main surface;
- project map/layers/assets on the left;
- inspector/properties/proposals on the right;
- comments/tasks, verification, history, and export reachable without losing selection.

Required states:

- no project open;
- scan/import running;
- asset skipped with path and reason;
- object selected;
- comment anchored;
- agent disconnected;
- proposal pending;
- preview/diff ready;
- verification failed;
- approved/applied with ledger row;
- rollback/reopen.

Avoid:

- reducing the product to a chat page;
- claiming "AI fixed it" before proposal, preview/diff, verification, approval, and ledger evidence.

## Data Tool

Purpose: inspect, filter, transform, compare, and export structured information.

Start with:

- table/list as product center;
- schema/source/freshness visible;
- saved filters/views;
- column controls, sorting, row detail, and export.

Required states:

- connection missing;
- query running;
- empty result;
- partial result;
- stale source;
- invalid filter/query;
- export failed.

Avoid:

- decorative charts before table clarity;
- hiding units, time ranges, source, or freshness.

## Product Website

Purpose: explain the product, route visitors, establish trust, and move them to action.

Start with:

- brand/product visible in the first viewport;
- clear offer or category;
- proof only when sourced;
- product screenshots/assets that show the real thing;
- content sections that answer what it is, who it is for, why it matters, and what to do next.

Required states:

- mobile navigation;
- pricing/plan or contact ambiguity handled;
- empty or unavailable media fallback;
- no invented claims.

Avoid:

- generic gradient/SVG hero when product imagery or real interface evidence is needed;
- fake testimonials, fake logos, fake metrics, or fake screenshots.

## 3D Or WebGL Surface

Purpose: inspect, demonstrate, or interact with 3D content.

Start with:

- stable full-bleed or properly framed viewport;
- loading/progress state;
- camera framing and fallback image;
- controls explained through icons/tooltips;
- reduced-motion and performance safeguards.

Required states:

- model loading;
- model failed;
- unsupported browser/GPU;
- reduced motion;
- selected object or interaction feedback;
- mobile fallback.

Avoid:

- blank canvas with no fallback;
- heavy decorative WebGL inside dense work panes unless it is the product.

## Landing Page

Purpose: convert a visitor for one offer.

Use the landing workflow skills when the surface is truly marketing or conversion-focused.

Start with:

- literal brand/product/category headline;
- relevant real or generated visual asset;
- clear offer, audience, proof, objections, CTA, and responsive flow.

Avoid:

- applying landing composition to dashboards, editors, workbenches, admin, or data tools.
