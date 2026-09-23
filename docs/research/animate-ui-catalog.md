# Animate UI Catalog

Generated from https://animate-ui.com and https://github.com/imskyleen/animate-ui.

Animate UI is a copy-first shadcn registry distribution of React components built with Tailwind CSS and Motion. It is not a normal npm UI library. Install individual pieces with `npx shadcn@latest add @animate-ui/<registry-name>`.

License note: MIT + Commons Clause. Use/adapt inside an application, website, or product; do not redistribute/sell the components themselves as a standalone library or bundle.

Inventory: 580 registry entries total: 1 style index, 159 demo entries, 260 animated icon entries, 73 component entries, 81 primitive entries, 5 hook entries, and 1 lib entry. The normal visual selection pool is 154 component/primitive entries. Hooks and lib entries are service dependencies, not design choices. Icons are intentionally excluded from the detailed tables because there are many animated Lucide variants and they should be installed by specific icon name.

Latest source check: `https://animate-ui.com/r/registry.json` and `https://github.com/imskyleen/animate-ui` on 2026-07-03.

Live docs coverage: `https://animate-ui.com/sitemap.xml` returns 404, so the live site map was built from `/`, `/docs`, `/docs/components`, `/docs/primitives`, `/docs/icons`, `.mdx` endpoints, and registry endpoints. Current full-site crawl found 361 internal paths, 172 live HTML pages, 171 live docs pages, 171 live docs `.mdx` endpoints, 580 registry item endpoints with 200 status, 75 component docs links, 82 primitive docs links, 6 icon docs links, and 8 guide/reference pages.

Fresh full-site recheck on 2026-07-03 03:16 MSK used a stricter non-asset crawler and confirmed the same useful surface: 172 live HTML pages, 171 docs HTML pages, 171 docs `.mdx` endpoints, 75 component docs links, 82 primitive docs links, 6 icon docs links, 8 guide/reference pages, and 580 registry items. Three icon endpoints that timed out during the concurrent pass (`icons-sun-dim`, `icons-thumbs-up`, `icons-x`) returned 200 on direct retry.

Whole-site audit on 2026-07-03 03:47 MSK re-crawled `/`, discovered internal non-asset paths, docs HTML, docs `.mdx`, `registry.json`, and all 580 item endpoints. Result: `sitemap.xml` still returns 404; 172 live HTML pages, 171 docs HTML pages, 171 docs `.mdx` endpoints, 73 installable component docs, 81 installable primitive docs, 6 icon docs, 8 guide/reference pages, 580/580 registry item endpoints OK, and no new useful non-docs app pages. Root shortcuts such as `/installation`, `/accessibility`, `/mcp`, `/roadmap`, and `/other-animated-distributions` return 404; use the `/docs/*` versions.

User-requested whole-site rewalk on 2026-07-03 05:22 MSK re-crawled the live internal surface from `/`, `/docs`, `/docs/components`, `/docs/primitives`, and `/docs/icons`, then checked every docs `.mdx` endpoint, `registry.json`, and all registry item endpoints. Result stayed stable: `sitemap.xml` returns 404; 186 internal non-asset paths discovered by the stricter crawler; 172 live HTML pages; 171 live docs pages; 171 live docs `.mdx` endpoints; 75 component docs links including indexes; 82 primitive docs links including index; 6 icon docs; 8 guide/reference pages; 580 registry items; and 580/580 `/r/<item>.json` endpoints OK. The only useful live non-docs HTML page remains `/`.

Whole-site rewalk on 2026-07-03 05:49 MSK again confirmed the same useful surface: `sitemap.xml` returns 404; 186 internal non-asset paths discovered; 172 live HTML pages; 171 docs `.mdx` endpoints with 200; 8 generated docs paths with 404; `registry.json` returns 200 with 580 items; all 580 `/r/<item>.json` endpoints return 200. The registry groups are still 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, and 1 style index.

User-requested full-site crawl on 2026-07-03 06:21 MSK rechecked root, docs branches, service map paths, docs `.mdx`, `registry.json`, and every registry item endpoint. Result: `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/docs/llms.txt`, `/.well-known/llms.txt`, `/docs.json`, and `/openapi.json` all return 404; 181 internal non-asset paths were probed; 172 HTML pages return 200; 9 generated internal paths return 404; 171 docs `.mdx` endpoints return 200; `registry.json` returns 580 items; and all 580 `/r/<item>.json` endpoints return 200. The only useful non-docs HTML page remains `/`.

User-requested full-site rewalk on 2026-07-03 10:48 MSK checked the full known surface again. Live `HEAD` checks on `animate-ui.com` returned 200 for `/`, all 171 docs pages, all 171 docs `.mdx` endpoints, and all 580 `/r/<item>.json` endpoints. `/r/registry.json` returns 200 on `HEAD`, but full `GET` from the live domain stalled twice after partial 20-24 KB downloads, so the registry body was revalidated through GitHub raw `apps/www/public/r/registry.json` at 417344 bytes and 580 items. Treat this as a current transport caveat: use GitHub raw for catalog rebuilding if the live registry body stalls, then still verify chosen live `/r/<item>.json` endpoints before install.

User-requested full-site rewalk on 2026-07-03 11:40 MSK checked the known surface again with GitHub raw registry plus live `HEAD` and calm endpoint retries. GitHub raw `apps/www/public/r/registry.json` fetched fully at 417344 bytes with 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` returned `ECONNRESET`. The expected HTML surface (`/` plus 171 docs pages) returned 200 after retrying `/docs/changelog`; all 171 docs `.mdx` endpoints returned 200; all 580 live `/r/<item>.json` endpoints returned 200 after calm retry. Service maps remain 404 and counts are unchanged.

User-requested whole-site rewalk on 2026-07-03 12:20 MSK checked service maps, live seed pages, the official GitHub tree, GitHub raw registry, all docs routes, docs `.mdx` endpoints, and every live item endpoint. Service maps still return 404. The GitHub tree has 171 unique docs routes: 8 guide pages, 75 component docs including indexes, 82 primitive docs including index, and 6 icon docs. Live `HEAD` returned 200 for all 171 docs routes after retrying `/docs/primitives/base/progress`; all 171 docs `.mdx` endpoints returned 200. GitHub raw registry fetched fully at 417344 bytes with 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` timed out after a partial 20895 byte download. All 580 live `/r/<item>.json` endpoints returned 200. Use GitHub tree and raw registry for full inventory, then verify exact live item endpoints before install.

