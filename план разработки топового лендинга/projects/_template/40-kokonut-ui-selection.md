# Kokonut UI Selection

Use this only after reading `44-kokonut-ui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- Kokonut UI used: yes/no
- Section need:
- Existing/native alternative considered first:
- Pro item involved: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Kokonut UI Items

Keep the explicit `none` row until a real verified Kokonut UI item replaces it.

| Section | Job | Category | Exact Item | Docs URL | Registry URL | Install Command | License/Access | Dependencies | Registry Dependencies | Visible Purpose | Adaptation | Reduced-motion fallback | Mobile Behavior | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no Kokonut UI item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | reject | task-001 | chg-001 | none | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/public/pro/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `motion`/`lucide-react`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Motion Primitives/Animate UI/Magic UI/custom/none |

## License And Adaptation Notes

- License checked:
- Pro access involved:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact Kokonut UI docs page is recorded before install.
- Exact registry endpoint is verified before install.
- Pro components/templates are rejected or marked reference-only unless access/license exists.
- Dependencies are listed in `08-component-and-asset-plan.md`.
- Reduced-motion fallback is defined for motion components.
- Mobile behavior is simplified and checked.
- Screenshots/video evidence are listed in evidence manifests.
