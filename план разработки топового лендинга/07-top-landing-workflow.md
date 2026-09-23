# Top Landing Workflow

This is the end-to-end loop for turning a simple landing page into a stronger one.

## Phase 1: Source Project Dossier

Run `01-universal-prompt-source-project.md` in the other project.

Output: `landing-source-dossier.md`.

Use `24-source-dossier-forensics.md` or `landing-source-forensics` if available, so the dossier includes screenshots, files, visual tokens, assets, commands and risks.

Do not start redesigning until the dossier exists or equivalent facts are gathered.

Check the dossier shape:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

## Phase 2: Intake In This Project

Bring the dossier here.

Create manually or run:

```bash
node scripts/create-landing-plan.mjs <project-slug> --dossier path/to/landing-source-dossier.md
```

Start with:

- `01-current-state-audit.md`
- `02-copy-and-offer-audit.md`
- `03-reference-board.md`
- `evidence/`

Use:

- `landing-dossier-schema`
- `landing-copy-offer-audit`
- `landing-proof-integrity-gate`
- `landing-evidence-pack`
- `landing-brand-dna-preservation`
- `landing-reference-source-catalog`
- `landing-reference-research`
- `landing-reference-scoring`
- `landing-visual-benchmark`

## Phase 3: Direction

Define:

- Design Read.
- Redesign mode.
- Brand DNA preserve/evolve/remove/introduce/protect decisions.
- Dials.
- Visual system.
- Offer and CTA.
- Section order.

Use:

- `design-taste-frontend`
- `landing-visual-direction`
- `landing-brand-dna-preservation`
- `landing-page-high-conversion`
- `layers-*`

## Phase 4: Storyboard

Create:

- `06-section-by-section-upgrade-plan.md`
- `07-animation-storyboard.md`
- `08-component-and-asset-plan.md`
- `13-section-pattern-selection.md`
- `14-animate-ui-selection.md` when Animate UI is considered
- `29-motion-primitives-selection.md` when Motion Primitives is considered
- `30-magic-ui-selection.md` when Magic UI is considered
- `31-aceternity-ui-selection.md` when Aceternity UI is considered
- `32-tailark-section-selection.md` when Tailark is considered
- `33-shadcnblocks-selection.md` when shadcnblocks is considered
- `34-micro-component-selection.md` when Kibo UI, Origin/Coss UI, or another micro-component source is considered
- `35-react-bits-selection.md` when React Bits is considered
- `36-pacekit-gsap-selection.md` when PaceKit GSAP is considered
- `37-cult-ui-selection.md` when Cult UI is considered
- `38-reui-selection.md` when ReUI is considered
- `39-twenty-first-dev-selection.md` when 21st.dev is considered
- `40-kokonut-ui-selection.md` when Kokonut UI is considered
- `41-mvpblocks-selection.md` when MVPBlocks is considered
- `42-smoothui-selection.md` when SmoothUI is considered
- `43-hextaui-selection.md` when HextaUI is considered
- `44-skiper-ui-selection.md` when Skiper UI is considered
- `45-eldora-ui-selection.md` when Eldora UI is considered
- `46-blocks-so-selection.md` when Blocks.so is considered
- `47-intent-ui-selection.md` when Intent UI is considered
- `24-thematic-reference-map.md`
- `15-reference-scorecard.md`
- `22-inspiration-synthesis.md`
- `26-motion-reference-map.md`
- `16-motion-recipe-selection.md`
- `17-visual-style-tile.md`
- `25-brand-dna-map.md`
- `18-section-storyboard-canvas.md`
- `19-asset-production-queue.md`
- `27-responsive-viewport-map.md`
- `28-change-traceability-matrix.md`

Use:

