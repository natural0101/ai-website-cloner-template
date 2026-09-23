# Source Scouting Log

Дата обновления: 2026-07-03.

## Уже полезно в проекте

### Animate UI

Источник: https://animate-ui.com/

Статус: уже добавлен каталог `docs/research/animate-ui-catalog.md` и скиллы `animate-ui-catalog`, `animate-ui-headless-accordion`.

Дополнительный проход: проверены `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons`, icon usage pages, guide pages, `.mdx` endpoints, `registry.json` and all 580 `/r/<item>.json` endpoints. Сайт не отдаёт `sitemap.xml`, поэтому карта собрана через recursive internal crawl, live sidebar, `.mdx` and registry. Итог записан в `17-animate-ui-full-site-map.md`: 361 internal paths probed, 172 live HTML pages, 171 live docs pages, 171 live `.mdx` endpoints, 580/580 registry item endpoints OK.

Повторная проверка всего сайта 2026-07-03 03:16 MSK: свежий non-asset crawl подтвердил те же полезные counts: 172 live HTML pages, 171 docs HTML pages, 171 live `.mdx` endpoints, 75 component docs links, 82 primitive docs links, 6 icon docs links, 8 guide/reference pages, 580 registry items. Новых рабочих разделов вне `/docs` and `/r` не найдено.

Контрольный проход 2026-07-03 03:47 MSK: повторно пройдены `/`, discovered internal non-asset paths, docs HTML, docs `.mdx`, `registry.json` and all 580 item-level registry endpoints. Результат: 580/580 registry item endpoints OK, 73 installable component docs, 81 installable primitive docs, 6 icon docs, 8 guide/reference pages, новых useful non-docs pages нет. Root guide shortcuts без `/docs` возвращают 404, поэтому source URLs должны быть только `/docs/*` or `/r/*`.

Контрольный проход по просьбе пользователя 2026-07-03 05:22 MSK: заново проверены live internal links от `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons`; отдельно проверены docs `.mdx`, `registry.json` and all 580 item endpoints. Результат остался стабильным: `sitemap.xml` отдаёт 404; 186 internal non-asset paths; 172 live HTML pages, 171 docs HTML pages, 171 live `.mdx` endpoints, 75 component docs links including indexes, 82 primitive docs links including index, 6 icon docs, 8 guide/reference pages, 580/580 registry item endpoints OK. Единственная useful non-docs HTML page: `/`.

Контрольный проход всего сайта 2026-07-03 05:49 MSK: снова проверены seed pages, discovered internal non-asset links, docs `.mdx`, registry index and all item endpoints. Результат: `sitemap.xml` 404, 186 internal non-asset paths, 172 live HTML pages, 171 docs `.mdx` endpoints with 200, 8 generated docs paths with 404, registry 200 with 580 items, 580/580 item endpoints OK. Новых рабочих pages outside `/docs` and `/r` нет.

Контрольный проход по просьбе пользователя 2026-07-03 10:48 MSK: снова проверена вся известная surface. Live `HEAD` на `animate-ui.com`: `/` 200, 171 docs pages 200, 171 docs `.mdx` endpoints 200, 580/580 `/r/<item>.json` endpoints 200. Live `GET /r/registry.json` сейчас нестабилен: два раза завис на частичной загрузке 20-24 KB, хотя `HEAD` отдаёт 200. Registry body перепроверен через GitHub raw `apps/www/public/r/registry.json`: 417344 bytes, 580 items, counts unchanged. Для каталога при зависании live registry брать GitHub raw; перед install проверять конкретный live item endpoint.

Контрольный проход по просьбе пользователя 2026-07-03 11:40 MSK: повторно проверена вся известная surface. GitHub raw registry: 200, 417344 bytes, 580 items. Live `HEAD /r/registry.json`: 200; live `GET /r/registry.json`: `ECONNRESET`. Expected HTML surface (`/` plus 171 docs pages) returned 200 after retrying `/docs/changelog`; 171/171 docs `.mdx` endpoints returned 200; calm retry of all registry items returned 580/580 live `/r/<item>.json` endpoints with 200. Service maps remain 404; counts unchanged.

Контрольный проход по просьбе пользователя 2026-07-03 12:20 MSK: проверены service maps, seed pages, official GitHub tree, GitHub raw registry, all docs routes, docs `.mdx` endpoints and every live item endpoint. Service maps remain 404. GitHub tree contains 171 docs routes: 8 guide, 75 component docs including indexes, 82 primitive docs including index, 6 icon docs. Live `HEAD` returned 200 for 171/171 docs routes after retrying `/docs/primitives/base/progress`; docs `.mdx` returned 171/171 200. GitHub raw registry returned 200, 417344 bytes, 580 items. Live `GET /r/registry.json` timed out after partial 20895 bytes, but `HEAD` returned 200 and all 580 live `/r/<item>.json` endpoints returned 200.

Что выяснено при полном проходе: полезная surface почти вся в `/docs` and `/r`; главная `/` не содержит дополнительного component catalog. Registry содержит 73 component entries, 81 primitive entries, 260 icons, 159 demos, 5 hooks, 1 lib and 1 index. `75 component docs links` includes two index/community pages; `82 primitive docs links` includes the primitives index. Hooks/lib are dependency helpers, not visual picks.

Отдельно проверено: `/docs/accessibility` требует reduced-motion discipline через MotionConfig; `/docs/changelog` показывает свежие additions like `motion-carousel`, `radial-menu`, `flip-card`, `gravity-stars`, `image-zoom`, `click`, `shine`; `/docs/roadmap` обещает future blocks/templates/backgrounds/text effects, но их нельзя считать доступными, пока нет registry item. `/docs/other-animated-distributions` даёт discovery leads: Magic UI, React Bits, Hover, Motion Examples, Aceternity UI, Pace UI, Eldora UI, Headless UI, Vue Bits, Inspira UI.

Плохие generated links, найденные crawl: `/docs/primitives/base/menuarrow`, `/menucheckboxitem`, `/menuitem`, `/menuradiogroup`, `/menuradioitem`, `/menushortcut`, `/menusubmenu`, `/menusubmenutrigger`, `/react/primitives/animate/tooltip`. Не использовать их как source.

Где применять: headless/radix/base компоненты, аккуратные animated primitives, accordion, disclosure, UI details.

Ограничение: не ставить все подряд. Брать точечно через catalog.

### Blocks.so

Источник: https://blocks.so/

Статус: добавлен source map `50-blocks-so-source-map.md`, selection template `projects/_template/46-blocks-so-selection.md` and skill `blocks-so-catalog`.

Проверка 2026-07-03: official shadcn registries index содержит `@blocks-so -> https://blocks.so/r/{name}.json`. GitHub repo `ephraimduncan/blocks` returned 200, GitHub API reports MIT, raw `LICENSE.md` is MIT, README documents `@blocks-so` and exact URL install. Sitemap returned 200 with 88 URLs: homepage, 11 category pages and 76 item pages; 88/88 sitemap URLs returned 200 on `HEAD`. GitHub raw registry `public/r/registry.json` returned 200, 571745 bytes, 77 entries. The registry has 76 unique install names because `file-upload-01` appears twice. 76/76 unique live item endpoints `https://blocks.so/r/<name>.json` returned 200. Live `HEAD /r/registry.json` returned 200, but live `GET /r/registry.json` returned `ECONNRESET`; use GitHub raw for catalog rebuilds and verify exact live item endpoints before install.

Где применять: credible app/product proof blocks: stats, onboarding, tables, dialogs, sidebars, AI chat, command menus, file upload, form layouts, grid lists and auth flow proof.

Риск: demo metrics, fake users, fake AI chats, fake file names, fake tables, fake forms and generic dashboard chrome. Reject unless real project content, dependency impact, mobile behavior, accessibility and QA evidence are recorded.

### Taste Skill

Источник: `taste-skill`.

Статус: главный анти-slop фильтр. Он управляет визуальным направлением, motion intensity, density, запретом AI-шаблонов и финальным pre-flight.

Где применять: всегда при планировании лендинга.

### Landing Page High Conversion

Источник: `landing-page-high-conversion`.

Статус: главный conversion-фрейм. Он удерживает лендинг в формате one offer, one audience, one action.

Где применять: структура, CTA, objection handling, FAQ, proof, SEO/AEO.

### Motion Reference Sources

Источники: https://examples.motion.dev/react, https://motion.dev/docs/react-scroll-animations, https://motion.dev/docs/react-layout-animations, https://motion.dev/docs/react-gestures, https://gsap.com/docs/v3/Plugins/ScrollTrigger/, https://gsap.com/showcase/, https://tympanus.net/codrops/category/playground/, https://web.dev/articles/animations-guide, https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

