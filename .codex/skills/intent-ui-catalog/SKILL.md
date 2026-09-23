---
name: intent-ui-catalog
description: Use when adding, selecting, adapting, or reviewing Intent UI components from intentui.com or the @intentui shadcn registry. Applies to accessible React Aria Components, forms, fields, selects, combo boxes, date/time/color controls, tables, menus, command menus, drawers, sheets, dialogs, navbars, sidebars, charts, auth blocks, and app/product proof surfaces. Requires exact endpoint, MIT/license, React Aria dependency, example/page rejection, mobile, accessibility, demo-data, and anti-bulk-install checks before install or adaptation.
---

# Intent UI Catalog

Use this skill when a landing plan considers Intent UI for accessible app-like controls, forms, data tables, filters, date/time/color pickers, command palettes, sidebars, navbars, charts, auth blocks, or product UI proof.

## Required First Step

Read the project source map:

```text
план разработки топового лендинга/51-intent-ui-source-map.md
```

If Intent UI is used or seriously considered for a project plan, fill:

```text
план разработки топового лендинга/projects/<slug>/47-intent-ui-selection.md
```

## Verified Model

- Official site: `https://intentui.com`.
- Registry URL template: `https://intentui.com/r/{name}`.
- Extension form `https://intentui.com/r/<name>.json` also returns JSON.
- Reliable source registry: `https://raw.githubusercontent.com/intentui/intentui/3.x/registry.json`.
- Current scan: 569 registry items.
- Registry split: 88 `registry:ui`, 438 `registry:page`, 25 `registry:block`, 12 style themes, 3 hooks, 2 libs, 1 `all` item.
- 569/569 live `/r/<name>.json` endpoints returned 200 on `HEAD`.
- Sitemap has 108 URLs; 108/108 returned 200 on `HEAD`.
- `llms.txt` is live and maps docs pages.
- Live `GET /r/registry.json` can return `ECONNRESET`; use GitHub raw registry for catalog rebuilds and verify exact live endpoints before install.

## License Gate

Intent UI is MIT.

- GitHub repo: `intentui/intentui`.
- Default branch: `3.x`.
- Raw license file: `LICENSE`.
- README says Intent UI is built on React Aria Components and Tailwind CSS.

Do not copy or treat paid `design.intentui.com` blocks/templates as public source unless project-specific access and license are documented.

## Install Pattern

Official namespace:

```bash
npx shadcn@latest add @intentui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://intentui.com/r/<name>
```

Do not install `@intentui/all`. Do not bulk-install.

## Best Landing Uses

- Accessible form controls: `field`, `text-field`, `input`, `textarea`, `select`, `combo-box`, `multiple-select`, `checkbox`, `radio`, `switch`, `number-field`.
- Date/time workflows: `date-field`, `date-picker`, `date-range-picker`, `range-calendar`, `time-field`.
- Data/product proof: `table`, `grid-list`, `tree`, `leaderboard`, `tracker`, `area-chart`, `bar-chart`, `line-chart`, `pie-chart`, `bar-list`.
- App navigation and command surfaces: `navbar`, `sidebar`, `command-menu`, `menu`, `context-menu`, `breadcrumbs`, `tabs`.
- Overlays: `dialog`, `modal`, `sheet`, `drawer`, `popover`, `tooltip`, `toast`.
- File and upload flows: `file-trigger`, `drop-zone`.
- Product proof blocks: `auth-01` through `auth-03`, `navbar-01` through `navbar-05`, `sidebar-*`, `chart-01` through `chart-03`.

## Reject By Default

- `registry:page` example items as production source; use them as reference-only unless the selection file explains the exception.
- `all` item and theme packs as broad install choices.
- Sidebars/navbars/auth blocks when they are decorative rather than product-proof.
- Color picker stack unless the product is a design/editor/color workflow.
- Chart/table stack unless real data, mobile behavior and truthful metrics exist.
- React Aria stack when existing local shadcn/Radix components already solve the section with lower dependency risk.
- Paid design.intentui blocks/templates without explicit access and license.

## Selection Checklist

1. Name the section job and whether Intent UI is install source, reference-only, or rejected.
2. Verify exact endpoint `https://intentui.com/r/<name>`.
3. Record docs/source URL from `llms.txt` or sitemap.
4. Record MIT license, React Aria dependency impact, registry dependencies, style adaptation, accessibility notes, mobile behavior, demo-data replacement, and QA evidence.
5. Map the item to `task-###` and `chg-###`.

## Sources

- https://intentui.com/
- https://intentui.com/sitemap.xml
- https://intentui.com/llms.txt
- https://intentui.com/r/registry.json
- https://github.com/intentui/intentui
- https://raw.githubusercontent.com/intentui/intentui/3.x/registry.json
- https://raw.githubusercontent.com/intentui/intentui/3.x/LICENSE
