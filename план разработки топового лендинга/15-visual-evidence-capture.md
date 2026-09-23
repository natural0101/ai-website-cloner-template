# Visual Evidence Capture

Use this protocol whenever a plan, implementation, or final QA mentions screenshots.

## Required Screenshot Set

Minimum:

- current desktop;
- current mobile;
- current hero crop;
- final desktop;
- final mobile;
- final hero crop.

When relevant:

- interaction state;
- open menu;
- accordion/tab state;
- form error state;
- reduced-motion fallback;
- WebGL/3D fallback;
- animation keyframe capture.

## Capture Options

### Existing Browser Tooling

Use the in-app browser, Playwright, Chrome DevTools, or project test tooling when available.

### Playwright Optional Path

Official docs:

- screenshots: https://playwright.dev/docs/screenshots
- visual comparisons: https://playwright.dev/docs/test-snapshots

Use Playwright only if the project already has it or the user approves adding it.

### Visual Regression Services

Use only when the project already uses them or the user asks:

- Percy: https://www.browserstack.com/docs/percy
- Chromatic: https://www.chromatic.com/docs/

## File Naming

Use:

```text
evidence/screenshots/<phase>-<viewport>-<section>-<short-note>.png
```

Examples:

```text
evidence/screenshots/current-desktop-hero.png
evidence/screenshots/final-mobile-hero.png
evidence/screenshots/final-desktop-faq-open.png
```

## Register Screenshots

After capturing, register each file:

```bash
node scripts/register-screenshot-evidence.mjs <project-slug> --id shot-001 --path evidence/screenshots/current-desktop-hero.png --source current --viewport desktop --purpose "Current hero baseline" --section "Hero"
```

For final QA:

```bash
node scripts/register-screenshot-evidence.mjs <project-slug> --id shot-final-001 --path evidence/screenshots/final-desktop-home.png --source final --viewport desktop --purpose "Final desktop review" --section "Full page"
```

## Review Checklist

For every screenshot, inspect:

- text clipping;
- overlap;
- CTA visibility;
- mobile wrapping;
- asset crop;
- sticky/fixed element collisions;
- section rhythm;
- animation state readability;
- blank or broken media;
- unexpected scrollbars.

## Evidence Rule

If a QA claim says "looks good on mobile" or "hero fits the viewport", there must be a screenshot path in `evidence/screenshot-manifest.md`.

