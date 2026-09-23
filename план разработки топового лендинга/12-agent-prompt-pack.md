# Agent Prompt Pack

These prompts are for moving work between agents without losing intent.

## Prompt A: Source Project Dossier

Use `01-universal-prompt-source-project.md` in the source project. If available, use `landing-source-forensics` before writing the dossier.

Expected output: `landing-source-dossier.md`.

Then validate with:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

## Prompt B: Planning In This Project

Use `02-upgrade-planner-prompt-this-project.md` in this project.

Expected output: a project folder under:

```text
план разработки топового лендинга/projects/<project-slug>/
```

## Prompt C: Implementation Agent

Use this after the project plan and evidence pack are filled.

```text
You are implementing a landing-page upgrade from an approved plan.

Before editing:
- Read the entire project plan folder.
- Read `landing-source-dossier.md` if present.
- Read `evidence/reference-manifest.md`, `evidence/screenshot-manifest.md`, `evidence/asset-manifest.md`, and `evidence/decision-log.md`.
- Read `14-animate-ui-selection.md` if Animate UI is used or considered.
- Read `29-motion-primitives-selection.md` if Motion Primitives is used or considered.
- Read `30-magic-ui-selection.md` if Magic UI is used or considered.
- Read `31-aceternity-ui-selection.md` if Aceternity UI is used or considered.
- Read `32-tailark-section-selection.md` if Tailark is used or considered.
- Read `33-shadcnblocks-selection.md` if shadcnblocks is used or considered.
- Read `34-micro-component-selection.md` if Kibo UI, Origin/Coss UI or a similar micro-component source is used or considered.
- Read `35-react-bits-selection.md` if React Bits is used or considered.
- Read `36-pacekit-gsap-selection.md` if PaceKit GSAP is used or considered.
- Read `37-cult-ui-selection.md` if Cult UI is used or considered.
- Read `38-reui-selection.md` if ReUI is used or considered.
- Read `39-twenty-first-dev-selection.md` if 21st.dev is used or considered.
- Read `40-kokonut-ui-selection.md` if Kokonut UI is used or considered.
- Read `41-mvpblocks-selection.md` if MVPBlocks is used or considered.
- Read `42-smoothui-selection.md` if SmoothUI is used or considered.
- Read `43-hextaui-selection.md` if HextaUI is used or considered.
- Read `44-skiper-ui-selection.md` if Skiper UI is used or considered.
- Read `45-eldora-ui-selection.md` if Eldora UI is used or considered.
- Read `46-blocks-so-selection.md` if Blocks.so is used or considered.
- Read `47-intent-ui-selection.md` if Intent UI is used or considered.
- Read `25-brand-dna-map.md` before changing colors, typography, assets, copy, routes, nav labels, form fields, legal copy, SEO copy or product proof.
- Read `52-reference-gallery-source-map.md` before treating external gallery, flow, motion or CRO sources as implementation authority.
- Read `24-thematic-reference-map.md` before using references as design authority.
- Read `15-reference-scorecard.md` before using any reference as design authority.
- Read `22-inspiration-synthesis.md` before translating references into layout, motion or assets.
- Read `26-motion-reference-map.md` before implementing animation or importing animation libraries.
- Read `53-motion-safety-source-map.md` before implementing animation, scroll choreography, WebGL/3D or animated component libraries.
- Read `16-motion-recipe-selection.md` before implementing animation.
- Read `17-visual-style-tile.md` before writing visual CSS, tokens, or section layouts.
- Read `18-section-storyboard-canvas.md` before editing section components.
- Read `19-asset-production-queue.md` before adding images, video, icons, screenshots, 3D, GLB, or WebGL.
- Read `27-responsive-viewport-map.md` before implementing layout, hero, nav, assets, sticky behavior, responsive grids, pricing, forms, or mobile motion.
- Read `20-implementation-task-graph.md` before choosing implementation order.
- Read `28-change-traceability-matrix.md` before editing. Every major change should have a `chg-###` ID, task ID and QA method.
- Read `21-plan-self-review.md` before editing. Do not implement unresolved blocker findings.
- Read `23-presentation-quality-review.md` after screenshots exist and before calling the page presentation-ready.
- Read the project AGENTS.md and framework rules.
- Check package.json before importing any library.

