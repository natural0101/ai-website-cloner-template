# Component Source Registry

Use this registry after `motion-component-source-map` and before installing anything.

## Decision Rule

Pick the smallest source that solves the section need.

1. Existing project component.
2. Native Tailwind/CSS.
3. shadcn/ui owned primitive.
4. Animate UI for animated/headless primitives.
5. Motion Primitives for focused motion.
6. Magic UI for high-impact marketing effects.
7. Aceternity, Tailark and shadcnblocks for section structure or exact gated blocks with selection gates.
8. Kibo UI for exact product-interface components with endpoint and dependency gates.
9. Origin/Coss UI for exact micro-components with selection gates.
10. React Bits for one earned memorable animation/background with dependency and performance gates.
11. PaceKit GSAP for exact GSAP components only when GSAP choreography is justified.
12. Cult UI for exact textured/product-widget details with style and dependency gates.
13. ReUI for exact app/product UI details with free/pro access and license gates.
14. 21st.dev for community component discovery or exact install only after page, command, CDN registry, license and dependency gates.
15. Kokonut UI for exact small shadcn-compatible AI/button/card/navigation/text details with MIT/pro and motion gates.
16. MVPBlocks for exact section blocks, MVP templates and text animations after endpoint, CLI, license and dependency gates.
17. SmoothUI for exact animated controls, AI/product proof details, text effects or small blocks after endpoint, MIT, dependency and broken-blocks-API gates.
18. HextaUI for exact app/SaaS product-proof blocks after endpoint, MIT, dependency, HTML-doc caveat and demo-data gates.
19. Skiper UI for uncommon motion details after official registry, terms/access, broken-preview, dependency, reduced-motion and anti-copy gates.
20. Eldora UI for exact device/product proof frames, animated text/backgrounds and small section blocks after endpoint, MIT, runtime, demo-data and anti-template gates.
21. Blocks.so for exact app/product proof blocks after endpoint, MIT, duplicate-entry, dependency, demo-data and anti-fake-proof gates.
22. Intent UI for accessible React Aria app controls, forms, tables, menus and product-proof blocks after endpoint, MIT, dependency, example-page and accessibility gates.
23. GSAP, Three.js, Blender only for story-critical motion/3D.

## Sources

### Animate UI

- URL: https://animate-ui.com/
- Best for: animated primitives, headless/radix/base components.
- Use when: the page needs polished UI behavior without inventing from scratch.
- Risk: too many animated details can feel noisy.
- Install: exact registry item only.
- Current scan: 580 registry items total, 580/580 item endpoints live, 73 components, 81 primitives, 260 icons, 159 demos, 5 hooks, 1 lib, 1 index.
- Normal visual selection pool: 154 component/primitive entries. Hooks/lib are dependency helpers; icons are exact one-off installs.
- Planning file: `17-animate-ui-full-site-map.md`.
- Selection file: `projects/<slug>/14-animate-ui-selection.md`.
- Good landing defaults: accordion, tabs, tooltip, auto-height, fade/slide/zoom, highlight/shine, counting/sliding numbers, exact buttons.
- Avoid by default: custom cursor, fireworks, radial nav/menu, GitHub stars wheel outside devtool pages, sidebar on simple landing pages.

### Magic UI

- URL: https://magicui.design/
- Best for: hero effects, backgrounds, text effects, logo clouds.
- Use when: a marketing section needs one memorable animated moment.
- Risk: overuse makes the page look like a component demo.
- Install: exact component only.
- Current scan: 247 registry items total, 77 `registry:ui`, 168 examples, 1 style, 1 lib; 77 component docs and 9 template docs checked on 2026-07-03; MIT license.
- Install command: `npx shadcn@latest add "https://magicui.design/r/<item>.json"`.
- Planning file: `34-magic-ui-source-map.md`.
- Selection file: `projects/<slug>/30-magic-ui-selection.md`.
- Good landing defaults: `marquee`, `hero-video-dialog`, `bento-grid`, `blur-fade`, `number-ticker`, `animated-list`, `animated-beam`, `safari`, `iphone`, `terminal`, `highlighter`, one CTA button effect.
- Avoid by default: `smooth-cursor`, `pointer`, `dock`, `cool-mode`, decorative `confetti`, fake tweets/logos/integrations, excessive particles/meteors/grids/glow.

### Motion Primitives

