---
name: product-ui-component-sourcing
description: "Use when choosing, adding, adapting, or auditing component sources and UI primitives for product interfaces: dashboards, admin panels, SaaS apps, AI design studios, canvas editors, data tools, app shells, sidebars, tables, trees, inspectors, command menus, drawers, dialogs, tabs, forms, charts, upload flows, proposal/diff panels, verification checklists, ledgers, history, and export/share surfaces. Helps agents avoid bulk installs, fake demo blocks, incompatible libraries, and landing-page component bias."
---

# Product UI Component Sourcing

Use this skill before adding or copying any third-party UI component into a product app. It routes component decisions through workflow, accessibility, dependency, and state needs instead of visual novelty.

## Required Reading

Always read:

```text
docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md
docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md
docs/design-workbench/COMPONENT_STATE_SPEC.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md
references/component-sourcing-matrix.md
```

For AI design studios or canvas editors, also read:

```text
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
.codex/skills/design-ai-workbench-screens/SKILL.md
.codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md
```

For Animate UI, Blocks.so, Kibo/Coss, ReUI, SmoothUI, Motion Primitives, or other catalogs, read the matching local catalog skill/source map before using the item.

## External Packet Discipline

When working in a target repository that has a `.design-agent/` packet, read `.design-agent/working-brief.md` before choosing or adding components, then verify it from the knowledge-base repository with `npm run design:brief-check -- "<target-project>"`. Record component choices in `.design-agent/final-report-template.md`, run `npm run design:final-check -- "<target-project>"` before final handoff, and refresh `.design-agent/readiness-report.md` with `npm run design:target-audit -- "<target-project>" --write`.

## Workflow

1. Name the job of the component in product terms: scan, select, edit, filter, compare, review, approve, recover, export, or navigate.
2. For AI design studios or canvas editors, map the component to `AI_DESIGN_APP_TRUSTED_VERTICAL.md`: source-of-truth object, false-state risk, proof/evidence surface, decision question, after-state, or recovery path.
3. Confirm where the component lives in `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`: app shell, main work zone, context/review zone, global action, local action, recovery path, or responsive fallback.
4. Define the component's action transitions with `PRODUCT_UI_INTERACTION_MODEL.md`: enabled, pending, success, failure, retry, undo/rollback, permission, proof.
5. Define factual status labels and messages with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`: object, state, reason, next action, evidence/source, and sample/demo/disconnected labels.
6. Define decision/review role with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`: comparison, evidence, risk, approval/rejection, after-state, audit/recovery.
7. Confirm the component belongs to a coherent implementation slice from `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`, not an isolated visual fragment.
8. Choose the nearest component blueprint from `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` and fill the relevant `COMPONENT_STATE_SPEC.md` fields.
9. Check `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md` so the component improves five-second clarity, product-specific detail, and visual precision instead of adding generic catalog polish.
10. Inspect the target project's existing UI stack and local components. Prefer existing primitives and wrappers first.
11. Choose the smallest source that provides the missing behavior:
   - Local component or native Tailwind/CSS.
   - shadcn/Radix/headless primitive.
   - Focused library such as TanStack Table, Monaco/CodeMirror, React Hook Form, cmdk, or Recharts only when the behavior warrants it.
   - Verified catalog item only when it saves real implementation work and can be adapted away from demo content.
12. Check dependency impact, license/source, accessibility, keyboard behavior, state/copy/decision coverage, responsive behavior, reduced-motion needs, and bundle/client boundary.
13. Record why each accepted component is accepted and why rejected candidates are rejected.
14. Implement one component/source at a time. Do not bulk-install a catalog.
15. Verify changed surfaces with build/typecheck and screenshots when available.

## Hard Rules

- Do not add a component because it looks good in a catalog.
- Do not install multiple UI systems for one screen.
- Do not use a landing block where a table/list/tree/inspector is the real product primitive.
- Do not leave fake users, fake metrics, fake AI chats, fake files, fake tables, or fake agent activity in product UI.
- Do not replace accessible primitives with custom divs unless there is a clear reason and the behavior is implemented.
- Do not use an animated component in dense work panes unless motion clarifies state, hierarchy, or continuity.

## Output Contract

For each candidate component/source, output:

- Product need:
- Top-design role:
- Trusted vertical role:
- IA placement:
- Interaction transitions:
- Copy/status language:
- Decision/review role:
- Implementation slice:
- Component blueprint:
- Existing local option:
- Candidate source:
- Accepted/rejected:
- Why:
- Dependency/license impact:
- State coverage:
- Accessibility/keyboard:
- Mobile/reduced-motion:
- Demo-data cleanup:
- Files affected:
- Verification:
