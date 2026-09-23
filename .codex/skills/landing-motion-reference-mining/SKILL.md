---
name: landing-motion-reference-mining
description: Map real motion and interaction references to landing-page sections before choosing animation recipes or writing animation storyboards. Use when planning hero entrances, scroll reveals, layout transitions, gesture feedback, text animation, product-flow motion, GSAP/ScrollTrigger scenes, Motion examples, Codrops demos, or when motion ideas feel generic, copied, excessive, or unsupported by references.
---

# Landing Motion Reference Mining

Use this skill after thematic/reference research and before `landing-motion-recipes`. The goal is to turn "make it smooth" into a small set of justified motion patterns tied to sections, references, implementation cost, and reduced-motion fallbacks.

## Required Reading

Read:

```text
план разработки топового лендинга/30-motion-reference-mining.md
план разработки топового лендинга/53-motion-safety-source-map.md
план разработки топового лендинга/19-motion-recipe-library.md
план разработки топового лендинга/projects/<slug>/24-thematic-reference-map.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
план разработки топового лендинга/projects/<slug>/22-inspiration-synthesis.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
```

## Source Lanes

Use these source lanes deliberately:

- Motion Examples: pattern inspiration for hero stagger, scroll image reveal, scroll text lines, layout transitions, copy buttons, number trends, toast stacks, draggable/gesture states, and text effects.
- Motion docs: implementation boundaries for scroll-triggered, scroll-linked, layout, gesture, and accessibility-safe React motion.
- GSAP ScrollTrigger docs/showcase: only for pinned, scrubbed, snapped, or timeline-heavy scroll scenes that Motion/CSS cannot express cleanly.
- Codrops Playground: experimental interaction reference. Borrow the interaction principle, not the demo identity.
- web.dev, MDN, and platform accessibility docs: performance and reduced-motion constraints.
- Existing project references: use product/category references first when they already show useful motion.

## Workflow

1. Read the page motion intensity from `05-visual-direction.md`.
2. List sections that need motion because it improves hierarchy, storytelling, feedback, or state transition.
3. For each section, gather at least one direct/product reference if available and one motion/source reference if motion will be implemented.
4. Classify each candidate as entrance, reveal, layout transition, state transition, gesture feedback, scroll-triggered, scroll-linked, text/number motion, ambient/idle, or 3D/canvas.
5. Record what to borrow, how to transform it for the brand, and what not to copy.
6. Reject candidates that add libraries, scroll complexity, or visual noise without section value.
7. Assign a motion safety verdict from `53-motion-safety-source-map.md`.
8. Promote only accepted candidates into `16-motion-recipe-selection.md` and then `07-animation-storyboard.md`.

## Decision Rules

- Prefer product/category references over generic animation galleries.
- Prefer CSS or Motion for React for common UI motion.
- Use Animate UI only when its exact item matches the selected pattern and fallback.
- Use GSAP only for real scroll choreography with pin/scrub/snap/timeline value.
- Use Three.js/WebGL only when runtime 3D is central to the story.
- Keep at most one signature hero motion and at most one heavy scroll scene per page.
- Every motion reference needs a reduced-motion fallback before promotion.
- Every promoted motion reference needs a motion safety verdict before implementation.

## Output Standard

`26-motion-reference-map.md` must include:

- source URLs and reference IDs;
- section mapping;
- visible result;
- trigger;
- borrow/transform/do-not-copy notes;
- library implication;
- reduced-motion fallback;
- mobile simplification;
- performance/accessibility risk;
- motion safety verdict;
- decision: accept, adapt, reject, or backlog.

Do not implement motion ideas that are missing from this map unless the plan explicitly marks them as custom and still fills the same fields.
