# Skiper UI Source Map

Дата проверки: 2026-07-03.

Skiper UI is an official shadcn registry directory source for uncommon animated components and motion-heavy landing details. Use it as a gated source for exact public registry items and visual references, not as a normal MIT/open-source component library.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Website | https://skiper-ui.com/ | 200 on `HEAD`; some full `GET` attempts timed out |
| Components index | https://skiper-ui.com/components | 200 |
| Pricing | https://skiper-ui.com/pricing | 200 on `HEAD`; advertises Premium and Exclusive access |
| Terms | https://skiper-ui.com/docs/terms-of-service | 200; restrictive website-content language |
| Privacy | https://skiper-ui.com/docs/privacy-policy | 200 |
| Docs root | https://skiper-ui.com/docs | 404 |
| Quick start | https://skiper-ui.com/docs/quick-start | in sitemap; full `GET` can timeout |
| Sitemap | https://skiper-ui.com/sitemap.xml | 200, 218 URLs |
| Robots | https://skiper-ui.com/robots.txt | 200 |
| LLM map | https://skiper-ui.com/llms.txt | 404 |
| Registry index | https://skiper-ui.com/registry/registry.json | 200, 38 items |
| Exact item endpoints | https://skiper-ui.com/registry/&lt;name&gt;.json | 38/38 returned 200 on `HEAD` |
| Wrong registry path | https://skiper-ui.com/r/registry.json | 404 |
| Wrong item path | https://skiper-ui.com/r/&lt;name&gt;.json | 404 on sampled items |
| Root registry guess | https://skiper-ui.com/registry.json | unstable/404 guess, not an install source |
| Official shadcn registries index | https://ui.shadcn.com/r/registries.json | contains `@skiper-ui` mapped to `https://skiper-ui.com/registry/{name}.json` |
| Public GitHub source repo | none verified | no MIT/public source repo found during audit |

## Site And Registry Inventory

Sitemap scan:

- 218 URLs total.
- 1 homepage, 1 components page, 1 pricing page, 1 user page.
- 4 docs paths: `/docs`, `/docs/quick-start`, `/docs/terms-of-service`, `/docs/privacy-policy`.
- 105 `/v1/skiper*` pages returned 200 on `HEAD`.
- 105 `/preview/skiper*` pages returned 404 on `HEAD`.
- Full HTML `GET` can be unstable for root, pricing, quick-start and some item pages. Use `HEAD`, registry endpoints and successful HTML pages as evidence instead of relying on one large page fetch.

Registry scan:

- Public registry index has 38 items.
- All items currently report `registry:ui`.
- 38/38 endpoints `https://skiper-ui.com/registry/<name>.json` returned 200 on `HEAD`.
- Item endpoint `GET` can occasionally reset. Retry before declaring a specific item broken.
- Registry index item rows omit file contents, while exact item endpoints include component files.

Official shadcn registry:

```text
@skiper-ui -> https://skiper-ui.com/registry/{name}.json
```

Install command:

```bash
npx shadcn@latest add @skiper-ui/<name>
```

Exact URL form:

```bash
npx shadcn@latest add https://skiper-ui.com/registry/<name>.json
```

## Access And License Gate

Skiper UI must not be treated as MIT in this planning system.

- The pricing page advertises paid Premium and Exclusive access, premium components, source-code access, early access and templates.
- The terms page says website content is reserved and restricts republishing, selling, reproducing, copying and redistributing material from `skiper-ui.com`.
- No official public source repository or MIT license was verified.
- A small unrelated-looking GitHub repo `nischayhq/skiper-ui` exists without a verified license and is not used as source evidence.
- Public registry endpoints can be considered install candidates only after project-specific terms/access review.
- Premium/account-only material, paid templates, Figma files, screenshots, private code and closed components are not copied or adapted.

## Registry Items

