---
name: landing-implementation-task-graph
description: Turn a landing-page strategy, storyboard, asset queue, motion plan, component plan, and visual style tile into an ordered implementation task graph with stable task IDs, build rings, blockers, files/routes, visible results, verification steps, screenshots, dependency budget, and evidence requirements. Use before writing final implementation tasks or handing a landing plan to another implementation agent.
---

# Landing Implementation Task Graph

Use this skill after the plan has section storyboard, asset queue, motion recipes, component choices and a visual style tile, but before implementation handoff.

## Required Files

Read:

```text
план разработки топового лендинга/23-implementation-task-graph.md
план разработки топового лендинга/projects/<slug>/05-visual-direction.md
план разработки топового лендинга/projects/<slug>/06-section-by-section-upgrade-plan.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/14-animate-ui-selection.md
план разработки топового лендинга/projects/<slug>/16-motion-recipe-selection.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/20-implementation-task-graph.md
план разработки топового лендинга/projects/<slug>/09-implementation-tasks.md
план разработки топового лендинга/projects/<slug>/11-implementation-handoff-prompt.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. Extract protected constraints first: routes, nav labels, form fields, analytics-sensitive labels, legal copy, SEO-critical content and claims.
2. Create ring 0 preserve task before any visual work.
3. Create ring 1 foundation tasks for tokens, shell, typography, spacing, surfaces and reusable wrappers.
4. Create section structure tasks before asset and motion tasks.
5. Create asset tasks from `19-asset-production-queue.md` before motion tasks that depend on those assets.
6. Create motion tasks from `16-motion-recipe-selection.md` only after section structure and assets exist.
7. Create responsive, accessibility and performance tasks after major sections exist.
8. Create final QA and handoff tasks last.
9. Mirror the final ordered summary into `09-implementation-tasks.md`.
10. Update `11-implementation-handoff-prompt.md` so implementation follows the graph order.

## Task Row Standard

Every task must include:

- stable `task-###` ID;
- build ring;
- type;
- section;
- `Blocked by`;
- `Blocks`;
- files or routes;
- plan sources;
- visible result;
- implementation notes;
- dependencies;
- verification;
- evidence to capture;
- risk;
- status.

## Rules

- Do not let motion tasks start before related structure and asset tasks.
- Do not let component install tasks start before source registry and dependency approval.
- Do not let Animate UI install tasks start before `14-animate-ui-selection.md` names the exact registry item and fallback.
- Do not let final QA start before screenshots and command results are planned.
- Do not create vague tasks such as "make hero better". State the visible result and evidence.
- Do not mark a task done without matching evidence.

## Output Standard

The graph should let a fresh implementation agent answer:

- what to do first;
- what is blocked;
- what files/routes are involved;
- what visible result should appear;
- what design/source documents justify the task;
- what screenshot or command proves it;
- which dependencies are accepted and why.
