---
name: landing-evidence-pack
description: Build and maintain evidence folders for landing-page redesign plans, including screenshots, reference manifests, asset manifests, decision logs, source URLs, and verification notes. Use when preparing a plan from a dossier, auditing visual quality, collecting references, or proving why a landing design decision is justified.
---

# Landing Evidence Pack

Use this skill whenever a landing plan needs proof instead of vague taste claims.

## Folder

Each project plan should include:

```text
evidence/
  README.md
  reference-manifest.md
  screenshot-manifest.md
  asset-manifest.md
  decision-log.md
  screenshots/
  references/
  assets/
  notes/
```

The `_template` folder already contains this structure.

## Workflow

1. Capture current-state evidence.
   - Desktop screenshot.
   - Mobile screenshot.
   - Hero crop.
   - Current URL or local route.

2. Capture reference evidence.
   - Add every source URL to `reference-manifest.md`.
   - Classify each source: direct, visual, motion, component, UX, CRO.
   - Write what to borrow and what not to copy.

3. Capture asset evidence.
   - List every image, video, GLB, logo, screenshot, icon, or generated asset in `asset-manifest.md`.
   - Record source, license/status, section usage, performance note, and alt text.

4. Capture decision evidence.
   - Use `decision-log.md` for major visual, motion, dependency, and copy decisions.
   - Include rejected alternatives, not just chosen ideas.

5. Keep plan files connected.
   - `03-reference-board.md` should point to reference IDs.
   - `04-visual-benchmark.md` should point to screenshot IDs.
   - `08-component-and-asset-plan.md` should point to asset IDs.

## Evidence Standards

- No reference without URL.
- No screenshot claim without screenshot path or explicit reason it is unavailable.
- No generated asset without prompt/spec.
- No dependency without decision-log entry.
- No motion direction without purpose and reduced-motion note.

## Output

When using this skill, update the relevant manifests and mention which evidence IDs support the plan.

