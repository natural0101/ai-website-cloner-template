# Animate UI Full Site Map

Дата обновления: 2026-07-03.

Источники проверки:

- https://animate-ui.com/
- https://animate-ui.com/docs
- https://animate-ui.com/docs/components
- https://animate-ui.com/docs/primitives
- https://animate-ui.com/docs/icons
- https://animate-ui.com/docs/icons/get-started
- https://animate-ui.com/docs/icons/usage/animations
- https://animate-ui.com/docs/icons/usage/persistence
- https://animate-ui.com/docs/icons/usage/timing
- https://animate-ui.com/docs/icons/usage/triggers
- https://animate-ui.com/docs/accessibility
- https://animate-ui.com/docs/changelog
- https://animate-ui.com/docs/roadmap
- https://animate-ui.com/docs/other-animated-distributions
- https://animate-ui.com/r/registry.json
- https://github.com/imskyleen/animate-ui

Проверка registry: 580 items total. Из них 1 style `index`, 159 `demo-*`, 260 `icons-*`, 73 `components-*`, 81 `primitives-*`, 5 `hooks-*`, 1 `lib-*`. Все 580 item-level endpoints вида `/r/<item>.json` отдают 200. Для работы с лендингами брать только точечные installable items, а demo использовать как reference формы и поведения.

Проверка live docs: `sitemap.xml` отсутствует, сайт отдаёт 404. Карта собрана через live sidebar на `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons` и через `.mdx` endpoints страниц. Найдено 171 unique docs links: 75 component docs links, 82 primitive docs links, 6 icon docs links, 8 guide/reference pages.

Проверка полного сайта: рекурсивный crawl внутренних ссылок от `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons` нашёл 361 internal paths total, 172 live HTML pages with 200, 171 docs `.mdx` endpoints with 200, and only one live non-docs HTML page: `/`. Главная страница даёт только внешние ссылки GitHub/X and static assets, поэтому полезная рабочая поверхность сайта находится в `/docs` and `/r`.

Повторная проверка всего сайта 2026-07-03 03:16 MSK: строгий non-asset crawl прошёл 351 internal paths, подтвердил 172 live HTML pages, 171 live docs HTML pages, 171 live docs `.mdx` endpoints, 75 component docs links, 82 primitive docs links, 6 icon docs links, 8 guide/reference pages and 580 registry items. Все найденные новые 404 совпали с уже известными generated links. Три icon endpoints, которые дали timeout в параллельном проходе (`icons-sun-dim`, `icons-thumbs-up`, `icons-x`), отдельно перепроверены через `/r/<item>.json` and returned 200.

Контрольный проход всего сайта 2026-07-03 03:47 MSK: заново проверены `/`, все найденные internal non-asset paths, docs HTML, docs `.mdx`, `registry.json` and all 580 `/r/<item>.json` endpoints. Итог не изменился: `sitemap.xml` отдаёт 404; 172 live HTML pages, 171 docs HTML pages, 171 live docs `.mdx` endpoints, 73 installable component docs, 81 installable primitive docs, 6 icon docs, 8 guide/reference pages, 580/580 registry item endpoints OK, новых useful non-docs app pages нет. Root shortcuts `/installation`, `/accessibility`, `/mcp`, `/roadmap`, `/other-animated-distributions` return 404; использовать только `/docs/installation`, `/docs/accessibility`, `/docs/mcp`, `/docs/roadmap`, `/docs/other-animated-distributions`.

Контрольный проход по просьбе пользователя 2026-07-03 05:22 MSK: заново пройдены live internal links от `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons`; отдельно проверены docs `.mdx`, `registry.json` and all `/r/<item>.json` endpoints. Итог остался тем же: `sitemap.xml` отдаёт 404; 186 internal non-asset paths discovered; 172 live HTML pages; 171 docs HTML pages; 171 live docs `.mdx` endpoints; 75 component docs links including indexes; 82 primitive docs links including index; 6 icon docs; 8 guide/reference pages; 580 registry items and 580/580 item endpoints OK. Единственная useful non-docs HTML page по-прежнему `/`.

