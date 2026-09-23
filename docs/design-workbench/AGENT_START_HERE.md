# Universal Design Agent Start Here

Use this folder as a design knowledge base even when the active project lives somewhere else. Do not edit this repository unless the user explicitly asks; import the ideas, skills, source maps, and QA gates into the target project.

## First Read

1. `AGENTS.md`
2. `docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md`
3. `docs/design-workbench/FORGESTUDIO_CONTEXT.md`
4. `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md`
5. `docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md`
6. `docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`
7. `docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md`
8. `docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md`
9. `docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`
10. `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md`
11. `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md`
12. `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md`
13. `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`
14. `docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md`
15. `docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md`
16. `docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md`
17. `docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md`
18. `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`
19. `docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md`
20. `docs/design-workbench/COMPONENT_STATE_SPEC.md`
21. `docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md`
22. `docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md`
23. `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`
24. `docs/design-workbench/PRODUCT_UI_VISUAL_QA.md`
25. `docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md`
26. `docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md`
27. `docs/design-workbench/AGENT_REPORT_EXAMPLES.md`
28. `docs/design-workbench/AGENT_PROMPTS.md`
29. `.codex/skills/product-ui-design-orchestrator/SKILL.md`
30. `.codex/skills/product-ui-design-orchestrator/references/universal-product-ui-playbook.md`
31. `.codex/skills/product-design-taste/SKILL.md`
32. `.codex/skills/product-design-taste/references/product-design-taste-playbook.md`
33. `.codex/skills/design-ai-workbench-screens/SKILL.md`
34. `.codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md`
35. `.codex/skills/product-ui-component-sourcing/SKILL.md`
36. `.codex/skills/product-ui-component-sourcing/references/component-sourcing-matrix.md`
37. `.codex/skills/product-ui-visual-qa/SKILL.md`
38. `.codex/skills/product-ui-visual-qa/references/visual-qa-checklist.md`
39. `docs/research/animate-ui-catalog.md`
40. `docs/research/animate-ui-whole-site-audit.md`
41. `план разработки топового лендинга/53-motion-safety-source-map.md`
42. `план разработки топового лендинга/54-proof-integrity-source-map.md`

## What This Knowledge Base Is For

It is no longer only a landing-page workbench. Use it for:

