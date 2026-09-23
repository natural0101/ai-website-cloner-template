# Cult UI Selection

Use this only after reading `41-cult-ui-source-map.md`, `11-component-source-registry.md`, `26-motion-reference-map.md`, `16-motion-recipe-selection.md`, and `08-component-and-asset-plan.md`.

## Selection Summary

- Cult UI used: yes/no
- Section need:
- Lower-risk source considered first:
- Exact reason Cult UI earns its dependency/style cost:
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Cult UI Items

| Section | Job | Item Type | Exact Item | Source URL | Registry URL | Install Command | Dependencies | Registry Dependencies | Visible Purpose | Adaptation | Reduced-motion fallback | Mobile simplification | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fill with section | Fill with job | surface/button/product/text/widget/media/background | Fill with exact item or none | Fill with docs URL | Fill with live registry URL or none | Fill with exact command or none | Fill with packages | Fill with registry deps or none | proof/tactility/hierarchy/texture/product-flow/media | Fill with how to transform | Fill with static or simpler state | Fill with mobile behavior | accept/adapt/reject/backlog/reference-only | task-001 | chg-001 | Fill with performance/UX risk | Fill with screenshot/video/check |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Fill with item or none | Fill with command or none | Fill with files | Fill with package impact | task-001 | Fill with check |

## Runtime And Style Gate

| Item | Why not native/shadcn/Animate UI/Motion/Magic UI | Heavy Dependency Accepted | Style Risk | Mobile/Reduced-motion Check | Decision |
| --- | --- | --- | --- | --- | --- |
| Fill with item or none | Fill with reason | yes/no | Fill with risk | Fill with check | accept/adapt/reject/backlog/reference-only |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| Fill with item or none | Fill with reason | Fill with risk | native/shadcn/Animate UI/Motion Primitives/Magic UI/React Bits/custom/none |

## License And Adaptation Notes

- License checked:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact `https://cult-ui.com/r/<item>.json` endpoint verified before install.
- No `registry:component` demo was copied as production UI without adaptation.
- Dependencies are listed in `08-component-and-asset-plan.md`.
- Motion purpose is mapped to `16-motion-recipe-selection.md` or marked visual/static.
- Reduced-motion fallback is defined.
- Mobile behavior is simplified and checked.
- Screenshots/video evidence are listed in evidence manifests.
