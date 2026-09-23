---
name: magic-ui-catalog
description: Choose, adapt, or review Magic UI components, effects, blocks, and templates for landing-page plans. Use when a plan considers Magic UI, animated hero/background/text/logo/proof effects, marketing components, shadcn registry installs from magicui.design, or when deciding whether a Magic UI effect is worth its dependency, motion, accessibility, and presentation risk.
---

# Magic UI Catalog

Use this skill to select exact Magic UI items for a landing plan without turning the page into a shiny component demo.

## Required Reading

Read before choosing an item:

```text
план разработки топового лендинга/34-magic-ui-source-map.md
план разработки топового лендинга/11-component-source-registry.md
план разработки топового лендинга/30-motion-reference-mining.md
```

If Magic UI is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/30-magic-ui-selection.md
```

## Source Facts

Latest audit recorded:

- Official site: `https://magicui.design`
- Registry: `https://magicui.design/r/registry.json`
- Source repo: `https://github.com/magicuidesign/magicui`
- License: MIT.
- Live docs found: 91 docs pages, 77 component docs, 9 template docs.
- Registry count: 247 total items: 77 `registry:ui`, 168 `registry:example`, 1 style, 1 lib.

Install exact items only:

```bash
npx shadcn@latest add "https://magicui.design/r/marquee.json"
```

## Best Landing Uses

- `marquee`: real logo strip or real testimonial/source snippets.
- `hero-video-dialog`: product demo/video proof in hero or feature section.
- `bento-grid`: feature/proof grid when content has real hierarchy.
- `blur-fade`: simple section reveal if existing CSS is too weak.
- `number-ticker`: real metrics and proof numbers.
- `animated-list`: live activity/proof list when data is real.
- `animated-beam`: product workflow or integration map.
- `safari`, `iphone`, `android`, `terminal`: product/device/code framing.
- `highlighter`: mark key copy or objection language.
- `interactive-hover-button`, `shiny-button`, `rainbow-button`: one CTA variant when brand supports it.

## Avoid By Default

- `smooth-cursor`, `pointer`, `dock`, `cool-mode`: often harms landing usability.
- `confetti`: only for post-action success, not first viewport decoration.
- `particles`, `meteors`, `retro-grid`, `flickering-grid`, `animated-grid-pattern`: background noise unless it supports brand story.
- `sparkles-text`, `comic-text`, `spinning-text`, `text-3d-flip`: use only when tone clearly supports playful/display text.
- `globe`, `orbiting-circles`, `icon-cloud`: reject if they imply fake integrations/global proof.
- `tweet-card`: use only with real permission/source and clear relevance.

## Selection Workflow

1. Start from section job, source evidence and reference decision.
2. Prefer native CSS, existing components, shadcn, Animate UI or Motion Primitives for ordinary UI motion.
3. Choose Magic UI only for a strong marketing moment that improves clarity, proof, memory, product tangibility or CTA feedback.
4. Record exact item, source URL, install command, dependencies and files affected.
5. Define reduced-motion fallback, mobile simplification and contrast/readability checks.
6. Reject tempting items with a reason so another agent does not add them later.

## Dependency Warnings

- `motion` appears often.
- Watch for `framer-motion`, `canvas-confetti`, `react-tweet`, `cobe`, `shiki`, `next-themes`, `rough-notation`, and `@radix-ui/react-icons`.
- This project already has `motion` absent and uses React 19 / Next 16 / Tailwind v4. Inspect copied code before assuming compatibility.
- Do not install both `motion` and `framer-motion` for one decorative effect.

## Hard Gates

- No Magic UI install without a row in `30-magic-ui-selection.md`.
- No background effect if it weakens copy contrast or CTA hierarchy.
- No fake social proof, fake logos, fake tweets, fake integrations or fake activity.
- No effect without reduced-motion fallback and mobile behavior.
- No item that duplicates Motion Primitives, Animate UI or native CSS without a stated reason.