Контрольный проход всего сайта 2026-07-03 05:49 MSK: повторно пройдены `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons`, все найденные internal non-asset links, docs `.mdx`, `registry.json` and all 580 registry item endpoints. Итог стабилен: `sitemap.xml` отдаёт 404; 186 internal non-asset paths discovered; 172 live HTML pages; 171 docs `.mdx` endpoints with 200; 8 generated docs paths with 404; registry отдаёт 580 items; 580/580 `/r/<item>.json` endpoints OK. Новых useful pages вне `/docs` and `/r` нет.

Контрольный проход по просьбе пользователя 2026-07-03 06:21 MSK: заново проверены root/docs branches, service-map paths, docs `.mdx`, `registry.json` and every `/r/<item>.json` endpoint. `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/docs/llms.txt`, `/.well-known/llms.txt`, `/docs.json` and `/openapi.json` all return 404, so готовой machine-readable карты сайта нет. Краул внутренних non-asset ссылок дал 181 paths: 172 HTML 200 and 9 generated/internal 404. Все 171 docs `.mdx` endpoints 200. Registry stable: 580 items and 580/580 item endpoints 200. Единственная useful non-docs HTML page остаётся `/`.

Контрольный проход по просьбе пользователя 2026-07-03 10:48 MSK: проверена вся известная рабочая поверхность сайта через live `HEAD` на `animate-ui.com` плюс source registry из GitHub raw, потому что live `GET /r/registry.json` дважды завис на частичной загрузке 20-24 KB. Результат: `/` 200, все 171 docs pages 200, все 171 docs `.mdx` endpoints 200, service maps по-прежнему 404, `/r/registry.json` даёт 200 на `HEAD`, GitHub raw `apps/www/public/r/registry.json` скачан полностью 417344 bytes and 580 items, all 580 live `/r/<item>.json` endpoints return 200 on `HEAD`. Новых рабочих разделов вне `/docs` and `/r` нет. Caveat для агентов: если body live registry stalls, rebuild catalog from GitHub raw, но перед install всё равно проверять выбранный live item endpoint.

Контрольный проход по просьбе пользователя 2026-07-03 11:40 MSK: снова проверена вся известная рабочая поверхность через GitHub raw registry plus live `HEAD` and calm retries. GitHub raw `apps/www/public/r/registry.json` fetched fully at 417344 bytes and 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` returned `ECONNRESET`. Expected HTML surface (`/` plus 171 docs pages) returned 200 after retrying `/docs/changelog`; all 171 docs `.mdx` endpoints returned 200; all 580 live `/r/<item>.json` endpoints returned 200 after calm retry. Service maps remain 404; counts unchanged; новых рабочих разделов вне `/docs` and `/r` нет.

Контрольный проход по просьбе пользователя 2026-07-03 12:20 MSK: заново проверены service maps, seed pages, official GitHub tree, GitHub raw registry, все docs routes, docs `.mdx` endpoints and every live `/r/<item>.json` endpoint. Service maps всё ещё 404. GitHub tree returned 171 unique docs routes: 8 guide pages, 75 component docs including indexes, 82 primitive docs including index, 6 icon docs. Live `HEAD` returned 200 for all 171 docs routes after retrying `/docs/primitives/base/progress`; all 171 docs `.mdx` endpoints returned 200. GitHub raw registry fetched fully at 417344 bytes and 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` timed out after partial 20895 bytes. All 580 live `/r/<item>.json` endpoints returned 200. Вывод: для полного inventory использовать GitHub tree plus raw registry, затем проверять exact live item endpoint перед install.

