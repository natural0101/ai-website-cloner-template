# ReUI Source Map

Дата проверки: 2026-07-03.

ReUI is a React/Tailwind/shadcn registry source for app UI, data-heavy components, dashboards, forms, blocks and paid templates. Use it as a gated product-interface source, not as a generic landing page style.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://reui.io/ | 200 |
| Docs | https://reui.io/docs | 200 |
| Get started | https://reui.io/docs/get-started | 200 |
| Registry docs | https://reui.io/docs/registry | 200 |
| License setup docs | https://reui.io/docs/license-setup | 200 |
| MCP docs | https://reui.io/docs/mcp | 200 |
| Agent skills docs | https://reui.io/docs/agent-skills | 200 |
| Sitemap | https://reui.io/sitemap.xml | 200, 209 URLs |
| Pricing | https://reui.io/pricing | 200 |
| License | https://reui.io/legal/license | 200 |
| Terms | https://reui.io/legal/terms-and-conditions | 200 |
| Root registry | https://reui.io/r/registry.json | 401, requires license key |
| Root `/registry.json` | https://reui.io/registry.json | 404 |
| Free item sample | https://reui.io/r/radix-nova/c-button-1.json | 200 JSON |
| Free item sample | https://reui.io/r/radix-nova/c-data-grid-1.json | 200 JSON |
| Primitive sample | https://reui.io/r/radix-nova/alert.json | 200 JSON |
| Premium/locked sample | https://reui.io/r/radix-nova/button.json | 401 without license |

## Surface Inventory

Sitemap check:

- 209 URLs total.
- Latest whole-site sitemap rewalk on 2026-07-03 05:49 MSK returned 200 for all 209 URLs.
- 45 docs URLs.
- 69 `/components/<name>` pages.
- 36 `/docs/components/*` pages: 18 Base and 18 Radix docs.
- 55 `/blocks/*` pages: 19 application, 9 data-grid, 9 solutions, 13 ecommerce and 5 marketing pages.
- `/templates` is live but currently shows 0 templates.

Component page scan found 1019 `c-*` component variant names across 69 component pages. Pricing page describes a free foundation of 1019 components and paid Pro/Ultimate tiers. Use exact `c-*` item URLs only after verifying the live endpoint.

Latest registry gate recheck on 2026-07-03 05:49 MSK: root `/registry.json` returned 404; `/r/registry.json` redirected to the style registry and returned 401 without license; exact free samples `c-button-1`, `c-alert-1`, `c-data-grid-1`, and `alert` returned 200; locked `button` returned 401 without license.

## Access And License

Free component examples use `c-*` names and can be installed without a license key according to ReUI docs. Some free examples pull shared `@reui/*` primitives as registry dependencies.

Premium blocks, icons and templates require a ReUI license key. License setup docs require:

```env
REUI_LICENSE_KEY=your-license-key-here
```

and authenticated `@reui` registry config with an Authorization Bearer header.

License page summary: purchased license allows building your own projects, shipping client projects and customizing code, but does not allow repackaging the licensed materials so others can obtain or resell them.

## Install Model

Free registry config from docs:

```json
{
  "registries": {
    "@reui": "https://reui.io/r/{style}/{name}.json"
  }
}
```

Recommended default style:

```text
radix-nova
```

Exact free component example:

```bash
npx shadcn@latest add @reui/c-alert-1
```

Exact URL example:

```bash
npx shadcn@latest add https://reui.io/r/radix-nova/c-alert-1.json
```

Do not use root `/registry.json`. Do not assume style registry indexes are public; root/style registry indexes returned 401 during this check.

## Dependency Risk

Representative checked endpoints:

- `c-button-1`: `registry:block`, depends on registry `button`.
- `c-data-grid-1`: `registry:block`, package dependency `@tanstack/react-table`, registry dependency `@reui/data-grid`.
- `data-grid`: `registry:ui`, dependencies include `@base-ui/react`, `@dnd-kit/*`, `@tanstack/react-table`, `@tanstack/react-virtual`, `class-variance-authority`, and many registry dependencies.
- `alert`: `registry:ui`, dependency `class-variance-authority`.

Bulk endpoint probing of extracted `c-*` names produced intermittent 403/locked responses, so exact endpoint verification is mandatory in each project. Treat 401/403 without license evidence as reference-only.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Product/app proof | `frame`, `c-frame-*`, `data-grid`, `c-data-grid-*`, `table`, `timeline` | Best for SaaS/admin/product sections where the UI itself is proof. |
| Forms and conversion | `field`, `input`, `input-group`, `select`, `combobox`, `phone-input`, `date-selector`, `file-upload` | Use when the landing includes a realistic form or product workflow. |
| Status and trust | `alert`, `c-alert-*`, `badge`, `rating`, `progress`, `stepper` | Good for status, onboarding, pricing/billing, system health and proof details. |
| Navigation and interaction | `accordion`, `tabs`, `popover`, `tooltip`, `drawer`, `sheet` | Use if local shadcn/Animate UI does not already cover it. |
| Data/product workflows | `kanban`, `tree`, `sortable`, `filters`, `scrollspy` | Use only when these workflows match the product story. |

## Avoid By Default

- Premium blocks, icons and templates without explicit ReUI license/access.
- Root registry or style registry indexes as source of truth when they return 401.
- Heavy data-grid/drag/sortable stacks for decorative mockups.
- Installing ReUI primitives when shadcn/local components already solve the UI.
- Copying ReUI demo content, claims or screenshots.
- Treating ReUI as a visual identity; use it for credible app interface details.

## Selection Flow

1. Identify the section's product proof or workflow need.
2. Check existing project components, shadcn, native Tailwind, Kibo UI and Origin/Coss first.
3. Select one exact ReUI item and style.
4. Verify the item page and exact registry endpoint.
5. Record free/pro status and license key evidence.
6. Record dependencies, registry dependencies and adaptation.
7. Define keyboard/focus QA, mobile behavior and fallback.
8. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/38-reui-selection.md
```

The file must record exact item, style, source URL, registry URL, install command, free/pro status, license key status, dependencies, registry dependencies, adaptation, mobile behavior, keyboard/focus QA, decision, owner `task-###`, `chg-###`, risk and QA evidence.