Fresh user-requested whole-site rewalk on 2026-07-03 12:59 MSK checked service maps, live seed pages, the official GitHub tree, GitHub raw registry, all docs routes, docs `.mdx` endpoints, and every live item endpoint. The useful surface stayed stable: service maps return 404; seed pages return 200; GitHub tree has 171 docs routes; 171/171 live docs routes return 200; 171/171 docs `.mdx` endpoints return 200; GitHub raw registry fetched fully at 417344 bytes with 580 items; live `HEAD /r/registry.json` returns 200 while live `GET /r/registry.json` hit a bounded `AbortError`; all 580 live `/r/<item>.json` endpoints return 200. Use GitHub tree and raw registry for full inventory, then verify exact live item endpoint before install.

User-requested whole-site rewalk on 2026-07-03 13:43 MSK checked the complete useful surface again: 7 service-map guesses, 5 seed pages, official GitHub tree, all 171 docs routes, all 171 docs `.mdx` endpoints, raw registry, live registry `HEAD`, bounded live registry `GET`, and every live item endpoint. Service maps still return 404; seed pages return 200; GitHub tree still has 171 docs routes; 171/171 docs HTML routes return 200; 171/171 docs `.mdx` endpoints return 200; raw registry returns 580 items; live `HEAD /r/registry.json` returns 200 while live `GET /r/registry.json` aborts under a bounded timeout; 580/580 live `/r/<item>.json` endpoints return 200. Counts are unchanged: 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, and 1 style index.

Count caveat: the 75 component docs links include `/docs/components` and `/docs/components/community`; the registry contains 73 installable component entries. The 82 primitive docs links include `/docs/primitives`; the registry contains 81 installable primitive entries.

Bad generated links observed during crawl: `/docs/primitives/base/menuarrow`, `/docs/primitives/base/menucheckboxitem`, `/docs/primitives/base/menuitem`, `/docs/primitives/base/menuradiogroup`, `/docs/primitives/base/menuradioitem`, `/docs/primitives/base/menushortcut`, `/docs/primitives/base/menusubmenu`, `/docs/primitives/base/menusubmenutrigger`, and `/react/primitives/animate/tooltip`. Do not cite or install from these paths.

For landing-page planning, also read:

```text
план разработки топового лендинга/17-animate-ui-full-site-map.md
```

That file maps the full Animate UI site to landing sections, component risks, and selection rules.

## Category Counts

| Category | Count |
| --- | ---: |
| components/animate | 7 |
| components/backgrounds | 7 |
| components/base | 16 |
| components/buttons | 8 |
| components/community | 11 |
| components/headless | 6 |
| components/radix | 18 |
| hooks/use-auto-height | 1 |
| hooks/use-controlled-state | 1 |
| hooks/use-data-state | 1 |
| hooks/use-is-in-view | 1 |
| hooks/use-motion-value-state | 1 |
| lib/get-strict-context | 1 |
| primitives/animate | 11 |
| primitives/base | 17 |
| primitives/buttons | 4 |
| primitives/effects | 14 |
| primitives/headless | 6 |
| primitives/radix | 18 |
| primitives/texts | 11 |

## Top Shared Dependencies

The table below is for the normal non-demo selection surface. The full 580-entry registry includes demos and animated icons; in that full surface `motion` appears in 366 entries and `@animate-ui/icons-icon` appears as a registry dependency in 259 icon entries. Do not use those full-registry counts to justify installing broad icon or demo groups.

| Count | Dependency |
| ---: | --- |
| 103 | `motion` |
| 57 | `@animate-ui/lib-get-strict-context` |
| 32 | `@animate-ui/hooks-use-controlled-state` |
| 24 | `lucide-react` |
| 21 | `@animate-ui/primitives-animate-slot` |
| 18 | `radix-ui` |
| 18 | `@animate-ui/hooks-use-is-in-view` |
| 17 | `@base-ui-components/react` |
| 15 | `class-variance-authority` |
| 10 | `@animate-ui/primitives-effects-highlight` |
| 6 | `@headlessui/react` |
| 5 | `@animate-ui/components-buttons-button` |
| 4 | `@animate-ui/primitives-buttons-button` |
| 3 | `@animate-ui/primitives-effects-particles` |
| 3 | `@animate-ui/primitives-base-preview-card` |
| 3 | `@animate-ui/primitives-radix-checkbox` |
| 3 | `@animate-ui/primitives-effects-auto-height` |
| 2 | `next-themes` |
| 2 | `@animate-ui/components-buttons-copy` |
| 2 | `shiki` |
| 2 | `@animate-ui/primitives-animate-tabs` |
| 2 | `@animate-ui/primitives-animate-tooltip` |
| 2 | `@animate-ui/primitives-base-accordion` |
| 2 | `@animate-ui/primitives-texts-sliding-number` |
| 2 | `@animate-ui/primitives-radix-accordion` |