Статус: добавлен слой `30-motion-reference-mining.md`, template `projects/_template/26-motion-reference-map.md` and skill `landing-motion-reference-mining`.

Что выяснено: Motion Examples полезен как gallery motion patterns, Motion docs нужны для implementation boundaries, GSAP ScrollTrigger только для pin/scrub/snap/timeline-heavy scenes, Codrops Playground хорош как experimental interaction reference, web.dev and MDN constrain performance and reduced-motion. Эти источники не заменяют product references: они объясняют motion behavior and implementation risk.

Где применять: before `16-motion-recipe-selection.md`, чтобы каждая анимация имела source URL, pattern, trigger, visible result, borrow, transform, do-not-copy, fallback, mobile simplification and decision.

### Responsive Viewport Sources

Источники: https://web.dev/learn/design/, https://web.dev/learn/design/media-queries, https://web.dev/learn/design/responsive-images, https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design, https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Viewport_meta_element, https://m3.material.io/foundations/layout/applying-layout, https://m3.material.io/foundations/layout/scaffold/overview, https://m3.material.io/foundations/adaptive-design/overview

Статус: добавлен слой `31-responsive-viewport-storyboard.md`, template `projects/_template/27-responsive-viewport-map.md` and skill `landing-responsive-viewport-storyboard`.

Что выяснено: responsive качество нужно планировать до implementation, особенно first viewport, hero crop, nav height, text wrapping, asset aspect ratios, sticky behavior, wide desktop and mobile screenshot QA. Старые Material URLs для window size classes дали 404, актуальные Material layout/adaptive URLs перепроверены and returned 200.

Где применять: before `20-implementation-task-graph.md`, чтобы responsive tasks and screenshot QA вошли в build order.

### Change Traceability Sources

Источники: https://www.figma.com/best-practices/guide-to-developer-handoff/, https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode, https://www.atlassian.com/software/confluence/templates/design-decision, https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record, https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/, https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/

Статус: добавлен слой `32-change-traceability-matrix.md`, template `projects/_template/28-change-traceability-matrix.md` and skill `landing-change-traceability`.

Что выяснено: handoff and verification quality depend on decisions being inspectable and verifiable. Для лендинга это превращается в compact chain: source evidence or assumption -> problem/reason -> reference/brand/section decision -> visible result -> task ID -> QA/evidence method.

Где применять: after `20-implementation-task-graph.md` and before `21-plan-self-review.md`, чтобы self-review saw orphan changes before implementation handoff.

## Новые источники для поиска компонентов и идей

### Magic UI

Источник: https://magicui.design/

Статус: добавлен слой `34-magic-ui-source-map.md`, template `projects/_template/30-magic-ui-selection.md` and skill `magic-ui-catalog`.

Проверка 2026-07-03: crawl found 288 internal paths, 118 live HTML pages, 91 docs pages, 77 component docs and 9 template docs. Registry `https://magicui.design/r/registry.json` returned 200 with 247 total items: 77 `registry:ui`, 168 examples, 1 style and 1 lib. GitHub repo `magicuidesign/magicui` returned 200 and MIT license.

Полезность: animated components/effects под React, TypeScript, Tailwind CSS и Motion. Хорошо подходит для одного сильного landing moment: product video dialog, logo/proof marquee, bento grid, number ticker, animated beam, device/code frame or CTA polish.

Как использовать: брать exact item only after `30-magic-ui-selection.md` records source URL, install command, dependencies, visual/motion purpose, reduced-motion fallback, mobile simplification, decision and QA. Не копировать стиль целиком.

Риск: легко сделать "все блестит". Reject by default: smooth cursor, pointer, dock, cool-mode, decorative confetti, fake tweets/logos/integrations, excessive particles/meteors/grids/glow. Пропускать через `taste-skill` и `ui-audit`.

### Motion Primitives

Источник: https://motion-primitives.com/

Статус: добавлен слой `33-motion-primitives-source-map.md`, template `projects/_template/29-motion-primitives-selection.md` and skill `motion-primitives-catalog`.

Проверка 2026-07-03: direct site crawl returned 429, поэтому использованы official GitHub repo and raw sources. GitHub API returned 200, registry `public/c/registry.json` returned 200 and contains 33 `registry:ui` items, installation docs/source returned 200, `LICENCE.md` returned MIT, README notes beta status.

Полезность: маленькие motion-компоненты, которые проще адаптировать, чем огромные готовые блоки. Лучшие landing uses: `animated-group`, `in-view`, `transition-panel`, short text effects, `animated-number`, `sliding-number`, `magnetic`, `image-comparison`, `scroll-progress`.

Как использовать: брать exact item only after `29-motion-primitives-selection.md` records source URL, install command, dependencies, motion purpose, reduced-motion fallback, mobile simplification, decision and QA.

Риск: не превращать каждую секцию в аттракцион. Reject by default: `cursor`, `dock`, `toolbar-*`, autoplay carousel, long paragraph text effects, excessive glow/tilt/spotlight.

### React Bits

Источник: https://www.reactbits.dev/

Статус: добавлен слой `39-react-bits-source-map.md`, template `projects/_template/35-react-bits-selection.md` and skill `react-bits-catalog`.

Проверка 2026-07-03: website, sitemap, `llms.txt`, root registry and item endpoints returned 200. Sitemap has 141 URLs: 23 text animation pages, 30 animation pages, 36 component pages, 45 background pages, 3 get-started pages and 3 extra pages. `https://reactbits.dev/r/registry.json` returned 536 `registry:component` items. GitHub `public/r` contains 537 JSON files: one `registry.json` plus 536 installable item JSON files. That is 134 unique components in four variants: `JS-CSS`, `JS-TW`, `TS-CSS`, `TS-TW`. Sample endpoints `https://reactbits.dev/r/SplitText-TS-TW` and `https://reactbits.dev/r/SplitText-TS-TW.json` returned JSON. GitHub repo and license returned 200; license is MIT + Commons Clause.

Полезность: exact animated React components for one memorable landing moment: short text animation, metric, section reveal, CTA/card interaction, media/gallery treatment or quiet background.

Как использовать: exact `TS-TW` item only after `35-react-bits-selection.md` records category, source URL, registry URL, install command `npx shadcn@latest add https://reactbits.dev/r/<Component>-TS-TW`, dependencies, license, fallback, mobile simplification, task ID, change ID, decision and QA.

Риск: dependency-heavy and highly visual. Representative TS/TW scan found common dependencies `ogl` 30, `gsap` 29, `three` 22, `motion` 20, `@react-three/fiber` 7. Reject custom cursors, WebGL/3D/shader, physics/game-like effects, long paragraph effects and autoplay galleries unless the section explicitly earns them and performance QA is planned.

### Hover.dev

Источник: https://www.hover.dev/

Статус: reference-only/gated copy source. Отдельный skill не добавлен, потому что это freemium copy-paste surface without shadcn/jsrepo registry.

Проверка 2026-07-03: website, sitemap, license, components index and several category pages returned 200. Sitemap has 36 URLs: home, pricing, templates, faq, features, color palette generator and 30 `/components/*` URLs. Live component categories include `three-d`, `faq`, `forms`, `grids`, `heros`, `boards`, `pricing`, `sign-in`, `testimonials`, `accordions`, `buttons`, `calendars`, `cards`, `carousels`, `countdown`, `dropdown-menu`, `inputs`, `links`, `loaders`, `modals`, `navigation`, `notifications`, `progress`, `tabs`, `tables`, `text`, `toggles`. The guessed `/components/hero-sections` returned 404; use `/components/heros`.

License check: license page says free components can be used without signup or purchase, components not marked free require Hover Pro, commercial/non-commercial use and modification are allowed, attribution is not required, but selling or redistributing components as standalone products is not permitted.

Полезность: interaction and component inspiration for hover states, nav, cards, testimonials, hero sections, pricing, forms, small 3D and playful UI details.

Как использовать: reference-only unless the exact component is marked free or Hover Pro access/license is explicit. Record source URL, access, license, copied files, dependency impact, adaptation, fallback, mobile behavior and QA in the relevant selection file: `33-shadcnblocks-selection.md` for section/block inspiration, `34-micro-component-selection.md` for small components, or `35-react-bits-selection.md` only if the final implementation is actually React Bits.

Риск: no registry endpoint, freemium/pro access, recognizable hover gimmicks, loaders/custom cursor/3D overuse, category paths can differ from guessed names.

### PaceKit GSAP

Источник: https://gsap.pacekit.dev/

Статус: добавлен слой `40-pacekit-gsap-source-map.md`, template `projects/_template/36-pacekit-gsap-selection.md` and skill `pacekit-gsap-catalog`.

