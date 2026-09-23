# PaceKit GSAP Selection

Use this only after reading `40-pacekit-gsap-source-map.md`, `11-component-source-registry.md`, `26-motion-reference-map.md`, and `16-motion-recipe-selection.md`.

## Selection Summary

- PaceKit GSAP used: yes/no
- Reason:
- CSS/Motion/Animate UI/React Bits alternative considered:
- GSAP dependency already accepted: yes/no
- Handoff allowed: yes/no

## Candidate PaceKit GSAP Items

| Section | Need | Category | Candidate item | Source URL | Registry URL | Install command | Dependencies | Registry dependencies | GSAP purpose | Reduced-motion fallback | Mobile simplification | Decision | Owner task ID | Change ID | Risk | QA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fill with section | Fill with job | text/scroll/button/product/utility | Fill with exact item or none | Fill with docs URL | Fill with live registry URL or none | Fill with exact command or none | `gsap`, `@gsap/react`, other packages | Fill with shadcn/PaceKit deps or none | timeline/sequence/scroll/choreography/state | Fill with static final state | Fill with mobile behavior | accept/adapt/reject/backlog/reference-only | task-001 | chg-001 | Fill with performance/UX risk | Fill with screenshot/video/check |

## Installation Queue

| Order | Item | Command | Files expected | Owner task ID | Change ID |
| --- | --- | --- | --- | --- | --- |
| 1 | Fill with exact item or none | Fill with exact command or none | Fill with files or none | task-001 | chg-001 |

## GSAP Runtime Gate

| Item | Why GSAP is required | Cheaper alternative rejected | Performance QA | Fallback |
| --- | --- | --- | --- | --- |
| Fill with item or none | Fill with timeline/scroll/state reason | CSS/Motion/Animate UI/React Bits/custom/none | Fill with desktop/mobile/reduced-motion check | Fill with fallback |

## Rejected Items

| Item | Temptation | Rejection reason | Safer alternative |
| --- | --- | --- | --- |
| liquid-cursor/liquid-glass/dot-loader/etc | Fill with why it looked useful | Fill with reason | CSS/Motion/Motion Primitives/React Bits/none |

## License And Adaptation Notes

- Use one exact PaceKit GSAP item at a time.
- Verify live `https://gsap.pacekit.dev/r/<item>.json` before install.
- Do not use old `ui.paceui.com` or guessed `paceui.com/r/gsap/*` URLs.
- Record `gsap` and `@gsap/react` dependency impact in `08-component-and-asset-plan.md`.
- Keep client boundaries tight and avoid global timeline side effects.
- Add desktop/mobile screenshot or video QA, reduced-motion QA and performance QA before handoff.
