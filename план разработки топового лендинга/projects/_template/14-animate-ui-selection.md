# Animate UI Selection

Use this only after reading `17-animate-ui-full-site-map.md` and `docs/research/animate-ui-catalog.md`.

## Section Decisions

| Section | Need | Live docs branch | Candidate registry item | Source URL | Install command | Dependency impact | Motion purpose | Reduced-motion fallback | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fill with project section | Fill with section job | Fill with components/primitives/icons/guide or "none" | Fill with exact item or "none" | Fill with docs or registry URL | Fill with exact command or "none" | Fill with packages and registry deps | Fill with purpose or "none" | Fill with fallback | Fill with risk |

## Icon Decisions

Use this section only when animated Lucide icons are selected.

| Icon role | Exact icon item | Wrapper needed | Trigger | Animation | Persistence | Timing | Reduced-motion fallback |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fill with CTA/status/tool role | Fill with exact `icons-*` item | Fill with yes/no | Fill with hover/tap/controlled/none | Fill with animation name | Fill with reset or persist | Fill with delay/loop or "none" | Fill with static icon fallback |

## Accepted Items

Record only items that survive component-source review, offer clarity review, dependency review, and mobile/reduced-motion review.

## Rejected Items

Record tempting Animate UI items that were not used, with the reason. This prevents the next agent from adding shiny motion without context.

## Notes For Implementation

- Install one exact item at a time.
- Preserve existing `cn()` and aliases.
- Keep client boundaries tight.
- Add screenshots after implementation.
- Do not add a background, cursor, radial menu, or particle effect without an explicit section purpose.
