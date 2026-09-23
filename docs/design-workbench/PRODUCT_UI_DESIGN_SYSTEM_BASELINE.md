# Product UI Design System Baseline

Use this as the starting design system for dashboards, editors, AI design studios, and product workbenches. Adapt to the target app's existing stack and brand.

Before applying tokens and visual style, map routes, navigation, app shell, panes, and responsive IA with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, define action transitions with `PRODUCT_UI_INTERACTION_MODEL.md`, define status language with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, and shape approval/review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.

For choosing concrete component sources, use `docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md` and `.codex/skills/product-ui-component-sourcing/SKILL.md`. For screen anatomy and component state requirements, use `PRODUCT_UI_SCREEN_RECIPES.md`, `PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, and `COMPONENT_STATE_SPEC.md`.

## Design Posture

Default feel:

- precise, calm, operational;
- high-density without clutter;
- strong selection and focus states;
- neutral surfaces with deliberate status color;
- compact controls and stable geometry;
- motion used for continuity and feedback only.

Avoid:

- marketing hero composition inside tools;
- decorative gradients behind controls;
- oversized cards for repeated operational data;
- novelty typography in sidebars, inspectors, tables, and forms.

## Token Baseline

| Token group | Default guidance |
| --- | --- |
| Radius | Pick one system: sharp `0-4px`, practical `6-8px`, or soft `10-12px`. Use it consistently. |
| Spacing | Use compact rhythm: `4, 8, 12, 16, 24, 32`. Dense panels usually live at `8/12/16`. |
| Typography | UI text `12-14px`, body `14-16px`, page headings `20-28px`. No hero-scale type inside tools. |
| Color | Neutral base, one accent family, explicit status colors for info/success/warning/error. |
| Border | Use subtle borders/dividers for structure; avoid nesting bordered cards inside bordered cards. |
| Shadow | Use only for overlays, popovers, drawers, menus, and elevated previews. |
| Motion | 120-200ms for controls, 180-260ms for state changes, 220-320ms for popovers/drawers. |
| Status copy | Short factual labels in dense controls; details live in helper text, inline alerts, tooltips, or detail panes. |
| Decision layout | Keep decision question, comparison/evidence, risk, and action zones visually connected. |

## Layout Patterns

| Pattern | Use |
| --- | --- |
| App shell | Top bar + side rail + main workspace + optional inspector/proposal panel |
| Split inspector | Canvas center, properties on right, project/layers on left |
| Master-detail | List/table left or center, detail drawer/panel right |
| Command palette | Fast navigation/actions, not a replacement for visible primary workflows |
| Drawer | Temporary review, proposal, settings, or detail panel |
| Modal | Use only for blocking confirmation or focused short form |

## Product Components

Every component should define visual states before implementation.

| Component | Required states |
| --- | --- |
| Button/icon button | default, hover, active, focus-visible, disabled, loading |
| Input/select/combobox | default, focused, filled, invalid, disabled, pending |
| Table/list row | default, hover, selected, focused, disabled, loading skeleton |
| Tabs/segmented control | default, active, hover, focus, disabled |
| Tree/layer item | default, expanded, selected, warning, locked, hidden |
| Inspector field | inherited, overridden, invalid, locked, reset available |
| Toast/alert | info, success, warning, error, action available |
| Card/panel | default, selected, warning/error, loading, empty |
| Tooltip/popover | open/closed, keyboard accessible, reduced motion safe |

For any reusable component, fill `COMPONENT_STATE_SPEC.md` before implementation or external sourcing.

Status badges, alerts, toasts, empty states, and disabled controls must follow `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`: name the object, reason, next action, and source/evidence when relevant.

## Data And Proof Rules

- Use organic sample data only when the UI needs examples, and label it sample/demo.
- Never present generated screenshots, mock metrics, fake logos, fake reviews, or fake agent status as real.
- If a dashboard needs metrics but no source exists, show "No data connected" or "Sample data" rather than invented proof.
- If a design editor shows imported assets, include source paths or registry rows when available.

## Accessibility Baseline

- All controls reachable by keyboard.
- Visible focus ring on every interactive element.
- 40x40px minimum hit area for touch where possible.
- Form fields have labels and error descriptions.
- Icon-only buttons have accessible names and tooltips.
- Contrast passes WCAG AA for body text and controls.
- Reduced motion keeps final content visible.

## Verification Baseline

Before handoff:

- Run the target project's typecheck/build/tests when available.
- Capture desktop and mobile screenshots for changed surfaces when possible.
- Check no overlap/clipping at narrow and wide widths.
- Verify empty/loading/error states are reachable or represented.
- Record why any external component/library was added and what existing local option was checked first.
- Report what was actually verified and what remains unverified.
