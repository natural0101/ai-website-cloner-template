# Micro Component Selection

Use this only after reading `38-micro-component-source-map.md`, `11-component-source-registry.md`, `18-section-storyboard-canvas.md`, and `08-component-and-asset-plan.md`.

## Selection Summary

- Micro component source used: yes/no
- Sources considered: Kibo UI / Origin-Coss / native shadcn / custom / rejected
- Role: form polish / app preview / product UI / code/media / table/data / proof detail / rejected
- License and access status:
- Existing/native alternative considered:
- Dependency budget:
- Live endpoint verification:
- Heavy endpoint/body-fetch caveat:
- Handoff allowed: yes/no

## Candidate Micro Components

| Section | Need | Source | Candidate item | Source URL | Registry or copy URL | Install command or copy method | Dependencies | Purpose | Adaptation required | Reduced-motion fallback | Mobile simplification | Keyboard/focus QA | Decision | Owner task ID | Change ID | Risk | QA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fill with section | Fill with job | Kibo/Origin-Coss/native/custom | Fill with exact item or none | Fill with live docs/item URL | Fill with JSON/copy source or none | Fill with exact command/copy method or none | Fill with packages | form/product-flow/proof/code/media/data | Fill with how to transform | Fill with fallback or none | Fill with mobile behavior | Fill with keyboard/focus check | accept/adapt/reject/backlog/reference-only | task-001 | chg-001 | Fill with risk | Fill with screenshot/check |

## Installation Or Copy Queue

| Order | Source | Item | Command or copy method | Files expected | Owner task ID | Change ID |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Fill with source or none | Fill with exact item or none | Fill with exact command/copy method | Fill with files or none | task-001 | chg-001 |

## Rejected Items

| Source | Item | Temptation | Rejection reason | Safer alternative |
| --- | --- | --- | --- | --- |
| Kibo/Origin-Coss/etc | Fill with item | Fill with why it looked useful | Fill with reason | Fill with native/custom/static/reference-only/none |

## License And Adaptation Notes

- Kibo UI item URLs use `https://www.kibo-ui.com/r/<name>.json`; root `/registry.json` is not valid.
- Kibo UI exact package names must be verified. Generic guesses such as `button`, `accordion`, or `ai-input` are not valid Kibo item evidence.
- For Kibo `editor`, `gantt`, or `reel`, require a fresh successful body fetch or mark the item reference-only/backlog.
- Origin/Coss live registry URLs use `https://coss.com/ui/r/<name>.json`; `originui.com/r/*` can redirect to HTML.
- Kibo UI is MIT-style; Origin UI is MIT. Still record exact source and license.
- Do not overwrite project style tokens or shadcn conventions just to use one component.
- Record dependency changes in `08-component-and-asset-plan.md`.
- Add screenshot QA, mobile QA, keyboard/focus QA, contrast QA and reduced-motion checks before handoff.