Проверка 2026-07-03: old `https://ui.paceui.com/` returned Vercel deployment 404, current `https://paceui.com/` and `https://gsap.pacekit.dev/` returned 200. `https://gsap.pacekit.dev/r/registry.json` returned 200 with 29 items: 1 `registry:style` and 28 `registry:ui`. GitHub repo `https://github.com/pacekit/gsap` returned 200; `public/r` contains 30 JSON files including `registry.json` and `mcp.json`; `LICENSE.md` is MIT. Live item endpoint `https://gsap.pacekit.dev/r/ai-modal-ability-selector.json` returned 200 JSON. Guessed `https://www.paceui.com/r/gsap/<item>.json` returned "registry doesn't exist", so do not use it.

Полезность: exact GSAP-powered shadcn registry items for text reveal, scramble, AI response writing, stagger/scroll reveal, stacked cards, button tactility and a few advanced surface effects.

Как использовать: exact item only after `36-pacekit-gsap-selection.md` records source URL, registry URL, install command `npx shadcn@latest add https://gsap.pacekit.dev/r/<item>.json`, `gsap`/`@gsap/react` dependency impact, registry dependencies, fallback, mobile simplification, task ID, change ID, decision and QA.

Риск: 26 of 28 UI items depend on `gsap` and `@gsap/react`. Reject if CSS, Motion Primitives, Animate UI, React Bits or existing components can do the same job. Reject custom cursor, loaders, fake AI UI, trend-only liquid glass and simple reveals without GSAP-worthy choreography.

### Cult UI

Источник: https://www.cult-ui.com/

Статус: добавлен слой `41-cult-ui-source-map.md`, template `projects/_template/37-cult-ui-selection.md` and skill `cult-ui-catalog`.

Проверка 2026-07-03: website, docs, installation docs, MCP docs, sitemap, live registry, GitHub repo and license returned 200. Root `https://cult-ui.com/` redirects to `https://www.cult-ui.com/`. Sitemap has 87 URLs, 86 docs URLs and 77 component docs URLs. `https://www.cult-ui.com/r/registry.json` returned 200 with 157 items: 78 `registry:ui` and 79 `registry:component` demo/example entries. All 157 item endpoints returned 200. Root `/registry.json` returned 404. GitHub repo `nolly-studio/cult-ui` returned 200; raw registry `apps/www/public/r/registry.json` returned 200; `LICENSE.md` is MIT.

Полезность: textured cards/buttons, product proof frames, browser/code/terminal mockups, animated numbers/text, hover media, poll/voting/onboarding widgets, quiet textures and a few hero surface ideas.

Как использовать: exact `registry:ui` item only after `37-cult-ui-selection.md` records source URL, registry URL, install command `npx shadcn@latest add https://cult-ui.com/r/<item>.json` or `@cult-ui/<item>`, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile simplification, task ID, change ID, decision and QA.

Риск: 32 items depend on `motion`; special dependencies include `@paper-design/shaders-react`, `three`, `jotai`, `dither-plugin`, `metal-fx`, `vaul`, `border-beam` and `embla-carousel-autoplay`. Reject shader/3D/heavy hero surfaces, fake `tweet-grid`, AI widgets, dock/dynamic-island, loading carousel, neumorphism/pixel/glass trends unless the brand and section job earn them.

### ReUI

Источник: https://reui.io/

Статус: добавлен слой `42-reui-source-map.md`, template `projects/_template/38-reui-selection.md` and skill `reui-catalog`.

Проверка 2026-07-03: website, docs, get-started, registry docs, license setup, MCP docs, agent skills docs, sitemap, pricing, legal license and terms returned 200. Sitemap has 209 URLs: 45 docs, 69 component pages, 36 component docs pages and 55 block pages. Root `/registry.json` returned 404. Root/style registry indexes returned 401 without license key. Docs state free component examples use `c-*` names and premium blocks, icons and templates require `REUI_LICENSE_KEY`. Pricing page reports 1019 free components. Component page scan extracted 1019 `c-*` variant names. Exact sample endpoints `https://reui.io/r/radix-nova/c-button-1.json`, `c-data-grid-1.json`, and `alert.json` returned 200 JSON; `button.json` returned 401 without license.

Контрольный sitemap-проход 2026-07-03 05:49 MSK: all 209 URLs from `https://reui.io/sitemap.xml` returned 200. Counts stayed stable: 45 docs URLs, 69 component pages, 36 docs component pages, 55 block pages, 1 templates page. Registry gate stayed the same: `/registry.json` 404, `/r/registry.json` 401 without license, exact free samples 200, locked `button.json` 401.

Полезность: credible app/product UI details: data grids, tables, frames, forms, filters, file upload, status alerts, ratings, timelines, dashboards and admin/product preview surfaces.

Как использовать: exact item only after `38-reui-selection.md` records style (`radix-nova` by default), source URL, registry URL, install command, free/pro access, license key status, dependencies, registry dependencies, adaptation, mobile behavior, keyboard/focus QA, task ID, change ID, decision and QA.

Риск: premium access, authenticated registry config, heavy data/grid/drag dependencies, and duplicate shadcn primitives. Treat 401/403 endpoints without license evidence as reference-only. Do not use ReUI as page visual identity.

### 21st.dev

Источник: https://21st.dev/

Статус: добавлен слой `43-21st-dev-source-map.md`, template `projects/_template/39-twenty-first-dev-selection.md` and skill `twenty-first-dev-catalog`.

Проверка 2026-07-03: website, community components, community templates, MCP page, `@shadcn` author page and sitemap returned 200. Sitemap has 9384 URLs: 8260 author/component pages, 1000 component tag/category pages, 92 weekly component pages and 26 theme pages. Category checks: hero 284, background 40, shader 87, AI chat 78, features 102, call-to-action 56. Generic registry guesses such as `https://21st.dev/r/shadcn/button` returned 403, so do not use guessed `/r/*` endpoints. Component pages expose commands like `npx @21st-dev/cli@beta add arlanoska/symbols-effect`; checked CDN registry JSON returned 200 for sample items. NPM `@21st-dev/cli@beta` returned version `1.1.5`, MIT.

Полезность: large inspiration and exact-component surface for hero, background, shader, AI-chat, CTA, pricing, feature, product-widget, table, calendar, sparkline and app-like details.

Как использовать: reference-first. Exact install only after `39-twenty-first-dev-selection.md` records component page, author/item, command, CDN registry URL or reference-only, license, dependency impact, adaptation, fallback, mobile behavior, task ID, change ID, decision and QA.

Риск: huge community marketplace, uneven quality, hidden Next payload install metadata, heavy WebGL/Three/HeroUI/chart/icon dependencies, unclear license on some items, and visual style drift. Reject broad imports and generic `/r/*` guesses.

### Kokonut UI

Источник: https://kokonutui.com/

Статус: добавлен слой `44-kokonut-ui-source-map.md`, template `projects/_template/40-kokonut-ui-selection.md` and skill `kokonut-ui-catalog`.

Проверка 2026-07-03: website, docs, sitemap, `llms.txt`, public registry, GitHub repo and raw license returned 200. Sitemap has 49 URLs: 47 docs URLs and 40 public registry items. Registry `https://kokonutui.com/r/registry.json` returned 40 `registry:component` items; all 40 item endpoints returned 200. Dependencies are mostly `motion` on 31 items and `lucide-react` on 20 items. GitHub license is MIT. `kokonutui.pro` returned 200 but `https://kokonutui.pro/r/registry.json` returned 404 HTML, so Pro is reference-only unless access/license is explicit.

Полезность: small shadcn-compatible source for AI prompt/search, file upload, bento/cards, animated buttons, navigation details, background hero accents and text effects.

Как использовать: exact public item only after `40-kokonut-ui-selection.md` records docs URL, registry URL, install command, MIT/pro access, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID, decision and QA.

Риск: Pro/templates access, decorative `motion`, liquid glass/tweet/fake AI/loaders, and local design-system drift. Reject if native CSS, Motion Primitives, Animate UI, Magic UI, React Bits, Cult UI, ReUI or current components can do the same job with lower risk.

### Aceternity UI

Источник: https://ui.aceternity.com/

Статус: добавлен слой `35-aceternity-ui-source-map.md`, template `projects/_template/31-aceternity-ui-selection.md` and skill `aceternity-ui-catalog`.

Проверка 2026-07-03: bounded crawl found 500 internal paths, 470 live HTML pages, 118 component pages and many `/blocks/*` pages. Registry `https://ui.aceternity.com/registry.json` returned 200 with 270 total items: 109 `registry:ui` and 161 `registry:block`. Item registry path is `https://ui.aceternity.com/registry/<name>.json`; `/r/*` returned 404. License/pro page returned 200 and contains redistribution restrictions for paid items.

