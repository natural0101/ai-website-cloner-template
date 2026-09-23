# Product UI Review Rubric

Use this before final handoff and whenever a design feels "better but still not top". It turns vague taste into a concrete product-design review. Pair it with `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` so the score cannot hide a generic but technically passing design.

Score each category:

```text
0 = missing or actively harmful
1 = present but weak / partial / generic
2 = strong, intentional, verified
```

Do not use the score as fake precision. Use it to find what to fix next.

## Rubric

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Surface fit | Landing/card aesthetic applied to a tool, or unclear surface type. | Surface classified, but layout still borrows the wrong pattern. | Surface, blueprint, screen recipe, and density match the job. |
| Workflow clarity | User's main loop is hidden or replaced by chat/decor. | Main action exists, but current object/status/recovery are weak. | Core loop, current object, next action, and recovery path are obvious. |
| Information architecture | Routes, navigation, shell, panes, and recovery paths are missing or incoherent. | Basic navigation exists, but route map, pane jobs, or responsive IA are weak. | Route map, nav model, app shell, zones, responsive IA, and recovery placement match the product job. |
| Interaction model | Actions are static or jump to vague success with no pending/failure/recovery. | Main actions have some feedback, but disabled, retry, undo, or proof states are weak. | Primary actions define enabled, pending, success, failure, recovery, permission, and proof behavior. |
| Copy/status clarity | Vague labels like "Done", "Success", "Ready", or "AI fixed it" hide object, reason, evidence, or next action. | Some states have useful labels, but important empty/error/proof/sample/AI messages remain generic. | Status copy names object, state, reason, next action, evidence/source, and sample/demo/disconnected truth where relevant. |
| Decision/review support | Approval, triage, review, or comparison screens make the user infer the choice from scattered panels. | Decision question or actions exist, but evidence, risk, options, after-state, or audit path are weak. | Decision question, options/comparison, evidence, risk, action policy, after-state, and audit/recovery are obvious. |
| Information hierarchy | Everything competes equally; no scan path. | Primary area is visible, but support panels/cards still compete. | Primary work surface, secondary controls, metadata, and risks have clear order. |
| State coverage | Mostly happy path. | Some empty/loading/error states, but important panes/components are missing states. | Major panes and reusable components cover empty/loading/error/selected/pending/success/retry/rollback as relevant. |
| Component craft | Static demo blocks, unstable sizing, inconsistent primitives. | Components work but lack full variants, keyboard details, or stable dimensions. | Component state specs are named; controls, rows, panels, drawers, tabs, and toolbars are stable and polished. |
| Data/proof honesty | Fake metrics, users, screenshots, assets, agent status, or proof appear real. | Demo/sample labels exist but are incomplete or easy to miss. | Every proof-like element has a source, empty/disconnected state, or clear sample/demo label. |
| Accessibility | Keyboard/focus/labels/contrast are missing or broken. | Basic labels/focus exist, but overlays or dense controls are weak. | Keyboard path, focus-visible, labels, contrast, hit areas, tooltips, and reduced motion are checked. |
| Responsive behavior | Desktop or mobile breaks, overlaps, clips, or hides critical actions. | Layout adapts but one important state/viewport is weak. | Desktop, narrow desktop, tablet, and mobile degrade intentionally without overlap/clipping. |
| Visual system | Generic palette, random spacing, inconsistent radius/type/icons. | Coherent enough, but lacks distinctness or precision. | Typography, spacing, radius, color, iconography, contrast, and density feel deliberate and product-specific. |
| Motion/feedback | Decorative, distracting, broken, or missing feedback. | Basic hover/transitions, but unclear motion policy. | Motion supports continuity, feedback, diff/state change, and respects reduced motion. |
| Evidence | No screenshots/browser checks or commands. | Some checks, but missing viewports/states or unclear artifacts. | Commands, screenshots/browser checks, evidence artifacts, blockers fixed, and risks are reported. |

## PASS Thresholds

Use the score to guide verdicts:

```text
PASS: all P0 gates pass, no category is 0, evidence is 2, and total score is 26+.
PASS WITH RISKS: all P0 gates pass, no category is 0 except a clearly explained unavailable backend/integration state, evidence is at least 1, and total score is 18+.
FAIL: any P0 blocker remains, evidence is 0 for a visual change, workflow clarity is 0, copy/status clarity is 0, decision/review support is 0 for a review/approval surface, data/proof honesty is 0, or total score is below 16.
```

Do not hide behind a high score. A single P0 blocker still means `FAIL`.

## Review Sequence

1. Identify the changed surface and route.
2. Name the brief, blueprint, information architecture, interaction model, screen recipe, and component state specs.
3. Check copy/status language with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
4. Check decision/review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
5. Run the five-second test from `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`.
6. Score the rubric honestly.
7. Fix all categories scored 0 and fix any benchmark failure that leaves primary object, state, next action, recovery, or evidence unclear.
8. Prefer fixing the lowest product-impact category before decorative polish.
9. Run visual QA evidence.
10. Report score, top-design benchmark result, blockers, evidence, risks, and verdict.

## Output Format

```text
Rubric score:
Top-design benchmark:
Surface fit:
Workflow clarity:
Information architecture:
Interaction model:
Copy/status clarity:
Decision/review support:
Information hierarchy:
State coverage:
Component craft:
Data/proof honesty:
Accessibility:
Responsive behavior:
Visual system:
Motion/feedback:
Evidence:
Total:
Blocking categories:
Next fixes:
Verdict:
```

## Common Score Smells

- High visual score but low workflow score: probably a nice mockup, not a product screen.
- High hierarchy score but low IA score: screens may look organized but navigation/recovery will break in real use.
- High workflow score but low interaction score: the path is visible, but actions still behave like a mockup.
- High interaction score but low copy/status score: states exist, but the user still cannot tell what happened, why, or what to do next.
- High workflow score but low decision/review score: the path exists, but the screen still does not help the user choose, approve, reject, or recover.
- High workflow score but low component craft: useful but not polished enough.
- High component craft but low state coverage: pretty happy path, fragile product.
- High evidence score but low visual system: verified mediocrity, continue design polish.
- High total but data/proof honesty 0: fail; trust is broken.