- `landing-motion-storyboard`
- `landing-section-patterns`
- `landing-asset-art-direction`
- `landing-motion-recipes`
- `landing-visual-direction`
- `landing-section-storyboard`
- `landing-asset-production`
- `landing-responsive-viewport-storyboard`
- `landing-change-traceability`
- `landing-reference-source-catalog`
- `landing-reference-scoring`
- `landing-thematic-reference-mining`
- `landing-inspiration-synthesis`
- `landing-motion-reference-mining`
- `landing-motion-safety-gate`
- `motion-component-source-map`
- `animate-ui-catalog`
- `motion-primitives-catalog`
- `magic-ui-catalog`
- `aceternity-ui-catalog`
- `tailark-section-catalog`
- `shadcnblocks-catalog`
- `micro-component-source-catalog`
- `kibo-ui-catalog`
- `react-bits-catalog`
- `pacekit-gsap-catalog`
- `cult-ui-catalog`
- `reui-catalog`
- `twenty-first-dev-catalog`
- `kokonut-ui-catalog`
- `mvpblocks-catalog`
- `smoothui-catalog`
- `hextaui-catalog`
- `skiper-ui-catalog`
- `eldora-ui-catalog`
- `blocks-so-catalog`
- `intent-ui-catalog`
- `17-animate-ui-full-site-map.md`
- `33-motion-primitives-source-map.md`
- `34-magic-ui-source-map.md`
- `35-aceternity-ui-source-map.md`
- `36-tailark-section-source-map.md`
- `37-shadcnblocks-source-map.md`
- `38-micro-component-source-map.md`
- `39-react-bits-source-map.md`
- `40-pacekit-gsap-source-map.md`
- `41-cult-ui-source-map.md`
- `42-reui-source-map.md`
- `43-21st-dev-source-map.md`
- `44-kokonut-ui-source-map.md`
- `45-mvpblocks-source-map.md`
- `46-smoothui-source-map.md`
- `47-hextaui-source-map.md`
- `48-skiper-ui-source-map.md`
- `49-eldora-ui-source-map.md`
- `50-blocks-so-source-map.md`
- `51-intent-ui-source-map.md`
- `52-reference-gallery-source-map.md`
- `54-proof-integrity-source-map.md`
- `28-thematic-reference-mining.md`
- `18-reference-scoring-matrix.md`
- `26-inspiration-synthesis.md`
- `30-motion-reference-mining.md`
- `53-motion-safety-source-map.md`
- `19-motion-recipe-library.md`
- `20-visual-direction-style-tiles.md`
- `29-brand-dna-preservation.md`
- `21-section-storyboard-canvas.md`
- `22-asset-production-queue.md`
- `31-responsive-viewport-storyboard.md`
- `32-change-traceability-matrix.md`

## Phase 5: Implementation Plan

Create:

- `09-implementation-tasks.md`
- `10-quality-gate.md`
- `11-implementation-handoff-prompt.md`
- `20-implementation-task-graph.md`
- `21-plan-self-review.md`

Each task must include:

- files;
- visible result;
- dependencies;
- risks;
- verification.

Implementation must be ordered by build rings:

- preserve current contract;
- foundation tokens and shell;
- section structure;
- assets;
- motion;
- responsive and quality;
- final handoff.

Use:

- `landing-implementation-task-graph`
- `landing-plan-self-review`
- `landing-implementation-handoff`
- `23-implementation-task-graph.md`
- `25-plan-self-review.md`

## Phase 6: Build And Review

When implementing:

- work section by section;
- verify desktop and mobile;
- take screenshots;
- audit copy;
- audit motion;
- check performance and accessibility;
- fix before moving on.

Run the minimum plan check before implementation:

```bash
node scripts/check-landing-plan.mjs <project-slug>
```

Use:

- `ui-audit`
- `details-that-make-interfaces-feel-better`
- browser/Playwright screenshots if available.

## Done Means

- The page has a clear offer and CTA.
- The visual direction is specific.
- Every section has a job.
- Every animation has a reason.
- Assets are planned or produced.
- Mobile works.
- No obvious AI template tells remain.
- Quality gate is filled with evidence.

Use `09-landing-type-routing-matrix.md` whenever the landing type is unclear or the selected sources feel generic.

Use `10-evidence-and-cro-sources.md` when a design decision needs CRO, UX, product psychology, or heuristic support.

Use `11-component-source-registry.md` before installing/copying any component source.

Use `12-agent-prompt-pack.md` to hand the plan to implementation, visual QA, or asset-production agents.

## Phase 7: Final QA

After implementation:

- fill `23-presentation-quality-review.md`;
- fill `12-final-qa-report.md`;
- use `14-final-qa-and-launch-gate.md`;
- use `27-presentation-quality-review.md`;
- capture desktop/mobile screenshots;
- register screenshots with `scripts/register-screenshot-evidence.mjs`;
- record commands run and remaining risks;
- do not call the page done until the final QA report has evidence.

Use:

- `landing-final-qa`
- `landing-presentation-review`
- `landing-visual-evidence-capture`
- `ui-audit`
- browser/Playwright screenshots if available.
