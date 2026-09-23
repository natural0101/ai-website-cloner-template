<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Website Reverse-Engineer Template

## What This Is
A reusable template for reverse-engineering any website into a clean, modern Next.js codebase using AI coding agents. The Next.js + shadcn/ui + Tailwind v4 base is pre-scaffolded — just run `/clone-website <url1> [<url2> ...]`.

## One-Link Operating Mode
When the user provides a URL in this workbench and asks to clone, copy, rebuild, reverse-engineer, or simply sends the URL as the next target, treat it as `/clone-website <url>`.

Do not require the user to remember internal commands. First run `npm run clone:prepare -- <url1> [<url2> ...]` to create the target folders and `docs/research/CURRENT_TARGETS.*`, then follow the canonical `.agents/skills/clone-website/SKILL.md` end to end. Read the generated output plan before editing: preserve existing routes, use collision-resistant site/page namespaces, and resolve multi-origin or route conflicts before writing. Ask follow-up questions only when scope cannot be inferred safely, such as whether multiple pages are required or whether the clone should be exact versus adapted.

## Tech Stack
- **Framework:** Next.js 16 (App Router, React 19, TypeScript strict)
- **UI:** shadcn/ui (Radix primitives, Tailwind CSS v4, `cn()` utility)
- **Icons:** Lucide React (default — will be replaced/supplemented by extracted SVGs)
- **Styling:** Tailwind CSS v4 with oklch design tokens
- **Deployment:** Vercel

## Commands
Run verification locally only. Do not add, enable, dispatch, or restore GitHub Actions workflows in this repository, including when merging upstream updates. GitHub Actions are disabled by the repository owner's explicit instruction.

- `npm run dev` — Start dev server
- `npm run build` — Production build
- `npm run lint` — ESLint check
- `npm run typecheck` — TypeScript check
- `npm run check` — Run lint + typecheck + build
- `npm run design:check` — Verify universal design workbench docs, generated agent rules, and product UI skills are wired together
- `npm run design:handoff -- "<target-project>"` — Print an auto-selected ready prompt for an agent working in another repository
- `npm run design:handoff -- "<target-project>" --write` — Write `DESIGN_AGENT_HANDOFF.md` into the target project
- `npm run design:pack -- "<target-project>"` — Write `DESIGN_AGENT_HANDOFF.md` plus `.design-agent/` prompt, working brief, manifest, acceptance checklist, final report template, and `AGENTS.md` snippet into the target project
- `npm run design:install-agent-rules -- "<target-project>"` — Install or update a managed design-agent block in the target project's `AGENTS.md`
- `npm run design:packet-check -- "<target-project>"` — Verify that a target project contains a complete design agent packet
- `npm run design:brief-check -- "<target-project>"` — Verify that `.design-agent/working-brief.md` is filled before coding, including product object model, visual system contract, blueprint, screen recipe/state specs, local files, and component state plan
- `npm run design:final-check -- "<target-project>"` — Verify that `.design-agent/final-report-template.md` contains real evidence before final handoff
- `npm run design:target-audit -- "<target-project>" --write` — Write `.design-agent/readiness-report.md` with packet, brief, final-report, and next-command status

## Code Style
- TypeScript strict mode, no `any`
- Named exports, PascalCase components, camelCase utils
- Tailwind utility classes, no inline styles
- 2-space indentation
- Responsive: mobile-first

## Design Principles
- **Pixel-perfect emulation** — match the target's spacing, colors, typography exactly
- **No personal aesthetic changes during emulation phase** — match 1:1 first, customize later
- **Real content** — use actual text and assets from the target site, not placeholders
- **Beauty-first** — every pixel matters

## Project Structure
```
src/
  app/              # Next.js routes
  components/       # React components
    ui/             # shadcn/ui primitives
    sites/          # Site/page namespaces and shared extracted icons
  lib/
    utils.ts        # cn() utility (shadcn)
  types/            # TypeScript interfaces
  hooks/            # Custom React hooks
public/
  sites/            # Namespaced site/page images, fonts, videos, and SEO assets
docs/
  research/         # Inspection output (design tokens, components, layout)
  design-references/ # Screenshots and visual references
blender-workbench/  # Blender MCP handoff, scripts, references, renders, GLB, .blend
scripts/            # Asset download scripts
```

## Universal Design Workbench

This repository also acts as a reusable design knowledge base for agents working in other projects. For dashboard, admin, SaaS app, AI design studio, canvas editor, product UI, website, motion, 3D, component-system, proof/data-integrity, or general frontend design work, first read:

- `docs/design-workbench/AGENT_START_HERE.md`
- `docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md`
- `docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json`
- `docs/design-workbench/FORGESTUDIO_CONTEXT.md`
- `docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md`
- `docs/design-workbench/UNIVERSAL_DESIGN_RUNBOOK.md`
- `docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`
- `docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md`
- `docs/design-workbench/PRODUCT_UI_SCREEN_RECIPES.md`
- `docs/design-workbench/PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md`
- `docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md`
- `docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md`
- `docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md`
- `docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`
- `docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md`
- `docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md`
- `docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md`
- `docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md`
- `docs/design-workbench/PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md`
- `docs/design-workbench/PRODUCT_UI_COMPONENT_BLUEPRINTS.md`
- `docs/design-workbench/COMPONENT_STATE_SPEC.md`
- `docs/design-workbench/PRODUCT_UI_COMPONENT_SOURCING.md`
- `docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md`
- `docs/design-workbench/PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`
- `docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md`
- `docs/design-workbench/PRODUCT_UI_VISUAL_QA.md`
- `docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md`
- `docs/design-workbench/AGENT_REPORT_EXAMPLES.md`
- `.codex/skills/product-ui-design-orchestrator/SKILL.md`
- `.codex/skills/product-design-taste/SKILL.md`
- `.codex/skills/product-ui-component-sourcing/SKILL.md`
- `.codex/skills/product-ui-visual-qa/SKILL.md`
- `.codex/skills/design-ai-workbench-screens/SKILL.md`

Do not force the landing-page workflow onto product UI. Start non-clone design work with `UNIVERSAL_DESIGN_RUNBOOK.md`: project read, product model, surface blueprint, workflow map, information architecture, screen/interaction/state/copy/decision inventory, design-system baseline, component sourcing, visual craft, implementation slice, and verification. Then fill `UNIVERSAL_PRODUCT_DESIGN_BRIEF.md`, name the product object model, define the visual system contract, choose the closest `PRODUCT_SURFACE_BLUEPRINTS.md` pattern, map routes, navigation, zones, app shell, responsive IA, and recovery paths with `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`, choose concrete recipes from `PRODUCT_UI_SCREEN_RECIPES.md`, define action transitions with `PRODUCT_UI_INTERACTION_MODEL.md`, define factual UI labels, empty/error copy, AI/proof status language, sample/demo labels, and inline-vs-toast policy with `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`, and shape decision/review screens with `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md` so options, comparison, evidence, risk, approval, after-state, and audit/recovery are visible. Before coding, fill `PRODUCT_UI_IMPLEMENTATION_SLICE_CONTRACT.md` so the route/screen, primary object, product object model, visual system contract, user job, data/fixture source, closest product surface blueprint, screen recipe/state specs, local files to inspect/change, component state plan, states, actions, responsive behavior, commands, screenshots, and risks form one coherent slice. Use `PRODUCT_UI_DASHBOARD_ADMIN_PLAYBOOK.md` for dashboards, admin panels, records UIs, operations screens, and data tools before choosing cards, filters, tables, detail panes, charts, or bulk actions. Use `PRODUCT_UI_COMPONENT_BLUEPRINTS.md` before implementing or sourcing app shells, tables/lists, filters, drawers, inspectors, command menus, task/proposal panels, diff viewers, verification checklists, ledgers, export panels, alerts, or toasts, then define key component states with `COMPONENT_STATE_SPEC.md`. Use `product-design-taste` for dashboard, editor, workbench, SaaS app, AI design studio, canvas, data tool, and product-flow taste decisions. Use `product-ui-component-sourcing` before adding external UI components, registries, or libraries; prefer existing local components, name the product job, avoid bulk installs, and remove/labeled demo data. Use `AI_DESIGN_APP_TRUSTED_VERTICAL.md`, `design-ai-workbench-screens`, `AI_WORKBENCH_INTERACTION_FLOWS.md`, and `AI_WORKBENCH_IMPLEMENTATION_SLICES.md` for ForgeStudio-like screen planning: launcher/import, workspace selection, comment-to-proposal, proposal review, ledger/export, connection states, and the proposal -> preview/diff -> verification -> approval -> transaction -> ledger state machine. Use `PRODUCT_UI_TOP_DESIGN_BENCHMARK.md`, `PRODUCT_UI_REVIEW_RUBRIC.md`, `product-ui-visual-qa`, `VISUAL_QA_EVIDENCE_PLAYBOOK.md`, and `AGENT_REPORT_EXAMPLES.md` before final handoff: five-second test, top-design target, mediocrity risks fixed, product-specific details, rubric score, screenshots/browser checks, responsive/no-overlap review, coherent-slice coverage, visual-system evidence naming typography-spacing-surface-color-tokens, IA evidence naming route/screen map/navigation/zones/responsive recovery, interaction evidence naming actions/transitions/pending-success-failure/recovery-permission/object, copy/status evidence naming affected object/state-status/reason-next-action/evidence-source-sample, decision/review evidence naming decision-question/options-comparison/evidence-risk/action/after-state/audit-recovery, interaction/state/copy/decision coverage, component-state evidence naming changed controls/states/proof, accessibility basics, component/data/proof risk checks, evidence artifacts, and PASS/PASS WITH RISKS/FAIL verdict. Use landing-specific files only when the target surface is actually a landing/marketing flow, or when a specific source map such as motion safety, proof integrity, Animate UI, asset production, or visual QA is useful outside landing context.

For ForgeStudio-like products, treat the UI as a supervisor/review/comment/canvas/proposal/verification/export surface for an external AI agent. Prioritize workflow clarity, object selection, side panels, inspector states, task/comment loops, proposal approval, evidence, history, empty/error/loading states, agent connection/scopes, comment-to-task bridge, pending proposal/approval bridge, failure/recovery handling, and export/reopen paths before decorative polish.

When handing work to another agent in a different repository, give them `docs/design-workbench/EXTERNAL_AGENT_HANDOFF.md` first. It is the compact operating contract for importing this knowledge base without turning product UI work back into a landing-page task.
For automation or tool routing, use `docs/design-workbench/DESIGN_WORKBENCH_MANIFEST.json` as the machine-readable map of modes, docs, skills, commands, and non-negotiables.
Use `npm run design:handoff -- "<target-project>"` to auto-select a prompt, or pass `--mode dashboard|universal|forgestudio|scratch|qa` when the surface type is known.
Add `--write` when the target repository should receive a local `DESIGN_AGENT_HANDOFF.md` file for the next agent.
Prefer `npm run design:pack -- "<target-project>"` for serious external handoff work; it writes `DESIGN_AGENT_HANDOFF.md` plus `.design-agent/README.md`, `.design-agent/prompt.txt`, `.design-agent/working-brief.md`, `.design-agent/manifest.json`, `.design-agent/acceptance-checklist.md`, `.design-agent/final-report-template.md`, and `.design-agent/AGENTS_SNIPPET.md` into the target repository.
Use `npm run design:install-agent-rules -- "<target-project>"` when the target repository should receive a managed `AGENTS.md` block so future agents auto-discover the design packet.
Run `npm run design:packet-check -- "<target-project>"` before handing the target repository to another agent.
Run `npm run design:brief-check -- "<target-project>"` after `.design-agent/working-brief.md` is filled and before coding, then run `npm run design:final-check -- "<target-project>"` before final handoff.
Run `npm run design:target-audit -- "<target-project>" --write` whenever you need a compact readiness report for the target repository.
When updating the universal design workbench, run `npm run design:check` after syncing agent rules and product UI skills.

## Optional Local Resources

The published fork includes reusable design knowledge, Blender instructions, and scripts. Downloaded vendor bundles, generated media, private/local session files, and external skill checkouts may exist only in a local workbench and are not published. Inspect referenced paths before using them; an absent optional resource does not block the core website-cloning workflow. Do not automatically commit these resources.

## Blender Workbench
Blender and web-3D work lives in `blender-workbench/`. Before changing any Blender asset, read `blender-workbench/HANDOFF.md`, `blender-workbench/CURRENT_STATE.md`, and `blender-workbench/QUALITY_GATE.md`.

Use `blender-workbench/scripts/blender_socket_call.py` for Blender MCP calls on port `9876`. For "match this image" work, follow `blender-workbench/REFERENCE_MATCHING.md` and save reference images, preview renders, overlay metrics, validation reports, GLB exports, and `.blend` files back into `blender-workbench/`.

For hands, mascots, figures, contour masks, single-image reconstruction, silhouette matching, or `FRONT_2_5D`/`TRUE_360`/`HYBRID_HERO` work, use `blender-workbench/shape-reconstruction-upgrade/` and the local `blender-shape-reconstruction` skill snapshot before modeling.

For every Blender task, first read `blender-workbench/AGENT_START_HERE.md` and classify the mode: `text/design`, `shape reconstruction`, `organic object`, `icon/hero object`, or `GLB export`. For complex forms, repeated failures, multi-part assemblies, reference matching, or unusual lookdev, activate `blender-workbench/research-feedback-upgrade/` and the v4 skills: `blender-staged-production`, `blender-structural-qa`, `blender-example-retrieval`, and `blender-mcp-security`. Do not use MCP as a random bpy-code executor; prefer AI Blender Agent Kit tools/workflows, staged edits, render/overlay/inspection after each stage, and rollback when a result gets worse.

## MOST IMPORTANT NOTES
- When launching Claude Code agent teams, ALWAYS have each teammate work in their own worktree branch and merge everyone's work at the end, resolving any merge conflicts smartly since you are basically serving the orchestrator role and have full context to our goals, work given, work achieved, and desired outcomes.
- After editing `AGENTS.md`, run `bash scripts/sync-agent-rules.sh` to regenerate platform-specific instruction files.
- Edit `.agents/skills/clone-website/SKILL.md` and its `references/` as the canonical cloning workflow. Run `node scripts/sync-skills.mjs` to regenerate compatibility skills, references, and commands for all supported platforms; never edit generated copies directly.

@docs/research/INSPECTION_GUIDE.md

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