Implementation rules:
- Preserve route slugs, primary nav labels, form field names, analytics-sensitive labels, legal copy, and SEO-critical content unless the plan explicitly allows changes.
- Implement in task graph order: preserve current contract, foundation tokens and shell, section structure, assets, motion, responsive and quality, final handoff.
- Do not start a task if `20-implementation-task-graph.md` says it is blocked.
- Do not implement a plan if `21-plan-self-review.md` says implementation handoff is not allowed.
- For each section, follow the planned visible result, asset IDs, reference IDs, motion purpose, reduced-motion fallback, and QA check.
- Do not implement motion unless it has a motion safety verdict and the verdict is not `reject`.
- Do not add a library unless the plan names it and the dependency impact is accepted.
- Do not overwrite preserved or protected Brand DNA decisions from `25-brand-dna-map.md`.
- Do not install Animate UI items unless `14-animate-ui-selection.md` names the exact registry item and reduced-motion fallback.
- Do not install Motion Primitives items unless `29-motion-primitives-selection.md` names the exact item, install command, dependency impact, reduced-motion fallback and mobile behavior.
- Do not install Magic UI items unless `30-magic-ui-selection.md` names the exact item, install command, dependency impact, reduced-motion fallback, mobile behavior and QA.
- Do not install Aceternity UI items unless `31-aceternity-ui-selection.md` names the exact item, type, install command or reference-only status, license/access note, dependency impact, adaptation, reduced-motion fallback and mobile behavior.
- Do not install, copy or adapt Tailark items unless `32-tailark-section-selection.md` names the exact item/block/page, kit/source, live source URL, preview URL, registry URL, install command or reference-only status, access/license note, dependency impact, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt shadcnblocks items unless `33-shadcnblocks-selection.md` names the exact block/component/page/template, source type, access, live source URL, registry URL, install command or reference-only status, license/access note, dependency impact, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt Kibo UI, Origin/Coss UI or similar micro-components unless `34-micro-component-selection.md` names the exact source/item, registry or copy URL, install/copy method, license/access note, dependency impact, adaptation, reduced-motion fallback, mobile behavior, keyboard/focus QA, task ID and change ID.
- Do not install, copy or adapt React Bits items unless `35-react-bits-selection.md` names the exact item, category, `TS-TW` variant, source URL, registry URL, install command, license/access note, dependency impact, heavy-runtime gate, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt PaceKit GSAP items unless `36-pacekit-gsap-selection.md` names the exact item, source URL, registry URL, install command, `gsap`/`@gsap/react` dependency impact, registry dependencies, GSAP runtime gate, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt Cult UI items unless `37-cult-ui-selection.md` names the exact item, source URL, registry URL, install command, dependency impact, registry dependencies, style/runtime gate, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt ReUI items unless `38-reui-selection.md` names the exact item, style, source URL, registry URL, install command, free/pro access, license key status, dependency impact, registry dependencies, adaptation, mobile behavior, keyboard/focus QA, task ID and change ID.
- Do not install, copy or adapt 21st.dev items unless `39-twenty-first-dev-selection.md` names the exact component page, author/item, command, CDN registry URL or reference-only status, license, dependency impact, adaptation, fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt Kokonut UI items unless `40-kokonut-ui-selection.md` names the exact docs page, registry item, registry URL, install command, MIT/pro access, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt MVPBlocks items unless `41-mvpblocks-selection.md` names the exact docs page, exact item, endpoint URL, CLI or exact URL command, BSD-3-Clause/MIT license caveat, dependencies, registry dependencies, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy or adapt SmoothUI items unless `42-smoothui-selection.md` names the exact docs or preview page, exact item, endpoint URL, command, MIT license, dependencies, registry dependencies, API/registry evidence, adaptation, reduced-motion fallback, mobile behavior, task ID and change ID. Never use `/api/v1/blocks` as block evidence.
- Do not install, copy or adapt HextaUI items unless `43-hextaui-selection.md` names the exact item, source URL, endpoint URL, command, MIT license, dependencies, registry dependencies, HTML-doc caveat, demo-data replacement, mobile behavior, task ID and change ID.
- Do not install, copy, reference or adapt Skiper UI items unless `44-skiper-ui-selection.md` names the exact item, source URL, endpoint URL, command, terms/access status, dependencies, registry dependencies, premium/private material avoided, reduced-motion fallback, mobile behavior, task ID and change ID.
- Do not install, copy, reference or adapt Eldora UI items unless `45-eldora-ui-selection.md` names the exact item, item type, source URL, endpoint URL, command, MIT license, dependencies, registry dependencies, demo/example material avoided, reduced-motion fallback, mobile behavior, performance risk, task ID and change ID.
- Do not install, copy, reference or adapt Blocks.so items unless `46-blocks-so-selection.md` names the exact item, category, source page, endpoint URL, command, MIT license, duplicate-entry caveat, dependencies, registry dependencies, demo-data replacement, fake-proof handling, accessibility notes, mobile behavior, task ID and change ID.
- Do not install, copy, reference or adapt Intent UI items unless `47-intent-ui-selection.md` names the exact item, item type, source URL, endpoint URL, command, MIT license, React Aria dependency impact, dependencies, registry dependencies, example-page and `all` avoidance, demo-data replacement, accessibility notes, mobile behavior, task ID and change ID.
- Do not promote a reference unless `24-thematic-reference-map.md` gives a closeness reason and section use.
- Do not copy a visual or motion reference unless `15-reference-scorecard.md` maps it to that section and explains what not to copy.
- Do not borrow from a reference unless `22-inspiration-synthesis.md` states the concrete visible decision and do-not-copy boundary.
- Do not implement motion unless `26-motion-reference-map.md` accepts or adapts the motion reference with borrow/transform/do-not-copy, fallback, mobile and library impact.
- Do not implement motion unless the recipe, detailed storyboard, reduced-motion fallback, and QA check are written.
- Do not introduce colors, fonts, radii, shadows, icon styles, or surface treatments that conflict with `17-visual-style-tile.md`.
- Do not implement a section until its storyboard row states user job, frame sketch, asset, references, motion, mobile frame, and QA risk.
- Do not add visual assets unless the asset queue defines role, source, spec, path, alt text, performance and status.
- Do not implement desktop-only layout unless `27-responsive-viewport-map.md` names mobile, tablet and wide transformations plus screenshot QA.
- Do not implement orphan changes absent from `28-change-traceability-matrix.md`.
- Do not invent proof, metrics, testimonials, logos, reviews, or product claims.
- Keep motion purposeful and bounded.
- Use real assets or planned placeholders with exact specs.

