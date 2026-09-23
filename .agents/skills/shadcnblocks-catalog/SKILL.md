---
name: shadcnblocks-catalog
description: Select verified shadcnblocks blocks, components, pages, templates, and free/pro registry items for landing-page plans. Use when considering shadcnblocks for hero, feature, pricing, FAQ, CTA, proof, ecommerce, app, dashboard, form, or component sections; when validating free versus Pro access, registry URLs, CLI commands, license restrictions, dependencies, mobile behavior, and adaptation rules; or when filling `33-shadcnblocks-selection.md`.
---

# shadcnblocks Catalog

Use this skill when shadcnblocks is considered as a section, page, or component source.

## Required Reading

Read:

- `план разработки топового лендинга/37-shadcnblocks-source-map.md`
- `план разработки топового лендинга/11-component-source-registry.md`
- active project `13-section-pattern-selection.md`, `18-section-storyboard-canvas.md`, `08-component-and-asset-plan.md`, and `33-shadcnblocks-selection.md` if present

## Workflow

1. Identify the job: marketing section, app section, ecommerce section, background, page, template, or small component.
2. Prefer native Tailwind/shadcn if the section need is simple.
3. If shadcnblocks helps, choose a specific live item page and registry item.
4. Record item ID, access status, source URL, registry URL, CLI command, dependencies, adaptation, mobile simplification, QA, `task-###`, and `chg-###` in `33-shadcnblocks-selection.md`.
5. Mark Pro/Premium items `reference-only` unless API-key access and license approval are explicit.
6. Add dependency impact to `08-component-and-asset-plan.md` only after selection is accepted.

## Source Rules

- Public item pages use `/block/<id>`, `/component/<id>`, `/page/<id>`, or `/template/<id>`.
- Public registry items use `https://www.shadcnblocks.com/r/<id>.json` or `/r/<id>`.
- Root `https://www.shadcnblocks.com/registry.json` returned 404 in the audit; do not use it.
- Free block examples like `hero1` and `feature1` returned 200 from `/r/<id>.json`.
- Pro examples like `hero125` and `pricing1` returned 401 without API authentication.
- Docs show public registry config as `"@shadcnblocks": "https://www.shadcnblocks.com/r/{name}.json"`.
- Docs show Pro auth with `SHADCNBLOCKS_API_KEY` and bearer headers.

## Acceptance Rules

- Accept only when the exact block/component improves section structure, proof, conversion clarity, or implementation speed.
- Replace demo copy, images, logos, icons, metrics, and claims with project evidence.
- Check license/access before copying source code or installing through CLI.
- Adapt layout, spacing, typography, palette, radius, surface treatment, and motion to the project style tile.
- Reject items that create a generic block-library look, dependency sprawl, fake proof, or a competing-component redistribution risk.

## Output

Fill or update:

- `33-shadcnblocks-selection.md`
- `13-section-pattern-selection.md`
- `18-section-storyboard-canvas.md`
- `08-component-and-asset-plan.md`
- related rows in `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`
