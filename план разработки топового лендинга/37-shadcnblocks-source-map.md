# shadcnblocks Source Map

Дата проверки: 2026-07-03.

shadcnblocks is useful when the plan needs a large shadcn-compatible source for marketing sections, app sections, ecommerce sections, backgrounds, pages, templates, and small UI components.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://www.shadcnblocks.com/ | 200 |
| Blocks index | https://www.shadcnblocks.com/blocks | 200, claims 1721+ blocks |
| Free blocks | https://www.shadcnblocks.com/blocks/free | 200, 106 free block links found |
| Components index | https://www.shadcnblocks.com/components | 200, claims 1684+ components |
| CLI page | https://www.shadcnblocks.com/shadcn-cli | 200 |
| Blocks docs | https://www.shadcnblocks.com/docs/blocks/getting-started | 200 |
| License | https://www.shadcnblocks.com/license | 200 |
| Pricing | https://www.shadcnblocks.com/pricing | 200 |
| Sitemap | https://www.shadcnblocks.com/sitemap.xml | 200, 3912 URLs |
| Robots | https://www.shadcnblocks.com/robots.txt | 200, disallows `/api/`, `/r/`, `/preview/`, `/screenshot/` |
| Public root registry | https://www.shadcnblocks.com/registry.json | 404, do not use |
| Free registry example | https://www.shadcnblocks.com/r/hero1.json | 200 |
| Free registry example | https://www.shadcnblocks.com/r/feature1.json | 200 |
| Pro registry example | https://www.shadcnblocks.com/r/hero125.json | 401 without API key |
| Pro registry example | https://www.shadcnblocks.com/r/pricing1.json | 401 without API key |
| Free GitHub repo | https://github.com/shadcnblocks/shadcn-ui-blocks | 200 |
| Free repo license | https://raw.githubusercontent.com/shadcnblocks/shadcn-ui-blocks/master/LICENSE.md | MIT + Commons Clause |

## Site Crawl Findings

The sitemap has 3912 URLs. A bounded HEAD crawl checked all sitemap URLs except registry/preview endpoints and found 3908 live URLs and 4 broken URLs.

| Path group | Count | Status summary |
| --- | ---: | --- |
| `/block/*` | 1645 | 1645 live |
| `/component/*` | 1684 | 1684 live |
| `/blocks/*` category pages | 270 | 267 live, 3 broken hero category pages |
| `/components/*` category pages | 87 | 87 live |
| `/page/*` | 48 | 47 live, 1 broken |
| `/template/*` | 16 | 16 live |
| `/docs/*` | 34 | 34 live |
| `/changelog/*` | 78 | 78 live |

Broken sitemap URLs found:

- `https://www.shadcnblocks.com/blocks/hero/layered`
- `https://www.shadcnblocks.com/blocks/hero/quad`
- `https://www.shadcnblocks.com/blocks/hero/inline-image-text`
- `https://www.shadcnblocks.com/page/modern-page2`

The blocks index reports:

- 1721+ total blocks.
- Marketing 1284, App 211, Ecommerce 151, Background 72.
- Example categories include hero, feature, pricing, contact, testimonial, footer, navbar, gallery, blog, CTA, stats, FAQ, code example, compliance, banner, careers, process, waitlist, dashboard, data table, checkout, shopping cart, product detail, shader, and background pattern.

The components index reports 1684+ extra components, including many shadcn-like variants for buttons, charts, forms, alerts, dialogs, input groups, dropdowns, sheets, sliders, cards, pagination, tables, and more.

## Access And License

Free page check:

- `https://www.shadcnblocks.com/blocks/free` linked 106 free block pages.
- Detail pages for those 106 links reported `Access: free`.
- Free examples: `hero1`, `hero3`, `hero7`, `hero45`, `hero47`, `hero115`, `feature1`, `feature13`, `feature17`, `feature51`, `feature72`, `feature73`, `feature166`, `feature197`, `pricing2`, `pricing4`, `pricing6`, `faq1`, `cta10`, `cta11`, `cta34` to `cta39`, `logos8`, `logos18`, `navbar1`, `footer2`, `testimonial9`, `testimonial10`.

Pro examples:

- `https://www.shadcnblocks.com/block/hero125` is live and marked `Access: pro`.
- `https://www.shadcnblocks.com/r/hero125.json` returned 401 without API authentication.
- `https://www.shadcnblocks.com/block/pricing1` is live and marked `Access: pro`.
- `https://www.shadcnblocks.com/r/pricing1.json` returned 401 without API authentication.

The free GitHub repo default branch is `master`; GitHub API reports license `Other`. The repo `LICENSE.md` is MIT plus Commons Clause. It allows use in an application, website, or product, including commercial use, but restricts selling, sublicensing, or redistributing the components themselves. Do not use this source to create a reusable component kit, marketplace item, website builder, AI generator, or competing component product.

The pricing page claims Pro access includes 1684+ Pro Components, 1562+ Pro Blocks, templates, Figma kit, admin kit, pages, page builder, and updates. Treat those as paid/pro until access and license are explicit.

## Install Model

Public registry config from the CLI page:

```json
{
  "registries": {
    "@shadcnblocks": "https://www.shadcnblocks.com/r/{name}.json"
  }
}
```

Public install example:

```bash
npx shadcn@latest add @shadcnblocks/hero1
```

Docs also show a Pro setup:

```json
{
  "registries": {
    "@shadcnblocks": {
      "url": "https://www.shadcnblocks.com/r/{name}",
      "headers": {
        "Authorization": "Bearer ${SHADCNBLOCKS_API_KEY}"
      }
    }
  }
}
```

Do not guess IDs. Confirm the live item page, access label, registry URL status, install command, dependencies, and license/access before implementation.

## Good Landing Uses

- Hero, feature, pricing, FAQ, CTA, logo/proof, testimonial, stats, footer, navbar, contact, waitlist, book-a-demo, case study, and compliance sections.
- Ecommerce sections like product detail, cart, checkout, product list, product specs, product gallery, trust strip, product quick view, and payment methods.
- App sections like dashboard, data table, onboarding, settings, invite user, todo list, address book, application shell, and sidebar when the landing previews a product UI flow.
- Background patterns only when the style tile earns them.
- Components only when existing shadcn/native primitives are not enough.

## Reject By Default

- Pro/Premium blocks without API-key access and license approval.
- Full visual identity copy, demo copy, fake metrics, fake logos, fake screenshots, and generic block-library rhythm.
- Items that replace a simple native section with heavy dependency sprawl.
- Component redistribution, reusable template kits, website builders, marketplace assets, or AI generators based on copied blocks.
- Broken sitemap URLs and guessed registry IDs.

## Required Selection File

Before implementation, fill:

```text
projects/<slug>/33-shadcnblocks-selection.md
```

The file must record exact item, source type, access status, live source URL, registry URL, install command or reference-only status, dependencies, license/access, adaptation, reduced-motion fallback if animated, mobile simplification, decision, owner `task-###`, and `chg-###`.
