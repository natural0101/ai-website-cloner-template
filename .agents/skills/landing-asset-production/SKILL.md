---
name: landing-asset-production
description: Turn landing-page asset ideas into a concrete production queue with specs, prompts, capture instructions, file paths, mobile crops, alt text, performance plans, status, and QA. Use when a landing plan needs hero visuals, product screenshots, generated images, diagrams, icons, logos, video, Blender renders, GLB/WebGL scenes, or when assets in a storyboard/component plan must become implementable files.
---

# Landing Asset Production

Use this skill after section storyboard and asset art direction, before implementation.

## Required Files

Read:

```text
план разработки топового лендинга/22-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/08-component-and-asset-plan.md
план разработки топового лендинга/projects/<slug>/18-section-storyboard-canvas.md
план разработки топового лендинга/projects/<slug>/17-visual-style-tile.md
```

Fill or update:

```text
план разработки топового лендинга/projects/<slug>/19-asset-production-queue.md
план разработки топового лендинга/projects/<slug>/evidence/asset-manifest.md
план разработки топового лендинга/projects/<slug>/evidence/decision-log.md
план разработки топового лендинга/projects/<slug>/10-quality-gate.md
```

## Workflow

1. Extract every asset implied by the storyboard.
2. Assign role: proof, explanation, emotion, memory, navigation, or motion.
3. Assign type and source: screenshot, generated image, photo, diagram, icon, logo, video, GLB, Blender render, WebGL, existing asset.
4. Write exact specs: aspect ratio, size, crop, subject, composition, style constraints.
5. Write prompt or capture instruction.
6. Write planned path, mobile crop, alt text, performance plan, status and QA.
7. Mirror produced or planned assets into `evidence/asset-manifest.md`.

## Rules

- Do not invent product screenshots, customer logos, metrics, testimonials, reviews, or certifications.
- Use real screenshots when product UI is the proof.
- Use generated imagery only when it supports the section message.
- Use 3D/WebGL only when it is central to the hero/story.
- Give video a poster, dimensions, lazy strategy and fallback.
- Give every meaningful image alt text.
- Use empty alt only for decorative images in implementation notes.
- Reserve stable dimensions for every image/video/3D container.
- Plan mobile crop before implementation.

## Output Standard

Every asset row must make implementation unambiguous:

- section and role;
- asset type and source;
- visual spec and prompt/capture instruction;
- final path;
- mobile crop;
- alt text;
- performance plan;
- status and QA check.
