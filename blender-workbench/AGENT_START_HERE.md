# Agent Start Here: Blender

This is the normalized entrypoint for Blender work in this repo. The v4 zip did not contain `AI_Blender_Agent_Kit/AGENT_START_HERE.md`; the nearest upstream entrypoint is `START_HERE_RU.md`. Use this file as the repo-local handoff.

## New Chat / New Agent Memory

If this work is being continued in a fresh chat, first read:

```text
blender-workbench/AGENT_MEMORY_PACKET/START_HERE_RU.md
```

That packet contains the latest user-context, current asset, hard rules, artifacts index and next-step plan. Treat it as the fastest onboarding path before reading the longer handoff docs.

## First Decision

Before any Blender task, classify the mode:

- `text/design` - 3D text, chrome/silver, clay, puffy, simple hero lettering.
- `shape reconstruction` - hands, mascot, single-image reference, silhouette/contour/layer stack.
- `organic object` - soft body, hand, fruit, character-like object, sculpted icon.
- `icon/hero object` - web hero GLB, visual asset, product-style scene.
- `GLB export` - optimization/export/validation of already built geometry.

## Skill Routing

- Use `blender-web-3d` for text/design, soft shapes, materials, lighting, camera, GLB.
- Use `blender-shape-reconstruction` for hands, figures, contours, masks, `FRONT_2_5D`, `TRUE_360`, `HYBRID_HERO`.
- Use `blender-staged-production` for complex assets, repeated failures, multi-part assemblies, unusual lookdev, or reference matching.
- Use `blender-structural-qa` for gaps, floating parts, contacts, fingers/limbs, assemblies.
- Use `blender-example-retrieval` before unfamiliar geometry/material code or after first API/topology/style failure.
- Use `blender-mcp-security` before arbitrary Python, local file ingestion, downloads, external generators, or writing outside workbench/output roots.

## Required Production Loop

1. Read-only inspect first.
2. Run capability probe when v4/staged work is active.
3. Create or update a scene graph with named parts, expected contacts, dimensions, materials, and acceptance criteria.
4. Work stage by stage: `INITIALIZATION -> GEOMETRY -> MATERIAL -> COMPOSITION -> LIGHTING -> EXPORT_QA`.
5. Change one dominant defect per attempt.
6. After every stage/attempt, produce render, overlay or inspection evidence.
7. If the result is worse, rollback to the checkpoint/best attempt.
8. Final check must include silhouette, proportions, material, lighting, camera, structural QA, and GLB readiness.

## Hard Rules

- Do not use MCP as "run random bpy code".
- Prefer AI Blender Agent Kit tools/workflows over ad hoc scripts.
- Do not mix geometry, material, camera, and lighting fixes in one patch.
- Do not call a single-image reconstruction true 360 unless hidden-side assumptions are explicitly accepted.
- Do not export preview cards, lights, cameras, reference planes, or old test objects into GLB.
- Keep authoritative state in `CURRENT_STATE.md` and reports in `artifacts/reports/`.
