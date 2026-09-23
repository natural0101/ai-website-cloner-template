# Section Pattern Library

Use this library when `06-section-by-section-upgrade-plan.md` needs concrete section ideas.

Every pattern must still be adapted to the product, audience, assets, and evidence.

## Hero Patterns

### Asymmetric Product Proof Hero

- Use for: SaaS, AI tools, B2B product, developer tool.
- Visible result: left side has outcome headline, short subhead, primary CTA; right side has real product screenshot, live component preview, or 3D object.
- Motion: hero text fades up once; product visual enters with 8 to 16px y offset; optional slow idle transform only after LCP.
- Inspiration sources: SaaS Landing Page, Saaspo, Land-book, direct competitors.
- Component source: native Tailwind, shadcn button, Animate UI/Motion Primitives for subtle reveal, React Bits only if one text/background moment is earned, Cult UI only for an exact hero/product detail, ReUI only for credible app UI proof, 21st.dev only after `39-twenty-first-dev-selection.md`, Kokonut UI only after `40-kokonut-ui-selection.md`, MVPBlocks only after `41-mvpblocks-selection.md`, SmoothUI only after `42-smoothui-selection.md`, HextaUI only after `43-hextaui-selection.md`, Skiper UI only after `44-skiper-ui-selection.md`, Eldora UI only after `45-eldora-ui-selection.md`, Blocks.so only after `46-blocks-so-selection.md`, Intent UI only after `47-intent-ui-selection.md`.
- Mobile: stack copy first, visual second, CTA remains visible.
- Avoid: fake dashboard, massive headline with tiny CTA, trust logos inside hero.

### Kinetic Type Hero

- Use for: agency, creative studio, editorial launch, brand-forward product.
- Visible result: typography is the main visual; one key word changes or reveals with purpose.
- Motion: text reveal, word swap, or mask reveal; reduced motion shows final phrase.
- Inspiration sources: Awwwards, Godly, Codrops, Motion docs.
- Component source: Motion Primitives, Magic UI text effects, React Bits text effects, Cult UI text/number details, SmoothUI text/number details only after `42-smoothui-selection.md`, PaceKit GSAP only for justified choreography, custom Motion.
- Mobile: fewer words, no clipped descenders.
- Avoid: unreadable type tricks, custom cursor by default, decorative scroll cues.

### 3D Object Hero

- Use for: product with memorable object, spatial concept, mascot, WebGL/Blender brand moment.
- Visible result: full or side hero with readable 3D object, not a tiny decorative model.
- Motion: slow idle, camera reveal, or one state change tied to story.
- Inspiration sources: Awwwards, Codrops, Three.js examples, Blender workbench renders.
- Component source: Three.js/WebGL, GLB, Blender static render fallback.
- Mobile: static render or simplified model.
- Avoid: blank canvas, unreadable object, heavy 3D without product meaning.

## Proof Patterns

### Logo Strip Under Hero

- Use for: real customer/company proof.
- Visible result: quiet row of real SVG logos below hero, no labels under each logo.
- Motion: optional fade-in only.
- Inspiration sources: direct competitors, SaaS galleries.
- Component source: native layout, Simple Icons/devicon if appropriate.
- Mobile: 2-column or horizontal scroll if many logos.
- Avoid: fake logos, text-only invented logos, industry labels under logos.

### Claim Proof Pair

- Use for: pages with strong claims needing evidence.
- Visible result: each claim sits next to proof: screenshot, testimonial, metric, or workflow.
- Motion: proof panel reveals after claim.
- Inspiration sources: CXL, Growth.Design, direct competitors.
- Component source: native layout, shadcn card only if card hierarchy is useful.
- Mobile: claim then proof, not side-by-side cramped.
- Avoid: fake metrics, vague "trusted by teams".

## Feature Patterns

### Bento With Real Visual Variation

