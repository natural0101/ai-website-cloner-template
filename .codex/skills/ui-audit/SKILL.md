---
name: ui-audit
description: "A systematic quality review framework covering accessibility, interaction, typography, layout, product UI states, dashboards, editors, AI design workbenches, and final QA with a self-improvement protocol for design evolution."
metadata:
  source_url: "https://www.aura.build/skills/c2d90f57-62c2-4ad3-8c44-9d5c8ea55074/ui-audit-and-quality-review"
---

ui-audit
When to use: Final-pass quality review before shipping — concrete, actionable findings across accessibility, interaction, forms, typography, navigation, layout, performance, and motion.

Priority Order
CRITICAL — Accessibility (semantic HTML, keyboard nav), form validation, missing labels
HIGH — Typography readability, navigation clarity, layout visual hierarchy, load states, motion accessibility
MEDIUM — Copy clarity and microcopy tone
Workflow
Identify changed/new surfaces to audit
Run CRITICAL checks (accessibility, keyboard, forms) first
Run HIGH checks (typography, navigation, layout, performance, motion)
Run MEDIUM checks (content, microcopy)
Report findings grouped by file with priority, description, and fix

Product UI Addendum
For dashboards, admin panels, AI design studios, canvas editors, or SaaS apps, also read:

```text
docs/design-workbench/UNIVERSAL_PRODUCT_DESIGN_BRIEF.md
docs/design-workbench/PRODUCT_SURFACE_BLUEPRINTS.md
docs/design-workbench/PRODUCT_UI_QUALITY_GATE.md
docs/design-workbench/PRODUCT_UI_REVIEW_RUBRIC.md
docs/design-workbench/PRODUCT_UI_DESIGN_SYSTEM_BASELINE.md
docs/design-workbench/PRODUCT_UI_VISUAL_QA.md
docs/design-workbench/VISUAL_QA_EVIDENCE_PLAYBOOK.md
docs/design-workbench/AGENT_REPORT_EXAMPLES.md
docs/design-workbench/AI_DESIGN_APP_SCREEN_BLUEPRINT.md
.codex/skills/product-ui-visual-qa/SKILL.md
```

Audit workflow visibility, panel hierarchy, selection states, empty/loading/error states, agent/proposal/review states, data/proof honesty, responsive degradation, and command/keyboard paths before visual polish.
For final product UI sign-off, require screenshots/browser checks or an explicit unverified-risk note. Use `product-ui-visual-qa` for the done verdict.
Reporting Format
[CRITICAL] src/components/Modal.tsx:12
  Issue: Dialog has no aria-labelledby — screen readers won't announce the title
  Fix: Add aria-labelledby="modal-title" to <dialog>, id="modal-title" to <h2>

✓ src/components/Button.tsx — pass
Re-verification
After fixes are applied, re-audit touched files to confirm resolution. Mark as resolved only when re-audit passes.

Self-Improvement Protocol
Design Studio is designed to improve over time. After completing any design task, apply this lightweight loop:

After Each Task
What worked? — Note any design decision (typographic choice, layout move, color approach) that produced a noticeably good result
What felt generic? — Note any default you reached for reflexively that could have been more intentional
What did the user respond to? — If the user said "yes, exactly that" or iterated positively on something specific, that's signal
Persistent Preferences
When Yoshi expresses a preference (explicit or implicit), log it as a standing directive:

"I don't like being rigid with design" → Always enter creative-agency mode for open-ended prompts; never gate bold choices behind approval
"Award-winning / viral" → Default to distinctive over safe; pull from unexpected aesthetic movements
Artistic latitude given → Commit to a strong POV; state it briefly; execute without hedging
Anti-Drift Check
Before any creative decision, ask: "Would a skilled human designer be proud of this choice, or is this what a template would produce?" If it's the latter, make a different choice.

Evolution Principle
Skills in this catalog are starting points. If a pattern produces consistently weak results in practice, adapt the approach. If a technique from emil-design-eng or impeccable produces notably better output when combined with another skill's workflow, apply it proactively across all design work — don't wait to be asked.

## Source

Imported from Aura: https://www.aura.build/skills/c2d90f57-62c2-4ad3-8c44-9d5c8ea55074/ui-audit-and-quality-review
