---
name: landing-implementation-handoff
description: Turn a completed landing-page plan and evidence pack into a precise implementation prompt for another agent, including protected constraints, section order, asset IDs, motion specs, dependency limits, verification commands, and final QA requirements.
---

# Landing Implementation Handoff

Use this skill after the planning folder has enough evidence and before another agent starts code changes.

## Inputs

- Project plan folder under `план разработки топового лендинга/projects/<project-slug>/`.
- `landing-source-dossier.md` if present.
- Evidence manifests.
- Repository AGENTS.md and package.json.

## Workflow

1. Confirm the plan is ready.
   - Run `node scripts/check-landing-plan.mjs <project-slug>`.
   - Inspect warnings manually.
   - Do not hand off a plan with failed checks unless the prompt explicitly says what is missing.

2. Extract implementation constraints.
   - Protected routes, nav labels, form fields, analytics labels, legal copy, SEO-critical content.
   - Approved dependencies and components.
   - Asset IDs and missing assets.
   - Motion specs and reduced-motion fallback.

3. Create the implementation prompt.
   - Use `план разработки топового лендинга/12-agent-prompt-pack.md`.
   - Prefer Prompt C for implementation.
   - Include absolute path to the plan folder.
   - Include commands to run.

4. Create QA follow-up prompt.
   - Use Prompt D for visual QA.
   - Include expected screenshots and quality gate update.

## Output

Write or update:

- `11-implementation-handoff-prompt.md` inside the project plan folder.

## Quality Bar

The handoff prompt must be specific enough that a fresh agent can implement without asking:

- what to preserve;
- what to change first;
- where each asset comes from;
- which references inspired each section;
- which animation library and fallback to use;
- how to verify the result.

