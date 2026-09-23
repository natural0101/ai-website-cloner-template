# SmoothUI Source Map

Дата проверки: 2026-07-03.

SmoothUI is an MIT shadcn-compatible registry of animated React components and landing blocks built around Tailwind CSS, Motion and shadcn install flows. Use it as a gated source for exact animated details, AI/product UI accents and small landing blocks, not as a full visual identity.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://smoothui.dev/ | 200 |
| Docs | https://smoothui.dev/docs | 200 |
| Sitemap | https://smoothui.dev/sitemap.xml | 200, 110 URLs |
| Robots | https://smoothui.dev/robots.txt | 200 |
| LLM map | https://smoothui.dev/llms.txt | 200 |
| Full LLM map | https://smoothui.dev/llms-full.txt | 200 |
| Components machine catalog | https://smoothui.dev/llms-components.json | 200, 72 components |
| OpenAPI | https://smoothui.dev/openapi.json | 200, 6 API paths |
| Registry index | https://smoothui.dev/r/registry.json | 200, 107 items |
| Legacy registry guess | https://smoothui.dev/registry.json | 404 HTML |
| Sample component endpoint | https://smoothui.dev/r/siri-orb.json | 200 JSON |
| Sample block endpoint | https://smoothui.dev/r/cta-1.json | 200 JSON |
| Sample block preview | https://smoothui.dev/blocks/preview/cta-1 | 200 HTML |
| Blocks API list | https://smoothui.dev/api/v1/blocks | 200 JSON, empty list |
| Blocks API item guess | https://smoothui.dev/api/v1/blocks/cta-1 | 500 HTML |
| GitHub repo | https://github.com/educlopez/smoothui | 200 |
| GitHub license | https://raw.githubusercontent.com/educlopez/smoothui/main/LICENSE | MIT |
| NPM package | https://www.npmjs.com/package/smoothui-cli | version 1.1.1, MIT |

## Site And Registry Inventory

Sitemap count:

- 110 URLs total.
- 1 home page.
- 1 docs root.
- 11 block docs pages.
- 73 component docs pages, including the component index and 72 component pages.
- 21 guide pages.
- 3 community pages.

Machine-readable surfaces:

- `llms.txt`, `llms-full.txt`, `llms-components.json` and `openapi.json` are live.
- OpenAPI exposes `/api/v1/components`, `/api/v1/components/{name}`, `/api/v1/components/search`, `/api/v1/blocks`, `/api/v1/blocks/{name}` and `/api/v1/suggest`.
- `/api/v1/components?pageSize=100` returned all 72 components with category, complexity, animation type, reduced-motion metadata and exact install command.
- `/api/v1/blocks` returned an empty data list, and block item API guesses returned 500. Do not use the blocks API as block evidence.

Registry scan:

- 107 item names in `https://smoothui.dev/r/registry.json`.
- 107/107 exact endpoints `https://smoothui.dev/r/<name>.json` returned 200 JSON.
- All registry items currently report `registry:ui`.
- Practical split: 72 components and 35 block/shared items.
- Components API reports 56 components with reduced-motion support and 16 without it.
- Main dependencies: `motion` on 94 items, `lucide-react` on 40, `@smoothui/data` on 8, `class-variance-authority` on 4, `radix-ui` on 3, `@radix-ui/react-slot` on 3, `usehooks-ts` on 2, `react-use-measure` on 2, `@radix-ui/react-popover` on 2, `gsap` on 1 and `react-tweet` on 1.

Component API categories:

| Category | Count |
| --- | ---: |
| `other` | 23 |
| `basic-ui` | 22 |
| `data-display` | 8 |
| `text` | 5 |
| `ai` | 4 |
| `button` | 4 |
| `layout` | 4 |
| `feedback` | 2 |

Animation metadata:

| Type | Count |
| --- | ---: |
| `spring` | 51 |
| `tween` | 16 |
| `gesture` | 3 |
| `scroll` | 1 |
| `none` | 1 |

Block/shared item names:

```text
cta-1, cta-2, cta-3, faq-1, faq-2, faq-3, faq-4, features-1, features-2, features-3, footer-1, footer-2, footer-3, footer-4, header-1, header-2, header-3, header-4, header-5, header-6, logo-cloud-1, logo-cloud-2, logo-cloud-3, logo-cloud-4, pricing-1, pricing-2, pricing-3, shared, stats-1, stats-2, team-1, team-2, testimonials-1, testimonials-2, testimonials-3
```

Component names:

