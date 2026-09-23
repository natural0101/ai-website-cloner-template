# Responsive Viewport Storyboard

Дата обновления: 2026-07-03.

Этот слой нужен перед implementation task graph. Он заставляет заранее описать, как лендинг выглядит в реальных viewport, а не только в абстрактной desktop-композиции.

## Проверенные источники

Все источники ниже проверены live-запросом 2026-07-03 and returned 200.

| Source | URL | Role |
| --- | --- | --- |
| web.dev Learn Responsive Design | https://web.dev/learn/design/ | Responsive design foundation and viewport thinking. |
| web.dev Media Queries | https://web.dev/learn/design/media-queries | Breakpoint and media query reference for responsive behavior. |
| web.dev Responsive Images | https://web.dev/learn/design/responsive-images | Image sizing, art direction and responsive asset selection. |
| MDN Responsive Design | https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design | Core responsive layout concepts and CSS techniques. |
| MDN Viewport Meta | https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Viewport_meta_element | Viewport meta behavior and mobile viewport basics. |
| Material Applying Layout | https://m3.material.io/foundations/layout/applying-layout | Adaptive layout and window size class thinking. |
| Material Scaffold Overview | https://m3.material.io/foundations/layout/scaffold/overview | Page structure and adaptive shell thinking. |
| Material Adaptive Design | https://m3.material.io/foundations/adaptive-design/overview | Current Material adaptive design entry point. |

## When To Use

Use for every landing-page plan before implementation. It is especially important when:

- hero has a large visual, 3D object, video, product screenshot or split layout;
- heading is long or CTA row has two actions;
- nav has many labels;
- sections use bento grids, cards, pricing tables, dashboards, galleries or diagrams;
- motion, sticky behavior, horizontal scroll, WebGL or carousel is planned;
- the page must look presentation-ready on mobile and wide desktop.

## Default Viewport Matrix

| ID | Size | Why it matters |
| --- | ---: | --- |
| `mobile-s` | 360 x 740 | catches cramped phones, long words, CTA wraps and hero height issues |
| `mobile` | 390 x 844 | common mobile proof viewport |
| `tablet` | 768 x 1024 | catches two-column to one-column transitions |
| `laptop` | 1440 x 900 | default desktop planning viewport |
| `wide` | 1920 x 1080 | catches stretched empty pages and weak wide composition |

Add custom viewports when analytics, app webview, iframe, kiosk, browser extension, or embedded product context demands it.

## Required Decisions

### First Viewport

For desktop, mobile and wide:

- visible brand/product/object/offer signal;
- headline line breaks;
- subhead line count;
- CTA position and wrap behavior;
- proof hint;
- hero visual crop;
- hint of the next section;
- nav height and behavior;
- what is allowed below the fold.

### Section Transformations

For each section:

- desktop composition;
- tablet composition;
- mobile composition;
- order changes;
- hidden, collapsed or replaced elements;
- sticky or scroll behavior changes;
- asset crop and aspect ratio;
- QA screenshot needed.

### Text And UI Fit

Plan exact rules for:

- long hero headline;
- button labels;
- nav labels;
- pricing and metric numbers;
- card titles and long words;
- legal/compliance copy;
- form labels and errors.

Use `text-wrap: balance` for headings when supported and useful, `text-wrap: pretty` for short body text when useful, stable button dimensions, and responsive constraints rather than viewport-scaled font sizes.

### Assets And Motion

- Reserve dimensions for images/video/canvas to avoid CLS.
- Write mobile crop rules before implementation.
- Simplify motion on mobile when it competes with reading or causes jank.
- Replace heavy WebGL/3D with static render or poster on small devices when needed.
- Keep reduced-motion fallback compatible with every viewport.

## Blocking Risks

- CTA falls below first viewport because hero visual is too tall.
- Mobile hero clips headline, CTA or product subject.
- Wide desktop has empty bands or stretched screenshots.
- Cards resize on hover and shift layout.
- Sticky header overlaps anchor targets.
- Horizontal overflow appears from grid, canvas, image, code block, table or long word.
- Pricing table becomes unreadable on mobile.
- Carousel hides critical content.

## Required Output

Fill:

```text
projects/<slug>/27-responsive-viewport-map.md
```

Then update:

```text
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/10-quality-gate.md
projects/<slug>/23-presentation-quality-review.md
```

Implementation handoff is not allowed until each planned viewport has an explicit composition and screenshot QA row.
