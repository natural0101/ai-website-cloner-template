---
name: landing-section-storyboard
description: Build per-section storyboard canvases for landing-page plans before implementation. Use when a landing plan needs each section to specify user job, frame sketch, copy/proof, visual style, asset, reference IDs, selected pattern, motion recipe, component source, mobile frame, and QA risk, or when vague section notes must become implementable screen-by-screen direction.
---

# Landing Section Storyboard

Use this skill after style tile, reference scorecard, section pattern selection, asset planning, and motion recipe selection. It is the bridge from planning to implementation tasks.

## Required Files

Read:

```text
план разработки топового лендинга/21-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/13-section-pattern-selection.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/09-implementation-tasks.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. List every major section in page order.
2. For each section, write the user job and visible frame sketch.
3. Link copy/proof to the offer audit and avoid invented claims.
4. Link visual style to `17-visual-style-tile.md`.
5. Link reference IDs to `15-reference-scorecard.md`.
6. Link pattern to `13-section-pattern-selection.md`.
7. Link motion recipe to `16-motion-recipe-selection.md` or write "none".
8. Link asset and component/source to `08-component-and-asset-plan.md`.
9. Define mobile frame and QA risk.
10. Convert rows into implementation tasks.

## Rules

- Every section needs a user job.
- Every accepted reference must be used only where it was scored and mapped.
- Every animated section must have a selected motion recipe and reduced-motion fallback.
- Every visual rule must match the style tile.
- Every asset claim must be backed by an existing asset or an asset production spec.
- Do not add decorative sections without a conversion or comprehension job.
- Do not invent proof, testimonials, metrics, logos, or product screenshots.

## Output Standard

A strong canvas lets another agent imagine the whole page without opening a design tool:

- first viewport composition is clear;
- section rhythm is visible;
- proof and objections are placed intentionally;
- assets and crops are specified;
- motion moments are scoped;
- mobile transformations are explicit;
- QA risks are concrete.
