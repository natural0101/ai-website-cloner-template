# Visual QA Evidence Playbook

Use this when a design agent must prove that a dashboard, admin panel, SaaS app, AI design studio, canvas editor, website, or 3D/WebGL surface is actually presentable in the browser.

Static code review is not visual evidence. A final report must include real commands, screenshots/browser checks, or a clear remaining-risk note.

For target handoff audits, use explicit evidence statuses:

```text
Project command evidence: REAL_PROJECT_COMMANDS / NOT_RUN_WITH_RISK:
Visual evidence verdict: REAL_BROWSER_SCREENSHOTS / USER_SCREENSHOTS / MANUAL_BROWSER_INSPECTION / NOT_RUN_WITH_RISK:
```

`READY FOR FINAL HANDOFF` requires `REAL_PROJECT_COMMANDS` and one real visual evidence verdict. `NOT_RUN_WITH_RISK`, planned checks, packet-only checks, or "not applicable" keep the target at `READY FOR CODING, NOT READY FOR FINAL HANDOFF`.

Final reports must also list real target-project files under `Files changed`. Use target-relative paths. `design:target-audit` treats missing paths, directories, and paths outside the target project as not ready for final handoff.

`Browser routes checked` must include the same route paths named in the working brief's `Route/screen`, `Route/screen/workflow to change`, or `Browser routes` fields. A final report for `/workspace/proposals` cannot claim readiness by checking only `/settings`.

`State coverage checked` must cover the working brief's `Included states`, except states explicitly named in `Deferred states`. If the brief promises empty, loading, error, selected, pending, and success states, the final report cannot claim readiness with only the loaded state checked.

`Component state evidence checked` must name the changed components or controls, the concrete states checked, and the evidence type: screenshot, browser inspection, keyboard/focus check, responsive viewport, command output, or manual artifact. `Checked`, `done`, or a component-only list without states and evidence is not enough.

`Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components. `Checked`, `done`, `looks good`, or a component-only list is not enough visual-system evidence.

`Implementation slice contract` must be substantive. It must name the changed route/screen, primary object, workflow/action, data/source truth, and state coverage. The final `Product read`, `Workflow improved`, and `Implementation slice contract` fields must reference the working brief's primary object, workflow/actions, and data/fixture truth; `done`, `improved`, or a detached component description is not enough.

`Rubric score` must be numeric and checkable. Use the /30 scale from `PRODUCT_UI_REVIEW_RUBRIC.md`: `PASS` requires 26+/30, `PASS WITH RISKS` requires 18+/30 or higher, and any 0/blocking category must be fixed or reported as a blocker.

`Five-second test` must be substantive, not `passed`, `checked`, or `looks good`. It must name object, state, next action, recovery, and evidence so the target audit can prove the screen communicates the work without implementation notes. `Mediocrity risks fixed` must reference the working brief's `Mediocrity risks to avoid`, and `Product-specific details` must reference the working brief's `Product-specific details to make distinctive`.

When using `REAL_PROJECT_COMMANDS`, list command-log artifacts under `Command evidence artifacts`; `design:target-audit` expects non-empty `.log`, `.txt`, `.md`, `.html`, or valid `.json` files in the target project. A command name in the final report without a log artifact is not enough for final handoff readiness.

When using `REAL_BROWSER_SCREENSHOTS` or `USER_SCREENSHOTS`, list screenshot/artifact paths under `Screenshots/browser checks` or `Evidence artifacts`; `design:target-audit` expects those files to exist in the target project, be non-empty, and match a real visual artifact signature for PNG, JPEG, WebP, GIF, MP4, or WebM. A text file renamed to `.png` is not evidence.

When using `MANUAL_BROWSER_INSPECTION`, list a notes artifact under `Evidence artifacts`; `design:target-audit` expects a non-empty `.md`, `.txt`, `.html`, or valid `.json` file in the target project. The notes must mention the checked route/screen, viewport name or pixel size, and a visual/layout/focus/overlap check. A sentence in the final answer is not enough for final handoff readiness.

## Evidence Matrix

| Evidence | Required when | Notes |
| --- | --- | --- |
| Build/typecheck/lint/test output | The project has these commands | Proves code health, not visual quality. |
| Browser screenshot | Any visual surface changed | Best evidence for overlap, clipping, spacing, media, canvas, and responsive layout. |
| Implementation slice evidence | Any product UI implementation changed | Proves the route/screen, primary object, data/fixture truth, states, actions, responsive behavior, and risks are coherent. |
| Interaction check | Menus, drawers, tabs, filters, tables, forms, canvas, WebGL, or comments changed | Check hover/focus/selected/open/closed states. |
| State screenshot or forced state | Empty, loading, error, disconnected, selected, pending, success, retry, rollback touched | Use real app state, mocks, fixtures, storybook, query params, local data, or controlled props. |
| Component state evidence | Any component/control was changed | Report component/control names, states checked, and screenshot/browser/manual/keyboard/responsive evidence. |
| Copy/status check | Status labels, empty/error copy, AI/proof language, sample/demo labels, or toasts changed | Use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`; verify object, reason, next action, evidence/source, and placement. |
| Decision/review check | Approval, comparison, triage, proposal review, evidence, risk, or audit UI changed | Use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`; verify decision question, options/comparison, evidence, risk, actions, after-state, and audit/recovery. |
| Accessibility spot check | Any interactive UI changed | Keyboard path, focus-visible, labels, hit areas, reduced motion. |
| Data/proof check | Metrics, screenshots, imported assets, users, logos, agent state, or proof-like claims shown | Confirm real source or label sample/demo. |

## Viewport Set

Default matrix:

```text
desktop-wide: 1440x900
desktop-narrow: 1024x768
tablet: 768x1024
mobile: 390x844
```

For desktop-first tools, mobile may become review-only or focused-edit mode, but it must not break, hide critical status, overlap controls, or show unusable blank panes.

## QA Sequence

1. Identify changed routes/screens.
2. Identify the chosen `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md` fields and `PRODUCT_SURFACE_BLUEPRINTS.md` surface.
3. Identify the `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` fields: route/screen, object, data source, workflow, states, responsive behavior, commands, screenshots, and risks.
4. Start the app the way the target project expects.
5. Run available code checks.
6. Open the changed screens in a real browser.
7. Capture or inspect each viewport.
8. Exercise the main workflow: navigate, select, filter/edit, open overlays, submit/retry, approve/export, or equivalent.
9. Check required states for the surface.
10. Check copy/status language for primary action states and major empty/error/disconnected/stale/sample states.
11. Check decision/review cockpit behavior for approval, triage, comparison, and proposal-review states.
12. Fix P0 blockers immediately.
13. Re-run the smallest evidence check that proves the blocker is gone.
14. Report evidence and remaining risks honestly.

Before final handoff, compare the working brief routes to `Browser routes checked`; every brief route path should appear in the final checked routes.
Also compare `Included states` to `State coverage checked`; missing promised states are final handoff risks unless they were explicitly deferred.
Also compare the working brief route/screen and IA fields to `Information architecture checked`; it should name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior rather than a generic IA claim.
Also compare the working brief visual system contract to `Visual system checked`; it should name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components rather than a generic visual claim.
Also compare action/transition fields to `Interaction model checked`; it should name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control rather than a static component claim.
Also compare copy/status fields to `Copy/status language checked`; it should name affected object, state/status, reason or next action, and evidence/source/sample label rather than generic `success`, `ready`, or `done` language.
Also compare decision/review fields to `Decision/review cockpit checked`; it should name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path rather than a generic review claim.
Also compare changed components and controls to `Component state evidence checked`; it should name components, states, and evidence rather than a generic state claim.
Also compare the working brief primary object, workflow/actions, and data/fixture truth to `Product read`, `Workflow improved`, and `Implementation slice contract`; the final report should describe the same product slice, not a generic component polish.
Also compare the working brief top-design fields to the final top-design fields. Generic text such as `passed`, `checked`, `improved`, or `done` does not prove top design; the final report must name object, state, next action, recovery, evidence, the mediocrity risks fixed, and the product-specific details preserved or added.

## Screenshot Naming

Use names that make evidence auditable:

```text
qa/<surface>/<route>__<state>__<viewport>.png
qa/dashboard/overview__loaded__1440x900.png
qa/dashboard/overview__empty__390x844.png
qa/workbench/studio__proposal-open__1024x768.png
qa/workbench/studio__agent-disconnected__390x844.png
```

If the project already has a screenshot/evidence folder, use that folder instead.

## Browser Check Notes

When Playwright or another browser tool is available, prefer:

- viewport screenshots;
- console error check;
- locator existence for primary actions;
- keyboard tab path smoke test;
- reduced-motion emulation when motion changed.

When browser automation is not available, use manual browser inspection or user-provided screenshots, and report the limitation.
Manual notes should be auditable, for example: `Route /dashboard, viewport 390x844: checked layout, focus path, sticky footer, no overlap/clipping`.

Do not install Playwright or another heavy test stack only to satisfy this playbook unless it fits the target project and the user asked for that setup.

## P0 Blockers

These block `PASS`:

- text, controls, toolbars, table cells, popovers, or tooltips overlap or clip;
- canvas, WebGL, video, image, GLB, or media region is blank without fallback;
- primary route or workflow cannot be reached;
- route map, app shell, navigation, or pane recovery path is missing for a product tool;
- changed UI is an isolated decorative/component fragment with no coherent route, object, workflow, data/source truth, state coverage, or evidence path;
- changed component/control lacks state evidence naming the component, checked states, and screenshot/browser/manual/keyboard/responsive proof;
- primary action has no visible pending/failure/retry/recovery path;
- primary action uses vague "done/success/ready" copy without object, reason, next action, or evidence;
- selected/current object is unclear in an editor, workbench, table, or inspector;
- empty/loading/error/disconnected state is missing for a major pane;
- proposal/diff/verification/approval/history collapse into a vague done state;
- approval/review surface has no visible evidence, risk, comparison, or after-decision/audit path;
- fake metrics, fake screenshots, fake imported assets, fake agent state, or fake proof appear as real;
- mobile or desktop-narrow viewport hides critical action/status with no alternative path;
- focus-visible is absent or keyboard path gets trapped;
- no browser/screenshot evidence exists and no limitation is reported.

## PASS Rules

Use:

```text
PASS
```

Only when changed screens have code checks plus browser/screenshot evidence, no P0 blockers, required states are represented, and remaining risks are minor.

Use:

```text
PASS WITH RISKS
```

When the UI is usable but evidence is partial, a non-critical state is unverified, or a dependency/back-end state could not be exercised.

Use:

```text
FAIL
```

When P0 blockers remain, visual evidence is missing for visual changes, or the main workflow is not usable.

## Evidence Summary Template

```text
Surface:
Brief/blueprint:
Implementation slice:
Information architecture:
Interaction model:
Copy/status language:
Decision/review cockpit:
Changed routes:
Viewports:
States:
Component state evidence checked:
Commands:
Files changed:
Project command evidence:
Command evidence artifacts:
Screenshots/browser evidence:
Visual evidence verdict:
P0 blockers found:
P0 blockers fixed:
Unverified risks:
Verdict:
```
