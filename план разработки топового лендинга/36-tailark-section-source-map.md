# Tailark Section Source Map

Дата проверки: 2026-07-03.

Tailark is useful when the plan needs stronger marketing-section structure: hero, logo cloud, features, integrations, content, stats, team, testimonials, CTA, footer, pricing, comparator, FAQ, auth, contact, bento, secondary hero, and page layouts.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Public site | https://tailark.com/ | 200 |
| Public docs | https://tailark.com/docs | 200, documents registry namespace and CLI usage |
| Public sitemap | https://tailark.com/sitemap.xml | 200, 208 URLs |
| Public blocks | https://tailark.com/blocks | 200 |
| Public category example | https://tailark.com/hero-section | 200, redirects to `/dusk/hero-section` |
| Public preview example | https://tailark.com/preview/dusk/hero-section/one | 200 |
| Public item registry example | https://tailark.com/r/hero-section-1.json | 200 |
| Mist item registry example | https://tailark.com/r/mist-hero-section-1.json | 200 |
| Veil item registry example | https://tailark.com/r/veil-hero-section-1.json | 200 |
| Public root registry | https://tailark.com/registry.json | 404, do not use |
| GitHub repo | https://github.com/tailark/blocks | 200 |
| Raw public registry | https://raw.githubusercontent.com/tailark/blocks/main/apps/www/registry.json | 154 items |
| Raw Veil registry | https://raw.githubusercontent.com/tailark/blocks/main/apps/www/veil-registry.json | 76 items |
| License | https://raw.githubusercontent.com/tailark/blocks/main/LICENCE.md | MIT for public repo |
| Pro site | https://pro.tailark.com/ | 200, paid/API-key access |
| Pro docs | https://pro.tailark.com/docs/quick-setup | 200, requires Tailark Pro API key |
| Pro sitemap | https://pro.tailark.com/sitemap.xml | 621 URLs |

## Crawl Findings

Public `tailark.com/sitemap.xml` returned 208 URLs:

- 18 live public category/home URLs returned 200.
- 190 old preview URLs returned 404. They are shaped like `/preview/<category>/<Title> (dusk-kit)` and should not be used.
- Current live preview URLs are shaped like `/preview/dusk/<category>/<number-word>` and are discovered from category pages.

Public GitHub registry facts:

- `apps/www/registry.json`: 154 items, including 20 `registry:ui` and 134 `registry:block`.
- `apps/www/veil-registry.json`: 76 items, including 19 `registry:ui` and 57 `registry:block`.
- Useful public block categories include call-to-action, comparator, content, FAQ, features, footer, hero-section, login, sign-up, forgot-password, stats, team, testimonials, logo-cloud, pricing, contact, and integrations.
- Common dependencies include shadcn button, card, input, label, avatar, accordion, Tailark icons/logos, Motion Primitives, Magic UI border-beam, `motion`, `next-themes`, and `dotted-map`.

Pro sitemap facts after normalizing malformed `https:/pro...` URLs:

- 621 URLs checked.
- 547 returned 200.
- 74 `/pages/*` URLs returned 404.
- 258 Pro preview URLs returned 200.
- Live Pro block categories include header, hero-section, secondary-hero, logo-cloud, features, features-carousel, expandable-features, bento, code-demo, how-it-works, integrations, content, stats, testimonials, CTA, footer, pricing, comparator, FAQ, blog blocks, team, description list, open roles, investors, auth blocks, and contact.

## Install Model

Public docs show:

```json
{
  "registries": {
    "@tailark": "https://tailark.com/r/{name}.json"
  }
}
```

Public install examples:

```bash
pnpm dlx shadcn add @tailark/hero-section-1
pnpm dlx shadcn add @tailark/mist-hero-section-1
```

Do not guess names. Copy the CLI command from the live category page or confirm the item URL returns 200.

Tailark Pro quick setup requires a generated API key and registry headers. Treat Pro as reference-only unless the project has explicit access and license approval.

## Good Landing Uses

- Hero structure when the current hero lacks hierarchy or a credible product visual zone.
- Feature/bento sections when cards are repetitive and need mixed visual rhythm.
- Pricing/comparator/FAQ when conversion sections need proven SaaS structure.
- Logo cloud/testimonials/stats when proof needs quieter, structured presentation.
- Auth/contact/footer when the landing includes account or sales flows.
- Page-level inspiration from Pro only as structure, unless access is explicit.

## Reject By Default

- Copying demo copy, fake logos, fake screenshots, or fake proof.
- Installing a whole block when native Tailwind plus shadcn is enough.
- Using old sitemap preview URLs as source evidence.
- Relying on `/registry.json`.
- Pro blocks, pages, illustrations, or snippets without explicit access and license.
- Keeping Tailark palette, spacing, icon family, or visual identity unchanged when it conflicts with the project style tile.

## Required Selection File

Before implementation, fill:

```text
projects/<slug>/32-tailark-section-selection.md
```

The file must record exact candidate, source URL, preview URL, registry URL, install command or reference-only status, dependencies, access/license, adaptation, reduced-motion fallback, mobile simplification, decision, owner `task-###`, and `chg-###`.
