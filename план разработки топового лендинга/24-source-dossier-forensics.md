# Source Dossier Forensics

Дата обновления: 2026-07-03.

Источники:

- https://playwright.dev/docs/screenshots
- https://playwright.dev/docs/test-snapshots
- https://developer.chrome.com/docs/lighthouse/overview
- https://developer.chrome.com/docs/devtools/css-overview
- https://developer.chrome.com/docs/devtools/coverage
- https://developer.chrome.com/docs/devtools/performance
- https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility/What_is_accessibility
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- https://www.nngroup.com/articles/ten-usability-heuristics/
- https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/
- https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/

Этот слой нужен в другом проекте, до передачи `landing-source-dossier.md` сюда. Его цель: сделать dossier доказательным, а не впечатлением по памяти.

## Что собрать

| Evidence type | Minimum | Why it matters |
| --- | --- | --- |
| Routes | landing route plus related routes/anchors | protects navigation and SEO |
| Files | page files, landing components, global styles, config | tells implementation where the surface lives |
| Screenshots | desktop, mobile, hero crop when possible | proves visual state and mobile behavior |
| Copy | headline, subhead, CTA, proof, pricing, FAQ, legal | prevents invented rewrite assumptions |
| Assets | images, videos, icons, logos, GLB/WebGL, fonts | drives asset queue and performance planning |
| Tokens | fonts, colors, radius, spacing rhythm, shadows, borders | gives visual direction a real baseline |
| Interactions | hover, scroll, tabs, forms, modal, video, 3D, motion | informs motion storyboard and reduced-motion needs |
| Heuristic issues | clarity, feedback, consistency, recognition, error prevention, minimalist design, severity | turns subjective critique into prioritized redesign work |
| Preservation | routes, nav labels, form fields, analytics labels, legal/SEO copy | protects behavior that redesign must not break |
| Commands | dev/build/lint/typecheck/test commands and known errors | tells this project what verification is possible |
| Runtime signals | console errors, hydration/runtime issues, broken images, failed network requests if visible | prevents designing on top of broken behavior |
| Risks | mobile, accessibility, performance, dependency and edit-risk notes | prevents hidden implementation traps |

## Evidence Inventory section

The source dossier must include:

- live URL or local preview URL;
- screenshot paths or reason screenshots are unavailable;
- desktop viewport used;
- mobile viewport used;
- screenshot IDs or filenames;
- important asset paths;
- CSS/token evidence;
- command output summary;
- console errors or unavailable reason;
- Lighthouse report/path or unavailable reason;
- manual accessibility check result;
- heuristic evaluation notes with severity;
- browser/Lighthouse/Playwright availability;
- unknowns that must be resolved here.

## Screenshot naming

Use stable names when possible:

```text
evidence/screenshots/current-home-desktop-full.png
evidence/screenshots/current-home-mobile-full.png
evidence/screenshots/current-home-hero-desktop.png
```

If the source project cannot save screenshots, write the reason and include the preview URL.

## Visual token inventory

Capture:

- font family and obvious type scale;
- primary/background/text/accent colors;
- section padding rhythm;
- card radius and border style;
- shadow/glow style;
- dominant layout pattern;
- repeated component patterns;
- motion and transition style.

This is not a redesign. It is a baseline.

## Accessibility and motion notes

Record:

- visible focus states;
- keyboard-risk areas such as menus, dialogs, accordions and forms;
- contrast concerns;
- images without useful alt text;
- animation that moves, scales, parallax-scrolls, loops or autoplay;
- whether `prefers-reduced-motion` is handled or unknown.

Do not treat Lighthouse or another automated checker as a full accessibility pass. Record automated availability separately from manual keyboard, contrast, labels, alt text and motion observations.

## Heuristic and severity notes

Use heuristic review as a short prioritization layer, not as academic filler. For each important issue, record:

- affected section;
- problem;
- heuristic or principle violated;
- severity: cosmetic, minor, major or blocker;
- evidence: screenshot, visible copy, file path, command output or exact unavailable reason;
- possible improvement direction.

## Performance notes

Record:

- heavy hero images, video, GLB/WebGL, background effects and large dependencies;
- missing image dimensions or aspect ratios;
- obvious layout shift risks;
- unused CSS/JS suspicion;
- whether Lighthouse, Coverage or Performance panel was checked.

## Red flags

- Dossier has no screenshots or preview URL.
- Dossier names components but not files.
- Dossier says "mobile is okay" without viewport or screenshot.
- Dossier names "nice colors" without actual tokens.
- Dossier lists problems without severity or evidence.
- Dossier says "Lighthouse/accessibility passed" without separating automated and manual evidence.
- Dossier suggests references before product/CTA is clear.
- Dossier invents proof, metrics, logos or testimonials.
- Dossier does not list do-not-change behavior.

## Output

Fill `landing-source-dossier.md` with the schema in:

```text
план разработки топового лендинга/13-source-dossier-schema.md
```

Then validate with:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```
