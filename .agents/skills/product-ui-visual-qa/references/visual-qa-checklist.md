# Product UI Visual QA Checklist

Use this reference when reviewing dashboards, editors, AI workbenches, SaaS apps, admin panels, or product workflows. First compare the result to `docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, the chosen `docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md` pattern, `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md`, `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, `docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md`, `docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` for operational surfaces, `docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, `docs/design-workbench/COMPONENT_STATE_SPEC.md`, `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`, and `docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md`. For AI workbenches, also compare to `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md` before accepting the slice. Use `docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md` for evidence collection and `docs/design-workbench/AGENT_REPORT_EXAMPLES.md` for final report shape.

## Evidence Priority

| Evidence | Strength | Notes |
| --- | --- | --- |
| Real browser screenshot | Strong | Best for overlap, spacing, responsive, canvas, assets. |
| Playwright/browser automation | Strong | Best for repeated routes, viewport matrix, interactions. |
| Build/typecheck/test output | Strong for code health | Does not prove visual quality alone. |
| Manual browser inspection | Medium | Useful if clearly reported. |
| Static code review | Weak for visuals | Not enough for final visual sign-off. |
| "Looks fine" statement | Not evidence | Never enough. |

Final reports must choose explicit statuses:

```text
Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK:
Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK:
```

Only real project commands plus real browser/user/manual visual evidence can support `READY FOR FINAL HANDOFF` in `design:target-audit`.
`Files changed` must list target-relative paths that exist inside the target project; missing files, directories, or paths outside the project block final handoff readiness.
`Browser routes checked` must include the route paths from `.design-agent/working-brief.md`; checking a different route is not evidence for the changed route.
`Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. Generic `checked`, `done`, `looks good`, or component-only wording is not evidence.
`Information architecture checked` must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior. Generic `checked`, `done`, or component-only wording is not evidence.
`Interaction model checked` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control. Generic `checked`, `done`, or static component wording is not evidence.
`Copy/status language checked` must name affected object, state/status, reason or next action, and evidence/source/sample label. Generic `checked`, `done`, `success`, or `ready` wording is not evidence.
`Decision/review cockpit checked` must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path. Generic `checked`, `done`, or component-only wording is not evidence.
`State coverage checked` must cover `.design-agent/working-brief.md` `Included states`, except states explicitly listed in `Deferred states`.
`Component state evidence checked` must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence. Generic `checked`, `done`, or component-only wording is not evidence.
`Product read`, `Workflow improved`, and `Implementation slice contract` must reference the working brief's route/screen, primary object, workflow/actions, data/source truth, and states. Generic `done/improved` or component-only wording is not implementation-slice evidence.
`Rubric score` must be numeric on the /30 scale; `PASS` requires 26+/30, `PASS WITH RISKS` requires 18+/30 or higher, and 0/blocking categories must be fixed or reported as blockers.
`Five-second test` must name object, state, next action, recovery, and evidence; generic `passed`, `checked`, `improved`, or `looks good` text is not visual QA evidence.
`Mediocrity risks fixed` and `Product-specific details` must reference the working brief's risk/detail fields so the final result is product-specific rather than generic polish.
For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, `Operational pattern checked` must name proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.
For `REAL_PROJECT_COMMANDS`, the listed command-log artifacts must exist in the target project and be non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` files.
For `REAL_BROWSER_SCREENSHOTS` or `USER_SCREENSHOTS`, the listed screenshot/artifact files must exist in the target project, be non-empty, and be valid PNG/JPEG/WebP/GIF/MP4/WebM files.
For `MANUAL_BROWSER_INSPECTION`, the listed notes artifact must exist in the target project and be a non-empty `.md`, `.txt`, `.html`, or valid `.json` file that names route/screen, viewport or pixel size, and visual/layout/focus/overlap check.

For screenshot naming, viewport policy, PASS/PASS WITH RISKS/FAIL rules, and evidence summary, use:

```text
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
```

## Viewport Matrix

Check changed surfaces at:

| Viewport | Purpose |
| --- | --- |
| Desktop wide `1440x900` or similar | Main tool layout, side panels, canvas, tables. |
| Desktop narrow `1024x768` | Panel pressure and toolbar wrapping. |
| Tablet `768x1024` | Drawer/collapse behavior, touch targets. |
| Mobile `390x844` or similar | Review/status mode, overflow, non-broken fallback. |

For desktop-first tools, mobile may be limited, but it must degrade intentionally and not break.

## P0 Visual Blockers

These block completion:

- text overlaps, clips, or escapes its container;
- buttons, tabs, toolbar controls, or table cells resize unpredictably;
- dropdowns/popovers/tooltips collide with panels or viewport edges;
- canvas overlays cover handles, comments, or critical UI incoherently;
- blank WebGL/canvas/media area without fallback;
- missing images/fonts/icons/GLB assets;
- unreadable contrast or invisible focus state;
- loading/empty/error state missing for a major pane;
- vague "done/success/ready" status used as sole feedback for important work;
- review/approval screen lacks decision question, comparison/options, evidence, risk, after-state, or audit/recovery;
- table/list row height shifts on hover/selection;
- fake metrics/proof/agent status/imported assets presented as real;
- no screenshot/browser check for a visual change and no explanation.
- route/screen, primary object, workflow, data/fixture truth, state coverage, and evidence do not form a coherent implementation slice.
- final implementation-slice fields do not reference the working brief's route/screen, primary object, workflow/actions, data/source truth, and states.
- final `Visual system checked` is generic or omits typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, or target-local tokens/components.
- final `Information architecture checked` is generic or omits route/screen map, navigation/app shell, main/context zones, or responsive/recovery behavior.
- final `Interaction model checked` is generic or omits primary actions/transitions, pending-success-failure states, recovery/permission behavior, or the affected object/control.
- final `Copy/status language checked` is generic or omits affected object, state/status, reason or next action, or evidence/source/sample label.
- final `Decision/review cockpit checked` is generic or omits decision question, options/comparison, evidence/risk, action, after-state, or audit/recovery path.
- final `Component state evidence checked` is generic or omits changed components/controls, concrete states, or screenshot/browser/manual/keyboard/responsive evidence.
- five-second test fails: primary object, state, next action, recovery, or evidence are unclear.
- AI design app final report omits proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, or export/reopen in `Operational pattern checked`.

## Product State Matrix

| Surface | States to verify |
| --- | --- |
| App shell/sidebar | active route, collapsed, hover, focus, disabled/unavailable |
| Table/list | empty, loading skeleton, selected, hover, sort/filter, error |
| Filters/saved views | active filters, reset, empty filtered result, disabled source unavailable |
| Bulk actions | zero selection hidden, selected count, confirmation, partial failure |
| Tree/layers | expanded/collapsed, selected, locked, hidden, warning |
| Inspector | no selection, multi-selection, invalid, locked, pending, reset available |
| Canvas | loading, render error, missing asset, selected object, zoom/pan, comment anchor |
| Task/comment | draft, pending agent, failed, needs revision, resolved, reopened |
| Proposal/diff | no agent, pending, ready, stale, verification failed, approved/rejected |
| Verification | not run, running, passed, warning, failed, retry |
| Ledger/history | empty, applied, rollback unavailable, restored/conflict |
| Export/share | pending, failed, partial, completed, permission denied |

## Layout Checks

- Top-design benchmark matches `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`: five-second test names object, state, next action, recovery, and evidence; weakest visual category, mediocrity risks fixed, and product-specific details are explicit and tied to the working brief.
- Route map, navigation model, app shell, main work zone, context/review zones, and recovery paths match `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
- Implementation slice matches `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`: route/screen, primary object, data/fixture source, workflow, included/deferred states, responsive behavior, commands, screenshots/browser evidence, and risks are explicit.
- Primary actions match `PRODUCT_UI_INTERACTION_MODEL.md`: pending, success, failure, retry/undo/rollback, permission, and proof behavior are visible where relevant.
- Status labels match `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`: object, reason, next action, and evidence/source/sample truth are visible where relevant.
- Decision/review surfaces match `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`: question, comparison, evidence, risk, actions, after-state, and audit/recovery are visible where relevant.
- Visual system evidence matches the working brief: typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components are named and visible.
- Responsive IA is intentional: hidden panes have a visible way back, and mobile/tablet are review/focused-edit/fallback flows rather than broken stacked desktop panels.
- Primary work surface is visually first.
- Support panels have distinct jobs and do not compete equally.
- Dense rows align to a shared grid.
- Repeated controls have stable dimensions.
- Long labels wrap intentionally or truncate with accessible full value.
- Toolbar icon buttons have fixed hit area and tooltip/accessibility name.
- Drawers/modals trap focus where appropriate and restore focus after close.
- Sticky headers/footers do not cover content.