Полезность: много high-impact components and blocks for landing pages: hero parallax, bento grids, sticky scroll, timeline, tracing beam, compare, testimonials, product/code frames, card systems and CTA treatments.

Как использовать: exact `registry:ui` item only after `31-aceternity-ui-selection.md` records type, source URL, install command, license/access, dependencies, adaptation required, fallback, mobile simplification, decision and QA. Treat `registry:block`, templates and All-Access/pro material as reference-only unless license/access is explicit.

Риск: паттерны узнаваемые and dependency-heavy. Не клонировать визуально 1:1. Reject heavy particles/shaders/Three/canvas, fake testimonials/logos/screenshots, floating pointers/docks/loaders unless the section earns them and QA budget exists.

### Tailark

Источник: https://tailark.com/

Статус: добавлен слой `36-tailark-section-source-map.md`, template `projects/_template/32-tailark-section-selection.md` and skill `tailark-section-catalog`.

Проверка 2026-07-03: public sitemap returned 208 URLs. Live category/home surface is 18 URLs; 190 old preview URLs shaped like `/preview/<category>/<Title> (dusk-kit)` returned 404. Current live public previews use paths like `https://tailark.com/preview/dusk/hero-section/one`. Public root `https://tailark.com/registry.json` returned 404, but item registry URLs like `https://tailark.com/r/hero-section-1.json`, `https://tailark.com/r/mist-hero-section-1.json`, and `https://tailark.com/r/veil-hero-section-1.json` returned 200.

GitHub check: official repo `https://github.com/tailark/blocks` returned 200, `LICENCE.md` is MIT, raw public registry contains 154 items: 20 `registry:ui` and 134 `registry:block`; raw Veil registry contains 76 items: 19 `registry:ui` and 57 `registry:block`. Public docs say to configure `"@tailark": "https://tailark.com/r/{name}.json"` and install with `pnpm dlx shadcn add @tailark/<name>`.

Pro check: `https://pro.tailark.com/docs/quick-setup` returned 200 and requires a generated API key. Pro sitemap returned 621 URLs; after normalizing malformed `https:/pro...` entries, 547 returned 200 and 74 `/pages/*` URLs returned 404. Treat Tailark Pro blocks, pages and illustrations as reference-only unless access and license are explicit.

Полезность: marketing blocks, SaaS pages, pricing, FAQ, testimonials, CTA, auth, contact, footer, bento rhythm, proof and page structure.

Как использовать: exact public item or reference-only decision only after `32-tailark-section-selection.md` records live source URL, preview URL, registry URL, install command, access/license, dependencies, adaptation, fallback, mobile simplification, task ID, change ID, decision and QA.

Риск: stale sitemap previews, no root registry, recognizable block look, pro/API-key restrictions, demo copy/logos/screenshots. Не копировать Pro/premium части, если нет доступа и лицензии.

### Kibo UI

Источник: https://www.kibo-ui.com/

Статус: добавлен общий micro-component слой `38-micro-component-source-map.md`, template `projects/_template/34-micro-component-selection.md`, общий skill `micro-component-source-catalog` and dedicated skill `kibo-ui-catalog`.

Проверка 2026-07-03: docs returned 200 and reported 41 components, 28 blocks and 1101 patterns. GitHub repo `shadcnblocks/kibo` returned 200, default branch `main`, MIT license, 3837 stars, latest observed push `2026-05-04T06:00:08Z`. Root `https://www.kibo-ui.com/registry.json` returned 404. Live `https://www.kibo-ui.com/r/registry.json` returned `HEAD` 200 but body can time out after partial JSON. GitHub raw registry is not a static file because `apps/docs/app/r/registry.json` is a route folder. 37 live item endpoints parsed as JSON: `announcement`, `avatar-stack`, `banner`, `calendar`, `choicebox`, `code-block`, `color-picker`, `combobox`, `comparison`, `contribution-graph`, `credit-card`, `cursor`, `deck`, `dialog-stack`, `dropzone`, `glimpse`, `image-crop`, `image-zoom`, `kanban`, `list`, `marquee`, `mini-calendar`, `pill`, `qr-code`, `rating`, `relative-time`, `sandbox`, `snippet`, `spinner`, `status`, `table`, `tags`, `theme-switcher`, `ticker`, `tree`, `typography`, `video-player`. `editor`, `gantt` and `reel` returned `HEAD` 200 but live body timed out at partial 21880 bytes, so require fresh body fetch or source adaptation before use. Generic guesses `button`, `accordion` and `ai-input` returned package lookup errors.

License check: GitHub repo metadata reports MIT and `license.md` is MIT-style.

Полезность: exact shadcn-compatible micro-components for forms, product/app previews, code snippets, ratings, tags, status, upload/dropzone, data/table, media and UI details.

Как использовать: exact item only after `34-micro-component-selection.md` records item URL, install command `npx shadcn@latest add https://www.kibo-ui.com/r/<item>.json`, dependencies, license, adaptation, mobile behavior, keyboard/focus QA, task ID, change ID, decision and QA.

Риск: many items are client-heavy. Reject by default: guessed package names, `cursor`, editors, gantt/kanban/video/player/table/calendar/code stacks if the landing only needs a static visual. For `editor`, `gantt`, or `reel`, require fresh body-fetch proof or mark reference-only/backlog.

### Coss UI / Origin UI

Источник: https://originui.com/

Current live URL: https://coss.com/ui

Статус: добавлен в общий micro-component слой `38-micro-component-source-map.md`, template `projects/_template/34-micro-component-selection.md` and skill `micro-component-source-catalog`.

Проверка 2026-07-03: `originui.com` routes redirect to `https://coss.com/ui`. `originui.com/r/accordion.json` redirected to HTML, not JSON. Live JSON endpoints work at `https://coss.com/ui/r/<name>.json`, with `accordion.json` and `button.json` returning 200 JSON. GitHub repo `https://github.com/shadcn/originui` returned 200; raw `registry.json` contains 646 items: 40 `registry:ui`, 600 `registry:component`, 5 `registry:hook`, 1 `registry:lib`. License is MIT.

Полезность: Base UI-oriented and shadcn-compatible small components: forms, dialog, popover, input, select, command, tooltip, drawer, date/calendar, upload/file UI, tables, avatar, badges and buttons.

Как использовать: exact item only after `34-micro-component-selection.md` records verified `https://coss.com/ui/r/<item>.json` endpoint or GitHub copy source, dependencies, license, adaptation, mobile behavior, keyboard/focus QA, task ID, change ID, decision and QA.

Риск: do not overwrite project CSS variables or shadcn style system just to use one component. Do not use `originui.com/r/*` unless it returns JSON; prefer Coss live endpoint or GitHub registry.

### shadcnblocks

Источник: https://www.shadcnblocks.com/

Статус: добавлен слой `37-shadcnblocks-source-map.md`, template `projects/_template/33-shadcnblocks-selection.md` and skill `shadcnblocks-catalog`.

Проверка 2026-07-03: sitemap returned 3912 URLs. Bounded HEAD crawl over sitemap URLs found 3908 live and 4 broken: `/blocks/hero/layered`, `/blocks/hero/quad`, `/blocks/hero/inline-image-text`, and `/page/modern-page2`. Live surface includes 1645 `/block/*` pages, 1684 `/component/*` pages, 87 component category pages, 267 live block category pages, 47 page item pages, 16 template pages, 34 docs pages and 78 changelog pages.

Access check: `/blocks/free` linked 106 free block pages and detail pages reported `Access: free`. Free registry examples `https://www.shadcnblocks.com/r/hero1.json` and `https://www.shadcnblocks.com/r/feature1.json` returned 200. Pro examples `https://www.shadcnblocks.com/r/hero125.json` and `https://www.shadcnblocks.com/r/pricing1.json` returned 401 without API key. Root `https://www.shadcnblocks.com/registry.json` returned 404.

Docs check: CLI docs show registry config `"@shadcnblocks": "https://www.shadcnblocks.com/r/{name}.json"` for public items and bearer-token setup with `SHADCNBLOCKS_API_KEY` for Pro. License page allows commercial/client end products but restricts redistributing components or derivatives outside an end product. Free GitHub repo `shadcnblocks/shadcn-ui-blocks` has MIT plus Commons Clause.

Полезность: huge shadcn-compatible source for hero, feature, pricing, FAQ, CTA, logo/proof, testimonials, contact, book-a-demo, case study, ecommerce, app preview, dashboard, data table, forms, pages and templates.

