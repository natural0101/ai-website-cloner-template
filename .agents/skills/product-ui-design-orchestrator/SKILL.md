---
name: product-ui-design-orchestrator
description: "Use when planning, building, auditing, or improving product UI beyond landing pages: dashboards, admin panels, AI design studios, canvas editors, workbenches, SaaS apps, onboarding flows, forms, tables, inspectors, sidebars, command surfaces, preview/review flows, full websites, or any frontend design task where the agent must route existing design skills without landing-page bias."
---

# Product UI Design Orchestrator

Use this skill first for product design work that is not purely a landing-page clone. It routes the existing design skills into a practical product-app workflow.

## Required Reading

Always read:

```text
docs/design-workbench/AGENT_START_HERE.md
docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md
docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json
docs/design-workbench/FORGESTUDIO_CONTEXT.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md
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
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
docs/design-workbench/AGENT_REPORT_EXAMPLES.md
references/universal-product-ui-playbook.md
```

For AI design apps, canvas editors, external-agent design workflows, proposal/diff review, verification, ledger/history, or ForgeStudio-like surfaces, also read:

```text
.codex/skills/design-ai-workbench-screens/SKILL.md
.codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
```

If the task mentions components, libraries, registries, Animate UI, motion, proof, 3D, assets, or component sourcing, also read the matching local source map before choosing components:

```text
.codex/skills/product-ui-component-sourcing/SKILL.md
.codex/skills/product-ui-component-sourcing/references/component-sourcing-matrix.md
docs/research/animate-ui-catalog.md
docs/research/animate-ui-whole-site-audit.md
план разработки топового лендинга/17-animate-ui-full-site-map.md
план разработки топового лендинга/53-motion-safety-source-map.md
план разработки топового лендинга/54-proof-integrity-source-map.md
```

## Workflow

