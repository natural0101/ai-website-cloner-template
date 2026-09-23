---
name: cult-ui-catalog
description: Select verified Cult UI shadcn registry items for landing-page plans. Use when a landing needs textured cards/buttons, hero surfaces, browser mockups, polls, onboarding, terminal/code components, animated numbers/text, media hovers, small background details, or when filling `37-cult-ui-selection.md`; requires exact item, live registry URL, dependency impact, license, adaptation, mobile, reduced-motion, task ID, and change ID before install or copy.
---

# Cult UI Catalog

Use this skill when Cult UI is considered for a landing page, hero detail, product mockup, interactive card, poll/onboarding widget, or small motion/detail component.

## Required Reading

Read before choosing any item:

```text
план разработки топового лендинга/41-cult-ui-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

If Cult UI is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/37-cult-ui-selection.md
```

## Install Pattern

Cult UI is a shadcn-style registry. Prefer the exact live registry URL:

```bash
npx shadcn@latest add https://cult-ui.com/r/<item>.json
```

If the project has registry aliases configured, this namespace is valid:

```json
{
  "registries": {
    "@cult-ui": "https://cult-ui.com/r/{name}.json"
  }
}
```

Then install exact items only:

```bash
npx shadcn@latest add @cult-ui/mock-browser-window
```

Do not bulk-install demos. Treat `registry:component` `*-demo` entries as references unless a demo is explicitly needed as a short-lived preview.

## Best Landing Defaults

- Product proof: `mock-browser-window`, `code-block`, `terminal-animation`, `hover-video-player`.
- CTA and tactile details: `texture-button`, `cosmic-button`, `bg-animate-button`, `gradient-button-group`, `metal-button` only with dependency approval.
- Cards and surfaces: `texture-card`, `minimal-card`, `shift-card`, `cutout-card`, `morph-surface`, `edge-blur`.
- Metrics and text: `animated-number`, `text-animate`, `typewriter`, `gradient-heading`.
- Engagement widgets: `choice-poll`, `feature-poll`, `feature-voting`, `vote-tally`, `poll-widget`, `onboarding`.
- Quiet backgrounds: `bg-image-texture`, `texture-overlay`, `svg-shapes`, `svg-bands`, `stripe-bg-guides`.

## Risk Gates

Reject or heavily gate:

- `dock`, `dynamic-island`, `loading-carousel`, `toolbar-expandable`, and `sortable-list` on simple marketing pages.
- Shader/3D/heavy visuals such as `shader-lens-blur`, `hero-liquid-metal`, `hero-dithering`, `hero-color-panel`, `hero-heatmap`, `canvas-fractal-grid`, and `grid-beam` unless the hero concept earns them and mobile/performance QA is planned.
- Fake social proof such as `tweet-grid` unless content is real or clearly illustrative.
- AI widgets such as `prompt-library` and `ai-instructions` unless the product genuinely has that workflow.
- Neumorphism/pixel text/glass trends unless they match the brand direction.

## Selection Rules

1. Start with the section job and the project style tile.
2. Check whether native CSS, shadcn, Animate UI, Motion Primitives, Magic UI, React Bits, or existing components solve it with lower risk.
3. Pick one exact Cult UI item.
4. Verify `https://cult-ui.com/r/<item>.json` returns JSON before install.
5. Record source URL, registry URL, install command, dependencies, registry dependencies, adaptation, fallback, mobile behavior, task ID, change ID, and QA in `37-cult-ui-selection.md`.
6. Keep brand tokens from the landing plan. Do not import Cult UI's look wholesale.

## Acceptance

Use Cult UI only when it adds a visible, explainable landing improvement: clearer product proof, more tactile CTA, richer surface, better interaction, or stronger hero asset. If the reason is only "looks cool", reject it.
