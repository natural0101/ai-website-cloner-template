# Blocks.so Selection

Use this only after reading `50-blocks-so-source-map.md`, `11-component-source-registry.md`, `08-component-and-asset-plan.md`, and the relevant section storyboard.

## Selection Summary

- Blocks.so used: yes/no
- Section need:
- Existing/native alternative considered first:
- MIT/license gate handled: yes/no
- Demo-data replacement handled: yes/no
- Overall decision: accept/adapt/reject/backlog/reference-only

## Candidate Blocks.so Items

Keep the explicit `none` row until a real verified Blocks.so item replaces it.

| Section | Job | Exact Item | Category | Source Page | Endpoint URL | Install Command | License/Access | Dependencies | Registry Dependencies | Evidence Path | Visible Purpose | Demo-data Replacement | Accessibility Notes | Mobile Behavior | Reduced-motion Fallback | Decision | Task ID | Change ID | QA Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | no Blocks.so item selected yet | none | none | none | none | none | MIT/reference-only | none | none | none | none | none | none | none | none | reject | task-001 | chg-001 | none |

## Installation Queue

| Order | Item | Command | Files Expected | Dependency Impact | License Gate | Owner Task | Verification |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | none | none | none | none | MIT/reference-only | task-001 | none |

## Runtime And Style Gate

| Item | Dependency | Why Accepted Or Rejected | Style Adaptation | Performance QA | Fallback |
| --- | --- | --- | --- | --- | --- |
| none | `recharts`/`@tanstack/react-table`/`react-dropzone`/`ai`/`framer-motion`/none | reject until exact need exists | none | none | none |

## Rejected Items

| Item | Why It Looked Useful | Rejection Reason | Replacement |
| --- | --- | --- | --- |
| none | none | none | native/shadcn/Tailark/shadcnblocks/ReUI/HextaUI/MVPBlocks/SmoothUI/Eldora UI/custom/none |

## License And Adaptation Notes

- MIT license checked:
- Source attribution needed:
- Public registry endpoint checked:
- Duplicate `file-upload-01` registry entry handled:
- Demo data replaced:
- Fake proof removed:
- Visual adaptation:
- Copy/content adaptation:
- Token/radius/spacing changes:
- Accessibility notes:

## QA Checklist

- Exact Blocks.so endpoint `https://blocks.so/r/<name>.json` is verified before install.
- Official `@blocks-so/<name>` or exact URL command is recorded before install.
- Source page `https://blocks.so/<category>/<name>` is recorded before install.
- Live registry body reset is not treated as source failure; GitHub raw registry is used for catalog rebuilds.
- Duplicate registry index entry `file-upload-01` is not counted as two choices.
- Dependencies and registry dependencies are listed in `08-component-and-asset-plan.md`.
- Demo metrics, users, files, chats, forms, tables and dashboard states use real project content or are rejected.
- Mobile behavior and accessibility states are defined for dense tables, dialogs, sidebars, forms and uploads.
- Screenshots/video evidence are listed in evidence manifests.
