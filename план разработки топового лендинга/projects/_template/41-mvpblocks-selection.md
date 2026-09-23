# MVPBlocks Selection

Use this only after reading `45-mvpblocks-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- MVPBlocks used: yes/no
- Section need:
- Existing/native alternative considered first:
- Root registry index used: no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate MVPBlocks Items

Keep the explicit `none` row until a real verified MVPBlocks item replaces it.

| Section | Job | Category | Exact Item | Docs URL | Endpoint URL | Install Or Copy Command | License/Access | Dependencies | Registry Dependencies | Visible Purpose | Adaptation | Reduced-motion fallback | Mobile Behavior | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no MVPBlocks item selected yet | none | none | none | none | none | BSD-3-Clause/MIT/reference-only | none | none | none | none | none | none | reject | task-001 | chg-001 | none | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | public/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `framer-motion`/`gsap`/`recharts`/`next`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Animate UI/Motion Primitives/Magic UI/Tailark/shadcnblocks/ReUI/Kokonut UI/custom/none |

## License And Adaptation Notes

- Repository license checked:
- NPM package license checked:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact MVPBlocks docs page is recorded before install or copy.
- Exact `https://blocks.mvp-subha.me/r/<name>.json` endpoint is verified before install.
- Root `/r/registry.json` and `/registry.json` are not used as evidence.
- Dependencies are listed in `08-component-and-asset-plan.md`.
- Demo copy, fake metrics, fake screenshots, fake logos and fake testimonials are replaced or rejected.
- Reduced-motion fallback is defined for motion components.
- Mobile behavior is simplified and checked.
- Screenshots/video evidence are listed in evidence manifests.