- URL: https://motion-primitives.com/
- Best for: small Motion-based interactions, transitions, animated text/components.
- Use when: motion should be precise and local.
- Risk: stacking many small effects creates visual chatter.
- Current scan: GitHub/repo registry checked on 2026-07-03 after direct site crawl returned 429. Registry has 33 `registry:ui` items, MIT license, beta README status.
- Install: exact item through `npx motion-primitives@latest add <item>` or `npx shadcn@latest add "https://motion-primitives.com/c/<item>.json"`.
- Planning file: `33-motion-primitives-source-map.md`.
- Selection file: `projects/<slug>/29-motion-primitives-selection.md`.
- Good landing defaults: `animated-group`, `in-view`, `transition-panel`, `text-effect`, `animated-number`, `sliding-number`, `magnetic`, `image-comparison`, `scroll-progress`.
- Avoid by default: `cursor`, `dock`, `toolbar-*`, autoplay carousel, long paragraph text effects, excessive glow/tilt/spotlight.

### React Bits

- URL: https://www.reactbits.dev/
- Best for: exact animated React components, text animations, card/media interactions and backgrounds.
- Use when: a section needs one memorable visible moment that lower-risk native CSS, Motion Primitives, Animate UI or Magic UI cannot cover.
- Risk: many items use `ogl`, `gsap`, `three`, `@react-three/*`, canvas/WebGL, custom cursors, physics or pointer tracking. Use a heavy-runtime gate.
- Current scan: sitemap has 141 URLs; `llms.txt` maps 23 text animations, 30 animations, 36 components and 45 backgrounds. `https://reactbits.dev/r/registry.json` returned 536 `registry:component` items, representing 134 unique components in `JS-CSS`, `JS-TW`, `TS-CSS`, `TS-TW` variants. License is MIT + Commons Clause.
- Install command: `npx shadcn@latest add https://reactbits.dev/r/<Component>-TS-TW`.
- Planning file: `39-react-bits-source-map.md`.
- Selection file: `projects/<slug>/35-react-bits-selection.md`.
- Good landing defaults: `BlurText`, `GradientText`, `RotatingText`, `CountUp`, `Counter`, `AnimatedList`, `FadeContent`, `Magnet`, `GlareHover`, `SpotlightCard`, `TiltedCard`, quiet `Aurora` or `DotGrid`.
- Avoid by default: custom cursors, WebGL/3D/shader backgrounds, physics/game effects, long paragraph effects, autoplay galleries that hide proof and any heavy dependency without mobile/performance QA.

### Hover.dev

- URL: https://www.hover.dev/
- Best for: reference-only interaction patterns, hover states, hero/nav/cards/pricing/forms/testimonials and small 3D inspiration.
- Use when: a section needs interaction inspiration or a manually copied free/licensed component.
- Risk: freemium/pro access, no verified registry, license forbids standalone resale/redistribution, guessed category URLs can 404, hover gimmicks can overpower content.
- Current scan: sitemap has 36 URLs including 30 `/components/*` category URLs. License page returned 200 and says free components need no signup/purchase, non-free components require Hover Pro, commercial/non-commercial use and modification are allowed, attribution is not required, and standalone sale/redistribution is not permitted.
- Install/copy: no registry install path verified. Treat as reference-only unless the exact component is free or Pro access/license is explicit; record copied files and adaptation in the relevant section/micro-component selection file.
- Good landing defaults: button hover, link hover, card hover, nav details, testimonials, pricing, form details.
- Avoid by default: loaders, custom cursor-like interactions, heavy 3D, copied templates, Pro items without access/license.

### PaceKit GSAP

- URL: https://gsap.pacekit.dev/
- Former/broken URL: https://ui.paceui.com/
- Best for: exact GSAP-powered text effects, scroll/stagger reveals, stacked card motion, button tactility and AI/product state writing.
- Use when: GSAP sequencing, timeline control or scroll choreography is explicitly needed and accepted.
- Risk: 26 of 28 UI items depend on `gsap` and `@gsap/react`; old Pace UI URL is dead; guessed `paceui.com/r/gsap/*` endpoints are invalid; custom cursor/liquid/glass/loader items can damage UX.
- Current scan: live registry `https://gsap.pacekit.dev/r/registry.json` has 29 items: 1 `registry:style`, 28 `registry:ui`. `public/r` in `pacekit/gsap` has 30 JSON files including `registry.json` and `mcp.json`. `LICENSE.md` is MIT.
- Install command: `npx shadcn@latest add https://gsap.pacekit.dev/r/<item>.json`.
- Planning file: `40-pacekit-gsap-source-map.md`.
- Selection file: `projects/<slug>/36-pacekit-gsap-selection.md`.
- Good landing defaults: `reveal-text`, `scramble-text`, `draw-line-text`, `flip-reveal`, `reveal-on-scroll`, `stagger-on-scroll`, `animated-stack`, `layered-stack`, `spring-button`, `fillable-button`, `tilt-card`, truthful `ai-response-writer`.
- Avoid by default: `liquid-cursor`, trend-only `liquid-glass`, loaders, fake AI controls, simple reveals that CSS/Motion can handle.

