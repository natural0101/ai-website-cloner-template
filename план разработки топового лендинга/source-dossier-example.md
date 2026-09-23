# Source Dossier Example

This is a compact example of the expected shape. Replace all content with real project evidence.

## 1. Product Snapshot

- product/service: Example AI meeting notes app.
- target audience: remote product and sales teams.
- primary CTA: Start free.
- conversion goal: account signup.
- offer: automatic meeting notes, action items, and searchable summaries.
- traffic/source assumption: organic search and founder-led social posts.
- known constraints: preserve route `/`, keep existing signup form field names.
- current quality level: functional but generic.

## 2. Current Site Map

- routes: `/`
- main files: `src/app/page.tsx`, `src/app/globals.css`
- landing components: `Hero`, `Features`, `Pricing`, `FAQ`
- shared UI components: `Button`, `Card`
- assets: logo SVG, two product screenshots
- SEO files: `src/app/layout.tsx`
- analytics/form integrations: signup button event name `signup_click`
- UI/motion dependencies: Tailwind, shadcn/ui, motion

## 3. Current Landing Structure

### Hero

- section ID/name: hero
- file/component: `src/components/Hero.tsx`
- current purpose: explain product and send users to signup.
- visible copy: "AI notes for every meeting"
- CTA/proof/assets: Start free, product screenshot.
- layout: centered headline and screenshot card.
- mobile behavior: screenshot becomes narrow but text remains readable.
- what works: clear category.
- what is weak: no audience, no proof, generic screenshot treatment.

## 4. Visual Audit

- typography: default sans, weak hierarchy.
- color palette: blue accent on white.
- spacing/rhythm: sections use same padding and same card grid.
- layout families: centered hero, three-card features, FAQ accordion.
- imagery/3D/video: one screenshot.
- motion/interactions: hover transitions only.
- mobile issues: CTA row wraps.
- responsive/viewport issues: mobile CTA wraps and wide desktop hero feels sparse.
- hero first viewport: desktop shows headline, CTA and screenshot; mobile pushes screenshot partly below fold.
- nav height/behavior: simple top nav, about 64px on desktop, collapses acceptably on mobile.
- text wrapping or overflow issues: CTA row wraps awkwardly at 390px.
- asset crop issues: screenshot loses side navigation detail on mobile.
- accessibility issues: weak focus states.
- manual accessibility notes: keyboard focus visible on CTA, weak on FAQ trigger; contrast not measured.
- heuristic issues by severity: major relevance issue in hero, minor CTA wrap issue, cosmetic repeated card rhythm.
- CTA/conversion friction: CTA is visible but not supported by proof above the fold.
- trust/proof gaps: no customer logos, metrics, quotes or security proof visible.
- performance risks: screenshot has no reserved aspect ratio.

## 5. Evidence Inventory

- live URL or local preview URL: `http://localhost:3000/`
- desktop screenshot path or unavailable reason: `evidence/screenshots/current-home-desktop-full.png`
- mobile screenshot path or unavailable reason: `evidence/screenshots/current-home-mobile-full.png`
- hero/above-fold screenshot path or unavailable reason: `evidence/screenshots/current-home-hero-desktop.png`
- desktop viewport: 1440 x 1000.
- mobile viewport: 390 x 844.
- tablet/wide viewport or unavailable reason: tablet not captured, wide not captured.
- first viewport notes: hero needs CTA and product screenshot subject visible at desktop and mobile.
- horizontal overflow check: no obvious horizontal overflow at 390px, but CTA wrap needs review.
- source files inspected: `src/app/page.tsx`, `src/components/Hero.tsx`, `src/app/globals.css`, `public/`.
- CSS/token evidence: blue accent, white background, 12px card radius, default sans, repeated 3-card grids.
- asset paths inspected: `public/logo.svg`, `public/screenshots/dashboard.png`.
- commands run and result: `npm run check` passed.
- console errors or unavailable reason: console not checked.
- Lighthouse report/path or unavailable reason: Lighthouse not run.
- manual accessibility check result: keyboard spot-check only; contrast not measured.
- heuristic evaluation notes: hero violates match-to-audience and recognition-over-recall because the category is clear but audience/proof is generic.
- browser/Lighthouse/Playwright availability: dev server and browser screenshot available, Lighthouse not run.
- unknowns: real customer logos and pricing claims.

## 6. Brand And Content Preservation

- copy to preserve: product name and signup CTA.
- routes/slugs/anchors to preserve: `/`, `#pricing`, `#faq`
- nav labels to preserve: Pricing, FAQ
- form fields to preserve: `email`
- analytics-sensitive labels: `signup_click`
- legal/SEO copy: privacy link.
- brand assets: logo SVG.
- do-not-change notes: do not remove existing signup form integration.

## 7. Upgrade Opportunities

1. problem: hero does not name the audience.
   severity: major.
   possible improvement: rewrite headline for remote teams.
   expected user impact: faster relevance.
   affected section: hero.
   heuristic/source principle: match between system and real world, recognition rather than recall.
   risk: if traffic is broader, audience may feel narrow.
   evidence: current hero screenshot and copy.

## 8. Reference Hooks

- URL: https://saaslandingpage.com/
  why relevant: SaaS section structure reference.
  borrow: proof placement and section hierarchy.
  do not copy: exact branding.
  section mapping: hero, proof, pricing.
- URL: https://motion.dev/
  why relevant: official motion implementation reference.
  borrow: reduced-motion aware UI animation patterns.
  do not copy: generic animation without section purpose.
  section mapping: hero reveal and FAQ interaction.
- URL: https://www.nngroup.com/articles/ten-usability-heuristics/
  why relevant: heuristic evaluation baseline.
  borrow: consistency, feedback, and recognition-over-recall checks.
  do not copy: treat heuristics as absolute conversion proof.
  section mapping: form, nav, FAQ.

## 9. Technical Constraints

- framework: Next.js.
- package manager: npm.
- build/dev/check commands: `npm run check`.
- installed UI libraries: shadcn/ui.
- installed animation libraries: motion.
- styling system: Tailwind.
- known errors: none observed.
- files risky to edit: signup form component.
- browser/screenshot availability: dev server available.

## 10. Handoff Summary

- best redesign mode: targeted evolution.
- recommended vibe: clean SaaS with restrained motion.
- recommended motion intensity: 5.
- recommended asset direction: real screenshot with annotated states.
- recommended first tasks: hero copy, screenshot treatment, proof row, feature rhythm, FAQ polish.
- open questions: real customer logos?
- assumptions: no paid plan launch yet.