Как использовать: exact item only after `33-shadcnblocks-selection.md` records live item URL, access status, registry URL, install command or reference-only, license/access, dependencies, adaptation, fallback, mobile simplification, task ID, change ID, decision and QA.

Риск: Pro/Premium is not available without API key, free license has Commons Clause restrictions, root registry is 404, and copied blocks can create generic block-library rhythm. Do not use for reusable kits, marketplaces, website builders, AI generators or competing component products.

### SaaS Landing Page

Источник: https://saaslandingpage.com/

Полезность: SaaS landing examples по секциям, страницам, industries, colors, fonts, tech и tools.

Как использовать: искать близкую структуру hero, pricing, features, FAQ, social proof.

Риск: не превращать все SaaS в одинаковые hero/cards/pricing. Использовать как структурный benchmark.

### Saaspo

Источник: https://saaspo.com/

Полезность: curated SaaS inspiration с фильтрами по pages, industries, styles, assets, colors, fonts, stack.

Как использовать: быстро подобрать 3 direct/domain references и 3 visual references.

Риск: это inspiration, не component source. Нельзя копировать branding или claims.

### SaaSFrame

Источник: https://www.saasframe.io/

Полезность: gallery SaaS websites, sections, copy and visual references.

Как использовать: быстрый benchmark для SaaS hero, features, pricing, testimonials.

Риск: структурный источник, не компонентная библиотека.

### Mobbin

Источник: https://mobbin.com/

Полезность: product UI and mobile/web flow references.

Как использовать: если лендинг обещает signup, onboarding, dashboard, app workflow, искать реальные flow patterns.

Риск: часть доступа может быть платной. Не копировать чужой product UI как бренд.

### Page Flows

Источник: https://pageflows.com/

Полезность: user flow recordings and screenshots for onboarding, checkout, signup, activation.

Как использовать: проверять, что лендинг ведет в понятный next step and product experience.

Риск: использовать как UX reference, не как visual style source.

### Codrops

Источник: https://tympanus.net/codrops/

Полезность: interaction demos, creative coding, WebGL, GSAP, CSS motion ideas.

Как использовать: только для motion references и unusual interaction patterns.

Риск: демки часто тяжелые или экспериментальные. Нужно адаптировать и проверять performance/reduced motion.

### Motion Docs

Источник: https://motion.dev/

Полезность: официальный источник для Motion for React, gestures, layout animation, scroll, reduced motion.

Как использовать: сверять реализацию motion-компонентов и fallbacks.

Риск: не использовать Motion там, где достаточно CSS transition.

### Web.dev Core Web Vitals

Источник: https://web.dev/vitals/

Полезность: LCP, INP, CLS как performance gate для лендингов с hero images, video, 3D и animation.

Как использовать: проверка после внедрения тяжелых ассетов и motion.

### Nielsen Norman Group Heuristics

Источник: https://www.nngroup.com/articles/ten-usability-heuristics/

Полезность: базовая UX-проверка clarity, feedback, consistency, error prevention.

Как использовать: sanity check для forms, CTA, навигации и интерактивных секций.

### CXL

Источник: https://cxl.com/blog/landing-page-optimization/

Полезность: conversion research, message match, landing page optimization framing.

Как использовать: обосновывать hero promise, CTA, offer clarity, proof placement и traffic-source alignment.

Риск: не превращать CRO статьи в универсальный закон. Применять к конкретному трафику и offer.

### Baymard

Источник: https://baymard.com/

Полезность: e-commerce, product page, checkout, filtering/search UX research.

Как использовать: если лендинг продает товар, подписку, checkout или product detail flow.

Риск: часть исследований premium. Не выдавать закрытый материал за открытый.

### Growth.Design

Источник: https://growth.design/

Полезность: UX/product psychology case studies, onboarding, conversion, retention.

Как использовать: объяснять поведенческую логику секций, onboarding promises, signup friction.

Риск: стиль комикса не копировать автоматически.

### Laws of UX

Источник: https://lawsofux.com/

Полезность: быстрые UX principles для cognitive load, choice overload, familiarity, feedback.

Как использовать: как vocabulary для обоснования, не как строгую норму.

### Figma Developer Handoff / Dev Mode

Источники:

- https://www.figma.com/best-practices/guide-to-developer-handoff/
- https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode

Полезность: developer handoff, annotations, inspectable design context, variables/styles/components.

Как использовать: как модель для нашего dossier/handoff: сохранять constraints, states, component notes, tokens and implementation details.

Риск: это не runtime source и не замена реальному коду. Не использовать термин Dev Mode как название нашей фичи/инструмента.

### UXPin Design Handoff Checklist

Источник: https://www.uxpin.com/studio/blog/design-handoff-checklist/

Полезность: checklist mindset for before/during/after handoff, design states, specs and developer communication.

Как использовать: усилить implementation handoff prompt and quality gate.

Риск: не копировать весь checklist как обязательный процесс, брать только применимые пункты.

### Lighthouse

Источник: https://developer.chrome.com/docs/lighthouse

Полезность: performance, accessibility, best practices and SEO audits.

Как использовать: финальный QA и launch gate, особенно после добавления изображений, видео, WebGL или animation libraries.

### WCAG / WAI

Источники:

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/WAI/fundamentals/

Полезность: accessibility baseline, contrast, keyboard, readable content, reduced motion.

Как использовать: accessibility QA для текста, форм, фокуса, alt text and motion.

### axe DevTools

Источник: https://docs.deque.com/devtools-for-web/

Полезность: automated accessibility testing support.

Как использовать: если есть browser/tooling, прогонять как дополнительную проверку, не как единственный критерий.

### Playwright Accessibility Testing

Источник: https://playwright.dev/docs/accessibility-testing

Полезность: automated accessibility checks in browser workflows.

Как использовать: если проект уже использует Playwright или есть browser automation.

### Playwright Screenshots And Visual Comparisons

Источники:

- https://playwright.dev/docs/screenshots
- https://playwright.dev/docs/test-snapshots

Полезность: screenshot capture and visual comparison when Playwright is already part of the project.

Как использовать: desktop/mobile/hero screenshots and optional visual regression checks.

Риск: не добавлять Playwright только ради одного screenshot без согласования.

### Percy

Источник: https://www.browserstack.com/docs/percy

Полезность: visual regression workflows for teams that already use Percy/BrowserStack.

Как использовать: только если проект уже использует Percy или пользователь просит.

### Chromatic

Источник: https://www.chromatic.com/docs/

Полезность: visual tests for Storybook/component workflows.

Как использовать: если проект уже работает со Storybook/Chromatic.

### Saaspo Sections And Hero References

Источник: https://saaspo.com/

Полезность: section-level SaaS examples, especially hero, pricing, feature and proof patterns.

Как использовать: выбирать конкретные section patterns, а не просто общий visual mood.

### Appcues Product-Led Onboarding

Источник: https://www.appcues.com/blog/product-led-growth

Полезность: product-led flow thinking, onboarding and activation context for app/SaaS landings.

Как использовать: product flow rail, onboarding promise, activation-oriented sections.

### Reference Scoring And UX Benchmarking

Источники:

- https://www.nngroup.com/articles/competitive-usability-evaluations/
- https://www.nngroup.com/articles/benchmarking-ux/
- https://baymard.com/ux-benchmark
- https://baymard.com/research/product-page
- https://mobbin.com/
- https://pageflows.com/

Полезность: превращает reference research в scored decision, а не в moodboard по вкусу.

Как использовать: direct/domain references проверять по product/audience/offer fit; visual references проверять по visual fit and differentiation; motion references проверять по motion value and accessibility/performance risk; Mobbin/Page Flows использовать для user-flow context.

Риск: не считать score математической истиной. Score нужен, чтобы заставить агента объяснить выбор и отклонить слабые references.

### Motion Systems And Recipes

Источники:

- https://motion.dev/docs/react-scroll-animations
- https://gsap.com/docs/v3/Plugins/ScrollTrigger/
- https://web.dev/articles/animations-guide
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- https://m3.material.io/styles/motion/easing-and-duration
- https://fluent2.microsoft.design/motion
- https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/

Полезность: дает основу для motion recipes, а не случайных эффектов. Motion for React покрывает scroll-triggered and scroll-linked patterns, GSAP нужен только для настоящего pin/scrub, web.dev удерживает performance, MDN and Apple reduced motion удерживают accessibility.

Как использовать: сначала выбрать section recipe, потом библиотеку. Для простых hover/reveal использовать CSS/Motion; для pinned scroll использовать GSAP только при явной storytelling причине; для depth/parallax/auto motion делать reduced-motion fallback.

Риск: motion легко выглядит как demo. Любая анимация без purpose, fallback and QA должна быть удалена.

### Motion Safety Gate

Источник: `53-motion-safety-source-map.md`

