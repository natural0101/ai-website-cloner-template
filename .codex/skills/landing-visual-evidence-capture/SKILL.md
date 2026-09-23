---
name: landing-visual-evidence-capture
description: Capture, name, register, and review screenshot evidence for landing-page planning, implementation QA, visual benchmark, mobile checks, hero crops, interaction states, and final launch review. Use when a landing plan or QA needs desktop/mobile screenshots, evidence manifests, or visual regression guidance.
---

# Landing Visual Evidence Capture

Use this skill when a plan, review, or final QA depends on screenshots.

## Required Reading

Read:

- `план разработки топового лендинга/15-visual-evidence-capture.md`
- project `evidence/screenshot-manifest.md`

## Workflow

1. Decide the screenshot set.
   - Current desktop/mobile/hero crop.
   - Final desktop/mobile/hero crop.
   - Interaction states if relevant.

2. Capture screenshots with available tooling.
   - In-app browser or Chrome DevTools.
   - Playwright only if already installed or approved.
   - Percy/Chromatic only if already used or requested.

3. Save files under:

```text
evidence/screenshots/
```

4. Register each screenshot:

```bash
node scripts/register-screenshot-evidence.mjs <project-slug> --id shot-001 --path evidence/screenshots/current-desktop-hero.png --source current --viewport desktop --purpose "Current hero baseline" --section "Hero"
```

5. Use screenshot IDs in:
   - `04-visual-benchmark.md`
   - `10-quality-gate.md`
   - `12-final-qa-report.md`

## Review Focus

- Text clipping.
- Overlap.
- CTA visibility.
- Mobile wrapping.
- Asset crop.
- Blank media.
- Sticky/fixed collisions.
- Animation state readability.

## Rule

Do not claim desktop/mobile/hero quality without screenshot evidence.

