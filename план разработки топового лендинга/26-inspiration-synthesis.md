# Inspiration Synthesis

Дата обновления: 2026-07-03.

Источники:

- https://www.nngroup.com/articles/competitive-usability-evaluations/
- https://www.nngroup.com/articles/benchmarking-ux/
- https://www.figma.com/resource-library/how-to-make-a-mood-board/
- https://www.figma.com/blog/design-critiques-at-figma/
- https://www.atlassian.com/blog/loom/design-review
- https://m3.material.io/styles/motion/overview

Этот слой переводит scored references в конкретные решения для лендинга. Он отвечает на фразу: "вот тут я вдохновился этим, потому что тема близка, и сделаю вот так".

## Difference From Scorecard

`15-reference-scorecard.md` решает, какие references достаточно полезны и безопасны.

`22-inspiration-synthesis.md` решает, как именно они меняют план:

- section composition;
- visual hierarchy;
- asset treatment;
- motion behavior;
- interaction detail;
- copy/proof placement;
- mobile transformation;
- implementation boundary.

## Required Inputs

Read:

- `03-reference-board.md`
- `24-thematic-reference-map.md`
- `04-visual-benchmark.md`
- `15-reference-scorecard.md`
- `17-visual-style-tile.md`
- `18-section-storyboard-canvas.md`
- `19-asset-production-queue.md`
- `21-plan-self-review.md` if present

## Synthesis Rules

- Every core or section reference must produce at least one concrete section decision.
- Every borrowed idea must say what not to copy.
- Aesthetic references can influence surface, rhythm and typography, but not proof or claims.
- Direct/domain references can influence offer structure and proof placement, but not brand identity.
- Motion references must become trigger, visible result, timing, fallback and QA note.
- Component references must become exact source choice or rejected source note.
- Anti-references must become a clear avoidance rule.
- If a reference is close in theme, say why it is close: audience, offer, product category, workflow, emotion, trust model or asset type.
- If thematic map rejects a reference, do not resurrect it in synthesis unless the rejection is explicitly resolved.

## Synthesis Fields

Each accepted reference should have:

- reference ID;
- URL;
- closeness reason;
- role;
- section mapping;
- what to borrow;
- what to transform;
- what not to copy;
- concrete visible decision;
- motion or interaction decision;
- asset implication;
- mobile implication;
- risk and QA.

## Examples Of Good Translation

Weak:

```text
Borrow premium feel from ref-004.
```

Strong:

```text
Hero uses ref-004's wide editorial spacing and asymmetric product image placement, but keeps our own palette and avoids their luxury serif. The visible result is a left-copy hero with a 16:10 product render crossing into the proof rail. Mobile stacks copy first, render second, proof third.
```

Weak:

```text
Use smooth scroll animation like ref-007.
```

Strong:

```text
Feature reveal uses ref-007's staged entrance logic, adapted to Motion fade+slide at 160ms stagger. It reveals proof cards only after the section heading is readable. Reduced motion renders cards immediately with opacity only.
```

## Anti-Copy Boundary

Never copy:

- brand identity;
- exact hero layout;
- proprietary illustrations;
- customer logos;
- testimonials;
- metrics;
- pricing claims;
- private product screenshots;
- premium/pro component source without license;
- text content;
- animation that creates accessibility or performance risk.

## Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/22-inspiration-synthesis.md
```

Then use it to update:

```text
05-visual-direction.md
06-section-by-section-upgrade-plan.md
07-animation-storyboard.md
17-visual-style-tile.md
18-section-storyboard-canvas.md
21-plan-self-review.md
```
