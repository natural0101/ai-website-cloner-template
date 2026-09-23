# Proof Integrity Source Map

Дата проверки: 2026-07-03.

Этот файл нужен перед visual direction, asset production and implementation. Он защищает лендинг от красивого, но недостоверного proof: fake logos, fake metrics, fake testimonials, fake screenshots, fake dashboard states, fake reviews, unsupported claims and copied competitor proof.

## Checked Sources

| Source | URL | Check result | Use |
| --- | --- | --- | --- |
| FTC Endorsements, Influencers, and Reviews | https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews | `200` | Endorsement, review, testimonial and influencer disclosure caution. |
| FTC Advertising FAQ for Small Business | https://www.ftc.gov/business-guidance/resources/advertising-faqs-guide-small-business | `200` | Advertising claim substantiation and small-business marketing caution. |
| FTC Advertising and Marketing on the Internet | https://www.ftc.gov/business-guidance/resources/advertising-marketing-internet-rules-road | automation `403` | Useful official reference if browser-accessible; record access caveat. |
| NN/g Trustworthiness in Web Design | https://www.nngroup.com/articles/trustworthy-design/ | `200` | Trust signals, credibility and user perception. |
| NN/g Commitment Levels | https://www.nngroup.com/articles/commitment-levels/ | `200` | How much trust/proof is needed before higher-commitment actions. |
| NN/g Concise, Scannable, Objective Writing | https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ | `200` | Objective, scannable claims and copy discipline. |
| Baymard Product Page UX | https://baymard.com/blog/current-state-ecommerce-product-page-ux | `200` | Product-page proof, content and decision support. |
| Baymard Perceived Security of Payment Forms | https://baymard.com/blog/perceived-security-of-payment-form | `200` | Trust/security perception around forms and payment flows. |
| Baymard User Reviews for DTC | https://baymard.com/blog/user-reviews-dtc | `200` | Review content quality and trust. |
| Baymard Ratings Distribution Summary | https://baymard.com/blog/user-ratings-distribution-summary | `200` | Rating distribution as a trust signal. |
| Baymard Reviews From Third Parties | https://baymard.com/blog/tours-and-experiences-reviews | `200` | Third-party review visibility and source trust. |

## Proof Types

| Proof type | Accept only if | If missing |
| --- | --- | --- |
| Customer logo | Source dossier or public customer relationship proves permission/usage | Replace with generic category proof or remove. |
| Testimonial/review | Real quote, person/company/source, permission or public citation, and non-misleading context | Replace with objection-handling copy or product evidence. |
| Metric | Source, time period, calculation basis and owner are known | Use qualitative claim or mark as needed evidence. |
| Case result | Baseline, result, timeframe and source are known | Use "example workflow" instead of outcome claim. |
| Security/compliance claim | Real certification, policy, audit, docs or feature evidence exists | Rephrase as current feature or remove. |
| Integration logos | Actual integration exists or docs/source prove support | Use text list, roadmap caveat or remove. |
| Product screenshot | Captured from real product or approved realistic demo with labeled demo status | Capture real UI, use diagram, or mark as concept. |
| Dashboard/table/chat/file state | Real project data, anonymized sample with label, or approved demo data | Replace fake data with skeleton, diagram or explain-state. |
| Awards/press | Public source URL exists | Remove or put in "desired proof" backlog. |
| Review stars/rating | Source, distribution and count are known | Do not show rating UI. |

## Claim Verdicts

Use one verdict for every major claim or proof item:

| Verdict | Meaning | Allowed use |
| --- | --- | --- |
| `verified` | Evidence exists and can be cited in the plan. | Use as visible proof. |
| `needs-evidence` | Claim may be true but evidence is absent from dossier. | Keep as planning question, not final visible copy. |
| `rephrase` | Claim is directionally useful but too absolute, vague, broad or risky. | Rewrite to a narrower supported claim. |
| `visual-only` | Asset can show emotion/style but not proof. | Do not pair with proof or outcome claims. |
| `reject` | False, copied, unsupported, misleading, private, premium-gated or brand-risky. | Remove. |

## Required Maps

Before implementation, create or update:

```text
projects/<slug>/02-copy-and-offer-audit.md
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/19-asset-production-queue.md
projects/<slug>/evidence/asset-manifest.md
projects/<slug>/evidence/decision-log.md
projects/<slug>/10-quality-gate.md
```

## Required Fields

Every visible claim, metric, testimonial, logo, screenshot or proof asset must include:

- claim/proof ID;
- section;
- visible text or asset;
- proof type;
- evidence source: dossier, URL, screenshot, file, product capture, public source, owner note or none;
- claim verdict;
- allowed visible wording;
- visual asset instruction;
- replacement if evidence is missing;
- risk: legal, trust, brand, privacy, fake proof, outdated proof, copied competitor proof;
- QA method.

## Hard Bans

- Do not invent customer logos, testimonials, reviews, star ratings, awards, metrics, certifications or press.
- Do not copy competitor proof, customer names, screenshots, dashboards, pricing claims or charts.
- Do not present generated or mock product UI as a real product screenshot.
- Do not hide demo-data status when using sample states.
- Do not imply security, compliance, AI accuracy, financial, medical, legal or productivity outcomes without evidence.
- Do not use "trusted by", "used by", "best", "number one", "guaranteed", "proven", "secure", "compliant" or exact percentage claims without proof.
- Do not use a component-library demo row as product proof.

## Safer Substitutions

When evidence is missing:

- replace exact metrics with specific feature/process language;
- replace logos with "built for teams like..." only when audience evidence supports it;
- replace testimonial cards with FAQ objections or product workflow evidence;
- replace fake dashboard screenshots with annotated workflow diagrams;
- label concept UI as "concept", "sample data" or remove proof framing;
- use source-dossier screenshots as current-state evidence;
- create a `needed-proof` backlog item instead of faking proof.

## QA Questions

Before handoff, answer:

1. Can every visible proof item be traced to evidence?
2. Does every metric include timeframe and source?
3. Are all screenshots real, labeled demo, or non-proof diagrams?
4. Are demo users, chats, files, invoices and tables replaced with real or clearly sample content?
5. Are security/compliance claims backed by docs or removed?
6. Are endorsements/reviews/testimonials real and contextual?
7. Would a user misunderstand generated visuals as proof?
8. Are missing proof items listed as backlog rather than shipped as claims?
