---
name: landing-source-forensics
description: Inspect an existing landing page in a source project and produce an evidence-rich `landing-source-dossier.md` before any redesign work. Use when preparing a simple landing for handoff into the top-landing planning folder, especially when routes, files, screenshots, visual tokens, assets, commands, protected behavior, accessibility, motion, performance risks, or technical constraints must be captured accurately.
---

# Landing Source Forensics

Use this skill in the source project before planning or redesigning.

## Required References

If available, read:

```text
план разработки топового лендинга/13-source-dossier-schema.md
план разработки топового лендинга/24-source-dossier-forensics.md
план разработки топового лендинга/01-universal-prompt-source-project.md
```

If those files are not present in the source project, still follow the same dossier shape and create `landing-source-dossier.md`.

## Workflow

1. Inspect project structure.
   - Read `package.json`, route files, page files, landing components, shared UI, global styles and public assets.
   - Use `rg --files` for file discovery.

2. Inspect current UI.
   - Start or use the dev server if safe and already supported by the project.
   - Capture or request desktop, mobile and hero screenshots when tooling is available.
   - If screenshots are unavailable, record preview URL and exact reason.

3. Capture baseline facts.
   - Product, audience, CTA, conversion goal, offer and constraints.
   - Sections, visible copy, layout, assets, proof and mobile behavior.
   - Typography, palette, spacing, radius, surfaces, imagery, motion and repeated patterns.

4. Capture preservation constraints.
   - Routes, slugs, anchors, nav labels, form fields, analytics labels, legal copy, SEO content and brand assets.
   - Never invent proof, metrics, customers, reviews, logos or certifications.

5. Capture evidence inventory.
   - Preview URL.
   - Screenshot paths or unavailable reasons.
   - Viewport sizes.
   - Source files inspected.
   - CSS/token evidence.
   - Asset paths inspected.
   - Commands run and result.
   - Console errors, hydration/runtime issues or unavailable reason.
   - Lighthouse report/path or unavailable reason.
   - Manual accessibility checks separate from automated checks.
   - Heuristic issues with severity and evidence.
   - Browser, Lighthouse or Playwright availability.
   - Unknowns.

6. Write `landing-source-dossier.md`.
   - Use the ten schema sections.
   - Link claims to files, screenshots, visible copy or command output.
   - Give important issues severity: cosmetic, minor, major or blocker.
   - Mark unknowns as `unknown`.

7. Validate if the checker is available.

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

## Output Quality

The dossier is ready only if a fresh planning agent can answer:

- what exists now;
- where it lives in code;
- what the current page looks like on desktop and mobile;
- what assets and tokens exist;
- what must not change;
- what risks can break implementation;
- which facts are missing and must be treated as assumptions.