- dashboards, admin panels, and data tools should use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`;
- AI design tools and canvas editors;
- SaaS product UI;
- websites and landing pages;
- component systems;
- motion, 3D/WebGL, generated assets, proof/data integrity, and final QA.

## Default Agent Route

1. Classify the surface before designing.
2. Follow `UNIVERSAL_DESIGN_RUNBOOK.md` for the full order of work.
3. Fill `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md` mentally or explicitly before choosing layout; do not code until the brief names the product object model, visual system contract, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan.
4. Pick the closest surface from `PRODUCT_SURFACE_BLUEPRINTS.md`.
5. Choose the screen recipe from `PRODUCT_UI_SCREEN_RECIPES.md`.
6. For dashboards, admin panels, and data tools, use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`.
7. Map object hierarchy, routes, navigation, zones, and responsive behavior with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`.
8. Define action transitions, pending/failure/recovery states, and proof behavior with `PRODUCT_UI_INTERACTION_MODEL.md`.
9. Define factual labels, empty/error/disconnected copy, sample/demo labels, and inline-vs-toast policy with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`.
10. Shape approval, comparison, triage, and proposal-review surfaces with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`.
11. Read the product workflow before changing visual style.
12. Use existing project conventions first.
13. Route to the smallest useful skill set.
14. Improve workflow states, copy, decisions, and hierarchy before decoration.
15. For AI design apps, start with `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, then map screens through `AI_DESIGN_APP_SCREEN_BLUEPRINT.md`, product-state transitions through `AI_WORKBENCH_INTERACTION_FLOWS.md`, and build order through `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`. If a `.design-agent/working-brief.md` packet exists, fill AI Design App Invariants before coding: proposal-only behavior, preview/diff, verification, human approval, transaction/ledger evidence, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen recovery.
16. Use `PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md` for tokens, controls, and state standards.
17. Fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` before coding so the work is one coherent route/screen/workflow, not isolated polish.
18. Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before implementing or sourcing reusable product components.
19. Define key component states with `COMPONENT_STATE_SPEC.md`.
20. Use `PRODUCT_UI_QUALITY_GATE.md` as the done checklist.
21. Check `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` so the result is not merely acceptable: run the five-second test, identify mediocrity risks, and name product-specific details.
22. Score the result with `PRODUCT_UI_REVIEW_RUBRIC.md`; fix any 0 before final handoff.
23. Use `VISUAL_QA_EVIDENCE_PLAYBOOK.md` and `product-ui-visual-qa` before final handoff; verify with screenshots/build/tests when the target project supports it.
24. Use `AGENT_REPORT_EXAMPLES.md` to shape the final report: rubric, evidence, blockers, risks, verdict.

## Skill Routing

| Task | Use |
| --- | --- |
| General app/dashboard/editor UI | `product-ui-design-orchestrator`, `UNIVERSAL_DESIGN_RUNBOOK.md`, `PRODUCT_UI_SCREEN_RECIPES.md` |
| Dashboard/admin/data tool operations UI | `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`, `product-design-taste` |
| Information architecture and navigation | `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, `UNIVERSAL_DESIGN_RUNBOOK.md` |
| Product interactions/action transitions | `PRODUCT_UI_INTERACTION_MODEL.md`, `COMPONENT_STATE_SPEC.md` |
| Product copy/status language | `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, `PRODUCT_UI_INTERACTION_MODEL.md`, `COMPONENT_STATE_SPEC.md` |
| Decision/review/approval surfaces | `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`, `PRODUCT_UI_INTERACTION_MODEL.md`, `PRODUCT_UI_REVIEW_RUBRIC.md` |
| Implementation slice planning | `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, `UNIVERSAL_DESIGN_RUNBOOK.md`, `PRODUCT_UI_VISUAL_QA.md` |
| Product UI taste from scratch | `product-design-taste` |
| AI design app / canvas workbench screens | `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, `design-ai-workbench-screens`, `AI_WORKBENCH_INTERACTION_FLOWS.md`, `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` |
| Product UI components and libraries | `product-ui-component-sourcing`, `COMPONENT_STATE_SPEC.md` |
| Product component anatomy/states | `PRODUCT_UI_COMPONENT_BLUEPRINTS.md`, `COMPONENT_STATE_SPEC.md` |
| Product UI visual QA / final review | `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`, `product-ui-visual-qa`, `ui-audit`, `PRODUCT_UI_REVIEW_RUBRIC.md`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md`, `AGENT_REPORT_EXAMPLES.md` |
| Existing UI upgrade | `redesign-existing-projects`, `ui-audit`, `ui-refactor-principles` |
| Detailed polish | `details-that-make-interfaces-feel-better` |
| Distinctive new frontend | `frontend-design-for-distinctive-interfaces` |
| Tailwind system | `tailwind-design-system-v4` |
| shadcn/Radix React primitives | `shadcn-ui` |
| Animate UI | `animate-ui-catalog` plus live endpoint check |
| Motion | `animation-systems-for-product-grade-web-motion` plus motion safety source map |
| Claims, screenshots, metrics, demo data | proof integrity source map |
| Landing conversion | landing workflow files |
| 3D/WebGL/Blender | `blender-workbench` and 3D skills |

## Dashboard And Product UI Defaults

- No landing hero unless the actual surface is marketing.
- Favor dense but organized scanning over decorative cards.
- Make sidebars, tables, inspectors, forms, filters, command menus, task queues, review states, and history easy to repeat-use.
- Final visual-system evidence must name typography/type scale, spacing/density rhythm, surfaces/radius/borders, color/status/contrast, and target-local tokens/components.
- Final information-architecture evidence must name route/screen map, navigation/app shell, main/context zones, and responsive/recovery behavior.
- Final interaction evidence must name primary actions/transitions, pending-success-failure states, recovery/permission behavior, and affected object/control.
- Final copy/status evidence must name affected object, state/status, reason or next action, and evidence/source/sample label.
- Final decision/review evidence must name decision question, options/comparison, evidence/risk, action, after-state, and audit/recovery path.
- Every important pane needs empty, loading, error, disabled, selected, pending, success, and retry/rollback states when relevant.
- Final component-state evidence must name changed components/controls, concrete states checked, and screenshot/browser/manual/keyboard/responsive evidence.
- Status copy must name the affected object, reason, next action, and evidence/sample label when relevant.
- Decision/review screens must show the decision question, options/comparison, evidence, risks, actions, after-state, and audit/recovery path.
- Implementation must target a coherent slice with route/screen, object, data/fixture truth, states, actions, responsive behavior, and evidence.
- AI design app work must expose proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen surfaces before it is treated as a real product slice.
- Motion should help continuity and feedback, not distract from work.
- Do not invent proof, metrics, logos, testimonials, screenshots, or "real" data.

