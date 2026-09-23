# Intent UI Selection

Use this only after reading `51-intent-ui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- Intent UI used: yes/no
- Section need:
- Existing/native alternative considered first:
- MIT/license gate handled: yes/no
- React Aria dependency accepted: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Intent UI Items

Keep the explicit `none` row until a real verified Intent UI item replaces it.

| Section | Job | Exact Item | Item Type | Source URL | Endpoint URL | Install Command | License/Access | Dependencies | Registry Dependencies | React Aria Impact | Evidence Path | Visible Purpose | Adaptation | Demo-data Replacement | Accessibility Notes | Mobile Behavior | Decision | Task ID | Change ID | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no Intent UI item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | License Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Accessibility QA | Mobile QA | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| none | `react-aria-components`/`@heroicons/react`/`recharts`/`@internationalized/date`/none | reject until exact need exists | none | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Origin-Coss/Kibo UI/ReUI/HextaUI/Blocks.so/custom/none |

## License And Adaptation Notes

- MIT license checked:
- Source attribution needed:
- Public registry endpoint checked:
- `registry:page` examples avoided or marked reference-only:
- `all` item avoided:
- Paid `design.intentui.com` material avoided:
- React Aria dependency accepted:
- Demo data replaced:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact Intent UI endpoint `https://intentui.com/r/<name>` is verified before install.
- Official `@intentui/<name>` or exact URL command is recorded before install.
- `@intentui/all` is not used.
- `registry:page` examples are not treated as production source without a written reason.
- Paid `design.intentui.com` blocks/templates are not used without explicit access/license.
- Dependencies and registry dependencies are listed in `08-component-and-asset-plan.md`.
- React Aria keyboard, focus, label, disabled, validation and screen-reader behavior are tested where relevant.
- Demo users, metrics, forms, files, charts and app states use real project content or are rejected.
- Mobile behavior is defined for forms, tables, sidebars, charts, date/time pickers and overlays.
- Screenshots/video evidence are listed in evidence manifests.
