# Motion Primitives Source Map

Дата обновления: 2026-07-03.

Motion Primitives is a focused copy-paste motion source for React components built with Motion and Tailwind. Use it when a landing needs a precise local motion component, not a full animated component system.

## Проверенные источники

Direct crawl of `https://motion-primitives.com` returned `429` during the audit, so the authoritative check used the official GitHub repo and raw registry.

| Source | URL | Result |
| --- | --- | --- |
| Website | https://motion-primitives.com | Canonical site; direct crawl returned 429 during this audit |
| GitHub repo | https://github.com/ibelick/motion-primitives | 200 via GitHub API |
| Registry JSON | https://raw.githubusercontent.com/ibelick/motion-primitives/main/public/c/registry.json | 200, 33 `registry:ui` items |
| Installation source | https://raw.githubusercontent.com/ibelick/motion-primitives/main/app/docs/installation/page.mdx | 200 |
| Install command source | https://raw.githubusercontent.com/ibelick/motion-primitives/main/components/website/installation-cli.tsx | 200 |
| License | https://raw.githubusercontent.com/ibelick/motion-primitives/main/LICENCE.md | 200, MIT |
| README | https://raw.githubusercontent.com/ibelick/motion-primitives/main/README.md | 200, beta status noted |

## Install Model

Motion Primitives supports two exact-item install paths:

```bash
npx motion-primitives@latest add text-effect
npx shadcn@latest add "https://motion-primitives.com/c/text-effect.json"
```

Do not bulk-install the set. Install one item only after `projects/<slug>/29-motion-primitives-selection.md` names the item, purpose, fallback, dependency impact and QA plan.

## Registry Inventory

Source registry: `public/c/registry.json`.

Count: 33 items, all `registry:ui`.

| Group | Items |
| --- | --- |
| Core components | `accordion`, `animated-background`, `animated-group`, `border-trail`, `carousel`, `cursor`, `dialog`, `disclosure`, `in-view`, `infinite-slider`, `transition-panel` |
| Text and numbers | `text-effect`, `text-loop`, `text-morph`, `text-roll`, `text-scramble`, `text-shimmer`, `text-shimmer-wave`, `animated-number`, `sliding-number`, `spinning-text` |
| Interaction and surfaces | `magnetic`, `morphing-dialog`, `morphing-popover`, `dock`, `glow-effect`, `image-comparison`, `toolbar-dynamic`, `toolbar-expandable`, `progressive-blur`, `scroll-progress`, `spotlight`, `tilt` |

Dependency pattern:

- Most items depend on `motion`.
- `infinite-slider`, `toolbar-expandable`, and `sliding-number` also depend on `react-use-measure`.
- `dialog`, `morphing-dialog`, `morphing-popover`, `toolbar-dynamic`, and `toolbar-expandable` can add helper hooks.
- The repo package is a Next 14 / React 18 site, while this project is Next 16 / React 19. Inspect copied code before assuming it is drop-in.

## Best Landing Defaults

| Need | Good items | Notes |
| --- | --- | --- |
| Hero or section entrance | `animated-group`, `in-view`, `text-effect` | Use one coordinated system. Do not animate every line differently. |
| Feature/product state switch | `transition-panel`, `animated-background` | Good for tabs or claim/evidence panels. |
| Metrics and proof | `animated-number`, `sliding-number` | Use real numbers only. Reduced motion should show final value. |
| Short hero word motion | `text-morph`, `text-roll`, `text-scramble`, `text-loop` | Only for short phrases; never for long body copy. |
| CTA feedback | `magnetic`, restrained `glow-effect` | One primary CTA max. |
| Before/after proof | `image-comparison` | Strong for redesign, product results, visual comparisons. |
| Long-form story progress | `scroll-progress` | Only when scroll depth matters. |
| Surface polish | `spotlight`, `tilt`, `border-trail`, `progressive-blur` | Use on one important surface, not the whole page. |

## Reject Or Use Carefully

- `cursor`: reject by default because custom cursors often reduce usability.
- `dock`, `toolbar-dynamic`, `toolbar-expandable`: use only for embedded app/product surfaces.
- `infinite-slider`: use only with real logos or content; no fake social proof.
- `carousel`: avoid autoplay and do not hide core proof.
- `spinning-text`, `text-shimmer`, `text-shimmer-wave`: small labels only.
- `animated-background`, `glow-effect`, `spotlight`, `tilt`: keep below copy and CTA hierarchy.

## Decision Rules

1. Start from `26-motion-reference-map.md` and `16-motion-recipe-selection.md`.
2. Use native CSS or current components for simple fade/slide/reveal.
3. Use Motion Primitives when a focused component saves real implementation complexity.
4. Record exact item, docs/registry URL, install command and dependency impact in `29-motion-primitives-selection.md`.
5. Add mobile simplification and reduced-motion fallback before implementation.
6. Put rejected tempting items in the rejection table so they do not reappear during implementation.

## Required Output

Fill this file when Motion Primitives is considered:

```text
projects/<slug>/29-motion-primitives-selection.md
```

Promote accepted rows into:

```text
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/28-change-traceability-matrix.md
```