## Recommended Picks For This Project

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-animate-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-animate-tabs` | - | `@animate-ui/primitives-animate-tabs` |
| `components-animate-tooltip` | Tooltip | `npx shadcn@latest add @animate-ui/components-animate-tooltip` | `motion` | `@animate-ui/primitives-animate-tooltip` |
| `components-animate-code-tabs` | Code Tabs | `npx shadcn@latest add @animate-ui/components-animate-code-tabs` | `shiki` | `@animate-ui/primitives-animate-tabs`, `@animate-ui/components-buttons-copy` |
| `components-animate-cursor` | Cursor | `npx shadcn@latest add @animate-ui/components-animate-cursor` | - | `@animate-ui/primitives-animate-cursor` |
| `components-animate-avatar-group` | Avatar Group | `npx shadcn@latest add @animate-ui/components-animate-avatar-group` | `motion` | `@animate-ui/primitives-animate-avatar-group` |
| `components-backgrounds-gradient` | Gradient Background | `npx shadcn@latest add @animate-ui/components-backgrounds-gradient` | `motion` | - |
| `components-backgrounds-stars` | Stars Background | `npx shadcn@latest add @animate-ui/components-backgrounds-stars` | `motion` | - |
| `components-backgrounds-gravity-stars` | Gravity Stars Background | `npx shadcn@latest add @animate-ui/components-backgrounds-gravity-stars` | `motion` | - |
| `components-backgrounds-hole` | Hole Background | `npx shadcn@latest add @animate-ui/components-backgrounds-hole` | `motion` | - |
| `components-backgrounds-bubble` | Bubble Background | `npx shadcn@latest add @animate-ui/components-backgrounds-bubble` | `motion` | - |
| `components-buttons-button` | Button | `npx shadcn@latest add @animate-ui/components-buttons-button` | `class-variance-authority` | `@animate-ui/primitives-buttons-button` |
| `components-buttons-copy` | Copy Button | `npx shadcn@latest add @animate-ui/components-buttons-copy` | `motion`, `lucide-react`, `class-variance-authority` | `@animate-ui/primitives-buttons-button`, `@animate-ui/hooks-use-controlled-state` |
| `components-buttons-flip` | Flip Button | `npx shadcn@latest add @animate-ui/components-buttons-flip` | `class-variance-authority` | `@animate-ui/components-buttons-button`, `@animate-ui/primitives-buttons-flip` |
| `components-buttons-liquid` | Liquid Button | `npx shadcn@latest add @animate-ui/components-buttons-liquid` | `class-variance-authority` | `@animate-ui/primitives-buttons-liquid` |
| `components-buttons-ripple` | Ripple Button | `npx shadcn@latest add @animate-ui/components-buttons-ripple` | `class-variance-authority` | `@animate-ui/components-buttons-button`, `@animate-ui/primitives-buttons-ripple` |
| `components-buttons-theme-toggler` | Theme Toggler Button | `npx shadcn@latest add @animate-ui/components-buttons-theme-toggler` | `next-themes`, `class-variance-authority`, `lucide-react` | `@animate-ui/primitives-effects-theme-toggler`, `@animate-ui/components-buttons-icon` |
| `components-community-motion-carousel` | Motion Carousel | `npx shadcn@latest add @animate-ui/components-community-motion-carousel` | `motion`, `lucide-react`, `embla-carousel`, `embla-carousel-react` | `@animate-ui/components-buttons-button` |
| `components-community-notification-list` | Notification List | `npx shadcn@latest add @animate-ui/components-community-notification-list` | `motion`, `lucide-react` | - |
| `components-community-pin-list` | Pin List | `npx shadcn@latest add @animate-ui/components-community-pin-list` | `motion`, `lucide-react` | - |
| `components-community-radial-menu` | Radial Menu | `npx shadcn@latest add @animate-ui/components-community-radial-menu` | `motion`, `lucide-react`, `@base-ui-components/react` | - |
| `components-community-share-button` | Share Button | `npx shadcn@latest add @animate-ui/components-community-share-button` | `motion`, `lucide-react`, `class-variance-authority` | - |
| `components-community-user-presence-avatar` | User Presence Avatar | `npx shadcn@latest add @animate-ui/components-community-user-presence-avatar` | `motion` | `@animate-ui/components-animate-tooltip` |
| `components-headless-accordion` | Accordion | `npx shadcn@latest add @animate-ui/components-headless-accordion` | `lucide-react` | `@animate-ui/primitives-headless-disclosure` |
| `components-headless-dialog` | Dialog | `npx shadcn@latest add @animate-ui/components-headless-dialog` | `lucide-react`, `motion` | `@animate-ui/primitives-headless-dialog` |
| `components-headless-popover` | Popover | `npx shadcn@latest add @animate-ui/components-headless-popover` | - | `@animate-ui/primitives-headless-popover` |
| `components-headless-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-headless-tabs` | `motion` | `@animate-ui/primitives-headless-tabs` |
| `primitives-effects-auto-height` | Auto Height | `npx shadcn@latest add @animate-ui/primitives-effects-auto-height` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-auto-height` |
| `primitives-effects-blur` | Blur | `npx shadcn@latest add @animate-ui/primitives-effects-blur` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-fade` | Fade | `npx shadcn@latest add @animate-ui/primitives-effects-fade` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-slide` | Slide | `npx shadcn@latest add @animate-ui/primitives-effects-slide` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-zoom` | Zoom | `npx shadcn@latest add @animate-ui/primitives-effects-zoom` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-tilt` | Tilt | `npx shadcn@latest add @animate-ui/primitives-effects-tilt` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-effects-magnetic` | Magnetic | `npx shadcn@latest add @animate-ui/primitives-effects-magnetic` | `motion` | `@animate-ui/primitives-animate-slot` |
| `primitives-effects-image-zoom` | Image Zoom | `npx shadcn@latest add @animate-ui/primitives-effects-image-zoom` | `motion` | - |
| `primitives-effects-particles` | Particles | `npx shadcn@latest add @animate-ui/primitives-effects-particles` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-effects-shine` | Shine | `npx shadcn@latest add @animate-ui/primitives-effects-shine` | `motion` | - |
| `primitives-effects-highlight` | Highlight | `npx shadcn@latest add @animate-ui/primitives-effects-highlight` | `motion` | - |
| `primitives-texts-splitting` | Splitting Text | `npx shadcn@latest add @animate-ui/primitives-texts-splitting` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-typing` | Typing Text | `npx shadcn@latest add @animate-ui/primitives-texts-typing` | `motion` | `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-texts-rotating` | Rotating Text | `npx shadcn@latest add @animate-ui/primitives-texts-rotating` | `motion` | `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-texts-morphing` | Morphing Text | `npx shadcn@latest add @animate-ui/primitives-texts-morphing` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-gradient` | Gradient Text | `npx shadcn@latest add @animate-ui/primitives-texts-gradient` | `motion` | - |
| `primitives-texts-shimmering` | Shimmering Text | `npx shadcn@latest add @animate-ui/primitives-texts-shimmering` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-sliding-number` | Sliding Number | `npx shadcn@latest add @animate-ui/primitives-texts-sliding-number` | `motion`, `react-use-measure` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-counting-number` | Counting Number | `npx shadcn@latest add @animate-ui/primitives-texts-counting-number` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-animate-scroll-progress` | Scroll Progress | `npx shadcn@latest add @animate-ui/primitives-animate-scroll-progress` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-motion-value-state` |
| `primitives-animate-motion-grid` | Motion Grid | `npx shadcn@latest add @animate-ui/primitives-animate-motion-grid` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-animate-pinned-list` | Pin List | `npx shadcn@latest add @animate-ui/primitives-animate-pinned-list` | `motion` | `@animate-ui/primitives-animate-slot` |
| `primitives-animate-spring` | Spring | `npx shadcn@latest add @animate-ui/primitives-animate-spring` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-motion-value-state` |
| `primitives-animate-slot` | Animate Slot | `npx shadcn@latest add @animate-ui/primitives-animate-slot` | `motion` | - |

