---
name: motion-primitives-catalog
description: Choose, adapt, or review Motion Primitives components for landing-page motion. Use when a plan considers Motion Primitives, focused React motion components, text effects, transition panels, in-view reveals, animated numbers, image comparison, magnetic/tilt/glow/spotlight effects, or when deciding between Motion Primitives, Animate UI, native CSS, shadcn, Magic UI, GSAP, or custom Motion code.
---

# Motion Primitives Catalog

Use this skill to select exact Motion Primitives items for a landing plan without turning the page into an animation demo.

## Required Reading

Read before choosing an item:

```text
план разработки топового лендинга/33-motion-primitives-source-map.md
план разработки топового лендинга/11-component-source-registry.md
план разработки топового лендинга/30-motion-reference-mining.md
```

If Motion Primitives is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/29-motion-primitives-selection.md
```

## Source Facts

Latest project audit recorded:

- Official site: `https://motion-primitives.com`
- Source repo: `https://github.com/ibelick/motion-primitives`
- Registry: `https://raw.githubusercontent.com/ibelick/motion-primitives/main/public/c/registry.json`
- Registry count: 33 `registry:ui` items.
- License: MIT via `LICENCE.md`.
- Project status: README says beta and expects new components and significant updates.
- Direct site crawl may return 429; use the repo, raw registry and docs source when the site rate-limits.

Install exact items only:

```bash
npx motion-primitives@latest add text-effect
npx shadcn@latest add "https://motion-primitives.com/c/text-effect.json"
```

## Best Landing Uses

- `animated-group`: section or hero stagger with one coordinated entrance.
- `in-view`: simple reveal wrappers when native CSS is too weak.
- `transition-panel`: feature tabs, product state panels, proof comparisons.
- `text-effect`, `text-morph`, `text-scramble`, `text-roll`: short hero word or label motion only.
- `animated-number`, `sliding-number`: metrics, pricing or proof changes.
- `magnetic`: one primary CTA or important interaction target.
- `image-comparison`: before/after or redesign/proof comparison.
- `scroll-progress`: long editorial/product story progress, not every landing.
- `progressive-blur`: image edge treatment or carousel masking.
- `spotlight`, `tilt`, `glow-effect`, `border-trail`: one restrained surface accent.

## Avoid By Default

- `cursor`: custom cursors often harm usability and accessibility.
- `dock`, `toolbar-dynamic`, `toolbar-expandable`: app-like controls; use only when the landing embeds a product surface.
- `infinite-slider`: use only for real logos or real media, never fake proof.
- `spinning-text`, `text-shimmer`, `text-shimmer-wave`: use sparingly for tiny labels, not core claims.
- `carousel`: avoid autoplay and avoid hiding core proof inside slides.
- `animated-background`: keep quieter than copy and CTA.

## Selection Workflow

1. Start from the section job and motion reference, not the component list.
2. Prefer native CSS or existing Motion wrappers for simple opacity/transform reveals.
3. Pick Motion Primitives when the interaction is local, focused, and exact.
4. Record the exact item, source URL, install command, dependencies and files affected.
5. Define reduced-motion fallback and mobile simplification before implementation.
6. Reject tempting items with a reason so the implementation agent does not add them later.

## Compatibility Notes

- Most items depend on `motion`.
- `infinite-slider`, `toolbar-expandable`, and `sliding-number` also require `react-use-measure`.
- Some items add local hooks such as `useClickOutside` or `usePreventScroll`.
- This project already uses React 19, Next 16, Tailwind v4 and `lucide-react`; inspect generated code before assuming it matches current conventions.
- Keep client boundaries tight and preserve `@/lib/utils` / `cn()` aliases.

## Hard Gates

- No Motion Primitives install without a row in `29-motion-primitives-selection.md`.
- No item if the motion purpose cannot be stated as hierarchy, storytelling, feedback, state transition, proof or comparison.
- No text animation on long paragraphs.
- No motion without reduced-motion fallback and mobile behavior.
- No item that duplicates an existing shadcn, Animate UI or native CSS solution without a stated reason.
