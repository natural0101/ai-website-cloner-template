# Eldora UI Selection

Use this only after reading `49-eldora-ui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- Eldora UI used: yes/no
- Section need:
- Existing/native alternative considered first:
- MIT/license gate handled: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Eldora UI Items

Keep the explicit `none` row until a real verified Eldora UI item replaces it.

| Section | Job | Exact Item | Item Type | Source URL | Endpoint URL | Install Command | License/Access | Dependencies | Registry Dependencies | Evidence Path | Visible Purpose | Adaptation | Mobile Behavior | Reduced-motion Fallback | Performance Risk | Decision | Task ID | Change ID | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no Eldora UI item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | License Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `motion`/`cobe`/`three`/`react-spring`/`react-three-fiber`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Animate UI/Motion Primitives/SmoothUI/Skiper UI/custom/none |

## License And Adaptation Notes

- MIT license checked:
- Source attribution needed:
- Public registry endpoint checked:
- Demo/example material avoided or adapted:
- Visual adaptation:
- Copy/content adaptation:
- Demo data replacement:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact Eldora UI endpoint `https://eldoraui.site/r/<name>.json` is verified before install.
- Official `@eldoraui/<name>` or exact URL command is recorded before install.
- `registry:example` items are not treated as normal install choices without a written reason.
- Wrong path `https://eldoraui.site/registry/<name>.json` is not used as evidence.
- Dependencies and registry dependencies are listed in `08-component-and-asset-plan.md`.
- Device frames, terminal output, GitHub comments, testimonials, logos and integration proof use real project content or are rejected.
- Heavy globe/map/background dependencies have performance and mobile fallbacks.
- Reduced-motion fallback and mobile behavior are defined.
- Screenshots/video evidence are listed in evidence manifests.
