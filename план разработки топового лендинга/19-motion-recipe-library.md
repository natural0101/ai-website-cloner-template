# Motion Recipe Library

Дата обновления: 2026-07-03.

Эта библиотека нужна после reference scoring, `26-motion-reference-map.md` and before `07-animation-storyboard.md`. Она превращает идею "добавить плавность" в конкретный рецепт: section, trigger, visible result, timing, library, fallback and QA.

Before accepting any recipe, read `53-motion-safety-source-map.md` and assign a motion safety verdict.

## Sources

- https://motion.dev/docs/react-scroll-animations
- https://examples.motion.dev/react
- https://motion.dev/docs/react-layout-animations
- https://motion.dev/docs/react-gestures
- https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- https://gsap.com/showcase/
- https://tympanus.net/codrops/category/playground/
- https://web.dev/articles/animations-guide
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- https://m3.material.io/styles/motion/easing-and-duration
- https://fluent2.microsoft.design/motion
- https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/
- `53-motion-safety-source-map.md`

## Motion Reference Gate

Before choosing a recipe, fill `projects/<slug>/26-motion-reference-map.md` or explicitly explain why a custom/static choice is enough. Accepted motion references must state source URL, pattern, trigger, visible result, borrow, transform, do-not-copy, library implication, reduced-motion fallback, mobile simplification and motion safety verdict.

## Motion Decision Ladder

1. Static state with strong hierarchy.
2. CSS transition for hover, focus, active, small opacity/transform.
3. Motion for React for state, reveal, layout, presence, gestures, light scroll.
4. Animate UI or Motion Primitives for known reusable primitives.
5. GSAP ScrollTrigger only for pinned/scrubbed story sections.
6. Three.js/WebGL only for meaningful runtime 3D.
7. Blender/static render when 3D should be beautiful but not interactive.

Do not move up the ladder unless the lower level cannot express the section story.

## Timing Tokens

| Token | Duration | Easing | Use |
| --- | ---: | --- | --- |
| micro-fast | 120ms to 180ms | ease-out | button/icon feedback |
| micro | 180ms to 260ms | ease-out | hover, focus, tap |
| reveal | 420ms to 700ms | cubic-bezier(0.2, 0.8, 0.2, 1) | section entrance |
| hero | 600ms to 900ms | cubic-bezier(0.16, 1, 0.3, 1) | first viewport entrance |
| state | 220ms to 420ms | ease-in-out | tabs, accordion, pricing toggle |
| scroll | scroll-linked | spring or scrub | sticky/pinned storytelling |
| idle | 6s to 14s loop | sine-like ease-in-out | subtle 3D/object breathing |

## Recipes

### Hero Signal Entrance

- Use for: hero on almost any landing.
- Visible result: eyebrow, headline, subhead, CTA and visual arrive in one readable sequence.
- Trigger: page load after content is available.
- Motion: text opacity 0 to 1, y 12 to 0; visual opacity 0 to 1, y 18 to 0, scale 0.98 to 1.
- Timing: 650ms to 850ms, small 70ms to 110ms stagger.
- Library: CSS or Motion for React.
- Reduced motion: final state instantly, no y movement.
- QA: CTA visible during and after entrance, no layout shift, LCP asset not blocked.

### Product Visual Reveal

- Use for: screenshot, app preview, product render, 3D still.
- Visible result: visual feels intentionally introduced, not pasted beside copy.
- Trigger: load or in-view once.
- Motion: clip/mask reveal or opacity/y reveal; avoid blur on text.
- Timing: 600ms to 900ms.
- Library: CSS clip-path for simple reveal, Motion for React for stateful reveal.
- Reduced motion: static final visual.
- QA: image dimensions reserved, crop readable on mobile.

### Proof Strip Fade

- Use for: logo strip, customer count, press logos, short metrics.
- Visible result: proof appears quietly after hero copy, without competing with CTA.
- Trigger: load or in-view once.
- Motion: opacity 0 to 1, y 8 to 0, 40ms to 70ms stagger.
- Timing: 350ms to 600ms.
- Library: CSS or Motion for React.
- Reduced motion: final opacity.
- QA: no fake logos, no flashing, contrast passes.

### Claim And Evidence Pair

- Use for: claim next to screenshot, metric, testimonial, workflow proof.
- Visible result: claim appears first, evidence follows as support.
- Trigger: in-view once.
- Motion: copy y 10 to 0; evidence y 16 to 0; optional scale 0.99 to 1.
- Timing: 500ms to 750ms.
- Library: Motion for React or Animate UI primitives/effects.
- Reduced motion: static stack.
- QA: evidence does not arrive so late that the claim feels unsupported.

