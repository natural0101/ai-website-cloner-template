# ForgeStudio Design Context

ForgeStudio is a local-first, AI-auditable design engineering studio for 2D, 3D, motion, and code. It is not a Figma clone or a chat page. The upstream product contract still emphasizes an external-AI-operated landing workspace for v0.1, while the root spec frames the product more broadly as a desktop app for visual products: pages, landings, UI components, images, fonts, 3D assets, code, export, history, and agent review.

Source inspected:

- `https://github.com/natural0101/ForgeStudio/tree/dev`
- Branch `dev`, visible head during latest check on 2026-07-04: `fb23246912b64135b7a17c5765c822672f10c300`
- Local read-only clone was used only to understand the product shape.

## Dev Repo Anatomy

The `dev` branch is a Vite/Vue studio plus local daemon/desktop shell and shared TypeScript packages:

- `apps/studio`: supervisor UI with canvas, left/right panels, AI command bar, comment threads, proposal cards, review tasks, verification checklist, action ledger, export/project panels, 3D viewport, and browser/accessibility/product-vertical tests.
- `apps/forge-daemon`: local MCP/HTTP daemon, browser verifier, agent action scheduler/worker, desktop/local release smoke tests, approval bridge, and golden vertical e2e tests.
- `apps/desktop`: Electron wrapper, local daemon launcher, tray/menu/window state, splash, guide window, installer config.
- `packages/application-service`: headless project session owner for UI, daemon, MCP, comments, proposals, previews, live merge metadata, and review reports.
- `packages/agent-gateway`: external-agent task/proposal/revision/export gateway and smoke tests.
- `packages/workspace-sync`: local project tree, design search, frontend files, registry, image dimensions, and export target logic.
- `packages/core-scene`, `core-transaction`, `core-history`, `contracts`, `validation`, `code-sync`, `render-2d`, `render-3d`, `landing-intelligence`: scene graph, transaction, ledger/history, schemas, code import/export, 2D/3D rendering, landing import intelligence.

Useful source lesson: the product is already organized around testable vertical behavior, not isolated UI pieces. Our agents should mirror that by choosing an implementation slice with route, object, state, action, evidence, and rollback/export path before visual polish.

Universal AI-design-app lesson: design the operational vertical before the screen. For any AI design product, the UI should expose source objects, permissions/scopes, pending work, proposal boundaries, preview/diff, verification, human approval, applied transaction, audit ledger, recovery, and export/reopen. If any link is mocked or deferred, label it near the affected object instead of hiding it behind optimistic status copy.

## Source-Derived Bridge Gate

The strongest ForgeStudio failure mode is not weak styling; it is a broken operational bridge hidden behind plausible panels. A ForgeStudio-like UI must make these bridges visible in the brief, implementation slice, and final report:

- agent connection/scopes: disconnected, connecting, connected, unhealthy, capability/scope grant, daemon/MCP endpoint, and permission-denied states;
- comment-to-task bridge: anchored comment, object/page/revision link, task status, agent inbox/thread link, and revise/resolve path;
- pending proposal/approval bridge: pending proposal source, changed objects/files, live-session handoff/poll/merge status, approve/revise/reject, and stale/conflict states;
- failure/recovery handling: inline failures for scan/import/agent/verification/export, no silent `console.warn`-only result, retry/rollback/reopen path, and reason next to the affected object;
- export/reopen persistence: target path, artifact list, partial/failure warnings, and proof that reopen/history preserves comments, ledger, and assets.

If any bridge is backend-incomplete, the UI must label the state as sample, blocked, disconnected, unavailable, or deferred. Do not replace a broken bridge with a decorative chat, optimistic success toast, or fake connected status.

## Product Essence

ForgeStudio lets a user open a local project folder, indexes pages/landings/components/assets/fonts/3D/code, imports visual surfaces into a studio, lets the user comment on objects, turns comments into external-agent tasks, receives proposal transactions, previews/verifies diffs, accepts or requests revision, then exports or reopens history.