## Full Non-Demo Non-Icon Catalog

### components/animate

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-animate-avatar-group` | Avatar Group | `npx shadcn@latest add @animate-ui/components-animate-avatar-group` | `motion` | `@animate-ui/primitives-animate-avatar-group` |
| `components-animate-code` | Code | `npx shadcn@latest add @animate-ui/components-animate-code` | `next-themes` | `@animate-ui/primitives-animate-code-block`, `@animate-ui/components-buttons-copy`, `@animate-ui/lib-get-strict-context` |
| `components-animate-code-tabs` | Code Tabs | `npx shadcn@latest add @animate-ui/components-animate-code-tabs` | `shiki` | `@animate-ui/primitives-animate-tabs`, `@animate-ui/components-buttons-copy` |
| `components-animate-cursor` | Cursor | `npx shadcn@latest add @animate-ui/components-animate-cursor` | - | `@animate-ui/primitives-animate-cursor` |
| `components-animate-github-stars-wheel` | GitHub Stars Wheel | `npx shadcn@latest add @animate-ui/components-animate-github-stars-wheel` | `motion` | `@animate-ui/primitives-effects-particles`, `@animate-ui/primitives-texts-scrolling-number` |
| `components-animate-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-animate-tabs` | - | `@animate-ui/primitives-animate-tabs` |
| `components-animate-tooltip` | Tooltip | `npx shadcn@latest add @animate-ui/components-animate-tooltip` | `motion` | `@animate-ui/primitives-animate-tooltip` |

### components/backgrounds

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-backgrounds-bubble` | Bubble Background | `npx shadcn@latest add @animate-ui/components-backgrounds-bubble` | `motion` | - |
| `components-backgrounds-fireworks` | Fireworks Background | `npx shadcn@latest add @animate-ui/components-backgrounds-fireworks` | - | - |
| `components-backgrounds-gradient` | Gradient Background | `npx shadcn@latest add @animate-ui/components-backgrounds-gradient` | `motion` | - |
| `components-backgrounds-gravity-stars` | Gravity Stars Background | `npx shadcn@latest add @animate-ui/components-backgrounds-gravity-stars` | `motion` | - |
| `components-backgrounds-hexagon` | Hexagon Background | `npx shadcn@latest add @animate-ui/components-backgrounds-hexagon` | - | - |
| `components-backgrounds-hole` | Hole Background | `npx shadcn@latest add @animate-ui/components-backgrounds-hole` | `motion` | - |
| `components-backgrounds-stars` | Stars Background | `npx shadcn@latest add @animate-ui/components-backgrounds-stars` | `motion` | - |

