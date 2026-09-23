# Change Traceability Matrix

Дата обновления: 2026-07-03.

Этот слой нужен перед implementation handoff. Он проверяет, что план не является набором красивых идей: каждая значимая правка должна иметь источник, причину, visible result, task ID and QA evidence.

## Проверенные источники

Все источники ниже проверены live-запросом 2026-07-03 and returned 200.

| Source | URL | Role |
| --- | --- | --- |
| Figma developer handoff | https://www.figma.com/best-practices/guide-to-developer-handoff/ | Handoff should make design intent and implementation details inspectable. |
| Figma Dev Mode guide | https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode | Design-to-development inspection and implementation context. |
| Atlassian design decision template | https://www.atlassian.com/software/confluence/templates/design-decision | Decision documentation pattern: context, options, decision, impact. |
| Microsoft Architecture Decision Record | https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record | Lightweight decision record pattern for durable implementation decisions. |
| NASA requirement writing | https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/ | Requirements need clarity, traceability and verification. |
| NASA requirements verification matrix | https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/ | Verification matrix pattern: requirement, method, evidence and status. |

## Why This Exists

Landing plans fail when:

- a section is redesigned because a reference looked good, not because the product needs it;
- implementation tasks are section names without visible results;
- QA checks are disconnected from what changed;
- protected routes, copy, forms or analytics labels are accidentally changed;
- motion, assets or responsive behavior appear during implementation without prior plan approval.

The traceability matrix prevents this by connecting each change to evidence and verification.

## Change ID Rules

Use stable IDs:

- `chg-001-copy-hero`
- `chg-002-hero-visual`
- `chg-003-proof-strip`
- `chg-004-motion-hero`
- `chg-005-responsive-hero`

Do not rename IDs after handoff. QA, screenshots and follow-up fixes should keep referring to the same IDs.

## Required Trace Chain

Each significant change should connect:

```text
source evidence or assumption
-> user/problem or conversion reason
-> reference/brand/section decision
-> visible result
-> implementation task ID
-> QA/evidence method
```

If a row cannot complete this chain, it is not ready for implementation.

## Change Classes

| Class | Examples | Required link |
| --- | --- | --- |
| Preserve | routes, nav labels, form fields, legal/SEO, analytics labels | `25-brand-dna-map.md` or dossier |
| Copy | headline, subhead, CTA, proof, FAQ | `02-copy-and-offer-audit.md` |
| Structure | section order, grouping, rhythm | `06-section-by-section-upgrade-plan.md`, `18-section-storyboard-canvas.md` |
| Visual | type, color, spacing, radius, surfaces, icon style | `17-visual-style-tile.md`, `25-brand-dna-map.md` |
| Reference | inspiration decisions | `15-reference-scorecard.md`, `22-inspiration-synthesis.md` |
| Motion | entrance, reveal, feedback, state, scroll | `26-motion-reference-map.md`, `16-motion-recipe-selection.md`, `07-animation-storyboard.md` |
| Asset | screenshot, image, video, 3D, GLB, WebGL | `19-asset-production-queue.md` |
| Responsive | first viewport, crop, wrapping, overflow | `27-responsive-viewport-map.md` |
| Component | shadcn, Animate UI, custom, library choice | `08-component-and-asset-plan.md`, `14-animate-ui-selection.md`, `29-motion-primitives-selection.md`, `30-magic-ui-selection.md`, `31-aceternity-ui-selection.md`, `32-tailark-section-selection.md`, `33-shadcnblocks-selection.md`, `34-micro-component-selection.md`, `35-react-bits-selection.md`, `36-pacekit-gsap-selection.md`, `37-cult-ui-selection.md`, `38-reui-selection.md`, `39-twenty-first-dev-selection.md`, `40-kokonut-ui-selection.md`, `41-mvpblocks-selection.md`, `42-smoothui-selection.md`, `43-hextaui-selection.md`, `44-skiper-ui-selection.md`, `45-eldora-ui-selection.md`, `46-blocks-so-selection.md`, `47-intent-ui-selection.md` |
| QA | screenshot, command, accessibility, performance | `10-quality-gate.md`, `20-implementation-task-graph.md`, evidence manifests |

## Required Output

Fill:

```text
projects/<slug>/28-change-traceability-matrix.md
```

Then update:

```text
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/21-plan-self-review.md
projects/<slug>/11-implementation-handoff-prompt.md
```

Implementation handoff is blocked if any major planned change has no source, no visible result, no task ID, or no QA evidence method.