## Accessibility Checks

- Keyboard can reach primary actions and exit overlays.
- Focus-visible state is visible against actual background.
- Icon-only buttons have accessible names and tooltips when ambiguous.
- Form fields have labels, units, helper/error text where needed.
- Color is not the only signal for status.
- Reduced motion keeps final content visible.
- Touch targets remain usable on tablet/mobile.

## Component And Data Checks

- Reusable components match `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` or explain a custom pattern.
- External components solve a named product job.
- Local primitives were checked before adding dependencies.
- No bulk catalog install occurred.
- Demo/sample content is removed or labeled.
- Fake users, files, AI chats, screenshots, imported assets, metrics, and proof are not presented as real.
- Source paths, timestamps, or registry rows appear where import/asset state needs evidence.

## Dashboard/Admin/Data Tool Checks

- Scope, data source, time range, and freshness are visible or sample data is labeled.
- Summary metrics are tied to the primary table/list and not invented decoration.
- Table/list is the primary work surface when scan/compare work is central.
- Filters, saved views, active filter count, reset, and empty filtered state exist when relevant.
- Selected row/detail pane mirrors the current object and exposes next actions.
- Bulk actions appear only with selection and show selected count and failure policy.
- Destructive actions have confirmation and recovery/restore path.
- Stale, partial, permission denied, and export failed states are not hidden in toast-only feedback.