### Cult UI

- URL: https://www.cult-ui.com/
- Best for: textured cards/buttons, product proof frames, browser/code/terminal mockups, polls, onboarding, animated numbers/text, hover media and quiet background texture.
- Use when: one exact component improves product proof, CTA tactility, surface richness or interaction clarity.
- Risk: shader/3D/heavy hero components, trend surfaces, fake social proof, and dependency-heavy widgets can overwhelm the offer.
- Current scan: sitemap has 87 URLs; live registry `https://www.cult-ui.com/r/registry.json` has 157 items: 78 `registry:ui`, 79 `registry:component` demo/example entries. All 157 item endpoints returned 200. Root `/registry.json` returned 404. GitHub repo `nolly-studio/cult-ui` and raw `LICENSE.md` returned 200; license is MIT.
- Install command: `npx shadcn@latest add https://cult-ui.com/r/<item>.json` or configure `"@cult-ui": "https://cult-ui.com/r/{name}.json"` and use `npx shadcn@latest add @cult-ui/<item>`.
- Planning file: `41-cult-ui-source-map.md`.
- Selection file: `projects/<slug>/37-cult-ui-selection.md`.
- Good landing defaults: `mock-browser-window`, `code-block`, `terminal-animation`, `texture-button`, `cosmic-button`, `texture-card`, `minimal-card`, `shift-card`, `animated-number`, `text-animate`, `gradient-heading`, `choice-poll`, `feature-poll`, `onboarding`, `bg-image-texture`, `texture-overlay`.
- Avoid by default: `dock`, `dynamic-island`, `loading-carousel`, `toolbar-expandable`, `sortable-list`, `shader-lens-blur`, shader hero variants, `canvas-fractal-grid`, `grid-beam`, fake `tweet-grid`, AI widgets without real product workflow, and `registry:component` demos as production code.

### ReUI

- URL: https://reui.io/
- Best for: realistic SaaS/app interface details, forms, data grids, tables, filters, file upload, frames, alerts, ratings, timelines, dashboard/admin/product previews.
- Use when: a section needs credible product UI proof or an app workflow that local shadcn/custom components would take too long to build.
- Risk: premium blocks/icons/templates require license key; root registry indexes return 401; data-grid/drag/sortable stacks can be heavy; many items duplicate shadcn primitives.
- Current scan: sitemap has 209 URLs; component page scan found 1019 `c-*` variant names across 69 component pages. Exact samples `https://reui.io/r/radix-nova/c-button-1.json`, `c-data-grid-1.json`, and `alert.json` returned 200 JSON. Root `/registry.json` returned 404, and root/style registry indexes returned 401 without license. License page allows own/client projects but forbids repackaging licensed materials.
- Install command: configure `"@reui": "https://reui.io/r/{style}/{name}.json"` and use `npx shadcn@latest add @reui/c-alert-1`, or exact URL `npx shadcn@latest add https://reui.io/r/radix-nova/c-alert-1.json`.
- Planning file: `42-reui-source-map.md`.
- Selection file: `projects/<slug>/38-reui-selection.md`.
- Good landing defaults: `frame`, `c-frame-*`, `data-grid`, `c-data-grid-*`, `table`, `filters`, `field`, `input`, `select`, `combobox`, `file-upload`, `alert`, `c-alert-*`, `rating`, `progress`, `stepper`, `timeline`.
- Avoid by default: premium blocks/icons/templates without license, root registry indexes, heavy data-grid/drag stacks for decoration, and ReUI primitives that duplicate existing shadcn/local UI without visible improvement.

### 21st.dev