### components/base

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-base-accordion` | Accordion | `npx shadcn@latest add @animate-ui/components-base-accordion` | `lucide-react` | `@animate-ui/primitives-base-accordion` |
| `components-base-alert-dialog` | Alert Dialog | `npx shadcn@latest add @animate-ui/components-base-alert-dialog` | - | `@animate-ui/primitives-base-alert-dialog`, `@animate-ui/components-buttons-button` |
| `components-base-checkbox` | Checkbox | `npx shadcn@latest add @animate-ui/components-base-checkbox` | `class-variance-authority` | `@animate-ui/primitives-base-checkbox` |
| `components-base-dialog` | Dialog | `npx shadcn@latest add @animate-ui/components-base-dialog` | `lucide-react` | `@animate-ui/primitives-base-dialog` |
| `components-base-files` | Files | `npx shadcn@latest add @animate-ui/components-base-files` | `lucide-react` | `@animate-ui/primitives-base-files` |
| `components-base-menu` | Menu | `npx shadcn@latest add @animate-ui/components-base-menu` | - | `@animate-ui/primitives-base-menu` |
| `components-base-popover` | Popover | `npx shadcn@latest add @animate-ui/components-base-popover` | - | `@animate-ui/primitives-base-popover` |
| `components-base-preview-card` | Preview Card | `npx shadcn@latest add @animate-ui/components-base-preview-card` | - | `@animate-ui/primitives-base-preview-card` |
| `components-base-preview-link-card` | Preview Link Card | `npx shadcn@latest add @animate-ui/components-base-preview-link-card` | - | `@animate-ui/primitives-base-preview-card` |
| `components-base-progress` | Progress | `npx shadcn@latest add @animate-ui/components-base-progress` | - | `@animate-ui/primitives-base-progress` |
| `components-base-radio` | Base Radio | `npx shadcn@latest add @animate-ui/components-base-radio` | `lucide-react` | `@animate-ui/primitives-base-radio` |
| `components-base-switch` | Switch | `npx shadcn@latest add @animate-ui/components-base-switch` | - | `@animate-ui/primitives-base-switch` |
| `components-base-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-base-tabs` | - | `@animate-ui/primitives-base-tabs` |
| `components-base-toggle` | Toggle | `npx shadcn@latest add @animate-ui/components-base-toggle` | - | `@animate-ui/primitives-base-toggle` |
| `components-base-toggle-group` | Toggle Group | `npx shadcn@latest add @animate-ui/components-base-toggle-group` | - | `@animate-ui/primitives-base-toggle-group` |
| `components-base-tooltip` | Tooltip | `npx shadcn@latest add @animate-ui/components-base-tooltip` | - | `@animate-ui/primitives-base-tooltip` |

### components/buttons

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-buttons-button` | Button | `npx shadcn@latest add @animate-ui/components-buttons-button` | `class-variance-authority` | `@animate-ui/primitives-buttons-button` |
| `components-buttons-copy` | Copy Button | `npx shadcn@latest add @animate-ui/components-buttons-copy` | `motion`, `lucide-react`, `class-variance-authority` | `@animate-ui/primitives-buttons-button`, `@animate-ui/hooks-use-controlled-state` |
| `components-buttons-flip` | Flip Button | `npx shadcn@latest add @animate-ui/components-buttons-flip` | `class-variance-authority` | `@animate-ui/components-buttons-button`, `@animate-ui/primitives-buttons-flip` |
| `components-buttons-github-stars` | GitHub Stars Button | `npx shadcn@latest add @animate-ui/components-buttons-github-stars` | `lucide-react` | `@animate-ui/primitives-buttons-button`, `@animate-ui/primitives-animate-github-stars` |
| `components-buttons-icon` | Icon Button | `npx shadcn@latest add @animate-ui/components-buttons-icon` | `class-variance-authority` | `@animate-ui/primitives-buttons-button`, `@animate-ui/primitives-effects-particles` |
| `components-buttons-liquid` | Liquid Button | `npx shadcn@latest add @animate-ui/components-buttons-liquid` | `class-variance-authority` | `@animate-ui/primitives-buttons-liquid` |
| `components-buttons-ripple` | Ripple Button | `npx shadcn@latest add @animate-ui/components-buttons-ripple` | `class-variance-authority` | `@animate-ui/components-buttons-button`, `@animate-ui/primitives-buttons-ripple` |
| `components-buttons-theme-toggler` | Theme Toggler Button | `npx shadcn@latest add @animate-ui/components-buttons-theme-toggler` | `next-themes`, `class-variance-authority`, `lucide-react` | `@animate-ui/primitives-effects-theme-toggler`, `@animate-ui/components-buttons-icon` |

### components/community

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-community-flip-card` | Flip Card | `npx shadcn@latest add @animate-ui/components-community-flip-card` | `motion`, `class-variance-authority`, `lucide-react` | - |
| `components-community-management-bar` | Management Bar | `npx shadcn@latest add @animate-ui/components-community-management-bar` | `motion`, `lucide-react` | `@animate-ui/primitives-texts-sliding-number` |
| `components-community-motion-carousel` | Motion Carousel | `npx shadcn@latest add @animate-ui/components-community-motion-carousel` | `motion`, `lucide-react`, `embla-carousel`, `embla-carousel-react` | `@animate-ui/components-buttons-button` |
| `components-community-notification-list` | Notification List | `npx shadcn@latest add @animate-ui/components-community-notification-list` | `motion`, `lucide-react` | - |
| `components-community-pin-list` | Pin List | `npx shadcn@latest add @animate-ui/components-community-pin-list` | `motion`, `lucide-react` | - |
| `components-community-playful-todolist` | Playful Todolist | `npx shadcn@latest add @animate-ui/components-community-playful-todolist` | `motion` | `@animate-ui/primitives-radix-checkbox` |
| `components-community-radial-intro` | Radial Intro | `npx shadcn@latest add @animate-ui/components-community-radial-intro` | `motion` | - |
| `components-community-radial-menu` | Radial Menu | `npx shadcn@latest add @animate-ui/components-community-radial-menu` | `motion`, `lucide-react`, `@base-ui-components/react` | - |
| `components-community-radial-nav` | Radial Nav | `npx shadcn@latest add @animate-ui/components-community-radial-nav` | `motion`, `lucide-react` | - |
| `components-community-share-button` | Share Button | `npx shadcn@latest add @animate-ui/components-community-share-button` | `motion`, `lucide-react`, `class-variance-authority` | - |
| `components-community-user-presence-avatar` | User Presence Avatar | `npx shadcn@latest add @animate-ui/components-community-user-presence-avatar` | `motion` | `@animate-ui/components-animate-tooltip` |

### components/headless

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-headless-accordion` | Accordion | `npx shadcn@latest add @animate-ui/components-headless-accordion` | `lucide-react` | `@animate-ui/primitives-headless-disclosure` |
| `components-headless-checkbox` | Checkbox | `npx shadcn@latest add @animate-ui/components-headless-checkbox` | `class-variance-authority`, `motion` | `@animate-ui/primitives-headless-checkbox` |
| `components-headless-dialog` | Dialog | `npx shadcn@latest add @animate-ui/components-headless-dialog` | `lucide-react`, `motion` | `@animate-ui/primitives-headless-dialog` |
| `components-headless-popover` | Popover | `npx shadcn@latest add @animate-ui/components-headless-popover` | - | `@animate-ui/primitives-headless-popover` |
| `components-headless-switch` | Switch | `npx shadcn@latest add @animate-ui/components-headless-switch` | - | `@animate-ui/primitives-headless-switch` |
| `components-headless-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-headless-tabs` | `motion` | `@animate-ui/primitives-headless-tabs` |

