# Промпт для этого проекта после получения dossier

Этот промпт используется здесь, в `ai-website-cloner-template`, после того как из другого проекта принесли `landing-source-dossier.md`.

```text
У нас есть dossier из другого проекта с простым лендингом. Твоя задача - составить подробный план улучшения лендинга до сильного, презентабельного уровня.

Перед началом:
- прочитай `landing-source-dossier.md`;
- проверь dossier командой `node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md`, если файл доступен локально;
- прочитай `план разработки топового лендинга/13-source-dossier-schema.md`;
- прочитай `план разработки топового лендинга/03-skill-and-source-synergy.md`;
- прочитай `план разработки топового лендинга/04-upgrade-plan-template.md`;
- прочитай `план разработки топового лендинга/09-landing-type-routing-matrix.md`;
- прочитай `план разработки топового лендинга/10-evidence-and-cro-sources.md`, если нужно обосновать CRO/UX решения;
- прочитай `план разработки топового лендинга/54-proof-integrity-source-map.md` before accepting claims, proof, testimonials, logos, metrics, screenshots, reviews, security/compliance claims or generated proof assets;
- прочитай `план разработки топового лендинга/11-component-source-registry.md` перед выбором компонентов;
- прочитай `план разработки топового лендинга/16-section-pattern-library.md` перед section-by-section storyboard;
- прочитай `план разработки топового лендинга/29-brand-dna-preservation.md` before visual direction, чтобы решить что preserve/evolve/remove/introduce/protect;
- прочитай `план разработки топового лендинга/17-animate-ui-full-site-map.md`, если рассматриваешь Animate UI;
- прочитай `план разработки топового лендинга/52-reference-gallery-source-map.md` before reference research, чтобы выбрать правильные galleries, product-flow sources, motion references, CRO evidence and access gates;
- прочитай `план разработки топового лендинга/28-thematic-reference-mining.md` before reference scorecard, чтобы найти thematic/adjacent/analogous references with closeness reasons;
- прочитай `план разработки топового лендинга/18-reference-scoring-matrix.md` перед финальным выбором references;
- прочитай `план разработки топового лендинга/26-inspiration-synthesis.md` перед visual direction and section decisions;
- прочитай `план разработки топового лендинга/30-motion-reference-mining.md` before motion recipes, чтобы motion был взят из реальных references with borrow/transform/do-not-copy boundaries;
- прочитай `план разработки топового лендинга/53-motion-safety-source-map.md` before accepting motion recipes, scroll choreography, WebGL/3D or animated component libraries;
- прочитай `план разработки топового лендинга/19-motion-recipe-library.md` перед animation storyboard;
- прочитай `план разработки топового лендинга/20-visual-direction-style-tiles.md` перед visual direction;
- прочитай `план разработки топового лендинга/21-section-storyboard-canvas.md` перед implementation tasks;
- прочитай `план разработки топового лендинга/22-asset-production-queue.md` перед asset/component plan;
- прочитай `план разработки топового лендинга/33-motion-primitives-source-map.md`, если рассматриваешь Motion Primitives;
- прочитай `план разработки топового лендинга/34-magic-ui-source-map.md`, если рассматриваешь Magic UI;
- прочитай `план разработки топового лендинга/35-aceternity-ui-source-map.md`, если рассматриваешь Aceternity UI;
- прочитай `план разработки топового лендинга/36-tailark-section-source-map.md`, если рассматриваешь Tailark;
- прочитай `план разработки топового лендинга/37-shadcnblocks-source-map.md`, если рассматриваешь shadcnblocks;
- прочитай `план разработки топового лендинга/38-micro-component-source-map.md`, если рассматриваешь Kibo UI, Origin/Coss UI или другой micro-component source;
- прочитай `план разработки топового лендинга/39-react-bits-source-map.md`, если рассматриваешь React Bits;
- прочитай `план разработки топового лендинга/40-pacekit-gsap-source-map.md`, если рассматриваешь PaceKit GSAP;
- прочитай `план разработки топового лендинга/41-cult-ui-source-map.md`, если рассматриваешь Cult UI;
- прочитай `план разработки топового лендинга/42-reui-source-map.md`, если рассматриваешь ReUI;
- прочитай `план разработки топового лендинга/43-21st-dev-source-map.md`, если рассматриваешь 21st.dev;
- прочитай `план разработки топового лендинга/44-kokonut-ui-source-map.md`, если рассматриваешь Kokonut UI;
- прочитай `план разработки топового лендинга/45-mvpblocks-source-map.md`, если рассматриваешь MVPBlocks;
- прочитай `план разработки топового лендинга/46-smoothui-source-map.md`, если рассматриваешь SmoothUI;
- прочитай `план разработки топового лендинга/47-hextaui-source-map.md`, если рассматриваешь HextaUI;
- прочитай `план разработки топового лендинга/48-skiper-ui-source-map.md`, если рассматриваешь Skiper UI;
- прочитай `план разработки топового лендинга/49-eldora-ui-source-map.md`, если рассматриваешь Eldora UI;
- прочитай `план разработки топового лендинга/50-blocks-so-source-map.md`, если рассматриваешь Blocks.so;
- прочитай `план разработки топового лендинга/51-intent-ui-source-map.md`, если рассматриваешь Intent UI;
- прочитай `план разработки топового лендинга/31-responsive-viewport-storyboard.md` перед implementation tasks, чтобы desktop/mobile/tablet/wide viewport frames были спланированы до верстки;
- прочитай `план разработки топового лендинга/23-implementation-task-graph.md` перед final implementation tasks and handoff;
- прочитай `план разработки топового лендинга/32-change-traceability-matrix.md` перед self-review and handoff, чтобы каждая правка имела source evidence, visible result, task ID and QA method;
- прочитай `план разработки топового лендинга/25-plan-self-review.md` перед handoff;
- прочитай `план разработки топового лендинга/27-presentation-quality-review.md` перед final QA, чтобы знать как проверять presentation quality по screenshots/live preview;
- используй локальные skills: landing-page-high-conversion, design-taste-frontend, landing-visual-direction, ui-audit, landing-dossier-schema, landing-source-forensics, landing-brand-dna-preservation, landing-proof-integrity-gate, landing-reference-source-catalog, landing-reference-research, landing-thematic-reference-mining, landing-reference-scoring, landing-inspiration-synthesis, landing-motion-reference-mining, landing-motion-safety-gate, landing-responsive-viewport-storyboard, landing-change-traceability, landing-evidence-pack, landing-visual-evidence-capture, landing-copy-offer-audit, landing-visual-benchmark, landing-section-patterns, landing-section-storyboard, landing-asset-art-direction, landing-asset-production, landing-motion-storyboard, landing-motion-recipes, motion-component-source-map, motion-primitives-catalog, magic-ui-catalog, aceternity-ui-catalog, tailark-section-catalog, shadcnblocks-catalog, micro-component-source-catalog, kibo-ui-catalog, react-bits-catalog, pacekit-gsap-catalog, cult-ui-catalog, reui-catalog, twenty-first-dev-catalog, kokonut-ui-catalog, mvpblocks-catalog, smoothui-catalog, hextaui-catalog, skiper-ui-catalog, eldora-ui-catalog, blocks-so-catalog, intent-ui-catalog, landing-upgrade-orchestrator, landing-implementation-task-graph, landing-plan-self-review, landing-presentation-review, landing-implementation-handoff, landing-final-qa;
- если проект связан с 3D/WebGL, добавь webgl-3d-object, three-js-animation и Blender workbench rules.

Нужно создать папку плана для конкретного проекта:
`план разработки топового лендинга/projects/<project-slug>/`

Внутри создай:
1. `01-current-state-audit.md`
2. `02-copy-and-offer-audit.md`
3. `03-reference-board.md`
4. `04-visual-benchmark.md`
5. `05-visual-direction.md`
6. `06-section-by-section-upgrade-plan.md`
7. `07-animation-storyboard.md`
8. `08-component-and-asset-plan.md`
9. `09-implementation-tasks.md`
10. `10-quality-gate.md`
11. `evidence/` manifests: `reference-manifest.md`, `screenshot-manifest.md`, `asset-manifest.md`, `decision-log.md`
12. `11-implementation-handoff-prompt.md`
13. `12-final-qa-report.md`
14. `13-section-pattern-selection.md`
15. `14-animate-ui-selection.md`
16. `29-motion-primitives-selection.md`
17. `30-magic-ui-selection.md`
18. `31-aceternity-ui-selection.md`
19. `32-tailark-section-selection.md`
20. `33-shadcnblocks-selection.md`
21. `34-micro-component-selection.md`
22. `35-react-bits-selection.md`
23. `36-pacekit-gsap-selection.md`
24. `37-cult-ui-selection.md`
25. `38-reui-selection.md`
26. `39-twenty-first-dev-selection.md`
27. `40-kokonut-ui-selection.md`
28. `41-mvpblocks-selection.md`
29. `42-smoothui-selection.md`
30. `43-hextaui-selection.md`
31. `44-skiper-ui-selection.md`
32. `45-eldora-ui-selection.md`
33. `46-blocks-so-selection.md`
34. `47-intent-ui-selection.md`
35. `15-reference-scorecard.md`
36. `24-thematic-reference-map.md`
37. `25-brand-dna-map.md`
38. `22-inspiration-synthesis.md`
39. `26-motion-reference-map.md`
40. `16-motion-recipe-selection.md`
41. `17-visual-style-tile.md`
42. `18-section-storyboard-canvas.md`
43. `19-asset-production-queue.md`
44. `27-responsive-viewport-map.md`
45. `20-implementation-task-graph.md`
46. `28-change-traceability-matrix.md`
47. `21-plan-self-review.md`
48. `23-presentation-quality-review.md`

Как мыслить и писать:
- Не пиши абстрактно "сделать красиво".
- Перед visual direction заполни brand DNA map: preserve, evolve, remove, introduce and protect decisions with evidence.
- Перед visual direction заполни proof integrity map inside copy/asset files: every visible claim, metric, logo, testimonial, review, screenshot and proof asset gets a verdict: verified, needs-evidence, rephrase, visual-only or reject.
- Перед visual direction заполни style tile: visual read, token sheet, section style rules and do-not-do list.
- Перед implementation tasks заполни section storyboard canvas: user job, frame sketch, copy/proof, asset, reference IDs, pattern, motion recipe, component source, mobile frame, QA risk.
- Перед implementation tasks заполни asset production queue: asset role, type, source, specs, prompt/capture instruction, path, mobile crop, alt text, performance, status.
- Перед implementation tasks заполни responsive viewport map: viewport set, first viewport plan, section transformations, text wrapping, asset crops, overflow risks and screenshot QA matrix.
- Перед handoff заполни implementation task graph: task IDs, build rings, blockers, files/routes, visible result, verification, evidence, screenshot matrix and dependency budget.
- Перед self-review заполни change traceability matrix: chg IDs, source evidence, reason, reference/brand/section link, visible result, task ID, QA/evidence method, orphan decisions.
- Перед handoff заполни plan self-review: blockers, generic language sweep, reference-to-decision check, motion/asset check and required plan patches.
- После implementation screenshots заполни presentation quality review: first impression, above-the-fold, hierarchy, credibility, distinctiveness, reference translation, motion polish, asset quality and mobile presentation.
- Для каждой секции объясняй видимый результат: "в hero будет такой-то объект, такая композиция, такой entrance motion, такой hover".
- Для каждой идеи укажи inspiration source: URL, что берем, что не копируем.
- Перед scorecard заполни thematic reference map: direct/domain, adjacent, analogous, flow, visual, motion/component and anti references with closeness reasons.
- Перед reference research используй reference gallery source map: выбери source lane, access status, screenshot evidence или reason unavailable; не продвигай references без section mapping.
- Перед финальным выбором references заполни scorecard: role, score, decision, section mapping.
- После scorecard заполни inspiration synthesis: closeness reason, borrow, transform, do-not-copy, concrete visible decision, motion/asset/mobile implications.
- Перед motion recipes заполни motion reference map: source URL, pattern, trigger, visible result, borrow, transform, do-not-copy, library implication, reduced-motion fallback, mobile simplification and decision.
- Перед accepting motion recipes assign motion safety verdict: safe, needs-simplification, static-fallback-only or reject; include performance risk and QA method.
- Перед animation storyboard выбери motion recipes: recipe, trigger, visible result, timing, library, fallback, QA.
- Для каждой анимации дай цель: hierarchy, storytelling, feedback или state transition.
- Если Motion Primitives рассматривается, заполни `29-motion-primitives-selection.md`: exact item, install command, dependencies, motion purpose, fallback, mobile simplification, decision and QA.
- Если Magic UI рассматривается, заполни `30-magic-ui-selection.md`: exact item, install command, dependencies, visual/motion purpose, fallback, mobile simplification, decision and QA.
- Если Aceternity UI рассматривается, заполни `31-aceternity-ui-selection.md`: exact item/block, type, source URL, install command or reference-only, license/access, dependencies, adaptation, fallback, mobile simplification, decision and QA.
- Если Tailark рассматривается, заполни `32-tailark-section-selection.md`: exact item/block/page, kit/source, live source URL, preview URL, registry URL, install command or reference-only, access/license, dependencies, adaptation, fallback, mobile simplification, task ID, change ID, decision and QA.
- Если shadcnblocks рассматривается, заполни `33-shadcnblocks-selection.md`: exact block/component/page/template, source type, access, live source URL, registry URL, install command or reference-only, license/access, dependencies, adaptation, fallback, mobile simplification, task ID, change ID, decision and QA.
- Если Kibo UI, Origin/Coss UI или другой micro-component source рассматривается, заполни `34-micro-component-selection.md`: exact source/item, source URL, registry/copy URL, install/copy method, dependencies, license/access, adaptation, fallback, mobile simplification, keyboard/focus QA, task ID, change ID, decision and QA.
- Если React Bits рассматривается, заполни `35-react-bits-selection.md`: exact item, category, `TS-TW` variant, source URL, registry URL, install command, dependencies, license/access, adaptation, fallback, mobile simplification, heavy runtime gate, task ID, change ID, decision and QA.
- Если PaceKit GSAP рассматривается, заполни `36-pacekit-gsap-selection.md`: exact item, source URL, registry URL, install command, `gsap`/`@gsap/react` dependencies, registry dependencies, GSAP purpose, fallback, mobile simplification, runtime gate, task ID, change ID, decision and QA.
- Если Cult UI рассматривается, заполни `37-cult-ui-selection.md`: exact item, source URL, registry URL, install command, dependencies, registry dependencies, visible purpose, adaptation, fallback, mobile simplification, style/runtime gate, task ID, change ID, decision and QA.
- Если ReUI рассматривается, заполни `38-reui-selection.md`: exact item, style, source URL, registry URL, install command, free/pro access, license key status, dependencies, registry dependencies, adaptation, mobile behavior, keyboard/focus QA, task ID, change ID, decision and QA.
- Если 21st.dev рассматривается, заполни `39-twenty-first-dev-selection.md`: exact component page, author/item, command, CDN registry URL or reference-only, license, dependency impact, adaptation, fallback, mobile behavior, task ID, change ID, decision and QA.
- Если Kokonut UI рассматривается, заполни `40-kokonut-ui-selection.md`: exact docs page, registry item, registry URL, install command, MIT/pro access, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID, decision and QA.
- Если MVPBlocks рассматривается, заполни `41-mvpblocks-selection.md`: exact docs page, exact item, endpoint URL, `npx mvpblocks add <name> --ts` or exact URL command, BSD-3-Clause/MIT license caveat, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID, decision and QA.
- Если SmoothUI рассматривается, заполни `42-smoothui-selection.md`: exact docs or preview page, exact item, endpoint URL, `npx shadcn@latest add @smoothui/<name>` or exact URL command, MIT license, dependencies, registry dependencies, API/registry evidence, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID, decision and QA. Blocks API `/api/v1/blocks` cannot be used as evidence.
- Если HextaUI рассматривается, заполни `43-hextaui-selection.md`: exact item, source URL from `llms.txt` or HTML page when it loads, endpoint URL, `npx shadcn@latest add @hextaui/<name>` or exact URL command, MIT license, dependencies, registry dependencies, HTML-doc caveat, demo-data replacement, mobile behavior, task ID, change ID, decision and QA.
- Если Skiper UI рассматривается, заполни `44-skiper-ui-selection.md`: exact item, source URL, endpoint URL, `npx shadcn@latest add @skiper-ui/<name>` or exact URL command, terms/access status, dependencies, registry dependencies, premium/private material avoided, reduced-motion fallback, mobile behavior, task ID, change ID, decision and QA.
- Если Eldora UI рассматривается, заполни `45-eldora-ui-selection.md`: exact item, item type, source URL, endpoint URL, `npx shadcn@latest add @eldoraui/<name>` or exact URL command, MIT license, dependencies, registry dependencies, demo/example material avoided, reduced-motion fallback, mobile behavior, performance risk, task ID, change ID, decision and QA.
- Если Blocks.so рассматривается, заполни `46-blocks-so-selection.md`: exact item, category, source page, endpoint URL, `npx shadcn@latest add @blocks-so/<name>` or exact URL command, MIT license, duplicate-entry caveat, dependencies, registry dependencies, demo-data replacement, fake-proof handling, mobile behavior, accessibility notes, task ID, change ID, decision and QA.
- Если Intent UI рассматривается, заполни `47-intent-ui-selection.md`: exact item, item type, source URL, endpoint URL, `npx shadcn@latest add @intentui/<name>` or exact URL command, MIT license, React Aria dependency impact, dependencies, registry dependencies, `registry:page`/`all` avoidance, demo-data replacement, accessibility notes, mobile behavior, task ID, change ID, decision and QA.
- Для каждого компонента скажи источник: native/Tailwind, shadcn, Animate UI, Magic UI, Motion Primitives, Aceternity, Tailark, Coss UI, React Bits, PaceKit GSAP, Cult UI, ReUI, 21st.dev, Kokonut UI, MVPBlocks, SmoothUI, HextaUI, Skiper UI, Eldora UI, Blocks.so, Intent UI, custom.
- Для каждого риска дай проверку: mobile, contrast, reduced motion, performance, copy, layout overlap.

Итоговый план должен отвечать на вопросы:
- что сохраняем;
- что усиливаем;
- что удаляем;
- какая будет визуальная система;
- где будет motion;
- где нужны реальные изображения, видео или 3D;
- какие файлы менять первыми;
- как проверить, что стало лучше, а не просто иначе.

Запреты:
- не менять route slugs, primary nav labels, form field names, legal copy без явного разрешения;
- не делать AI-purple/dark-mesh/three-card шаблон по умолчанию;
- не ставить случайные библиотеки;
- не копировать premium/pro компоненты без лицензии;
- не выдавать план без concrete section storyboard.
```
