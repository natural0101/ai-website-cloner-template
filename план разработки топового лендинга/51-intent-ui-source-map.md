# Intent UI Source Map

Дата проверки: 2026-07-03.

Intent UI is an MIT, React Aria Components and Tailwind based component registry. Use it as a gated source for accessible app/product UI details: forms, fields, selects, combo boxes, date/time/color controls, tables, menus, command menus, drawers, sheets, dialogs, navbars, sidebars, charts, auth blocks and product proof surfaces. It is not a default landing decoration source.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://intentui.com/ | live site; full `GET` can reset during audit |
| Sitemap | https://intentui.com/sitemap.xml | 200, 108 URLs |
| Robots | https://intentui.com/robots.txt | 200 |
| LLM map | https://intentui.com/llms.txt | 200, 8094 bytes |
| Live registry index | https://intentui.com/r/registry.json | full `GET` returned `ECONNRESET` during audit |
| Root registry guess | https://intentui.com/registry.json | 404 |
| Exact item endpoints | https://intentui.com/r/&lt;name&gt; and https://intentui.com/r/&lt;name&gt;.json | sampled both work; 569/569 `.json` endpoints returned 200 on `HEAD` |
| GitHub repo | https://github.com/intentui/intentui | 200, MIT via GitHub API |
| GitHub license | https://raw.githubusercontent.com/intentui/intentui/3.x/LICENSE | MIT |
| GitHub public registry | https://raw.githubusercontent.com/intentui/intentui/3.x/registry.json | 200, 459676 bytes, 569 items |
| GitHub README | https://raw.githubusercontent.com/intentui/intentui/3.x/README.md | documents React Aria Components and MIT |

## Site And Registry Inventory

Sitemap:

- 108 URLs total.
- 5 block/category URLs under `/blocks`.
- 96 docs URLs.
- `blog`, `showcase`, `components`, `icons`, `colors`, `sponsor`.
- 108/108 sitemap URLs returned 200 on `HEAD`.
- `llms.txt` is live and maps docs `.md` URLs.

Registry scan:

- 569 registry items total.
- 88 `registry:ui` items.
- 438 `registry:page` examples.
- 25 `registry:block` items.
- 12 `registry:style` theme entries.
- 3 `registry:hook` entries.
- 2 `registry:lib` entries.
- 1 `registry:item` entry named `all`.
- 569/569 exact live item endpoints returned 200 on `HEAD`.
- Raw registry on `main` returned 404; the active branch is `3.x`.
- Live `GET /r/registry.json` returned `ECONNRESET`; use GitHub raw registry for catalog rebuilds and verify exact live item endpoints before install.

Install command:

```bash
npx shadcn@latest add @intentui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://intentui.com/r/<name>
```

The `.json` variant also works:

```bash
npx shadcn@latest add https://intentui.com/r/<name>.json
```

## License And Access Gate

Intent UI is MIT.

- GitHub API reports MIT.
- Raw `LICENSE` on `3.x` is MIT.
- README says the project is built on React Aria Components and Tailwind CSS and is MIT licensed.

Do not treat `design.intentui.com` blocks/templates as public source unless project-specific access and license are documented.

## Registry Groups

| Group | Count | Notes |
| --- | ---: | --- |
| `registry:ui` | 88 | Main component pool. |
| `registry:page` | 438 | Example pages; reference-only by default. |
| `registry:block` | 25 | Navbar, sidebar, auth and chart blocks. Use as gated product proof. |
| `registry:style` | 12 | Theme entries; do not install broadly. |
| `registry:hook` | 3 | `use-clipboard`, `use-media-query`, `use-mobile`. Dependency helpers. |
| `registry:lib` | 2 | `date`, `primitive`. Dependency helpers. |
| `registry:item` | 1 | `all`; do not use. |

Core UI items:

```text
area-chart, avatar, badge, bar-chart, bar-list, breadcrumbs, button-group, button, calendar, card, carousel, chart, checkbox, choice-box, color-area, color-field, color-picker, color-slider, color-swatch-picker, color-swatch, color-thumb, color-wheel, combo-box, command-menu, container, context-menu, date-field, date-picker, date-range-picker, description-list, dialog, disclosure-group, drawer, drop-zone, dropdown, field, file-trigger, grid-list, heading, input-otp, input, keyboard, leaderboard, line-chart, link, list-box, loader, menu, meter, modal, multiple-select, native-select, navbar, note, number-field, pagination, pie-chart, popover, progress-bar, progress-circle, radio, range-calendar, scroll-area, search-field, select, separator, sheet, show-more, sidebar, skeleton, slider, snippet, switch, table, tabs, tag-field, tag-group, text-field, text, textarea, time-field, toast, toggle-group, toggle, toolbar, tooltip, tracker, tree
```

