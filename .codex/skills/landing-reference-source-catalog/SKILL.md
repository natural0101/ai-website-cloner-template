---
name: landing-reference-source-catalog
description: Choose and audit landing-page reference sources before collecting inspiration. Use when a landing plan needs source routing across galleries, SaaS examples, product-flow libraries, motion references, CRO evidence, or when references must be mapped to sections with access, license, anti-copy, and risk gates.
---

# Landing Reference Source Catalog

Use this skill before `landing-reference-research`, `landing-thematic-reference-mining`, `landing-reference-scoring`, or any reference-board work that depends on external galleries.

## Required Reading

Read:

```text
план разработки топового лендинга/52-reference-gallery-source-map.md
план разработки топового лендинга/06-reference-query-playbook.md
план разработки топового лендинга/28-thematic-reference-mining.md
```

If the active project folder exists, also read:

```text
план разработки топового лендинга/projects/<slug>/landing-source-dossier.md
план разработки топового лендинга/projects/<slug>/25-brand-dna-map.md
```

If those files are absent, infer the source brief from available plan files and mark the missing evidence as a risk.

## Workflow

1. Extract the product category, buyer, CTA, trust model, workflow, asset type, desired emotion, and important sections.
2. Choose source lanes before searching:
   - direct/domain landing examples;
   - SaaS structure and proof;
   - product flow;
   - visual language;
   - motion/interaction;
   - CRO or UX evidence;
   - anti-reference.
3. Pick sources from `52-reference-gallery-source-map.md` based on the lane.
4. Check access status for each source or candidate URL. Record blocked, manual-only, premium, account-gated, timeout, or sitemap-only status.
5. Reject candidates with no closeness reason, no section mapping, inaccessible premium dependency, copied proof risk, or heavy motion without fallback.
6. Promote only references that make a concrete section, motion, asset, copy, proof, or UX decision stronger.

## Output

Record source decisions in:

```text
план разработки топового лендинга/projects/<slug>/24-thematic-reference-map.md
план разработки топового лендинга/projects/<slug>/03-reference-board.md
план разработки топового лендинга/projects/<slug>/15-reference-scorecard.md
план разработки топового лендинга/projects/<slug>/22-inspiration-synthesis.md
план разработки топового лендинга/projects/<slug>/evidence/reference-manifest.md
```

For motion references, also update:

```text
план разработки топового лендинга/projects/<slug>/26-motion-reference-map.md
```

## Candidate Fields

For every candidate, write:

- source URL and access status;
- lane;
- closeness reason;
- section mapping;
- what to borrow;
- what to transform;
- what not to copy;
- risk;
- screenshot evidence path or reason screenshot is unavailable.

## Source Safety Rules

- Treat `403`, `429`, `525`, timeout, or blocked automation as an access caveat, not as proof that the source is useless.
- Use browser/manual-only sources only when screenshot or URL evidence is recorded.
- Use premium/account-gated sources only as reference, never as copied material.
- Prefer original site URLs over gallery wrapper pages when possible.
- Do not copy proprietary screenshots, claims, logos, testimonials, customer proof, pricing, or code.
- A source that is visually strong but not close to product, buyer, workflow, trust model, asset type, emotion, or interaction must be rejected.
