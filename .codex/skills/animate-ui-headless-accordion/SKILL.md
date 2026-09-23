---
name: animate-ui-headless-accordion
description: Use when adding, adapting, or reviewing Animate UI's Headless Accordion pattern in a React, Next.js, Tailwind, shadcn-style codebase. Covers registry install, dependency chain, API, motion behavior, SEO keepRendered, accessibility, and license caveats.
keywords: animate-ui, accordion, disclosure, headless-ui, motion, shadcn, react, nextjs, tailwind
metadata:
  docs_url: "https://animate-ui.com/docs/components/headless/accordion"
  registry_url: "https://animate-ui.com/r/components-headless-accordion.json"
  source_repo: "https://github.com/imskyleen/animate-ui"
  license: "MIT + Commons Clause"
---

# Animate UI Headless Accordion

Use this skill when the task needs a polished animated accordion/disclosure UI.

## What To Install

Main component:

```bash
npx shadcn@latest add @animate-ui/components-headless-accordion
```

Registry chain:

- `@animate-ui/components-headless-accordion`
- `@animate-ui/primitives-headless-disclosure`
- `@animate-ui/lib-get-strict-context`

Runtime dependencies:

- `lucide-react`
- `motion`
- `@headlessui/react`

## What The Component Provides

Exports:

- `Accordion`
- `AccordionItem`
- `AccordionButton`
- `AccordionPanel`

Usage shape:

```tsx
<Accordion>
  <AccordionItem>
    <AccordionButton>Accordion Item</AccordionButton>
    <AccordionPanel>
      <div>Accordion Content</div>
    </AccordionPanel>
  </AccordionItem>
</Accordion>
```

Important props:

- `AccordionButton.showArrow?: boolean`, default `true`
- `AccordionPanel.transition?: Transition`, default `{ type: 'spring', stiffness: 150, damping: 22 }`
- `AccordionPanel.keepRendered?: boolean`, default `false`
- `keepRendered` keeps content mounted, useful for SEO or expensive content that should not remount.

## Implementation Notes

Animate UI's accordion is a styled wrapper around its Headless Disclosure primitive, which wraps `@headlessui/react` Disclosure.

The panel animation uses `motion/react` with:

- height `0` to `auto`
- opacity `0` to `1`
- `y` offset
- a mask gradient controlled by `--mask-stop`
- `AnimatePresence` for exit animation when `keepRendered` is false

When adapting into this project:

1. Replace registry aliases with project aliases:
   - `@/registry/primitives/headless/disclosure` -> local disclosure path
   - `@/registry/lib/get-strict-context` -> local helper path
   - `@workspace/ui/lib/utils` -> project `cn()` helper, usually `@/lib/utils`
2. Keep `use client` on the disclosure primitive.
3. Keep Headless UI semantics; do not replace buttons with divs.
4. Preserve focus-visible states and disabled states.
5. Check mobile width, text wrapping, and reduced motion expectations.

## License Caveat

Animate UI is MIT + Commons Clause. It can be used and adapted inside an application, website, or product. Do not redistribute or sell the components themselves as a standalone component library or bundle.

## Sources

- Docs: https://animate-ui.com/docs/components/headless/accordion
- Registry: https://animate-ui.com/r/components-headless-accordion.json
- Source: https://github.com/imskyleen/animate-ui
