---
name: twenty-first-dev-catalog
description: Select verified 21st.dev community components for landing-page plans. Use when a landing needs discovery from 21st.dev, community React components, hero/background/shader/AI-chat/CTA/pricing/features inspiration, 21st CLI install commands, CDN registry JSON checks, or when filling `39-twenty-first-dev-selection.md`; requires exact component page, author/item slug, command, registry URL if present, license, dependency impact, access gate, adaptation, fallback, mobile, QA, task ID, and change ID before install or copy.
---

# 21st.dev Catalog

Use this skill when 21st.dev is considered for a landing page, especially for community-made hero sections, shader/background effects, AI-chat surfaces, CTA/pricing/features sections, product widgets, app-like micro UI, or visual inspiration from a large component marketplace.

## Required Reading

Read before selecting any item:

```text
план разработки топового лендинга/43-21st-dev-source-map.md
план разработки топового лендинга/11-component-source-registry.md
```

If 21st.dev is used or seriously considered, fill:

```text
план разработки топового лендинга/projects/<slug>/39-twenty-first-dev-selection.md
```

## Source Model

21st.dev is a discovery and community registry surface, not a default design system. Treat it as reference-first. Install only one exact component when its visible effect or structure is chosen deliberately.

Common install command from component pages:

```bash
npx @21st-dev/cli@beta add <author>/<component>
```

Some component pages expose CDN registry JSON such as:

```text
https://cdn.21st.dev/<author>/<component>/registry.<stamp>.json
```

Use the CDN registry URL as install evidence only after verifying it returns 200 JSON. If a page has no extractable registry URL, record the item as reference-only unless a browser capture proves the install command and files.

## Best Landing Uses

- Reference mining: find directions for hero, CTA, pricing, feature, AI, shader, background, text and product-widget moments.
- Hero and visual moments: use only if the idea maps to the landing story and does not replace the offer.
- Product proof widgets: tables, calendars, charts, avatars, sparklines, upload/file, editor-like or AI-chat UI.
- High-impact effects: shaders, WebGL, halftone, iridescent, ASCII, video/image treatments only with performance QA.
- Community snippets: copy or install only after license, dependency and local token adaptation are explicit.

## Gates

Reject or mark reference-only when:

- no exact component page is recorded.
- no command or live CDN registry JSON can be verified.
- license is missing, unclear or incompatible.
- heavy dependencies such as `three`, WebGL, shader libraries, HeroUI, chart packages or icon libraries are added for decoration.
- the item duplicates an existing shadcn, Animate UI, Motion Primitives, Magic UI, React Bits, ReUI or custom component with no visible improvement.
- essential content is hidden inside hover, autoplay, canvas or pointer-only interactions.

## Selection Rules

1. Start from the section job and reference board.
2. Search 21st.dev by exact category or tag, not broadly.
3. Prefer using 21st.dev as inspiration unless the exact component is worth the dependency and adaptation cost.
4. Record component page, author/item slug, command, CDN registry URL if present, registry status, license, dependencies, adaptation, fallback, mobile behavior, QA, task ID and change ID in `39-twenty-first-dev-selection.md`.
5. Promote accepted items into component plan, motion recipe, implementation task graph and change traceability.
6. Keep rejected tempting items in the rejection table to prevent later shiny installs.

## Acceptance

Use 21st.dev when it gives a concrete visual or interaction idea that improves the landing's story. Do not use it as a broad component dumping ground.