### components/radix

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `components-radix-accordion` | Accordion | `npx shadcn@latest add @animate-ui/components-radix-accordion` | `lucide-react` | `@animate-ui/primitives-radix-accordion` |
| `components-radix-alert-dialog` | Alert Dialog | `npx shadcn@latest add @animate-ui/components-radix-alert-dialog` | - | `@animate-ui/primitives-radix-alert-dialog`, `@animate-ui/components-buttons-button` |
| `components-radix-checkbox` | Checkbox | `npx shadcn@latest add @animate-ui/components-radix-checkbox` | `class-variance-authority` | `@animate-ui/primitives-radix-checkbox` |
| `components-radix-dialog` | Dialog | `npx shadcn@latest add @animate-ui/components-radix-dialog` | `lucide-react` | `@animate-ui/primitives-radix-dialog` |
| `components-radix-dropdown-menu` | Dropdown Menu | `npx shadcn@latest add @animate-ui/components-radix-dropdown-menu` | `lucide-react` | `@animate-ui/primitives-radix-dropdown-menu` |
| `components-radix-files` | Files | `npx shadcn@latest add @animate-ui/components-radix-files` | `lucide-react` | `@animate-ui/primitives-radix-files` |
| `components-radix-hover-card` | Hover Card | `npx shadcn@latest add @animate-ui/components-radix-hover-card` | - | `@animate-ui/primitives-radix-hover-card` |
| `components-radix-popover` | Popover | `npx shadcn@latest add @animate-ui/components-radix-popover` | - | `@animate-ui/primitives-radix-popover` |
| `components-radix-preview-link-card` | Preview Link Card | `npx shadcn@latest add @animate-ui/components-radix-preview-link-card` | - | `@animate-ui/primitives-radix-preview-link-card` |
| `components-radix-progress` | Progress | `npx shadcn@latest add @animate-ui/components-radix-progress` | - | `@animate-ui/primitives-radix-progress` |
| `components-radix-radio-group` | Radio Group | `npx shadcn@latest add @animate-ui/components-radix-radio-group` | `lucide-react` | `@animate-ui/primitives-radix-radio-group` |
| `components-radix-sheet` | Sheet | `npx shadcn@latest add @animate-ui/components-radix-sheet` | `lucide-react` | `@animate-ui/primitives-radix-sheet` |
| `components-radix-sidebar` | Sidebar | `npx shadcn@latest add @animate-ui/components-radix-sidebar` | `radix-ui`, `class-variance-authority`, `motion`, `lucide-react` | `@animate-ui/primitives-radix-checkbox`, `@animate-ui/lib-get-strict-context`, `button`, `input`, `separator`, `skeleton`, `use-mobile` |
| `components-radix-switch` | Switch | `npx shadcn@latest add @animate-ui/components-radix-switch` | - | `@animate-ui/primitives-radix-switch` |
| `components-radix-tabs` | Tabs | `npx shadcn@latest add @animate-ui/components-radix-tabs` | - | `@animate-ui/primitives-radix-tabs` |
| `components-radix-toggle` | Toggle | `npx shadcn@latest add @animate-ui/components-radix-toggle` | `class-variance-authority` | `@animate-ui/primitives-radix-toggle` |
| `components-radix-toggle-group` | Toggle Group | `npx shadcn@latest add @animate-ui/components-radix-toggle-group` | `class-variance-authority` | `@animate-ui/primitives-radix-toggle-group`, `@animate-ui/components-radix-toggle`, `@animate-ui/lib-get-strict-context` |
| `components-radix-tooltip` | Tooltip | `npx shadcn@latest add @animate-ui/components-radix-tooltip` | - | `@animate-ui/primitives-radix-tooltip` |

### hooks/use-auto-height

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `hooks-use-auto-height` | useAutoHeight | `npx shadcn@latest add @animate-ui/hooks-use-auto-height` | - | - |

### hooks/use-controlled-state

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `hooks-use-controlled-state` | useControlledState | `npx shadcn@latest add @animate-ui/hooks-use-controlled-state` | - | - |

### hooks/use-data-state

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `hooks-use-data-state` | useDataState | `npx shadcn@latest add @animate-ui/hooks-use-data-state` | - | - |

### hooks/use-is-in-view

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `hooks-use-is-in-view` | useIsInView | `npx shadcn@latest add @animate-ui/hooks-use-is-in-view` | `motion` | - |

### hooks/use-motion-value-state

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `hooks-use-motion-value-state` | useMotionValueState | `npx shadcn@latest add @animate-ui/hooks-use-motion-value-state` | - | - |

### lib/get-strict-context

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `lib-get-strict-context` | getStrictContext | `npx shadcn@latest add @animate-ui/lib-get-strict-context` | - | - |

