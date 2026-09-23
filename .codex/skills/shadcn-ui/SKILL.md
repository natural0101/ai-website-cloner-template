---
name: shadcn-ui
description: Use when adding, reviewing, or refactoring shadcn/ui components in React, Next.js, TypeScript, Tailwind CSS v4 projects, especially product UI, dashboards, editors, forms, app shells, dialogs, drawers, command menus, tables, and inspectors. Prefer official shadcn patterns, Radix primitives, accessible states, and project-local conventions.
metadata:
  source_url: "https://www.aura.build/skills/b8543dfb-058a-4fff-b84c-9a139d852005/shadcn"
  docs_url: "https://ui.shadcn.com/docs/installation"
---

# shadcn/ui Skill

Use this skill when the task touches shadcn/ui components, Radix primitives, app UI primitives, Tailwind component styling, or component installation.

For product UI or AI design studio work, read:

```text
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
```

## Workflow

1. Inspect the existing project components before adding anything. Prefer local wrappers in `src/components/ui` and the project's `cn()` helper.
2. Read the installed component API or local source before using props from memory.
3. Keep components accessible: labels, focus-visible styles, keyboard behavior, ARIA only when needed, and disabled/loading states.
4. Match the project's Tailwind v4 token approach. Avoid inline styles unless the existing component requires CSS variables.
5. Do not create a custom primitive when a shadcn/Radix primitive already fits.
6. For dashboards/editors, define selected, pending, empty, loading, error, disabled, focus-visible, and responsive states before styling.
7. For visual work, verify desktop and mobile states with screenshots before calling it done.

## Next.js Notes

- Add `use client` only for interactive components.
- Keep server components server-side when possible.
- Avoid importing browser-only shadcn primitives into server-only code.

## Quality Bar

A component is not finished until hover, focus, disabled, loading, error, empty, and responsive states are considered. If the component appears in repeated UI, make spacing and sizing stable so labels or icons do not resize the layout.

For toolbars, inspectors, trees, layer rows, proposal panels, and data lists, selected and pending states are mandatory.
