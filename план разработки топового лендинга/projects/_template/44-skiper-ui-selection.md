# Skiper UI Selection

Use this only after reading `48-skiper-ui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- Skiper UI used: yes/no
- Section need:
- Existing/native alternative considered first:
- Terms/access gate handled: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Skiper UI Items

Keep the explicit `none` row until a real verified Skiper UI item replaces it.

| Section | Job | Exact Item | Source URL | Endpoint URL | Install Command | Access/License Status | Dependencies | Registry Dependencies | Evidence Path | Visible Purpose | Adaptation | Mobile Behavior | Reduced-motion Fallback | Performance Risk | Decision | Task ID | Change ID | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no Skiper UI item selected yet | none | none | none | none | public-registry/reference-only; not MIT | none | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | terms/access not approved | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `framer-motion`/`lenis`/`swiper`/`gsap`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Animate UI/Motion Primitives/SmoothUI/custom/none |

## Access And Adaptation Notes

- Terms/access checked:
- Source attribution needed:
- Public registry endpoint checked:
- Premium/account-only material avoided:
- Visual adaptation:
- Copy/content adaptation:
- Demo data replacement:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact Skiper UI endpoint `https://skiper-ui.com/registry/<name>.json` is verified before install.
- Official `@skiper-ui/<name>` or exact URL command is recorded before install.
- `/preview/skiper*`, `/r/*`, and root `/registry.json` are not used as evidence.
- Terms/access status is recorded; Skiper UI is not marked MIT unless a project-specific license proof exists.
- Premium, account-only, private source, paid template and Figma material are not copied.
- Dependencies and registry dependencies are listed in `08-component-and-asset-plan.md`.
- Brand-like demos are adapted beyond recognition or rejected.
- Reduced-motion fallback and mobile behavior are defined.
- Screenshots/video evidence are listed in evidence manifests.
