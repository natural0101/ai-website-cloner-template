# 11 Implementation Handoff Prompt

Use this after files `01` through `10`, `20-implementation-task-graph.md`, and the `evidence/` manifests are filled.

## Implementation Prompt

```text
You are implementing a landing-page upgrade from this project plan.

Read everything in this folder before editing:
- landing-source-dossier.md if present;
- 01-current-state-audit.md;
- 02-copy-and-offer-audit.md;
- 03-reference-board.md;
- 04-visual-benchmark.md;
- 05-visual-direction.md;
- 06-section-by-section-upgrade-plan.md;
- 07-animation-storyboard.md;
- 08-component-and-asset-plan.md;
- 26-motion-reference-map.md;
- 27-responsive-viewport-map.md;
- 09-implementation-tasks.md;
- 10-quality-gate.md;
- 20-implementation-task-graph.md;
- 28-change-traceability-matrix.md;
- evidence/reference-manifest.md;
- evidence/screenshot-manifest.md;
- evidence/asset-manifest.md;
- evidence/decision-log.md.

Then implement tasks in `20-implementation-task-graph.md` order and mirror the summary in `09-implementation-tasks.md`.

Hard constraints:
- preserve protected routes, nav labels, form field names, analytics-sensitive labels, legal copy, and SEO-critical content;
- do not invent proof, metrics, logos, testimonials, reviews, or claims;
- do not install dependencies not listed in the plan;
- do not start a task that is blocked in `20-implementation-task-graph.md`;
- every animation must match `07-animation-storyboard.md` and include reduced-motion fallback;
- every motion idea must be accepted or adapted in `26-motion-reference-map.md`;
- every layout must respect `27-responsive-viewport-map.md` for mobile, tablet, laptop and wide viewports;
- every major change must have a `chg-###` traceability row with source evidence, task ID and QA method;
- every asset must match `08-component-and-asset-plan.md` or be explicitly recorded as missing.

Verification:
- run project checks;
- capture desktop and mobile screenshots if possible;
- update `10-quality-gate.md` with evidence;
- report files changed, commands run, screenshots, and remaining risks.
```
