---
name: tailark-section-catalog
description: Select verified Tailark and Tailark Pro marketing section blocks for landing-page plans. Use when choosing hero, feature, pricing, FAQ, CTA, testimonial, logo-cloud, auth, page, bento, or SaaS marketing sections from Tailark; when validating Tailark install commands, registry URLs, access/licensing, mobile behavior, dependencies, and adaptation rules; or when filling `32-tailark-section-selection.md`.
---

# Tailark Section Catalog

Use this skill when Tailark is considered as a section-structure source, not as a generic visual style to copy.

## Required Reading

Read:

- `план разработки топового лендинга/36-tailark-section-source-map.md`
- `план разработки топового лендинга/11-component-source-registry.md`
- active project `13-section-pattern-selection.md`, `18-section-storyboard-canvas.md`, `08-component-and-asset-plan.md`, and `32-tailark-section-selection.md` if present

## Workflow

1. Identify the section job: clarity, proof, feature explanation, pricing, objection handling, CTA, auth, footer, or page structure.
2. Pick a Tailark candidate only from a live category page, live preview URL, or live item registry URL.
3. Record the exact item name, source URL, preview URL, registry URL, install command, dependencies, and access status in `32-tailark-section-selection.md`.
4. Decide `accept`, `adapt`, `reject`, `backlog`, or `reference-only`.
5. If accepted, add dependency impact and files to `08-component-and-asset-plan.md`.
6. Map the selection to stable `task-###` and `chg-###` IDs before implementation handoff.

## Source Rules

- Public Tailark uses item URLs like `https://tailark.com/r/hero-section-1.json`.
- Public Tailark docs say to configure the namespace in `components.json` as `"@tailark": "https://tailark.com/r/{name}.json"`.
- Public install commands use `pnpm dlx shadcn add @tailark/<name>`.
- Mist kit uses names like `mist-hero-section-1`.
- Veil kit item URLs can exist at `/r/veil-*.json`, but check the source map and dependencies before use.
- Do not rely on `https://tailark.com/registry.json`; it returned 404 in the audit.
- Do not rely on old public sitemap preview URLs shaped like `/preview/<category>/<Title> (dusk-kit)`; they returned 404. Use current preview URLs shaped like `/preview/dusk/hero-section/one`.
- Treat Tailark Pro as paid/API-key material. Use Pro blocks, pages, and illustrations as `reference-only` unless access and licensing are explicit.

## Acceptance Rules

- Accept a block only if section structure is the real gap.
- Prefer adapting layout rhythm, hierarchy, and composition over copying the full look.
- Replace demo copy, logos, screenshots, icons, and claims with project evidence.
- Record mobile simplification even for static blocks.
- Record reduced-motion fallback when the candidate depends on Motion, Magic UI, Motion Primitives, or animated primitives.
- Reject recognizable blocks when they would make the landing feel like a Tailark demo.

## Output

Fill or update:

- `32-tailark-section-selection.md`
- `13-section-pattern-selection.md`
- `18-section-storyboard-canvas.md`
- `08-component-and-asset-plan.md`
- related rows in `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`
