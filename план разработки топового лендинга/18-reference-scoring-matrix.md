# Reference Scoring Matrix

Дата обновления: 2026-07-03.

Эта матрица нужна перед visual direction и section storyboard. Она защищает план от случайного inspiration: красивый сайт может быть плохим reference для конкретного продукта, аудитории, CTA или motion.

Перед scorecard сначала прочитать `52-reference-gallery-source-map.md` и заполнить `24-thematic-reference-map.md`. Scorecard принимает только references with a clear closeness reason, recorded access status and section use.

## Sources

- https://www.nngroup.com/articles/competitive-usability-evaluations/
- https://www.nngroup.com/articles/benchmarking-ux/
- https://baymard.com/ux-benchmark
- https://baymard.com/research/product-page
- https://mobbin.com/
- https://pageflows.com/
- https://www.designkit.org/methods/analogous-inspiration.html
- `52-reference-gallery-source-map.md`

## Reference Roles

Каждый URL получает одну primary role:

| Role | Use | Example |
| --- | --- | --- |
| Direct/domain | Same market, same buyer, same conversion pressure | competitor landing, industry category leader |
| Visual language | Typography, color, composition, art direction | premium brand page, editorial product page |
| Motion/interaction | Entrance, scroll, hover, state transition | Codrops/Awwwards interaction, product flow animation |
| Component/source | Concrete block or primitive source | Animate UI, Motion Primitives, React Bits, PaceKit GSAP, Cult UI, ReUI, 21st.dev, Kokonut UI, MVPBlocks, SmoothUI, HextaUI, Skiper UI, Eldora UI, Blocks.so, Intent UI, Tailark, shadcnblocks |
| Flow/CRO | User journey, onboarding, checkout, signup evidence | Mobbin, Page Flows, Baymard, NN/g |
| Anti-reference | Useful because it shows what not to do | cluttered hero, fake dashboard, low contrast |

## Closeness Gate

Before scoring, each reference must answer:

- why it is close enough;
- which lane it belongs to;
- what the access status is: live, browser/manual only, blocked automation, premium/account gated, timeout or sitemap-only;
- which section it informs;
- what must not be copied;
- what risk could make it unusable.

If those answers are missing, keep it in `24-thematic-reference-map.md` as rejected or anti-reference, not in the scorecard.

## Score Scale

Use 0 to 3.

| Score | Meaning |
| ---: | --- |
| 0 | Not useful or actively misleading |
| 1 | Weakly useful, maybe one small detail |
| 2 | Useful for one section or design layer |
| 3 | Strong fit, should influence plan decisions |

## Criteria

| Criterion | Question |
| --- | --- |
| Product fit | Is this close to the product category or problem? |
| Audience fit | Is the intended user or buyer similar? |
| Offer/CTA fit | Is the conversion action similar enough? |
| Section fit | Does it clearly help a specific section? |
| Visual fit | Does the visual language fit the desired brand direction? |
| Motion value | Does the motion clarify hierarchy, story, feedback, or state? |
| Asset feasibility | Can we produce comparable real assets without faking proof? |
| Differentiation | Does borrowing from it avoid generic SaaS sameness? |
| Proof integrity | Does it support real claims instead of invented metrics/logos? |
| Implementation fit | Can we build it with existing stack or accepted dependencies? |
| Accessibility/performance risk | Will it avoid contrast, keyboard, motion, LCP, INP, CLS issues? |
| License/access risk | Is it safe to use as inspiration/source under available access? |

## Decision Bands

| Total | Decision |
| ---: | --- |
| 30 to 36 | Core reference. Use in direction and section storyboard. |
| 22 to 29 | Section reference. Use only where it maps clearly. |
| 14 to 21 | Detail reference. Borrow one small pattern or avoid. |
| 0 to 13 | Reject or keep as anti-reference. |

## Required Mix

For a strong plan, collect:

- 2 to 3 direct/domain references.
- 2 to 3 visual language references.
- 1 to 2 motion/interaction references.
- 1 to 2 flow/CRO references when signup, onboarding, checkout, pricing, or product flow matters.
- 1 anti-reference when the market is full of bad patterns.

## Borrowing Rules

- Borrow structure, hierarchy, behavior, spacing rhythm, asset strategy, and motion logic.
- Do not copy brand identity, proprietary claims, testimonials, logos, illustrations, exact layouts, premium/pro blocks, or private screenshots.
- A reference can inspire only the section it scores well for.
- A reference with high visual fit but low offer fit cannot define the full page.
- A reference with high motion value but high accessibility/performance risk must be simplified.
- A component source is not a design direction by itself.

## Output Requirements

Fill `projects/<slug>/15-reference-scorecard.md` before finalizing:

- `03-reference-board.md`
- `24-thematic-reference-map.md`
- `04-visual-benchmark.md`
- `05-visual-direction.md`
- `06-section-by-section-upgrade-plan.md`
- `07-animation-storyboard.md`
- `13-section-pattern-selection.md`

Every final section idea should point to at least one scored reference or explain why none applies.