Core loop:

```text
external agent -> inspect -> propose -> preview -> verify -> comment -> revise -> export
```

Canonical scene state is changed only through `DesignTransaction` and the transaction engine. External AI clients are proposal-only operators. The UI is a supervisor, review, comment/task, preview, evidence, approval, export, and rollback surface.

Upstream wording to preserve:

- README frames the current app as a local workspace for creating and checking landing pages with an external AI agent.
- `FORGE_PRODUCT_ROOT_SPEC.md` defines the non-negotiable vertical: open local folder -> design search -> import -> canvas -> object comment -> agent task -> proposal -> preview/diff -> approve or revise -> export/reopen.
- `docs/PRODUCT_CONTRACT.md` says the main operator is an external AI agent, and ForgeStudio is the supervisor/review client.
- The v0.1 contract requires motion and limited GLB/Web 3D to run in the published landing runtime.
- Current docs also frame ForgeStudio as a local desktop supervisor with loopback daemon/MCP, scoped agent sessions, pending approvals, review comment threads, action ledger, preview/export surfaces, save/reopen/recovery, and a golden-local-project release gate.
- Agent-facing flows use scoped MCP tools and resources: capabilities, agent session, inspect/propose/preview/verify/comment/revise/export, comment inbox/thread/reply, session summary, and proposal-only writes.

Knowledge-base interpretation:

- Use ForgeStudio as the clearest reference for AI-operated design workflow, anchored comments, proposals, verification, ledger/history, and export.
- Use `AI_WORKBENCH_INTERACTION_FLOWS.md` to preserve the state machine: proposal -> preview/diff -> verification -> human approval -> `DesignTransaction` -> ledger/history.
- Use ForgeStudio's newer review cockpit, pending approvals, comment-thread model, scoped permissions, and golden e2e gate as examples for product UI that exposes real work instead of decorative status.
- Do not copy its landing-only v0.1 framing into unrelated dashboards, admin panels, SaaS apps, or editor surfaces.
- For product UI, keep the same rigor: real state, no fake agent/proof, stable review loops, and visible evidence.

## Design Implications For Agents

For ForgeStudio-like implementation or audit work, use `AI_DESIGN_APP_TRUSTED_VERTICAL.md` as the operating contract after this context file. It converts the source read into source-of-truth objects, false-state bans, implementation slices, proof/evidence expectations, and QA questions.

- Prioritize product workflow clarity over decorative landing aesthetics.
- Show real project state: pages, components, assets, fonts, 3D assets, code, import warnings, agent connection, pending proposals, verification, ledger, history.
- A comment is a task, not a passive note.
- "Fixed" requires accepted diff, closed comment task, and ledger/history evidence.
- "Agent connected" must not be faked.
- "Project imported" must show real pages/components/assets registry.
- "AI changed design" must show proposal -> preview/diff -> approval -> transaction.
- Empty states must explain the cause and next action.

## UI Surfaces To Design Well

- Project open/import screen.
- Design search report.
- Project map sidebar.
- Pages/components/assets registry.
- Canvas viewport and selection overlay.
- Layer/object inspector.
- Context menu and comment composer.
- Comment/task queue.
- Review cockpit with awaiting-you, approvals, open, and resolved counts.
- Agent status and proposal panel.
- Preview/diff/verification panel.
- Action ledger and history/recovery.
- Export/share surface.
- Settings, privacy, local daemon/MCP connection states.
- Permission/scope grant and agent-session orientation states.

## Visual Direction

ForgeStudio should feel like a serious creative engineering tool:

- quiet, precise, dense, and readable;
- dark/light capable, but not generic dark-blue SaaS;
- strong selection states and focus rings;
- stable side panels and toolbars;
- restrained motion for continuity;
- no fake proof, fake dashboards, fake agent states, or decorative AI gradients by default.
