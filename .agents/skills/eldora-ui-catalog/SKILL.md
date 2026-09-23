---
name: eldora-ui-catalog
description: Use when adding, selecting, adapting, or reviewing Eldora UI components from eldoraui.site or the official @eldoraui shadcn registry. Applies to landing components, animated text, device mockups, browser frames, terminal/GitHub proof, cobe globe/map/integrations visuals, holographic cards, logo timelines, backgrounds, CTA/pricing/footer blocks, and Eldora UI references. Requires exact endpoint, MIT/license, dependency, reduced-motion, mobile, performance, and anti-template-copy checks before install or adaptation.
---

# Eldora UI Catalog

Use this skill when a landing plan considers Eldora UI for exact installable components, landing blocks, product mockups, text motion, backgrounds, terminal/GitHub proof, integrations visuals, or visual references.

## Required First Step

Read the project source map:

```text
план разработки топового лендинга/49-eldora-ui-source-map.md
```

If Eldora UI is used or seriously considered for a project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/45-eldora-ui-selection.md
```

## Verified Model

- Official shadcn registry directory namespace: `@eldoraui`.
- Official URL template: `https://eldoraui.site/r/{name}.json`.
- Public registry index: `https://eldoraui.site/r/registry.json`.
- Current scan: 115 registry items.
- Item split: 1 style, 39 `registry:ui`, 58 `registry:example`, 1 lib, 16 `registry:block`.
- 115/115 exact endpoints returned 200.
- Wrong registry path: `https://eldoraui.site/registry/<name>.json`.
- Sitemap has 56 URLs: `/`, 45 docs pages and 10 blog pages. All returned 200 on `HEAD`.
- `llms.txt` is live and useful for component docs links.
- `www` full HTML `GET` can timeout; prefer bare `https://eldoraui.site`, `llms.txt`, registry endpoints and GitHub raw evidence.

## License Gate

Eldora UI is MIT.

- GitHub repo: `karthikmudunuri/eldoraui`.
- Raw license file: `LICENSE.md`.
- Public registry in GitHub: `apps/www/public/r/registry.json`.

Still record source URL, endpoint URL, dependencies and adaptation notes. Do not redistribute Eldora UI as a competing component library, and do not leave demo copy, fake testimonials, fake logos, fake GitHub comments or fake terminal output as product proof.

## Install Pattern

Official namespace:

```bash
npx shadcn@latest add @eldoraui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://eldoraui.site/r/<name>.json
```

Use exact item names only. Do not bulk-install.

## Best Landing Uses

- Device and browser proof: `safari-browser`, `browser`, `macbook-pro`, `iphone-17-pro`, `ipad`.
- Developer/product proof: `terminal`, `github-inline-comments`, `clerk-otp`.
- Integrations/geography: `integrations`, `cobe-globe`, `map`, `logo-timeline`.
- Text and CTA motion: `fade-text`, `blur-in-text`, `word-pull-up-text`, `letter-pull-up-text`, `gradual-spacing-text`, `animated-shiny-button`, `live-button`.
- Background and visual depth: `grid`, `animated-grid-pattern`, `novatrix-background`, `hacker-background`, `photon-beam`, `holographic-card`.
- Section structure: `header-01`, `header-02`, `logo-cloud-*`, `testimonal-*`, `features-01`, `cta-*`, `pricing-*`, `footer-01`.

## Reject By Default

- `registry:example` items as install choices unless the example itself is explicitly needed as reference-only evidence.
- Full section blocks when they would create generic template identity.
- Fake testimonials, fake logos, fake terminal output, fake GitHub comments and fake usage proof.
- `cobe-globe`, `three`, `ogl`, `react-three-fiber`, `react-spring`, and globe/background effects unless the product story earns the runtime cost.
- Device-frame components when the product has no real screenshot, workflow or app UI to show.
- Heavy motion when Animate UI, Motion Primitives, SmoothUI, Skiper UI or custom lightweight code already solves the section.
- Misspelled source item names such as `testimonal-*` and `seperate-away-text` must be recorded exactly for install, but exposed copy should use correct spelling.

## Selection Checklist

1. Name the section job and whether Eldora is install source, reference-only, or rejected.
2. Verify exact endpoint `https://eldoraui.site/r/<name>.json`.
3. Record docs URL from `llms.txt` or sitemap.
4. Record MIT license, install command, dependencies, registry dependencies, runtime cost, reduced-motion fallback, mobile simplification and QA evidence.
5. Map the item to `task-###` and `chg-###`.

## Sources

- https://eldoraui.site/
- https://eldoraui.site/llms.txt
- https://eldoraui.site/r/registry.json
- https://github.com/karthikmudunuri/eldoraui
- https://raw.githubusercontent.com/karthikmudunuri/eldoraui/main/LICENSE.md
- https://ui.shadcn.com/r/registries.json