Verification:
- Run typecheck/lint/build or the repository's closest available checks.
- Capture desktop and mobile screenshots if tooling is available.
- Register screenshots with `scripts/register-screenshot-evidence.mjs` when evidence files are available.
- Update the quality gate with evidence.
- Report changed files, verification results, and remaining risks.
```

## Prompt D: Visual QA Agent

```text
You are reviewing the implemented landing page for visual quality and plan compliance.

Read:
- the completed project plan;
- evidence manifests;
- screenshots or live URL;
- changed files if available.

Review for:
- offer and CTA clarity;
- first impression and above-the-fold clarity;
- visual hierarchy;
- typography, color, radius, spacing consistency;
- hero viewport fit;
- section rhythm and repetition;
- asset quality and crop;
- motion purpose and reduced-motion fallback;
- mobile layout;
- accessibility and performance risks;
- mismatch between plan and implementation.

Fill `23-presentation-quality-review.md` with screenshot/live evidence. Return findings ordered by severity with file/section references and concrete fixes.
```

## Prompt D2: Final QA Agent

```text
You are performing final QA before the landing page is called done.

Read:
- the completed project plan;
- `10-quality-gate.md`;
- `12-final-qa-report.md`;
- `23-presentation-quality-review.md`;
- `evidence/` manifests;
- `14-final-qa-and-launch-gate.md`.
- `15-visual-evidence-capture.md`.

Check:
- desktop and mobile screenshots;
- hero viewport fit;
- CTA visibility;
- visual hierarchy and section rhythm;
- copy, proof, and CTA intent;
- motion purpose and reduced-motion fallback;
- accessibility basics;
- performance risks;
- protected routes/nav/forms/legal/SEO preservation;
- mismatch between plan and implementation.

Fill `12-final-qa-report.md` with commands, screenshots, verdict, and remaining risks.
Do not mark presentation-ready without evidence and a non-blocked `23-presentation-quality-review.md`.
```

## Prompt E: Asset Production Agent

```text
You are producing missing visual assets for a landing page plan.

Read:
- `08-component-and-asset-plan.md`;
- `evidence/asset-manifest.md`;
- visual direction;
- section plan.

For each missing asset:
- define type, aspect ratio, composition, style, prompt, negative prompt, mobile crop, alt text, and performance note;
- if 3D is required, state whether it should be GLB runtime, Blender render, or WebGL scene;
- update `evidence/asset-manifest.md`.

Do not generate decorative assets that do not support the section message.
```

## Prompt F: Final Handoff Summary

```text
Summarize this landing upgrade for the next agent or human reviewer.

Include:
- product and primary CTA;
- design read and dials;
- brand DNA preserve/evolve/remove/introduce/protect decisions;
- chosen references;
- thematic reference map decisions;
- reference scorecard decisions;
- motion reference map decisions;
- motion recipe decisions;
- visual style tile decisions;
- section storyboard canvas;
- asset production queue;
- responsive viewport map decisions;
- change traceability decisions;
- chosen section patterns;
- chosen Animate UI items and rejected tempting items;
- chosen Tailark items or rejected Tailark references;
- chosen shadcnblocks items or rejected shadcnblocks references;
- chosen micro-components or rejected micro-component references;
- chosen React Bits items or rejected React Bits references;
- chosen PaceKit GSAP items or rejected PaceKit GSAP references;
- chosen Cult UI items or rejected Cult UI references;
- chosen ReUI items or rejected ReUI references;
- chosen 21st.dev items or rejected 21st.dev references;
- chosen Kokonut UI items or rejected Kokonut UI references;
- chosen MVPBlocks items or rejected MVPBlocks references;
- chosen SmoothUI items or rejected SmoothUI references;
- chosen HextaUI items or rejected HextaUI references;
- chosen Skiper UI items or rejected Skiper UI references;
- chosen Eldora UI items or rejected Eldora UI references;
- chosen Blocks.so items or rejected Blocks.so references;
- chosen Intent UI items or rejected Intent UI references;
- implementation task graph;
- plan self-review verdict;
- presentation quality review verdict;
- section-by-section changes;
- animation storyboard summary;
- assets and dependencies;
- commands run;
- evidence links;
- risks still open.
```
