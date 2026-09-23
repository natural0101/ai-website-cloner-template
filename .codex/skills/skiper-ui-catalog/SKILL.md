---
name: skiper-ui-catalog
description: Use when adding, selecting, adapting, or reviewing Skiper UI components from skiper-ui.com or the official @skiper-ui shadcn registry. Applies to uncommon landing motion, scroll effects, carousels, animated numbers, tooltips, inputs, video players, and Skiper UI references. Requires exact endpoint, access/license, premium/terms, dependency, reduced-motion, mobile, and anti-copy checks before install or adaptation.
---

# Skiper UI Catalog

Use this skill when a landing plan considers Skiper UI for uncommon motion components, scroll choreography, animated text, carousels, input details, custom tooltip/video/player surfaces, or visual inspiration from `skiper-ui.com`.

## Required First Step

Read the project source map:

```text
план разработки топового лендинга/48-skiper-ui-source-map.md
```

If Skiper UI is used or seriously considered for a project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/44-skiper-ui-selection.md
```

## Verified Model

- Official shadcn registry directory namespace: `@skiper-ui`.
- Official URL template: `https://skiper-ui.com/registry/{name}.json`.
- Public registry index: `https://skiper-ui.com/registry/registry.json`.
- Current registry scan: 38 `registry:ui` items, and 38/38 exact endpoints returned 200.
- Wrong registry paths: `/r/registry.json`, `/r/<name>.json`, and root `/registry.json`.
- Sitemap has 218 URLs: `/`, `/components`, `/pricing`, `/user`, 4 docs paths, 105 `/v1/skiper*` pages, and 105 `/preview/skiper*` pages.
- All 105 `/preview/skiper*` sitemap URLs returned 404 on `HEAD`.
- Public `/v1/skiper*` pages returned 200 on `HEAD`, but large HTML `GET` requests can timeout or reset.

## Access And License Gate

Skiper UI is not an MIT/open-source catalog in this plan.

- Pricing page advertises Premium and Exclusive paid access.
- Terms page includes restrictive website-content language.
- No official public GitHub source repo or MIT license was verified.
- Use only public registry items whose exact endpoint is reachable and whose use is acceptable for the project.
- Do not copy premium, paid, account-only, template, Figma, or private source material.
- Do not redistribute Skiper UI as a component library or component bundle.
- Record the terms/access decision in the project selection file before install or adaptation.

## Install Pattern

Prefer the official namespace only after the access gate is recorded:

```bash
npx shadcn@latest add @skiper-ui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://skiper-ui.com/registry/<name>.json
```

Use exact item names only. Do not bulk-install.

## Good Landing Uses

- `skiper16`, `skiper34`, `skiper87`: scroll-driven card/image/fade sections when the story needs progression.
- `skiper28`, `skiper31`, `skiper58`: short hero or navigation text motion.
- `skiper37`, `skiper89`: metrics and progress when the numbers are real.
- `skiper47`, `skiper48`, `skiper49`, `skiper50`, `skiper51`, `skiper54`: media or proof carousels with mobile simplification.
- `skiper52`, `skiper53`, `skiper64`: focused hover/product-detail moments.
- `skiper67`, `skiper101`, `skiper105`, `skiper106`: video, tooltip, and input details when they support a real workflow.

## Reject By Default

- Brand-named demos such as Apple/Nike/Vercel-style ideas unless adapted beyond recognition.
- `skiper17` and `skiper39` unless GSAP is already justified by the motion storyboard.
- `skiper25` unless sound is core to the product and has an accessible mute/default-off behavior.
- `skiper61` mouse-follow effects for ordinary landing content.
- `skiper65` debug/breakpoint tools outside internal development.
- Any `preview/skiper*` URL as evidence, because preview sitemap URLs currently return 404.
- Any component that creates fake product proof, fake metrics, fake users, fake dashboards, or decorative motion without section purpose.

## Selection Checklist

1. Name the section job and why native CSS, existing components, Animate UI, Motion Primitives, Magic UI, SmoothUI, HextaUI, React Bits, or custom code is not a better fit.
2. Verify the exact endpoint `https://skiper-ui.com/registry/<name>.json`.
3. Record install command, dependencies, registry dependencies, access/license gate, source URL, and endpoint URL.
4. Record reduced-motion fallback, mobile simplification, performance risk, and QA evidence.
5. Map the item to `task-###` and `chg-###`.
6. If the idea is only visual inspiration, mark it `reference-only` and do not install.

## Sources

- https://skiper-ui.com/
- https://skiper-ui.com/components
- https://skiper-ui.com/pricing
- https://skiper-ui.com/docs/terms-of-service
- https://skiper-ui.com/registry/registry.json
- https://ui.shadcn.com/r/registries.json
