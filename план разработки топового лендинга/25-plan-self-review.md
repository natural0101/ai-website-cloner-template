# Plan Self Review

Дата обновления: 2026-07-03.

Источники:

- https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/
- https://m3.material.io/styles/motion/overview
- https://m3.material.io/styles/motion/transitions/applying-transitions
- https://www.figma.com/blog/design-critiques-at-figma/
- https://www.atlassian.com/blog/loom/design-review

Этот слой проверяет сам план до implementation. Он нужен, когда файлы уже заполнены, но ещё не ясно, получится ли из них презентабельный лендинг.

## Зачем

План может пройти формальные проверки и всё равно быть слабым:

- секции описаны общими словами;
- inspiration есть, но не связано с конкретными решениями;
- motion звучит красиво, но не имеет видимого результата;
- assets названы, но без роли и композиции;
- mobile and reduced motion упомянуты, но не проверяемы;
- implementation tasks есть, но не говорят, что должно измениться на экране.
- planned changes do not have source evidence, task IDs, or QA methods.

Self-review должен остановить такой план до того, как агент начнёт кодить.

## Review dimensions

| Dimension | Pass means | Fail means |
| --- | --- | --- |
| Offer clarity | one audience, one promise, one primary CTA | vague offer, multiple CTAs, unclear conversion |
| Section specificity | every section has user job, visible result and proof | "make better", "modernize", "add animation" |
| Reference mapping | each reference says borrow and do not copy per section | moodboard without decisions |
| Visual system | typography, color, radius, spacing, surfaces and assets are concrete | style words without tokens or rules |
| Motion intent | every animation has trigger, purpose, visible result, timing and fallback | animation is decorative or unspecified |
| Asset realism | every asset has role, source, spec, path, alt/performance note | vague "add image" or fake screenshot |
| Change traceability | every major change has source evidence, reason, task ID and QA method | orphan changes or tasks without `chg-###` IDs |
| Implementation readiness | tasks have blockers, files, verification and evidence | task list is just section names |
| Presentation readiness | plan explains why result will look stronger | plan is technically complete but not convincing |

## Red-flag language

These words are not banned, but a plan using them without specifics needs revision:

- modern;
- sleek;
- premium;
- clean;
- dynamic;
- engaging;
- smooth;
- beautiful;
- polished;
- immersive;
- professional;
- improve visuals;
- add animation;
- make it pop.

Replace them with concrete design decisions:

- "hero uses left-aligned copy with product proof rail and a 16:10 dashboard crop";
- "CTA has a 120ms press feedback and no layout movement";
- "feature cards become a comparison strip, inspired by ref-003 density but not its palette";
- "background motion is removed on reduced motion and falls back to a static radial grid image".

## Self-review process

1. Read the project plan folder.
2. Read `landing-source-dossier.md` if present.
3. Read evidence manifests.
4. Review the plan against the dimensions above.
5. Create findings ordered by severity.
6. Convert each finding into a concrete patch request for a plan file.
7. Update `21-plan-self-review.md` with verdict and fixes.
8. Do not hand off implementation until all blocking findings are resolved or explicitly accepted as risk.

## Finding format

```text
ID:
Severity: blocker / high / medium / low
Plan file:
Section:
Issue:
Why it weakens the landing:
Required fix:
Evidence needed:
Status:
```

## Minimum pass

The plan can move to implementation only when:

- no blocker findings remain;
- every major section has a visible result;
- references are mapped to sections;
- motion is purposeful and has fallback;
- assets are specific enough to produce or wire;
- task graph names files, blockers, verification and evidence;
- change traceability matrix has no orphan major changes;
- remaining risks are written in `10-quality-gate.md` and `11-implementation-handoff-prompt.md`.

## Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/21-plan-self-review.md
```
