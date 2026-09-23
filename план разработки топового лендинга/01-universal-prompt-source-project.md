# Универсальный промпт для другого проекта

Скопируй весь текст ниже и передай агенту в другом проекте с простым лендингом.

```text
Ты работаешь в проекте с существующим простым лендингом. Твоя задача сейчас не редизайнить и не переписывать код, а подготовить точный dossier для передачи в другой проект, где будет составлен план улучшения дизайна.

Работай в два прохода:
1. Inventory pass: собери факты, файлы, screenshots, tokens, copy, routes, assets, commands.
2. Evaluation pass: выпиши проблемы с evidence, severity, user impact, affected section, and likely redesign direction.

Сначала изучи текущий проект:
- package.json, framework, routes, app/pages structure;
- главную страницу и все landing-related components;
- CSS/Tailwind/design tokens;
- assets, public images, videos, 3D models, icons;
- copy, CTA, forms, analytics-sensitive labels;
- mobile/tablet/desktop behavior, if можно быстро проверить;
- first viewport: hero fit, CTA visibility, nav height, crop/overflow issues;
- screenshot или preview, если dev server доступен;
- console errors, obvious hydration/runtime errors, if browser/devtools доступны;
- Lighthouse/performance/accessibility availability or unavailable reason;
- manual accessibility checks: keyboard focus, contrast concerns, labels/alt text, reduced motion;
- heuristic issues using common UX heuristics: clarity, feedback, consistency, recognition, error prevention, minimalist design;
- если доступен `landing-source-forensics`, используй его как checklist.

Создай файл `landing-source-dossier.md` в корне проекта.

Формат dossier должен соответствовать схеме `13-source-dossier-schema.md` из проекта `ai-website-cloner-template`.

Если у тебя нет доступа к этой схеме, используй структуру ниже без изменения заголовков:

## 1. Product Snapshot
- product/service:
- target audience:
- primary CTA:
- conversion goal:
- offer:
- traffic/source assumption:
- known constraints:
- current quality level:

## 2. Current Site Map
- routes:
- main files:
- landing components:
- shared UI components:
- assets:
- SEO files:
- analytics/form integrations:
- UI/motion dependencies:

## 3. Current Landing Structure
Для каждой секции:
- section ID/name:
- file/component:
- current purpose:
- visible copy:
- CTA/proof/assets:
- layout:
- mobile behavior:
- what works:
- what is weak:

## 4. Visual Audit
- typography:
- color palette:
- spacing/rhythm:
- layout families:
- imagery/3D/video:
- motion/interactions:
- mobile issues:
- responsive/viewport issues:
- hero first viewport:
- nav height/behavior:
- text wrapping or overflow issues:
- asset crop issues:
- accessibility issues:
- manual accessibility notes:
- heuristic issues by severity:
- CTA/conversion friction:
- trust/proof gaps:
- performance risks:

## 5. Evidence Inventory
- live URL or local preview URL:
- desktop screenshot path or unavailable reason:
- mobile screenshot path or unavailable reason:
- hero/above-fold screenshot path or unavailable reason:
- desktop viewport:
- mobile viewport:
- tablet/wide viewport or unavailable reason:
- first viewport notes:
- horizontal overflow check:
- source files inspected:
- CSS/token evidence:
- asset paths inspected:
- commands run and result:
- console errors or unavailable reason:
- Lighthouse report/path or unavailable reason:
- manual accessibility check result:
- heuristic evaluation notes:
- browser/Lighthouse/Playwright availability:
- unknowns:

## 6. Brand And Content Preservation
- copy that should be preserved:
- routes/slugs/anchors to preserve:
- nav labels to preserve:
- form fields to preserve:
- analytics-sensitive buttons/labels:
- legal/SEO content:
- brand assets:
- do-not-change notes:

## 7. Upgrade Opportunities
Сделай 8-15 пунктов. Для каждого:
- problem:
- severity: cosmetic / minor / major / blocker:
- possible improvement:
- expected user impact:
- affected section:
- heuristic/source principle:
- risk:
- evidence:

## 8. Reference Hooks
Если интернет доступен, найди 5-8 близких references:
- direct competitors/domain:
- visual/aesthetic references:
- motion/interaction references:
Для каждого дай URL и коротко: "что можно взять, что нельзя копировать".
Если интернет недоступен, напиши какие references нужно искать.

## 9. Technical Constraints
- framework:
- package manager:
- styling system:
- installed UI libraries:
- installed animation libraries:
- framework restrictions:
- build/dev commands:
- known errors:
- files that look risky to edit:
- browser/screenshot availability:

## 10. Handoff Summary
Дай короткий executive summary:
- current quality level:
- best redesign mode: preserve / targeted evolution / overhaul;
- recommended vibe:
- recommended motion intensity:
- recommended asset direction:
- recommended first 5 implementation tasks.
- open questions:
- assumptions:

Важно:
- Не выдумывай метрики, логотипы, отзывы, клиентов.
- Не меняй код, если я явно не попросил.
- Все выводы привязывай к файлам, screenshots или видимому UI.
- Не пиши "mobile норм" без viewport или screenshot/unavailable reason.
- Не пиши "цвета приятные" без хотя бы примерных tokens.
- Не пиши "доступность норм" только по Lighthouse; разделяй automated result и manual notes.
- Не ставь high severity без evidence: screenshot, file path, visible copy, command output, or exact unavailable reason.
- Если чего-то не знаешь, пометь как unknown, а не придумывай.
- Если возможно, после создания dossier скажи, что его надо проверить командой:
  `node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md`
```
