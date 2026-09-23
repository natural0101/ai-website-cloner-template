---
name: landing-final-qa
description: Perform final QA for an implemented landing page against the approved plan, screenshots, accessibility, performance, copy, motion, assets, and launch-readiness gates. Use when reviewing a built landing page, filling `12-final-qa-report.md`, checking presentation readiness, or deciding whether implementation is actually done.
---

# Landing Final QA

Use this skill after implementation, not during early planning.

## Required Reading

Read:

- the project plan folder;
- `10-quality-gate.md`;
- `12-final-qa-report.md`;
- `evidence/` manifests;
- `план разработки топового лендинга/53-motion-safety-source-map.md`;
- `план разработки топового лендинга/14-final-qa-and-launch-gate.md`.

## Workflow

1. Verify plan compliance.
   - Section order.
   - Protected content.
   - Asset IDs.
   - Motion storyboard.
   - Approved dependencies.

2. Inspect visuals.
   - Desktop, mobile, hero crop.
   - Typography, spacing, rhythm, clipping, overlap.
   - Asset quality and crop.

3. Inspect copy.
   - Offer, audience, CTA.
   - Proof and claims.
   - FAQ and objections.

4. Inspect motion.
   - Purpose.
   - Motion safety verdict.
   - Reduced-motion fallback.
   - Mobile simplification.
   - No content hiding or layout shift.
   - No scroll animation through React state.

5. Inspect accessibility and performance.
   - Contrast, focus, labels, alt text, keyboard access.
   - LCP, INP, CLS, lazy-loading, heavy dependency impact.

6. Fill `12-final-qa-report.md`.
   - Include commands.
   - Include screenshot paths.
   - Include remaining risks.
   - Give a presentation-ready verdict.

## Official References

- Lighthouse docs: https://developer.chrome.com/docs/lighthouse
- Core Web Vitals: https://web.dev/vitals/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WAI fundamentals: https://www.w3.org/WAI/fundamentals/
- axe DevTools: https://docs.deque.com/devtools-for-web/
- Playwright accessibility testing: https://playwright.dev/docs/accessibility-testing

## Hard Rule

Do not mark the landing page done if screenshots are missing, the QA report is empty, accessibility/performance risks are uninspected, or the implementation does not match the approved plan.
