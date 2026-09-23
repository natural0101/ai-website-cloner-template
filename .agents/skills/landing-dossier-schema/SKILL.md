---
name: landing-dossier-schema
description: Create and validate source-project landing dossiers before planning a landing-page upgrade. Use when preparing `landing-source-dossier.md`, checking whether a dossier has the required sections, validating handoff quality, or converting a loose audit into the standard schema.
---

# Landing Dossier Schema

Use this skill in the source project or this project before planning.

## Required Reading

Read:

- `план разработки топового лендинга/13-source-dossier-schema.md`
- `план разработки топового лендинга/24-source-dossier-forensics.md`
- `план разработки топового лендинга/source-dossier-example.md` if an example is useful

## Workflow

1. Inspect the source project.
   - Routes, files, components, assets, package.json.
   - Copy, CTA, forms, analytics labels, SEO content.
   - Screenshots or live preview if available.
   - Desktop/mobile viewport evidence, visual tokens, commands, accessibility, motion and performance risks.
   - Console/runtime signals, heuristic issues, severity and manual accessibility notes where available.

2. Create `landing-source-dossier.md`.
   - Use all ten required schema sections.
   - Use real file paths and visible copy.
   - Fill `Evidence Inventory` with screenshot paths or unavailable reasons, viewport sizes, inspected files, commands and token evidence.
   - Mark unknowns as `unknown`.
   - Do not invent metrics, proof, customers, screenshots, or references.
   - Separate automated checks such as Lighthouse from manual accessibility and visual observations.

3. Validate.
   - In this project, run:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

4. Fix failures.
   - Missing required headings block planning.
   - Warnings can remain only if they are explained.

## Quality Bar

The dossier must let a fresh agent answer:

- what the product is;
- who it is for;
- what conversion means;
- what sections exist;
- what assets exist;
- what screenshots, tokens, files and commands support the audit;
- what must not change;
- what references are relevant;
- what technical constraints affect implementation.
