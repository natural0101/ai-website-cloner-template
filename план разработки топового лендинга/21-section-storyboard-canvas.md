# Section Storyboard Canvas

Дата обновления: 2026-07-03.

Section storyboard canvas нужен после style tile, reference scorecard, section patterns and motion recipes. Он превращает план в понятный будущий экран: что пользователь видит, почему это работает, какой source inspiration, какой asset, какая анимация, какой component source and what to verify.

## Sources

- https://www.figma.com/resource-library/what-is-wireframing/
- https://www.figma.com/resource-library/how-to-make-a-user-journey-map/
- https://www.nngroup.com/articles/storyboards-visualize-ideas/
- https://www.nngroup.com/articles/journey-mapping-101/
- https://www.interaction-design.org/literature/topics/storyboards
- https://www.uxpin.com/studio/blog/wireframe-examples/

## What This Is

This is not a high-fidelity design file. It is a compact section-level storyboard that another agent can implement without guessing.

A good row answers:

- What is the section job?
- What is the visible composition?
- What is the main copy/proof?
- What exact asset appears?
- Which references justify it?
- Which pattern and style rules apply?
- What motion happens?
- Which component/source is planned?
- How does it change on mobile?
- What can break?

## Required Inputs

- `01-current-state-audit.md`
- `02-copy-and-offer-audit.md`
- `05-visual-direction.md`
- `06-section-by-section-upgrade-plan.md`
- `13-section-pattern-selection.md`
- `15-reference-scorecard.md`
- `16-motion-recipe-selection.md`
- `17-visual-style-tile.md`
- `08-component-and-asset-plan.md`

## Canvas Fields

| Field | What to write |
| --- | --- |
| Section | Hero, proof, features, pricing, FAQ, CTA, etc. |
| User job | What the section must make the user understand or do |
| Frame sketch | Short layout sketch in words, e.g. "left copy, right product crop, proof strip below" |
| Above the fold or scroll | Where it appears in the page rhythm |
| Copy/proof | Headline, claim, metric, testimonial, FAQ answer, CTA |
| Visual style | Token/rule from `17-visual-style-tile.md` |
| Asset | Screenshot, render, image, diagram, video, 3D, icon system |
| Reference IDs | IDs from `15-reference-scorecard.md` |
| Pattern | Pattern from `13-section-pattern-selection.md` |
| Motion recipe | Recipe from `16-motion-recipe-selection.md` |
| Component/source | native, shadcn, Animate UI, Motion Primitives, Magic UI, React Bits, PaceKit GSAP, Cult UI, ReUI, 21st.dev, Kokonut UI, MVPBlocks, SmoothUI, HextaUI, Skiper UI, Eldora UI, Blocks.so, Intent UI, custom, GSAP, Three.js |
| Mobile frame | How it collapses or changes |
| QA risk | Layout, copy, proof, a11y, performance, motion, mobile |

## Canvas Rules

- Every major section gets one row.
- Every row needs at least one reference ID or a clear reason no reference applies.
- Every row needs a visual style rule and a mobile frame.
- If a section has motion, it must point to a selected motion recipe.
- If a section needs an asset, it must point to asset plan details.
- If a section uses Animate UI, it must point to `14-animate-ui-selection.md`.
- If a section uses Cult UI, it must point to `37-cult-ui-selection.md`.
- If a section uses ReUI, it must point to `38-reui-selection.md`.
- If a section uses 21st.dev, it must point to `39-twenty-first-dev-selection.md`.
- If a section uses Kokonut UI, it must point to `40-kokonut-ui-selection.md`.
- If a section uses MVPBlocks, it must point to `41-mvpblocks-selection.md`.
- If a section uses SmoothUI, it must point to `42-smoothui-selection.md`.
- If a section uses HextaUI, it must point to `43-hextaui-selection.md`.
- If a section uses Skiper UI, it must point to `44-skiper-ui-selection.md`.
- If a section uses Eldora UI, it must point to `45-eldora-ui-selection.md`.
- If a section uses Blocks.so, it must point to `46-blocks-so-selection.md`.
- If a section uses Intent UI, it must point to `47-intent-ui-selection.md`.
- Do not invent proof to make a storyboard stronger.
- Do not add decorative sections that do not support the offer.

## Storyboard Quality Bar

The final storyboard should let a reviewer imagine the page section by section without seeing screenshots.

It should include:

- first viewport composition;
- section rhythm and transitions;
- proof placement;
- asset crops and proportions;
- interaction and animation moments;
- mobile transformations;
- rejected ideas and why they were rejected.

## Output

Fill `projects/<slug>/18-section-storyboard-canvas.md`, then mirror decisions into:

- `06-section-by-section-upgrade-plan.md`
- `07-animation-storyboard.md`
- `08-component-and-asset-plan.md`
- `09-implementation-tasks.md`
- `10-quality-gate.md`