Статус: accepted as `landing-motion-safety-gate`.

Проверено 2026-07-03: WCAG 2.2, WCAG Understanding 2.3.3 Animation from Interactions, MDN `prefers-reduced-motion`, web.dev prefers-reduced-motion, web.dev animations guide, web.dev animations and performance, web.dev Core Web Vitals, web.dev LCP, Chrome DevTools animations, Material motion easing/duration, Fluent 2 motion, Apple HIG motion and Apple reduced-motion evaluation criteria all returned `200`.

Полезность: добавляет safety verdict layer after motion references and before implementation. Каждая анимация получает verdict: `safe`, `needs-simplification`, `static-fallback-only` or `reject`, плюс reduced-motion fallback, mobile simplification, performance risk and QA method.

Как использовать: read `53-motion-safety-source-map.md` before accepting rows in `26-motion-reference-map.md`, `16-motion-recipe-selection.md` and `07-animation-storyboard.md`. Reject motion that hides CTA, shifts layout, lacks fallback, adds heavy dependencies for small flourishes or risks LCP/INP/CLS.

Риск: не превращать safety gate в запрет на всю анимацию. Цель: оставить motion that helps hierarchy, storytelling, feedback or state transition, and simplify the rest.

### Visual Direction And Style Tiles

Источники:

- https://styletil.es/
- https://www.figma.com/blog/design-systems-101-what-is-a-design-system/
- https://www.figma.com/design-systems/
- https://m3.material.io/foundations
- https://atlassian.design/foundations
- https://atlassian.design/tokens/
- https://carbondesignsystem.com/elements/2x-grid/overview/

Полезность: style tile превращает "сделать красиво" в конкретные visual tokens and section rules. Design systems sources дают foundations, tokens, spacing and consistency thinking.

Как использовать: после reference scoring создать style tile: visual read, primary direction, token sheet, section style rules, do-not-do list, implementation notes.

Риск: не превращать style tile в жесткий design system там, где нужен один landing. Он должен давать direction and tokens, а не тормозить implementation.

### Section Storyboards And Wireframes

Источники:

- https://www.figma.com/resource-library/what-is-wireframing/
- https://www.figma.com/resource-library/how-to-make-a-user-journey-map/
- https://www.nngroup.com/articles/storyboards-visualize-ideas/
- https://www.nngroup.com/articles/journey-mapping-101/
- https://www.interaction-design.org/literature/topics/storyboards
- https://www.uxpin.com/studio/blog/wireframe-examples/

Полезность: wireframes and storyboards force the plan to show structure, user job, sequence, visible result and risk before implementation.

Как использовать: after references, style tile, patterns and motion recipes, fill a section storyboard canvas for every major section.

Риск: canvas не должен стать low-fidelity design theater. Он нужен для implementation clarity, not documentation vanity.

### Asset Production And Media Optimization

Источники:

- https://nextjs.org/docs/app/api-reference/components/image
- https://web.dev/learn/images/
- https://web.dev/articles/optimize-lcp
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/alt
- https://accessibility.huit.harvard.edu/describe-content-images
- https://web.dev/articles/lazy-loading-video
- https://modelviewer.dev/
- https://threejs.org/docs/#examples/en/loaders/GLTFLoader

Полезность: asset queue keeps hero visuals, screenshots, generated imagery, video and GLB/WebGL from becoming vague placeholders. It also forces alt text, stable dimensions, priority/lazy strategy, poster/fallback and mobile crop.

Как использовать: after section storyboard, list every required asset with role, type, source, spec, prompt/capture instruction, file path, mobile crop, alt text, performance and status.

Риск: не генерировать декоративные ассеты ради красоты. Если asset не поддерживает proof, explanation, emotion, memory, navigation or motion, он не нужен.

### Implementation Task Graph And Handoff

Источники:

- https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies
- https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/about-tasklists
- https://playwright.dev/docs/test-snapshots
- https://developer.chrome.com/docs/lighthouse/overview
- https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Performance_budgets
- https://web.dev/articles/performance-budgets-101
- https://web.dev/articles/use-lighthouse-for-performance-budgets

Полезность: превращает красивый план в порядок внедрения с blockers, task IDs, visible result, files, verification and evidence. GitHub sources дают language for dependencies and tasklists; Playwright, Lighthouse and performance budgets дают доказательный QA layer.

Как использовать: after storyboard, assets, motion recipes and visual style tile, fill `20-implementation-task-graph.md`, then update `09-implementation-tasks.md` and `11-implementation-handoff-prompt.md`.

Риск: не превращать план в project-management theater. Task graph нужен только для порядка работ, блокеров and evidence.

### Source Dossier Forensics

Источники:

- https://playwright.dev/docs/screenshots
- https://playwright.dev/docs/test-snapshots
- https://developer.chrome.com/docs/lighthouse/overview
- https://developer.chrome.com/docs/devtools/css-overview
- https://developer.chrome.com/docs/devtools/coverage
- https://developer.chrome.com/docs/devtools/performance
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/What_is_accessibility
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

Полезность: усиливает самый первый handoff. Source project must send facts, not vibes: screenshots, viewport names, files, routes, visual tokens, assets, commands, accessibility/motion/performance risks.

Как использовать: before moving a simple landing into this planning project, run `01-universal-prompt-source-project.md` with the forensics checklist and validate the result with `scripts/check-source-dossier.mjs`.

Риск: не заставлять другой проект делать полноценный redesign audit. Forensics нужен только для baseline evidence.

### Inspiration Synthesis

Источники:

- https://www.nngroup.com/articles/competitive-usability-evaluations/
- https://www.nngroup.com/articles/benchmarking-ux/
- https://www.figma.com/resource-library/how-to-make-a-mood-board/
- https://www.figma.com/blog/design-critiques-at-figma/
- https://www.atlassian.com/blog/loom/design-review
- https://m3.material.io/styles/motion/overview

Полезность: переводит references в конкретные decisions. Scorecard говорит "этот URL полезен"; synthesis говорит "в hero берем композиционную логику, меняем asset treatment, не копируем brand identity, motion адаптируем так".

Как использовать: after `15-reference-scorecard.md`, fill `22-inspiration-synthesis.md` before final visual direction, section storyboard, motion storyboard and plan self-review.

Риск: не превращать moodboard в копирование. Каждый borrow должен иметь transform and do-not-copy boundary.

### Presentation Quality Review

Источники:

- https://www.figma.com/blog/design-critiques-at-figma/
- https://www.atlassian.com/blog/loom/design-review
- https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- https://www.nngroup.com/articles/aesthetic-usability-effect/
- https://credibility.stanford.edu/guidelines/
- https://m3.material.io/styles/motion/overview
- https://m3.material.io/styles/motion/transitions/applying-transitions

Полезность: добавляет post-implementation critique по screenshots/live preview. Этот слой проверяет first impression, above-the-fold clarity, visual hierarchy, trust, composition, distinctiveness, reference translation, motion polish, asset quality and mobile presentation.

Как использовать: после implementation screenshots fill `23-presentation-quality-review.md`, затем только после non-blocked verdict закрывать `12-final-qa-report.md`.

Риск: не подменять screenshot review вкусовщиной. Каждый finding должен ссылаться на viewport, screenshot/live evidence, section and exact visual fix.

### Thematic Reference Mining

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

Полезность: добавляет слой перед reference scorecard. Он заставляет искать не только прямых конкурентов, но и adjacent, analogous, flow, visual, motion/component and anti references. Для каждого URL нужно объяснить closeness reason: product, audience, CTA, trust model, workflow, asset type, emotion or interaction.

Как использовать: после dossier и before `15-reference-scorecard.md` fill `24-thematic-reference-map.md`; затем продвигать в scorecard только candidates with clear section use and acceptable risk.

Риск: нельзя тащить "красивый сайт" без причины близости. Если нет live URL/screenshot or no closeness reason, reference rejected.

### Brand DNA Preservation

Источники:

- https://www.figma.com/blog/design-systems-101-what-is-a-design-system/
- https://www.figma.com/design-systems/
- https://www.nngroup.com/articles/design-systems-101/
- https://www.nngroup.com/articles/design-systems-vs-style-guides/
- https://www.nngroup.com/articles/front-end-style-guides/
- https://atlassian.design/foundations/
- https://m3.material.io/foundations
- https://carbondesignsystem.com/elements/2x-grid/overview/

Полезность: добавляет pre-style-tile слой, который извлекает current brand DNA: promise, voice, colors, type, layout rhythm, surfaces, icons, assets, motion and protected content. Он не даёт redesign agent заменить текущий продукт чужим reference style.

