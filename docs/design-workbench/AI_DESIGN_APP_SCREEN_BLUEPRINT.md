# AI Design App Screen Blueprint

Use this when designing ForgeStudio-like products or any AI-assisted design/workbench application from scratch.

For detailed screen/component/state patterns, also use:

```text
docs/design-workbench/AI_DESIGN_APP_TRUSTED_VERTICAL.md
.codex/skills/design-ai-workbench-screens/SKILL.md
.codex/skills/design-ai-workbench-screens/references/ai-workbench-screen-patterns.md
docs/design-workbench/AI_WORKBENCH_INTERACTION_FLOWS.md
docs/design-workbench/AI_WORKBENCH_IMPLEMENTATION_SLICES.md
docs/design-workbench/PRODUCT_UI_INFORMATION_ARCHITECTURE.md
docs/design-workbench/PRODUCT_UI_INTERACTION_MODEL.md
docs/design-workbench/PRODUCT_UI_COPY_STATUS_LANGUAGE.md
docs/design-workbench/PRODUCT_UI_DECISION_REVIEW_COCKPIT.md
```

## Product Spine

Start with `AI_DESIGN_APP_TRUSTED_VERTICAL.md` when the app resembles ForgeStudio or any external-agent design workflow. It defines the trusted vertical, source-of-truth objects, false-state bans, and slice QA that prevent the screen from becoming a decorative chat/editor shell.

The UI must expose this loop as real surfaces:

```text
project open -> design search -> import map -> canvas -> object comment/task -> agent proposal -> preview/diff -> verification -> approve/revise -> ledger/history -> export/reopen
```

Do not collapse this into a chat page. Chat can be a secondary affordance, not the product spine.

For route maps, workspace zones, responsive IA, and recovery placement, use `PRODUCT_UI_INFORMATION_ARCHITECTURE.md`. For generic action transitions, use `PRODUCT_UI_INTERACTION_MODEL.md`. For status labels, empty/error copy, sample/demo labels, and AI/proof language, use `PRODUCT_UI_COPY_STATUS_LANGUAGE.md`. For proposal review, import approval, verification review, export review, and ledger decisions, use `PRODUCT_UI_DECISION_REVIEW_COCKPIT.md`. For the AI workbench object model, allowed state transitions, proof requirements, and interaction QA gate, use `AI_WORKBENCH_INTERACTION_FLOWS.md` before drawing or refactoring screens. For concrete vertical slices to implement first, use `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`.

## Required Screens

| Screen | Purpose | Must show | States |
| --- | --- | --- | --- |
| Project launcher | Open or reopen a local project | Recent projects, open folder, connection/privacy status | Empty recent list, folder permission denied, indexing unavailable |
| Design search report | Explain what was found | Pages, components, assets, fonts, code, 3D, warnings | No pages found, partial scan, import warnings |
| Import review | Let user approve discovered surfaces | Import candidates, source paths, confidence, asset dependencies | Needs approval, skipped asset, unsupported file |
| Studio workspace | Main work surface | Canvas, project map, layers/assets, inspector, comments/tasks, agent/proposals | No project, no page selected, agent disconnected |
| Canvas viewport | Inspect and select visual objects | Page/frame, selection overlays, zoom, pan, breakpoints | Loading preview, render error, missing asset |
| Object inspector | Edit/view selected object | Properties, source file, constraints, tokens, responsive values | No selection, multi-selection, locked object |
| Comment/task thread | Turn feedback into work | Anchor, message, task status, linked tx/proposal | Draft, pending agent, needs revision, resolved |
| Agent proposal panel | Review agent output | Summary, changed objects/files, diff, checks, risk | No agent, pending, failed, blocked, ready to preview |
| Preview/diff | Compare before/after | Visual diff, code diff, viewport variants, acceptance checks | Diff unavailable, verification failed, stale proposal |
| Ledger/history | Audit what happened | Transactions, actor, linked comments, time, result | Empty history, rollback unavailable, conflict |
| Export/share | Produce artifact | Target path, file list, warnings, open result | Export pending, failed, partial, completed |
| Settings/connection | Configure local agent/MCP/privacy | Daemon status, endpoint, provider, network defaults | Disconnected, unhealthy, permission required |

## Workspace Layout

Default desktop layout:

```text
top bar: project, page, agent status, verification/export
left rail: project map, pages, layers/assets
center: canvas and preview
right panel: inspector or proposal/diff
bottom/status bar: zoom, viewport, selection, ledger summary, warnings
```

Rules:

- Keep the canvas central and visually quiet.
- Keep sidebars resizable/collapsible but never hidden by default on desktop.
- Mirror selection across canvas, layers, inspector, comments, and ledger when relevant.
- Put destructive actions behind confirmation or reversible history.
- Use tooltips for icon-only tools; do not label every toolbar icon with text.

## Component Inventory

| Component | Notes |
| --- | --- |
| Project/source tree | Supports file path, page/component/asset type, warning badges |
| Layer list | Stable row height, selection, lock/visibility, nested groups |
| Canvas controls | Zoom, pan, fit, breakpoint, grid, selection mode |
| Inspector fields | Label, value, unit, token binding, reset, disabled/locked state |
| Comment anchor | Position-aware, selection-linked, readable at zoom levels |
| Task card | Status, owner/agent, anchor, latest message, linked transaction |
| Proposal card | Summary, risk, changed files/objects, acceptance checks |
| Verification checklist | Passed/warning/failed grouping, worst state first |
| Diff viewer | Before/after, visual/code tabs, viewport selector |
| Decision cockpit | Decision question, comparison, evidence, risk, approve/revise/reject, after-state |
| Action ledger row | Actor, transaction, linked comment, time, rollback/reopen |
| Toast/inline alert | Reserve toast for transient events; use inline for actionable failures |

## Status Language

Use direct, factual UI copy:

- "Agent disconnected"
- "Project not imported"
- "3 assets skipped"
- "Proposal needs approval"
- "Verification failed"
- "Export completed"
- "Sample proposal"
- "Ledger row created"

Avoid fake confidence and vague success:

- "AI fixed it"
- "Everything ready"
- "Looks good"
- "Magic applied"
- "Done" before accepted diff, closed task/comment, and ledger/history evidence

## Responsive Strategy

This is a tool. Desktop is primary.

- Desktop: full multi-panel workspace.
- Tablet: collapsible sidebars, canvas remains central, proposal/inspector in drawer.
- Mobile: review/comment/status mode first; deep editing can be limited, but must not break.

## Minimum Prototype Slice

If time is limited, build this vertical slice:

```text
open project -> show design search summary -> select page -> select object -> create comment task -> show mock proposal state -> preview/diff placeholder -> approve/revise controls -> ledger row -> export state
```

Even if the backend is incomplete, the UI must honestly label mock/sample states and not claim real agent work.

For a fuller sequence of buildable slices, use `AI_WORKBENCH_IMPLEMENTATION_SLICES.md`.