- URL: https://21st.dev/
- Best for: reference mining or exact community component selection for hero, background, shader, AI-chat, CTA, pricing, feature, product-widget and app-like details.
- Use when: a section needs a concrete community pattern or effect and existing native/shadcn/Motion/Animate UI/Magic UI/ReUI sources are not a better fit.
- Risk: huge community marketplace, uneven quality, hidden Next payload install metadata, heavy WebGL/Three/HeroUI/chart/icon dependencies, unclear license on some items and visual style drift.
- Current scan: sitemap has 9384 URLs, including 8260 author/component pages and 1000 tag/category pages. Sample component pages expose CDN registry JSON that returned 200. Generic `/r/shadcn/*` guesses returned 403 and must not be used as install evidence.
- Install command: `npx @21st-dev/cli@beta add <author>/<component>`, only after exact component page is verified.
- Planning file: `43-21st-dev-source-map.md`.
- Selection file: `projects/<slug>/39-twenty-first-dev-selection.md`.
- Good landing defaults: `/community/components/s/hero`, `/background`, `/shader`, `/ai-chat`, `/features`, `/call-to-action`, `/pricing-section`, exact product widgets such as tables, calendars and sparklines after dependency review.
- Avoid by default: broad imports, generic `/r/*` guesses, heavy effects for decoration, unclear license items and community styling that overrides the landing brand.

### Kokonut UI

- URL: https://kokonutui.com/
- Best for: small polished shadcn-compatible AI inputs, animated buttons, cards, navigation details, file upload, background accents and text effects.
- Use when: one exact public component speeds up a specific section job and lower-risk existing sources are not a better fit.
- Risk: most items use `motion`; Pro/templates are separate; liquid glass, tweet cards, loaders and fake AI can weaken landing credibility.
- Current scan: sitemap has 49 URLs; public registry has 40 `registry:component` items; all 40 item endpoints returned 200. GitHub license is MIT. `kokonutui.pro/r/registry.json` returned 404 HTML.
- Install command: `npx shadcn@latest add @kokonutui/<name>` or exact URL `npx shadcn@latest add https://kokonutui.com/r/<name>.json`.
- Planning file: `44-kokonut-ui-source-map.md`.
- Selection file: `projects/<slug>/40-kokonut-ui-selection.md`.
- Good landing defaults: `ai-prompt`, `ai-input-search`, `file-upload`, `bento-grid`, `currency-transfer`, `carousel-cards`, `spotlight-cards`, `particle-button`, `gradient-button`, `hold-button`, `action-search-bar`, `smooth-tab`, `shape-hero`, `shimmer-text`.
- Avoid by default: Pro items without access, `liquid-glass-card`, `tweet-card`, loaders, fake AI, decorative `motion` where CSS or existing components suffice.

### MVPBlocks

- URL: https://blocks.mvp-subha.me/
- Best for: exact section blocks, MVP templates, hero/pricing/FAQ/CTA/testimonial/header/footer/bento/dashboard/chatbot and text animation references.
- Use when: a landing needs fast section structure and lower-risk sources do not solve the same job with better brand fit.
- Risk: broad template identity copying, demo copy, fake proof, Framer Motion/GSAP/dashboard/chatbot dependencies, Next-specific imports and root registry guesses.
- Current scan: sitemap has 96 URLs, `llms.txt` and `llms-full.txt` are live, npm package `mvpblocks` is version 2.1.13, GitHub repo license is BSD-3-Clause, package metadata says MIT. CLI constants list 252 items: 77 `registry:ui`, 171 `registry:block`, 3 hooks and 1 lib. All 252 exact endpoints `https://blocks.mvp-subha.me/r/<name>.json` returned 200. Root `/r/registry.json` and `/registry.json` returned 404.
- Install command: `npx mvpblocks add <name> --ts`.
- Exact URL form: `npx shadcn@latest add https://blocks.mvp-subha.me/r/<name>.json`.
- Planning file: `45-mvpblocks-source-map.md`.
- Selection file: `projects/<slug>/41-mvpblocks-selection.md`.
- Good landing defaults: `hero-1`, `minimal-hero`, `gradient-hero`, `mockup-hero`, `feature-*`, `bento-grid-*`, `cta-*`, `faq-*`, `simple-pricing`, `technical-pricing`, `testimonials-carousel`, `header-*`, `footer-*`, short text effects.
- Avoid by default: root registry indexes, `target-cursor`, loaders, copied full templates, 3D/globe/Web3 hero, fake AI/chatbot/dashboard proof and heavy dependencies without mobile/performance QA.

### SmoothUI

