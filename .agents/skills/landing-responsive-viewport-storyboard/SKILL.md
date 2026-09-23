---
name: landing-responsive-viewport-storyboard
description: Create explicit desktop, tablet, and mobile viewport storyboards for landing-page plans before implementation. Use when a landing plan needs hero first-viewport composition, responsive section transformations, text wrapping, asset crops, breakpoint behavior, overflow prevention, mobile CTA visibility, screenshot QA, or when an implemented page looks good on one size but breaks on another.
---

# Landing Responsive Viewport Storyboard

Use this skill after visual direction, section storyboard, asset queue, and motion reference map are drafted, before implementation tasks are finalized. The goal is to make each important viewport intentional, not a squeezed desktop.

## Required Reading

Read:

```text
план разработки топового лендинга/31-responsive-viewport-storyboard.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/27-responsive-viewport-map.md
план разработки топового лендинга/projects/<slug>/20-implementation-task-graph.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
план разработки топового лендинга/projects/<slug>/23-presentation-quality-review.md
```

## Viewports To Plan

Use these by default unless the source project has stronger analytics:

- `mobile-s`: 360 x 740
- `mobile`: 390 x 844
- `tablet`: 768 x 1024
- `laptop`: 1440 x 900
- `wide`: 1920 x 1080

Add route-specific viewports when the product needs them, such as kiosk, embedded widget, app webview, or fold height under 700px.

## Workflow

1. Mark first-viewport requirements: brand/product signal, offer, primary CTA, proof hint, and next-section hint.
2. For each section, state how layout transforms across mobile, tablet, laptop, and wide.
3. Define text wrapping rules for headings, CTA rows, nav labels, cards, metrics and long words.
4. Define asset crop rules per viewport, especially hero screenshots, product renders, 3D/WebGL, video, and diagrams.
5. Define motion simplification on mobile and reduced-motion interaction with the viewport.
6. Record overflow risks: horizontal scroll, clipped text, clipped visual, nav height, sticky overlap, cards resizing on hover, CTA pushed below fold.
7. Promote responsive tasks into `20-implementation-task-graph.md`.
8. Add screenshot QA entries for every planned viewport.

## Hard Gates

- First viewport must communicate what the page is, who it is for, why it matters, and how to act.
- Primary CTA must be visible in the first desktop viewport unless the brief explicitly rejects a CTA-first landing.
- Mobile hero must not clip important text, visual subject, or CTA.
- Wide desktop must not look empty, stretched, or like a centered mobile layout.
- Long words, button labels, nav labels, prices, metrics, and card titles must fit or wrap intentionally.
- Assets need stable aspect ratios and viewport-specific crops.
- Horizontal scrolling is a blocker unless it is a deliberate carousel with controls.

## Output Standard

`27-responsive-viewport-map.md` must include:

- viewport matrix;
- hero first-viewport plan;
- per-section responsive transformations;
- typography and wrapping rules;
- asset crop rules;
- motion simplification rules;
- overflow and sticky risk register;
- screenshot QA matrix;
- task graph updates.

Do not finalize implementation handoff until this map is filled or the plan explicitly explains why a single fixed viewport is acceptable.
