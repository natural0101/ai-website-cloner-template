---
name: smoothui-catalog
description: Use SmoothUI safely as a shadcn-compatible source for animated React components and landing blocks. Trigger when choosing, installing, adapting, rejecting, or auditing SmoothUI items for landing pages, product UI proofs, animated controls, text effects, AI UI, section blocks, shadcn registry commands, or exact SmoothUI endpoints.
---

# SmoothUI Catalog

## Overview

Use SmoothUI only when an exact animated component or block improves a specific section job. Prefer native/local/shadcn, Animate UI, Motion Primitives, Magic UI, ReUI, Kokonut UI or MVPBlocks when they solve the same need with lower risk.

## Source Facts

- Main site: `https://smoothui.dev/`.
- Registry index: `https://smoothui.dev/r/registry.json`.
- Exact endpoint form: `https://smoothui.dev/r/<name>.json`.
- Component API: `https://smoothui.dev/api/v1/components?pageSize=100`.
- Component item API: `https://smoothui.dev/api/v1/components/<name>`.
- Blocks API is not reliable: `/api/v1/blocks` returned an empty list and `/api/v1/blocks/<name>` returned 500 during the 2026-07-03 audit.
- License: MIT on GitHub and npm package metadata.
- Verified inventory on 2026-07-03: 110 sitemap URLs, 107 registry items, 107/107 item endpoints live, 72 components, 35 block/shared items.

## Install Commands

Use one exact item at a time:

```bash
npx shadcn@latest add @smoothui/<name>
npx shadcn@latest add https://smoothui.dev/r/<name>.json
npx smoothui-cli@latest add <name>
```

Do not bulk-install all SmoothUI items. Record the exact command, endpoint, dependencies and owner task before installing.

## Selection Workflow

1. Read the local source map if it exists: `план разработки топового лендинга/46-smoothui-source-map.md`.
2. Identify the section job: CTA tactility, product UI proof, AI workflow, form control, metric motion, text effect or section structure.
3. Check existing project components and lower-risk sources first.
4. Pick one exact SmoothUI item or reject SmoothUI for that section.
5. For components, verify the docs URL, `/api/v1/components/<name>` metadata and exact `/r/<name>.json` endpoint.
6. For blocks, verify the docs category or `/blocks/preview/<name>` page and exact `/r/<name>.json` endpoint. Do not use `/api/v1/blocks` as evidence.
7. Record the item in `projects/<slug>/42-smoothui-selection.md` with dependencies, registry dependencies, MIT license, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID and QA evidence.

## Useful Landing Picks

- Section blocks: `header-1..6`, `cta-1..3`, `features-1..3`, `pricing-1..3`, `faq-1..4`, `stats-1..2`, `testimonials-1..3`, `footer-1..4`, `logo-cloud-1..4`.
- AI/product UI: `ai-input`, `ai-branch`, `agent-avatar`, `siri-orb`, `apple-invites`, `image-metadata-preview`, `switchboard-card`, `product-card`, `job-listing-component`.
- CTA/buttons: `smooth-button`, `magnetic-button`, `button-copy`, `dot-morph-button`, `clip-corners-button`.
- Controls/forms: `animated-input`, `animated-file-upload`, `animated-o-t-p-input`, `animated-tags`, `animated-toggle`, `animated-stepper`, `animated-tabs`, `animated-progress-bar`, `combobox`, `select`, `searchable-dropdown`.
- Proof/text motion: `number-flow`, `price-flow`, `reveal-text`, `scroll-reveal-paragraph`, `scramble-hover`, `typewriter-text`, `wave-text`.
- Layout/media: `expandable-cards`, `scrollable-card-stack`, `infinite-slider`, `phototab`, `glow-hover-card`, `interactive-image-selector`.

## Rejection Rules

- Reject root `/registry.json`; it returned 404 HTML.
- Reject `/api/v1/blocks` and `/api/v1/blocks/<name>` as block evidence.
- Reject `cursor-follow`, loaders and skeletons unless they solve a real interaction state.
- Reject `gooey-popover` unless `gsap` is already justified.
- Reject `tweet-card`, fake reviews, fake stars and fake logos unless evidence is real.
- Reject AI components for non-AI products.
- Reject broad replacement of local shadcn primitives.
- Add custom reduced-motion fallback for any item whose API metadata says `hasReducedMotion=false`.
- Reject anything that shifts layout, hides content, traps focus or breaks mobile scanning.
