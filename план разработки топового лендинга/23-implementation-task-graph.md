# Implementation Task Graph

Дата обновления: 2026-07-03.

Источники:

- https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies
- https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists
- https://playwright.dev/docs/test-snapshots
- https://developer.chrome.com/docs/lighthouse/overview
- https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Performance_budgets
- https://web.dev/articles/performance-budgets-101
- https://web.dev/articles/use-lighthouse-for-performance-budgets

Этот файл превращает дизайн-план в порядок внедрения. Он нужен перед handoff агенту, который будет менять код.

## Главный принцип

Не начинать с эффектов. Сначала закрепить смысл, структуру, visual system, assets and constraints. Потом внедрять motion and polish. Иначе лендинг быстро становится набором красивых, но несвязанных кусков.

## Что должен доказать task graph

- В каком порядке делать работу.
- Какие задачи блокируют другие задачи.
- Какие файлы или зоны кода затрагивает каждая задача.
- Какой visible result должен появиться.
- Какие references, storyboard rows, motion recipes and asset IDs относятся к задаче.
- Какие проверки доказывают, что задача реально готова.
- Какие screenshots or evidence надо приложить.

## Task ID format

Использовать стабильные ID:

```text
task-001-foundation-preserve-current-contract
task-002-foundation-tokens-and-shell
task-003-section-hero-structure
task-004-section-hero-assets
task-005-section-hero-motion
```

ID не переименовывать после handoff, чтобы screenshots, notes and follow-up QA могли ссылаться на тот же task.

## Build rings

| Ring | Name | Что входит | Почему раньше |
| --- | --- | --- | --- |
| 0 | Preserve | routes, nav, forms, SEO, legal, analytics-sensitive labels | чтобы не сломать продуктовую механику |
| 1 | Foundation | tokens, layout shell, typography, spacing, surfaces, component wrappers | без этого секции будут разными |
| 2 | Structure | hero, feature, proof, pricing, FAQ, CTA content and layout | сначала readable page, потом polish |
| 3 | Assets | screenshots, generated visuals, diagrams, icons, video, GLB, alt text, dimensions | motion and layout зависят от реальных размеров |
| 4 | Motion | entrance, scroll, hover, state, reduced-motion fallback | motion работает только поверх готовой структуры |
| 5 | Responsive and quality | mobile, tablet, desktop, accessibility, performance, visual QA | качество проверяется на собранной странице |
| 6 | Final handoff | screenshots, commands, risks, launch gate | чтобы следующий агент видел доказательства |

## Task row fields

Каждая задача должна иметь:

- `Task ID`.
- `Ring`.
- `Section`.
- `Blocked by`.
- `Blocks`.
- `Files or routes`.
- `Plan sources`.
- `Change IDs`.
- `Visible result`.
- `Implementation notes`.
- `Dependencies`.
- `Verification`.
- `Evidence`.
- `Risk`.
- `Status`.

## Dependency rules

- `Blocked by` должен ссылаться на task IDs or `none`.
- `Blocks` должен ссылаться на task IDs or `none`.
- Motion task не может идти до section structure task and asset task.
- Asset implementation не может идти до asset queue row.
- Component install не может идти до component source registry and dependency approval.
- Animate UI install не может идти до `14-animate-ui-selection.md`.
- Motion Primitives install не может идти до `29-motion-primitives-selection.md`.
- Magic UI install не может идти до `30-magic-ui-selection.md`.
- Aceternity UI install не может идти до `31-aceternity-ui-selection.md`.
- Tailark install/copy/adaptation не может идти до `32-tailark-section-selection.md`.
- shadcnblocks install/copy/adaptation не может идти до `33-shadcnblocks-selection.md`.
- Kibo UI, Origin/Coss UI or micro-component install/copy/adaptation не может идти до `34-micro-component-selection.md`.
- React Bits install/copy/adaptation не может идти до `35-react-bits-selection.md`.
- PaceKit GSAP install/copy/adaptation не может идти до `36-pacekit-gsap-selection.md`.
- Cult UI install/copy/adaptation не может идти до `37-cult-ui-selection.md`.
- ReUI install/copy/adaptation не может идти до `38-reui-selection.md`.
- 21st.dev install/copy/adaptation не может идти до `39-twenty-first-dev-selection.md`.
- Kokonut UI install/copy/adaptation не может идти до `40-kokonut-ui-selection.md`.
- MVPBlocks install/copy/adaptation не может идти до `41-mvpblocks-selection.md`.
- SmoothUI install/copy/adaptation не может идти до `42-smoothui-selection.md`.
- HextaUI install/copy/adaptation не может идти до `43-hextaui-selection.md`.
- Skiper UI install/copy/reference/adaptation не может идти до `44-skiper-ui-selection.md`.
- Eldora UI install/copy/reference/adaptation не может идти до `45-eldora-ui-selection.md`.
- Blocks.so install/copy/reference/adaptation не может идти до `46-blocks-so-selection.md`.
- Intent UI install/copy/reference/adaptation не может идти до `47-intent-ui-selection.md`.
- Section implementation не может идти до storyboard row and visual style tile.
- Implementation task не должен идти в handoff без `chg-###` links from `28-change-traceability-matrix.md`.
- Final QA не может идти до screenshots, command results and remaining-risk notes.

## Implementation order algorithm

1. Read the source dossier and plan folder.
2. Extract protected constraints from current state audit, copy audit, quality gate and handoff prompt.
3. Create ring 0 preserve task before any visual changes.
4. Create ring 1 foundation task for tokens, shell and reusable primitives.
5. For each section, create structure task first.
6. For each section asset, create asset task before motion.
7. For each section motion, create motion task after structure and assets.
8. Create mobile and accessibility tasks after all major sections exist.
9. Create performance task after all heavy assets and motion exist.
10. Create final QA and handoff tasks last.

## Task types

| Type | Use |
| --- | --- |
| Preserve | protect existing route, nav, form, analytics, SEO, legal, data source |
| Foundation | tokens, layout shell, global CSS, type scale, reusable wrappers |
| Section | visible section content and layout |
| Asset | produce or wire image, screenshot, icon, video, 3D/GLB/WebGL asset |
| Motion | implement animation recipe and reduced-motion fallback |
| Component | install, adapt or create component |
| QA | screenshots, accessibility, performance, visual review, final gate |

## Verification menu

Use the repo's available commands first:

```bash
npm run lint
npm run typecheck
npm run build
npm run check
```

Then add project-specific evidence:

- desktop screenshot;
- mobile screenshot;
- hero viewport screenshot;
- interaction screenshot or short recording when motion matters;
- Lighthouse or browser performance pass when heavy assets changed;
- accessibility scan or manual keyboard/focus check;
- `prefers-reduced-motion` check when motion changed.

## Evidence rule

A task is not done just because code changed. It is done only when the row has evidence that matches its visible result:

- screenshot for visual layout;
- command output for type/build/lint;
- manifest row for assets;
- reduced-motion note for animation;
- URL and reference ID for design inspiration;
- quality-gate update for final QA.

## Common failure patterns

- Starting with a background effect before the offer is clear.
- Installing a component because it looks premium but no section needs it.
- Building motion before real asset dimensions are known.
- Treating mobile as a final shrink step instead of a separate QA task.
- Adding screenshots without naming viewport, section and purpose.
- Leaving a task as "done" with no evidence.

## Output

For each project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/20-implementation-task-graph.md
```

Then update:

```text
план разработки топового лендинга/projects/<slug>/09-implementation-tasks.md
план разработки топового лендинга/projects/<slug>/11-implementation-handoff-prompt.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```