Контрольный проход по просьбе пользователя 2026-07-03 12:59 MSK: заново проверены service maps, seed pages, official GitHub tree, GitHub raw registry, все docs routes, docs `.mdx` endpoints and every live `/r/<item>.json` endpoint. Итог стабильный: service maps всё ещё 404; seed pages `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons` returned 200; GitHub tree returned 171 unique docs routes: 8 guide pages, 75 component docs including indexes, 82 primitive docs including index, 6 icon docs; 171/171 live docs routes returned 200; 171/171 docs `.mdx` endpoints returned 200; GitHub raw registry fetched fully at 417344 bytes and 580 items; live `HEAD /r/registry.json` returned 200 while live `GET /r/registry.json` hit a bounded `AbortError`; all 580 live `/r/<item>.json` endpoints returned 200. Вывод не изменился: для полного inventory использовать GitHub tree plus raw registry, затем проверять exact live item endpoint перед install.

Контрольный проход по просьбе пользователя 2026-07-03 13:43 MSK: заново проверена вся полезная поверхность сайта: 7 service-map guesses, 5 seed pages, official GitHub tree, все 171 docs routes, все 171 docs `.mdx` endpoints, raw registry, live registry `HEAD`, bounded live registry `GET` and every live `/r/<item>.json` endpoint. Итог стабильный: service maps всё ещё 404; seed pages returned 200; GitHub tree returned 171 unique docs routes: 8 guide pages, 75 component docs including indexes, 82 primitive docs including index, 6 icon docs; 171/171 live docs routes returned 200; 171/171 docs `.mdx` endpoints returned 200; raw registry returned 580 items; live `HEAD /r/registry.json` returned 200 while live `GET /r/registry.json` hit a bounded `AbortError`; all 580 live `/r/<item>.json` endpoints returned 200. Counts unchanged: 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, 1 style index.

Уточнение counts: `75 component docs links` = 73 installable component pages + `/docs/components` + `/docs/components/community`. `82 primitive docs links` = 81 installable primitive pages + `/docs/primitives`. Нормальный selection pool из registry: 73 components + 81 primitives + 5 hooks + 1 lib = 160 non-demo/non-icon items, но hooks/lib are service dependencies, not visual choices.

Найденные плохие internal/generated links: `/docs/primitives/base/menuarrow`, `/menucheckboxitem`, `/menuitem`, `/menuradiogroup`, `/menuradioitem`, `/menushortcut`, `/menusubmenu`, `/menusubmenutrigger` from `/docs/components/base/menu`, and `/react/primitives/animate/tooltip` from `/docs/components/animate/tooltip`. Их не использовать как source URLs. Для menu брать `/docs/components/base/menu` and `/docs/primitives/base/menu`; для tooltip брать `/docs/components/animate/tooltip` and `/docs/primitives/animate/tooltip`.

## Полный проход сайта

### Guide pages

| Page | Зачем смотреть |
| --- | --- |
| `/docs` | базовая модель: Animate UI это copy-first distribution, не npm-library |
| `/docs/installation` | установка через shadcn CLI и структура проекта |
| `/docs/accessibility` | reduced motion, Motion accessibility and comfort rules |
| `/docs/mcp` | shadcn Registry MCP setup, полезно как reference, но не обязательный путь |
| `/docs/troubleshooting` | version floor: Motion, React, Tailwind, Base UI, Radix, Headless UI |
| `/docs/changelog` | новые компоненты и icon updates |
| `/docs/roadmap` | upcoming blocks/templates and multi-primitive direction |
| `/docs/other-animated-distributions` | discovery список соседних animated distributions |

### Whole-site crawl evidence

| Surface | Result | Notes |
| --- | ---: | --- |
| Homepage HTML | 1 live page | `/` only; useful outbound links are GitHub and X |
| Docs HTML | 171 live pages | full docs surface |
| Docs `.mdx` | 171 live endpoints | source-like content for every docs page |
| Registry index | 580 items | `/r/registry.json` |
| Registry item endpoints | 580 live endpoints | `/r/<registry-name>.json`, all checked 200 |
| Service maps | 0 live maps | `sitemap.xml`, `robots.txt`, `llms.txt`, `docs.json`, `openapi.json` return 404 |
| Non-docs internal app pages | 0 useful pages | no extra component docs outside `/docs` |
| Latest user-requested rewalk | stable at 2026-07-03 13:43 MSK | GitHub tree has 171 docs routes; 171/171 live docs routes 200, 171/171 docs `.mdx` 200, 580/580 live item endpoints 200; live registry `GET` hit bounded `AbortError`, GitHub raw registry body OK |

