# Implementation Task Graph

Use this after the storyboard, asset queue, motion recipes, component choices and visual style tile exist.

## Readiness

| Input | Status | Evidence | Gap |
| --- | --- | --- | --- |
| Source dossier | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Reference scorecard | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Visual style tile | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Section storyboard | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Asset queue | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Motion recipes | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Component choices | Fill with ready/missing | Fill with file path | Fill with gap or "none" |
| Change traceability | Fill with ready/missing | Fill with file path | Fill with gap or "none" |

## Build Graph Summary

| Ring | Goal | First task | Last task | Completion evidence |
| --- | --- | --- | --- | --- |
| 0 Preserve | Fill with protected behavior | Fill with task ID | Fill with task ID | Fill with evidence |
| 1 Foundation | Fill with tokens/shell goal | Fill with task ID | Fill with task ID | Fill with evidence |
| 2 Structure | Fill with section structure goal | Fill with task ID | Fill with task ID | Fill with evidence |
| 3 Assets | Fill with asset goal | Fill with task ID | Fill with task ID | Fill with evidence |
| 4 Motion | Fill with animation goal | Fill with task ID | Fill with task ID | Fill with evidence |
| 5 Responsive and quality | Fill with QA goal | Fill with task ID | Fill with task ID | Fill with evidence |
| 6 Final handoff | Fill with launch/handoff goal | Fill with task ID | Fill with task ID | Fill with evidence |

## Task Graph

| Task ID | Change IDs | Ring | Type | Section | Blocked by | Blocks | Files or routes | Plan sources | Visible result | Verification | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| task-001-preserve-current-contract | chg-001 | 0 Preserve | Preserve | Global | none | task-002-foundation-shell | Fill with protected files/routes | 01, 02, 10, dossier, 28 | Existing routes, nav, forms, SEO, legal and analytics-sensitive labels are preserved or explicitly approved for change | Fill with command/manual check | Fill with evidence path or note | Fill with planned/in-progress/done/blocked |
| task-002-foundation-shell | chg-002 | 1 Foundation | Foundation | Global | task-001-preserve-current-contract | task-003-first-section-structure | Fill with files/routes | 05, 17, 18, 28 | Shared shell, typography, color, spacing, radius and surface rules support the redesign | Fill with command/screenshot | Fill with evidence path or note | Fill with planned/in-progress/done/blocked |

## Blocking Map

| Blocker task | Blocked tasks | Reason | How to unblock |
| --- | --- | --- | --- |
| Fill with task ID | Fill with task IDs | Fill with dependency reason | Fill with exact unblock action |

## Per-Task Detail

Copy this block for each serious task.

```text
Task ID:
Change IDs:
Ring:
Type:
Section:
Blocked by:
Blocks:
Files or routes:
Plan sources:
Reference IDs:
Asset IDs:
Motion recipe IDs:
Visible result:
Implementation notes:
Dependencies:
Verification:
Evidence to capture:
Risk:
Status:
```

## Verification Plan

| Verification | Applies to tasks | Command or method | Required evidence | Owner agent |
| --- | --- | --- | --- | --- |
| Typecheck | Fill with task IDs | Fill with command | Fill with output note | Fill with agent |
| Build | Fill with task IDs | Fill with command | Fill with output note | Fill with agent |
| Desktop screenshot | Fill with task IDs | Fill with capture method | Fill with screenshot path | Fill with agent |
| Mobile screenshot | Fill with task IDs | Fill with capture method | Fill with screenshot path | Fill with agent |
| Reduced-motion check | Fill with task IDs | Fill with browser or code method | Fill with evidence path/note | Fill with agent |
| Performance budget | Fill with task IDs | Fill with Lighthouse/manual method | Fill with report path/note | Fill with agent |

## Screenshot Matrix

| Shot ID | Task ID | Viewport | Section | Purpose | Expected path | Status |
| --- | --- | --- | --- | --- | --- | --- |
| shot-001 | Fill with task ID | desktop | Fill with section | Fill with purpose | evidence/screenshots/fill-with-name.png | Fill with planned/captured/needs-fix |

## Dependency Budget

| Dependency | Introduced by task | Why needed | Alternative considered | Accepted risk | Verification |
| --- | --- | --- | --- | --- | --- |
| Fill with dependency or "none" | Fill with task ID | Fill with reason | Fill with alternative | Fill with risk | Fill with check |

## Handoff Notes

- Fill with first task the implementation agent should start.
- Fill with tasks that must not start until assets are produced.
- Fill with tasks that need browser screenshots before being called done.
- Fill with known risks that visual QA must re-check.
