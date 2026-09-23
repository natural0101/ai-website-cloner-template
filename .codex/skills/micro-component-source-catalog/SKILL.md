---
name: micro-component-source-catalog
description: Select verified shadcn-compatible micro-components from Kibo UI, Origin UI/Coss UI, or similar focused component registries for landing-page plans. Use when a landing needs polished forms, command menus, calendars, code blocks, tables, upload/dropzone, ratings, tags, color pickers, media players, product/app-preview widgets, or other small UI details; when validating registry URLs, copy/install model, dependencies, license, mobile behavior, reduced-motion needs, and task/change mapping; or when filling `34-micro-component-selection.md`.
---

# Micro Component Source Catalog

Use this skill when the page needs small UI details rather than a whole section block.

For dashboards, editors, AI design studios, canvas workbenches, SaaS apps, admin panels, or product UI, use `product-ui-component-sourcing` first. Also read `docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md` and `docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md`. Only use this skill after the product job, local component options, dependency impact, and demo-data cleanup plan are clear.

## Required Reading

Read:

- `план разработки топового лендинга/38-micro-component-source-map.md`
- `план разработки топового лендинга/11-component-source-registry.md`
- active project `08-component-and-asset-plan.md`, `18-section-storyboard-canvas.md`, and `34-micro-component-selection.md` if present

## Workflow

1. Identify the exact micro-interaction or UI need: form, picker, command menu, table, code, upload, calendar, rating, tag, media, product/app preview, or status.
2. Prefer existing project components, native Tailwind, and shadcn primitives first.
3. If a source helps, pick one exact item from Kibo UI or Origin/Coss. Use `$kibo-ui-catalog` for Kibo-specific dependency and endpoint caveats.
4. Record source, item ID, registry/copy URL, dependencies, license, adaptation, mobile behavior, reduced-motion fallback if animated, owner `task-###`, and `chg-###` in `34-micro-component-selection.md`.
5. Reject heavy items when the landing only needs a static visual or a simple native component.

## Source Rules

- Kibo UI installable items use `https://www.kibo-ui.com/r/<name>.json`.
- Kibo UI has no useful root `/registry.json`; item endpoints are the source of truth. Live `/r/registry.json` can exist but time out on body fetch, so do not use a partial registry body as proof.
- Kibo UI generic guesses such as `button`, `accordion`, or `ai-input` are invalid if they return package lookup errors.
- Kibo UI `editor`, `gantt`, and `reel` need a fresh body-fetch success or explicit source-adaptation plan before use.
- Origin UI now redirects to `https://coss.com/ui` for the live site.
- Origin/Coss live registry items use `https://coss.com/ui/r/<name>.json`.
- `https://originui.com/r/<name>.json` can redirect to HTML, not JSON. Do not use it as the registry endpoint.
- Origin UI GitHub has `registry.json` and `public/r`, but verify live Coss endpoint before implementation.

## Acceptance Rules

- Accept only when the component improves a real workflow, proof display, product preview, form quality, or interaction clarity.
- List every dependency, especially heavy libraries such as `shiki`, `react-icons`, `jotai`, `recharts`, editors, media players, drag/drop stacks, and calendars.
- Keep client boundaries tight. Do not turn a static landing section into a client-heavy app shell without reason.
- Replace demo content and icons with project evidence.
- Add mobile and keyboard/focus QA for forms, menus, tables, uploads, drawers, and command interactions.

## Output

Fill or update:

- `34-micro-component-selection.md`
- `08-component-and-asset-plan.md`
- `18-section-storyboard-canvas.md`
- related rows in `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`
