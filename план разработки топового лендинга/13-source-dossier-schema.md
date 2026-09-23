# Source Dossier Schema

This schema is for the other project. It makes `landing-source-dossier.md` predictable enough to validate and use here.

## Required File

```text
landing-source-dossier.md
```

## Required Sections

### 1. Product Snapshot

- product/service:
- target audience:
- primary CTA:
- conversion goal:
- offer:
- traffic/source assumption:
- known constraints:
- current quality level:

### 2. Current Site Map

- routes:
- main files:
- landing components:
- shared UI components:
- assets:
- SEO files:
- analytics/form integrations:
- UI/motion dependencies:

### 3. Current Landing Structure

For every section:

- section ID/name:
- file/component:
- current purpose:
- visible copy:
- CTA/proof/assets:
- layout:
- mobile behavior:
- what works:
- what is weak:

### 4. Visual Audit

- typography:
- color palette:
- spacing/rhythm:
- layout families:
- imagery/3D/video:
- motion/interactions:
- mobile issues:
- responsive/viewport issues:
- hero first viewport:
- nav height/behavior:
- text wrapping or overflow issues:
- asset crop issues:
- accessibility issues:
- manual accessibility notes:
- heuristic issues by severity:
- CTA/conversion friction:
- trust/proof gaps:
- performance risks:

### 5. Evidence Inventory

- live URL or local preview URL:
- desktop screenshot path or unavailable reason:
- mobile screenshot path or unavailable reason:
- hero/above-fold screenshot path or unavailable reason:
- desktop viewport:
- mobile viewport:
- tablet/wide viewport or unavailable reason:
- first viewport notes:
- horizontal overflow check:
- source files inspected:
- CSS/token evidence:
- asset paths inspected:
- commands run and result:
- console errors or unavailable reason:
- Lighthouse report/path or unavailable reason:
- manual accessibility check result:
- heuristic evaluation notes:
- browser/Lighthouse/Playwright availability:
- unknowns:

### 6. Brand And Content Preservation

- copy to preserve:
- routes/slugs/anchors to preserve:
- nav labels to preserve:
- form fields to preserve:
- analytics-sensitive labels:
- legal/SEO copy:
- brand assets:
- brand DNA clues: colors, fonts, voice, layout rhythm, asset style, motion style, trust signals:
- do-not-change notes:

### 7. Upgrade Opportunities

8 to 15 items. For each:

- problem:
- severity: cosmetic / minor / major / blocker:
- possible improvement:
- expected user impact:
- affected section:
- heuristic/source principle:
- risk:
- evidence:

### 8. Reference Hooks

Minimum target when internet is available:

- 3 direct/domain references:
- 3 aesthetic/visual references:
- 2 motion/component references:

For each:

- URL:
- why relevant:
- borrow:
- do not copy:
- section mapping:

### 9. Technical Constraints

- framework:
- package manager:
- build/dev/check commands:
- installed UI libraries:
- installed animation libraries:
- styling system:
- known errors:
- files risky to edit:
- browser/screenshot availability:

### 10. Handoff Summary

- best redesign mode: preserve / targeted evolution / overhaul;
- recommended vibe:
- recommended motion intensity:
- recommended asset direction:
- recommended first tasks:
- open questions:
- assumptions:

## Validation

Run in this project:

```bash
node scripts/check-source-dossier.mjs path/to/landing-source-dossier.md
```

The checker validates headings, key terms, URLs, placeholders, and dossier length. It is a minimum gate, not a substitute for human review.

Use severity to prioritize planning. A `blocker` prevents conversion or comprehension, `major` damages a core CTA or trust path, `minor` causes friction but has a workaround, and `cosmetic` is presentational polish.

## Handoff Inspiration

This schema follows the same spirit as design-to-development handoff: make design intent inspectable and implementation-safe.

Useful public references:

- Source dossier forensics: `24-source-dossier-forensics.md`
- Figma developer handoff: https://www.figma.com/best-practices/guide-to-developer-handoff/
- Figma Dev Mode guide: https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode
- UXPin design handoff checklist: https://www.uxpin.com/studio/blog/design-handoff-checklist/
