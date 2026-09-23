# Brand DNA Preservation

Дата обновления: 2026-07-03.

Источники:

- https://www.figma.com/blog/design-systems-101-what-is-a-design-system/
- https://www.figma.com/design-systems/
- https://www.nngroup.com/articles/design-systems-101/
- https://www.nngroup.com/articles/design-systems-vs-style-guides/
- https://www.nngroup.com/articles/front-end-style-guides/
- https://atlassian.design/foundations/
- https://m3.material.io/foundations
- https://carbondesignsystem.com/elements/2x-grid/overview/

Этот слой нужен после source dossier и до visual direction. Он отвечает на вопрос: "что у текущего лендинга уже является брендом, что надо сохранить, что аккуратно эволюционировать, что удалить, а что можно добавить".

## Why This Exists

Редизайн часто ломает то, что уже работало:

- узнаваемый цвет;
- тон текста;
- продуктовый скриншот;
- nav labels;
- CTA wording;
- доверительный proof;
- форма или интеграция;
- простая структура, которая была понятна пользователю.

`25-brand-dna-map.md` не даёт агенту заменить проект чужим reference style. Style tile должен опираться на эту карту.

## Inputs

Read:

- `landing-source-dossier.md`;
- `01-current-state-audit.md`;
- `02-copy-and-offer-audit.md`;
- `04-visual-benchmark.md`;
- screenshot evidence;
- source files and CSS/token evidence from the dossier.

## DNA Layers

| Layer | What to inspect | Decision |
| --- | --- | --- |
| Brand promise | headline, offer, CTA, proof, user anxiety | preserve / sharpen / replace |
| Voice | tone, vocabulary, sentence length, confidence level | preserve / make clearer / change |
| Color | brand colors, accents, semantic colors, contrast | preserve / evolve / remove / introduce |
| Typography | display, body, mono, weights, hierarchy | preserve / evolve / replace |
| Layout rhythm | section spacing, density, grid, card rhythm | preserve / tighten / rebuild |
| Surface language | cards, borders, shadows, media frames, backgrounds | preserve / simplify / rebuild |
| Icon and illustration style | icon family, stroke, fill, diagrams, mascots | preserve / unify / replace |
| Product assets | screenshots, renders, video, 3D, photos | preserve / recrop / recreate / remove |
| Motion character | existing hover, reveal, scroll, state transitions | preserve / reduce / upgrade / remove |
| Protected content | routes, nav labels, form labels, legal, SEO, analytics | preserve unless explicitly approved |

## Decision Words

Use only these decisions:

- `Preserve`: keep as-is because it supports recognition, trust, SEO, analytics, or conversion.
- `Evolve`: keep the idea but improve execution.
- `Remove`: delete because it weakens clarity, trust, accessibility, performance, or presentation quality.
- `Introduce`: add something new because the current system lacks it.
- `Protect`: do not change without explicit approval.

## Required Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/25-brand-dna-map.md
```

Then use it to update:

```text
05-visual-direction.md
17-visual-style-tile.md
18-section-storyboard-canvas.md
19-asset-production-queue.md
20-implementation-task-graph.md
11-implementation-handoff-prompt.md
```

## Quality Bar

Every preserved or evolved item must cite evidence:

- screenshot path;
- source file;
- CSS token;
- asset path;
- copy snippet;
- route/nav/form/SEO constraint;
- user or business reason.

If evidence is missing, mark the item as assumed and add it to risks.

## Anti-Redesign-Amnesia Rules

- Do not change CTA wording if it is analytics-sensitive and not approved.
- Do not replace real product proof with decorative graphics.
- Do not discard brand color unless contrast, readability or positioning demands it.
- Do not introduce a new visual language only because a reference uses it.
- Do not flatten a distinctive brand into generic SaaS cards.
- Do not preserve weak design just because it exists. Preserve only what has a user, brand, technical or business reason.
