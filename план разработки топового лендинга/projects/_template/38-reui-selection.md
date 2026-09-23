# ReUI Selection

Use this only after reading `42-reui-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- ReUI used: yes/no
- Section need:
- Existing/shadcn/Kibo/Origin alternative considered first:
- Style chosen: radix-nova/base-nova/none
- Access status: free/pro/license-key-needed/reference-only
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate ReUI Items

Keep the explicit `none` row until a real verified ReUI item replaces it.

| Section | Job | Style | Exact Item | Source URL | Registry URL | Install Command | Access | License Key Status | Dependencies | Registry Dependencies | Visible Purpose | Adaptation | Mobile Behavior | Keyboard/Focus QA | Decision | Task ID | Change ID | Risk | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no ReUI item selected yet | none | none | none | none | none | reference-only | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | Access Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Fill with item or none | Fill with command or none | Fill with files | Fill with package impact | free/pro/license-key | task-001 | Fill with check |

## Access And Registry Gate

| Item | Endpoint Status | Free/Pro | License Evidence | Replacement If Blocked | Decision |
| --- | --- | --- | --- | --- | --- |
| Fill with item or none | 200/401/403/not checked | free/pro/reference-only | none/key/path/account note | shadcn/Kibo/Origin/custom/reference-only/none | accept/adapt/reject/backlog/reference-only |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| Fill with item or none | Fill with reason | Fill with access/dependency/UX reason | native/shadcn/Kibo/Origin/custom/reference-only/none |

## License And Adaptation Notes

- License checked:
- Free/pro status:
- `REUI_LICENSE_KEY` needed:
- Source attribution needed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact ReUI endpoint verified before install.
- 401/403 endpoints are rejected or marked reference-only unless license evidence exists.
- Root `/registry.json` is not used.
- Dependencies are listed in `08-component-and-asset-plan.md`.
- Keyboard/focus behavior is checked for interactive components.
- Mobile behavior is simplified and checked.
- Screenshots/video evidence are listed in evidence manifests.
