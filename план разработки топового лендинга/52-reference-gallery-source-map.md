# Reference Gallery Source Map

Дата проверки: 2026-07-03.

Этот файл нужен до `24-thematic-reference-map.md`. Он отвечает на вопрос: где искать reference, какой роли он служит, как учитывать access caveat, и как не превратить план лендинга в случайный moodboard.

## Core Rule

Reference source is accepted only when it can map to a concrete decision:

- section structure;
- offer or proof pattern;
- product flow;
- visual language;
- asset treatment;
- motion pattern;
- component/source candidate;
- anti-reference rule.

If the reference only looks cool and has no closeness reason, reject it.

## Source Routing

| Need | Primary sources | Secondary sources | Output file |
| --- | --- | --- | --- |
| Direct/domain landing examples | SaaS Landing Page, SaaSFrame, Landingfolio, Lapa Ninja, Land-book | Saaspo, direct competitors from search | `24-thematic-reference-map.md`, `03-reference-board.md` |
| SaaS section structure and pricing/proof | SaaSFrame, SaaS Landing Page, Landingfolio | Tailark, shadcnblocks, MVPBlocks as component references | `03-reference-board.md`, `15-reference-scorecard.md` |
| Product flow, onboarding, signup, checkout | Mobbin, Pageflows | Baymard and NN/g for evidence | `24-thematic-reference-map.md`, `22-inspiration-synthesis.md` |
| Fresh visual language | Recent/Godly, Siteinspire, Minimal Gallery, MaxiBestOf, HTTPSTER, Refero | Land-book, Lapa Ninja | `03-reference-board.md`, `17-visual-style-tile.md` |
| Dark or niche visual language | Dark Mode Design, HTTPSTER, Refero | Awwwards, Minimal Gallery | `17-visual-style-tile.md` |
| Navbar/header ideas | Navbar Gallery, direct competitors | shadcnblocks, Tailark, Intent UI | `18-section-storyboard-canvas.md` |
| Motion, WebGL, 3D, interaction | Awwwards, Codrops, Motion Examples, Motion docs | Recent/Godly | `26-motion-reference-map.md`, `16-motion-recipe-selection.md` |
| CRO, UX, heuristic evidence | Baymard, NN/g | product analytics from dossier | `02-copy-and-offer-audit.md`, `10-quality-gate.md` |
| Anti-reference | Any generic competitor or gallery page | crowded category examples | `24-thematic-reference-map.md`, `21-plan-self-review.md` |

## Checked Sources

