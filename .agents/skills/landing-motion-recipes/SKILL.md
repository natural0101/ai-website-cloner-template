---
name: landing-motion-recipes
description: Choose and document purposeful section-level motion recipes for landing pages before writing detailed animation storyboards or implementation tasks. Use when planning hero entrances, scroll choreography, product reveals, proof fades, bento staggers, product flow tabs, pricing toggles, FAQ accordions, CTA feedback, image zoom, WebGL/3D idle motion, or when reviewing whether landing-page motion is visible, specific, reduced-motion safe, and presentation-ready.
---

# Landing Motion Recipes

Use this skill after reference scoring and section pattern selection, before finalizing `07-animation-storyboard.md`.

## Required Files

Read:

```text
план разработки топового лендинга/19-motion-recipe-library.md
план разработки топового лендинга/53-motion-safety-source-map.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
план разработки топового лендинга/projects/<slug>/13-section-pattern-selection.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. Read the visual direction dials, especially motion intensity.
2. List sections that actually need motion.
3. Select a recipe from `19-motion-recipe-library.md` or write a custom recipe with the same fields.
4. Record trigger, visible result, source/reference IDs, timing, library, reduced-motion fallback, mobile simplification, performance risk, motion safety verdict, and QA.
5. Reject tempting motion that does not support hierarchy, storytelling, feedback, or state transition.
6. Transfer accepted recipes into detailed animated moments in `07-animation-storyboard.md`.
7. Update component/dependency impact in `08-component-and-asset-plan.md`.

## Motion Budget Rules

- Select at most one hero-level motion system.
- Select at most one scroll choreography per page.
- Keep infinite or idle motion rare and meaningful.
- Prefer CSS for simple hover/focus/active states.
- Prefer Motion for React for React state, reveal, layout, presence, gestures, and light scroll.
- Use Animate UI or Motion Primitives only for reusable primitives that match the plan.
- Use GSAP only for real pin/scrub/scroll choreography.
- Use Three.js/WebGL only when 3D is central to the story.
- Use Blender/static render when runtime 3D adds cost without product value.

## Hard Bans

- No motion that hides or delays the primary CTA.
- No layout shift during reveal.
- No scroll animation implemented with React state.
- No custom cursor by default.
- No autoplay carousel for critical content.
- No particle/background effect without a section purpose.
- No endless loops inside feature cards.
- No missing reduced-motion fallback.
- No accepted recipe without a motion safety verdict.

## Output Standard

Every accepted recipe must answer:

- What changes visually?
- Why does the user benefit?
- Which section owns it?
- Which reference or source justifies it?
- What library implements it?
- What happens for reduced motion?
- What must be checked on mobile?
- What performance/accessibility risk remains?
- What is the motion safety verdict?