- URL: https://smoothui.dev/
- Best for: exact animated shadcn-compatible controls, product UI details, AI UI accents, text effects and small landing blocks.
- Use when: a section needs one polished interaction or a small block and native/local/shadcn, Animate UI, Motion Primitives, Magic UI, Kokonut UI or MVPBlocks is not a better fit.
- Risk: most items use `motion`; some social/AI/proof components can create fake product evidence; `gooey-popover` brings `gsap`; `tweet-card` brings `react-tweet`; blocks API is currently not usable.
- Current scan: sitemap has 110 URLs; `llms.txt`, `llms-full.txt`, `llms-components.json`, `openapi.json` and `https://smoothui.dev/r/registry.json` are live. Registry has 107 items, and all 107 exact endpoints returned 200. Component API returns 72 components; practical registry split is 72 components plus 35 block/shared items. GitHub and npm package metadata report MIT. `/registry.json` returned 404. `/api/v1/blocks` returned an empty list, and block item API guesses returned 500.
- Install command: `npx shadcn@latest add @smoothui/<name>` or `npx smoothui-cli@latest add <name>`.
- Exact URL form: `npx shadcn@latest add https://smoothui.dev/r/<name>.json`.
- Planning file: `46-smoothui-source-map.md`.
- Selection file: `projects/<slug>/42-smoothui-selection.md`.
- Good landing defaults: `smooth-button`, `magnetic-button`, `animated-input`, `animated-file-upload`, `animated-tabs`, `animated-stepper`, `number-flow`, `price-flow`, `reveal-text`, `typewriter-text`, `wave-text`, `ai-input`, `siri-orb`, `product-card`, `switchboard-card`, `header-*`, `cta-*`, `features-*`, `pricing-*`, `faq-*`, `testimonials-*`, `footer-*`.
- Avoid by default: blocks API evidence, root registry guesses, `cursor-follow`, loaders, fake tweets/reviews/stars/logos, fake AI widgets, broad shadcn primitive replacement and any `hasReducedMotion=false` item without custom fallback.

### HextaUI

- URL: https://www.hextaui.com/
- Best for: app/SaaS product-proof blocks, AI workflow UI, auth/onboarding, billing/pricing/subscription, settings/admin, team/task/project screens and exact foundation components.
- Use when: a section needs credible app UI proof and local shadcn/custom, ReUI, MVPBlocks, SmoothUI or Kokonut UI does not already solve it with lower risk.
- Risk: many blocks create fake product surfaces if demo data is not replaced; foundation items duplicate shadcn; individual HTML docs pages can time out; dense app blocks can fail mobile.
- Current scan: sitemap child has 143 URLs, `llms.txt` and RSS are live, public registry has 139 `registry:ui` items, and all 139 exact endpoints returned 200. Official shadcn registry index maps `@hextaui` to `https://hextaui.com/r/{name}.json`. GitHub license is MIT. `/registry.json` and `registry.hextaui.com/r/registry.json` returned 404. Many individual HTML detail pages timed out during audit, so use registry, `llms.txt` and GitHub evidence.
- Install command: `npx shadcn@latest add @hextaui/<name>`.
- Exact URL form: `npx shadcn@latest add https://hextaui.com/r/<name>.json`.
- Planning file: `47-hextaui-source-map.md`.
- Selection file: `projects/<slug>/43-hextaui-selection.md`.
- Good landing defaults: `ai-prompt-input`, `ai-message`, `ai-conversation`, `ai-model-selector`, `ai-usage-quota`, `billing-pricing-table`, `billing-plan-selector`, `billing-subscription-card`, `billing-usage-billing`, `auth-login-form`, `auth-signup-form`, `settings-api-keys`, `settings-integrations`, `settings-team-members`, `team-dashboard`, `team-permissions-matrix`, `task-board`, `task-list`, `project-list`.
- Avoid by default: timed-out HTML pages as sole proof, root registry guesses, broad primitive replacement, fake AI/auth/billing/team/task surfaces, heavy app dependencies without product reason and dense layouts without mobile simplification.

### Skiper UI

