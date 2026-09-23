---
name: landing-reference-research
description: Find and evaluate landing-page references before redesigning, then map each inspiration to concrete sections, motion, assets, and risks.
---

# Landing Reference Research

Use this skill when planning or redesigning a landing page and the work needs real inspiration, not generic taste.

## Required Inputs

- Current project brief or `landing-source-dossier.md`.
- Product category, audience, offer, and primary CTA if known.
- Any existing references from the user.

## Workflow

1. Read `план разработки топового лендинга/00-source-scouting-log.md` if it exists.
2. Read `план разработки топового лендинга/52-reference-gallery-source-map.md` before choosing reference sources.
3. Collect references in three groups:
   - 3 direct/domain references: similar product, audience, offer, or buyer anxiety.
   - 2 thematic/adjacent/analogous references: similar workflow, trust model, visual emotion, asset type, or interaction.
   - 3 visual/aesthetic references: typography, composition, image language, color, density.
   - 2 motion/component references: interaction, transition, animated component, 3D/WebGL if relevant.
4. Route sources by lane:
   - SaaS Landing Page, SaaSFrame, Landingfolio, Lapa Ninja, Land-book, Saaspo, and direct competitors for direct/domain examples.
   - Mobbin and Pageflows for product flows, onboarding, signup and checkout.
   - Recent/Godly, Siteinspire, Minimal Gallery, MaxiBestOf, Refero, HTTPSTER, Dark Mode Design, and Navbar Gallery for visual language.
   - Awwwards, Codrops, Motion Examples, and Motion docs for motion, WebGL, 3D and interaction.
   - Baymard and NN/g for CRO, form, checkout, heuristic and UX evidence.
   - Animate UI catalog, Magic UI, Motion Primitives, React Bits, Aceternity, Tailark, Coss UI, 21st.dev and other local source maps for component or effect discovery.
5. For every reference, write:
   - URL.
   - Access status: live, blocked automation, browser/manual only, premium/account gated, timeout, or sitemap-only.
   - Closeness reason: product, audience, CTA, trust model, workflow, asset type, emotion, or interaction.
   - Why it is relevant.
   - What to borrow.
   - What not to copy.
   - Which landing section it informs.
   - Risk: license, performance, brand mismatch, accessibility, over-motion.
6. Convert inspiration into implementation language:
   - layout pattern;
   - asset requirement;
   - motion purpose;
   - component source candidate;
   - QA check.

## Output

Create or update `24-thematic-reference-map.md` and `03-reference-board.md` inside the active project plan folder, or include the same sections in the final response if no folder exists.

## Quality Bar

- No moodboard without section mapping.
- No "looks cool" justification. Explain the user-facing purpose.
- No copying premium/pro assets or code without license.
- No references that contradict the product audience or trust level.
- Use references to make a decision, not to collect decoration.
