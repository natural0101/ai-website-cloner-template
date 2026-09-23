---
name: ui-refactor-principles
description: Use when reviewing or improving a UI that feels generic, noisy, flat, cramped, visually weak, unclear, or weak as a product surface. Applies a practical UI refactor checklist for dashboards, editors, app shells, hierarchy, typography, spacing, color, buttons, clutter, empty states, shadows, contrast, and grouping without copying any proprietary source text.
metadata:
  reviewed_sources:
    - "https://github.com/gnurio/refactoring-ui-plugin"
  note: "Original local synthesis. Do not copy restricted repository text."
---

# UI Refactor Principles

Use this skill when the interface already exists but does not feel deliberate, premium, readable, or easy to scan.

For product UI, dashboards, AI design studios, canvas editors, admin panels, or SaaS apps, first read:

```text
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
```

If the product resembles ForgeStudio or another AI design workbench, also read:

```text
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
```

## Review Order

1. Establish the attention path.
   - Name what should be seen first, second, and third.
   - Reduce anything that competes with the primary action or core content.
   - Increase contrast through size, weight, placement, color, or spacing before adding decoration.

2. Fix typography.
   - Use a small, intentional type scale instead of many arbitrary sizes.
   - Make labels, body text, section headings, and hero text clearly different jobs.
   - Use muted text for secondary information, not low-opacity unreadable text.
   - Check line length, line height, wrapping, and mobile clipping.

3. Normalize spacing.
   - Group related elements tightly and separate unrelated groups more strongly.
   - Prefer a consistent spacing rhythm.
   - If the layout feels cramped, remove elements before shrinking everything.

4. Tune color.
   - Separate neutral surfaces, primary actions, accents, status colors, and destructive states.
   - Avoid using strong accent color on too many elements.
   - Check contrast on text, icons, borders, disabled states, and translucent overlays.

5. Clarify button hierarchy.
   - One obvious primary action per region.
   - Secondary actions should be visible but quieter.
   - Tertiary actions can be links, icon buttons, or menus.
   - Every interactive element needs hover, focus-visible, disabled, and loading states when relevant.

6. Remove visual clutter.
   - Delete unnecessary borders, backgrounds, dividers, badges, shadows, icons, and labels.
   - If everything is boxed, nothing is grouped.
   - Use whitespace, alignment, and typography before adding another container.

7. Design empty, loading, and error states.
   - Empty states should explain the situation and provide a next action.
   - Loading states should preserve layout size.
   - Error states should identify the problem and recovery path.

8. Use depth functionally.
   - Shadows and elevation should communicate layering, interactivity, or focus.
   - Avoid decorative haze around ordinary cards.
   - Use consistent shadow direction, softness, and surface contrast.

9. Check grouping and scan paths.
   - Related labels, controls, values, and helper text should read as one unit.
   - Repeated items should have stable dimensions.
   - Dense tools need predictable alignment more than expressive composition.
   - Product workbenches need visible selection, task/proposal status, and recovery paths before decorative polish.

## Output Format

When reviewing, return:

1. Top three issues blocking quality.
2. Concrete fixes with component or section references.
3. A short polish checklist for desktop and mobile.

When implementing, change the smallest surface that improves the hierarchy first, then verify with screenshots.