Как использовать: after dossier/current audit fill `25-brand-dna-map.md`; then style tile, storyboard, asset queue, task graph and handoff must respect Preserve/Evolve/Remove/Introduce/Protect decisions.

Риск: нельзя сохранять слабый дизайн просто потому что он текущий. Preserve только если есть screenshot/source/copy/business/user evidence.

## Источники визуального вдохновения

### Recent / Godly

Источник: https://godly.website/

Полезность: свежие подборки web/interface/branding/product/typography/motion/3D/editorial.

Как использовать: moodboard, визуальный язык, типографика, motion references.

### Land-book

Источник: https://land-book.com/

Полезность: фильтры по type, industry, style, typography, color, platform. Подходит для поиска близких лендингов.

Как использовать: 3 domain references + 3 aesthetic references.

### Lapa Ninja

Источник: https://www.lapa.ninja/

Полезность: большая база landing page examples, категории SaaS, AI, 3D, bento, typography, gradient, etc.

Как использовать: искать страницы по категории продукта и вытаскивать паттерны секций.

### Awwwards

Источник: https://www.awwwards.com/

Полезность: interaction design, WebGL, GSAP, 3D, scrolling, animated websites.

Как использовать: только для сильных interaction references и art direction. Не тащить тяжелые эффекты без пользы.

### Reference Gallery Source Map

Источник: `52-reference-gallery-source-map.md`

Статус: accepted as `landing-reference-source-catalog`.

Проверено 2026-07-03: Land-book homepage and sitemap returned automation `403`; Lapa Ninja homepage returned automation `403` while sitemap returned `200`; Godly redirected to Recent and returned `200`; Recent returned `200`; Awwwards homepage returned `200` and sitemap returned `404`; Codrops returned `200`; Motion Examples and Motion docs returned `200`; Mobbin homepage and sitemap returned `200`; Pageflows homepage and sitemap returned `200`; SaaSFrame homepage and sitemap/RSS returned `200`; SaaS Landing Page homepage and sitemap index returned `200`; Saaspo returned automation `403`; Landingfolio homepage and sitemap returned `200`; One Page Love returned `525`; Siteinspire returned automation `429`; Minimal Gallery returned `200`; MaxiBestOf returned automation `403`; Refero, HTTPSTER, Dark Mode Design, Navbar Gallery, Baymard and NN/g returned `200`.

Полезность: закрывает routing problem перед reference research. Теперь агент выбирает lane first: direct/domain landing examples, SaaS structure, product flow, visual language, motion/interaction, CRO/UX evidence, header/navigation or anti-reference.

Как использовать: read `52-reference-gallery-source-map.md` before `24-thematic-reference-map.md`; record access status for every candidate; promote only references with section mapping and clear closeness reason.

Риск: blocked automation is not a dead source. `403`, `429`, `525`, timeout, browser/manual only and premium/account-gated states must be recorded as access caveats, not ignored.

## Внешние skill-кандидаты

### github/awesome-copilot premium frontend UI

Источник: https://github.com/github/awesome-copilot/blob/main/skills/premium-frontend-ui/SKILL.md

Статус: не установлен напрямую.

Почему: есть полезная энергия про polish/motion, но есть риск конфликта с нашим `taste-skill`: custom cursors, preloaders, слишком много motion и визуального шума.

Что берем: идею "frontend should feel premium".

Что не берем: автоматический перегрев, если brief этого не требует.

### Motion AI Kit

Источник: https://motion.dev/

Статус: не установлен.

Почему: Motion упоминает AI Kit для Codex/Claude, но это часть Motion+ и может требовать платный доступ. Нельзя считать доступным по умолчанию.

Что берем: идею точных motion specs и официальную документацию Motion.

Что не берем: зависимость от платного набора без решения пользователя.

## Правило отбора

Новый источник принимается только если он закрывает одну из дыр:

1. Лучше исследует references.
2. Лучше выбирает компоненты.
3. Лучше планирует motion.
4. Лучше проверяет качество.
5. Лучше переносит факты между проектами.

Если источник просто дублирует `taste-skill` или делает дизайн более шаблонным, он не нужен.

### MVPBlocks

Источник: https://blocks.mvp-subha.me/

Статус: accepted as `mvpblocks-catalog` with strict gates.

Проверено 2026-07-03: website 200, sitemap 96 URLs, `llms.txt` 200, `llms-full.txt` 200, GitHub repo `subhadeeproy3902/mvpblocks` 200, repo license BSD-3-Clause, npm package `mvpblocks` version 2.1.13 with MIT package metadata. CLI constants list 252 items: 77 `registry:ui`, 171 `registry:block`, 3 hooks and 1 lib. All 252 exact endpoints `https://blocks.mvp-subha.me/r/<name>.json` returned 200. Root `/r/registry.json` and `/registry.json` returned 404, so never use root registry indexes as install proof.

Полезность: strong source for fast section structure, MVP templates, hero/pricing/FAQ/CTA/testimonial/header/footer/bento/dashboard/chatbot blocks and short text animations. It fills a gap between Tailark/shadcnblocks section structure and small component sources.

Как использовать: read `45-mvpblocks-source-map.md`, then fill `projects/<slug>/41-mvpblocks-selection.md` before using `npx mvpblocks add <name> --ts` or an exact endpoint install. Record docs URL, endpoint URL, dependencies, license caveat, adaptation, mobile behavior, reduced-motion fallback, task ID and change ID.

Риск: broad template copying, fake proof, demo screenshots, Framer Motion/GSAP/dashboard/chatbot dependencies, Next-specific imports and decorative cursor/loader/3D effects. Reject unless the section job earns the dependency and the copy/assets are rewritten for the product.

### SmoothUI

Источник: https://smoothui.dev/

Статус: accepted as `smoothui-catalog` with strict gates.

Проверено 2026-07-03: website 200, sitemap 110 URLs, robots 200, `llms.txt` 200, `llms-full.txt` 200, `llms-components.json` 200, `openapi.json` 200, `https://smoothui.dev/r/registry.json` 200 with 107 items, and all 107 exact item endpoints `https://smoothui.dev/r/<name>.json` returned 200. Component API returned 72 components with category, dependency, animation and reduced-motion metadata. Practical registry split: 72 components plus 35 block/shared items. GitHub repo `educlopez/smoothui` and npm package `smoothui-cli` report MIT license; npm version is 1.1.1. Legacy `/registry.json` returned 404. `/api/v1/blocks` returned an empty list and `/api/v1/blocks/<name>` returned 500, so never use the blocks API as block evidence.

Полезность: strong source for exact animated controls, CTA/button tactility, product UI proof, AI UI accents, text effects, metric motion and small section blocks. It fills the gap between small component sources like Kokonut UI and broader block/template sources like MVPBlocks.

Как использовать: read `46-smoothui-source-map.md`, then fill `projects/<slug>/42-smoothui-selection.md` before using `npx shadcn@latest add @smoothui/<name>`, `npx smoothui-cli@latest add <name>` or an exact endpoint install. Record docs or preview URL, endpoint URL, dependencies, registry dependencies, MIT license, API/registry evidence, adaptation, mobile behavior, reduced-motion fallback, task ID and change ID.

Риск: most items use `motion`; fake AI, fake tweets, fake reviews, fake stars and fake logos can weaken trust; `gooey-popover` brings `gsap`; `tweet-card` brings `react-tweet`; block API is broken; `hasReducedMotion=false` items need custom fallback. Reject unless the section job earns the dependency and the proof/copy is real.

### HextaUI

Источник: https://www.hextaui.com/

Статус: accepted as `hextaui-catalog` with strict gates.

Проверено 2026-07-03: website 200, showcase 200, components index 200, docs root `/docs` 404, sitemap index 200, child sitemap 143 URLs, `llms.txt` 200, RSS 200, `https://www.hextaui.com/r/registry.json` 200 with 139 items, and all 139 exact item endpoints `https://www.hextaui.com/r/<name>.json` returned 200. Official shadcn `registries.json` contains `@hextaui` mapped to `https://hextaui.com/r/{name}.json`. GitHub repo `preetsuthar17/HextaUI` reports MIT license, raw `LICENSE` on `master` is MIT, and raw GitHub registry matches the public registry. Legacy `/registry.json` returned 404 and `registry.hextaui.com/r/registry.json` returned 404. During direct fetch audit, many individual HTML component/block pages timed out, so endpoint JSON, `llms.txt`, GitHub registry and official shadcn registry entry are the reliable evidence path.

Полезность: strong source for app/SaaS proof blocks: AI prompt/chat/model/citations/usage, auth onboarding, billing/pricing/subscription, settings/admin, team collaboration and task/project workflows. It fills an app-product-proof gap between ReUI, MVPBlocks and SmoothUI.