### primitives/animate

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-animate-avatar-group` | Avatar Group | `npx shadcn@latest add @animate-ui/primitives-animate-avatar-group` | `motion` | `@animate-ui/primitives-animate-tooltip` |
| `primitives-animate-code-block` | Code Block | `npx shadcn@latest add @animate-ui/primitives-animate-code-block` | `shiki` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-animate-cursor` | Cursor | `npx shadcn@latest add @animate-ui/primitives-animate-cursor` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-animate-github-stars` | Github Stars | `npx shadcn@latest add @animate-ui/primitives-animate-github-stars` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/primitives-texts-sliding-number`, `@animate-ui/primitives-effects-particles`, `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-animate-motion-grid` | Motion Grid | `npx shadcn@latest add @animate-ui/primitives-animate-motion-grid` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-animate-pinned-list` | Pin List | `npx shadcn@latest add @animate-ui/primitives-animate-pinned-list` | `motion` | `@animate-ui/primitives-animate-slot` |
| `primitives-animate-scroll-progress` | Scroll Progress | `npx shadcn@latest add @animate-ui/primitives-animate-scroll-progress` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-motion-value-state` |
| `primitives-animate-slot` | Animate Slot | `npx shadcn@latest add @animate-ui/primitives-animate-slot` | `motion` | - |
| `primitives-animate-spring` | Spring | `npx shadcn@latest add @animate-ui/primitives-animate-spring` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-motion-value-state` |
| `primitives-animate-tabs` | Tabs | `npx shadcn@latest add @animate-ui/primitives-animate-tabs` | `motion` | `@animate-ui/primitives-effects-highlight`, `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-animate-tooltip` | Tooltip | `npx shadcn@latest add @animate-ui/primitives-animate-tooltip` | `motion`, `@floating-ui/react` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |

### primitives/base

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-base-accordion` | Base Accordion | `npx shadcn@latest add @animate-ui/primitives-base-accordion` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-alert-dialog` | Base Alert Dialog | `npx shadcn@latest add @animate-ui/primitives-base-alert-dialog` | `motion`, `@base-ui-components/react` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-base-checkbox` | Base Checkbox | `npx shadcn@latest add @animate-ui/primitives-base-checkbox` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-collapsible` | Base Collapsible | `npx shadcn@latest add @animate-ui/primitives-base-collapsible` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-dialog` | Base Dialog | `npx shadcn@latest add @animate-ui/primitives-base-dialog` | `motion`, `@base-ui-components/react` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-base-files` | Files | `npx shadcn@latest add @animate-ui/primitives-base-files` | `motion` | `@animate-ui/primitives-base-accordion`, `@animate-ui/primitives-effects-highlight`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-menu` | Base Menu | `npx shadcn@latest add @animate-ui/primitives-base-menu` | `motion`, `@base-ui-components/react` | `@animate-ui/primitives-effects-highlight`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state`, `@animate-ui/hooks-use-data-state` |
| `primitives-base-popover` | Base Popover | `npx shadcn@latest add @animate-ui/primitives-base-popover` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-preview-card` | Base Preview Card | `npx shadcn@latest add @animate-ui/primitives-base-preview-card` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-preview-link-card` | Base Preview Link Card | `npx shadcn@latest add @animate-ui/primitives-base-preview-link-card` | `motion`, `@base-ui-components/react` | `@animate-ui/primitives-base-preview-card`, `@animate-ui/lib-get-strict-context` |
| `primitives-base-progress` | Base Progress | `npx shadcn@latest add @animate-ui/primitives-base-progress` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/primitives-texts-counting-number` |
| `primitives-base-radio` | Base Radio | `npx shadcn@latest add @animate-ui/primitives-base-radio` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-switch` | Base Switch | `npx shadcn@latest add @animate-ui/primitives-base-switch` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-tabs` | Base Tabs | `npx shadcn@latest add @animate-ui/primitives-base-tabs` | `motion`, `@base-ui-components/react` | `@animate-ui/primitives-effects-auto-height`, `@animate-ui/primitives-effects-highlight`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-toggle` | Base Toggle | `npx shadcn@latest add @animate-ui/primitives-base-toggle` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-base-toggle-group` | Base Toggle Group | `npx shadcn@latest add @animate-ui/primitives-base-toggle-group` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state`, `@animate-ui/primitives-effects-highlight` |
| `primitives-base-tooltip` | Base Tooltip | `npx shadcn@latest add @animate-ui/primitives-base-tooltip` | `motion`, `@base-ui-components/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |

### primitives/buttons

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-buttons-button` | Button | `npx shadcn@latest add @animate-ui/primitives-buttons-button` | `motion` | `@animate-ui/primitives-animate-slot` |
| `primitives-buttons-flip` | Flip Button | `npx shadcn@latest add @animate-ui/primitives-buttons-flip` | `motion` | `@animate-ui/lib-get-strict-context`, `@animate-ui/primitives-animate-slot` |
| `primitives-buttons-liquid` | Liquid Button | `npx shadcn@latest add @animate-ui/primitives-buttons-liquid` | `motion` | `@animate-ui/lib-get-strict-context`, `@animate-ui/primitives-animate-slot` |
| `primitives-buttons-ripple` | Ripple Button | `npx shadcn@latest add @animate-ui/primitives-buttons-ripple` | `motion` | `@animate-ui/lib-get-strict-context`, `@animate-ui/primitives-animate-slot` |

### primitives/effects

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-effects-auto-height` | Auto Height | `npx shadcn@latest add @animate-ui/primitives-effects-auto-height` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-auto-height` |
| `primitives-effects-blur` | Blur | `npx shadcn@latest add @animate-ui/primitives-effects-blur` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-click` | Click | `npx shadcn@latest add @animate-ui/primitives-effects-click` | `motion` | - |
| `primitives-effects-effect` | Effect | `npx shadcn@latest add @animate-ui/primitives-effects-effect` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-fade` | Fade | `npx shadcn@latest add @animate-ui/primitives-effects-fade` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-highlight` | Highlight | `npx shadcn@latest add @animate-ui/primitives-effects-highlight` | `motion` | - |
| `primitives-effects-image-zoom` | Image Zoom | `npx shadcn@latest add @animate-ui/primitives-effects-image-zoom` | `motion` | - |
| `primitives-effects-magnetic` | Magnetic | `npx shadcn@latest add @animate-ui/primitives-effects-magnetic` | `motion` | `@animate-ui/primitives-animate-slot` |
| `primitives-effects-particles` | Particles | `npx shadcn@latest add @animate-ui/primitives-effects-particles` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-effects-shine` | Shine | `npx shadcn@latest add @animate-ui/primitives-effects-shine` | `motion` | - |
| `primitives-effects-slide` | Slide | `npx shadcn@latest add @animate-ui/primitives-effects-slide` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |
| `primitives-effects-theme-toggler` | Theme Toggler | `npx shadcn@latest add @animate-ui/primitives-effects-theme-toggler` | - | - |
| `primitives-effects-tilt` | Tilt | `npx shadcn@latest add @animate-ui/primitives-effects-tilt` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/lib-get-strict-context` |
| `primitives-effects-zoom` | Zoom | `npx shadcn@latest add @animate-ui/primitives-effects-zoom` | `motion` | `@animate-ui/primitives-animate-slot`, `@animate-ui/hooks-use-is-in-view` |

