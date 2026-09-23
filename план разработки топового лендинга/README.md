# План разработки топового лендинга

Эта папка нужна как мост между любым простым лендингом и этим проектом, где мы готовим сильный дизайн-план и потом улучшаем реализацию.

## Как пользоваться

1. В другом проекте открой файл `01-universal-prompt-source-project.md`.
2. Передай его агенту в том проекте.
3. Агент должен создать `landing-source-dossier.md` с фактами о текущем лендинге: продукт, аудитория, CTA, структура, дизайн, файлы, проблемы, ассеты.
4. Перенеси этот dossier сюда.
5. В этом проекте используй `02-upgrade-planner-prompt-this-project.md`.
6. На выходе должен появиться не абстрактный редизайн, а план: что меняется, почему, где какая анимация, какие источники вдохновения подходят, какие компоненты брать, что проверять.

## Что здесь лежит

- `00-source-scouting-log.md` - найденные источники и что из них реально полезно.
- `01-universal-prompt-source-project.md` - универсальный промпт для другого проекта.
- `02-upgrade-planner-prompt-this-project.md` - промпт для этого проекта после получения dossier.
- `03-skill-and-source-synergy.md` - как скиллы и источники работают вместе, а не мешают друг другу.
- `04-upgrade-plan-template.md` - шаблон итогового плана улучшения лендинга.
- `05-quality-gate.md` - проверка перед тем, как считать результат нормальным.
- `06-reference-query-playbook.md` - конкретные поисковые запросы для references, компонентов и motion.
- `07-top-landing-workflow.md` - полный цикл: dossier, references, direction, storyboard, implementation, QA.
- `08-skill-install-candidates.md` - что установлено, что создано локально, что оставлено только как reference.
- `09-landing-type-routing-matrix.md` - какой набор skills/sources/assets/motion брать для разных типов лендингов.
- `10-evidence-and-cro-sources.md` - CRO/UX источники для доказательных решений, не только визуального вкуса.
- `11-component-source-registry.md` - registry компонентных источников, когда что брать, какие риски.
- `12-agent-prompt-pack.md` - prompts для source dossier, planning, implementation, visual QA, asset production, final handoff.
- `13-source-dossier-schema.md` - строгая схема `landing-source-dossier.md` для другого проекта.
- `14-final-qa-and-launch-gate.md` - финальная проверка после реализации: screenshots, accessibility, performance, motion, launch risks.
- `15-visual-evidence-capture.md` - как снимать, именовать и регистрировать screenshots для visual QA.
- `16-section-pattern-library.md` - конкретные section patterns: hero, proof, features, pricing, FAQ, CTA, 3D, motion.
- `17-animate-ui-full-site-map.md` - полная карта Animate UI по категориям, landing-секциям, рискам и install rules.
- `18-reference-scoring-matrix.md` - scoring references по fit, section value, motion, risk and source safety.
- `19-motion-recipe-library.md` - конкретные motion recipes по секциям, триггерам, timing, fallback and QA.
- `20-visual-direction-style-tiles.md` - style tile guide: typography, color, spacing, radius, surfaces, assets and section style rules.
- `21-section-storyboard-canvas.md` - per-section storyboard canvas linking copy, visual style, asset, reference, pattern, motion, component and QA.
- `22-asset-production-queue.md` - очередь ассетов: screenshots, generated images, diagrams, video, 3D/GLB, prompts, alt text, performance and QA.
- `23-implementation-task-graph.md` - граф внедрения: task IDs, rings, blockers, files, visible result, verification and evidence.
- `24-source-dossier-forensics.md` - как другому проекту собрать evidence-rich dossier: screenshots, files, tokens, assets, commands, risks.
- `25-plan-self-review.md` - pre-implementation critique: generic language, weak references, vague motion, missing visible decisions.
- `26-inspiration-synthesis.md` - перевод references в конкретные section decisions, motion, assets and anti-copy boundaries.
- `27-presentation-quality-review.md` - post-implementation visual critique: first impression, above the fold, hierarchy, credibility, distinctiveness, asset quality and mobile presentation.
- `28-thematic-reference-mining.md` - поиск тематически близких direct, adjacent, analogous, flow, visual, motion, component and anti references before scorecard.
- `29-brand-dna-preservation.md` - карта того, что в текущем лендинге сохранить, эволюционировать, удалить, добавить или защитить before style tile.
- `30-motion-reference-mining.md` - поиск и перевод реальных motion references в section-level motion map before recipe/storyboard.
- `31-responsive-viewport-storyboard.md` - desktop/mobile/tablet/wide viewport storyboard before implementation, with first viewport, crops, wrapping, overflow and screenshot QA.
- `32-change-traceability-matrix.md` - traceability gate: source evidence -> reason -> reference/brand/section decision -> task -> QA.
- `33-motion-primitives-source-map.md` - Motion Primitives source map: exact items, install model, dependency risk and selection rules.
- `34-magic-ui-source-map.md` - Magic UI source map: marketing effects, templates, install model, dependency risk and rejection rules.
- `35-aceternity-ui-source-map.md` - Aceternity UI source map: high-impact components, blocks, license/access risk, dependency risk and adaptation rules.
- `36-tailark-section-source-map.md` - Tailark source map: public/pro section blocks, registry URLs, stale sitemap risks, install model and adaptation rules.
- `37-shadcnblocks-source-map.md` - shadcnblocks source map: free/pro blocks, components, pages, CLI registry, license restrictions and selection rules.
- `38-micro-component-source-map.md` - Kibo UI and Origin/Coss micro-component source map: exact registry/copy URLs, dependencies, license and rejection rules.
- `39-react-bits-source-map.md` - React Bits source map: exact animated components, TS/Tailwind variants, dependency risk and rejection rules.
- `40-pacekit-gsap-source-map.md` - PaceKit GSAP source map: exact GSAP registry items, dependency risk and GSAP-worthy selection rules.
- `41-cult-ui-source-map.md` - Cult UI source map: exact shadcn registry items, MIT license, texture/product-widget use cases and style/dependency gates.
- `42-reui-source-map.md` - ReUI source map: free/pro registry model, app UI components, license key gates and product-interface selection rules.
- `43-21st-dev-source-map.md` - 21st.dev source map: community component discovery, CLI install model, CDN registry checks, dependency/license gates and reference-first rules.
- `44-kokonut-ui-source-map.md` - Kokonut UI source map: public shadcn registry, MIT/pro gate, animated AI/buttons/cards/navigation/text component rules.
- `45-mvpblocks-source-map.md` - MVPBlocks source map: exact block endpoints, CLI install model, section/template gates, license caveat and dependency risks.
- `46-smoothui-source-map.md` - SmoothUI source map: full site audit, 107 registry endpoints, component API, broken blocks API warning, MIT license and selection rules.
- `47-hextaui-source-map.md` - HextaUI source map: app/SaaS block registry, official shadcn namespace, HTML-doc caveat, MIT license and product-proof gates.
- `48-skiper-ui-source-map.md` - Skiper UI source map: official shadcn namespace, public registry items, premium/terms caveat, broken preview URLs and motion-heavy selection gates.
- `49-eldora-ui-source-map.md` - Eldora UI source map: MIT shadcn registry, device/product proof frames, animated text/backgrounds, section blocks and runtime gates.
- `50-blocks-so-source-map.md` - Blocks.so source map: MIT app/product proof blocks, official shadcn namespace, duplicate item caveat, live registry reset caveat and fake-proof gates.
- `51-intent-ui-source-map.md` - Intent UI source map: MIT React Aria component registry, accessible app controls, blocks, examples and dependency gates.
- `52-reference-gallery-source-map.md` - reference gallery source map: landing galleries, SaaS examples, product-flow libraries, visual inspiration, motion references, CRO evidence, access caveats and anti-copy gates.
- `53-motion-safety-source-map.md` - motion safety source map: WCAG, reduced-motion, Core Web Vitals, animation performance, mobile comfort, verdicts and hard gates before implementation.
- `54-proof-integrity-source-map.md` - proof integrity source map: FTC/NNG/Baymard-backed gates for claims, metrics, testimonials, logos, reviews, screenshots, demo data and generated proof assets.
- `source-dossier-example.md` - компактный пример dossier правильной формы.
- `projects/_template/` - готовая структура файлов для плана конкретного лендинга.

## Быстрые команды

Создать папку плана:

```bash
node scripts/create-landing-plan.mjs <project-slug>
```

Создать папку и сразу скопировать dossier:

```bash
node scripts/create-landing-plan.mjs <project-slug> --dossier path/to/landing-source-dossier.md
```

Проверить план:

```bash
node scripts/check-landing-plan.mjs <project-slug>
```

Проверить dossier из другого проекта:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

Зарегистрировать screenshot evidence:

```bash
node scripts/register-screenshot-evidence.mjs <project-slug> --id shot-001 --path evidence/screenshots/current-desktop-hero.png --source current --viewport desktop --purpose "Current hero baseline" --section "Hero"
```

Передать план implementation agent:

```text
Используй `12-agent-prompt-pack.md`, Prompt C, и путь к `projects/<project-slug>/`.
```

Главная идея: другой проект дает фактическую базу. Этот проект делает дизайн-стратегию, визуальное направление, copy/offer аудит, evidence pack, reference board, анимационный сценарий, asset direction, компонентный выбор, граф внедрения and план внедрения.