| Source | URL | Check result | Use | Caveat |
| --- | --- | --- | --- | --- |
| Land-book | https://www.land-book.com/ | automation `403`; sitemap `403` | filtered landing examples, industry/style/aesthetic scan | browser/manual source only; do not rely on scripted crawl |
| Lapa Ninja | https://www.lapa.ninja/ | homepage automation `403`; sitemap `200` | landing categories, SaaS, AI, 3D, bento, typography patterns | use browser or sitemap-backed URLs; record access status |
| Recent/Godly | https://godly.website/ | `200`, redirects to `http://recent.design/?ref=godly` | fresh visual language, typography, editorial/product mood | use for art direction, not conversion structure by default |
| Recent | https://recent.design/ | `200` | fresh web/product visual language | score by closeness, not trendiness |
| Awwwards | https://www.awwwards.com/ | homepage `200`; sitemap `404` | motion, WebGL, 3D, high-interaction art direction | high performance/accessibility risk; do not copy heavy effects blindly |
| Codrops | https://tympanus.net/codrops/ | `200` | interaction demos, scroll effects, WebGL ideas | implementation must be simplified and tied to a section purpose |
| Motion Examples | https://examples.motion.dev/react | `200`, redirects to Motion examples | Motion reference patterns | use as implementation reference with reduced-motion fallback |
| Motion docs | https://motion.dev/docs/react | `200` | official API and accessibility behavior | use for implementation proof, not visual inspiration alone |
| Mobbin | https://mobbin.com/ | homepage `200`; sitemap `200` | product flows, onboarding, signup, mobile/app screenshots | premium/account material is reference-only; do not copy proprietary screens |
| Pageflows | https://pageflows.com/ | homepage `200`; sitemap `200` | product flows, checkout, signup, onboarding recordings/screens | account/premium caveat; record what is visible and accessible |
| SaaSFrame | https://saasframe.io/ | `200`, redirects to `https://www.saasframe.io/`; sitemap/RSS `200` | SaaS landing sections, pricing, proof, integration patterns | reference only; do not clone competitor claims or proof |
| SaaS Landing Page | https://saaslandingpage.com/ | homepage `200`; sitemap index `200` | SaaS landing examples, section order, copy/proof pattern | score against current offer, not generic SaaS aesthetics |
| Saaspo | https://saaspo.com/ | automation `403` | SaaS examples and visual inspiration | browser/manual source only |
| Landingfolio | https://www.landingfolio.com/ | homepage `200`; sitemap `200` | landing page and section inspiration | some entries are reference/gallery pages; verify original site URL |
| One Page Love | https://www.onepagelove.com/ | automation `525` | one-page landing ideas if accessible in browser | not reliable for automation; do not require it in checks |
| Siteinspire | https://www.siteinspire.com/ | automation `429` | editorial, portfolio and brand-led web design | browser/manual source; rate limited |
| Minimal Gallery | https://minimal.gallery/ | `200` | restrained, minimal visual direction | can over-flatten SaaS/product proof if copied directly |
| MaxiBestOf | https://www.maxibestof.one/ | automation `403` | curated high-quality visual direction | browser/manual source only |
| Refero | https://refero.design/ | `200` | UI/product/interface inspiration | use for UI treatment and flows, not as proof claims |
| HTTPSTER | https://httpster.net/ | `200` | broad web design inspiration | score for closeness; avoid random agency aesthetics |
| Dark Mode Design | https://www.darkmodedesign.com/ | `200` | dark-mode references | use only when brand and contrast needs support dark direction |
| Navbar Gallery | https://www.navbar.gallery/ | `200` | header/navigation reference patterns | nav must match current IA and CTA, not gallery novelty |
| Baymard | https://baymard.com/ | `200` | ecommerce, forms, checkout, UX evidence | evidence source, not visual style source |
| NN/g | https://www.nngroup.com/ | `200` | heuristics, benchmarking, usability evidence | cite for UX rationale; do not use as aesthetic reference |

## Required Fields Per Candidate

Every candidate recorded from these sources must include:

- source URL and access status;
- lane: direct/domain, adjacent/theme, workflow/flow, visual language, motion/component, evidence, anti-reference;
- closeness reason: product, audience, CTA, trust model, workflow, asset type, emotion, interaction, mobile constraint or risk pattern;
- section mapping;
- what to borrow;
- what to transform;
- what not to copy;
- risk: license, premium access, performance, accessibility, brand mismatch, fake proof, over-motion;
- screenshot evidence or reason screenshot is unavailable.

## Access Rules

- `403`, `429`, `525` or timeout is an access caveat, not proof that the source is useless.
- If the source is browser/manual only, record that in `evidence/reference-manifest.md`.
- If the source is premium/account-gated, use it only as reference and write the access status.
- If an original site URL is visible from a gallery entry, prefer the original site for final reference evidence.
- Never copy proprietary screenshots, claims, logos, testimonials, pricing tables, or customer proof.

## Promotion Rules

1. Collect raw candidates in `24-thematic-reference-map.md`.
2. Promote only section-useful candidates into `03-reference-board.md`.
3. Score promoted references in `15-reference-scorecard.md`.
4. Translate accepted references in `22-inspiration-synthesis.md`.
5. Motion candidates must also go through `26-motion-reference-map.md`.
6. Evidence or CRO candidates must support a specific copy, form, pricing, trust or flow decision.

## Rejection Rules

Reject a source candidate when:

- it has no closeness reason;
- it has no concrete section use;
- it would force fake proof or copied screenshots;
- it pushes the page toward generic SaaS/AI sameness;
- it depends on inaccessible premium material;
- it requires heavy motion without a reduced-motion fallback;
- it contradicts brand DNA or current product promise.
