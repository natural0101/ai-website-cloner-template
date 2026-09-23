# Micro Component Source Map

Дата проверки: 2026-07-03.

This source map is for small shadcn-compatible UI details, not whole landing sections. Use it when the plan needs forms, command menus, calendars, code blocks, data tables, upload/dropzone, ratings, tags, media, product/app-preview widgets, or similar details.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Kibo UI docs | https://www.kibo-ui.com/docs | 200 |
| Kibo UI live registry index | https://www.kibo-ui.com/r/registry.json | `HEAD` 200; body can time out after partial JSON |
| Kibo UI item example | https://www.kibo-ui.com/r/code-block.json | 200 JSON |
| Kibo UI item example | https://www.kibo-ui.com/r/color-picker.json | 200 JSON |
| Kibo UI bad generic endpoint | https://www.kibo-ui.com/r/button.json | 500 package lookup error, do not use guessed names |
| Kibo UI root registry | https://www.kibo-ui.com/registry.json | 404, do not use |
| Kibo UI GitHub | https://github.com/shadcnblocks/kibo | 200 |
| Kibo UI README | https://raw.githubusercontent.com/shadcnblocks/kibo/main/README.md | 200 |
| Kibo UI license | https://raw.githubusercontent.com/shadcnblocks/kibo/main/license.md | 200, MIT-style |
| Origin UI / Coss live site | https://coss.com/ui | 200 |
| Origin UI original domain | https://originui.com/ | redirects to `https://coss.com/ui` |
| Origin/Coss item example | https://coss.com/ui/r/accordion.json | 200 JSON |
| Origin/Coss item example | https://coss.com/ui/r/button.json | 200 JSON |
| Origin UI GitHub | https://github.com/shadcn/originui | 200 |
| Origin UI registry | https://raw.githubusercontent.com/shadcn/originui/main/registry.json | 646 items |
| Origin UI license | https://raw.githubusercontent.com/shadcn/originui/main/LICENSE.md | MIT |

## Kibo UI Findings

Kibo UI is a custom registry built on top of shadcn/ui. The current GitHub repo is `shadcnblocks/kibo`; GitHub API reports MIT license, 3837 stars, default branch `main`, and latest observed push on 2026-05-04. README describes Kibo UI as composable, accessible, open source components for shadcn/ui.

Fresh check on 2026-07-03 found 44 package folders, including 40 user-facing package names and 4 workspace/service packages. Root `/registry.json` returned 404. Live `/r/registry.json` returned 200 on `HEAD`, but full body can time out after partial JSON. GitHub raw registry is not a static file; `apps/docs/app/r/registry.json` is a route folder, not a raw registry source. Use package names plus exact live item endpoints as install evidence.

Cleanly parsed live item endpoints:

```text
announcement, avatar-stack, banner, calendar, choicebox, code-block, color-picker, combobox, comparison, contribution-graph, credit-card, cursor, deck, dialog-stack, dropzone, glimpse, image-crop, image-zoom, kanban, list, marquee, mini-calendar, pill, qr-code, rating, relative-time, sandbox, snippet, spinner, status, table, tags, theme-switcher, ticker, tree, typography, video-player
```

Large live endpoints with `HEAD 200` but body timeout during this audit:

```text
editor, gantt, reel
```

Install model:

```bash
npx shadcn@latest add https://www.kibo-ui.com/r/code-block.json
```

Dependency notes from parsed endpoints:

- Frequent: `lucide-react` 19, shadcn `button` 11, `@radix-ui/react-use-controllable-state` 9, `radix-ui` 5, `badge` 4, `motion` 4.
- Higher-cost examples: `code-block` brings Shiki, `@shikijs/transformers`, `react-icons`; `table` brings `@tanstack/react-table` and `jotai`; `kanban` brings `@dnd-kit/*` and `tunnel-rat`; `sandbox` brings `@codesandbox/sandpack-react`; `dropzone` brings `react-dropzone`; `video-player` brings `media-chrome`.
- Heavy package manifests: `editor` uses Tiptap, ProseMirror, lowlight, fuse.js and tippy.js; `gantt` uses dnd-kit, date-fns, jotai and lodash.throttle; `reel` uses motion.

Useful landing choices:

- `announcement`, `banner`, `avatar-stack`, `rating`, `tags`, `status`, `spinner`, `relative-time`, `ticker`, `marquee` for proof and UI polish.
- `code-block`, `snippet`, `sandbox`, `typography` for developer tools and code sections.
- `combobox`, `choicebox`, `calendar`, `dropzone`, `image-crop`, `color-picker` for forms and interactive product-preview flows.
- `table`, `kanban`, `tree`, `contribution-graph` only when the landing honestly previews product UI.
- `gantt`, `editor`, `reel` only after a fresh exact-body fetch succeeds or source adaptation is explicitly planned.
- `video-player`, `deck`, `image-zoom`, `credit-card` only with a clear content/product reason.

Reject by default:

- `cursor` unless the whole page interaction model earns it.
- Heavy code/media/editor/table/calendar components for a static marketing page.
- Components with dependencies like `shiki`, `react-icons`, `jotai`, drag/drop stacks, media players or charting when a static visual is enough.
- Generic endpoint guesses like `button`, `accordion`, or `ai-input`; these returned package lookup errors.

## Origin UI / Coss Findings

Origin UI is an MIT-licensed copy-and-paste component library. The public Origin domain currently redirects to `https://coss.com/ui`. The GitHub repo contains `registry.json`, `registry/default`, and `public/r`.

Raw GitHub registry stats:

- 646 items total.
- 40 `registry:ui`.
- 600 `registry:component`.
- 5 `registry:hook`.
- 1 `registry:lib`.

Live endpoint rules:

- `https://originui.com/r/accordion.json` redirected to HTML at `https://coss.com/ui`, not JSON.
- `https://coss.com/ui/r/accordion.json` returned 200 JSON.
- `https://coss.com/ui/r/button.json` returned 200 JSON.
- Some raw registry names may not have matching live Coss endpoints; verify each exact endpoint before use.

README setup model says to copy files from `registry/default/ui` to `components/ui`, copy `utils.ts` from `registry/default/lib`, and add CSS variables. Treat this as a copy/adapt source unless a live Coss registry URL is verified.

Useful landing choices:

- Form fields, date/calendar variants, select/combobox, dropdown, command, popover, dialog, drawer, pagination, tabs, tooltip, upload/file UI, avatar, badge, button, breadcrumb, and table details.
- Use when a section needs a polished control, not when shadcn's existing primitive already solves it.

Reject by default:

- Replacing the whole project's shadcn style layer just to use one component.
- Copying Origin/Coss CSS variables over the project's style tile.
- Registry URLs on `originui.com/r/*` unless they return JSON; prefer verified `coss.com/ui/r/*` endpoints.
- `registry:hook` or `registry:lib` items without a component that needs them.

## Selection Rules

Before implementation, fill:

```text
projects/<slug>/34-micro-component-selection.md
```

The file must record source, exact item, source URL, registry/copy URL, install command or copy method, dependencies, license/access, adaptation, reduced-motion fallback if animated, mobile simplification, keyboard/focus QA, owner `task-###`, and `chg-###`.

For Kibo UI, also record live endpoint verification. For `editor`, `gantt`, or `reel`, record a fresh body-fetch result or mark the item reference-only/backlog.
