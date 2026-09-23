# Visual Direction Style Tiles

Дата обновления: 2026-07-03.

Style tile нужен между reference scoring и implementation plan. Он фиксирует, как лендинг будет выглядеть до кода: typography, color, spacing, radius, surface, imagery, icon style, section composition, motion feel and do-not-copy rules.

## Sources

- https://styletil.es/
- https://www.figma.com/blog/design-systems-101-what-is-a-design-system/
- https://www.figma.com/design-systems/
- https://m3.material.io/foundations
- https://atlassian.design/foundations
- https://atlassian.design/tokens/
- https://carbondesignsystem.com/elements/2x-grid/overview/

## Style Tile Purpose

A style tile is not a moodboard and not a pixel-perfect comp. It is a decision sheet that says:

- what the interface should feel like;
- which visual tokens create that feeling;
- which references justify the choices;
- how sections should vary while staying coherent;
- which visual defaults are banned for this project.

## Required Inputs

- `landing-source-dossier.md`
- `25-brand-dna-map.md`
- `03-reference-board.md`
- `15-reference-scorecard.md`
- `04-visual-benchmark.md`
- product category, audience, offer, CTA
- existing brand assets or current colors/type if preserving

## Visual Read

Write one precise sentence:

```text
Reading this as: <landing type> for <audience>, with a <visual language>, leaning toward <system/aesthetic family>, because <evidence>.
```

Bad: "modern premium SaaS".

Good: "Reading this as: trust-first AI operations landing for technical buyers, with a precise industrial interface language, leaning toward dense neutral surfaces, crisp proof panels, restrained green status accents, and low-motion product reveals."

## Token Decisions

| Layer | Required decision | Notes |
| --- | --- | --- |
| Typography | display font, body font, mono font, scale, line height | Avoid generic font choice without reason |
| Color | background, surface, text, muted text, accent, semantic colors | One accent system unless brand requires more |
| Spacing | section padding, grid gap, card gap, text rhythm | Must support mobile |
| Radius | buttons, cards, media, inputs | Define a rule, not random radii |
| Surface | flat, bordered, glass, inset, elevated, editorial | Match product trust level |
| Shadow | none, ambient, sharp, colored, inset | No generic black shadow on light UI |
| Borders | hairline, contrast, dividers, none | Avoid border soup |
| Icons | family, stroke/fill, size, use cases | One icon family |
| Images/assets | screenshot, photo, 3D, diagram, illustration | Real proof beats decoration |
| Motion feel | calm, tactile, kinetic, cinematic, static | Must map to `16-motion-recipe-selection.md` |

## Brand DNA Gate

Before choosing new tokens, read `25-brand-dna-map.md`.

Every style tile must state:

- which current brand tokens are preserved;
- which tokens evolve and how;
- which weak elements are removed;
- which new elements are introduced and why;
- which content/routes/forms/legal/SEO are protected.

If a reference conflicts with a protected item, the protected item wins unless the user explicitly approves the change.

## Style Directions

Choose one primary direction and optionally one rejected alternate.

### Precision SaaS

- Visual: clean neutral background, sharp proof panels, small status accents.
- Typography: geometric or grotesk sans, readable body.
- Assets: product screenshot, live UI fragment, real metrics.
- Motion: calm reveal, tabs, state transitions.
- Avoid: AI-purple mesh, fake dashboard, six identical cards.

### Product-Led App

- Visual: interface-first, flow rail, screenshot crops, active states.
- Typography: utilitarian but polished.
- Assets: real product screen sequence.
- Motion: active step preview, subtle feedback.
- Avoid: decorative abstract hero that hides product.

### Premium Consumer

- Visual: object/photo-led, strong material treatment, generous whitespace.
- Typography: display sans by default; serif only with brand reason.
- Assets: product/lifestyle photography or generated product image.
- Motion: product reveal, tactile CTA, image hover.
- Avoid: beige/brass/espresso default unless brand explicitly requires it.

### Editorial Agency

- Visual: asymmetric grid, expressive type, portfolio/reference imagery.
- Typography: high-contrast display system.
- Assets: case visuals, texture, composition.
- Motion: kinetic type or scroll stack if story needs it.
- Avoid: unreadable type tricks and decorative cursor by default.

### Trust-First Service

- Visual: clear hierarchy, stable layout, accessible contrast, restrained color.
- Typography: readable sans, generous line height.
- Assets: real process diagram, proof, certifications if real.
- Motion: mostly feedback/state, minimal reveals.
- Avoid: heavy parallax, vague illustrations, low-contrast decoration.

### Technical/Developer Tool

- Visual: docs/product hybrid, code samples, CLI/API proof, precise grids.
- Typography: sans plus mono, compact but readable.
- Assets: code tabs, diagrams, terminal or real product UI.
- Motion: code tab transition, copy feedback, measured reveals.
- Avoid: fake terminal commands and noisy hacker neon.

## Section Visual Rules

For each section, define:

- composition family: split, stack, bento, rail, table, timeline, editorial, full-bleed visual;
- visual density: airy, balanced, dense;
- asset type and crop;
- surface treatment;
- typography role;
- accent use;
- motion feel;
- mobile transformation.

No two adjacent sections should feel like the same card layout unless repetition is the point.

## Anti-Slop Checks

- No "modern premium" without tokens.
- No AI-purple/dark mesh unless the brand earns it.
- No beige/brass premium-consumer default.
- No three equal cards as the default feature section.
- No fake screenshots or fake proof.
- No mixed radius systems.
- No mixed icon families.
- No section style flip without reason.
- No hero without real visual strategy.
- No visual reference used outside its scored section.

## Output

Fill `projects/<slug>/17-visual-style-tile.md`, then reflect the decisions in:

- `05-visual-direction.md`
- `06-section-by-section-upgrade-plan.md`
- `08-component-and-asset-plan.md`
- `13-section-pattern-selection.md`
- `16-motion-recipe-selection.md`
- `10-quality-gate.md`
