# Eldora UI Source Map

Дата проверки: 2026-07-03.

Eldora UI is an MIT, shadcn-compatible registry of landing components, device mockups, animated text, backgrounds and small section blocks. Use it as a gated source for exact product proof frames, developer/product UI moments, text motion and section structure when lower-risk local, Animate UI, Motion Primitives, SmoothUI or Skiper UI sources are not a better fit.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://eldoraui.site/ | 200 on `HEAD`; full `GET` can timeout |
| WWW website | https://www.eldoraui.site/ | full `GET` can timeout |
| Sitemap | https://eldoraui.site/sitemap.xml | 200, 56 URLs |
| Robots | https://eldoraui.site/robots.txt | 200 |
| LLM map | https://eldoraui.site/llms.txt | 200, 11883 bytes |
| Registry index | https://eldoraui.site/r/registry.json | 200, 115 items |
| WWW registry alias | https://www.eldoraui.site/registry.json | 200, 115 items |
| Exact item endpoints | https://eldoraui.site/r/&lt;name&gt;.json | 115/115 returned 200 |
| Wrong item path | https://eldoraui.site/registry/&lt;name&gt;.json | 404 on sampled items |
| Official shadcn registries index | https://ui.shadcn.com/r/registries.json | contains `@eldoraui` mapped to `https://eldoraui.site/r/{name}.json` |
| GitHub repo | https://github.com/karthikmudunuri/eldoraui | 200, MIT via GitHub API |
| GitHub license | https://raw.githubusercontent.com/karthikmudunuri/eldoraui/main/LICENSE.md | MIT |
| GitHub public registry | https://raw.githubusercontent.com/karthikmudunuri/eldoraui/main/apps/www/public/r/registry.json | 200, 115 items |
| GitHub components config | https://raw.githubusercontent.com/karthikmudunuri/eldoraui/main/apps/www/components.json | 200 |

## Site And Registry Inventory

Sitemap:

- 56 URLs total.
- 1 homepage.
- 45 docs pages.
- 10 blog pages.
- All 56 sitemap URLs returned 200 on `HEAD`.
- `llms.txt` lists component docs and is the best source for docs-page evidence.
- Full HTML `GET` requests against `www` and some docs pages can timeout. Use bare `eldoraui.site`, `HEAD`, `llms.txt`, exact registry endpoints and GitHub raw registry as reliable evidence.

Registry scan:

- 115 registry items total.
- 1 `registry:style` item.
- 39 `registry:ui` items.
- 58 `registry:example` items.
- 1 `registry:lib` item.
- 16 `registry:block` items.
- 115/115 exact endpoints `https://eldoraui.site/r/<name>.json` returned 200.
- `https://eldoraui.site/registry/<name>.json` returned 404 on sampled items and must not be used as install evidence.

Official shadcn registry:

```text
@eldoraui -> https://eldoraui.site/r/{name}.json
```

Install command:

```bash
npx shadcn@latest add @eldoraui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://eldoraui.site/r/<name>.json
```

## License Gate

Eldora UI is MIT.

- GitHub API reports MIT.
- Raw `LICENSE.md` on `main` is MIT.
- Raw public registry at `apps/www/public/r/registry.json` matches the public item count.

Do not redistribute Eldora UI as a competing component library. Do not leave demo copy, fake testimonials, fake logos, fake GitHub comments, fake terminal output or fake metrics as product proof.

## Registry Groups

| Group | Count | Notes |
| --- | ---: | --- |
| `registry:ui` | 39 | Main exact component pool. |
| `registry:example` | 58 | Demo/reference layer; do not select as normal install source. |
| `registry:block` | 16 | Headers, logo clouds, testimonials, features, CTA, pricing and footer sections. Use only when section structure is genuinely needed. |
| `registry:style` | 1 | `index`; dependency helper. |
| `registry:lib` | 1 | `utils`; dependency helper. |

Core UI items:

```text
safari-browser, macbook-pro, iphone-17-pro, ipad, browser, cobe-globe, github-inline-comments, animated-badge, grid, clerk-otp, marquee, integrations, terminal, testimonal-slider, map, svg-ripple-effect, animated-frameworks, blur-in-text, fade-text, gradual-spacing-text, letter-pull-up-text, multi-direction-slide-text, seperate-away-text, wavy-text, word-pull-up-text, novatrix-background, photon-beam, hacker-background, card-flip-hover, scale-letter-text, font-weight-text, animated-grid-pattern, live-button, animated-shiny-button, animated-list, orbit-rotation, logo-timeline, dock-text, holographic-card
```

