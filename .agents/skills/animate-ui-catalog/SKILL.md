---
name: animate-ui-catalog
description: Use when adding, selecting, adapting, or reviewing Animate UI components, primitives, effects, text animations, animated buttons, backgrounds, hooks, or icons in this project. Requires checking the local Animate UI catalog before choosing a registry item.
metadata:
  docs_url: "https://animate-ui.com"
  registry_base: "https://animate-ui.com/r/"
  source_repo: "https://github.com/imskyleen/animate-ui"
  local_catalog: "docs/research/animate-ui-catalog.md"
  license: "MIT + Commons Clause"
---

# Animate UI Catalog

Use this skill when the user asks for animated UI, polished motion, interactive components, animated text, premium buttons, backgrounds, accordions/dialogs/tabs/popovers, or Animate UI specifically.

## Required First Step

Read the project catalog before choosing a component:

```text
docs/research/animate-ui-catalog.md
```

The catalog contains the current scan of Animate UI registry items, install commands, dependencies, and registry dependency chains.

For landing-page planning, also read:

```text
план разработки топового лендинга/17-animate-ui-full-site-map.md
```

That site map covers the live docs crawl, not just the registry. It separates visible docs pages from registry-only service entries.

If Animate UI is used or even seriously considered for a landing plan, fill:

```text
план разработки топового лендинга/projects/<slug>/14-animate-ui-selection.md
```

## Install Pattern

Animate UI is copy-first, shadcn-registry style. Install one item at a time:

```bash
npx shadcn@latest add @animate-ui/<registry-name>
```

Examples:

```bash
npx shadcn@latest add @animate-ui/components-buttons-liquid
npx shadcn@latest add @animate-ui/primitives-effects-magnetic
npx shadcn@latest add @animate-ui/primitives-texts-splitting
```

Do not bulk-install the whole site. Pick the smallest registry item that matches the design need.

## Best Categories For This Project

- `primitives/effects`: auto-height, blur, fade, slide, zoom, tilt, magnetic, particles, shine, highlight.
- `primitives/texts`: splitting, typing, rotating, morphing, gradient, shimmering, sliding/counting numbers.
- `components/buttons`: button, copy, flip, liquid, ripple, theme toggler.
- `components/backgrounds`: gradient, stars, gravity-stars, hole, bubble.
- `components/animate`: tabs, tooltip, cursor, avatar group, code tabs.
- `components/community`: motion carousel, notification list, pin list, radial menu/nav, share button, user presence avatar.
- `components/headless` and `components/radix`: use when accessibility primitives matter and the project already uses the matching primitive family.

## Full Site Counts

Latest checked full site, live docs, `.mdx`, and registry: `https://animate-ui.com/`, `https://animate-ui.com/docs`, `https://animate-ui.com/docs/components`, `https://animate-ui.com/docs/primitives`, `https://animate-ui.com/docs/icons`, and `https://animate-ui.com/r/registry.json`.

Latest whole-site audit on 2026-07-03 03:47 MSK rechecked `/`, discovered internal non-asset paths, docs HTML, docs `.mdx`, `registry.json`, and all 580 item endpoints.

Full-site crawl:

- 361 internal paths probed.
- 172 live HTML pages.
- 171 live docs pages.
- 171 live docs `.mdx` endpoints.
- 580 registry item endpoints checked with 200 status.
- Only `/` exists as useful non-docs HTML; the working surface is `/docs` and `/r`.

Live docs crawl:

- `sitemap.xml` returns 404, so use sidebar links and `.mdx` docs endpoints.
- 171 unique docs links.
- 75 component docs links: 73 installable component pages plus `/docs/components` and `/docs/components/community`.
- 82 primitive docs links: 81 installable primitive pages plus `/docs/primitives`.
- 6 icon docs links.
- 8 guide/reference pages.

Registry scan:

- 580 registry items total.
- 1 style `index`.
- 159 demo entries.
- 260 animated icon entries.
- 73 component entries.
- 81 primitive entries.
- 5 hook entries.
- 1 lib entry.
- 160 non-demo/non-icon items, but the normal visual selection pool is 154 component/primitive entries.

Treat demos as references. Treat icons as exact one-off installs. Treat hooks and lib as dependency-chain helpers. Treat the 154 component/primitive entries as the normal component selection pool.