- URL: https://skiper-ui.com/
- Best for: uncommon motion details, scroll stories, short text motion, real metric/progress animation, proof/media carousels, video, tooltip and input details.
- Use when: a section needs one distinctive motion/detail and native CSS, existing components, Animate UI, Motion Primitives, Magic UI, React Bits, SmoothUI, HextaUI or custom code is not a better fit.
- Risk: Premium/Exclusive access, restrictive terms language, no verified MIT source repo, broken preview URLs, unstable large HTML GET requests, Lenis/Swiper/GSAP cost and recognizable brand-like demos.
- Current scan: official shadcn registry index maps `@skiper-ui` to `https://skiper-ui.com/registry/{name}.json`; public registry has 38 `registry:ui` items; 38/38 exact item endpoints returned 200 on `HEAD`; sitemap has 218 URLs, but all 105 `/preview/skiper*` URLs returned 404. `/r/*` and root `/registry.json` are wrong paths.
- Access/license: not treated as MIT. Use only public registry items after terms/access gate; never copy premium, account-only, paid template, private source or Figma material.
- Install command: `npx shadcn@latest add @skiper-ui/<name>`.
- Exact URL form: `npx shadcn@latest add https://skiper-ui.com/registry/<name>.json`.
- Planning file: `48-skiper-ui-source-map.md`.
- Selection file: `projects/<slug>/44-skiper-ui-selection.md`.

### Eldora UI

- URL: https://eldoraui.site/
- Best for: device/browser mockups, terminal/GitHub proof, integrations/globe/map visuals, animated text, CTA/status details, backgrounds and small section blocks.
- Use when: a landing needs exact product proof framing or one polished visual/motion detail and local/native, Animate UI, Motion Primitives, SmoothUI, Skiper UI, HextaUI, MVPBlocks or custom code is not a better fit.
- Risk: examples are not normal install choices, section blocks can become template identity, device frames and proof widgets can create fake evidence, and globe/background dependencies can be heavy.
- Current scan: official shadcn registry index maps `@eldoraui` to `https://eldoraui.site/r/{name}.json`; public registry has 115 items; 115/115 exact endpoints returned 200; sitemap has 56 URLs with all 56 returning 200 on `HEAD`; `llms.txt` is live; GitHub license is MIT. Wrong path `https://eldoraui.site/registry/<name>.json` returned 404 on sampled items.
- Install command: `npx shadcn@latest add @eldoraui/<name>`.
- Exact URL form: `npx shadcn@latest add https://eldoraui.site/r/<name>.json`.
- Planning file: `49-eldora-ui-source-map.md`.
- Selection file: `projects/<slug>/45-eldora-ui-selection.md`.

### Blocks.so

- URL: https://blocks.so/
- Best for: app/product proof blocks: stats, auth/login, onboarding, tables, dialogs, sidebars, AI chat, command menus, file upload, form layouts and grid lists.
- Use when: a landing section needs credible product UI proof and local shadcn/custom, ReUI, HextaUI, MVPBlocks, SmoothUI or Eldora UI does not already solve it with lower risk.
- Risk: demo metrics, fake users, fake AI chats, fake file names, fake tables and generic dashboard chrome can weaken credibility if not replaced with real project content.
- Current scan: official shadcn registry index maps `@blocks-so` to `https://blocks.so/r/{name}.json`; sitemap has 88 URLs with 88/88 returning 200 on `HEAD`; GitHub raw registry has 77 `registry:block` entries but 76 unique install names because `file-upload-01` is duplicated; 76/76 unique live item endpoints returned 200. Live `GET /r/registry.json` returned `ECONNRESET`; use GitHub raw `public/r/registry.json` for catalog rebuilds.
- License: MIT via GitHub API and raw `LICENSE.md`.
- Install command: `npx shadcn@latest add @blocks-so/<name>`.
- Exact URL form: `npx shadcn@latest add https://blocks.so/r/<name>.json`.
- Planning file: `50-blocks-so-source-map.md`.
- Selection file: `projects/<slug>/46-blocks-so-selection.md`.
- Good landing defaults: `stats-*`, `onboarding-*`, `table-*`, `dialog-*`, `command-menu-*`, `file-upload-*`, `form-layout-*`, `grid-list-*`, and `ai-*` only for real AI workflows.
- Avoid by default: fake dashboards, login blocks as generic CTA, sidebars as decoration, AI/file/table blocks without real product relevance, and heavy dependencies such as `recharts`, `@tanstack/react-table`, `react-dropzone`, `ai` or `framer-motion` without explicit section need.

### Intent UI