Block items:

```text
header-01, header-02, logo-cloud-01, logo-cloud-02, logo-cloud-03, logo-cloud-04, testimonal-01, testimonal-02, testimonal-03, features-01, cta-01, cta-02, cta-03, pricing-01, pricing-02, footer-01
```

Source spelling caveat: registry item names include `testimonal-*` and `seperate-away-text`. Use exact item names for install, but do not copy misspellings into user-facing copy.

Common dependencies:

| Dependency | Count |
| --- | ---: |
| `react` | 35 |
| `motion` | 17 |
| `lucide-react` | 12 |
| `clsx` | 9 |
| `motion/react` | 9 |
| `next-themes` | 4 |
| `three` | 2 |
| `@headlessui/react` | 1 |
| `@radix-ui/react-accordion` | 1 |
| `class-variance-authority` | 1 |
| `cobe` | 1 |
| `ogl` | 1 |
| `react-icons` | 1 |
| `react-spring` | 1 |
| `react-three-fiber` | 1 |
| `tailwind-merge` | 1 |

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Product/browser/device proof | `safari-browser`, `browser`, `macbook-pro`, `iphone-17-pro`, `ipad` | Use only with real screenshots, product UI or workflow content. |
| Developer/product proof | `terminal`, `github-inline-comments`, `clerk-otp` | Replace demo terminal output, comments and OTP copy with real product story. |
| Integrations/geography | `integrations`, `cobe-globe`, `map`, `logo-timeline` | Globe/map need performance and mobile fallback. |
| Text motion | `fade-text`, `blur-in-text`, `word-pull-up-text`, `letter-pull-up-text`, `gradual-spacing-text`, `multi-direction-slide-text`, `wavy-text`, `font-weight-text` | Use for short hero words, labels and metrics, not paragraphs. |
| CTA and status detail | `animated-shiny-button`, `live-button`, `animated-badge` | One focused action/status detail only. |
| Background and depth | `grid`, `animated-grid-pattern`, `novatrix-background`, `hacker-background`, `photon-beam`, `holographic-card`, `svg-ripple-effect` | Keep behind content and check contrast. |
| Section structure | `header-*`, `logo-cloud-*`, `testimonal-*`, `features-01`, `cta-*`, `pricing-*`, `footer-01` | Use as structure/reference; rewrite copy, brands, logos and metrics. |

## Reject Or Use Carefully

- Reject `registry:example` items as normal install choices; use them as reference-only unless a selection file explains why the demo is needed.
- Reject full section blocks if they create a generic template identity.
- Reject fake testimonials, fake logos, fake terminal output, fake GitHub comments and fake integration names.
- Reject device frames if the product has no real screenshot or app surface.
- Reject `cobe-globe`, `three`, `ogl`, `react-three-fiber`, `react-spring` and heavy backgrounds unless the product story earns the runtime.
- Reject `motion` text effects when Animate UI, Motion Primitives, SmoothUI, Skiper UI, CSS or existing code covers the same result with lower risk.
- Reject backgrounds that lower contrast or compete with the CTA.
- Reject blocks that cannot be made mobile-readable without substantial adaptation.

## Selection Flow

1. Identify the section job and whether Eldora is install source, reference-only or rejected.
2. Check existing/local/shadcn, Animate UI, Motion Primitives, Magic UI, React Bits, SmoothUI, Skiper UI, HextaUI, MVPBlocks and custom code first.
3. Choose one exact Eldora item or explicitly reject Eldora for the section.
4. Verify docs URL from `llms.txt` or sitemap and endpoint `https://eldoraui.site/r/<name>.json`.
5. Record MIT license, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, performance risk, task ID, change ID and QA.
6. Map the item to `08-component-and-asset-plan.md`, `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`.

## Required Project File

```text
projects/<slug>/45-eldora-ui-selection.md
```

The file must record exact item, item type, source URL, endpoint URL, install command, MIT license, dependencies, registry dependencies, evidence path, visible purpose, adaptation, mobile behavior, reduced-motion fallback, performance risk, decision, task ID, change ID and QA evidence.