### primitives/headless

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-headless-checkbox` | Headless Checkbox | `npx shadcn@latest add @animate-ui/primitives-headless-checkbox` | `motion`, `@headlessui/react` | - |
| `primitives-headless-dialog` | Headless Dialog | `npx shadcn@latest add @animate-ui/primitives-headless-dialog` | `motion`, `@headlessui/react` | - |
| `primitives-headless-disclosure` | Headless Disclosure | `npx shadcn@latest add @animate-ui/primitives-headless-disclosure` | `motion`, `@headlessui/react` | `@animate-ui/lib-get-strict-context` |
| `primitives-headless-popover` | Headless Popover | `npx shadcn@latest add @animate-ui/primitives-headless-popover` | `motion`, `@headlessui/react` | `@animate-ui/lib-get-strict-context` |
| `primitives-headless-switch` | Headless Switch | `npx shadcn@latest add @animate-ui/primitives-headless-switch` | `motion`, `@headlessui/react` | `@animate-ui/lib-get-strict-context` |
| `primitives-headless-tabs` | Headless Tabs | `npx shadcn@latest add @animate-ui/primitives-headless-tabs` | `motion`, `@headlessui/react` | `@animate-ui/lib-get-strict-context`, `@animate-ui/primitives-effects-highlight`, `@animate-ui/primitives-effects-auto-height` |

### primitives/radix

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-radix-accordion` | Radix Accordion | `npx shadcn@latest add @animate-ui/primitives-radix-accordion` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-alert-dialog` | Radix Alert Dialog | `npx shadcn@latest add @animate-ui/primitives-radix-alert-dialog` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-checkbox` | Radix Checkbox | `npx shadcn@latest add @animate-ui/primitives-radix-checkbox` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-collapsible` | Radix Collapsible | `npx shadcn@latest add @animate-ui/primitives-radix-collapsible` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-dialog` | Radix Dialog | `npx shadcn@latest add @animate-ui/primitives-radix-dialog` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-dropdown-menu` | Radix Dropdown Menu | `npx shadcn@latest add @animate-ui/primitives-radix-dropdown-menu` | `motion`, `radix-ui` | `@animate-ui/primitives-effects-highlight`, `@animate-ui/hooks-use-controlled-state`, `@animate-ui/hooks-use-data-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-files` | Files | `npx shadcn@latest add @animate-ui/primitives-radix-files` | `motion` | `@animate-ui/primitives-radix-accordion`, `@animate-ui/primitives-effects-highlight`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-hover-card` | Radix Hover Card | `npx shadcn@latest add @animate-ui/primitives-radix-hover-card` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-popover` | Radix Popover | `npx shadcn@latest add @animate-ui/primitives-radix-popover` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-preview-link-card` | Radix Preview Link Card | `npx shadcn@latest add @animate-ui/primitives-radix-preview-link-card` | `radix-ui` | `@animate-ui/primitives-radix-hover-card`, `@animate-ui/lib-get-strict-context` |
| `primitives-radix-progress` | Radix Progress | `npx shadcn@latest add @animate-ui/primitives-radix-progress` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context` |
| `primitives-radix-radio-group` | Radix Radio Group | `npx shadcn@latest add @animate-ui/primitives-radix-radio-group` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-sheet` | Radix Sheet | `npx shadcn@latest add @animate-ui/primitives-radix-sheet` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-switch` | Radix Switch | `npx shadcn@latest add @animate-ui/primitives-radix-switch` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-tabs` | Radix Tabs | `npx shadcn@latest add @animate-ui/primitives-radix-tabs` | `motion`, `radix-ui` | `@animate-ui/primitives-effects-highlight`, `@animate-ui/primitives-effects-auto-height`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-toggle` | Radix Toggle | `npx shadcn@latest add @animate-ui/primitives-radix-toggle` | `motion`, `radix-ui` | `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-toggle-group` | Radix Toggle Group | `npx shadcn@latest add @animate-ui/primitives-radix-toggle-group` | `motion`, `radix-ui` | `@animate-ui/primitives-effects-highlight`, `@animate-ui/lib-get-strict-context`, `@animate-ui/hooks-use-controlled-state` |
| `primitives-radix-tooltip` | Radix Tooltip | `npx shadcn@latest add @animate-ui/primitives-radix-tooltip` | `motion`, `radix-ui` | `@animate-ui/hooks-use-controlled-state`, `@animate-ui/lib-get-strict-context` |

### primitives/texts

| Registry name | Title | Install | Dependencies | Registry dependencies |
| --- | --- | --- | --- | --- |
| `primitives-texts-counting-number` | Counting Number | `npx shadcn@latest add @animate-ui/primitives-texts-counting-number` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-gradient` | Gradient Text | `npx shadcn@latest add @animate-ui/primitives-texts-gradient` | `motion` | - |
| `primitives-texts-highlight` | Highlight Text | `npx shadcn@latest add @animate-ui/primitives-texts-highlight` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-morphing` | Morphing Text | `npx shadcn@latest add @animate-ui/primitives-texts-morphing` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-rolling` | Rolling Text | `npx shadcn@latest add @animate-ui/primitives-texts-rolling` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-rotating` | Rotating Text | `npx shadcn@latest add @animate-ui/primitives-texts-rotating` | `motion` | `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-texts-scrolling-number` | Scrolling Number | `npx shadcn@latest add @animate-ui/primitives-texts-scrolling-number` | `motion` | `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |
| `primitives-texts-shimmering` | Shimmering Text | `npx shadcn@latest add @animate-ui/primitives-texts-shimmering` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-sliding-number` | Sliding Number | `npx shadcn@latest add @animate-ui/primitives-texts-sliding-number` | `motion`, `react-use-measure` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-splitting` | Splitting Text | `npx shadcn@latest add @animate-ui/primitives-texts-splitting` | `motion` | `@animate-ui/hooks-use-is-in-view` |
| `primitives-texts-typing` | Typing Text | `npx shadcn@latest add @animate-ui/primitives-texts-typing` | `motion` | `@animate-ui/hooks-use-is-in-view`, `@animate-ui/lib-get-strict-context` |

## Icon Note

Animated icons are under `icons/<lucide-icon-name>`. Install only the exact icon needed, for example `npx shadcn@latest add @animate-ui/icons-arrow-right`.