## Animate UI Current Facts

Latest full crawl recorded in this knowledge base:

- Useful live surface: `/docs` and `/r`.
- Docs routes: 171.
- Docs `.mdx`: 171/171 live.
- Registry items: 580.
- Item endpoints: 580/580 live.
- Service maps such as `sitemap.xml`, `robots.txt`, `llms.txt`, `docs.json`, and `openapi.json` return 404.
- Live `GET /r/registry.json` can abort or stall; use GitHub raw registry for full inventory, then verify exact live `/r/<item>.json` before install.

## Pasteable Prompt For Another Agent

Prefer generating a target-local packet first:

```bash
npm run design:pack -- "<TARGET_PROJECT_PATH>"
npm run design:install-agent-rules -- "<TARGET_PROJECT_PATH>"
npm run design:packet-check -- "<TARGET_PROJECT_PATH>"
npm run design:brief-check -- "<TARGET_PROJECT_PATH>"
npm run design:final-check -- "<TARGET_PROJECT_PATH>"
npm run design:target-audit -- "<TARGET_PROJECT_PATH>" --write
```

Then give the receiving agent `DESIGN_AGENT_HANDOFF.md` and `.design-agent/acceptance-checklist.md` from the target project.
The receiving agent should fill `.design-agent/working-brief.md` before coding and use `.design-agent/final-report-template.md` before final handoff. If `AGENTS.md` should be updated manually instead of by command, use `.design-agent/AGENTS_SNIPPET.md`.
`design:brief-check` must pass before coding; it rejects generic product fields and requires user/job/object, product object model, visual system contract, workflow/action path, data/source truth, verification evidence, route/screen, and top-design target. For AI design apps it also rejects missing or `N/A` AI Design App Invariants.
It also requires the agent to choose the closest product surface blueprint, screen recipe/state specs, local files to inspect/change, and component state plan before coding.

```text
Use the design knowledge base at:
C:\Users\se-20\OneDrive\Рабочий стол\ai-website-cloner-template

The active project is elsewhere. Do not modify the knowledge-base repository unless asked.

Read docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md, docs/design-workbench/AGENT_START_HERE.md, docs/design-workbench/FORGESTUDIO_CONTEXT.md, docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md for AI design apps/canvas workbenches, docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md, docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md, docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md, docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md, docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md for dashboard/admin/data-tool work, docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md, docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md, docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md, docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md, docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md, docs/design-workbench/COMPONENT_STATE_SPEC.md, docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md, docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md, docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md, docs/design-workbench/AGENT_REPORT_EXAMPLES.md, .codex/skills/product-ui-design-orchestrator/SKILL.md, .codex/skills/product-design-taste/SKILL.md, .codex/skills/product-ui-component-sourcing/SKILL.md, .codex/skills/product-ui-visual-qa/SKILL.md, and .codex/skills/design-ai-workbench-screens/SKILL.md when the target is an AI design app or canvas/editor workbench. For AI design apps, also read docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md, docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md, and docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md before layout work; fill AI Design App Invariants with proposal-only, preview/diff, verification, human approval, transaction/ledger, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen visibility. Start by following the Universal Design Runbook, filling the Universal Product Design Brief, naming the product object model, defining the visual system contract, choosing the closest Product Surface Blueprint, mapping information architecture, choosing a screen recipe, naming local files to inspect/change, defining component state specs, defining action transitions, defining copy/status language, shaping decision/review cockpits, choosing component blueprints, and planning the rubric/evidence path. Improve the active project's product UI/dashboard/editor/site using the installed skills and source maps. Do not force landing-page structure onto product UI. Route product taste, screen patterns, IA/navigation, interactions, copy/status, decision/review, component, motion, proof/data, 3D, and QA decisions through the local skills and source maps. Before final handoff, run the top-design benchmark, score with the product UI review rubric, run product UI visual QA with evidence, and report `Component state evidence checked` with changed components/controls, states, and screenshot/browser/manual/keyboard/responsive proof.
```
