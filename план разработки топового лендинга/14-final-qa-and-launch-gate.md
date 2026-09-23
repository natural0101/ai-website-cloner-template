# Final QA And Launch Gate

Use this after implementation and before calling a landing page done.

## Required Evidence

- Desktop screenshot.
- Mobile screenshot.
- Hero crop.
- Screenshot of any animated/interactive state if relevant.
- Registered screenshot manifest entries.
- Completed `23-presentation-quality-review.md` with non-blocked verdict.
- Commands run.
- Accessibility/performance notes.
- Remaining risks.

## Visual QA

Check:

- Presentation quality review has no blocker findings.
- Hero fits first viewport.
- Primary CTA is visible without scroll on desktop.
- Navigation is one line on desktop.
- Typography hierarchy is clear.
- Text does not overlap, clip, or wrap badly.
- Layout rhythm changes across sections.
- No section looks like an uncustomized component demo.
- Assets are sharp, properly cropped, and relevant.
- Mobile layout is not a shrunken desktop.

## Copy QA

Check:

- One offer.
- One audience.
- One primary CTA intent.
- No fake proof.
- No fake numbers.
- No generic "elevate/unleash/seamless" filler.
- FAQ answers real objections.
- Every visible string was reread.

## Motion QA

Check:

- Every animation appears in `07-animation-storyboard.md`.
- Every animation has a purpose.
- Every accepted animation has a motion safety verdict from `53-motion-safety-source-map.md`.
- Reduced-motion fallback exists.
- Motion does not hide CTA or content.
- No layout shift during reveal.
- No scroll animation implemented with React state.
- Heavy WebGL/3D has static fallback.

## Accessibility QA

Check:

- Text contrast passes WCAG AA target.
- Buttons and links have focus states.
- Forms have labels and error/help text.
- Images have useful alt text or empty alt when decorative.
- Keyboard navigation reaches interactive elements.
- Motion respects reduced-motion preference.

## Performance QA

Check:

- LCP asset is optimized or prioritized.
- Images have stable dimensions.
- Heavy below-fold media is lazy-loaded.
- 3D/WebGL/video has fallback.
- CLS risk is low.
- Bundle/dependency additions are justified.

## Useful Official References

- Lighthouse docs: https://developer.chrome.com/docs/lighthouse
- web.dev Core Web Vitals: https://web.dev/vitals/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI accessibility fundamentals: https://www.w3.org/WAI/fundamentals/
- axe DevTools: https://docs.deque.com/devtools-for-web/
- Playwright accessibility testing: https://playwright.dev/docs/accessibility-testing

## Output

Fill `12-final-qa-report.md` in the project plan folder. The page is not done until the report contains evidence, commands, screenshots, and remaining risks.

Use `15-visual-evidence-capture.md` for screenshot naming and manifest registration.