Block items:

```text
auth-01, auth-02, auth-03, chart-01, chart-02, chart-03, navbar-01, navbar-02, navbar-03, navbar-04, navbar-05, sidebar-01, sidebar-02, sidebar-03, sidebar-04, sidebar-05, sidebar-06, sidebar-07, sidebar-08, sidebar-09, sidebar-12, sidebar-15, sidebar-16, sidebar-17, sidebar-19
```

Common runtime dependencies:

| Dependency | Count |
| --- | ---: |
| `react-aria-components` | 137 |
| `@heroicons/react` | 82 |
| `tailwind-merge` | 66 |
| `@internationalized/date` | 17 |
| `recharts` | 13 |
| `tailwind-variants` | 13 |
| `@react-stately/color` | 11 |
| `sonner` | 10 |
| `react-stately` | 8 |
| `motion` | 3 |

Raw registry caveat: many registry dependencies in GitHub raw are localhost URLs such as `http://localhost:3000/r/button`. Live registry items return `https://intentui.com/r/<name>` dependencies. Verify live endpoint before install.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Accessible form proof | `field`, `text-field`, `input`, `textarea`, `select`, `combo-box`, `multiple-select`, `checkbox`, `radio`, `switch`, `number-field` | Use when the product has real form/configuration UX. |
| Date/time workflow | `date-field`, `date-picker`, `date-range-picker`, `range-calendar`, `time-field` | Good for scheduling, booking, dashboards and reporting. |
| Data and product proof | `table`, `grid-list`, `tree`, `leaderboard`, `tracker`, chart items | Requires real rows/metrics and mobile transformation. |
| Command and navigation | `command-menu`, `menu`, `context-menu`, `navbar`, `sidebar`, `breadcrumbs`, `tabs` | Good for app/developer/power-user products. |
| Overlays and feedback | `dialog`, `modal`, `sheet`, `drawer`, `popover`, `tooltip`, `toast` | Use for real flow states, not decoration. |
| File/import flow | `file-trigger`, `drop-zone` | Use for file, import, document or media products. |
| Product proof blocks | `auth-*`, `navbar-*`, `sidebar-*`, `chart-*` | Replace demo copy/data and avoid generic chrome. |

## Reject Or Use Carefully

- Reject `registry:page` example items as production source unless explicitly justified.
- Reject `all` and broad theme packs.
- Reject paid `design.intentui.com` material without explicit access/license.
- Reject React Aria stack if local shadcn/Radix/native components already solve the section with lower dependency risk.
- Reject color picker controls unless the product is color/design/editor related.
- Reject chart/table blocks without real data and mobile plan.
- Reject sidebar/navbar/auth blocks as decorative app chrome.
- Reject demo users, fake metrics, fake forms, fake files and fake charts.

## Selection Flow

1. Identify the section job and whether Intent UI is install source, reference-only or rejected.
2. Check existing/local/shadcn, Origin/Coss, Kibo UI, ReUI, HextaUI, Blocks.so, MVPBlocks, SmoothUI and custom code first.
3. Choose one exact Intent UI item or explicitly reject Intent UI for the section.
4. Verify docs/source URL from `llms.txt` or sitemap and endpoint `https://intentui.com/r/<name>`.
5. Record MIT license, React Aria dependency impact, dependencies, registry dependencies, adaptation, accessibility notes, mobile behavior, demo-data replacement, task ID, change ID and QA.
6. Map the item to `08-component-and-asset-plan.md`, `20-implementation-task-graph.md` and `28-change-traceability-matrix.md`.

## Required Project File

```text
projects/<slug>/47-intent-ui-selection.md
```

The file must record exact item, item type, source URL, endpoint URL, install command, MIT license, dependencies, registry dependencies, React Aria impact, visible purpose, adaptation, demo-data replacement, accessibility notes, mobile behavior, decision, task ID, change ID and QA evidence.
