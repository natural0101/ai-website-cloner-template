---
name: aceternity-ui-catalog
description: Choose, adapt, or reject Aceternity UI components, registry items, blocks, templates, hero sections, bento grids, parallax/scroll effects, backgrounds, cards, navbars, pricing sections, and high-impact landing patterns. Use when a plan considers Aceternity UI or needs to decide whether an Aceternity component/block is appropriate, licensed, dependency-safe, adapted enough, mobile-safe, and worth its motion/accessibility risk.
---

# Aceternity UI Catalog

Use this skill to select Aceternity UI as a source of section patterns or exact registry components without cloning a recognizable template or importing heavy effects by impulse.

## Required Reading

Read before choosing an item:

```text
план разработки топового лендинга/35-aceternity-ui-source-map.md
план разработки топового лендинга/11-component-source-registry.md
план разработки топового лендинга/30-motion-reference-mining.md
```

If Aceternity UI is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/31-aceternity-ui-selection.md
```

## Source Facts

Latest audit recorded:

- Official site: `https://ui.aceternity.com`
- Registry index: `https://ui.aceternity.com/registry.json`
- Item registry pattern: `https://ui.aceternity.com/registry/<name>.json`
- CLI alias: `@aceternity/<name>`.
- Registry count: 270 items total: 109 `registry:ui`, 161 `registry:block`.
- Live crawl found 470 live HTML pages and 118 component pages.
- License/pro page exists and prohibits redistribution of paid items. Treat blocks/templates/pro as license-gated unless the user confirms access.

Install exact free registry components only:

```bash
npx shadcn@latest add @aceternity/bento-grid
npx shadcn@latest add https://ui.aceternity.com/registry/bento-grid.json
```

## Best Landing Uses

- `bento-grid`: feature/proof grid when content hierarchy is real.
- `hero-parallax`, `parallax-hero-images`: strong visual/product gallery hero.
- `sticky-scroll-reveal`, `tracing-beam`, `timeline`: product story or process explanation.
- `compare`: before/after or redesign proof.
- `animated-testimonials`, `infinite-moving-cards`: real testimonials only.
- `card-hover-effect`, `wobble-card`, `glare-card`, `card-spotlight`: one card system.
- `hero-highlight`, `pointer-highlight`, `text-generate-effect`, `flip-words`: short text emphasis.
- `background-beams`, `aurora-background`, `spotlight`, `background-lines`: one restrained hero/background layer.
- `safari`, `macbook-scroll`, `terminal`, `code-block`: product/code presentation.

## Avoid By Default

- `following-pointer`, `floating-dock`, `floating-navbar`, `loader`, `multi-step-loader`: landing usability risks.
- Heavy backgrounds like `vortex`, `sparkles`, `shooting-stars`, `stars-background`, `background-beams-with-collision`: reject unless the brand story earns them.
- `globe`, `3d-globe`, `canvas-reveal-effect`, `dither-shader`, shader/Three items: use only when 3D/WebGL is central and QA budget exists.
- `sidebar`, complex navbars, login/signup sections: app-shell sources, not default landing patterns.
- Any `registry:block` or template: reference-only unless access and license are confirmed.

## Selection Workflow

1. Start from the section job, source evidence, reference score and style tile.
2. Decide whether Aceternity is a reference pattern, exact component install, or rejected candidate.
3. Prefer exact `registry:ui` items for install; treat `registry:block` as reference unless license/access is confirmed.
4. Record source URL, registry item, command, dependencies, mobile behavior, reduced-motion fallback and adaptation notes.
5. Transform visual identity: change copy, assets, spacing, palette, icon family, rhythm and motion so the result is native to the project.
6. Reject tempting items that are too recognizable, too heavy or unsupported by evidence.

## Dependency Warnings

- `motion` appears across most registry items.
- `@tabler/icons-react` appears frequently and may duplicate `lucide-react`.
- Heavy deps include `three`, `@react-three/fiber`, `@react-three/drei`, `three-globe`, `cobe`, `@tsparticles/*`, `react-fast-marquee`, `react-dropzone`, `react-markdown`, `react-syntax-highlighter`.
- Do not add Three/R3F, particles, marquee, syntax highlighting or icon packs for a decorative effect.

## Hard Gates

- No Aceternity install without a row in `31-aceternity-ui-selection.md`.
- No `registry:block` or template copying without explicit license/access note.
- No 1:1 clone of Aceternity visual identity.
- No fake testimonials, fake logos, fake screenshots or fake integration visuals.
- No heavy WebGL/particle/scroll effect without reduced-motion fallback, mobile simplification and screenshot QA.
