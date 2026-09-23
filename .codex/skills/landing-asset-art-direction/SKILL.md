---
name: landing-asset-art-direction
description: Plan landing-page visual assets including hero imagery, product screenshots, generated images, video, icons, logos, 3D models, Blender assets, and WebGL scenes. Use when a landing page needs stronger visuals, a hero object, section imagery, product proof, or asset specs for implementation.
---

# Landing Asset Art Direction

Use this skill when the page needs concrete visual assets. A landing page should not rely on text, gradients, and empty cards when the product needs to feel real.

## Inputs

- Product category and audience.
- Existing assets from `public/`, design files, screenshots, or Blender workbench.
- Reference board.
- Visual direction and section plan if available.

## Asset Decision Tree

1. If the product UI is the proof, use a real screenshot or live component preview.
2. If the product is physical or emotional, use photography or generated product/lifestyle imagery.
3. If the concept is abstract but central, use 3D/WebGL or a Blender asset.
4. If the section is operational, use diagrams, icon systems, or real interface fragments.
5. If no strong asset can be produced now, write a placeholder spec with exact size, composition, and prompt.

## Required Asset Plan

For every major section:

- Asset type: photo, generated image, screenshot, video, 3D, WebGL, icon, logo, diagram.
- Purpose: proof, emotion, explanation, hierarchy, delight.
- Composition: aspect ratio, crop, subject, background, negative space.
- Style: material, lighting, color, typography if present.
- Source: existing, generated, downloaded, Blender, Three.js, SVG/logo.
- Implementation: file path or component plan.
- Performance: size, lazy load, priority, poster, fallback.
- Mobile crop:
- Accessibility alt text:

## 3D And Blender Rules

- Use 3D only when it carries product meaning or brand memory.
- Keep hero 3D visually readable at mobile sizes.
- Export GLB when the web page needs runtime 3D.
- Export PNG/WebP render when the object is decorative and does not need interaction.
- Use reduced-motion fallback for rotating or scroll-linked 3D.
- Run a render/screenshot check before calling it finished.

## Output

Create or update `06-component-and-asset-plan.md` or an asset section with:

- Asset inventory.
- New asset specs.
- Generation prompts if needed.
- Blender/WebGL notes if needed.
- File naming plan.
- QA checks.

## Quality Gate

- Hero has a real visual strategy.
- Every repeated section has visual variation.
- Assets have stable dimensions.
- Heavy assets are optimized or lazy-loaded.
- Alt text is planned.
- Visuals support the message instead of decorating around it.