### Bento Calm Stagger

- Use for: feature grid with 4 to 6 cards.
- Visible result: grid resolves in a fast scan pattern.
- Trigger: in-view once.
- Motion: cards opacity/y with max stagger 50ms.
- Timing: 450ms to 650ms.
- Library: CSS, Motion for React, Animate UI fade/slide.
- Reduced motion: static cards.
- QA: hover states do not resize cards, no endless loops inside cards.

### Product Flow Rail

- Use for: 3 to 5 product steps, onboarding, workflow, app promise.
- Visible result: active step changes preview; user understands sequence.
- Trigger: click/tap, keyboard, optional in-view initial reveal.
- Motion: preview crossfade or x 8 to 0, active indicator slide.
- Timing: 240ms to 420ms.
- Library: Motion for React, Animate UI tabs, Motion Primitives.
- Reduced motion: instant state change with clear active styling.
- QA: keyboard works, mobile tap targets are large, no hidden content.

### Sticky Problem To Solution Stack

- Use for: transformation story across 3 to 5 steps.
- Visible result: copy and visual change as scroll advances.
- Trigger: scroll.
- Motion: sticky panel, step fade/translate, optional progress rail.
- Timing: scroll-linked or 400ms triggered transitions.
- Library: Motion for React for simple sticky; GSAP ScrollTrigger for pin/scrub only when needed.
- Reduced motion: normal stacked sections.
- QA: no scroll hijack, mobile gets non-sticky layout, CTA still reachable.

### Pricing Toggle Clarity

- Use for: monthly/yearly, seat count, tier comparison.
- Visible result: price changes are legible and trustworthy.
- Trigger: toggle/click.
- Motion: number slide/count, plan highlight moves.
- Timing: 180ms to 320ms.
- Library: CSS, Motion for React, Animate UI numbers/toggle.
- Reduced motion: instant number swap.
- QA: no hidden price conditions, screen reader label remains clear.

### FAQ Accordion Ease

- Use for: objections, support, pricing, security, fit questions.
- Visible result: one answer expands without jarring page jump.
- Trigger: click/tap/keyboard.
- Motion: height/auto-height, opacity, slight y.
- Timing: 220ms to 360ms.
- Library: shadcn accordion, Animate UI accordion, native details with CSS.
- Reduced motion: instant expand/collapse.
- QA: focus-visible, keyboard, content remains mounted if SEO needs it.

### CTA Tactile Feedback

- Use for: primary CTA, copy button, submit button.
- Visible result: button feels responsive, not playful unless brand allows it.
- Trigger: hover, press, focus, loading, success.
- Motion: scale 1 to 0.98 on press; icon x 0 to 3; loading/success state.
- Timing: 120ms to 220ms.
- Library: CSS, Motion for React, Animate UI button primitives.
- Reduced motion: color/weight state only.
- QA: state does not shift layout, label remains visible.

### Image Zoom Detail

- Use for: product screenshot, gallery, portfolio, ecommerce detail.
- Visible result: hover/tap shows more detail without losing context.
- Trigger: hover or tap.
- Motion: image scale 1 to 1.04 inside clipped frame.
- Timing: 220ms to 420ms.
- Library: CSS or Animate UI image zoom.
- Reduced motion: no zoom, optional border/overlay.
- QA: no text inside image becomes unreadable, mobile tap does not trap.

### 3D Object Idle

- Use for: hero object, mascot, product metaphor, WebGL central scene.
- Visible result: object feels alive but readable.
- Trigger: idle after first render, optional pointer orbit.
- Motion: slow rotation, light shimmer, camera micro drift.
- Timing: 6s to 14s loop.
- Library: Three.js/WebGL or Blender-rendered sprite/video if runtime is unnecessary.
- Reduced motion: static render or paused first frame.
- QA: canvas nonblank, object framed, mobile fallback, no battery-heavy loop below fold.

## Recipe Selection Rules

- Select at most one hero-level motion system.
- Select at most one scroll choreography per page.
- Avoid infinite motion on informational content.
- Give every recipe a source reference or explain why it is custom.
- Keep motion intensity aligned with `05-visual-direction.md`.
- Record rejected motion ideas. Rejection is part of good taste.

## Output

Fill `projects/<slug>/16-motion-recipe-selection.md`, then write the final detailed sequence in `07-animation-storyboard.md`.
