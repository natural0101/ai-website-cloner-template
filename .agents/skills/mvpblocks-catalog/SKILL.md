---
name: mvpblocks-catalog
description: Select verified MVPBlocks components, blocks, templates and text animations for landing-page plans. Use when a landing considers MVPBlocks, MVPBlocks CLI, Next.js/Tailwind/Framer Motion sections, hero/pricing/FAQ/CTA/testimonial/footer/header/bento/dashboard/chatbot blocks, or when filling `41-mvpblocks-selection.md`; requires exact docs page, exact item endpoint or CLI command, license caveat, dependency impact, adaptation, reduced-motion fallback, mobile behavior, task ID, change ID and QA before install or copy.
---

# MVPBlocks Catalog

Use this skill when MVPBlocks is considered for a landing page, especially for a section-level block, MVP template, AI/SaaS/product preview, portfolio, pricing, FAQ, CTA, header, footer, testimonial, bento grid, dashboard preview, chatbot surface, or text animation.

## Required Sources

Read these before selecting an item:

```text
план разработки топового лендинга/45-mvpblocks-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

If MVPBlocks is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/41-mvpblocks-selection.md
```

## Verified Model

MVPBlocks has a live site, sitemap, `llms.txt`, `llms-full.txt`, npm CLI, GitHub repo and 252 exact item endpoints:

```text
https://blocks.mvp-subha.me/r/<name>.json
```

The root registry indexes `https://blocks.mvp-subha.me/r/registry.json` and `https://blocks.mvp-subha.me/registry.json` returned 404. Do not cite them as install evidence.

Preferred CLI command:

```bash
npx mvpblocks add <name> --ts
```

Exact URL form, when using shadcn-style install manually:

```bash
npx shadcn@latest add https://blocks.mvp-subha.me/r/<name>.json
```

## Accept

Accept an MVPBlocks item only when:

- exact docs page and exact item endpoint are recorded;
- item solves a section job faster than native Tailwind, local components, shadcn, Animate UI, Motion Primitives, Magic UI, Tailark, shadcnblocks, ReUI, 21st.dev or Kokonut UI;
- demo copy, fake metrics, logos and screenshots are replaced with product-specific evidence;
- dependencies such as `framer-motion`, `gsap`, `recharts`, `next`, `next-themes`, `react-hook-form` or Radix packages are justified;
- mobile behavior and reduced-motion fallback are explicit;
- task ID, change ID and screenshot/video QA are planned.

## Prefer

- `hero-1`, `minimal-hero`, `gradient-hero`, `mockup-hero`, `app-hero` only as structure or reference.
- `feature-*`, `bento-grid-*`, `cta-*`, `faq-*`, `pricing-*`, `simple-pricing`, `technical-pricing`.
- `testimonials-carousel`, `testimonials-marquee`, `header-*`, `footer-*`, `logo-cloud` items.
- `animated-ai-chat`, `conversation1`, `working-chatbot`, dashboard blocks only for real product workflow proof.
- Text animation items only for short headlines, metrics or labels.

## Reject

Reject or mark reference-only when:

- only root registry indexes are available;
- item is a full visual identity replacement instead of a section aid;
- `target-cursor`, loaders, heavy dashboard/chatbot stacks, 3D/globe, GSAP text effects or Web3 hero are decorative;
- dependencies are heavier than the section job;
- item uses Next-specific imports in a non-Next target without adaptation;
- demo content would create fake claims or fake social proof.

## Output

Record exact item, docs URL, endpoint URL, command, license/access, dependencies, registry dependencies, visible purpose, adaptation, reduced-motion fallback, mobile behavior, decision, task ID, change ID, risk and QA evidence in `41-mvpblocks-selection.md`.
