# Product UI Top Design Benchmark

Use this when an agent must make a product UI, dashboard, editor, AI design studio, website, or hybrid surface feel top-tier rather than merely acceptable.

Top design is not decoration. It is the point where workflow clarity, visual craft, state truth, and evidence all reinforce each other.

## Top-Tier Bar

A product surface is top-tier only when it passes all of these:

| Dimension | Top-tier signal | Common mediocre substitute |
| --- | --- | --- |
| Product fit | The layout is unmistakably built for the user's job and frequency of use. | Generic SaaS cards or landing rhythm applied to a tool. |
| First read | Within five seconds, the user knows current object, state, risk, and next action. | Pretty panels, but the user must hunt for what matters. |
| Hierarchy | One primary work surface dominates; support zones are clearly secondary. | Every panel/card has similar weight. |
| State truth | Empty, loading, error, pending, success, failed, stale, disconnected, and recovery states are designed. | Happy-path mockup plus a toast. |
| Decision support | Review/approval screens make the choice obvious with comparison, evidence, risk, action, after-state, and recovery. | User infers from scattered metadata. |
| Component precision | Rows, controls, panels, toolbars, chips, and overlays have stable dimensions and full states. | Good static styling but weak hover/focus/disabled/pending variants. |
| Visual system | Typography, spacing, radius, color, iconography, density, and motion feel intentional and specific. | Default Tailwind/shadcn look with a new accent color. |
| Trust | Proof-like UI is sourced, labeled sample/demo, or absent. | Fake metrics, fake agent activity, fake screenshots, fake imported assets. |
| Evidence | Commands and screenshots/browser checks cover actual changed routes/states/viewports. | "Looks good" or build-only proof. |

## Five-Second Test

Before final handoff, inspect the changed screen and answer:

```text
What is the primary object?
What state is it in?
What needs attention?
What is the next useful action?
What can fail or be recovered?
What evidence proves the UI is telling the truth?
```

If any answer requires reading implementation notes, the design is not top-tier yet.

Final report fields must preserve those answers. `Five-second test: passed`, `Top-design benchmark checked: yes`, `Mediocrity risks fixed: improved`, or similar generic text is not evidence. Write the actual object, state, next action, recovery, and evidence, then name which brief risks were fixed and which product-specific details make the screen distinctive.

## AI Design Studio Benchmark

For ForgeStudio-like tools, top-tier means the screen makes supervised AI work feel safe, fast, and inspectable:

- The trusted vertical is visible for the slice: project, design search, import, object, comment/task, proposal, preview/diff, verification, approval, transaction, ledger, export/reopen.
- Agent status is factual, not atmospheric.
- Proposal, preview, verification, approval, transaction, ledger, and export are separate states.
- Canvas, layers, inspector, comments/tasks, proposals, verification, and history mirror the same current object.
- The decision cockpit shows question, comparison, evidence, risk, approve/revise/reject, after-state, and recovery together.
- Mock/sample states are impossible to confuse with real applied agent work.

## Dashboard/Admin Benchmark

For dashboards, admin panels, records UIs, and data tools:

- The main table/list or operational object is visually first when scan/compare work is central.
- Scope, filters, source, freshness, and empty filtered state are visible.
- Bulk/destructive actions appear only with selection and show count, object type, impact, partial failure, and recovery.
- Detail panes show current object, status, validation, source, next action, and audit/recovery.
- Charts are used only when they answer faster than a table.

## Website/Product Page Benchmark

For websites and product pages:

- The first viewport communicates the product/category/offer without hiding the next section.
- Visual assets reveal the actual product, workflow, object, place, person, or outcome.
- Proof is sourced or removed.
- CTAs are grounded in the user journey, not repeated mechanically.
- Motion and imagery support comprehension, not novelty.

## Top-Design Anti-Patterns

- A beautiful component with no route, state, or workflow.
- A dashboard made of oversized marketing cards.
- An AI tool that is mostly chat.
- A workbench where proposal, preview, verification, and applied state blur together.
- A dense UI with no stable row/control dimensions.
- A polished happy path with no error/retry/recovery.
- Decorative gradients, glass, or motion hiding weak hierarchy.
- Unverified screenshots, fake proof, or sample data presented as real.

## Final Benchmark Contract

Before final handoff, report:

```text
Top-design target:
Five-second test:
Primary object/state/next action:
Weakest remaining visual category:
Mediocrity risks fixed:
Distinctive product-specific details:
Evidence used:
Verdict:
```

Use this together with `PRODUCT_UI_REVIEW_RUBRIC.md`, `PRODUCT_UI_QUALITY_GATE.md`, `PRODUCT_UI_VISUAL_QA.md`, and `VISUAL_QA_EVIDENCE_PLAYBOOK.md`.