- URL: https://intentui.com/
- Best for: accessible app controls, form-heavy product proof, date/time/color controls, tables, command menus, overlays, navbars, sidebars, charts and auth blocks.
- Use when: a section needs real product UI behavior and local shadcn/Radix/native, Origin/Coss, Kibo UI, ReUI, HextaUI, Blocks.so or custom code does not solve it with lower dependency risk.
- Risk: React Aria Components stack can be a broad dependency shift; `registry:page` examples are not production source; `all` and theme packs are bulk installs; color/date/chart/table controls can be overkill.
- Current scan: sitemap has 108 URLs with 108/108 returning 200 on `HEAD`; `llms.txt` is live; GitHub repo `intentui/intentui` is MIT and default branch `3.x`; raw registry `3.x/registry.json` has 569 items: 88 `registry:ui`, 438 `registry:page`, 25 `registry:block`, 12 themes, 3 hooks, 2 libs and 1 `all` item. 569/569 live `/r/<name>.json` endpoints returned 200 on `HEAD`. Live `GET /r/registry.json` returned `ECONNRESET`; use GitHub raw for catalog rebuilds.
- Install command: `npx shadcn@latest add @intentui/<name>`.
- Exact URL form: `npx shadcn@latest add https://intentui.com/r/<name>`.
- Planning file: `51-intent-ui-source-map.md`.
- Selection file: `projects/<slug>/47-intent-ui-selection.md`.
- Good landing defaults: `field`, `text-field`, `select`, `combo-box`, `date-picker`, `table`, `grid-list`, `command-menu`, `dialog`, `sheet`, `drawer`, `navbar`, `sidebar`, `auth-*`, `chart-*`.
- Avoid by default: `all`, broad theme entries, `registry:page` examples as production source, paid `design.intentui.com` material without access, fake data/forms/charts and React Aria stack when simpler shadcn/local code is enough.

### Aceternity UI

- URL: https://ui.aceternity.com/
- Best for: landing sections, bento, parallax, hover effects, hero ideas.
- Use when: prototyping a section that needs strong visual structure.
- Risk: recognizable style. Adapt heavily.
- Current scan: 270 registry items total, 109 `registry:ui`, 161 `registry:block`; 118 component pages found; `/registry.json` and `/registry/<name>.json` are the live registry paths.
- Install command: `npx shadcn@latest add @aceternity/<item>` or `npx shadcn@latest add https://ui.aceternity.com/registry/<item>.json`.
- Planning file: `35-aceternity-ui-source-map.md`.
- Selection file: `projects/<slug>/31-aceternity-ui-selection.md`.
- Good landing defaults: `bento-grid`, `hero-parallax`, `parallax-hero-images`, `sticky-scroll-reveal`, `tracing-beam`, `timeline`, `compare`, `animated-testimonials`, `card-hover-effect`, `hero-highlight`, `safari`, `terminal`, `magnetic-button`.
- Avoid by default: `registry:block` without license/access, following pointer, floating dock/navbar, loaders, heavy particles/shaders/Three/canvas effects, fake testimonials/logos/screenshots.

### Tailark

- URL: https://tailark.com/
- Best for: marketing blocks, SaaS pages, pricing, FAQ, testimonials, CTA, auth, contact and footer sections.
- Use when: section structure is the gap, not animation.
- Risk: stale sitemap preview URLs, recognizable block look, Pro/API-key access and dependency drift.
- Current scan: public sitemap has 208 URLs with 18 live category/home URLs and 190 stale preview 404s. Public raw registry has 154 items: 20 `registry:ui` and 134 `registry:block`. Veil raw registry has 76 items: 19 `registry:ui` and 57 `registry:block`. Pro sitemap has 621 URLs, with 547 live after URL normalization and 74 `/pages/*` 404s.
- Install command: configure `"@tailark": "https://tailark.com/r/{name}.json"`, then use `pnpm dlx shadcn add @tailark/<item>`.
- Live item registry path: `https://tailark.com/r/<item>.json`.
- Planning file: `36-tailark-section-source-map.md`.
- Selection file: `projects/<slug>/32-tailark-section-selection.md`.
- Good landing defaults: `hero-section`, `features`, `pricing`, `faqs`, `logo-cloud`, `testimonials`, `stats`, `call-to-action`, `footer`, `contact`, auth sections.
- Avoid by default: Pro blocks/pages/illustrations without explicit access, old `/preview/<category>/<Title> (dusk-kit)` URLs, root `/registry.json`, demo copy/logos/screenshots, and full visual identity copy.

### Origin UI