### Exact component docs inventory

| Branch | Pages |
| --- | --- |
| `components/animate` | `avatar-group`, `code`, `code-tabs`, `cursor`, `github-stars-wheel`, `tabs`, `tooltip` |
| `components/backgrounds` | `bubble`, `fireworks`, `gradient`, `gravity-stars`, `hexagon`, `hole`, `stars` |
| `components/base` | `accordion`, `alert-dialog`, `checkbox`, `dialog`, `files`, `menu`, `popover`, `preview-card`, `preview-link-card`, `progress`, `radio`, `switch`, `tabs`, `toggle`, `toggle-group`, `tooltip` |
| `components/buttons` | `button`, `copy`, `flip`, `github-stars`, `icon`, `liquid`, `ripple`, `theme-toggler` |
| `components/community` | `flip-card`, `management-bar`, `motion-carousel`, `notification-list`, `pin-list`, `playful-todolist`, `radial-intro`, `radial-menu`, `radial-nav`, `share-button`, `user-presence-avatar` |
| `components/headless` | `accordion`, `checkbox`, `dialog`, `popover`, `switch`, `tabs` |
| `components/radix` | `accordion`, `alert-dialog`, `checkbox`, `dialog`, `dropdown-menu`, `files`, `hover-card`, `popover`, `preview-link-card`, `progress`, `radio-group`, `sheet`, `sidebar`, `switch`, `tabs`, `toggle`, `toggle-group`, `tooltip` |

### Exact primitive docs inventory

| Branch | Pages |
| --- | --- |
| `primitives/animate` | `avatar-group`, `code-block`, `cursor`, `github-stars`, `motion-grid`, `pinned-list`, `scroll-progress`, `slot`, `spring`, `tabs`, `tooltip` |
| `primitives/base` | `accordion`, `alert-dialog`, `checkbox`, `collapsible`, `dialog`, `files`, `menu`, `popover`, `preview-card`, `preview-link-card`, `progress`, `radio`, `switch`, `tabs`, `toggle`, `toggle-group`, `tooltip` |
| `primitives/buttons` | `button`, `flip`, `liquid`, `ripple` |
| `primitives/effects` | `auto-height`, `blur`, `click`, `effect`, `fade`, `highlight`, `image-zoom`, `magnetic`, `particles`, `shine`, `slide`, `theme-toggler`, `tilt`, `zoom` |
| `primitives/headless` | `checkbox`, `dialog`, `disclosure`, `popover`, `switch`, `tabs` |
| `primitives/radix` | `accordion`, `alert-dialog`, `checkbox`, `collapsible`, `dialog`, `dropdown-menu`, `files`, `hover-card`, `popover`, `preview-link-card`, `progress`, `radio-group`, `sheet`, `switch`, `tabs`, `toggle`, `toggle-group`, `tooltip` |
| `primitives/texts` | `counting-number`, `gradient`, `highlight`, `morphing`, `rolling`, `rotating`, `scrolling-number`, `shimmering`, `sliding-number`, `splitting`, `typing` |

### Other animated distributions from the site

Animate UI itself points to these complementary sources on `/docs/other-animated-distributions`; treat them as discovery leads, not automatic installs.

| Source | URL | Use |
| --- | --- | --- |
| Magic UI | https://magicui.design | marketing effects and hero moments |
| React Bits | https://reactbits.dev | animated React inspiration |
| Hover | https://www.hover.dev/ | interaction examples |
| Motion Examples | https://examples.motion.dev/react | Motion reference examples |
| Aceternity UI | https://ui.aceternity.com | recognizable high-impact blocks, adapt heavily |
| Pace UI | https://ui.paceui.com/ | additional UI inspiration |
| Eldora UI | https://www.eldoraui.site/ | additional UI inspiration |
| Headless UI | https://headlessui.com/ | accessible unstyled primitives |
| Vue Bits | https://vue-bits.dev | Vue-side inspiration only |
| Inspira UI | https://inspira-ui.com/ | Vue-side inspiration only |

