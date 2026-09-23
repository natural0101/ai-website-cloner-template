# Thematic Reference Mining

Дата обновления: 2026-07-03.

Источники:

- https://www.designkit.org/methods/analogous-inspiration.html
- https://www.designkit.org/methods/secondary-research.html
- https://www.designkit.org/methods/find-themes.html
- https://www.designkit.org/methods/mash-ups.html
- https://www.nngroup.com/articles/competitive-usability-evaluations/
- https://www.nngroup.com/articles/benchmarking-ux/
- https://www.figma.com/resource-library/how-to-make-a-mood-board/
- https://mobbin.com/
- https://pageflows.com/
- `52-reference-gallery-source-map.md`

Этот слой нужен до reference scorecard. Он отвечает на вопрос: "почему эта страница близка по теме, поведению, аудитории, доверию или визуальному языку, и что из неё можно использовать".

## Why This Exists

Обычный поиск часто даёт либо прямых конкурентов, либо красивые страницы без связи с продуктом. Для сильного лендинга нужны разные типы references:

- same market;
- same buyer anxiety;
- same workflow;
- same product proof pattern;
- same visual emotion;
- same asset type;
- same interaction moment;
- useful opposite example.

`24-thematic-reference-map.md` собирает эти связи до scoring, чтобы `15-reference-scorecard.md` и `22-inspiration-synthesis.md` не были moodboard по вкусу.

Перед поиском выбрать source lane по `52-reference-gallery-source-map.md`. Это защищает от двух ошибок: искать product-flow в визуальных галереях и брать Awwwards/Recent как conversion structure без проверки fit.

## Reference Lanes

| Lane | What counts | Use |
| --- | --- | --- |
| Direct competitor | same category, same buyer, similar CTA | offer structure, proof placement, objection handling |
| Domain adjacent | nearby market with similar trust model | credibility, language, section sequence |
| Audience adjacent | same buyer persona but different product | tone, density, buying anxieties |
| Workflow adjacent | similar user journey, onboarding, checkout, activation | product flow, screenshots, step framing |
| Visual language | similar desired feeling, density, editorial/product treatment | typography, composition, color, asset treatment |
| Motion/interaction | similar reveal, state transition, scroll story, hover behavior | motion recipes and QA risk |
| Component/source | reusable component, primitive, block, effect | implementation candidate and dependency risk |
| Analogous inspiration | different industry but same emotional or behavioral challenge | fresh composition or metaphor without copying competitor norms |
| Anti-reference | shows what to avoid | do-not-do rule |

## Closeness Reasons

Every reference needs at least one closeness reason:

- product category;
- audience or buyer;
- conversion action;
- trust model;
- workflow;
- data/proof type;
- asset type;
- visual emotion;
- interaction pattern;
- mobile constraint;
- risk pattern.

If no closeness reason can be named, reject the reference.

## Search Packs

Replace `{category}`, `{buyer}`, `{workflow}`, `{emotion}`, `{asset}`, and `{section}` with dossier facts.

Direct/domain:

```text
{category} SaaS landing page
{category} product homepage pricing
{category} alternatives landing page
{buyer} software landing page
```

Adjacent/theme:

```text
{buyer} dashboard landing page
{workflow} onboarding landing page
{category} trust security compliance landing page
{emotion} product website case study
```

Flow:

```text
site:mobbin.com {workflow}
site:pageflows.com {workflow}
site:mobbin.com {category} onboarding
site:pageflows.com {category} signup
```

Visual:

```text
site:land-book.com {category}
site:lapa.ninja {category}
site:godly.website {emotion} {asset}
site:saaspo.com {category}
site:landingfolio.com {category}
site:recent.design {emotion} {asset}
site:siteinspire.com {category} {emotion}
site:minimal.gallery {emotion}
site:refero.design {workflow}
site:httpster.net {category}
site:darkmodedesign.com {category}
```

Motion/component:

```text
{section} scroll animation landing page
{asset} reveal animation website
Awwwards {category} interaction
Codrops {interaction pattern}
site:examples.motion.dev/react {interaction pattern}
Animate UI {section}
Motion Primitives {interaction}
Magic UI {effect}
```

Analogous:

```text
best {emotion} product website
{workflow} experience design examples
{asset} editorial product page
{trust model} landing page examples
```

## Required Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/24-thematic-reference-map.md
```

Minimum:

- 2 direct/domain candidates;
- 2 adjacent/theme candidates;
- 1 workflow/flow candidate if the landing has signup, onboarding, checkout, booking, dashboard, or product UI;
- 1 visual language candidate;
- 1 motion/component candidate if animation or special component is planned;
- 1 anti-reference for crowded/generic markets.

Every candidate must include source URL, access status, source lane, closeness reason, section mapping, borrow, transform, do-not-copy and risk. Access statuses such as `403`, `429`, `525`, timeout, browser/manual only or premium/account gated must be recorded instead of silently ignored.

Then use the map to fill:

```text
03-reference-board.md
15-reference-scorecard.md
22-inspiration-synthesis.md
17-visual-style-tile.md
18-section-storyboard-canvas.md
```

## Rejection Rules

Reject a reference when:

- no live URL or screenshot can be captured;
- it is only "cool" without product/audience/workflow/visual reason;
- it would push the page into a generic AI/SaaS look;
- it requires fake proof, fake screenshots or copied claims;
- it depends on inaccessible premium/pro source;
- its motion would create accessibility, mobile or performance risk;
- it contradicts the brand, CTA or buyer trust model.
