---
name: landing-visual-direction
description: Create concrete landing-page visual direction and style tiles before implementation. Use when a landing plan needs typography, color, spacing, radius, surface, shadows, icon style, asset treatment, section composition rules, anti-slop constraints, or when vague labels like premium, modern, beautiful, Awwwards, SaaS, clean, editorial, or luxury must be converted into buildable design tokens and section rules.
---

# Landing Visual Direction

Use this skill after reference scoring and visual benchmarking, before final section tasks and implementation.

## Required Files

Read:

```text
план разработки топового лендинга/20-visual-direction-style-tiles.md
план разработки топового лендинга/projects/<slug>/01-current-state-audit.md
план разработки топового лендинга/projects/<slug>/04-visual-benchmark.md
план разработки топового лендинга/projects/<slug>/25-brand-dna-map.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. Read the Brand DNA map and list preserve/evolve/remove/introduce/protect constraints.
2. Write a one-sentence visual read: landing type, audience, visual language, aesthetic/system family, evidence.
3. Choose one primary direction and optionally one rejected alternate.
4. Fill the token sheet: typography, color, spacing, radius, surface, shadow/border, icons, assets, motion feel.
5. Define section style rules: composition family, visual density, asset treatment, surface, accent use, mobile transformation.
6. Write the do-not-do list for this project.
7. Update downstream files so implementation tasks use the same tokens and section rules.

## Decision Rules

- Product, audience, and CTA choose the aesthetic.
- Existing brand tokens are starting material, not noise.
- Protected Brand DNA decisions beat visual references.
- Reference scorecard decisions beat random taste.
- One accent system, one radius system, one icon family, one surface language.
- Real product proof beats decorative visuals.
- Style tile can reject a beautiful reference if it harms trust, conversion, accessibility, or performance.

## Anti-Slop Checks

- No "modern premium" without token values.
- No AI-purple or dark mesh default.
- No beige/brass premium-consumer default unless brand requires it.
- No fake dashboard screenshots or fake proof.
- No three equal cards as default visual plan.
- No mixed radii, shadows, icon families, or section themes.
- No style flip between adjacent sections without a reason.
- No visual reference used outside its scored section.

## Output Standard

A useful style tile lets another agent implement without guessing:

- exact visual read;
- token values or tight token ranges;
- reference IDs behind choices;
- section-by-section visual rules;
- mobile transformations;
- rejected directions;
- implementation notes and QA checks.
