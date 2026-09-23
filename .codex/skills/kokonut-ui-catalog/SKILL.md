---
name: kokonut-ui-catalog
description: Select verified Kokonut UI shadcn registry components for landing-page plans. Use when a landing considers Kokonut UI, animated buttons, AI inputs, background effects, cards, navigation, file upload, text effects, bento/product cards, or when filling `40-kokonut-ui-selection.md`; requires exact docs page, registry item, install command, MIT/pro access status, dependency impact, reduced-motion fallback, mobile behavior, task ID, change ID, and QA before install or copy.
---

# Kokonut UI Catalog

Use this skill when Kokonut UI is considered for a landing page, especially for a small exact shadcn-compatible component such as AI prompt/search, file upload, bento/cards, animated buttons, background hero details, text effects or navigation details.

## Required Reading

Read before selecting any item:

```text
план разработки топового лендинга/44-kokonut-ui-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

If Kokonut UI is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/40-kokonut-ui-selection.md
```

## Install Model

Kokonut UI public components use a shadcn registry:

```bash
npx shadcn@latest add @kokonutui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://kokonutui.com/r/<name>.json
```

Do not assume Kokonut UI Pro items are available. Treat `kokonutui.pro` templates/components as reference-only unless access and license are explicit.

## Best Landing Uses

- AI/agent UI details: `ai-prompt`, `ai-input-search`, `ai-loading`, `ai-text-loading`, `ai-voice`.
- CTA tactility: `particle-button`, `gradient-button`, `hold-button`, `attract-button`, `command-button`, `slide-text-button`.
- Product proof cards: `bento-grid`, `apple-activity-card`, `currency-transfer`, `carousel-cards`, `spotlight-cards`.
- Navigation details: `morphic-navbar`, `toolbar`, `smooth-tab`, `profile-dropdown`, `action-search-bar`, `smooth-drawer`.
- Form/product input: `file-upload`, `avatar-picker`, `team-selector`.
- Hero/background/text accents: `shape-hero`, `beams-background`, `background-paths`, `flow-field`, `shimmer-text`, `dynamic-text`, `sliced-text`.

## Gates

Reject or mark reference-only when:

- the item is from Kokonut UI Pro and access/license is not explicit.
- the exact docs page, registry URL and install command are not recorded.
- the same effect is already covered by native CSS, Motion Primitives, Animate UI, Magic UI, React Bits, Cult UI, ReUI or existing local components.
- the item adds `motion` for a decorative effect with no section purpose.
- liquid glass, tweet cards, loaders, fake AI or playful effects distract from the offer.

## Selection Rules

1. Start from section job, motion recipe and component plan.
2. Prefer exact public registry items only; do not bulk-install.
3. Record docs page, registry item, registry URL, install command, license/pro status, dependencies, registry dependencies, visible purpose, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID and QA in `40-kokonut-ui-selection.md`.
4. Promote accepted items into component plan, motion recipe, implementation task graph and change traceability.
5. Keep rejected tempting items in the rejection table.

## Acceptance

Use Kokonut UI when a small, polished, shadcn-compatible component is faster and clearer than building from scratch. It should not replace the landing's visual system.