### Guide page findings

- `/docs/accessibility`: use `MotionConfig reducedMotion="user"` at the app root when Animate UI/Motion is used.
- `/docs/changelog`: current public docs show `1.0.27` on 2025-12-15; recent additions include `motion-carousel`, `radial-menu`, `flip-card`, `radial-intro`, `gravity-stars`, `image-zoom`, `click`, `shine`, and many animated icons.
- `/docs/roadmap`: blocks, templates, new animated backgrounds, text animations, effects, carousel, dropzone, magnetic cursor and more primitive coverage are planned/in progress. Do not rely on roadmap items as available install sources until they appear in registry/docs.

### Live docs structure

| Branch | Live docs count | Что внутри | Как использовать |
| --- | ---: | --- | --- |
| `/docs/components` | 75 | landing-ready styled components, category index pages and community page | брать готовый компонент только если он совпадает с section job |
| `/docs/primitives` | 82 | low-level effects, primitive wrappers, text motion and behavior | брать как motion foundation под свой visual style |
| `/docs/icons` | 6 | icon start page and usage pages for animations, persistence, timing, triggers | ставить wrapper and exact icons only |
| `/docs` guide pages | 8 | installation, accessibility, MCP, troubleshooting, roadmap, changelog, alternatives | читать перед внедрением or audit |

### Component branches

| Branch | Installable pages | URL base | Good use |
| --- | ---: | --- | --- |
| `components/animate` | 7 | `/docs/components/animate/*` | tabs, tooltip, code, cursor, avatar group, GitHub stars wheel |
| `components/backgrounds` | 7 | `/docs/components/backgrounds/*` | one ambient hero/background layer |
| `components/base` | 16 | `/docs/components/base/*` | app-like controls when Base UI is intentional |
| `components/buttons` | 8 | `/docs/components/buttons/*` | CTA, copy, icon, theme and special buttons |
| `components/community` | 11 | `/docs/components/community/*` | carousel, notification, pin, share, presence, radial demos |
| `components/headless` | 6 | `/docs/components/headless/*` | accordion, checkbox, dialog, popover, switch, tabs with Headless UI semantics |
| `components/radix` | 18 | `/docs/components/radix/*` | shadcn/Radix-compatible interaction surfaces |

### Primitive branches

| Branch | Installable pages | URL base | Good use |
| --- | ---: | --- | --- |
| `primitives/animate` | 11 | `/docs/primitives/animate/*` | reusable motion shells: slot, tabs, tooltip, scroll progress, spring |
| `primitives/base` | 17 | `/docs/primitives/base/*` | Base UI behavior primitives |
| `primitives/buttons` | 4 | `/docs/primitives/buttons/*` | button motion behavior under custom styles |
| `primitives/effects` | 14 | `/docs/primitives/effects/*` | fade, slide, zoom, blur, auto height, magnetic, tilt, shine, particles |
| `primitives/headless` | 6 | `/docs/primitives/headless/*` | Headless UI behavior primitives |
| `primitives/radix` | 18 | `/docs/primitives/radix/*` | Radix behavior primitives |
| `primitives/texts` | 11 | `/docs/primitives/texts/*` | short text effects, metrics and hero word motion |

### Icons branch

Animate UI icons are animated Lucide icons and are marked beta on the docs. Use them only when the icon itself carries meaning in a button, nav action, status or product affordance.

| Page | Use |
| --- | --- |
| `/docs/icons/get-started` | install the icon wrapper and exact icons |
| `/docs/icons/usage/animations` | choose icon animation name, not every icon supports the same custom animation |
| `/docs/icons/usage/persistence` | decide whether the icon returns to initial state or keeps the animated state |
| `/docs/icons/usage/timing` | set delay and loop rules |
| `/docs/icons/usage/triggers` | choose animate, hover, tap or controlled trigger |

Icon rules:

