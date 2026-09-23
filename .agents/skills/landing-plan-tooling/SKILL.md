---
name: landing-plan-tooling
description: Create and validate project-specific folders inside "план разработки топового лендинга" using the local scripts and template. Use when starting a new landing upgrade plan from a dossier, cloning the _template folder, checking plan completeness, or preparing handoff files for implementation.
---

# Landing Plan Tooling

Use this skill when the user brings a `landing-source-dossier.md` from another project or asks to start/check a landing upgrade plan.

## Commands

Create a plan folder:

```bash
node scripts/create-landing-plan.mjs <project-slug>
```

Create a plan folder and copy a dossier into it:

```bash
node scripts/create-landing-plan.mjs <project-slug> --dossier path/to/landing-source-dossier.md
```

Check a plan folder:

```bash
node scripts/check-landing-plan.mjs <project-slug>
```

You can also pass an absolute or relative folder path to `check-landing-plan.mjs`.

## Workflow

1. Create the folder from `_template`.
2. Copy or place `landing-source-dossier.md` into the folder.
3. Fill files `01-current-state-audit.md` through `10-quality-gate.md`.
4. Run `check-landing-plan.mjs`.
5. Treat failures as blocking. Treat warnings as prompts to inspect empty fields or tables.

## Rules

- Do not overwrite an existing project plan folder.
- Do not mark a plan complete until the check passes and the quality gate has evidence.
- The checker is a minimum gate. Passing it does not replace visual review.
- If the plan uses heavy motion, WebGL, video, or 3D, add explicit performance and reduced-motion evidence manually.

