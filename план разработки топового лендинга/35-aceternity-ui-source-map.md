# Aceternity UI Source Map

Дата обновления: 2026-07-03.

Aceternity UI is a high-impact shadcn-style source for components, blocks and landing patterns. Use it as a pattern/reference source or exact component source only when the section earns the visual weight.

## Проверенные источники

| Source | URL | Result |
| --- | --- | --- |
| Website | https://ui.aceternity.com | 470 live HTML pages found during bounded crawl |
| Components | https://ui.aceternity.com/components | 118 component pages found |
| Blocks | https://ui.aceternity.com/blocks | live, includes many block categories |
| CLI docs | https://ui.aceternity.com/docs/cli | 200 |
| Registry index | https://ui.aceternity.com/registry.json | 200, 270 total items |
| Item registry example | https://ui.aceternity.com/registry/hero-parallax.json | 200 |
| License/pro page | https://ui.aceternity.com/licence | 200 |

Known route caveats:

- `/docs/installation` returned 404; use `/docs/cli`.
- `/registry.json` and `/registry/registry.json` both returned the registry index.
- `/r/registry.json` and `/r/<item>.json` returned 404. Do not use `/r/*` for Aceternity.
- Generated docs strings like `/registry/{name}.json` or `/registry/[component].json` are placeholders, not real source URLs.

## Registry Inventory

Registry: `https://ui.aceternity.com/registry.json`.

Count:

- 270 total items.
- 109 `registry:ui`.
- 161 `registry:block`.

Install model:

```bash
npx shadcn@latest add @aceternity/bento-grid
npx shadcn@latest add https://ui.aceternity.com/registry/bento-grid.json
```

Treat `registry:ui` as installable component candidates. Treat `registry:block`, templates and All-Access/pro pages as reference-only unless the user confirms license/access.

## Useful Families

| Family | Good candidates |
| --- | --- |
| Hero and feature sections | `hero-parallax`, `parallax-hero-images`, `container-scroll-animation`, `macbook-scroll`, `hero-highlight`, `spotlight`, `background-beams`, `aurora-background`, `background-lines` |
| Feature/proof grids | `bento-grid`, `layout-grid`, `wobble-card`, `card-hover-effect`, `focus-cards`, `glowing-effect`, `compare` |
| Product story motion | `sticky-scroll-reveal`, `tracing-beam`, `timeline`, `tabs`, `animated-modal`, `apple-cards-carousel` |
| Social proof | `animated-testimonials`, `infinite-moving-cards`, `animated-tooltip`, `avatar/testimonial related blocks` |
| Text emphasis | `text-generate-effect`, `flip-words`, `typewriter-effect`, `container-text-flip`, `pointer-highlight`, `colourful-text` |
| Product/code framing | `safari`, `terminal`, `code-block`, `macbook-scroll`, `world-map` |
| CTA and microinteraction | `moving-border`, `hover-border-gradient`, `magnetic-button`, `stateful-button` |

## High-Risk Candidates

- `following-pointer`, `floating-dock`, `floating-navbar`, `loader`, `multi-step-loader`: risky for landing usability.
- `vortex`, `sparkles`, `shooting-stars`, `stars-background`, `background-beams-with-collision`: easy to become decorative noise.
- `globe`, `3d-globe`, `canvas-reveal-effect`, `dither-shader`, `shaders`, `pixelated-canvas`, `webcam-pixel-grid`: heavy/WebGL/canvas category, needs dedicated QA.
- `sidebar`, navbars, login/signup blocks: app-shell patterns, not default landing sections.
- `registry:block` items: reference-only unless license/access is explicit.

## Dependency Warnings

Top dependency signals from registry:

- `motion`: 165 items.
- `@tabler/icons-react`: 66 items, may duplicate `lucide-react`.
- `react-fast-marquee`: 6 items.
- Heavy or special deps include `three`, `@react-three/fiber`, `@react-three/drei`, `three-globe`, `cobe`, `@tsparticles/react`, `@tsparticles/engine`, `@tsparticles/slim`, `react-dropzone`, `react-markdown`, `react-syntax-highlighter`, `react-icons`, `date-fns`, `svg-dotted-map`.

Decision rule: if the dependency is not already needed by the product story, reject or adapt the idea with native CSS, existing components, Motion Primitives, Animate UI or Magic UI.

## Best Landing Defaults

| Need | Candidate | Notes |
| --- | --- | --- |
| Premium feature grid | `bento-grid`, `wobble-card`, `card-hover-effect` | Adapt copy/assets/palette; do not clone visual identity. |
| Strong hero visual | `hero-parallax`, `parallax-hero-images`, `macbook-scroll` | Requires real product imagery and mobile crop plan. |
| Product process/story | `sticky-scroll-reveal`, `tracing-beam`, `timeline` | Use only when section sequence matters. |
| Before/after proof | `compare` | Strong for redesign/product results. |
| Testimonials | `animated-testimonials`, `infinite-moving-cards` | Real testimonial content only. |
| Text emphasis | `pointer-highlight`, `flip-words`, `text-generate-effect` | Short copy only. |
| CTA treatment | `moving-border`, `hover-border-gradient`, `magnetic-button` | One CTA variant max. |

## Required Output

Fill this file when Aceternity UI is considered:

```text
projects/<slug>/31-aceternity-ui-selection.md
```

Promote accepted rows into:

```text
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/28-change-traceability-matrix.md
```