| Item | Description | Dependencies | Registry Dependencies |
| --- | --- | --- | --- |
| `skiper3` | Apple play button | `framer-motion` | none |
| `skiper4` | Theme toggle buttons | `framer-motion`, `lucide-react` | none |
| `skiper16` | Card stack scroll | `framer-motion`, `lenis` | none |
| `skiper17` | Card stack with gsap and rotate | `gsap`, `@gsap/react`, `framer-motion`, `lenis` | none |
| `skiper19` | Svg follow scroll | `framer-motion` | none |
| `skiper25` | Music toggle btn | `framer-motion`, `use-sound` | none |
| `skiper26` | Theme toggle btn | `framer-motion`, `lucide-react`, `next-themes` | none |
| `skiper28` | 3D perspective text | `framer-motion`, `lenis` | none |
| `skiper30` | Oliver parallax | `framer-motion`, `lenis` | none |
| `skiper31` | Text Scroll animation | `framer-motion`, `lenis` | none |
| `skiper34` | Scroll images reveal 003 | `framer-motion`, `lenis` | none |
| `skiper37` | Animated number | `@number-flow/react`, `framer-motion`, `lucide-react`, `react-intersection-observer` | none |
| `skiper39` | Canvas crowd | `gsap` | none |
| `skiper40` | CssLink | none | none |
| `skiper41` | Progressive Blur | none | none |
| `skiper47` | Perspective carousel | `swiper`, `framer-motion`, `lucide-react` | none |
| `skiper48` | Card swipe carousel | `swiper`, `framer-motion`, `lucide-react` | none |
| `skiper49` | Inverted perspective carousel | `swiper`, `framer-motion`, `lucide-react` | none |
| `skiper50` | Creative carousel 001 | `swiper`, `framer-motion`, `lucide-react` | none |
| `skiper51` | Creative carousel 002 | `swiper`, `framer-motion`, `lucide-react` | none |
| `skiper52` | ExpandOnHover | `framer-motion` | none |
| `skiper53` | ExpandOnHover vertical | `framer-motion` | none |
| `skiper54` | Shadcn clipPath Carousal | `framer-motion`, `embla-carousel-autoplay`, `lucide-react` | `carousel` |
| `skiper58` | Text roll navigation | `framer-motion` | none |
| `skiper61` | Mouse follow animations | `framer-motion` | none |
| `skiper62` | Loop animation hook | `framer-motion` | none |
| `skiper63` | Apple squicircle effect | `framer-motion`, `lucide-react` | none |
| `skiper64` | Gooey Effect | `framer-motion` | none |
| `skiper65` | Breakpoint indicator | none | none |
| `skiper66` | SVG clip path mask | none | none |
| `skiper67` | Video player 001 | `framer-motion`, `media-chrome` | none |
| `skiper87` | Scroll with fade effect | `framer-motion` | `scroll-area` |
| `skiper89` | Scroll progress 001 | `@number-flow/react`, `framer-motion` | none |
| `skiper99` | Animated icons 002 | `framer-motion`, `lucide-react` | none |
| `skiper101` | Custom tooltip | `@radix-ui/react-tooltip` | `tooltip` |
| `skiper102` | Debug Pannel | `framer-motion` | none |
| `skiper105` | Auto Scale input | `dialkit` | none |
| `skiper106` | Smooth caret input | `framer-motion` | none |

Dependency count:

| Dependency | Count |
| --- | ---: |
| `framer-motion` | 31 |
| `lucide-react` | 11 |
| `lenis` | 6 |
| `swiper` | 5 |
| `@number-flow/react` | 2 |
| `gsap` | 2 |
| `@gsap/react` | 1 |
| `@radix-ui/react-tooltip` | 1 |
| `dialkit` | 1 |
| `embla-carousel-autoplay` | 1 |
| `media-chrome` | 1 |
| `next-themes` | 1 |
| `react-intersection-observer` | 1 |
| `use-sound` | 1 |

## Best Landing Defaults

| Need | Candidate items | Notes |
| --- | --- | --- |
| Scroll story | `skiper16`, `skiper34`, `skiper87` | Use for section-by-section reveal, product narrative or proof progression. Require Lenis/reduced-motion fallback when used. |
| Short text motion | `skiper28`, `skiper31`, `skiper58` | Use for short hero phrases, labels or nav, not long body copy. |
| Metrics and progress | `skiper37`, `skiper89` | Use only with real metrics. Do not animate fake claims. |
| Media and proof carousel | `skiper47`, `skiper48`, `skiper49`, `skiper50`, `skiper51`, `skiper54` | Swiper/Embla cost accepted only for real galleries, testimonials, workflow cards or visual proof. |
| Product detail hover | `skiper52`, `skiper53`, `skiper64` | One focused hover/detail moment; mobile needs tap or static fallback. |
| Workflow UI detail | `skiper67`, `skiper101`, `skiper105`, `skiper106` | Good for product video, tooltip and input sections if the workflow is real. |
| Visual reference only | `skiper3`, `skiper63`, brand-named demos | Use as inspiration only unless adapted beyond recognition. |

## Reject Or Use Carefully

- Reject `/preview/skiper*` URLs as source evidence because all sitemap preview URLs returned 404.
- Reject `/r/*` and root `/registry.json` as install evidence.
- Reject premium, account-only, paid template, private source or Figma material unless the project has explicit access and permission.
- Reject any use that ignores the terms/access caveat or states MIT without proof.
- Reject Apple/Nike/Vercel-like brand demos unless the final result is visually and conceptually distinct.
- Reject `skiper17` and `skiper39` unless GSAP is already justified by the motion storyboard.
- Reject `skiper25` sound by default. If used, sound must be opt-in or muted by default.
- Reject `skiper61` mouse-follow effects for normal landing content.
- Reject `skiper65` and `skiper102` as public-facing landing UI unless used only for internal debugging.
- Reject Lenis/Swiper/GSAP when native CSS, Motion Primitives, Animate UI, SmoothUI or custom lightweight code covers the same effect.

## Selection Flow

1. Identify the section job and missing motion/detail.
2. Check native/local/shadcn, Animate UI, Motion Primitives, Magic UI, React Bits, SmoothUI, HextaUI and custom code first.
3. Decide whether Skiper is install source, reference-only, or rejected.
4. Verify exact endpoint `https://skiper-ui.com/registry/<name>.json`.
5. Record official namespace or exact URL command, dependencies, registry dependencies, terms/access gate, mobile behavior, reduced-motion fallback, performance risk and QA.
6. Map the item to `task-###` and `chg-###`.

## Required Project File

```text
projects/<slug>/44-skiper-ui-selection.md
```

The file must record exact item, source URL, endpoint URL, install command, access/license status, dependencies, registry dependencies, evidence path, visible purpose, adaptation, mobile behavior, reduced-motion fallback, performance risk, decision, task ID, change ID and QA evidence.
