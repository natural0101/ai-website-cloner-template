# 21st.dev Selection

Use this only after reading `43-21st-dev-source-map.md`, `11-component-source-registry.md`, `03-reference-board.md`, `15-reference-scorecard.md`, and the relevant section storyboard.

## Selection Summary

- 21st.dev used: yes/no
- Discovery purpose:
- Exact component install allowed: yes/no
- Existing/native alternative considered first:
- Access status: public/reference-only/installable
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate 21st.dev Items

Keep the explicit `none` row until a real verified 21st.dev item replaces it.

| Section | Job | Category/Tag | Component Page | Author/Item | Command | CDN Registry URL | Registry Status | License | Dependencies | Registry Dependencies | Visible Purpose | Adaptation | Fallback | Mobile Behavior | QA Evidence | Decision | Task ID | Change ID | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no 21st.dev item selected yet | none | none | none | none | none | not checked | none | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | reference-only | task-001 | none |

## Access And Registry Gate

| Item | Component Page Status | CDN Registry Status | License Evidence | Replacement If Blocked | Decision |
| --- | --- | --- | --- | --- | --- |
| none | not checked | not checked | none | native/shadcn/Motion Primitives/Animate UI/Magic UI/custom/none | reject |

## Heavy Runtime Gate

| Item | Heavy Dependency | Why Accepted Or Rejected | Performance QA | Fallback |
| --- | --- | --- | --- | --- |
| none | `three`/WebGL/HeroUI/chart/icons/none | reject until exact need exists | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/custom/none |

## License And Adaptation Notes

- License checked:
- Source page:
- Command checked:
- CDN registry checked:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact 21st.dev component page is recorded before install.
- Command is recorded before install.
- CDN registry URL is verified if used.
- Generic `/r/*` guesses are not used as evidence.
- License and dependency impact are listed.
- Heavy runtime is accepted only with performance QA.
- Mobile and reduced-motion fallback are checked.
- Screenshots/video evidence are listed in evidence manifests.