## AI Workbench Checks

- The trusted vertical segment from `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md` is named and visible.
- Source-of-truth objects are visible where relevant: project folder, design search report, import plan, visual object, anchored comment, agent task, proposal, verification run, transaction, ledger entry, and export artifact.
- False states are absent: no fake connected agent, fake imported project, fake proof, or "AI fixed it" without proposal, preview/diff, verification, approval, transaction, closed task/comment, and ledger evidence.
- Agent connection truth is visible.
- The selected implementation slice from `docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md` is named and covered.
- External AI output is proposal-only until approval.
- AI Design App Invariants are concrete in the working brief when a packet exists; `N/A` is accepted only for non-AI-design-app surfaces.
- Proposal, preview/diff, verification, approve/revise, transaction, applied/rejected, agent connection/scopes, comment-to-task bridge, pending approval bridge, failure/recovery, and ledger states are distinct.
- "Done" requires accepted diff, closed comment/task, and ledger/history row.
- Chat does not replace the canvas/workbench spine.
- Stale proposal, verification failed, rollback unavailable, disconnected, skipped asset, and permission states are visible where relevant.
- Use `docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md` to check core objects, allowed transitions, blocked transitions, proof/evidence, and mock/sample labels.

## Report Format

Use concise findings:

```text
[P0] Screen/viewport:
Issue:
Evidence:
Fix:

[P1] Screen/viewport:
Issue:
Evidence:
Fix:
```

Final verdict:

```text
PASS
PASS WITH RISKS
FAIL
```

Use `FAIL` if P0 blockers remain or no visual/browser evidence exists for a visual change.