1. Classify the surface: `dashboard`, `admin`, `design-editor`, `canvas-workbench`, `SaaS-app`, `website`, `landing`, `marketing`, `3D/WebGL`, or `hybrid`.
2. If another agent will work in a different repository and this knowledge-base repository is available, generate a target-local packet with `npm run design:pack -- "<target-project>"`, optionally install the managed target `AGENTS.md` block with `npm run design:install-agent-rules -- "<target-project>"`, verify it with `npm run design:packet-check -- "<target-project>"`, hand over the target `DESIGN_AGENT_HANDOFF.md`, require `.design-agent/working-brief.md` before coding, verify the filled brief with `npm run design:brief-check -- "<target-project>"`, keep `.design-agent/acceptance-checklist.md` open during work, use `.design-agent/AGENTS_SNIPPET.md` when manual rule installation is needed, use `.design-agent/final-report-template.md` before final handoff, verify the final report with `npm run design:final-check -- "<target-project>"`, and write a compact readiness report with `npm run design:target-audit -- "<target-project>" --write` when handing the target to a user or another agent. Treat failed `design:brief-check` as a coding blocker; it checks product substance, not only placeholders. Before coding, the brief must name the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan. For AI design studios, canvas editors, proposal/diff workflows, or ForgeStudio-like workbenches, `design:brief-check` also requires AI Design App Invariants: proposal-only behavior, preview/diff visibility, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery. Treat `READY FOR CODING, NOT READY FOR FINAL HANDOFF` as a real blocker until the report has `REAL_PROJECT_COMMANDS` plus real browser/user/manual visual evidence.
3. Follow `UNIVERSAL_DESIGN_RUNBOOK.md` for the end-to-end order: project read, product model, blueprint, workflow, IA, screen/interaction/state/copy/decision inventory, design system, component sourcing, craft, implementation slice, and verification.
4. Fill the Universal Product Design Brief and choose the closest Product Surface Blueprint.
5. Map routes/navigation/zones with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, choose screen recipes from `PRODUCT_UI_SCREEN_RECIPES.md`, define action transitions with `PRODUCT_UI_INTERACTION_MODEL.md`, define factual labels/messages with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, shape decision/review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, choose component blueprints, and define key component states with `COMPONENT_STATE_SPEC.md`.
6. For dashboards, admin panels, records UIs, operations screens, or data tools, apply `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` before choosing cards, filters, tables, detail panes, charts, or bulk actions.
7. State the design read in one line: user, job, density, tone, and primary workflow.
8. Choose the route:
   - Existing app redesign: use `redesign-existing-projects`, `ui-audit`, `ui-refactor-principles`.
   - Product UI taste or new app surface: use `product-design-taste` before visual polish.
   - AI design app / canvas workbench screen planning: use `design-ai-workbench-screens`.
   - New product UI: use `product-design-taste`, `frontend-design-for-distinctive-interfaces`, `tailwind-design-system-v4`, `shadcn-ui` when applicable.
   - Micro-polish: use `details-that-make-interfaces-feel-better`.
   - Motion: use `animation-systems-for-product-grade-web-motion` plus motion safety rules.
   - Components: use `product-ui-component-sourcing`, then the matching catalog skill/source map and exact endpoint checks.
   - Evidence/proof/data: use proof integrity rules without assuming landing context.
   - Product taste decisions: read `.codex/skills/product-design-taste/SKILL.md` and `.codex/skills/product-design-taste/references/product-design-taste-playbook.md`.
   - Final visual QA: use `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`, `PRODUCT_UI_REVIEW_RUBRIC.md`, `product-ui-visual-qa`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md`, and `AGENT_REPORT_EXAMPLES.md` before calling the work done.
9. Audit real workflows before visuals: route map, navigation model, app shell, object selection, filtering, editing, review, approval, export, recovery, pending/success/failure/retry states.
10. For AI design apps or canvas workbenches, start with `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, map required screens and components from `AI_DESIGN_APP_SCREEN_BLUEPRINT.md`, map the interaction state machine with `AI_WORKBENCH_INTERACTION_FLOWS.md`, choose a buildable vertical slice with `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` plus `design-ai-workbench-screens`, and fill AI Design App Invariants before coding: external AI is proposal-only until preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen proof are visible.
11. Use `PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md` to keep tokens, layout, component states, and motion consistent.
12. Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before implementing or sourcing reusable product components.
13. Fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` before coding: route/screen, primary object, product object model, visual system contract, user job, data/fixture truth, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, included/deferred states, action path, responsive behavior, commands, screenshots/browser evidence, and risks.
14. Preserve IA evidence in final reports: `Information architecture checked` must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior.
15. Preserve interaction evidence in final reports: `Interaction model checked` must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and the affected object/control.
16. Preserve copy/status evidence in final reports: `Copy/status language checked` must name affected object, state/status, reason or next action, and evidence/source/sample label.
17. Preserve decision/review evidence in final reports: `Decision/review cockpit checked` must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path.
18. Preserve visual-system evidence in final reports: `Visual system checked` must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
19. Preserve slice coherence in final reports: `Product read`, `Object model checked`, `Visual system checked`, `Workflow improved`, and `Implementation slice contract` must reference the brief's route/screen, primary object, product object model, visual system contract, workflow/actions, data/source truth, and states; generic `done/improved` or component-only wording is not enough.
20. Preserve component-state evidence in final reports: `Component state evidence checked` must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence.
21. Improve the smallest coherent surface first, then run `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` and `product-ui-visual-qa` to verify five-second clarity, desktop, tablet, mobile, keyboard, focus, reduced motion, and no overlap.

## Product UI Rules

- Do not force landing-page structure onto apps. No hero-first layout for dashboards, editors, admin tools, or ForgeStudio-like workbenches.
- Dense tools need hierarchy, alignment, state clarity, and speed more than decorative composition.
- Every repeated surface needs stable dimensions: tables, rows, cards, toolbar buttons, inspector fields, tabs, counters, chips, and tiles.
- Every user workflow needs empty, loading, error, disabled, selected, hover, focus-visible, pending, success, and rollback/retry states when relevant.
- Every important state needs factual copy: object, state, reason, next action, and evidence/sample label where relevant.
- Review and approval surfaces need a visible decision question, comparison/options, evidence, risk, action policy, after-state, and audit/recovery path.
- Motion must explain hierarchy, feedback, continuity, or state change. Delete decorative motion that slows a work surface.
- Do not invent metrics, logos, screenshots, testimonials, demo dashboard data, or proof-like UI. Label mock data as sample/demo or remove proof framing.
- Do not install component libraries in bulk. Pick the smallest item that solves a named interaction or state problem.
- Before adding a component source or dependency, name the product job it solves and check existing local components first.
- Do not code from a weak working brief. Core fields must name user/job/object, product object model, visual system contract, workflow/action path, data/source truth, route/screen, verification evidence, and top-design target; generic `improve UI`, `make better`, `use app`, `done`, or core-field `N/A` blocks coding.
- Do not code until the brief names the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
- Do not code an AI design app, canvas workbench, proposal/diff workflow, or ForgeStudio-like surface when AI Design App Invariants are missing or marked `N/A`. The brief must name where proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery appear.
- Do not call a final report ready if `Product read`, `Workflow improved`, or `Implementation slice contract` fail to mention the same route/screen, primary object, workflow/actions, data/source truth, and states from the working brief.
- Do not call a final report ready if `Information architecture checked` omits route/screen map, navigation/app shell, main/context zones, or responsive/recovery behavior.
- Do not call a final report ready if `Interaction model checked` omits primary actions/transitions, pending-success-failure states, recovery/permission behavior, or the affected object/control.
- Do not call a final report ready if `Copy/status language checked` omits affected object, state/status, reason or next action, or evidence/source/sample label.
- Do not call a final report ready if `Decision/review cockpit checked` omits decision question, options/comparison, evidence/risk, action, after-state, or audit/recovery path.
- Do not call a final report ready if `Visual system checked` omits typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, or target-local tokens/components.
- Do not call a final report ready if `Component state evidence checked` omits changed components/controls, concrete states, or screenshot/browser/manual/keyboard/responsive evidence.
- Do not call an AI design app final report ready unless `Operational pattern checked` names proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.

## Output

When planning, produce:

- Surface type:
- Runbook phase coverage:
- Brief/blueprint:
- Rubric target:
- Top-design benchmark:
- Design read:
- Product object model:
- Visual system contract:
- Visual system evidence:
- Workflow map:
- Information architecture:
- Information architecture evidence:
- Interaction model:
- Interaction evidence:
- Copy/status language:
- Copy/status evidence:
- Decision/review cockpit:
- Decision/review evidence:
- Screen recipe/state specs:
- Local files to inspect/change:
- Component state plan:
- AI Design App Invariants:
- Operational pattern:
- Interaction flow/invariants:
- AI workbench implementation slice:
- Screen inventory:
- Design-system baseline:
- Skill route:
- Component/source choices:
- Component blueprints:
- Implementation slice contract:
- State coverage:
- Component state evidence:
- Motion/proof/data safeguards:
- Verification/evidence plan:

When implementing, change files and verify with the project's real commands and screenshots where available. Finish with the done statement from `docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md`.