Latest audit result: `sitemap.xml` still returns 404; 580/580 registry item endpoints return 200; there are 73 installable component docs and 81 installable primitive docs. Root shortcuts such as `/installation`, `/accessibility`, `/mcp`, `/roadmap`, and `/other-animated-distributions` return 404, so cite and use the `/docs/*` versions.

User-requested whole-site rewalk on 2026-07-03 05:22 MSK rechecked the live internal surface from `/`, `/docs`, `/docs/components`, `/docs/primitives`, and `/docs/icons`, then checked docs `.mdx`, `registry.json`, and all item endpoints. Result stayed stable: `sitemap.xml` returns 404; 186 internal non-asset paths; 172 live HTML pages; 171 live docs HTML pages; 171 live docs `.mdx` endpoints; 75 component docs links including indexes; 82 primitive docs links including index; 6 icon docs; 8 guide/reference pages; 580 registry items; and 580/580 `/r/<item>.json` endpoints OK. The only useful live non-docs HTML page remains `/`.

Latest whole-site rewalk on 2026-07-03 05:49 MSK confirmed the same useful surface: `sitemap.xml` returns 404; 186 internal non-asset paths; 172 live HTML pages; 171 docs `.mdx` endpoints with 200; 8 generated docs paths with 404; `registry.json` returns 200 with 580 items; 580/580 item endpoints return 200. Registry groups are still 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, and 1 style index.

Latest user-requested full-site crawl on 2026-07-03 06:21 MSK rechecked root, docs branches, service-map paths, docs `.mdx`, `registry.json`, and every registry item endpoint. `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/docs/llms.txt`, `/.well-known/llms.txt`, `/docs.json`, and `/openapi.json` all return 404. The live surface stays stable: 172 HTML pages with 200, 171 docs `.mdx` endpoints with 200, 9 generated/internal 404 paths, 580 registry items, and 580/580 item endpoints with 200.

Latest user-requested full-site rewalk on 2026-07-03 10:48 MSK checked the whole known surface again. Live `HEAD` checks returned 200 for `/`, 171 docs pages, 171 docs `.mdx` endpoints, and 580/580 `/r/<item>.json` endpoints. Live `GET /r/registry.json` currently stalls after partial 20-24 KB downloads, although `HEAD` returns 200; GitHub raw `apps/www/public/r/registry.json` fetched fully at 417344 bytes with 580 items and unchanged counts. If the live registry body stalls, rebuild the catalog from GitHub raw, then verify the chosen live item endpoint before install.

