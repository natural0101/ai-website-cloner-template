---
name: react-bits-catalog
description: Select, adapt, or reject exact React Bits animated components for landing-page plans. Use when considering React Bits text animations, interaction effects, animated components, backgrounds, shadcn/jsrepo install URLs, TS/Tailwind variants, dependency impact, performance risk, reduced-motion fallback, mobile simplification, or when filling `35-react-bits-selection.md`.
---

# React Bits Catalog

Use this skill when React Bits is a candidate source for a landing animation, animated component, text effect, background, gallery, cursor-like effect, or playful interaction.

## Required Reading

Read first:

```text
план разработки топового лендинга/39-react-bits-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

For a concrete project, also read:

```text
projects/<slug>/26-motion-reference-map.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/18-section-storyboard-canvas.md
projects/<slug>/35-react-bits-selection.md
```

## Source Rules

- Use official sources: `https://reactbits.dev`, `https://reactbits.dev/llms.txt`, `https://reactbits.dev/r/registry.json`, and `https://github.com/DavidHDev/react-bits`.
- Prefer TypeScript + Tailwind variant IDs for this project: `<Component>-TS-TW`.
- Exact install command pattern:

```bash
npx shadcn@latest add https://reactbits.dev/r/<Component>-TS-TW
```

- `https://reactbits.dev/r/<Component>-TS-TW.json` also returns JSON, but use the documented no-extension URL unless there is a tool-specific reason.
- Do not install a whole category or multiple variants of the same component.

## Selection Rules

1. Start from the section job and motion purpose, not the component name.
2. Prefer existing CSS, Motion Primitives, Animate UI, or Magic UI if they solve the same job with lower dependency cost.
3. Use React Bits when the component creates a concrete memorable moment: product tangibility, short hero word treatment, proof metric, media/gallery moment, or one meaningful background.
4. Record exact source page, registry URL, install command, dependencies, purpose, fallback, mobile simplification, task ID, change ID and QA in `35-react-bits-selection.md`.
5. Promote accepted rows to component plan, motion recipe, implementation task graph and traceability matrix.

## Good Landing Defaults

- Text: `BlurText`, `CountUp`, `Counter`, `DecryptedText`, `GradientText`, `RotatingText`, `ScrollVelocity`, `ShinyText`.
- Section entrance/detail: `AnimatedList`, `FadeContent`, `GlareHover`, `Magnet`, `SpotlightCard`, `TiltedCard`, `VariableProximity`.
- Product/media moments: `Carousel`, `Stack`, `Stepper`, `ImageTrail`, `PixelCard`, `DomeGallery` only when the media is real.
- Backgrounds: `Aurora`, `DotGrid`, `LightRays`, `Threads`, `Waves`, `Squares` only as one quiet layer behind content.

## Reject By Default

- Custom cursors: `BlobCursor`, `Crosshair`, `GhostCursor`, `TargetCursor`, `TextCursor` unless cursor interaction is product-critical.
- Heavy WebGL/3D/shader items using `three`, `@react-three/*`, `ogl`, `postprocessing`, `rapier`, `matter-js` unless the hero is explicitly a visual/3D experience and performance QA is budgeted.
- Physics/game-like backgrounds such as `Ballpit`, `Antigravity`, `FallingText` unless the brand earns playfulness.
- Long paragraph text effects. Text animation is for short display copy, metrics or labels.
- Autoplaying galleries/carousels that hide essential proof.

## Acceptance Rules

- One React Bits component per viewport moment unless the plan explicitly justifies more.
- Dependency impact must be accepted before install.
- Reduced-motion fallback must render useful static content, not an empty area.
- Mobile behavior must be simplified if hover, cursor, WebGL, scroll scrub or large canvas is involved.
- Screenshot QA must include desktop and mobile; canvas/WebGL choices need nonblank render and performance checks.
- License note must mention MIT + Commons Clause and avoid redistributing components as a standalone library.
