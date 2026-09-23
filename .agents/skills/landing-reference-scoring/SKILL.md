---
name: landing-reference-scoring
description: Score and triage landing-page references before they influence visual direction, section plans, motion storyboards, component choices, or implementation handoff. Use when a plan has a reference board, visual inspiration URLs, competitor examples, motion references, UI galleries, Mobbin/Page Flows/Baymard/NNG evidence, or any decision about what to borrow, reject, or map to sections.
---

# Landing Reference Scoring

Use this skill after collecting references and before locking visual direction, section patterns, motion, or component sources.

## Required Files

Read:

```text
план разработки топового лендинга/18-reference-scoring-matrix.md
план разработки топового лендинга/projects/<slug>/03-reference-board.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
```

Then use the scorecard to update:

- `04-visual-benchmark.md`
- `05-visual-direction.md`
- `06-section-by-section-upgrade-plan.md`
- `07-animation-storyboard.md`
- `13-section-pattern-selection.md`
- `14-animate-ui-selection.md` if Animate UI is considered
- `evidence/reference-manifest.md`
- `evidence/decision-log.md`

## Workflow

1. Classify each reference as direct/domain, visual language, motion/interaction, component/source, flow/CRO, or anti-reference.
2. Score each reference 0 to 3 across the matrix criteria.
3. Assign a decision: core reference, section reference, detail reference, reject, or anti-reference.
4. Map each accepted reference to exact sections.
5. Write what to borrow and what not to copy.
6. Reject references with poor offer fit, unsafe license/access, fake-proof risk, inaccessible motion, or high implementation cost.
7. Update downstream planning files so every visual/motion/component claim points back to a scored reference.

## Decision Rules

- Conversion clarity beats visual taste.
- Direct/domain references cannot dictate art direction unless visual fit is also strong.
- Visual references cannot dictate structure unless offer and section fit are strong.
- Motion references need a motion purpose and reduced-motion fallback.
- Component sources are not design direction.
- A reference with high performance or accessibility risk must be simplified.
- Never borrow protected assets, exact layouts, brand identity, claims, testimonials, logos, or private screenshots.
- Keep at least one anti-reference when the market is full of common bad patterns.

## Minimum Quality Bar

A usable scorecard has:

- at least 5 concrete URLs across roles;
- at least 2 direct/domain references when available;
- at least 1 motion/interaction reference if animation is planned;
- at least 1 flow/CRO reference when signup, onboarding, checkout, pricing, or product flow matters;
- explicit rejected references;
- section mapping for every accepted reference;
- risk checks for mobile, accessibility, performance, license/access, and proof integrity.