```text
agent-avatar, ai-branch, ai-input, animated-avatar-group, animated-file-upload, animated-input, animated-o-t-p-input, animated-progress-bar, animated-stepper, animated-tabs, animated-tags, animated-toggle, animated-tooltip, app-download-stack, apple-invites, basic-accordion, basic-dropdown, basic-modal, basic-toast, book, breadcrumb, button-copy, checkbox, clip-corners-button, combobox, context-menu, contribution-graph, cursor-follow, dialog, dot-morph-button, drawer, dropdown-menu, dynamic-island, expandable-cards, exposure-slider, figma-comment, form, github-stars-animation, glow-hover-card, gooey-popover, grid-loader, image-metadata-preview, infinite-slider, interactive-image-selector, job-listing-component, magnetic-button, notification-badge, number-flow, pagination, phototab, power-off-slide, price-flow, product-card, radio-group, reveal-text, reviews-carousel, rich-popover, scramble-hover, scroll-reveal-paragraph, scrollable-card-stack, scrubber, searchable-dropdown, select, siri-orb, skeleton-loader, smooth-button, social-selector, switchboard-card, tweet-card, typewriter-text, user-account-avatar, wave-text
```

## Install Model

SmoothUI CLI:

```bash
npx smoothui-cli@latest add <name>
```

Official shadcn namespace:

```bash
npx shadcn@latest add @smoothui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://smoothui.dev/r/<name>.json
```

Use exact item names only. Do not bulk-install. For blocks, record both the preview URL and exact registry endpoint because the blocks API is currently not usable as evidence.

## License Gate

The GitHub repo and `smoothui-cli` npm package both report MIT license. Treat public registry items as usable in personal and commercial site/app work, while still recording source URL, endpoint, dependencies and adaptation notes.

Do not redistribute SmoothUI as a competing component library, and do not leave demo copy, fake AI behavior, fake tweets, fake reviews or placeholder product data as product claims.

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Section structure | `header-1..6`, `cta-1..3`, `features-1..3`, `pricing-1..3`, `faq-1..4`, `stats-1..2`, `testimonials-1..3`, `footer-1..4`, `logo-cloud-1..4` | Use as structure or motion reference; rewrite copy, brands, logos and screenshots. |
| AI/product proof | `ai-input`, `ai-branch`, `agent-avatar`, `siri-orb`, `apple-invites`, `image-metadata-preview`, `switchboard-card`, `product-card`, `job-listing-component` | Use only when the product workflow is real. |
| Buttons and CTA tactility | `smooth-button`, `magnetic-button`, `button-copy`, `dot-morph-button`, `clip-corners-button` | One or two focused actions only. |
| Forms and controls | `animated-input`, `animated-file-upload`, `animated-o-t-p-input`, `animated-tags`, `animated-toggle`, `animated-stepper`, `animated-tabs`, `animated-progress-bar`, `combobox`, `select`, `searchable-dropdown` | Good for product UI demos and conversion forms. |
| Proof and metrics | `number-flow`, `price-flow`, `contribution-graph`, `github-stars-animation`, `reviews-carousel`, `tweet-card` | Reject if the metric or social proof is not real. |
| Text motion | `reveal-text`, `scroll-reveal-paragraph`, `scramble-hover`, `typewriter-text`, `wave-text` | Use for short headlines, labels or metrics, not body paragraphs. |
| Layout and media detail | `expandable-cards`, `scrollable-card-stack`, `infinite-slider`, `phototab`, `glow-hover-card`, `interactive-image-selector`, `book` | Needs mobile simplification and reduced-motion fallback. |

## Reject Or Use Carefully

- Reject root `/registry.json` as install evidence because it returned 404 HTML.
- Reject `/api/v1/blocks` as block evidence because it returned an empty list, and `/api/v1/blocks/<name>` returned 500.
- Reject `cursor-follow`, loaders and skeletons by default unless they solve a real interaction state.
- Reject `gooey-popover` unless `gsap` is already justified by the motion storyboard.
- Reject `tweet-card`, fake reviews, fake stars and fake logos unless source evidence is real.
- Reject `siri-orb`, AI branch/input and agent avatars for non-AI products.
- Reject broad replacement of local shadcn primitives.
- Treat any component with `hasReducedMotion=false` as requiring a custom fallback before implementation.
- Reject items whose animation hides content, shifts layout, traps focus or breaks mobile scanning.

## Selection Flow

1. Identify the section job and missing interaction or block structure.
2. Check native/local/shadcn, Animate UI, Motion Primitives, Magic UI, Tailark, shadcnblocks, ReUI, Kokonut UI and MVPBlocks first.
3. Choose one exact SmoothUI item or explicitly reject SmoothUI for the section.
4. For components, verify docs URL, `/api/v1/components/<name>` metadata and endpoint `https://smoothui.dev/r/<name>.json`.
5. For blocks, verify docs category, preview URL and endpoint `https://smoothui.dev/r/<name>.json`; do not use `/api/v1/blocks`.
6. Record dependencies, registry dependencies, MIT license, adaptation, reduced-motion fallback, mobile behavior and QA.
7. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/42-smoothui-selection.md
```

The file must record exact docs page or preview page, item, endpoint URL, install command, MIT license/access, dependencies, registry dependencies, API or registry evidence, visible purpose, adaptation, reduced-motion fallback, mobile behavior, decision, task ID, change ID, risk and QA evidence.
