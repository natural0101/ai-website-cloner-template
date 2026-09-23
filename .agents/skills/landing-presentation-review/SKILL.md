---
name: landing-presentation-review
description: Review an implemented landing page, live preview, or screenshot set for presentation quality after build work. Use when judging whether a landing page looks polished, credible, distinctive, on-plan, and ready to show, especially after visual QA screenshots, before final QA, or when the user says the result is not presentation-ready.
---

# Landing Presentation Review

Use this skill after implementation screenshots or a live preview exist. It judges the visible result, not just whether the plan or code is complete.

## Required Reading

Read:

```text
план разработки топового лендинга/27-presentation-quality-review.md
план разработки топового лендинга/projects/<slug>/12-final-qa-report.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/22-inspiration-synthesis.md
план разработки топового лендинга/projects/<slug>/07-animation-storyboard.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/21-plan-self-review.md
```

Also inspect desktop and mobile screenshots, a live URL, or browser viewport captures. If neither screenshots nor live preview are available, mark the review blocked for missing visual evidence.

## Output

Fill:

```text
план разработки топового лендинга/projects/<slug>/23-presentation-quality-review.md
```

Update when needed:

```text
план разработки топового лендинга/projects/<slug>/12-final-qa-report.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. Review the desktop first viewport without relying on the plan.
2. Review the mobile first viewport.
3. Score first impression, above the fold, hierarchy, credibility, composition, distinctiveness, reference translation, motion polish, asset quality and mobile presentation.
4. Compare screenshots against the style tile, storyboard, inspiration synthesis, motion recipes and asset queue.
5. Identify anything that looks like an unmodified component demo or generic AI template.
6. Write findings with viewport, section, screenshot/live evidence and exact visual fix.
7. Block presentation-ready verdict if evidence is missing or any first-viewport blocker remains.

## Blocking Conditions

Block if:

- desktop screenshot and live URL are both missing;
- mobile screenshot and live URL are both missing;
- hero does not communicate the offer;
- primary CTA is hidden or visually weak in the first desktop viewport;
- product, brand, venue, person or object should be first-viewport signal but is absent;
- page looks like an unmodified component-library demo;
- assets are blurry, fake, stretched, irrelevant or visibly placeholder-like;
- mobile clips important text or visual content;
- motion hides content, shifts layout, feels gimmicky or lacks reduced-motion fallback;
- references are copied too closely or are not visible in the result.

## Finding Format

Use:

```text
ID:
Severity:
Viewport:
Section:
Evidence:
Issue:
Why it hurts presentation quality:
Required visual fix:
Plan file to update if needed:
Implementation file to update if known:
Status:
```
