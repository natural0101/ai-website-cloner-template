---
name: reui-catalog
description: Select verified ReUI shadcn registry items for landing-page plans. Use when a landing needs app UI details, forms, data grids, filters, upload/file UI, frames, badges, accordions, alerts, tables, dashboards, admin/product previews, or when filling `38-reui-selection.md`; requires exact item, style, live registry URL, free/pro access check, license key status, dependency impact, adaptation, mobile, accessibility, task ID, and change ID before install or copy.
---

# ReUI Catalog

Use this skill when ReUI is considered for a landing page, especially for product/app-preview UI, data-heavy sections, forms, admin dashboards, feature panels, filters, tables, timelines, alerts, file upload, or realistic SaaS interface details.

## Required Reading

Read before choosing any item:

```text
план разработки топового лендинга/42-reui-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

If ReUI is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/38-reui-selection.md
```

## Registry Model

ReUI uses a shadcn registry with style variants:

```json
{
  "registries": {
    "@reui": "https://reui.io/r/{style}/{name}.json"
  }
}
```

Recommended default for this project is `radix-nova` unless the plan explicitly chooses `base-nova`.

Free component examples use `c-*` names:

```bash
npx shadcn@latest add @reui/c-alert-1
```

Exact URL form:

```bash
npx shadcn@latest add https://reui.io/r/radix-nova/c-alert-1.json
```

Premium blocks, icons, templates and some registry entries require `REUI_LICENSE_KEY` and authenticated registry config. Do not use them unless access is explicit.

## Best Landing Defaults

- SaaS/app proof: `data-grid`, `c-data-grid-*`, `frame`, `c-frame-*`, `table`, `filters`, `timeline`.
- Forms and conversion flows: `field`, `input`, `input-group`, `select`, `combobox`, `date-selector`, `phone-input`, `file-upload`.
- Trust/status: `alert`, `c-alert-*`, `badge`, `rating`, `progress`, `stepper`.
- Navigation/detail: `accordion`, `tabs`, `popover`, `tooltip`, `drawer`, `sheet`.
- Product preview realism: `kanban`, `tree`, `sortable`, `scrollspy` only when the product actually has those workflows.

## Access Gates

Reject or mark reference-only when:

- root `registry.json` or style registry returns 401.
- exact item endpoint returns 401 or 403 and no license key/access is available.
- the item is a premium block, icon or template and the plan has no explicit ReUI license evidence.
- the component duplicates local shadcn UI without visible improvement.
- the section is a simple marketing section where native CSS, shadcn or existing components are enough.

## Selection Rules

1. Start with the section job and product evidence.
2. Prefer existing project components, shadcn, native Tailwind, Kibo/Origin/Coss or simpler sources first.
3. Choose exact item and style: usually `radix-nova` + `c-*` free component example.
4. Verify the exact live registry URL before install.
5. Record free/pro access, license key status, dependencies, registry dependencies, adaptation, mobile behavior, keyboard/focus QA, task ID, change ID and QA in `38-reui-selection.md`.
6. Keep the visual system from the landing plan. ReUI should provide realistic UI structure, not replace brand direction.

## Acceptance

Use ReUI when it makes a product interface or operational workflow feel real and credible. If the goal is only a generic landing block, use Tailark, shadcnblocks, native layout or custom composition instead.
