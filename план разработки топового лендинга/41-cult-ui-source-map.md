# Cult UI Source Map

Дата проверки: 2026-07-03.

Cult UI is a shadcn-style registry with distinctive UI details, textured surfaces, hero pieces and small product widgets. Use it as a gated detail/source layer, not as a page-wide visual identity.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://www.cult-ui.com/ | 200 |
| Docs | https://www.cult-ui.com/docs | 200 |
| Installation docs | https://www.cult-ui.com/docs/installation | 200 |
| MCP docs | https://www.cult-ui.com/docs/mcp-server | 200 |
| Sitemap | https://www.cult-ui.com/sitemap.xml | 200, 87 URLs |
| Live registry | https://www.cult-ui.com/r/registry.json | 200, 157 items |
| Source repo | https://github.com/nolly-studio/cult-ui | 200 |
| Raw registry | https://raw.githubusercontent.com/nolly-studio/cult-ui/main/apps/www/public/r/registry.json | 200 |
| License | https://raw.githubusercontent.com/nolly-studio/cult-ui/main/LICENSE.md | MIT |

Root `https://cult-ui.com/` redirects to `https://www.cult-ui.com/`. Root `/registry.json` returns 404; use `/r/registry.json` and `/r/<item>.json`.

## Registry Inventory

Live registry count:

- 157 total items.
- 78 `registry:ui` items.
- 79 `registry:component` demo/example items.
- 157/157 item endpoints returned 200.

Sitemap count:

- 87 URLs.
- 86 docs URLs.
- 77 component docs URLs.

Treat `registry:ui` entries as the normal selection pool. Treat `registry:component` `*-demo` entries as examples or short-lived previews, not default implementation choices.

## Install Model

Exact URL install:

```bash
npx shadcn@latest add https://cult-ui.com/r/<item>.json
```

Registry alias from the docs:

```json
{
  "registries": {
    "@cult-ui": "https://cult-ui.com/r/{name}.json"
  }
}
```

Then:

```bash
npx shadcn@latest add @cult-ui/<item>
```

Use Cult UI only after `projects/<slug>/37-cult-ui-selection.md` records exact item, source URL, registry URL, install command, dependencies, registry dependencies, adaptation, fallback, mobile simplification, task ID, change ID and QA.

## Dependency Risk

Common dependencies in the 157-item registry:

| Count | Dependency |
| ---: | --- |
| 32 | `motion` |
| 8 | `@radix-ui/react-use-controllable-state` |
| 5 | `lucide-react` |
| 5 | `@paper-design/shaders-react` |
| 4 | `@radix-ui/react-slot` |
| 4 | `react-use-measure` |
| 4 | `geist` |
| 2 | `class-variance-authority` |
| 2 | `@hugeicons/core-free-icons` |
| 2 | `@hugeicons/react` |

One-off heavy or special dependencies include `three`, `jotai`, `dither-plugin`, `embla-carousel-autoplay`, `@radix-ui/react-scroll-area`, `metal-fx`, `vaul`, and `border-beam`.

Cult UI should lose to native CSS, existing components, Animate UI, Motion Primitives or Magic UI unless the exact component improves the page's visible story.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Product proof frame | `mock-browser-window`, `code-block`, `terminal-animation` | Good for devtool, AI, SaaS and product-preview sections with real content. |
| CTA tactility | `texture-button`, `cosmic-button`, `bg-animate-button`, `gradient-button-group` | Use one primary button treatment, not several competing button systems. |
| Surface richness | `texture-card`, `minimal-card`, `shift-card`, `cutout-card`, `morph-surface`, `edge-blur` | Adapt colors, radius and texture intensity to the style tile. |
| Metrics and short text | `animated-number`, `text-animate`, `typewriter`, `gradient-heading` | Use only for short hero words, metrics or concise labels. |
| Engagement widgets | `choice-poll`, `feature-poll`, `feature-voting`, `vote-tally`, `poll-widget`, `onboarding` | Use when the landing benefits from participatory or product-flow proof. |
| Media detail | `hover-video-player`, `bg-media`, `dither-image` | Verify mobile behavior and media performance. |
| Quiet background texture | `bg-image-texture`, `texture-overlay`, `svg-shapes`, `svg-shapes-animated`, `svg-bands`, `stripe-bg-guides` | Keep behind copy and CTA; avoid overpowering contrast. |

## Avoid By Default

- `dock`, `dynamic-island`, `loading-carousel`, `toolbar-expandable`, and `sortable-list` on ordinary landing pages.
- Shader-heavy or 3D-like visuals: `shader-lens-blur`, `hero-dithering`, `hero-color-panel`, `hero-static-radial-gradient`, `hero-heatmap`, `hero-liquid-metal`, `canvas-fractal-grid`, `grid-beam`.
- `tweet-grid` unless testimonials/social posts are real and allowed.
- `prompt-library` and `ai-instructions` unless the product genuinely contains those workflows.
- Neumorphism, pixel text, glass and metal effects unless the chosen visual direction earns that style.
- `registry:component` demo entries as production source without adaptation.

## Selection Flow

1. Identify the section job and visible gap.
2. Check lower-risk sources first: native CSS, shadcn, Animate UI, Motion Primitives, Magic UI, existing components.
3. Select one exact `registry:ui` item.
4. Verify the docs page and `https://cult-ui.com/r/<item>.json`.
5. Record dependency impact and registry dependencies.
6. Define reduced-motion fallback and mobile simplification.
7. Map the item to `task-###` and `chg-###`.
8. Add screenshot/video QA evidence after implementation.

## Required Project File

```text
projects/<slug>/37-cult-ui-selection.md
```

The file must record exact item, source URL, registry URL, install command, dependencies, registry dependencies, motion/visual purpose, adaptation, reduced-motion fallback, mobile simplification, decision, owner `task-###`, `chg-###`, risk and QA evidence.
