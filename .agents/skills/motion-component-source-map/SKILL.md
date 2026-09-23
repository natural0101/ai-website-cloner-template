---
name: motion-component-source-map
description: Choose the right component or motion source for product UI, dashboards, editors, websites, and landing-page interactions without bloating the app or mixing incompatible animation systems.
---

# Motion Component Source Map

Use this skill when a product UI, dashboard, editor, website, landing page, or app surface needs animated UI, component sourcing, scroll effects, visual polish, or 3D/WebGL.

For product UI component/library choices, first read:

```text
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
.codex/skills/product-ui-component-sourcing/SKILL.md
```

## First Checks

1. Read `package.json`.
2. Identify existing UI and animation stack.
3. Prefer existing stack before adding dependencies.
4. Never assume a package is installed.
5. Do not mix Motion, GSAP, and Three.js inside the same component tree unless there is a clear boundary.

## Source Selection

### Existing Components

Use first when the project already has a component with the right semantics.

### Tailwind / Native CSS

Use for layout, typography, simple hover states, and non-interactive visual polish.

### shadcn/ui

Use for owned React primitives when the project already uses shadcn or wants editable code.

### Animate UI

Use for animated/headless/radix/base components. Read `docs/research/animate-ui-catalog.md` before selecting.

Best for: accordion, disclosure, tabs, primitives, animated UI details.

### Motion Primitives

Use for focused motion components that should feel polished without large block templates.

Best for: text scramble, transition panels, animated tabs, lightweight interaction states.

### Magic UI

Use when a marketing surface, launch page, or website section needs a strong animated effect.

Best for: hero/background/text/logo effects. Apply sparingly.

### React Bits

Use as an idea catalog for animated snippets. Verify license and dependencies before copying.

Best for: experimental text/image/background effects.

### Aceternity UI

Use as block inspiration or a quick starting point for a section.

Best for: hero sections, bento grids, parallax blocks, glow/glare effects.

Risk: recognizable patterns. Adapt heavily.

### Tailark

Use for marketing block structure and page composition.

Best for: hero, pricing, FAQ, logo cloud, testimonials, bento, CTA.

Risk: respect premium/pro access and license.

### Coss UI / Base UI

Use for accessible primitives, forms, overlays, menus, inputs, drawers, and command palettes.

### GSAP

Use only for real scroll choreography: pinned sections, scrubbed horizontal pan, sticky stack.

Must include cleanup and reduced-motion fallback.

### Three.js / WebGL / Blender

Use only when 3D is central to the product story or hero. Keep the scene full-bleed or meaningfully integrated. Verify it renders and is not blank.

## Output Format

For every chosen component/effect:

- Need:
- Candidate source:
- Why this source:
- Dependency impact:
- Files affected:
- Reduced-motion plan:
- Mobile plan:
- Risk:
- Verification:

## Hard No

- No component because "it looks cool".
- No random package install.
- No duplicate animation libraries for the same effect.
- No heavy scroll/3D below a vague product claim.
- No effects that harm readability, contrast, or conversion.
