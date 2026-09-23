# Responsive Viewport Map

Use after `18-section-storyboard-canvas.md`, `19-asset-production-queue.md`, `26-motion-reference-map.md` and `17-visual-style-tile.md`. Read `31-responsive-viewport-storyboard.md` before filling this file.

## Viewport Set

| Viewport ID | Size | Reason | Screenshot required | Notes |
| --- | ---: | --- | --- | --- |
| mobile-s | 360 x 740 | cramped phone check | yes | Fill with route/section notes |
| mobile | 390 x 844 | common mobile check | yes | Fill with route/section notes |
| tablet | 768 x 1024 | tablet transition check | yes | Fill with route/section notes |
| laptop | 1440 x 900 | default desktop check | yes | Fill with route/section notes |
| wide | 1920 x 1080 | wide composition check | yes | Fill with route/section notes |

## First Viewport Plan

| Viewport ID | Brand/product signal | Headline line breaks | Subhead lines | CTA position | Proof hint | Hero visual crop | Next section hint | Nav behavior | Blocker risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobile | Fill with visible signal | Fill with expected wrapping | Fill with count | Fill with position/wrap | Fill with proof | Fill with crop | Fill with yes/no | Fill with behavior | Fill with risk |

## Section Transformations

| Section | Desktop composition | Tablet composition | Mobile composition | Order changes | Hidden/replaced elements | Asset crop/aspect | Motion simplification | QA screenshot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hero | Fill with frame | Fill with frame | Fill with frame | Fill with changes | Fill with changes | Fill with crop | Fill with simplification | Fill with shot ID |

## Typography And UI Fit

| Element | Risk | Rule | Min/max size or width | Wrap behavior | QA |
| --- | --- | --- | --- | --- | --- |
| Hero headline | Fill with risk | Fill with rule | Fill with constraint | Fill with balance/pretty/manual line break | Fill with viewport |
| Primary CTA | Fill with risk | Fill with rule | Fill with constraint | Fill with no-wrap/wrap-stack | Fill with viewport |

## Asset Crop Rules

| Asset ID | Section | Desktop crop | Mobile crop | Wide crop | Stable dimensions | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| asset-001 | Fill with section | Fill with crop | Fill with crop | Fill with crop | Fill with width/height/aspect | Fill with fallback |

## Overflow And Sticky Risk Register

| Risk ID | Viewport | Section | Risk | Prevention | QA method | Status |
| --- | --- | --- | --- | --- | --- | --- |
| resp-001 | mobile | Hero | Fill with overflow/clipping risk | Fill with prevention | Fill with screenshot/check | open |

## Screenshot QA Matrix

| Screenshot ID | Viewport | Section or range | Must prove | Evidence path after implementation |
| --- | --- | --- | --- | --- |
| shot-responsive-001 | mobile | Hero | CTA, headline and hero subject fit first viewport | Fill after capture |

## Task Graph Updates

| Task ID | Responsive requirement | Files/routes | Depends on | Verification |
| --- | --- | --- | --- | --- |
| task-xxx | Fill with responsive requirement | Fill with files | Fill with task IDs | Fill with viewport screenshot/check |

## Handoff Guardrails

- Do not implement desktop-only composition without the mobile and wide frame.
- Do not hide primary content on mobile unless the plan names the replacement.
- Do not use viewport-scaled font sizes as the only fit strategy.
- Do not call presentation-ready until screenshot QA covers the required viewport set.