Latest user-requested full-site rewalk on 2026-07-03 11:40 MSK checked the known surface again with GitHub raw registry plus live `HEAD` and calm retries. GitHub raw `apps/www/public/r/registry.json` fetched fully at 417344 bytes with 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` returned `ECONNRESET`. Expected HTML surface (`/` plus 171 docs pages) returned 200 after retrying `/docs/changelog`; all 171 docs `.mdx` endpoints returned 200; all 580 live `/r/<item>.json` endpoints returned 200 after calm retry. Service maps remain 404 and counts are unchanged.

Latest user-requested whole-site rewalk on 2026-07-03 12:20 MSK checked service maps, live seed pages, official GitHub tree, GitHub raw registry, all docs routes, docs `.mdx` endpoints, and every live item endpoint. Service maps still return 404. The official GitHub tree has 171 unique docs routes: 8 guide pages, 75 component docs including indexes, 82 primitive docs including index, and 6 icon docs. Live `HEAD` returned 200 for all 171 docs routes after retrying `/docs/primitives/base/progress`; all 171 docs `.mdx` endpoints returned 200. GitHub raw registry fetched fully at 417344 bytes with 580 items. Live `HEAD /r/registry.json` returned 200, while live `GET /r/registry.json` timed out after partial 20895 bytes. All 580 live `/r/<item>.json` endpoints returned 200. Use GitHub tree and raw registry for full inventory if live HTML or registry body stalls, then verify exact live item endpoint before install.

Fresh user-requested whole-site rewalk on 2026-07-03 12:59 MSK checked service maps, live seed pages, official GitHub tree, GitHub raw registry, all docs routes, docs `.mdx` endpoints, and every live item endpoint. The useful surface stayed stable: service maps return 404; seed pages return 200; the official GitHub tree has 171 unique docs routes; 171/171 live docs routes return 200; 171/171 docs `.mdx` endpoints return 200; GitHub raw registry fetched fully at 417344 bytes with 580 items; live `HEAD /r/registry.json` returns 200 while live `GET /r/registry.json` hit a bounded `AbortError`; all 580 live `/r/<item>.json` endpoints return 200. Use GitHub tree and raw registry for full inventory if live HTML or registry body stalls, then verify exact live item endpoint before install.

Latest user-requested whole-site rewalk on 2026-07-03 13:43 MSK checked service maps, seed pages, official GitHub tree, all 171 docs routes, all 171 docs `.mdx` endpoints, raw registry, live registry `HEAD`, bounded live registry `GET`, and all 580 live item endpoints. Result stayed stable: service maps return 404; seed pages return 200; GitHub tree has 171 docs routes; 171/171 docs HTML routes return 200; 171/171 docs `.mdx` endpoints return 200; raw registry returns 580 items; live `HEAD /r/registry.json` returns 200 while live `GET /r/registry.json` aborts under a bounded timeout; all 580 live `/r/<item>.json` endpoints return 200. Counts are unchanged: 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, and 1 style index.

Bad generated links observed during crawl:

- `/docs/primitives/base/menuarrow`
- `/docs/primitives/base/menucheckboxitem`
- `/docs/primitives/base/menuitem`
- `/docs/primitives/base/menuradiogroup`
- `/docs/primitives/base/menuradioitem`
- `/docs/primitives/base/menushortcut`
- `/docs/primitives/base/menusubmenu`
- `/docs/primitives/base/menusubmenutrigger`
- `/react/primitives/animate/tooltip`

Do not cite or install from those paths. Use `/docs/components/base/menu`, `/docs/primitives/base/menu`, `/docs/components/animate/tooltip`, and `/docs/primitives/animate/tooltip`.

Registry-only service entries:

- `hooks-use-auto-height`
- `hooks-use-controlled-state`
- `hooks-use-data-state`
- `hooks-use-is-in-view`
- `hooks-use-motion-value-state`
- `lib-get-strict-context`

The live docs pages for `/docs/hooks/*` and `/docs/lib/*` currently return 404. Install these only as dependency-chain helpers, not as design choices.

## Icon Rules

Animate UI icons are animated Lucide icons. The docs mark them as beta, so use them carefully.

- Install the icon wrapper only if animated icons are actually used.
- Install exact icons only, for example `npx shadcn@latest add @animate-ui/icons-arrow-right`.
- Check icon usage docs for `animation`, persistence, timing and trigger behavior.
- Prefer hover, tap or controlled triggers for CTA/tool icons.
- Avoid looping icons unless the loop communicates a live status.
- Reduced motion fallback must be a static icon or a tiny opacity/state change.

## Dependency Awareness

Common dependencies:

- `motion`
- `lucide-react`
- `class-variance-authority`
- `@headlessui/react`
- `radix-ui`
- `@base-ui-components/react`
- `next-themes`
- `shiki`

Before installing, inspect `package.json`. If the dependency is not already present, expect `shadcn` to add it or install it deliberately.

## Adaptation Rules

1. Match this project's existing aliases and utilities.
   - Prefer `@/lib/utils` for `cn()`.
   - Avoid leaving Animate UI's monorepo aliases such as `@workspace/ui/lib/utils`.
2. Preserve accessibility semantics from the primitive.
3. Keep client boundaries tight: only interactive components need `use client`.
4. Do not install animated backgrounds or particles unless they serve the product story.
5. Verify desktop and mobile screenshots for layout, motion, clipping, and overlap.
6. Avoid custom cursor, fireworks, radial menu/nav, GitHub stars wheel, and app sidebar unless the landing brief specifically earns them.

## License Caveat

Animate UI is MIT + Commons Clause. Use/adapt inside an application, website, or product. Do not redistribute or sell the components themselves as a standalone component library or bundle.

## Sources

- https://animate-ui.com
- https://animate-ui.com/docs
- https://github.com/imskyleen/animate-ui
