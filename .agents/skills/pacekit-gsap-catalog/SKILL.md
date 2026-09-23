---
name: pacekit-gsap-catalog
description: Select, adapt, or reject exact PaceKit GSAP registry components for landing-page plans. Use when considering PaceKit GSAP text effects, scroll reveal, stagger reveal, buttons, AI UI details, liquid/glass/cursor effects, shadcn registry install URLs, `gsap` and `@gsap/react` dependency impact, reduced-motion fallback, mobile simplification, performance QA, or when filling `36-pacekit-gsap-selection.md`.
---

# PaceKit GSAP Catalog

Use this skill only when the project is considering a PaceKit GSAP component. Do not use PaceKit GSAP for basic fade, slide, hover or in-view effects that native CSS, Motion Primitives, Animate UI or existing components can handle.

## Required Reading

Read first:

```text
план разработки топового лендинга/40-pacekit-gsap-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

For a concrete project, also read:

```text
projects/<slug>/26-motion-reference-map.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/18-section-storyboard-canvas.md
projects/<slug>/36-pacekit-gsap-selection.md
```

## Source Rules

- Current live docs: `https://gsap.pacekit.dev/`.
- Current registry index: `https://gsap.pacekit.dev/r/registry.json`.
- Exact item URL: `https://gsap.pacekit.dev/r/<item>.json`.
- GitHub source: `https://github.com/pacekit/gsap`.
- Old `https://ui.paceui.com/` returns Vercel deployment 404 and must not be used as a live source.
- `https://www.paceui.com/` is the Pace UI umbrella site; its guessed `/r/gsap/*` endpoints are not valid for GSAP items.

Install pattern:

```bash
npx shadcn@latest add https://gsap.pacekit.dev/r/<item>.json
```

## Selection Rules

1. Start from the motion purpose and section storyboard.
2. Reject by default if CSS, Motion Primitives, Animate UI, React Bits or an existing component can provide the same result with less runtime cost.
3. Choose PaceKit GSAP only for GSAP-worthy choreography: text reveal with meaningful timing, AI response/state writing, stacked card choreography, scroll reveal/stagger that needs GSAP, or a button/card interaction where GSAP is already accepted.
4. Record item URL, install command, dependencies, registry dependencies, purpose, fallback, mobile simplification, task ID, change ID and QA in `36-pacekit-gsap-selection.md`.
5. Promote accepted rows to component plan, motion recipe, implementation task graph and traceability matrix.

## Good Landing Defaults

- Text: `reveal-text`, `scramble-text`, `draw-line-text`, `flip-reveal`.
- Scroll/story: `reveal-on-scroll`, `stagger-on-scroll`, `animated-stack`, `layered-stack`.
- Buttons/cards: `spring-button`, `fillable-button`, `tilt-card`, restrained `gradient-shadow`.
- AI/product UI: `ai-response-writer`, `ai-suggestions`, `ai-token-counter` only when the product actually has AI state/proof.

## Reject By Default

- `liquid-cursor`: custom cursor risk.
- `liquid-glass`: high visual trend risk unless the visual language earns it.
- `dot-loader`, `dot-flow`: loaders rarely improve landing conversion.
- `github-star-counter`: only for real open-source/devtool proof.
- `ai-modal-*`: only if the landing truthfully previews AI control flows.
- Any GSAP item for a simple reveal that CSS/Motion can handle.

## Acceptance Rules

- `gsap` and `@gsap/react` dependency impact must be accepted before install.
- Reduced-motion fallback must show final readable content.
- Mobile behavior must avoid hover/cursor-only interaction.
- Scroll items need screenshot/video QA across desktop and mobile.
- Keep client boundaries tight and avoid global timeline side effects.
- License note must mention MIT license from `pacekit/gsap`.
