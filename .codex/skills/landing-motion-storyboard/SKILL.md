---
name: landing-motion-storyboard
description: Turn a landing-page plan into a precise motion storyboard with triggers, timing, libraries, section choreography, micro-interactions, reduced-motion fallbacks, and performance checks. Use when adding animations, scroll storytelling, WebGL/3D motion, hover states, or reviewing whether motion is purposeful.
---

# Landing Motion Storyboard

Use this skill after the structure and visual direction are clear. Motion should explain, guide, or respond. It should not be added because a library exists.

## Inputs

- Section-by-section plan.
- Visual direction.
- Component source plan.
- `53-motion-safety-source-map.md`.
- Existing animation libraries from `package.json`.
- User motion preference if stated.

## Motion Purpose Labels

Every animation must use one purpose:

- Hierarchy: draw attention to the most important element.
- Storytelling: reveal content in a narrative sequence.
- Feedback: acknowledge hover, tap, form, click, drag, or selection.
- State transition: show that UI changed state.

If an animation has no purpose, delete it.

## Library Selection

- CSS transitions: simple hover, active, focus, small opacity/transform changes.
- Motion for React: React state, gestures, reveal, layout, presence, light scroll.
- Animate UI / Motion Primitives: reusable animated primitives.
- GSAP ScrollTrigger: pinned or scrubbed scroll choreography only.
- Three.js/WebGL: real 3D/canvas scene only.
- Blender render: when runtime 3D is not needed.

Do not mix GSAP, Motion, and Three.js in the same component tree without clear boundaries.

## Storyboard Format

For each animated moment:

- Section:
- Element:
- Trigger: load, in-view, hover, tap, scroll, drag, state change.
- Before:
- After:
- Motion values: opacity, x/y, scale, rotate, blur, path, camera, light.
- Duration/easing:
- Stagger:
- Purpose:
- Library:
- Component boundary:
- Reduced-motion fallback:
- Mobile simplification:
- Performance risk:
- Motion safety verdict:
- QA check:

## Timing Guidance

- Hero entrance: 400ms to 900ms, no blocking loader.
- Micro-interaction: 120ms to 260ms.
- Section reveal: 450ms to 800ms.
- Scroll scrub: tied to scroll, no surprise jumps.
- 3D idle: slow enough to read as premium, not restless.

## Hard Bans

- No animation that hides CTA.
- No layout shift during reveal.
- No scroll listener in React state.
- No infinite loops on informational cards.
- No more than one marquee per page.
- No reduced-motion omission.
- No missing motion safety verdict.
- No heavy 3D if a static render communicates the same thing.

## Output

Create or update `07-animation-storyboard.md` with all animated moments and fallbacks. If motion is not needed, state that and explain what static interaction states are enough.
