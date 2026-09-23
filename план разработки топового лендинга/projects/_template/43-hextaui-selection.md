# HextaUI Selection

Use this only after reading `47-hextaui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- HextaUI used: yes/no
- Section need:
- Existing/native alternative considered first:
- HTML docs caveat handled: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate HextaUI Items

Keep the explicit `none` row until a real verified HextaUI item replaces it.

| Section | Job | Group | Exact Item | Source URL | Endpoint URL | Install Command | License/Access | Dependencies | Registry Dependencies | Evidence Path | Visible Purpose | Adaptation | Mobile Behavior | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no HextaUI item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | reject | task-001 | chg-001 | none | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/public/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `react-markdown`/`shiki`/`recharts`/`next`/`vaul`/`react-day-picker`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/ReUI/MVPBlocks/SmoothUI/Kokonut UI/custom/none |

## License And Adaptation Notes

- License checked:
- HTML docs caveat:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Demo data replacement:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact HextaUI endpoint `https://www.hextaui.com/r/<name>.json` is verified before install.
- Official `@hextaui/<name>` or exact URL command is recorded before install.
- HTML detail page timeout is handled by using registry, `llms.txt`, GitHub or RSS evidence.
- Root `/registry.json` and registry subdomain guesses are not used as evidence.
- Dependencies and registry dependencies are listed in `08-component-and-asset-plan.md`.
- Demo copy, fake metrics, fake users, fake invoices, fake prompts and fake workflows are replaced or rejected.
- Mobile behavior is simplified and checked for dense app blocks.
- Screenshots/video evidence are listed in evidence manifests.
