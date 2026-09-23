---
name: landing-proof-integrity-gate
description: Audit landing-page proof integrity before planning or implementation. Use when a landing plan includes claims, metrics, testimonials, reviews, customer logos, awards, security/compliance statements, product screenshots, dashboard states, generated assets, component-library demo data, or any visible proof that must be verified, rephrased, labeled, backlogged, or rejected.
---

# Landing Proof Integrity Gate

Use this skill after copy/offer audit begins and before visual direction, asset production, component selection, implementation handoff, or final QA.

## Required Reading

Read:

```text
план разработки топового лендинга/54-proof-integrity-source-map.md
план разработки топового лендинга/10-evidence-and-cro-sources.md
план разработки топового лендинга/22-asset-production-queue.md
```

If the active project folder exists, also read:

```text
план разработки топового лендинга/projects/<slug>/landing-source-dossier.md
план разработки топового лендинга/projects/<slug>/02-copy-and-offer-audit.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/evidence/asset-manifest.md
план разработки топового лендинга/projects/<slug>/evidence/decision-log.md
```

## Workflow

1. Extract every visible or planned claim, proof item and proof-like asset.
2. Classify each as customer logo, testimonial, review, metric, case result, security/compliance claim, integration logo, product screenshot, dashboard state, award/press, rating, generated visual or component-library demo data.
3. Assign a claim verdict:
   - `verified`
   - `needs-evidence`
   - `rephrase`
   - `visual-only`
   - `reject`
4. For each item, record source evidence, allowed visible wording, visual instruction, replacement if missing, risk and QA method.
5. Remove, rephrase or backlog anything unsupported.
6. Mirror proof decisions into copy audit, asset queue, component/asset plan, decision log and quality gate.

## Required Output

Update:

```text
план разработки топового лендинга/projects/<slug>/02-copy-and-offer-audit.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/evidence/asset-manifest.md
план разработки топового лендинга/projects/<slug>/evidence/decision-log.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

During final QA, also check:

```text
план разработки топового лендинга/projects/<slug>/12-final-qa-report.md
```

## Non-Negotiable Rules

- Do not invent customer logos, testimonials, reviews, star ratings, awards, metrics, certifications, press or security/compliance claims.
- Do not present generated/mock UI as a real product screenshot.
- Do not use component-library demo data as product proof.
- Do not copy competitor screenshots, claims, customer proof, pricing or charts.
- Label sample data or remove proof framing.
- Replace missing proof with narrower copy, workflow explanation, diagram, FAQ objection handling or needed-proof backlog.

## Row Requirements

Every proof row must include:

- claim/proof ID;
- section;
- visible text or asset;
- proof type;
- evidence source;
- claim verdict;
- allowed visible wording;
- replacement if evidence is missing;
- risk;
- QA method.
