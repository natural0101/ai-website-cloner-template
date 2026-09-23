---
name: design-ai-workbench-screens
description: "Use when planning, designing, building, or auditing ForgeStudio-like AI design applications, canvas editors, AI workbenches, local-first design tools, proposal/diff review interfaces, comment-to-agent task loops, design import flows, inspector/layer panels, verification/ledger/history surfaces, or any product UI where an external AI agent proposes visual changes that a human previews, verifies, approves, revises, exports, or rolls back."
---

# Design AI Workbench Screens

Use this skill for concrete screen and component planning in AI-assisted design tools. Pair it with `product-ui-design-orchestrator` for routing and `product-design-taste` for taste decisions.

## Required Reading

Always read:

```text
docs/design-workbench/FORGESTUDIO_CONTEXT.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
references/ai-workbench-screen-patterns.md
```

If the task involves 3D/WebGL/Blender assets, also read the local `blender-workbench/` handoff and relevant 3D skills before designing previews, asset panels, or export states.

## External Packet Discipline

When working in a target repository that has a `.design-agent/` packet, read `.design-agent/working-brief.md` before choosing an AI workbench slice, then verify it from the knowledge-base repository with `npm run design:brief-check -- "<target-project>"`. Before final handoff, use `.design-agent/final-report-template.md`, run `npm run design:final-check -- "<target-project>"`, and refresh `.design-agent/readiness-report.md` with `npm run design:target-audit -- "<target-project>" --write`.

## Workflow

1. Start with `AI_DESIGN_APP_TRUSTED_VERTICAL.md`: name the trusted vertical segment, source-of-truth objects, false-state risks, proof/evidence surfaces, decision question, after-state, and recovery path for the changed slice.
2. Identify the slice: `launcher`, `design-search`, `import-review`, `studio-workspace`, `canvas`, `inspector`, `comments-tasks`, `agent-proposal`, `preview-diff`, `verification`, `ledger-history`, `export-share`, `settings-connection`, or `end-to-end`.
3. Map the slice to the product loop:

```text
open project -> design search -> import -> inspect -> comment/task -> agent proposal -> preview/diff -> verify -> approve/revise -> export/reopen
```

4. Map the slice through `AI_WORKBENCH_INTERACTION_FLOWS.md`: core objects, allowed transitions, blocked transitions, proof/evidence, and rollback/reopen path.
5. Choose a buildable vertical slice from `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`: project launcher/import, workspace selection/inspector, comment task to proposal, proposal preview/diff, or ledger/export.
6. Fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` for the chosen slice before coding: route/screen, primary object, user job, data/fixture truth, included/deferred states, action path, responsive behavior, commands, screenshots/browser evidence, and risks.
7. Fill the target `.design-agent/working-brief.md` AI Design App Invariants before coding when a packet exists: external AI is proposal-only until what evidence exists, where preview/diff is visible, where verification is visible, where human approval happens, where transaction/ledger evidence appears, where agent connection/scopes are visible, how comments become tasks, how pending proposals/approvals cross into the live UI, how failures/recovery are handled inline, and how export/reopen recovery works. `N/A` is valid only when the surface is not an AI design app.
8. Map workspace IA with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`: route map, left/center/right zones, current object, review/proposal zones, ledger/recovery path, and responsive IA.
9. Define workspace interaction transitions with `PRODUCT_UI_INTERACTION_MODEL.md`: pending proposal, failed task, stale diff, verification retry, approval, revise/reject, ledger, export, rollback.
10. Define factual status labels with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`: agent disconnected, proposal ready, verification failed, sample proposal, ledger row created, rollback unavailable, and no vague applied/done state.
11. Shape proposal/import/export/verification review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`: decision question, comparison, evidence, risk, approve/revise/reject, after-state, ledger/recovery.
12. Choose the required layout pattern from `references/ai-workbench-screen-patterns.md`.
13. Choose the matching recipe from `PRODUCT_UI_SCREEN_RECIPES.md`, usually AI Design Studio Workspace, Proposal / Diff Review, Verification / Ledger / History, or Export / Share.
14. Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` and `COMPONENT_STATE_SPEC.md` for layer rows, inspector fields, comment/task cards, proposal panels, verification rows, and export artifacts.
15. Use `product-ui-component-sourcing` before adding external primitives for trees, inspectors, tables, command menus, diff viewers, charts, uploaders, or drawers.
16. Define visible objects, states, actions, copy, decisions, and evidence before visual styling.
17. Decide where the current object, current task, agent status, verification state, and rollback path are visible.
18. Design empty/loading/error/permission/disconnected states for every major pane in the slice.
19. Run `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` for the chosen slice: five-second test, primary object/state/next action, weakest visual category, mediocrity risks, and product-specific details.
20. Verify that external AI is proposal-only: no UI may claim a change is applied before preview, verification, approval, transaction, and ledger evidence.

## Non-Negotiables

- Do not collapse an AI design app into a chat page.
- Do not hide project import, source paths, skipped assets, or agent connection state.
- Do not show "AI fixed it" without accepted diff, closed comment/task, and ledger/history row.
- Do not use "done", "success", or "ready" when the UI means proposal, preview, verification, approval, transaction, ledger, or export.
- Do not make proposal review a pile of panels; it needs a decision cockpit with comparison, evidence, risk, actions, after-state, and ledger/recovery.
- Do not provide multiple mutation paths for canonical design state.
- Do not skip the proposal -> preview/diff -> verification -> human approval -> transaction -> ledger path.
- Do not leave AI Design App Invariants generic or `N/A` for ForgeStudio-like screens; name proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen surfaces before coding.
- Keep canvas, layer tree, inspector, comments/tasks, proposals, verification, and history visually connected through selection and status.
- Label mock/sample proposal states honestly when backend integration is incomplete.

## Output Contract

When planning or auditing, output:

- Slice:
- Top-design benchmark:
- Trusted vertical segment:
- AI Design App Invariants:
- Implementation slice:
- Implementation slice contract:
- Product-loop coverage:
- Interaction flow/invariants:
- Operational pattern:
- Information architecture:
- Interaction model:
- Copy/status language:
- Decision/review cockpit:
- Screen recipe/state specs:
- Component blueprints:
- Required panes:
- State matrix:
- Primary actions:
- Evidence/proof elements:
- Risk states:
- Responsive behavior:
- Accessibility requirements:
- Verification plan:

When implementing, build the smallest coherent slice, then verify with the target project's real checks and screenshots when available.