- Install `icons-icon` wrapper only if animated icons are actually used.
- Install individual icons like `icons-arrow-right`, never treat all 260 icons as a normal bundle.
- Use loop only when the final state matches the initial state or the loop is a deliberate status signal.
- Prefer hover/tap triggers for CTA and tool buttons. Avoid autoplaying icons in dense content.
- For reduced motion, icon animation must degrade to a static Lucide icon or a single opacity/state transition.

### Registry-only service entries

The registry includes 5 `hooks-*` entries and 1 `lib-get-strict-context` entry. Live docs pages for `/docs/hooks/*` and `/docs/lib/*` currently return 404. Treat them as dependency-chain items, not as visual choices for a landing.

## Что есть на сайте

| Семейство | Count | Для чего на лендинге | Риск |
| --- | ---: | --- | --- |
| `components/animate` | 7 | tabs, tooltip, code, cursor, avatar group, GitHub stars wheel | cursor и GitHub stars wheel легко выглядят как gimmick |
| `components/backgrounds` | 7 | hero/background scene, ambient layer, product mood | шум, performance, конкуренция с CTA |
| `components/base` | 16 | app-like controls на landing или embedded product UI | dependency на `@base-ui-components/react` может не совпасть с проектом |
| `components/buttons` | 8 | CTA, copy, theme toggle, icon actions | liquid/ripple/particles быстро перегревают UI |
| `components/community` | 11 | carousel, notification list, social/proof widgets, radial moments | много демо-like паттернов, нужны жесткие причины |
| `components/headless` | 6 | accessible accordion, dialog, popover, switch, tabs | нужен `@headlessui/react` и аккуратная стилизация |
| `components/radix` | 18 | shadcn/Radix-style accordion, dialog, dropdown, sheet, sidebar, tabs | `radix-ui` bundle и дублирование shadcn |
| `primitives/animate` | 11 | motion shell: tabs, tooltip, scroll progress, motion grid | требуют ручной сборки и QA |
| `primitives/base` | 17 | Base UI primitives for custom components | extra dependency, больше интеграционной работы |
| `primitives/buttons` | 4 | custom CTA behavior | motion должен поддерживать действие, не заменять смысл |
| `primitives/effects` | 14 | reveal, fade, slide, zoom, tilt, magnetic, shine, highlight, particles | эффект ради эффекта портит presentation quality |
| `primitives/headless` | 6 | headless semantics with custom surface | больше ручной ответственности за design states |
| `primitives/radix` | 18 | Radix semantics with custom animation | следить за overlap with existing shadcn |
| `primitives/texts` | 11 | hero words, metrics, proof numbers, short labels | не анимировать длинные абзацы |
| `hooks` | 5 | auto height, controlled state, in-view, motion-value state | ставить только как dependency chain |
| `lib` | 1 | strict context helper | ставить только как dependency chain |
| `icons` | 260 | animated Lucide icons | ставить только exact icon |

## Как выбирать

1. Начать с задачи секции: clarity, proof, comparison, navigation, pricing, FAQ, demo, CTA.
2. Проверить, есть ли уже shadcn/ui или локальный компонент.
3. Если нужен animated primitive, смотреть `docs/research/animate-ui-catalog.md`.
4. Выбрать самый маленький registry item.
5. Заполнить `projects/<slug>/14-animate-ui-selection.md`.
6. В `08-component-and-asset-plan.md` записать dependencies, registry dependencies and reduced-motion fallback.
7. Не ставить item, если motion purpose нельзя объяснить одной строкой.

## Секция к компоненту

