---
name: landing-change-traceability
description: Build and audit a landing-page change traceability matrix that connects source dossier evidence, user problems, references, brand DNA decisions, section decisions, motion/assets/viewport constraints, implementation tasks, and QA evidence. Use before implementation handoff, during plan self-review, when a plan feels like disconnected ideas, or when every proposed design change must prove why it exists and how it will be verified.
---

# Landing Change Traceability

Use this skill after section, reference, motion, asset, viewport, and task-graph planning are drafted. It creates the final connective tissue: every meaningful change needs a source, a reason, a visible outcome, an implementation task, and a verification method.

## Required Reading

Read:

```text
план разработки топового лендинга/32-change-traceability-matrix.md
план разработки топового лендинга/projects/<slug>/01-current-state-audit.md
план разработки топового лендинга/projects/<slug>/02-copy-and-offer-audit.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
план разработки топового лендинга/projects/<slug>/22-inspiration-synthesis.md
план разработки топового лендинга/projects/<slug>/25-brand-dna-map.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
план разработки топового лендинга/projects/<slug>/27-responsive-viewport-map.md
план разработки топового лендинга/projects/<slug>/20-implementation-task-graph.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/28-change-traceability-matrix.md
план разработки топового лендинга/projects/<slug>/21-plan-self-review.md
план разработки топового лендинга/projects/<slug>/11-implementation-handoff-prompt.md
```

## Workflow

1. List every meaningful planned change: copy, section order, layout, visual system, asset, motion, component, viewport, proof, form, SEO-sensitive content.
2. Give each change a stable `chg-###` ID.
3. Link each change to source evidence or a stated assumption.
4. Link accepted references, brand DNA decisions, section storyboard rows, asset IDs, motion IDs, responsive risks and task IDs.
5. State the visible result in browser terms.
6. State verification evidence: screenshot, command, accessibility check, responsive viewport, reduced-motion check, source diff or manual QA.
7. Mark orphan changes as blocked until they have a source, reason and QA.

## Change Classes

- Preserve: keep existing behavior/content/brand asset.
- Copy: headline, CTA, proof, FAQ, nav labels, form labels.
- Structure: section order, grouping, page rhythm.
- Visual: typography, color, spacing, surfaces, icons, imagery.
- Asset: screenshot, generated image, video, 3D, GLB, WebGL, logo.
- Motion: entrance, reveal, state, feedback, scroll, idle.
- Responsive: first viewport, crop, wrapping, breakpoint, overflow.
- Component: shadcn, Animate UI, custom component, library decision.
- Technical: routing, analytics, SEO, performance, accessibility.

## Hard Gates

- No implementation task without a traceable change ID.
- No major visual change without source evidence or a clearly marked assumption.
- No reference influence without borrow/transform/do-not-copy notes.
- No motion without motion reference, recipe, fallback and QA.
- No asset without asset ID, source/spec and mobile crop.
- No responsive-sensitive change without viewport QA.
- No protected route, nav label, form field, legal copy, SEO copy or analytics-sensitive label change unless explicitly allowed.

## Output Standard

`28-change-traceability-matrix.md` must include:

- change inventory;
- evidence links;
- reference/brand/section mapping;
- implementation task mapping;
- QA/evidence mapping;
- orphan or blocked decisions;
- protected-change review;
- handoff summary.

Use the matrix to patch weak plan files before handoff, not just to describe gaps.