- Use for: 4 to 6 capabilities that need scanning.
- Visible result: mixed cells with screenshot crop, icon, stat, diagram, and text.
- Motion: staggered reveal, no infinite loops.
- Inspiration sources: Land-book, Tailark, Aceternity, shadcnblocks.
- Component source: native CSS grid, shadcn, Tailark/shadcnblocks/MVPBlocks as structure, Cult UI texture/cards only after `37-cult-ui-selection.md`, ReUI app frames/data/forms only after `38-reui-selection.md`, 21st.dev community references only after `39-twenty-first-dev-selection.md`, Kokonut UI cards/inputs only after `40-kokonut-ui-selection.md`, SmoothUI cards/controls/blocks only after `42-smoothui-selection.md`, HextaUI app proof only after `43-hextaui-selection.md`, Skiper UI motion details only after `44-skiper-ui-selection.md`, Eldora UI device/proof/background details only after `45-eldora-ui-selection.md`, Blocks.so app/product proof blocks only after `46-blocks-so-selection.md`, Intent UI accessible controls/forms/tables only after `47-intent-ui-selection.md`; fill `32-tailark-section-selection.md` before using Tailark, `33-shadcnblocks-selection.md` before using shadcnblocks, `41-mvpblocks-selection.md` before using MVPBlocks, `42-smoothui-selection.md` before using SmoothUI, `43-hextaui-selection.md` before using HextaUI, `44-skiper-ui-selection.md` before using Skiper UI, `45-eldora-ui-selection.md` before using Eldora UI, `46-blocks-so-selection.md` before using Blocks.so and `47-intent-ui-selection.md` before using Intent UI.
- Mobile: single column with meaningful order.
- Avoid: six white text cards, empty bento cells, same background in every cell.

### Sticky Problem To Solution Stack

- Use for: explaining transformation across 3 to 5 steps.
- Visible result: left copy/story changes while right visual panel updates.
- Motion: scroll-triggered sticky stack only if it clarifies sequence.
- Inspiration sources: Codrops, Awwwards, GSAP ScrollTrigger docs.
- Component source: PaceKit GSAP or custom GSAP only for true pin/scrub/choreography, Motion for simple in-view steps.
- Mobile: plain stacked cards, no forced scroll hijack.
- Avoid: scroll effect with no story, broken pinning, hidden CTA.

### Product Flow Rail

- Use for: app/product onboarding or workflow.
- Visible result: 3 to 5 steps with real screenshots or screen states.
- Motion: active step changes preview; hover/tap feedback.
- Inspiration sources: Mobbin, Page Flows, Appcues/product-led onboarding.
- Component source: tabs, carousel, Animate UI, Motion Primitives, ReUI only for real app workflow previews, 21st.dev only for exact community workflow references, Kokonut UI only for exact small workflow details, SmoothUI only for exact animated workflow details, HextaUI only for exact app/SaaS workflow proof, Skiper UI only for one gated uncommon motion detail, Eldora UI only for exact product proof/device/text/background details, MVPBlocks only for real workflow or chatbot/dashboard proof, Blocks.so only for real onboarding/table/dialog/sidebar/AI/upload workflow proof, Intent UI only for real accessible forms/tables/menus/date controls.
- Mobile: swipeable screens or vertical steps.
- Avoid: fake UI rectangles, generic "Step 1".

## Pricing And Conversion Patterns

### Honest Pricing Focus

- Use for: SaaS with simple plans.
- Visible result: one recommended plan, clear difference, risk reversal, FAQ nearby.
- Motion: none or small hover/active feedback.
- Inspiration sources: SaaS Landing Page, Saaspo, direct competitors.
- Component source: shadcn, native cards.
- Mobile: plans stack with CTA visible.
- Avoid: confusing toggles, fake scarcity, too many decorative badges.

### Waitlist Minimal Conversion

- Use for: launch/waitlist/high-intent traffic.
- Visible result: short hero, one proof or product hint, email form, privacy reassurance.
- Motion: form feedback only.
- Inspiration sources: launch pages, Product Hunt examples, direct competitors.
- Component source: native form, shadcn input/button.
- Mobile: form is first-screen reachable.
- Avoid: long page, fake invite scarcity, beta labels if not true.

## FAQ And Objection Patterns

### Objection Accordion

- Use for: high-friction offers, pricing/security/fit questions.
- Visible result: 6 to 10 specific questions grouped by objection.
- Motion: accessible accordion open/close.
- Inspiration sources: CXL, Baymard for product/e-commerce, direct competitors.
- Component source: Animate UI accordion, shadcn accordion.
- Mobile: large touch targets.
- Avoid: generic FAQs that do not answer real buying friction.

## Final CTA Patterns

### Proof Echo CTA

- Use for: repeating the primary action after proof.
- Visible result: short headline restating outcome, same CTA label as hero, one proof reminder.
- Motion: simple reveal.
- Inspiration sources: high-conversion landing pages, CXL.
- Component source: native layout.
- Mobile: CTA not hidden below decorative asset.
- Avoid: new CTA intent, long manifesto, extra links.

## Pattern Selection Rule

For each selected pattern, record:

- pattern name;
- section;
- why it fits the offer/audience;
- inspiration URLs;
- visual result;
- motion purpose;
- asset requirement;
- component source;
- mobile fallback;
- risk and QA check.
