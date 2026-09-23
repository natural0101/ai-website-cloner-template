# Motion Reference Mining

Дата обновления: 2026-07-03.

Этот слой нужен между thematic/reference scoring and `16-motion-recipe-selection.md`. Он отвечает на вопрос: не просто "какая анимация будет", а "из какого реального motion reference мы взяли принцип, что именно трансформируем, что не копируем, какой риск и fallback".

Before promoting any motion candidate, read `53-motion-safety-source-map.md` and assign a motion safety verdict.

## Проверенные источники

Все источники ниже проверены live-запросом 2026-07-03 and returned 200.

| Source | URL | Role |
| --- | --- | --- |
| Motion Examples | https://examples.motion.dev/react | Pattern gallery for hero stagger, scroll reveals, layout transitions, gestures, text/number effects and UI feedback. Use as pattern reference, not as visual identity. |
| Motion scroll docs | https://motion.dev/docs/react-scroll-animations | Implementation guidance for scroll-triggered and scroll-linked React animation. |
| Motion layout docs | https://motion.dev/docs/react-layout-animations | Layout, FLIP and shared-element transition guidance. |
| Motion gestures docs | https://motion.dev/docs/react-gestures | Hover, press, drag and gesture feedback guidance. |
| GSAP ScrollTrigger docs | https://gsap.com/docs/v3/Plugins/ScrollTrigger/ | Use only for pinned, scrubbed, snapped or timeline-heavy scroll scenes. |
| GSAP Showcase | https://gsap.com/showcase/ | Reference for high-polish motion systems, with strict adaptation and performance review. |
| Codrops Playground | https://tympanus.net/codrops/category/playground/ | Experimental interaction ideas. Borrow principles, not demo identity. |
| web.dev animations guide | https://web.dev/articles/animations-guide | Performance guidance for high-performance CSS animation. |
| MDN prefers-reduced-motion | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | Reduced-motion source for fallback requirements. |
| Motion safety source map | `53-motion-safety-source-map.md` | Landing-specific safety verdicts, hard gates, Core Web Vitals budget, reduced-motion and QA requirements. |

## When To Use

Use this whenever a plan says:

- hero entrance;
- scroll reveal, sticky story, horizontal pan or parallax;
- layout/shared element transition;
- hover/tap/drag feedback;
- animated metrics or text;
- product-flow tabs or state transitions;
- 3D/canvas idle motion;
- any Animate UI, SmoothUI, Motion, GSAP or Codrops-inspired idea.

If the page is static and motion intensity is low, still fill the rejection section so the implementation agent does not add shine later without context.

## Search Lanes

| Lane | Query/source pattern | Best for | Caution |
| --- | --- | --- | --- |
| Product motion | `{category} website animation`, `{category} interactive landing page` | Direct product fit | Competitors may have claims/assets you cannot copy. |
| Motion Examples | `examples.motion.dev/react` plus pattern names like `hero-stagger`, `scroll-image-reveal`, `scroll-text-lines`, `scroll-zoom-hero`, `copy-button`, `number-trend` | React motion behavior | Do not treat example visuals as brand direction. |
| Motion docs | Motion scroll/layout/gestures docs | Implementation feasibility | Docs are not a design reference by themselves. |
| GSAP | ScrollTrigger docs/showcase and `GSAP {interaction pattern}` | Pinned or scrubbed storytelling | Avoid for simple reveals. |
| Codrops | `Codrops {interaction pattern}` or Playground | Experimental interaction principle | High risk of looking like a demo if copied. |
| Accessibility/performance | web.dev, MDN, Apple/Material/Fluent motion guidance | QA gates | Use to constrain, not to decorate. |

## Reference Extraction Schema

For each motion reference, capture:

- Reference ID and URL.
- Source type: product, Motion example, docs, GSAP, Codrops, component library, platform guidance.
- Section and user job.
- Trigger: load, in-view, hover, press, drag, scroll, state change, idle.
- Visible result in one sentence.
- Borrow: the motion principle to reuse.
- Transform: how it becomes native to this brand and section.
- Do not copy: visual identity, exact timing, assets, claims, gimmick, or code without license.
- Library implication: CSS, Motion, Animate UI, SmoothUI, GSAP, Three.js, Blender/static.
- Reduced-motion fallback.
- Mobile simplification.
- Performance/accessibility risk.
- Motion safety verdict: safe, needs-simplification, static-fallback-only or reject.
- Decision: accept, adapt, reject, backlog.

## Pattern To Section Map

| Section need | Good motion reference type | Default implementation |
| --- | --- | --- |
| Hero clarity | Hero stagger, product visual reveal, scroll-zoom hero only when product earns it | CSS or Motion for React |
| Proof and metrics | Counting/sliding number, proof strip fade | CSS or Motion for React |
| Feature explanation | Claim/evidence pair, bento calm stagger, product flow rail | Motion for React, Animate UI or SmoothUI tabs/effects |
| Workflow story | Sticky problem-to-solution stack, scroll image reveal | Motion for React, GSAP only if pinned/scrubbed |
| Pricing clarity | Toggle state transition, number trend | CSS, Motion for React, Animate UI or SmoothUI number primitive |
| FAQ and objections | Auto-height disclosure, accordion ease | shadcn/Radix/Headless/Animate UI/SmoothUI |
| CTA feedback | Press scale, icon nudge, copy success | CSS or Motion for React |
| Product/object presence | Slow 3D idle or static render reveal | Three.js/WebGL or Blender/static |

## Acceptance Rules

- Accept a motion reference only if it supports hierarchy, storytelling, feedback or state transition.
- Keep the CTA visible and stable during hero motion.
- Prefer transform and opacity; avoid layout-affecting animation.
- Do not add GSAP, Three.js or a component library for a single tiny flourish.
- Do not promote custom cursor, scroll hijack, autoplay carousel, full-page loader or particle background unless the brief clearly requires it.
- Every accepted motion reference must have a reduced-motion fallback and mobile simplification.
- Every accepted motion reference must have a `safe` or simplified `needs-simplification` resolved verdict before implementation.

## Required Output

Fill:

```text
projects/<slug>/26-motion-reference-map.md
```

Then promote accepted rows into:

```text
projects/<slug>/29-motion-primitives-selection.md
projects/<slug>/30-magic-ui-selection.md
projects/<slug>/31-aceternity-ui-selection.md
projects/<slug>/32-tailark-section-selection.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/07-animation-storyboard.md
projects/<slug>/08-component-and-asset-plan.md
```

The implementation agent must not add motion that is absent from `26-motion-reference-map.md`, `16-motion-recipe-selection.md` and `07-animation-storyboard.md`.
