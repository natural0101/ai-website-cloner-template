---
name: kibo-ui-catalog
description: Select, adapt, or review verified Kibo UI shadcn-compatible components for landing-page plans and product UI previews. Use when a landing needs exact product-interface details such as code blocks, snippets, sandboxes, tables, kanban, gantt, tree, calendar, combobox, dropzone, editor, image tools, media player, rating, tags, status, banners, proof widgets, dependency budgeting, live endpoint validation, or when filling `34-micro-component-selection.md`.
---

# Kibo UI Catalog

## Overview

Use Kibo UI as a product-interface detail source, not as decoration. It is strongest when a landing needs a credible app surface, workflow preview, form/detail control, code/media section, proof widget, or data view.

## Required Reading

Read:

- `план разработки топового лендинга/38-micro-component-source-map.md`
- `план разработки топового лендинга/11-component-source-registry.md`
- active project `34-micro-component-selection.md`, `08-component-and-asset-plan.md`, and `18-section-storyboard-canvas.md` if present

## Verified Model

- Site: `https://www.kibo-ui.com/`
- Registry index: `https://www.kibo-ui.com/r/registry.json`
- Item endpoint: `https://www.kibo-ui.com/r/<name>.json`
- GitHub: `https://github.com/shadcnblocks/kibo`
- License: MIT via repo metadata and `license.md`
- Install: `npx shadcn@latest add https://www.kibo-ui.com/r/<name>.json`

Root `/registry.json` is invalid and returns 404. Generic guesses such as `accordion`, `button`, and `ai-input` return package lookup errors. Use exact package names only.

## Selection Pool

Cleanly parsed live item endpoints during the latest check:

```text
announcement, avatar-stack, banner, calendar, choicebox, code-block, color-picker, combobox, comparison, contribution-graph, credit-card, cursor, deck, dialog-stack, dropzone, glimpse, image-crop, image-zoom, kanban, list, marquee, mini-calendar, pill, qr-code, rating, relative-time, sandbox, snippet, spinner, status, table, tags, theme-switcher, ticker, tree, typography, video-player
```

Large endpoints with `HEAD 200` but live body timeout during the latest check:

```text
editor, gantt, reel
```

Use those only after a fresh exact-body fetch succeeds or after adapting directly from source with explicit dependency review.

## Best Fits

- Proof polish: `announcement`, `banner`, `avatar-stack`, `rating`, `tags`, `status`, `ticker`, `relative-time`.
- Developer/product sections: `code-block`, `snippet`, `sandbox`, `typography`.
- Forms and inputs: `combobox`, `choicebox`, `calendar`, `mini-calendar`, `dropzone`, `color-picker`, `image-crop`.
- Product UI previews: `table`, `kanban`, `tree`, `contribution-graph`, `dialog-stack`, `glimpse`.
- Media/content: `video-player`, `image-zoom`, `deck`, `credit-card`.

## Reject By Default

- `cursor` unless the whole page interaction model earns it.
- `editor`, `gantt`, and `reel` unless the live body fetch or source adaptation is verified and dependency budget is accepted.
- `calendar`, `code-block`, `table`, `kanban`, `sandbox`, `video-player`, and `color-picker` when a static screenshot or local shadcn primitive would communicate the same thing.
- Any item that introduces drag/drop, Tiptap, Shiki, Sandpack, media, table, calendar, or motion runtime solely for decoration.

## Required Gate

Before implementation, fill or update `34-micro-component-selection.md` with:

- exact Kibo item name;
- source URL and registry URL;
- install command;
- live endpoint verification result;
- dependencies and dependency budget;
- product/story purpose;
- mobile simplification;
- keyboard/focus QA for interactive components;
- reduced-motion fallback if animated;
- `task-###` and `chg-###`;
- decision: accept, adapt, reject, backlog, or reference-only.

## Dependency Awareness

Common dependency risks from the latest endpoint/package check:

- `lucide-react` appears often.
- `@radix-ui/react-use-controllable-state`, `radix-ui`, `button`, `badge`, `command`, `popover`, `select`, and other shadcn registry dependencies may be pulled in.
- Heavy items may add `@dnd-kit/*`, `jotai`, `date-fns`, `@tanstack/react-table`, `shiki`, `@shikijs/transformers`, `@codesandbox/sandpack-react`, `react-dropzone`, `react-fast-marquee`, `media-chrome`, image tools, Tiptap, `lowlight`, `fuse.js`, `tippy.js`, or `motion`.

If the dependency does not directly support the section's visible story, reject or adapt with native/local UI.
