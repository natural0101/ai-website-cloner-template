---
name: landing-motion-safety-gate
description: Audit landing-page motion for accessibility, reduced-motion behavior, mobile comfort, Core Web Vitals, layout stability, library weight, and implementation risk. Use before approving animation storyboards, motion recipes, scroll choreography, WebGL/3D, Animate UI/Motion/GSAP effects, or final QA for a landing page.
---

# Landing Motion Safety Gate

Use this skill after motion references or recipes exist, before implementation handoff and again during final QA.

## Required Reading

Read:

```text
план разработки топового лендинга/53-motion-safety-source-map.md
план разработки топового лендинга/30-motion-reference-mining.md
план разработки топового лендинга/19-motion-recipe-library.md
```

If the active project folder exists, also read:

```text
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/27-responsive-viewport-map.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
```

## Workflow

1. List every accepted or proposed animated moment.
2. Confirm each moment has a purpose: hierarchy, storytelling, feedback or state transition.
3. Assign a motion safety verdict:
   - `safe`
   - `needs-simplification`
   - `static-fallback-only`
   - `reject`
4. Check reduced-motion fallback, mobile simplification, CTA visibility, layout stability, interaction accessibility and performance risk.
5. Reject or simplify motion that hides content, shifts layout, uses heavy properties, scroll hijacks, lacks fallback, adds a large dependency for a small flourish or threatens LCP/INP/CLS.
6. Write the accepted safer version back into the motion files.

## Required Output

Update rows in:

```text
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

For final QA, also update:

```text
план разработки топового лендинга/projects/<slug>/12-final-qa-report.md
план разработки топового лендинга/projects/<slug>/23-presentation-quality-review.md
```

## Row Requirements

Every accepted motion row must include:

- visible result;
- purpose;
- implementation level: CSS, Motion, Animate UI, Motion Primitives, GSAP, Three.js, Blender/static or custom;
- reduced-motion fallback;
- mobile simplification;
- performance risk;
- motion safety verdict;
- QA method.

## Non-Negotiable Rules

- Keep primary CTA and critical content visible.
- Prefer transform and opacity.
- Reserve layout space before reveal.
- Do not animate layout-affecting properties unless explicitly justified.
- Do not use raw scroll listeners or React state for frame-by-frame scroll animation.
- Do not ship blocking loaders, scroll hijack, custom cursor, autoplay critical carousel or endless decorative loops by default.
- Use GSAP only for real pin/scrub/timeline choreography.
- Use Three.js/WebGL only when runtime 3D is central and has a static fallback.
- Reduced motion must show the final content, not an empty hidden state.
