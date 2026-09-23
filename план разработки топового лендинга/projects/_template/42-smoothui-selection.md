# SmoothUI Selection

Use this only after reading `46-smoothui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- SmoothUI used: yes/no
- Section need:
- Existing/native alternative considered first:
- Blocks API used as evidence: no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate SmoothUI Items

Keep the explicit `none` row until a real verified SmoothUI item replaces it.

| Section | Job | Type | Exact Item | Docs Or Preview URL | Endpoint URL | Install Command | License/Access | Dependencies | Registry Dependencies | API Or Registry Evidence | Visible Purpose | Adaptation | Reduced-motion fallback | Mobile Behavior | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no SmoothUI item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/public/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `motion`/`lucide-react`/`gsap`/`react-tweet`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Animate UI/Motion Primitives/Magic UI/Kokonut UI/MVPBlocks/custom/none |

## License And Adaptation Notes

- License checked:
- Blocks API status checked:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact SmoothUI docs page or preview page is recorded before install or adaptation.
- Exact `https://smoothui.dev/r/<name>.json` endpoint is verified before install.
- For components, `/api/v1/components/<name>` metadata is checked when available.
- For blocks, `/api/v1/blocks` and `/api/v1/blocks/<name>` are not used as evidence.
- Dependencies are listed in `08-component-and-asset-plan.md`.
- Demo copy, fake metrics, fake screenshots, fake tweets, fake logos and fake AI states are replaced or rejected.
- Reduced-motion fallback is defined for motion components, especially components with no built-in reduced-motion flag.
- Mobile behavior is simplified and checked.
- Screenshots/video evidence are listed in evidence manifests.
