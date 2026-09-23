# MVPBlocks Source Map

Дата проверки: 2026-07-03.

MVPBlocks is an open-source library of copy-paste and CLI-installable blocks for Next.js, React, Tailwind CSS and Framer Motion. Use it as a gated section-structure and MVP-template source, not as a default visual identity.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://blocks.mvp-subha.me/ | 200 |
| Templates | https://blocks.mvp-subha.me/templates | 200 |
| Showcase | https://blocks.mvp-subha.me/showcase | 200 |
| CLI docs | https://blocks.mvp-subha.me/docs/cli | 200 |
| Add block docs | https://blocks.mvp-subha.me/docs/add-a-block | 200 |
| Sitemap | https://blocks.mvp-subha.me/sitemap.xml | 200, 96 URLs |
| LLM map | https://blocks.mvp-subha.me/llms.txt | 200 |
| Full LLM map | https://blocks.mvp-subha.me/llms-full.txt | 200 |
| Root registry guess | https://blocks.mvp-subha.me/r/registry.json | 404 HTML |
| Legacy registry guess | https://blocks.mvp-subha.me/registry.json | 404 HTML |
| Sample item | https://blocks.mvp-subha.me/r/hero-1.json | 200 JSON |
| GitHub repo | https://github.com/subhadeeproy3902/mvpblocks | 200 |
| GitHub license | https://raw.githubusercontent.com/subhadeeproy3902/mvpblocks/main/LICENSE | BSD-3-Clause |
| NPM package | https://www.npmjs.com/package/mvpblocks | version 2.1.13, MIT package license |

## Site And Registry Inventory

Sitemap:

- 96 URLs total.
- 89 docs URLs.
- 7 top-level URLs.

CLI constants and item endpoints:

- 252 item names in `cli/src/constants.js`.
- 252/252 exact endpoints `https://blocks.mvp-subha.me/r/<name>.json` returned 200 JSON.
- Types: 77 `registry:ui`, 171 `registry:block`, 3 `registry:hook`, 1 `registry:lib`.
- Root indexes `/r/registry.json` and `/registry.json` returned 404 and must not be used as evidence.

Top categories from item metadata:

| Category | Count |
| --- | ---: |
| `mainsection` | 52 |
| `text-animation` | 47 |
| `shadcn` | 46 |
| `interactive` | 22 |
| `layout` | 21 |
| `dashboard` | 20 |
| `design` | 16 |
| `form-element` | 14 |
| `navigation` | 12 |
| `hero` | 12 |
| `card` | 11 |
| `loader` | 11 |
| `animation` | 10 |
| `pricing` | 10 |
| `team` | 10 |

Common dependencies:

| Dependency | Count |
| --- | ---: |
| `react` | 129 |
| `lucide-react` | 91 |
| `framer-motion` | 88 |
| `next-themes` | 10 |
| `class-variance-authority` | 9 |
| `@radix-ui/react-slot` | 5 |
| `recharts` | 4 |
| `@number-flow/react` | 3 |
| `gsap` | 2 |
| `next` | 2 |

Common registry dependencies:

- `utils.json` on 82 items.
- `button.json` on 49 items.
- `input.json` on 14 items.
- `label.json` on 12 items.
- `card.json` on 11 items.
- `badge.json` on 10 items.

## Install Model

Preferred CLI command:

```bash
npx mvpblocks add <name> --ts
```

Exact URL form:

```bash
npx shadcn@latest add https://blocks.mvp-subha.me/r/<name>.json
```

Do not bulk-install. Pick exact items only.

The CLI can initialize a fresh project and can install dependencies automatically. In this template, use it only inside an already reviewed target project, after the section plan and dependency gate are filled.

## License Gate

The repository license is BSD-3-Clause. The npm CLI package metadata reports MIT. Treat MVPBlocks as usable for personal and commercial app/site work, but record both license signals in the selection file.

Do not redistribute MVPBlocks as a competing component library or leave copied demo content as a product claim.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Hero structure | `hero-1`, `minimal-hero`, `gradient-hero`, `mockup-hero`, `app-hero`, `geometric-hero` | Use as composition reference; rewrite copy, colors and assets. |
| Product proof | `mockup-hero`, `animated-ai-chat`, `conversation1`, `working-chatbot`, dashboard blocks | Use only when the product workflow is real. |
| Feature section | `feature-1`, `feature-2`, `feature-3`, `bento-grid-1`, `bento-grid-2`, `bento-grid-3` | Good for section skeletons, not final proof copy. |
| Pricing | `simple-pricing`, `technical-pricing`, `pricing-2`, `pricing-3`, `pricing-4`, `pricing-5` | Replace tiers and claims with real offer. |
| FAQ and objections | `faq-1`, `faq-2`, `faq-3`, `faq-4` | Must map to real buyer objections. |
| CTA and conversion | `cta-1`, `cta-2`, `cta-3`, `waitlist` | Use after copy/offer audit. |
| Trust and social proof | `testimonials-carousel`, `testimonials-marquee`, `logo-cloud`, `sparkles-logo` | Reject fake testimonials and fake logos. |
| Navigation and footer | `header-1`, `header-2`, `footer-4col`, `footer-animated`, `footer-glow`, `footer-newsletter`, `footer-standard` | Keep simple landing nav unless product needs more. |
| Text motion | `blur-in-text`, `fade-in-up-text`, `shiny-text`, `shuffle-text`, `text-reveal`, `wave-text` | Short headlines, metrics and labels only. |

## Reject Or Use Carefully

- Reject `target-cursor`, `target-cursor-demo`, loaders and preloaders by default.
- Reject 3D/globe/Web3 hero unless the product story earns it and mobile/performance QA is planned.
- Reject dashboard, chatbot, finance and AI blocks when they would create fake product proof.
- Reject GSAP text effects if CSS, Motion Primitives, Animate UI or existing Motion code can do the job.
- Reject full template identity copying from `ai-saas-marketing`, `designer-portfolio`, `developer-portfolio`, `paymintx`, `opus-devops` and similar templates.
- Reject any item whose `next/link`, `next` or App Router assumptions do not match the target project.
- Reject any MVPBlocks item if Tailark, shadcnblocks, ReUI, Kokonut UI or local shadcn already solves the same section with lower dependency and better brand fit.

## Selection Flow

1. Identify the section job and missing structure.
2. Check native/local/shadcn, Animate UI, Motion Primitives, Magic UI, Tailark, shadcnblocks, ReUI, 21st.dev and Kokonut UI first.
3. Choose one exact MVPBlocks item or template reference.
4. Verify docs page and exact endpoint `https://blocks.mvp-subha.me/r/<name>.json`.
5. Record dependencies, registry dependencies, license caveat, adaptation, reduced-motion fallback, mobile behavior and QA.
6. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/41-mvpblocks-selection.md
```

The file must record exact docs page, item, endpoint URL, CLI or exact URL command, license/access, dependencies, registry dependencies, visible purpose, adaptation, fallback, mobile behavior, decision, task ID, change ID, risk and QA evidence.
