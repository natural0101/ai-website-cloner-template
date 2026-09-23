# PaceKit GSAP Source Map

Дата обновления: 2026-07-03.

PaceKit GSAP is a shadcn-style registry of GSAP-powered React components. Use it only when the section earns GSAP choreography; it is not a default reveal library.

## Verified Sources

| Source | URL | Result |
| --- | --- | --- |
| Current docs | https://gsap.pacekit.dev/ | 200 |
| Live registry | https://gsap.pacekit.dev/r/registry.json | 200, 29 items |
| Item JSON sample | https://gsap.pacekit.dev/r/ai-modal-ability-selector.json | 200 JSON |
| Source repo | https://github.com/pacekit/gsap | 200 |
| Raw registry | https://raw.githubusercontent.com/pacekit/gsap/main/public/r/registry.json | 200 |
| License | https://raw.githubusercontent.com/pacekit/gsap/main/LICENSE.md | MIT |
| Old Pace UI URL | https://ui.paceui.com/ | 404 Vercel deployment missing |
| Pace UI umbrella | https://www.paceui.com/ | 200, but guessed `/r/gsap/*` endpoints are not valid |

## Registry Inventory

Live registry count:

- 29 total items.
- 1 `registry:style` item named `index`.
- 28 `registry:ui` items.

Public `public/r` contains 30 JSON files: 28 UI item files, `registry.json`, and `mcp.json`.

Docs categories from `content/docs/components/meta.json`:

- AI Toolkit: `ai-modal-selector`, `ai-modal-ability-selector`, `ai-suggestions`, `ai-response-writer`, `ai-token-counter`.
- Text Effects: `reveal-text`, `scramble-text`, `squash-text`, `bouncing-text`, `draw-line-text`, `mouse-wave-text`.
- Dot Animations: `dot-loader`, `dot-flow`, `flow-builder`.
- Buttons: `text-fall-button`, `spring-button`, `fillable-button`.
- Utility and misc: `swap`, `animated-stack`, `layered-stack`, `gradient-shadow`, `github-star-counter`, `profile-peek`, `flip-reveal`.
- Special cases: `overlay-effects`, `reveal-on-scroll`, `stagger-on-scroll`, `liquid-cursor`, `liquid-glass`, `tilt-card`.

Not every docs page has an installable registry item. Verify exact item JSON before use.

## Install Model

Use exact item registry URL:

```bash
npx shadcn@latest add https://gsap.pacekit.dev/r/<item>.json
```

Do not use old `ui.paceui.com` or guessed `paceui.com/r/gsap/*` URLs.

Use PaceKit GSAP only after `projects/<slug>/36-pacekit-gsap-selection.md` records item, source URL, registry URL, install command, dependencies, registry dependencies, GSAP purpose, fallback, mobile simplification, task ID, change ID and QA.

## Dependency Risk

Registry dependency scan:

- `gsap`: 26 items.
- `@gsap/react`: 26 items.
- `tw-animate-css`, `class-variance-authority`, `lucide-react`: style/index item.
- Some items depend on shadcn or PaceKit registry dependencies such as `button`, `dropdown-menu`, `tooltip`, `@pacekit-gsap/swap`, `@pacekit-gsap/dot-loader`, or `@pacekit-gsap/rolling-number`.

PaceKit GSAP should lose to CSS, Motion Primitives, Animate UI or existing components unless the planned animation needs GSAP-specific sequencing, timeline control or interaction choreography.

## Best Landing Defaults

| Need | Good candidates | Notes |
| --- | --- | --- |
| Hero or section text reveal | `reveal-text`, `scramble-text`, `draw-line-text`, `flip-reveal` | Short display text only; reduced motion shows final text. |
| Product/state writing | `ai-response-writer`, `ai-suggestions`, `ai-token-counter` | Only for truthful AI/product UI previews. |
| Scroll/story reveal | `reveal-on-scroll`, `stagger-on-scroll`, `animated-stack`, `layered-stack` | Use when timing and sequence matter. |
| CTA/card tactility | `spring-button`, `fillable-button`, `tilt-card`, `gradient-shadow` | One primary action or surface max. |
| Open-source proof | `github-star-counter` | Only with real GitHub project and real numbers. |

## Reject Or Use Carefully

- Reject `liquid-cursor` by default because custom cursors reduce normal UX.
- Reject `liquid-glass` unless the brand has an explicit glass/material direction and contrast QA.
- Reject `dot-loader` and `dot-flow` unless loading/progress is a real product state.
- Reject `ai-modal-*` unless the product truthfully has AI controls and the component is adapted to real data.
- Reject any PaceKit item for a simple fade/slide/hover that CSS, Motion Primitives, Animate UI or React Bits can handle more cheaply.

## Selection Rules

1. Start from `26-motion-reference-map.md` and `16-motion-recipe-selection.md`.
2. Use PaceKit GSAP only when GSAP is already justified by section choreography.
3. Verify exact live registry item URL before adding it.
4. Record decision in:

```text
projects/<slug>/36-pacekit-gsap-selection.md
```

5. Promote accepted rows into:

```text
projects/<slug>/08-component-and-asset-plan.md
projects/<slug>/16-motion-recipe-selection.md
projects/<slug>/20-implementation-task-graph.md
projects/<slug>/28-change-traceability-matrix.md
```

6. Keep rejected tempting GSAP items in the rejection table so implementation does not add them later.
