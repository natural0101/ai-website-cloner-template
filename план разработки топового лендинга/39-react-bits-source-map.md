# React Bits Source Map

Дата обновления: 2026-07-03.

React Bits is a large animated React component source for text animations, interaction effects, UI components and backgrounds. Use it as a source of one memorable section-level moment, not as a general component system.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://reactbits.dev/ | 200 during check |
| Sitemap | https://reactbits.dev/sitemap.xml | 200, 141 URLs |
| Agent docs | https://reactbits.dev/llms.txt | 200, component/category map and install commands |
| Registry JSON | https://reactbits.dev/r/registry.json | 200, 536 `registry:component` items |
| Item JSON sample | https://reactbits.dev/r/SplitText-TS-TW | 200 JSON |
| Item JSON sample with suffix | https://reactbits.dev/r/SplitText-TS-TW.json | 200 JSON |
| Source repo | https://github.com/DavidHDev/react-bits | 200 |
| License | https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md | MIT + Commons Clause |

GitHub `public/r` check found 537 JSON files: one `registry.json` plus 536 item JSON files. The 536 installable entries are 134 unique components, each in four variants: `JS-CSS`, `JS-TW`, `TS-CSS`, `TS-TW`.

## Site Inventory

Sitemap count:

- 141 URLs total.
- 1 home URL.
- 3 get-started URLs.
- 23 text animation pages.
- 30 animation pages.
- 36 component pages.
- 45 background pages.
- 3 extra pages: showcase, sponsors, favorites.

`llms.txt` gives the same useful category surface:

- `Text Animations`: 23.
- `Animations`: 30.
- `Components`: 36.
- `Backgrounds`: 45.

## Install Model

Prefer TypeScript + Tailwind for this project:

```bash
npx shadcn@latest add https://reactbits.dev/r/<Component>-TS-TW
```

Equivalent JSON URL works:

```bash
npx shadcn@latest add https://reactbits.dev/r/<Component>-TS-TW.json
```

React Bits also documents jsrepo:

```bash
npx jsrepo@latest add https://reactbits.dev/r/<Component>-TS-TW
```

Do not bulk-install. Use React Bits only after `projects/<slug>/35-react-bits-selection.md` records the exact item, category, source page, registry URL, install command, dependency impact, motion purpose, fallback, mobile simplification, task ID, change ID and QA.

## Dependency Risk

Representative `TS-TW` registry scan found:

| Dependency | Count |
| --- | ---: |
| `ogl` | 30 |
| `gsap` | 29 |
| `three` | 22 |
| `motion` | 20 |
| `@react-three/fiber` | 7 |
| `@react-three/drei` | 4 |
| `postprocessing` | 4 |
| `@gsap/react` | 2 |
| `react-icons` | 2 |

Other single-use dependencies observed include `@react-three/postprocessing`, `@use-gesture/react`, `face-api.js`, `gl-matrix`, `lenis`, `lucide-react`, `maath`, `matter-js`, and `react-router-dom`.

The same scan flagged 96 of 134 `TS-TW` components as heavy or interaction-risk because of WebGL, shaders, GSAP, Three, physics, cursor tracking, canvas-like behavior or similar implementation cost. This is why React Bits needs a stricter gate than Motion Primitives.

## Best Landing Defaults

| Need | Good candidates | Notes |
| --- | --- | --- |
| Hero word treatment | `BlurText`, `GradientText`, `RotatingText`, `ShinyText`, `DecryptedText` | Short phrases only; no body copy animation. |
| Proof metrics | `CountUp`, `Counter` | Real numbers only; fallback shows final number. |
| Section reveal | `AnimatedList`, `FadeContent` | Use one coordinated reveal system. |
| CTA or card detail | `Magnet`, `GlareHover`, `SpotlightCard`, `TiltedCard`, `ElectricBorder` | One important element, not every card. |
| Product/media moment | `Carousel`, `Stack`, `Stepper`, `PixelCard`, `DomeGallery` | Use real screenshots/media; no fake product proof. |
| Quiet ambient background | `Aurora`, `DotGrid`, `LightRays`, `Threads`, `Waves`, `Squares` | One background layer max; contrast and CTA must win. |
| Scroll/motion accent | `ScrollVelocity`, `VariableProximity`, restrained `ImageTrail` | Must map to a story beat. |

## Reject Or Use Carefully

- Reject custom cursor items by default: `BlobCursor`, `Crosshair`, `GhostCursor`, `TargetCursor`, `TextCursor`.
- Reject heavy WebGL/3D/shader items unless the landing's primary story is visual/3D and performance QA is budgeted: many backgrounds use `ogl`, `three`, `@react-three/*`, or `postprocessing`.
- Reject physics/game-like effects such as `Ballpit`, `Antigravity`, `FallingText`, `Cubes` unless the brand and product earn playfulness.
- Reject long paragraph effects and essential content hidden behind hover, pointer tracking, drag, autoplay carousel or canvas animation.
- Reject items that require new app shell assumptions such as `react-router-dom` unless the current project already uses them.
- Treat GSAP items as higher cost than Motion/CSS. If a simple reveal is enough, use native CSS, Motion Primitives, Animate UI or existing components.

## Selection Rules

1. Start from `26-motion-reference-map.md` and `16-motion-recipe-selection.md`.
2. Check whether native CSS, Motion Primitives, Animate UI, Magic UI or current components can do the job with lower risk.
3. Choose exact `TS-TW` item only when React Bits creates a specific visible result that the section needs.
4. Record source page, registry URL, install command, dependencies, purpose, fallback, mobile simplification, task ID, change ID and QA in:

```text
projects/<slug>/35-react-bits-selection.md
```

5. Promote accepted rows into:

```text
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/28-change-traceability-matrix.md
```

6. Keep rejected tempting items in the rejection table so the implementation agent does not re-add them later.
