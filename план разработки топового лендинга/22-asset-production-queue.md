# Asset Production Queue

Дата обновления: 2026-07-03.

Asset queue превращает visual/storyboard decisions в исполнимые ассеты: screenshots, generated images, diagrams, logos, icons, video, 3D renders, GLB/WebGL scenes. Она нужна до implementation, чтобы герой и секции не строились на пустых cards, fake screenshots, gradients or vague placeholders.

For proof-like assets, read `54-proof-integrity-source-map.md` and assign a claim verdict before implementation.

## Sources

- https://nextjs.org/docs/app/api-reference/components/image
- https://web.dev/learn/images/
- https://web.dev/articles/optimize-lcp
- https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/alt
- https://accessibility.huit.harvard.edu/describe-content-images
- https://web.dev/articles/lazy-loading-video
- https://modelviewer.dev/
- https://threejs.org/docs/#examples/en/loaders/GLTFLoader
- `54-proof-integrity-source-map.md`

## Asset Roles

| Role | Use | Good asset |
| --- | --- | --- |
| Proof | Make claim believable | real product screenshot, customer logo, metric visual, case image |
| Explanation | Make workflow clear | diagram, step screenshot, annotated UI, product flow |
| Emotion | Make product desirable | photography, generated lifestyle image, product render |
| Memory | Make brand memorable | 3D object, mascot, distinctive hero visual |
| Navigation | Help scan | icon system, category marks, visual labels |
| Motion | Support animation | video, sprite, GLB, WebGL object, image sequence |

## Queue Fields

| Field | What to write |
| --- | --- |
| ID | `asset-001`, `asset-002`, etc. |
| Section | Hero, proof, features, pricing, FAQ, CTA |
| Role | proof, explanation, emotion, memory, navigation, motion |
| Type | screenshot, generated image, photo, diagram, icon, logo, video, GLB, Blender render, WebGL |
| Source | existing, capture, generate, download, Blender, Three.js, manual SVG |
| Spec | aspect ratio, pixel size, crop, subject, composition |
| Style constraints | lighting, material, color, typography, background, do-not-show |
| Prompt | generation/capture/Blender prompt or capture instruction |
| Negative prompt | what to avoid |
| File path | planned final path |
| Mobile crop | how it changes below 768px |
| Alt text | meaningful text or empty alt if decorative |
| Performance | priority/lazy, dimensions, poster, compression, fallback |
| Status | planned, in progress, produced, reviewed, rejected |
| QA | screenshot/render/overlay/visual check |
| Claim verdict | verified, needs-evidence, rephrase, visual-only or reject when the asset implies proof |

## Asset Rules

- Hero needs a real visual strategy: product screenshot, product object, generated image, diagram, video, 3D, or explicit "no visual because..." rationale.
- Product proof should be real. Do not invent dashboards, metrics, customers, testimonials, logos, or screenshots.
- Generated or mock product UI must be labeled as sample/concept or treated as visual-only, not proof.
- Generated images must support the section message, not decorate around weak copy.
- Diagrams must explain a real workflow or decision.
- Icons need one family and consistent stroke/fill.
- Videos need poster, dimensions, lazy strategy and fallback.
- GLB/WebGL needs static fallback, mobile plan, reduced-motion plan and render check.
- All images need stable dimensions and crop plan.
- Alt text must describe meaningful content. Decorative images should use empty alt in implementation.

## Prompt Pattern

Use this structure for generated or Blender assets:

```text
Purpose:
Section:
Subject:
Composition:
Aspect ratio:
Visual style:
Material/lighting:
Color constraints:
Text in image:
Do not include:
Mobile crop:
Alt text:
Performance target:
```

## Performance Notes

- Above-fold hero images need explicit size, priority/preload decision and no layout shift.
- Below-fold images should be lazy-loaded.
- Use responsive sizes and stable aspect ratios.
- Compress photographic assets to WebP/AVIF when supported by the project.
- Avoid huge transparent PNGs for hero objects.
- Do not autoplay heavy video without a clear reason.
- Runtime 3D should be central to the story, not a decorative burden.

## Output

Fill `projects/<slug>/19-asset-production-queue.md`, then mirror produced assets into:

- `08-component-and-asset-plan.md`
- `18-section-storyboard-canvas.md`
- `evidence/asset-manifest.md`
- `evidence/decision-log.md`
- `10-quality-gate.md`
