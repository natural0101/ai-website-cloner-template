---
name: landing-plan-self-review
description: Critique a completed landing-page improvement plan before implementation handoff, checking for vague language, weak offer clarity, generic design, missing visible section decisions, weak reference mapping, vague motion, underspecified assets, unresolved blockers, and insufficient evidence. Use after files `01` through `20` are filled and before another agent starts implementation.
---

# Landing Plan Self Review

Use this skill after planning and before implementation handoff.

## Required Reading

Read:

```text
план разработки топового лендинга/25-plan-self-review.md
план разработки топового лендинга/projects/<slug>/landing-source-dossier.md
план разработки топового лендинга/projects/<slug>/03-reference-board.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/20-implementation-task-graph.md
```

If `landing-source-dossier.md` is absent, review the plan but mark missing source evidence as a risk.

## Output

Fill:

```text
план разработки топового лендинга/projects/<slug>/21-plan-self-review.md
```

Update when needed:

```text
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
план разработки топового лендинга/projects/<slug>/11-implementation-handoff-prompt.md
```

## Workflow

1. Score the plan across offer clarity, section specificity, reference mapping, visual system, motion intent, asset realism, implementation readiness and presentation readiness.
2. Sweep for generic language and replace it with concrete visible decisions.
3. Verify that every important reference maps to a section decision and a do-not-copy boundary.
4. Verify that every important animation has purpose, trigger, visible result, timing and reduced-motion fallback.
5. Verify that every major asset has role, source, spec, path, alt/performance note and QA risk.
6. Verify that task graph items have files, blockers, verification and evidence.
7. Write blocker findings for anything that would make implementation guess.
8. Allow implementation handoff only when no blocker findings remain or the risk is explicitly accepted.

## Blocking Conditions

Block handoff if:

- the primary offer, audience or CTA is unclear;
- a major section lacks a visible result;
- references are not mapped to concrete section decisions;
- motion is decorative or lacks reduced-motion fallback;
- assets are vague or likely fake;
- tasks do not name files/routes and verification;
- the plan uses generic language instead of design decisions;
- evidence is missing for current state, references, assets or risk.

## Finding Format

Use:

```text
ID:
Severity:
Plan file:
Section:
Issue:
Why it weakens the landing:
Required fix:
Evidence needed:
Status:
```