Как использовать: read `47-hextaui-source-map.md`, then fill `projects/<slug>/43-hextaui-selection.md` before using `npx shadcn@latest add @hextaui/<name>` or exact endpoint install. Record source URL from `llms.txt` or HTML page when it loads, endpoint URL, dependencies, registry dependencies, MIT license, HTML-doc caveat, demo-data replacement, mobile behavior, task ID and change ID.

Риск: broad replacement of local shadcn primitives, fake product surfaces, dense mobile layouts, and dependencies such as `react-markdown`, `shiki`, `recharts`, `next`, `vaul`, `react-day-picker`, `embla-carousel-react` or `react-resizable-panels`. Reject if the section does not need real app UI proof or if demo users, invoices, usage numbers, prompts and workflows cannot be made credible.

### Skiper UI

Источник: https://skiper-ui.com/

Статус: accepted as `skiper-ui-catalog` with strict terms/access gates.

Проверено 2026-07-03: official shadcn registry index contains `@skiper-ui` mapped to `https://skiper-ui.com/registry/{name}.json`. Website `HEAD` 200, components page 200, pricing page 200 on `HEAD`, terms page 200, sitemap 200 with 218 URLs, robots 200, `llms.txt` 404, docs root `/docs` 404. Sitemap contains 105 `/v1/skiper*` pages and 105 `/preview/skiper*` pages; all `/v1` pages returned 200 on `HEAD`, and all preview pages returned 404. Registry index `https://skiper-ui.com/registry/registry.json` returned 200 with 38 `registry:ui` items, and 38/38 exact endpoints `https://skiper-ui.com/registry/<name>.json` returned 200 on `HEAD`. Wrong paths `/r/registry.json`, sampled `/r/<name>.json`, and root `/registry.json` are not valid install evidence. Some full HTML `GET` requests timed out or reset, so use registry endpoints plus successful HTML pages as evidence.

Access/license caveat: Skiper UI is not treated as MIT. Pricing advertises Premium and Exclusive access, and terms restrict republishing, selling, reproducing, copying and redistributing website material. No official public MIT/source repo was verified. Use public registry items only after recording project-specific terms/access status; never copy premium, account-only, paid template, private source or Figma material.

Как использовать: read `48-skiper-ui-source-map.md`, then fill `projects/<slug>/44-skiper-ui-selection.md` before using `npx shadcn@latest add @skiper-ui/<name>` or exact endpoint install. Record exact item, source URL, endpoint URL, terms/access status, dependencies, registry dependencies, reduced-motion fallback, mobile behavior, task ID and change ID. Best candidates are scroll stories, short text motion, real metrics/progress, proof carousels, product-detail hover, video, tooltip and input details. Reject preview URLs, premium/private material, brand-like demos without strong adaptation, sound/mouse-follow/debug tools by default and GSAP/Lenis/Swiper when a lighter source can do the job.

### Eldora UI

Источник: https://eldoraui.site/

Статус: accepted as `eldora-ui-catalog` with strict runtime and proof gates.

Проверено 2026-07-03: official shadcn registry index contains `@eldoraui` mapped to `https://eldoraui.site/r/{name}.json`. Sitemap 200 with 56 URLs, all sitemap URLs returned 200 on `HEAD`; `robots.txt` 200; `llms.txt` 200; `https://eldoraui.site/r/registry.json` 200 with 115 items; all 115 exact item endpoints `https://eldoraui.site/r/<name>.json` returned 200. Wrong sampled path `https://eldoraui.site/registry/<name>.json` returned 404. GitHub repo `karthikmudunuri/eldoraui` reports MIT, raw `LICENSE.md` is MIT, and raw GitHub public registry matches 115 items. Full HTML `GET` on `www` and some docs pages can timeout, so use bare domain, `HEAD`, `llms.txt`, registry endpoints and GitHub raw registry as reliable evidence.

Полезность: exact device/browser frames, terminal/GitHub/product proof, integrations/globe/map, animated text, CTA/status details, visual depth backgrounds and small section blocks. It fills a product-proof and device mockup gap between SmoothUI, Skiper UI, HextaUI and MVPBlocks.

Как использовать: read `49-eldora-ui-source-map.md`, then fill `projects/<slug>/45-eldora-ui-selection.md` before using `npx shadcn@latest add @eldoraui/<name>` or exact endpoint install. Record exact item, item type, docs/source URL, endpoint URL, MIT license, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, performance risk, task ID and change ID.

Риск: `registry:example` items should be reference-only by default; blocks can create template identity; device frames, terminal output, GitHub comments, testimonials, logos and integration proof can become fake evidence; globe/map/background effects bring runtime cost (`cobe`, `three`, `ogl`, `react-three-fiber`, `react-spring`). Reject unless the section job earns the dependency and real content replaces demo content.

### Blocks.so

Источник: https://blocks.so/

Статус: accepted as `blocks-so-catalog` with strict app-proof and fake-proof gates.

Проверено 2026-07-03: official shadcn registry index contains `@blocks-so` mapped to `https://blocks.so/r/{name}.json`. Sitemap 200 with 88 URLs: homepage, 11 category pages and 76 item pages. All 88 sitemap URLs returned 200 on `HEAD`. GitHub repo `ephraimduncan/blocks` reports MIT, raw `LICENSE.md` is MIT, README documents `@blocks-so` and exact URL install. GitHub raw registry `public/r/registry.json` returned 200, 571745 bytes, 77 entries, all `registry:block`. There are 76 unique install names because `file-upload-01` is duplicated in the registry index. 76/76 unique live item endpoints `https://blocks.so/r/<name>.json` returned 200. Live `HEAD /r/registry.json` returned 200, but live `GET /r/registry.json` returned `ECONNRESET`; use GitHub raw registry for catalog rebuilds, then verify exact live item endpoints before install.

Полезность: credible app/product proof blocks for stats, auth/login, onboarding, tables, dialogs, sidebars, AI chat, command menus, file upload, form layouts and grid lists. It fills a practical product-surface gap between ReUI, HextaUI, MVPBlocks, SmoothUI and Eldora UI.

Как использовать: read `50-blocks-so-source-map.md`, then fill `projects/<slug>/46-blocks-so-selection.md` before using `npx shadcn@latest add @blocks-so/<name>` or exact endpoint install. Record exact item, category, source page, endpoint URL, MIT license, duplicate-entry caveat, dependencies, registry dependencies, demo-data replacement, accessibility notes, mobile behavior, task ID and change ID.

Риск: fake dashboards, fake metrics, fake users, fake AI chats, fake file names, fake tables, fake forms and generic app chrome. Reject unless the section job earns the block and real project content replaces demo content.

### Intent UI

Источник: https://intentui.com/

Статус: accepted as `intent-ui-catalog` with strict React Aria, accessibility and anti-bulk-install gates.

Проверено 2026-07-03: sitemap 200 with 108 URLs and 108/108 URLs returned 200 on `HEAD`; `robots.txt` 200; `llms.txt` 200 with 8094 bytes; GitHub repo `intentui/intentui` reports MIT and default branch `3.x`; raw `3.x/LICENSE` is MIT; raw `3.x/registry.json` returned 200, 459676 bytes, 569 items. Registry split: 88 `registry:ui`, 438 `registry:page` examples, 25 `registry:block`, 12 themes, 3 hooks, 2 libs and 1 `all` item. 569/569 live `/r/<name>.json` endpoints returned 200 on `HEAD`. Both `https://intentui.com/r/<name>` and `https://intentui.com/r/<name>.json` returned JSON on sampled items. Live `GET /r/registry.json` returned `ECONNRESET`; root `/registry.json` returned 404. Use GitHub raw registry for catalog rebuilds and verify exact live item endpoints before install.

Полезность: accessible React Aria product UI controls: forms, fields, selects, combo boxes, date/time/color controls, tables, grids, trees, command menus, overlays, navbars, sidebars, charts and auth blocks. It fills an accessibility-heavy app-interface gap between local shadcn/Radix, Origin/Coss, Kibo UI, ReUI, HextaUI and Blocks.so.

Как использовать: read `51-intent-ui-source-map.md`, then fill `projects/<slug>/47-intent-ui-selection.md` before using `npx shadcn@latest add @intentui/<name>` or exact endpoint install. Record exact item, item type, source URL, endpoint URL, MIT license, React Aria dependency impact, dependencies, registry dependencies, demo-data replacement, accessibility notes, mobile behavior, task ID and change ID.

Риск: React Aria Components stack can be a broad dependency shift; `registry:page` examples are reference-only by default; `all` and theme entries are not valid install choices; paid `design.intentui.com` material is not public source without access/license; demo users, fake forms, fake charts and generic app chrome must be replaced or rejected.