| Landing need | Good candidates | Notes |
| --- | --- | --- |
| Hero entrance | `primitives-effects-fade`, `primitives-effects-slide`, `primitives-texts-splitting`, `primitives-texts-gradient` | Одна крупная entrance-система, не набор всех эффектов |
| Hero ambient background | `components-backgrounds-gradient`, `components-backgrounds-stars`, `components-backgrounds-hexagon`, `components-backgrounds-bubble` | Слой должен быть тише текста и CTA |
| CTA polish | `components-buttons-button`, `components-buttons-ripple`, `components-buttons-liquid`, `primitives-effects-magnetic` | Magnetic/liquid только для primary CTA или special hero action |
| FAQ | `components-headless-accordion`, `components-radix-accordion`, `primitives-effects-auto-height` | Headless если важна семантика, Radix если проект уже Radix/shadcn-heavy |
| Feature tabs | `components-animate-tabs`, `components-headless-tabs`, `components-radix-tabs` | Tabs должны менять meaning/content, не быть декором |
| Pricing toggle | `components-headless-switch`, `components-radix-switch`, `components-radix-toggle-group`, `primitives-texts-sliding-number` | Анимировать цену можно, скрывать условия нельзя |
| Metrics and proof | `primitives-texts-counting-number`, `primitives-texts-sliding-number`, `components-animate-avatar-group` | Только реальные числа и реальные claims |
| Product code/API landing | `components-animate-code`, `components-animate-code-tabs`, `components-buttons-copy` | Проверить `shiki`, `next-themes`, copy behavior |
| Social/activity proof | `components-community-notification-list`, `components-community-user-presence-avatar`, `components-animate-tooltip` | Не имитировать fake activity |
| Visual gallery | `components-community-motion-carousel`, `primitives-effects-image-zoom` | Проверить mobile swipe, keyboard, reduced motion |
| App-like drawer/sheet | `components-radix-sheet`, `components-headless-dialog`, `components-radix-dialog` | Не добавлять modal, если CTA может вести прямо |
| Navigation detail | `components-radix-dropdown-menu`, `components-base-menu`, `components-radix-sidebar` | Sidebar почти всегда для app, не для простого landing |
| One-off delight | `primitives-effects-shine`, `primitives-effects-highlight`, `primitives-effects-click` | Должен быть на важном элементе, а не по всей странице |

## Что не брать по умолчанию

- `components-animate-cursor`: custom cursor почти всегда мешает доступности и привычному UX.
- `components-backgrounds-fireworks`: подходит только для celebratory/product moment, не как общий фон.
- `components-backgrounds-gravity-stars` и `components-backgrounds-hole`: эффектные, но могут перетянуть внимание с offer.
- `components-community-radial-menu`, `components-community-radial-nav`, `components-community-radial-intro`: брать только если radial motion связан с продуктом.
- `components-animate-github-stars-wheel` и `components-buttons-github-stars`: только для open-source/devtool страниц.
- `components-radix-sidebar`: почти всегда app shell, не landing hero.
- `components-base-files` и `components-radix-files`: только если продукт реально про files/docs/tree.
- Any `icons-*`: ставить только конкретную иконку, не пакет.

## Семейства: что выбрать

- `components/*`: брать, когда нужен готовый styled component.
- `primitives/*`: брать, когда нужен motion/behavior, но визуальная оболочка должна быть своя.
- `headless`: брать, когда важна семантика Headless UI и проект готов добавить `@headlessui/react`.
- `radix`: брать, когда проект уже shadcn/Radix-oriented and dependency cost accepted.
- `base`: брать только если Base UI direction реально подходит. Учитывать, что registry использует `@base-ui-components/react`, а этот проект сейчас имеет `@base-ui/react`.
- `effects`: лучшее место для small polish, если есть reduced-motion fallback.
- `texts`: только для коротких hero words, metrics, labels. Не использовать на больших paragraph blocks.
- `backgrounds`: максимум один branded ambient layer per viewport.

## Install protocol

```bash
npx shadcn@latest add @animate-ui/<registry-name>
```

Перед install:

- проверить `package.json`;
- записать source URL and registry name;
- выписать runtime dependencies;
- проверить duplicate with shadcn/local component;
- определить motion purpose;
- определить reduced-motion fallback;
- снять desktop/mobile screenshots после внедрения.

## Minimum QA

- CTA не перекрыт эффектами.
- Motion не начинается до того, как текст readable.
- Hover/tap states не двигают layout.
- Mobile не теряет content из-за absolute layers.
- `prefers-reduced-motion` не оставляет пустые states.
- Background не ухудшает contrast.
- Component source записан в evidence/decision log.
