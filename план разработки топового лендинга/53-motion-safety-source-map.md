# Motion Safety Source Map

Дата проверки: 2026-07-03.

Этот файл нужен между motion references and implementation. Он превращает "анимация красивая" в safety decision: можно ли ее внедрять на лендинге без вреда для доступности, производительности, мобильного UX and conversion.

## Checked Official Sources

All sources below returned `200` during live check on 2026-07-03.

| Source | URL | Use |
| --- | --- | --- |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | Accessibility baseline and conformance reference. |
| WCAG Understanding 2.3.3 Animation from Interactions | https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html | Motion triggered by interaction can create vestibular risk; use as a strict caution for non-essential motion. |
| MDN `prefers-reduced-motion` | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion | CSS media feature for reduced-motion fallback. |
| web.dev prefers-reduced-motion | https://web.dev/articles/prefers-reduced-motion | Implementation and user-preference guidance. |
| web.dev animations guide | https://web.dev/articles/animations-guide | High-performance CSS animation guidance. |
| web.dev animations and performance | https://web.dev/articles/animations-and-performance | Property choice and animation performance guidance. |
| web.dev Core Web Vitals | https://web.dev/articles/vitals | LCP, INP and CLS field-quality targets. |
| web.dev LCP | https://web.dev/articles/lcp | Hero/media/LCP risk for first viewport animation. |
| Chrome DevTools animations | https://developer.chrome.com/docs/devtools/css/animations | Inspect, replay and debug CSS animations. |
| Material motion easing and duration | https://m3.material.io/styles/motion/easing-and-duration | Easing and duration model for system-like motion. |
| Fluent 2 motion | https://fluent2.microsoft.design/motion | Product UI motion principles and restraint. |
| Apple HIG motion | https://developer.apple.com/design/human-interface-guidelines/motion | Platform guidance for motion clarity and comfort. |
| Apple reduced motion evaluation criteria | https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/ | Concrete reduced-motion evaluation prompts. |

## Motion Safety Verdicts

Use one verdict per animated moment:

| Verdict | Meaning | Allowed next step |
| --- | --- | --- |
| `safe` | Uses transform/opacity or state-only changes, has reduced-motion fallback, does not affect CTA/content/layout, and has low mobile/perf risk. | Implement. |
| `needs-simplification` | Idea is useful but current version has motion, mobile, scroll, dependency or performance risk. | Simplify before implementation. |
| `static-fallback-only` | Runtime motion is not worth the risk, but final/static state is valuable. | Implement static render/state only. |
| `reject` | No user-facing purpose or unacceptable access, accessibility, performance, mobile or conversion risk. | Do not implement. |

## Hard Gates

Reject or simplify any motion that:

- hides or delays the primary CTA;
- shifts layout during reveal;
- animates large `width`, `height`, `top`, `left`, `filter`, heavy blur, large shadows or many SVG paths at once;
- uses scroll hijack, forced snap, blocking loader, custom cursor, autoplay carousel for critical content or endless background motion without purpose;
- uses React state or raw `scroll` listeners for frame-by-frame scroll animation;
- has no `prefers-reduced-motion` or equivalent fallback;
- requires GSAP, Three.js, WebGL or a component library for a tiny flourish;
- makes mobile content harder to read, tap or scroll;
- increases LCP/INP/CLS risk without an explicit mitigation.

## Safe Defaults

| Moment | Default safe implementation | Reduced-motion fallback |
| --- | --- | --- |
| Hover, focus, press | CSS transition on color, border, shadow, opacity or transform; 120ms to 220ms | color/border/focus state only |
| Section reveal | opacity and y 8 to 16px, once when in view; 420ms to 700ms | static final state |
| Hero entrance | one readable sequence; CTA visible throughout; no blocking loader | static final hero |
| Tab, pricing, accordion state | CSS or Motion layout/state transition; 180ms to 420ms | instant state swap with active style |
| Sticky story | CSS sticky or Motion; GSAP only for true pin/scrub story | normal stacked sections |
| 3D/WebGL | meaningful hero object, DPR clamp, static fallback, lazy if below fold | static render or paused first frame |

## Performance Budget

Use these as planning targets:

- LCP target: under 2.5s.
- INP target: under 200ms.
- CLS target: under 0.1.
- Hero animation must not block LCP content.
- Reserve dimensions for images, video, canvas, embeds and animated frames.
- Lazy-load below-fold heavy media, 3D and video.
- Prefer CSS for small interactions.
- Keep one major motion runtime per page unless the plan proves separate boundaries.

## Required Fields In Motion Plan

Every accepted motion row in `26-motion-reference-map.md`, `16-motion-recipe-selection.md` and `07-animation-storyboard.md` must include:

- motion purpose: hierarchy, storytelling, feedback or state transition;
- source/reference ID or explicit custom reason;
- visible result;
- implementation level: CSS, Motion, Animate UI, Motion Primitives, GSAP, Three.js, Blender/static or custom;
- reduced-motion fallback;
- mobile simplification;
- performance risk;
- motion safety verdict;
- QA method: screenshot, video capture, browser reduced-motion test, keyboard/focus test, Lighthouse/Web Vitals, DevTools animation inspection or Playwright check.

## Implementation Checks

Before handoff:

1. Verify no accepted motion is missing from `07-animation-storyboard.md`.
2. Verify every `needs-simplification` row has a simpler accepted replacement or is rejected.
3. Test reduced motion by forcing `prefers-reduced-motion: reduce`.
4. Confirm CTA, nav and first viewport content remain visible.
5. Confirm mobile layout uses simplified or static motion.
6. Confirm LCP asset dimensions and priority are not broken by animation.
7. Confirm no layout shift happens during reveal.

## Anti-Patterns

- "Smooth scroll animation" without trigger, visible result, fallback and QA.
- Animated gradient/noise/particles used to compensate for weak visual direction.
- Awwwards-style WebGL copied into a SaaS landing where buyer trust matters more than spectacle.
- Product screenshots hidden behind long reveal delays.
- Multiple libraries added because each effect came from a different gallery.
- Reduced-motion fallback that leaves empty or invisible content.