- URL: https://coss.com/ui
- Former URL: https://originui.com/
- Best for: accessible small components, Base UI-inspired primitives, forms, commands, popovers, calendars, upload/file UI, tables and app UI details.
- Use when: forms, inputs, menus, tooltips, overlays need polish.
- Risk: Origin domain redirects to Coss, some `originui.com/r/*` endpoints return HTML, not JSON. Do not mix component systems without reason.
- Current scan: GitHub registry has 646 items: 40 `registry:ui`, 600 `registry:component`, 5 hooks and 1 lib. Live Coss endpoints such as `https://coss.com/ui/r/accordion.json` and `https://coss.com/ui/r/button.json` returned JSON. Origin UI is MIT.
- Install/copy: prefer verified `https://coss.com/ui/r/<item>.json` if it returns JSON; otherwise use GitHub registry/copy source with explicit file and CSS-token review.
- Planning file: `38-micro-component-source-map.md`.
- Selection file: `projects/<slug>/34-micro-component-selection.md`.

### shadcnblocks

- URL: https://www.shadcnblocks.com/
- Best for: shadcn landing blocks, app sections, ecommerce sections, pages, templates and extra components.
- Use when: the page needs a proven section structure or exact shadcn-compatible block faster than custom composition.
- Risk: block-level sameness, large Pro/Premium surface, Commons Clause restrictions, API-key access, and dependency drift.
- Current scan: sitemap has 3912 URLs; bounded HEAD crawl found 3908 live and 4 broken. Live item pages include 1645 `/block/*`, 1684 `/component/*`, 47 `/page/*`, and 16 `/template/*`. Free page links 106 free blocks. Public root `/registry.json` returned 404. Free registry examples `hero1` and `feature1` returned 200; Pro examples `hero125` and `pricing1` returned 401 without API key.
- Install command: configure `"@shadcnblocks": "https://www.shadcnblocks.com/r/{name}.json"`, then use `npx shadcn@latest add @shadcnblocks/<item>`.
- Pro install requires `SHADCNBLOCKS_API_KEY` and bearer headers.
- Planning file: `37-shadcnblocks-source-map.md`.
- Selection file: `projects/<slug>/33-shadcnblocks-selection.md`.
- Good landing defaults: free `hero*`, `feature*`, `pricing*`, `faq1`, `cta*`, `logos*`, `testimonial*`, `navbar1`, `footer2`, contact, book-a-demo, case study, compliance, ecommerce and app preview blocks.
- Avoid by default: Pro/Premium items without access/license, broken sitemap URLs, guessed registry IDs, demo copy/logos/screenshots/claims, reusable component kit redistribution, and generic block-library rhythm.

### Kibo UI

- URL: https://www.kibo-ui.com/
- Best for: exact shadcn-compatible product UI details: code blocks, snippets, sandboxes, tables, kanban, tree, calendars, combobox, dropzone, image tools, media player, ratings, tags, status, banners and proof widgets.
- Use when: a landing needs credible product-interface proof and a local shadcn/custom component would take longer or be less faithful.
- Risk: many items are real app components with heavier dependencies; live registry body can stream slowly; guessed item names can return package errors; `editor`, `gantt` and `reel` need fresh body-fetch/source-adaptation proof before use.
- Current scan: `https://www.kibo-ui.com/r/registry.json` returns 200 on `HEAD`, but body can time out after partial JSON. Root `/registry.json` returns 404. 37 exact item endpoints parsed cleanly; `editor`, `gantt` and `reel` return `HEAD 200` but body timed out during the audit. GitHub package manifests and MIT license are live.
- Install command: `npx shadcn@latest add https://www.kibo-ui.com/r/<item>.json`.
- Planning file: `38-micro-component-source-map.md`.
- Selection file: `projects/<slug>/34-micro-component-selection.md`.
- Skill: `kibo-ui-catalog`.
- Good landing defaults: `announcement`, `banner`, `avatar-stack`, `rating`, `tags`, `status`, `relative-time`, `ticker`, `code-block`, `snippet`, `combobox`, `choicebox`, `dropzone`, `image-zoom`, `table`, `tree`, `contribution-graph`.
- Avoid by default: guessed `button`/`accordion`/`ai-input` endpoints, `cursor`, `editor`, `gantt`, `reel`, `kanban`, `video-player`, `calendar`, Shiki/Sandpack/Tiptap/table/media/drag-drop stacks unless the landing truly previews product UI.

## Install Checklist

Before installing or copying:

- Source URL recorded in `evidence/reference-manifest.md`.
- License/access checked.
- Dependency impact listed in `08-component-and-asset-plan.md`.
- Motion purpose listed if animated.
- Reduced-motion fallback planned.
- Mobile behavior planned.
- No duplicate library already solves it.
