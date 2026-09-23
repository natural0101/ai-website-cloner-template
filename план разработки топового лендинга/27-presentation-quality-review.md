# Presentation Quality Review

Дата обновления: 2026-07-03.

Источники:

- https://www.figma.com/blog/design-critiques-at-figma/
- https://www.atlassian.com/blog/loom/design-review
- https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- https://www.nngroup.com/articles/aesthetic-usability-effect/
- https://credibility.stanford.edu/guidelines/
- https://m3.material.io/styles/motion/overview
- https://m3.material.io/styles/motion/transitions/applying-transitions

Этот слой нужен после implementation screenshots или live preview. Он отвечает не на вопрос "собрано ли", а на вопрос "выглядит ли это как сильный, уверенный, презентабельный лендинг".

## Когда использовать

Использовать после:

- `21-plan-self-review.md` разрешил implementation;
- implementation agent сделал изменения;
- есть desktop/mobile screenshots или live URL;
- `12-final-qa-report.md` ещё не закрыт как presentation-ready.

Если screenshots нет, review должен сразу поставить blocker: нельзя оценить presentation quality по описанию.

## Review lenses

| Lens | Pass means | Fail means |
| --- | --- | --- |
| First impression | за 3 секунды понятно что это, для кого, зачем и куда нажать | hero красивый, но смысл размыт |
| Above the fold | brand/product/object/offer видны в первом viewport, CTA не спрятан | первый экран выглядит как wallpaper или пустой moodboard |
| Visual hierarchy | взгляд идёт headline, proof, product visual, CTA, supporting detail | все элементы одинаковой громкости |
| Trust and credibility | proof, product state, claims and assets feel real | fake metrics, generic screenshots, декоративные claims |
| Composition | есть ось, баланс, rhythm, controlled whitespace and section contrast | всё плавает, центруется случайно, sections одинаковые |
| Distinctiveness | страница не считывается как стандартный AI template | dark-purple mesh, generic bento, stock cards без причины |
| Reference translation | видно, что взято из references и как трансформировано | reference mentioned, but result not visibly connected |
| Motion polish | motion помогает hierarchy, state or story and feels timed | motion отвлекает, дергает layout or exists only because library allowed it |
| Asset quality | images, 3D, screenshots, icons are sharp, cropped and meaningful | blurry, stretched, fake, irrelevant or decorative assets |
| Mobile presentation | mobile is intentionally composed, not squeezed desktop | text overlaps, CTA lost, assets cropped badly |

## Scoring

Use 1 to 5.

- `5`: presentation-ready, only small polish.
- `4`: strong, with specific minor fixes.
- `3`: acceptable structure, but not memorable or not refined.
- `2`: visibly rough, generic or inconsistent.
- `1`: not presentation-ready.

Overall verdict:

- `ship`: no blocker, average 4+ and screenshots prove it.
- `revise`: no fatal issue, but 1-3 high-impact fixes remain.
- `blocked`: screenshots missing, hero fails, CTA hidden, mobile broken, assets fake, or reference/motion decisions are contradicted.

## Required checks

1. Open desktop screenshot or live page at desktop width.
2. Open mobile screenshot or live page at mobile width.
3. Compare against `17-visual-style-tile.md`, `18-section-storyboard-canvas.md`, `22-inspiration-synthesis.md`, `07-animation-storyboard.md`, `16-motion-recipe-selection.md`, and `19-asset-production-queue.md`.
4. Check first impression without reading the plan.
5. Check the plan-to-screen match section by section.
6. Check if any component still looks uncustomized.
7. Check if motion and assets are helping the offer.
8. Record findings with evidence paths or live viewport names.

## Finding format

```text
ID:
Severity: blocker / high / medium / low
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

## Common blockers

- No desktop screenshot and no live URL.
- No mobile screenshot and no live URL.
- Hero does not communicate the offer.
- Primary CTA is not visible in the first desktop viewport.
- Product, brand, venue, person or object is not a first-viewport signal when it should be.
- Page looks like an unmodified component library demo.
- Assets are blurry, fake, stretched or unrelated.
- Mobile hero clips important text or visual.
- Motion hides content, shifts layout or ignores reduced-motion.
- References are copied too closely or not visible in the result at all.

## Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/23-presentation-quality-review.md
```

Then update:

```text
план разработки топового лендинга/projects/<slug>/12-final-qa-report.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

The page is not presentation-ready until blocker and high findings are fixed or explicitly accepted as launch risk.
